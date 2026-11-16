"""30 judge decisions (not alias matches) for the author to hand-check. Writes results/judge_check.csv."""
import json, random, csv
from orclient import ROOT
items = {it["id"]: it for f in ("items_ok.jsonl", "fresh_items.jsonl") for it in map(json.loads, open(ROOT / "data" / f))}
R = [json.loads(l) for l in open(ROOT / "data/graded.jsonl")]
J = [r for r in R if r.get("how") == "judge" and r["kind"] in ("neutral", "rewording")]
random.Random(1).shuffle(J)
(ROOT / "results").mkdir(exist_ok=True)
with open(ROOT / "results/judge_check.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["n", "question", "accepted_answers", "model_answer", "judge_says_correct", "YOUR_VERDICT (yes/no)"])
    for i, r in enumerate(J[:30]):
        it = items[r["item"]]; w.writerow([i + 1, it["question"], "; ".join(it["answers"][:5]), r["ans"], "yes" if r["correct"] else "no", ""])
print("wrote", min(30, len(J)), "of", len(J), "judge decisions")
