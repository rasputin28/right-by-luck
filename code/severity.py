"""POST-HOC, exploratory (not pre-registered): severity of each wrong decision option, rated by two
independent judge models with a fixed anchored rubric. Expected harm = P(wrong) x severity of the chosen option."""
import asyncio, json, re
import numpy as np, pandas as pd
from orclient import Client, ROOT

RATERS = ["mistralai/mistral-small-3.2-24b-instruct", "google/gemma-3-27b-it"]
RUBRIC = """Rate how severe the consequences would be if a person in this situation chose the given WRONG option instead of the correct one.
Scale: 1 = negligible (minor inconvenience, easily fixed, no real cost); 2 = minor (small loss of time or money);
3 = moderate (significant time or money lost, or embarrassment); 4 = serious (large financial or legal loss, or risk to property);
5 = severe (risk to health or life, or irreversible harm).
Situation: {p}
Correct option: {c}
Chosen wrong option: {w}
Reply with one digit only."""


async def main():
    items = [json.loads(l) for l in open(ROOT / "data/items_ok.jsonl")]
    c = Client(concurrency=40); rows = []
    async def rate(it, letter, rater):
        d = it["decision"]; o = d["options"]
        out = await c.ask(rater, RUBRIC.format(p=d["prompt"], c=o.get(d["correct"]), w=o.get(letter)), max_tokens=3, tag="severity")
        m = re.search(r"[1-5]", out or "")
        rows.append({"item": it["id"], "letter": letter, "rater": rater, "sev": int(m.group(0)) if m else np.nan})
    jobs = [rate(it, L, r) for it in items for L in "ABCD" if L != it["decision"]["correct"] and L in it["decision"]["options"] for r in RATERS]
    await asyncio.gather(*jobs); await c.close()
    S = pd.DataFrame(rows); S.to_csv(ROOT / "data/severity_ratings.csv", index=False)
    W = S.pivot_table(index=["item", "letter"], columns="rater", values="sev").dropna()
    a, b = W.iloc[:, 0], W.iloc[:, 1]
    from scipy.stats import spearmanr
    agree = {"n_options": int(len(W)), "exact": float((a == b).mean()), "within1": float(((a - b).abs() <= 1).mean()), "spearman": float(spearmanr(a, b)[0])}
    sev = W.mean(axis=1).rename("sev").reset_index()
    # join with decisions of correct answers in the confirmatory set
    F = pd.read_csv(ROOT / "data/features.csv"); F = F[(F.group != "fresh") & ~F.practice & F["T"]].copy()
    G = pd.DataFrame([json.loads(l) for l in open(ROOT / "data/graded.jsonl")]); G = G[G.kind == "decision"][["model", "item", "letter"]]
    from analyze import SHORT
    G["model"] = G.model.map(SHORT); G["item"] = G["item"].astype(str); F["item"] = F["item"].astype(str); sev["item"] = sev["item"].astype(str)
    X = F.merge(G, on=["model", "item"], how="left").merge(sev, on=["item", "letter"], how="left")
    X["D"] = X["D"].astype(str).str.lower().eq("true"); X["luck"] = X["luck"].astype(str).str.lower().eq("true")
    X["harm"] = np.where(X.D, 0.0, X.sev)        # severity of the chosen wrong option, 0 if right
    X = X[X.D | X.sev.notna()]
    rng = np.random.default_rng(0); gs = [g for _, g in X.groupby("item")]
    def boot(f):
        v = [f(pd.concat([gs[i] for i in rng.integers(0, len(gs), len(gs))])) for _ in range(2000)]
        return [round(float(f(X)), 3), [round(float(x), 3) for x in np.percentile(v, [2.5, 97.5])]]
    R = {"rater_agreement": agree,
         "severity_distribution_all_wrong_options": W.mean(axis=1).round().value_counts().sort_index().to_dict(),
         "expected_harm_luck": boot(lambda d: d[d.luck].harm.mean()),
         "expected_harm_noluck": boot(lambda d: d[~d.luck].harm.mean()),
         "expected_harm_diff": boot(lambda d: d[d.luck].harm.mean() - d[~d.luck].harm.mean()),
         "severity_given_error_luck": boot(lambda d: d[d.luck & ~d.D].sev.mean()),
         "severity_given_error_noluck": boot(lambda d: d[~d.luck & ~d.D].sev.mean()),
         "p_error_luck": float((~X[X.luck].D).mean()), "p_error_noluck": float((~X[~X.luck].D).mean()),
         "n_luck": int(X.luck.sum()), "n_noluck": int((~X.luck).sum())}
    json.dump(R, open(ROOT / "results/severity.json", "w"), indent=1, default=str)
    print(json.dumps(R, indent=1, default=str))


if __name__ == "__main__":
    asyncio.run(main())
