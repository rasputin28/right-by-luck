# Right by Luck: Measuring When a Language Model's Correct Answer Is Not Knowledge

Joel Suro Villalobos (AI Safety Mexico, [aismx.org](https://www.aismx.org/en/)) · Claude (Anthropic, `claude-opus-5-5`; secondary co-author: coding, analysis, drafting, literature search)

AI × Epistemics Research Sprint (Apart Research), November 2026 · Track 1: Model Epistemics & Decision-Making Evals

**Paper:** [`paper/paper.pdf`](paper/paper.pdf) · **Pre-registration:** [`PREREGISTRATION.md`](PREREGISTRATION.md) · **Design explainer:** [`explainer/explainer.pdf`](explainer/explainer.pdf)

## What this is

A stopped clock shows the right time twice a day. A *Gettier answer* is a correct answer a model gives through a process that does not depend on the fact asked about. We test for it from outside the model with two checks taken from theories of knowledge:

- **Rewording (safety):** ask the same question 4 other ways; the answer must stay correct.
- **Neighbours (sensitivity):** ask 3 similar questions whose true answers differ; the model must not repeat the original answer.

A correct answer that fails either check is *right by luck*. The study was pre-registered before any tested model saw a study item.

## Main results (313 PopQA questions × 3 models, 95% bootstrap CIs)

| | GPT-4o-mini | Llama-3.3-70B | Qwen2.5-72B |
|---|---|---|---|
| Accuracy | 59.7% | 65.8% | 51.1% |
| Correct answers that are right by luck | 47.6% (40.6–54.5) | 42.7% (36.4–49.0) | 44.4% (36.9–51.9) |
| All answers with no luck found | 31% | 38% | 28% |

- Per check, among correct answers (post hoc): a rewording breaks the answer 17.0% of the time, a punctuation-only control 4.0%, an identical repeat 3.3%.
- Against the pre-registered (conservative) noise floor the net luck rate is **inconclusive** for every model.
- Fresh-fact control (organisations founded after the models' cutoffs): the tests flag only 42% of correct answers as luck (pre-registered threshold 80%), so luck rates are lower bounds; pattern luck needs "fake-barn" neighbours.
- H1 (lucky answers → worse decisions): 6.4 points, inconclusive. H2: inconclusive. H3 (confidence AUROC 0.67): inconclusive. H4: refuted; confidence drops 10.6 points on nearby failures.

Full numbers: [`results/results.json`](results/results.json).

## Why a method, not a benchmark

A fixed set of Gettier items would enter the training data of later models and then measure memory, not luck. The contribution is a **protocol for generating fresh tests** (paper, Section 3). Please run it with your own generator; agreement across generators is the evidence.

## Reproduce

Requirements: Python 3.12, an OpenRouter key.

```sh
uv venv && uv pip install pandas pyarrow httpx numpy scikit-learn matplotlib scipy
echo "OPENROUTER_API_KEY=..." > .env          # never commit this file
sh code/get_popqa.sh                           # PopQA test split -> data/sources/
cd code
python calibrate.py      # fame-band calibration (288 items not used in the study)
python build.py          # items: rewordings, pressure, decision (generator + checker)
python fresh.py          # fresh-fact control from data/sources/wikidata_orgs_2026.json
python run.py            # 14,322 calls to the 3 tested models
python run_noconf.py     # robustness: same battery without the confidence request
python grade.py && python grade.py responses_noconf.jsonl graded_noconf.jsonl
python analyze.py        # pre-registered + post-hoc analysis -> results/results.json
python figs.py           # figures
```

Every call is cached by a hash of its full request in `data/calls.jsonl`, so re-running the scripts reuses our exact responses. Delete that file to query the models again.

**Expect small differences on a fresh run.** Tested models were called through OpenRouter with the provider fixed and fallbacks disabled (GPT-4o-mini: OpenAI; Llama-3.3-70B: CoreWeave, fp16; Qwen2.5-72B: DeepInfra, fp8), temperature 0, top-p 1, seed 0. We cannot control the provider's hardware, load balancing or batching: in our run an identical prompt changed its correctness 3.3% of the time. The generator (`deepseek/deepseek-chat-v3.1`) and judge (`mistralai/mistral-small-3.2-24b-instruct`) were not provider-pinned; the provider of every call is in the log.

## Files

| Path | Content |
|---|---|
| `PREREGISTRATION.md` | Hypotheses, thresholds and design, committed 2026-11-16 00:20 CST before any study query |
| `DECISIONS.md` | Design decisions log (Spanish) |
| `code/` | All scripts; prompts are in `run.py`, `build.py`, `grade.py`, `fresh.py` |
| `data/items_ok.jsonl` | The 334 study items (questions, rewordings, neighbours, pressure targets, decision tasks) |
| `data/fresh_items.jsonl` | The 100 fresh-fact control items |
| `data/calls.jsonl` | Log of every API call: request, response, provider, response id, UTC time |
| `data/responses*.jsonl`, `data/graded*.jsonl` | Responses and grades |
| `data/features.csv` | One row per model × item, the input to the analysis |
| `results/` | `results.json`, figures, judge hand-check sheet |
| `data/sources/` | Wikidata query and result for the fresh-fact control (PopQA is downloaded by `get_popqa.sh`) |

## Disclosure

Builds on the first author's slide deck "Knowledge Definitions in Safety Alignment" (presented during the sprint) and an unpublished draft essay, both written before the sprint. All code, data, experiments and results were produced during the sprint. Claude (Anthropic) wrote most of the code and drafts under the first author's direction; the first author made the design decisions and is responsible for all content.

## License

Code: MIT. Our generated items and logs: CC BY 4.0. PopQA and Wikidata keep their own licenses.
