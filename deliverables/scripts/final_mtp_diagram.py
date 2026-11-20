#!/usr/bin/env python3
"""The framework diagram that opens the deck.

One picture, drawn from the pipeline's own stage table: the five stages, what
each one does, and the two places where the framework answers with a refusal
instead of an answer. The gate is picked out in the accent, because it is the
part of the picture the talk is about.

The figure is drawn at the size it is placed at, so that the type in the
picture is the size it will be on the slide.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import (Circle, FancyArrowPatch,  # noqa: E402
                               FancyBboxPatch, Rectangle)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "deliverables" / "assets" / "mtp_pipeline.png"

INK = "#111111"
SOFT = "#3C3C42"
GREY = "#6E6E76"
LINE = "#C9C9D0"
ACCENT = "#291972"
TINT = "#F2F0F8"

W, H = 9.60, 2.30

STAGES = [
    ("STAGE 0", "Query-form\nvalidation", "lexical, fails open"),
    ("STAGE 1", "Hybrid\nretrieval", "BM25 and bge-m3, fused"),
    ("STAGE 2", "Rerank\nand quota", "cross-encoder, floor"),
    ("STAGE 3", "Confidence\ngate", "posterior at tau = 0.05"),
    ("STAGE 4", "Generation\nand claims", "answer with evidence"),
]


def build(path: Path = OUT) -> Path:
    """Draw the framework diagram and write it as a PNG."""
    with matplotlib.rc_context({
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    }):
        fig, ax = plt.subplots(figsize=(W, H))
        ax.set_xlim(-0.10, W + 0.10)
        ax.set_ylim(-0.12, H + 0.12)
        ax.axis("off")
        fig.patch.set_alpha(0.0)

        n = len(STAGES)
        margin, box_w, box_h = 0.16, 1.62, 1.06
        gap = (W - 2 * margin - n * box_w) / (n - 1)
        top = 1.94

        for i, (label, name, sub) in enumerate(STAGES):
            x = margin + i * (box_w + gap)
            is_gate = i == 3
            ax.add_patch(FancyBboxPatch(
                (x, top - box_h), box_w, box_h,
                boxstyle="round,pad=0.010,rounding_size=0.045",
                linewidth=1.4 if is_gate else 1.0,
                edgecolor=ACCENT if is_gate else LINE,
                facecolor=TINT if is_gate else "#FFFFFF"))
            ax.text(x + box_w / 2, top + 0.16, label, ha="center", va="center",
                    fontsize=7.6, color=ACCENT if is_gate else GREY,
                    fontweight="bold")
            ax.text(x + box_w / 2, top - 0.44, name, ha="center", va="center",
                    fontsize=10.4, color=INK, linespacing=1.30)
            ax.text(x + box_w / 2, top - box_h + 0.15, sub, ha="center",
                    va="center", fontsize=7.8, color=GREY, style="italic")

            if i < n - 1:
                ax.add_patch(FancyArrowPatch(
                    (x + box_w + 0.05, top - box_h / 2),
                    (x + box_w + gap - 0.05, top - box_h / 2),
                    arrowstyle="-|>", mutation_scale=10,
                    linewidth=1.0, color=LINE))

        # The two refusals. The first costs no retrieval and no model call,
        # because it runs first. The second costs no model call either, because
        # the generator is only reached when the gate has accepted.
        for idx in (0, 3):
            x = margin + idx * (box_w + gap) + box_w / 2
            ax.add_patch(FancyArrowPatch(
                (x, top - box_h), (x, 0.42),
                arrowstyle="-|>", mutation_scale=10, linewidth=1.1,
                color=ACCENT, connectionstyle="arc3,rad=0"))
            ax.text(x, 0.28, "REFUSE", ha="center", va="center",
                    fontsize=7.6, color=ACCENT, fontweight="bold")

        fig.subplots_adjust(left=0.002, right=0.998, top=0.998, bottom=0.002)
        fig.savefig(path, dpi=220, transparent=True)
        plt.close(fig)
    return path


#: The title-slide picture. It carries the idea of the work in one frame:
#: industrial text on the left, the retrieval machinery in the middle, and the
#: two ways the framework can answer on the right. It is drawn in the deck's
#: own face and palette, so that a picture on the first page does not fight
#: the twenty-four slides behind it.
INTENT_OUT = ROOT / "deliverables" / "assets" / "mtp_intent.png"

ACCENT = "#291972"
ACCENT_SOFT = "#EDEAF6"
INK = "#111111"
SOFT = "#3C3C42"
GREY = "#6E6E76"
LINE = "#D6D6DC"
PANEL = "#F7F7F9"
WHITE = "#FFFFFF"

DOCS = [
    ("Supply-chain procedures", "text"),
    ("Equipment manuals", "text"),
    ("Calibration records", "table"),
    ("Regulatory text", "chart"),
]


def _icon_user(ax, cx, cy, s, color):
    ax.add_patch(Circle((cx, cy + 0.13 * s), 0.10 * s, facecolor=color,
                        edgecolor="none"))
    ax.add_patch(FancyBboxPatch(
        (cx - 0.17 * s, cy - 0.17 * s), 0.34 * s, 0.20 * s,
        boxstyle="round,pad=0,rounding_size=0.05", facecolor=color,
        edgecolor="none"))


def _icon_page(ax, cx, cy, s, color):
    ax.add_patch(Rectangle((cx - 0.13 * s, cy - 0.16 * s), 0.26 * s, 0.32 * s,
                           facecolor="none", edgecolor=color, linewidth=1.3))
    for i, w in enumerate((0.16, 0.16, 0.10)):
        ax.plot([cx - 0.08 * s, cx - 0.08 * s + w * s],
                [cy + 0.07 * s - i * 0.08 * s] * 2, color=color, linewidth=1.1)


def _icon_table(ax, cx, cy, s, color):
    ax.add_patch(Rectangle((cx - 0.15 * s, cy - 0.15 * s), 0.30 * s, 0.30 * s,
                           facecolor="none", edgecolor=color, linewidth=1.3))
    for f in (1 / 3, 2 / 3):
        ax.plot([cx - 0.15 * s + 0.30 * s * f] * 2,
                [cy - 0.15 * s, cy + 0.15 * s], color=color, linewidth=0.9)
    ax.plot([cx - 0.15 * s, cx + 0.15 * s], [cy + 0.02 * s] * 2, color=color,
            linewidth=0.9)


def _icon_chart(ax, cx, cy, s, color):
    for dx, h in ((-0.12, 0.14), (-0.01, 0.26), (0.10, 0.20)):
        ax.add_patch(Rectangle((cx + dx * s, cy - 0.15 * s), 0.08 * s, h * s,
                               facecolor=color, edgecolor="none"))


def _icon_scales(ax, cx, cy, s, color):
    ax.plot([cx, cx], [cy - 0.17 * s, cy + 0.17 * s], color=color,
            linewidth=1.8)
    ax.plot([cx - 0.17 * s, cx + 0.17 * s], [cy + 0.09 * s] * 2, color=color,
            linewidth=1.8)
    for dx in (-0.17, 0.17):
        ax.plot([cx + dx * s, cx + dx * s], [cy + 0.09 * s, cy - 0.01 * s],
                color=color, linewidth=1.2)
        ax.add_patch(Rectangle((cx + dx * s - 0.08 * s, cy - 0.10 * s),
                               0.16 * s, 0.09 * s, facecolor=color,
                               edgecolor="none"))


def _icon_search(ax, cx, cy, s, color):
    ax.add_patch(Circle((cx - 0.03 * s, cy + 0.05 * s), 0.12 * s,
                        facecolor="none", edgecolor=color, linewidth=2.0))
    ax.plot([cx + 0.06 * s, cx + 0.17 * s], [cy - 0.04 * s, cy - 0.15 * s],
            color=color, linewidth=2.2, solid_capstyle="round")


def _icon_tick(ax, cx, cy, r, face, mark):
    ax.add_patch(Circle((cx, cy), r, facecolor=face, edgecolor="none"))
    ax.plot([cx - r * 0.42, cx - r * 0.10, cx + r * 0.45],
            [cy - r * 0.02, cy - r * 0.34, cy + r * 0.36], color=mark,
            linewidth=2.0, solid_capstyle="round")


def _icon_cross(ax, cx, cy, r, face, mark):
    ax.add_patch(Circle((cx, cy), r, facecolor=face, edgecolor="none"))
    d = r * 0.36
    ax.plot([cx - d, cx + d], [cy - d, cy + d], color=mark, linewidth=2.0,
            solid_capstyle="round")
    ax.plot([cx - d, cx + d], [cy + d, cy - d], color=mark, linewidth=2.0,
            solid_capstyle="round")


def build_intent(path: Path = INTENT_OUT) -> Path:
    """Draw the title-slide picture."""
    with matplotlib.rc_context({
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    }):
        fig, ax = plt.subplots(figsize=(10.4, 3.08))
        ax.set_xlim(0, 10.4)
        ax.set_ylim(0, 3.08)
        ax.axis("off")
        fig.patch.set_alpha(0.0)

        def box(x, y, w, h, *, face=WHITE, edge=LINE, lw=0.9, r=0.05):
            ax.add_patch(FancyBboxPatch(
                (x, y), w, h,
                boxstyle=f"round,pad=0.008,rounding_size={r}",
                linewidth=lw, edgecolor=edge, facecolor=face))

        def arrow(x0, y0, x1, y1, color=SOFT, lw=1.3):
            ax.add_patch(FancyArrowPatch(
                (x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=11,
                linewidth=lw, color=color, connectionstyle="arc3,rad=0"))

        def head(x0, x1, y, h, text):
            ax.add_patch(FancyBboxPatch(
                (x0, y - h), x1 - x0, h,
                boxstyle="round,pad=0.008,rounding_size=0.05",
                linewidth=0.9, edgecolor=ACCENT, facecolor=ACCENT))
            ax.text((x0 + x1) / 2, y - h / 2, text, ha="center", va="center",
                    fontsize=9.6, color=WHITE, fontweight="bold")

        # ---- the question
        box(0.08, 2.42, 2.16, 0.46, face=PANEL, edge=LINE)
        _icon_user(ax, 0.34, 2.65, 0.42, SOFT)
        ax.text(0.60, 2.65, "A User's Question", ha="left", va="center",
                fontsize=11.0, color=INK, fontweight="bold")

        # ---- the corpus
        box(0.08, 0.12, 2.16, 2.06, face=WHITE, edge=LINE)
        head(0.08, 2.24, 2.18, 0.32, "THE CORPUS")
        icons = (_icon_page, _icon_page, _icon_table, _icon_scales)
        for i, (name, modality) in enumerate(DOCS):
            y = 1.44 - i * 0.36
            box(0.16, y, 2.00, 0.30, face=WHITE, edge=LINE, lw=0.7, r=0.03)
            icons[i](ax, 0.32, y + 0.15, 0.32, SOFT)
            ax.text(0.48, y + 0.15, name, ha="left", va="center", fontsize=8.8,
                    color=INK)
            ax.text(2.08, y + 0.15, modality, ha="right", va="center",
                    fontsize=8.0, color=GREY, style="italic")

        arrow(2.28, 1.16, 2.78, 1.16)
        ax.text(2.53, 1.36, "retrieve", ha="center", va="bottom", fontsize=9.0,
                color=SOFT, style="italic")

        # ---- the pool
        box(2.84, 0.40, 1.72, 1.78, face=WHITE, edge=LINE)
        head(2.84, 4.56, 2.18, 0.32, "THE POOL")
        for i in range(3):
            y = 1.30 - i * 0.34
            box(2.94, y, 1.52, 0.28, face=WHITE, edge=LINE, lw=0.7, r=0.03)
            ax.text(3.08, y + 0.14, f"chunk {i + 1}", ha="left", va="center",
                    fontsize=9.4, color=SOFT)

        arrow(4.60, 1.16, 5.10, 1.16)
        ax.text(4.85, 1.36, "rerank", ha="center", va="bottom", fontsize=9.0,
                color=SOFT, style="italic")

        # ---- the gate
        box(5.16, 0.46, 2.08, 1.78, face=ACCENT_SOFT, edge=ACCENT, lw=1.2)
        head(5.16, 7.24, 2.24, 0.34, "THE GATE")
        _icon_search(ax, 6.20, 1.62, 0.50, ACCENT)
        ax.text(6.20, 1.06, "Does the evidence\ncontain the answer?",
                ha="center", va="center", fontsize=10.6, color=INK,
                linespacing=1.34)

        # ---- the two answers
        arrow(7.30, 1.58, 7.76, 2.02, SOFT)
        box(7.82, 1.82, 2.50, 0.62, face=WHITE, edge=ACCENT, lw=1.2)
        _icon_tick(ax, 8.08, 2.13, 0.15, ACCENT, WHITE)
        ax.text(8.32, 2.24, "An answer, with every claim", ha="left",
                va="center", fontsize=9.8, color=INK)
        ax.text(8.32, 2.00, "tagged by the evidence behind it", ha="left",
                va="center", fontsize=8.8, color=SOFT, style="italic")

        arrow(7.30, 1.10, 7.76, 0.66, SOFT)
        box(7.82, 0.40, 2.50, 0.62, face=PANEL, edge=LINE)
        _icon_cross(ax, 8.08, 0.71, 0.15, SOFT, WHITE)
        ax.text(8.32, 0.82, "A refusal, and no model call", ha="left",
                va="center", fontsize=9.8, color=INK)
        ax.text(8.32, 0.58, "was made at all", ha="left", va="center",
                fontsize=8.8, color=SOFT, style="italic")

        fig.subplots_adjust(left=0.002, right=0.998, top=0.998, bottom=0.002)
        fig.savefig(path, dpi=220, transparent=True)
        plt.close(fig)
    return path


if __name__ == "__main__":
    build()
    p = build_intent()
    print(f"[diagram] wrote {p}")
