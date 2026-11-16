# Novedad: safety epistemológica = robustez de entrada + durabilidad del modelo (búsqueda 2026-11-15)

VEREDICTO: se sostiene, pero ACOTADA. Nadie encontrado trata paráfrasis/contrafactuales + fine-tuning/cuantización como UNA condición anti-suerte de conocimiento. Pero (i) unificar perturbación de entrada y de pesos ya existe sin marco epistémico (Dai et al. 2025), y (ii) "verdad = invariancia ante transformaciones", con Nozick y continual learning, ya está propuesto conceptualmente (Lopez-Paz, nov 2026). La novedad es el marco epistemológico + la medición empírica conjunta, no la idea de mirar ambos ejes.

Ningún trabajo hace exactamente lo nuestro.

## Trabajos verificados (abiertos en arXiv)
1. Lopez-Paz, D. (2026). "Against All Likelihood". arXiv:2611.09385. Verdad como invariancia ante transformaciones del entorno; cita a Nozick; habla de continual learning. Lo más cercano en espíritu. Difiere: conceptual, sin safety/sensitivity, sin pruebas sobre versiones del modelo.
2. Fierro, Dhar, Stamatiou, Garneau, Søgaard (2024). "Defining Knowledge: Bridging Epistemology and Large Language Models". EMNLP 2024, arXiv:2410.02499. Formaliza 5 definiciones de conocimiento para LLMs (incl. virtud) y propone protocolos. Difiere: el abstract no menciona safety/sensitivity/anti-suerte ni durabilidad.
3. Uyar, T. (2026). "From the Gettier Machine to Justified True Output: A Three-Step Account of Rational Trust in Generative AI". arXiv:2610.38112. Gettier + sensitivity aplicados a la IA generativa. Difiere: filosófico, la sensitivity es del USUARIO, no una métrica del modelo.
4. Dai, Yang, Zhou, Zhu (2025). "Breach in the Shield: Unveiling the Vulnerabilities of Large Language Models". EACL 2026, arXiv:2504.03714. Una sola medida (FI, geometría de la información) de estabilidad ante perturbaciones de entrada Y de parámetros. Difiere: sin marco epistémico ni conocimiento factual. Amenaza directa a "unificar ambos ejes es nuevo".
5. Rababah et al. (2026). "The Illusion of Equivalency: Statistical Characterization of Quantization Effects in LLMs". arXiv:2607.08734. "Correctness Agreement": qué ítems siguen correctos tras cuantizar; la precisión agregada oculta cambios. Es nuestra durabilidad local ítem a ítem, sin paráfrasis ni epistemología.
6. Wang et al. (2025). "Through a Compressed Lens: Investigating The Impact of Quantization on Factual Knowledge Recall". arXiv:2505.13963. La cuantización reduce poco el recall factual (más en modelos chicos). Difiere: sin paráfrasis ni anti-suerte.
7. Dies, Maynard, Savcisens, Eliassi-Rad (2025). "Epistemic Familiarity is Associated With Belief Stability in Large Language Models" (Findings EMNLP 2026). arXiv:2511.19166. P-StaT: estabilidad de creencias ante perturbaciones semánticas; retracción >50%. Difiere: solo entradas, no versiones del modelo; sin safety.
8. Elazar et al. (2021). "Measuring and Improving Consistency in Pretrained Language Models" (ParaRel). TACL, arXiv:2102.01017. Consistencia ante paráfrasis. Es nuestra base de safety-ante-entradas; sin durabilidad.

Otros verificados para citar: Kadavath et al. 2022 "Language Models (Mostly) Know What They Know" (arXiv:2207.05221); Gekhman et al. 2024 "Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations?" (arXiv:2405.05904); Zheng, Lapata, Pan 2024 "How Reliable are LLMs as Knowledge Bases? Re-thinking Facutality and Consistency" [sic en arXiv] (arXiv:2407.13578).
Descartado: Chacón Sartori, arXiv:2603.28371 (RETIRADO por error en resultados; no citar).

## (a) Redacción propuesta
"To our knowledge, no prior work operationalizes the epistemological safety (anti-luck) condition for LLM knowledge as a single criterion spanning both nearby inputs (paraphrases, counterfactuals) and nearby models (fine-tuned and quantized variants); prior work measures these axes separately (e.g., ParaRel; correctness agreement under quantization) or unifies them without an epistemic account of knowledge (Dai et al., 2025; Lopez-Paz, 2026)."

## (b) Citar sí o sí
Lopez-Paz 2611.09385; Fierro et al. 2410.02499; Dai et al. 2504.03714; Rababah et al. 2607.08734; Elazar et al. 2102.01017; + RepNoise 2405.14577, TAR 2408.00761, Qi et al. 2412.07097 (ya conocidos). Recomendable: Uyar 2610.38112, Kadavath 2207.05221, Dies et al. 2511.19166, Wang et al. 2505.13963.

Límite: no encontré trabajos empíricos sobre Gettier/anti-suerte en LLMs (arXiv API, Semantic Scholar, búsqueda web, LessWrong). No leí PDFs completos: solo abstracts.
