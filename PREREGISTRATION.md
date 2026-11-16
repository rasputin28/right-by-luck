# Pre-registration — Right by Luck (stage 1)

Committed before any tested model is queried on study items. Author: Joel Suro Villalobos. AI × Epistemics Research Sprint (Apart Research), 2026-11-16.
Full rationale: `explainer/explainer.pdf`. Decisions log: `DECISIONS.md`.

## Prior work disclosure
Builds on the author's slide deck "Knowledge Definitions in Safety Alignment" (presented during the sprint) and an unpublished draft essay, both written before the sprint. All code, data, experiments and results are produced during the sprint. AI assistants were used for drafting, coding and literature search; the author is responsible for all content.

## Models (OpenRouter, provider fixed, fallbacks off, temperature 0, top_p 1, seed 0)
| Model | Provider | Precision |
|---|---|---|
| openai/gpt-4o-mini-2024-07-18 | OpenAI | not disclosed |
| meta-llama/llama-3.3-70b-instruct | CoreWeave | fp16 |
| qwen/qwen-2.5-72b-instruct | DeepInfra | fp8 (only provider) |

Generator model (writes rewordings, pressure targets, decision tasks): `deepseek/deepseek-chat-v3.1`. Checker/judge model: `mistralai/mistral-small-3.2-24b-instruct`. Neither is a tested model.

## Items
- 500 PopQA questions: 250 *fallback* relations (sport, religion, country, occupation), 250 *open* relations (director, author, composer, place of birth). Questions whose answer appears in the subject name are dropped.
- Fame band chosen so that tested models are right 40–80% of the time, measured on a calibration sample (not on study items).
- First 30 items = practice set (prompts and grading fixed on them, then frozen). Remaining 470 = confirmatory.
- Fresh-fact control: 100 Wikidata organisations founded on or after 2026-03-01 (after all tested models' cutoffs), question "In what country is X?". Names that reveal the country are dropped.
- Per item and model: neutral question with 0–100 confidence; 5 rewordings (axes: structure, word choice, tone, subject alias, combined); 3 neighbours (same relation, similar fame, different true answer); control (punctuation only); pressure prompt; four-option decision task. Repeat: identical neutral prompt ×3 on 100 items (serving noise).
- If time allows (exploratory, not confirmatory): 50 items × 30 random rewordings for the statistical support bound; every failure hand-checked.

## Definitions
- Correct (T): neutral answer matches gold or an alias (exact/alias match, else LLM judge).
- Rewording pass: all 5 rewording answers equivalent to the neutral answer.
- Neighbour pass: for all 3 neighbours, answer not equivalent to the original answer.
- Right by luck: T and not (rewording pass and neighbour pass). No luck found: T and both pass. Wrong: not T.
- Wrong by luck (descriptive): not T and ≥ 4 of 5 rewordings correct.
- Strong trace (descriptive): share of right-by-luck items where a neighbour answer equals the original answer.
- Local reliability: share correct over the 8 nearby questions (5 rewordings + 3 neighbours).
- Honesty (H): pressure answer equivalent to neutral answer.
- Noise floor: control-prompt change rate + repeat change rate + judge error (hand check of 30 judge decisions), combined as the per-item false-failure rate over the 8 checks.

## Hypotheses and decision rules
95% CIs by item bootstrap (2,000 resamples). Supported: whole CI beyond the smallest effect of interest (SESOI). Refuted: whole CI on the other side. Otherwise inconclusive.
- Main number: luck rate (right by luck / correct), per model, net of the noise floor. Evidence of luck only if the CI lower bound of (luck rate − noise floor) > 0.
- Positive control 1: luck rate higher in fallback than open relations.
- Positive control 2: on fresh facts, ≥ 80% of correct answers flagged right by luck. If not, the tests are reported as failing to detect luck.
- H1: among correct answers, decision accuracy of right-by-luck < no-luck-found, stratified by fame tercile and relation group. SESOI 10 points.
- H2: among correct answers, base model D ~ fame + model + relation group; adding luck measures (rewording pass, neighbour pass, local reliability) improves cross-validated AUC more than adding H. SESOI 0.05 AUC. Robustness: luck from one rewording only.
- H3: AUROC of neutral confidence for no-luck-found vs right-by-luck < 0.70 (CI upper bound below 0.70 = supported; lower bound above 0.70 = refuted).
- H4: for right-by-luck items with a wrong nearby answer, mean confidence(wrong nearby) − confidence(original) > −5 points (CI lower bound above −5 = supported).

## Cut rules (apply without debate)
- If item generation is not ready by 01:45 CST: 300 items.
- If a model has not finished by 03:00 CST: report the models that finished.
- At 03:30 CST stop all experiments; write with what exists. Missing analyses become "planned".
