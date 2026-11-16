# Novedad del ε-δ epistémico — búsqueda de literatura (2026-11-15)

**Veredicto: ACOTADO.** La garantía estadística en sí (cota Clopper-Pearson sobre la probabilidad de responder bien a preguntas muestreadas de una distribución de prompts) YA EXISTE para LLMs: QuaCer-C / LLMCert-C (Chaudhary et al., 2402.15929), y la misma familia hizo lo mismo para sesgo y para selección de herramientas. Lo nuevo es (i) D definida como vecindad de UNA pregunta con ejes de estilo explícitos (ellos usan grafos de conocimiento + ruido de contexto), (ii) leer la cota como condición de safety (Sosa/Williamson) y separar la cota inferior existencial ("tasa de suerte") de la superior estadística, (iii) los ejes principales de falla. No hallé ningún trabajo que una garantía estadística con safety/anti-suerte.

Todos los ids se verificaron con export.arxiv.org/api/query?id_list=<id>.

## Trabajos

1. **Certifying Knowledge Comprehension in LLMs** — Isha Chaudhary, Vedaant V. Jain, Gagandeep Singh — 2024 — arXiv:2402.15929 (QuaCer-C).
   Parecido: el más cercano; cotas de alta confianza sobre P(respuesta correcta) para preguntas muestreadas de una distribución de prompts, con ruido natural. Diferencia: la distribución sale de grafos de conocimiento (comprensión en contexto, multi-salto), no de reformulaciones de una pregunta fija por ejes de estilo; sin marco epistémico.
2. **Certifying Counterfactual Bias in LLMs** — Isha Chaudhary, Qian Hu, Manoj Kumar, Morteza Ziyadi, Rahul Gupta, Gagandeep Singh — 2024 — arXiv:2405.18780 (LLMCert-B).
   Parecido: certificado = cota sobre la probabilidad de respuesta sin sesgo bajo una distribución de prompts contrafactuales. Diferencia: la propiedad es sesgo, no conocimiento factual.
3. **Quantitative Certification of Agentic Tool Selection** — Jehyeok Yeon, Isha Chaudhary, Gagandeep Singh — 2025 — arXiv:2510.03992 (LLMCert-T).
   Parecido: misma receta (Bernoulli + cota de alta confianza bajo una distribución declarada). Diferencia: selección de herramientas. Muestra que la receta ya es un método general.
4. **Sound Probabilistic Safety Bounds for Large Language Models** — Mahdi Nazeri, Anne-Kathrin Schmuck, Sadegh Soudjani, Alessandro Abate — 2026 — arXiv:2607.20286.
   Parecido: cotas PAC con Clopper-Pearson para LLMs. Diferencia: la aleatoriedad está en la decodificación (árbol de generación, prompt fijo), no en las perturbaciones del prompt; la propiedad es salida dañina.
5. **Prompt Risk Control: A Rigorous Framework for Responsible Deployment of Large Language Models** — Thomas P. Zollo, Todd Morrill, Zhun Deng, Jake C. Snell, Toniann Pitassi, Richard Zemel — 2023 — arXiv:2311.13628.
   Parecido: cotas superiores libres de distribución sobre el riesgo de un prompt, incluso bajo cambio de distribución. Diferencia: sirve para ELEGIR un prompt según la población de usuarios, no para certificar un hecho ante paráfrasis.
6. **DOVE: A Large-Scale Multi-Dimensional Predictions Dataset Towards Meaningful LLM Evaluation** — Eliya Habba, Ofir Arviv, Itay Itzhak, Yotam Perlitz, Elron Bandel, Leshem Choshen, Michal Shmueli-Scheuer, Gabriel Stanovsky — 2025 — arXiv:2503.01622.
   Parecido: perturbaciones a lo largo de dimensiones explícitas y su efecto conjunto (base para "ejes principales"). Diferencia: dimensiones de formato de benchmark (delimitadores, enumeradores, redacción de la instrucción); no da garantía ni descomposición tipo PCA.
7. **ProSA: Assessing and Understanding the Prompt Sensitivity of LLMs** — Jingming Zhuo, Songyang Zhang, Xinyu Fang, Haodong Duan, Dahua Lin, Kai Chen — 2024 — arXiv:2410.12405.
   Parecido: sensibilidad al prompt a nivel de instancia (PromptSensiScore). Diferencia: es una métrica descriptiva; no da cota ni ejes.
8. **Standards for Belief Representations in LLMs** — Daniel A. Herrmann, Benjamin A. Levinstein — 2024 — arXiv:2405.21030.
   Parecido: lleva la epistemología formal a las creencias de los LLM (condiciones de adecuación). Diferencia: trata la creencia, no el conocimiento ni la safety; no tiene garantía estadística. Es el puente filosófico más cercano que encontré.

Sin resultados en arXiv: Gettier/safety/"epistemic luck"/reliabilismo + LLM + garantía estadística; ANOVA o diseño factorial de la sensibilidad al prompt.

## (a) ¿Es nuevo?
Acotado. La certificación Clopper-Pearson del conocimiento bajo una distribución de prompts ya existe (QuaCer-C). No es nuevo como método estadístico. Lo nuevo es: la vecindad de safety por ejes de estilo, la lectura epistémica con la asimetría entre cota inferior y cota superior, y los ejes principales de falla.

Frase para el paper:
> "Statistical certification of LLM correctness over prompt distributions is not new (Chaudhary et al., 2024; Zollo et al., 2023); our contribution is to define the distribution as an explicit, axis-structured neighbourhood of a single question and to read the resulting Clopper–Pearson bound as an operational, distribution-relative version of the epistemic safety condition (Sosa, 1999; Williamson, 2000), together with the observation that observed 'luck' is an existential lower bound while the certificate is a statistical upper bound."

## (b) Citas obligatorias
2402.15929 (QuaCer-C, la primera que hay que diferenciar), 2405.18780, 2311.13628, 2503.01622, 2405.21030; más las ya conocidas: 1811.07209, 1902.02918, 2310.11324, 2401.00595, 2102.01017.
