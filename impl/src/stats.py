"""Statistical machinery for the evaluation chapter.

Everything here is standard and every formula is stated, because the paper's
defensibility rests on choosing the right test for each question and on
reporting effect sizes, not just p-values.

Which test for which question
------------------------------
* **Two raters, nominal labels** -> Cohen's kappa. The benchmark's
  inter-annotator agreement is exactly this.
* **Two systems, same queries, binary outcome** -> McNemar's test. This is
  the right test for "is system A better than system B on the same 300
  questions", because the two systems are paired on every item and the
  discordant pairs carry all the information.
* **Two systems, same queries, continuous/ordinal outcome** -> Wilcoxon
  signed-rank test (non-parametric) or a paired t-test if the differences are
  approximately normal.
* **Effect size** -> always reported alongside a p-value. A p-value says
  "unlikely under the null"; it does not say "large". Cohen's d for paired
  samples is d_z = mean(diff) / sd(diff).

Why not a t-test on the primary comparison
-------------------------------------------
Per-query faithfulness scores are bounded in [0, 1] and their distribution is
typically left-skewed with a spike at 1.0 (most queries are answered
faithfully). The normality assumption of the t-test is violated on the
paired *differences*, so the Wilcoxon signed-rank test is the safe default.
McNemar is used when the outcome is binary (hallucinated / not hallucinated),
which is how the headline hallucination-rate comparison is reported.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass
class TestResult:
    name: str
    statistic: float
    p_value: float
    n: int
    effect_size: float | None = None
    effect_name: str = ""
    interpretation: str = ""

    def to_dict(self) -> dict:
        return {
            "test": self.name,
            "statistic": float(self.statistic),
            "p_value": float(self.p_value),
            "n": self.n,
            "effect_size": None if self.effect_size is None else float(self.effect_size),
            "effect_name": self.effect_name,
            "interpretation": self.interpretation,
        }


def cohens_kappa(a: list, b: list) -> tuple[float, float, float]:
    """Cohen's kappa with an asymptotic standard error and 95% CI.

    kappa = (Po - Pe) / (1 - Pe)

    where Po is the observed agreement between the two raters and Pe is the
    agreement expected by chance given each rater's own marginal
    distribution.

    Why kappa and not raw agreement: raw agreement is inflated by categories
    that dominate the marginals. If 90% of questions are "easy", two raters
    who both always say "easy" agree 90% of the time while agreeing on nothing
    that required judgement. kappa corrects for that.

    The variance formula is Fleiss, Cohen & Everitt (1969) for large samples:

        SE(kappa) = sqrt( Po(1 - Po) / (N(1 - Pe)) )

    and the confidence interval is kappa +/- 1.96 * SE.
    """
    a = np.asarray(a, dtype=object)
    b = np.asarray(b, dtype=object)
    if a.size != b.size:
        raise ValueError("rater lists must be the same length")
    n = a.size
    if n == 0:
        return float("nan"), float("nan"), float("nan")

    observed = float(np.mean(a == b))
    cats = set(a.tolist()) | set(b.tolist())
    pa = {c: float(np.mean(a == c)) for c in cats}
    pb = {c: float(np.mean(b == c)) for c in cats}
    expected = float(sum(pa[c] * pb[c] for c in cats))
    if np.isclose(expected, 1.0):
        return 1.0, 0.0, 1.0
    kappa = (observed - expected) / (1.0 - expected)
    se = math.sqrt(max(observed * (1.0 - observed) / (n * (1.0 - expected)), 0.0))
    return kappa, kappa - 1.96 * se, kappa + 1.96 * se


def mcnemar_test(
    system_a: list[bool], system_b: list[bool], exact: bool = True
) -> TestResult:
    """McNemar's test on two paired systems with binary outcomes.

    Build the 2x2 table of discordant pairs:

                 B correct  B wrong
        A correct      b         c
        A wrong        d         e

    Under the null of no systematic difference, b and d are exchangeable and
    b + d ~ Binomial(n_discordant, 0.5). The exact binomial test is the
    standard choice; the chi-square approximation requires n_discordant >= 25.
    """
    a = np.asarray(system_a, dtype=bool)
    b = np.asarray(system_b, dtype=bool)
    if a.size != b.size:
        raise ValueError("systems must be evaluated on the same items")
    b_only = int(np.sum(a & ~b))   # A right, B wrong
    c_only = int(np.sum(~a & b))   # A wrong, B right
    n_disc = b_only + c_only

    if n_disc == 0:
        return TestResult(
            name="McNemar (exact)",
            statistic=0.0,
            p_value=1.0,
            n=int(a.size),
            effect_size=0.0,
            effect_name="difference in proportion",
            interpretation="No discordant pairs; the systems agreed on every item.",
        )

    if exact:
        p = stats.binomtest(min(b_only, c_only), n_disc, 0.5).pvalue
    else:
        chi2 = (abs(b_only - c_only) - 1) ** 2 / n_disc
        p = stats.chi2.sf(chi2, 1)

    n = int(a.size)
    diff = float(a.mean() - b.mean())
    direction = "A" if diff > 0 else ("B" if diff < 0 else "neither")
    return TestResult(
        name="McNemar (exact)" if exact else "McNemar (chi2, cc)",
        statistic=float(b_only - c_only),
        p_value=float(p),
        n=n,
        effect_size=diff,
        effect_name="difference in proportion",
        interpretation=(
            f"System {direction} is better by {abs(diff)*100:.2f} percentage points "
            f"({b_only} discordant wins vs {c_only} losses)."
        ),
    )


def wilcoxon_signed_rank(
    system_a: list[float], system_b: list[float]
) -> TestResult:
    """Wilcoxon signed-rank test on paired differences.

    The differences are ranked by absolute magnitude; the test asks whether
    the sum of positive ranks differs from the sum of negative ranks more than
    chance allows. Zero differences are discarded (the default 'wilcox'
    handling). Cohen's d_z = mean(diff)/sd(diff) is reported as the effect
    size.
    """
    a = np.asarray(system_a, dtype=np.float64)
    b = np.asarray(system_b, dtype=np.float64)
    if a.size != b.size:
        raise ValueError("systems must be evaluated on the same items")
    diff = a - b
    nz = diff[diff != 0]
    if nz.size == 0:
        return TestResult(
            name="Wilcoxon signed-rank",
            statistic=0.0,
            p_value=1.0,
            n=int(a.size),
            effect_size=0.0,
            effect_name="Cohen's d_z",
            interpretation="All paired differences are exactly zero.",
        )
    stat, p = stats.wilcoxon(a, b, zero_method="wilcox")
    sd = diff.std(ddof=1) if diff.size > 1 else float("nan")
    d_z = float(diff.mean() / sd) if sd and not math.isnan(sd) and sd > 0 else 0.0
    return TestResult(
        name="Wilcoxon signed-rank",
        statistic=float(stat),
        p_value=float(p),
        n=int(a.size),
        effect_size=d_z,
        effect_name="Cohen's d_z",
        interpretation=(
            f"Mean paired difference {diff.mean():+.4f} (d_z = {d_z:+.3f})."
        ),
    )


def paired_t_test(system_a: list[float], system_b: list[float]) -> TestResult:
    """Paired t-test, kept for the cases where normality is defensible."""
    a = np.asarray(system_a, dtype=np.float64)
    b = np.asarray(system_b, dtype=np.float64)
    stat, p = stats.ttest_rel(a, b)
    diff = a - b
    sd = diff.std(ddof=1) if diff.size > 1 else float("nan")
    d_z = float(diff.mean() / sd) if sd and not math.isnan(sd) and sd > 0 else 0.0
    return TestResult(
        name="paired t-test",
        statistic=float(stat),
        p_value=float(p),
        n=int(a.size),
        effect_size=d_z,
        effect_name="Cohen's d_z",
        interpretation=f"Mean paired difference {diff.mean():+.4f}.",
    )


def bootstrap_ci(
    values: np.ndarray,
    statistic=np.mean,
    n_bootstrap: int = 10_000,
    alpha: float = 0.05,
    seed: int = 20261118,
) -> tuple[float, float, float]:
    """Percentile bootstrap confidence interval.

    Resample the observations with replacement n_bootstrap times, recompute the
    statistic each time, and take the empirical 2.5% and 97.5% quantiles.

    Assumptions and limits: the percentile bootstrap assumes the sampling
    distribution of the statistic is approximately symmetric around its
    percentile estimate. It is reliable for means and proportions at the
    sample sizes here, but with n < 20 the interval should be read as
    indicative rather than exact -- which is why the paper's small-sample
    claims lean on the exact tests above and on the effect size rather than on
    the interval width.
    """
    values = np.asarray(values, dtype=np.float64)
    if values.size == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, values.size, size=(n_bootstrap, values.size))
    draws = statistic(values[idx], axis=1)
    lo, hi = np.quantile(draws, [alpha / 2, 1 - alpha / 2])
    return float(statistic(values)), float(lo), float(hi)


def cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    """Cliff's delta -- a non-parametric effect size that does not assume
    normality.

    delta = (#(a > b) - #(a < b)) / (n_a * n_b)

    It lies in [-1, 1]; 0 means the two samples are indistinguishable, and the
    conventional thresholds are |delta| < 0.147 (negligible), < 0.33 (small),
    < 0.474 (medium), otherwise large.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.size == 0 or b.size == 0:
        return float("nan")
    gt = np.sum(a[:, None] > b[None, :])
    lt = np.sum(a[:, None] < b[None, :])
    return float((gt - lt) / (a.size * b.size))


def cliffs_delta_significance(delta: float, n_a: int, n_b: int) -> float:
    """Approximate two-sided p-value for Cliff's delta under the null of
    independence, using the normal approximation to the hypergeometric
    variance."""
    if delta is None or math.isnan(delta):
        return float("nan")
    n = n_a * n_b
    se = np.sqrt((n * (n + 1) / 12.0) / (n_a * n_b))
    if se == 0:
        return float("nan")
    z = abs(delta) / se
    return float(2 * stats.norm.sf(z))


def wilcoxon_rank_biserial(a: list[float], b: list[float]) -> float:
    """Wilcoxon matched-pairs rank-biserial correlation -- the matched-pairs
    counterpart of Cliff's delta, in [-1, 1]."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    diff = a - b
    nz = diff[diff != 0]
    if nz.size == 0:
        return 0.0
    ranks = stats.rankdata(np.abs(nz))
    r_plus = float(ranks[nz > 0].sum())
    r_minus = float(ranks[nz < 0].sum())
    return (r_plus - r_minus) / (r_plus + r_minus)
