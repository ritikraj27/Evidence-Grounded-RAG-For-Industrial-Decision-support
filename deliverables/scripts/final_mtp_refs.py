#!/usr/bin/env python3
"""The eight works the work stands on, in IEEE style.

Both decks cite the same eight works, so the citations live here rather than
being written twice. Each entry is a pair: the IEEE citation, and the sentence
that says where the work is used.
"""

#: (IEEE citation, where this work is used)
IEEE_REFS = [
    ("[1] G. V. Cormack, C. L. A. Clarke, and S. Bütcher, \"Reciprocal rank "
     "fusion outperforms Condorcet and individual rank learning methods,\" in "
     "Proc. 32nd Int. ACM SIGIR Conf. Res. Develop. Inf. Retrieval (SIGIR), "
     "2009, pp. 758-759, doi: 10.1145/1571941.1572114.",
     "The fusion function and the constant of 60 used in stage one."),

    ("[2] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. "
     "Küttler, M. Lewis, W.-T. Yih, T. Rocktäschel, S. Riedel, and D. Kiela, "
     "\"Retrieval-augmented generation for knowledge-intensive NLP tasks,\" in "
     "Adv. Neural Inf. Process. Syst. (NeurIPS), vol. 33, 2020, pp. "
     "9459-9474, arXiv: 2005.11401.",
     "The reader and retriever split the framework inherits."),

    ("[3] V. Karpukhin, B. Oguz, S. Min, P. Lewis, L. Wu, S. Edunov, D. Chen, "
     "and W.-T. Yih, \"Dense passage retrieval for open-domain question "
     "answering,\" in Proc. Conf. Empirical Methods Natural Lang. Process. "
     "(EMNLP), 2020, pp. 6769-6781, doi: 10.18653/v1/2020.emnlp-main.550.",
     "The dense leg, and the encoder that replaced the general-purpose "
     "sentence encoder."),

    ("[4] Y. A. Yadkori, I. Kuzborskij, D. Stutz, and A. György, \"Mitigating "
     "LLM hallucinations via conformal abstention,\" arXiv:2405.01563, 2024.",
     "The shape of a calibrated abstention with a coverage guarantee."),

    ("[5] H. Joren, J. Zhang, C.-S. Ferng, D.-C. Juan, and A. Taly, \"Sufficient "
     "context: A new lens on retrieval augmented generation systems,\" "
     "arXiv:2411.06037, 2024.",
     "The distinction between relevance and sufficiency, and the "
     "risk-coverage lens."),

    ("[6] P. Rajpurkar, R. Jia, and P. Liang, \"Know what you don't know: "
     "Unanswerable questions for SQuAD,\" in Proc. Conf. Assoc. Comput. "
     "Linguist. (ACL), 2018, pp. 518-528, doi: 10.18653/v1/P18-2124.",
     "The requirement that an unanswerable question be plausible, which the "
     "repaired class was built to satisfy."),

    ("[7] A. Tikhomirov and V. Savchenko, \"The selection effect: Why compact "
     "LLM verifiers for emotion classification fail behind encoder confidence "
     "gates,\" in Proc. Conf. Empirical Methods Natural Lang. Process. "
     "(EMNLP), 2026. [Online]. Available: "
     "https://aclanthology.org/2026.emnlp-main.1049/",
     "The rule that a selected slice cannot be compared with an unselected "
     "one."),

    ("[8] S. Goswami and S. Kurra, \"HALT-RAG: A task-adaptable framework for "
     "hallucination detection with calibrated NLI ensembles and abstention,\" "
     "arXiv:2509.07475, 2025.",
     "The closest published work to this gate, and the one the measurement "
     "is positioned against."),
]
