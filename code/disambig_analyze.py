"""POST-HOC: compare luck with and without Wikidata disambiguation of subject names."""
import json, numpy as np, pandas as pd
from orclient import ROOT
from analyze import SHORT
rng = np.random.default_rng(0)
items = {it["id"]: it for it in map(json.loads, open(ROOT / "data/items_ok.jsonl"))}
practice = {i for i, it in items.items() if it["order"] < 30}

def feats(fn):
    G = pd.DataFrame([json.loads(l) for l in open(ROOT / "data" / fn)])
    G = G[G.kind.isin(["neutral", "rewording", "neighbour", "control"]) & (G.rep == 0)]
    rows = []
    for (m, iid), g in G.groupby(["model", "item"]):
        if iid in practice or str(iid).startswith("fresh"): continue
        T = bool(g[g.kind == "neutral"].correct.iloc[0]); rw = g[g.kind == "rewording"]; nb = g[g.kind == "neighbour"]
        rows.append({"model": SHORT[m], "item": iid, "T": T, "rw_fail": 1 - rw.correct.mean(), "ctrl": bool(g[g.kind == "control"].correct.iloc[0]) != T,
                     "luck_rw": T and not rw.correct.all(), "luck_nb": T and bool(nb.same_as_orig_gold.astype(bool).any()),
                     "luck": T and (not rw.correct.all() or bool(nb.same_as_orig_gold.astype(bool).any()))})
    return pd.DataFrame(rows)

def boot(df, f):
    gs = [g for _, g in df.groupby("item")]; v = [f(pd.concat([gs[i] for i in rng.integers(0, len(gs), len(gs))])) for _ in range(2000)]
    return round(f(df), 3), np.percentile(v, [2.5, 97.5]).round(3).tolist()

LEAK = set(json.load(open(ROOT / "data/disambig_leak_ids.json")))
R = {}
for name, fn, keep in [("original_all", "graded.jsonl", None), ("disambiguated_all", "graded_disambig.jsonl", None),
                       ("original_noleak", "graded.jsonl", "noleak"), ("disambiguated_noleak", "graded_disambig.jsonl", "noleak")]:
    F = feats(fn)
    if keep: F = F[~F.item.isin(LEAK)]
    C = F[F["T"]]
    R[name] = {"accuracy": boot(F, lambda d: d["T"].mean()), "luck_rate": boot(C, lambda d: d.luck.mean()),
               "wording_luck": boot(C, lambda d: d.luck_rw.mean()), "neighbour_luck": boot(C, lambda d: d.luck_nb.mean()),
               "rw_fail_per_check": boot(C, lambda d: d.rw_fail.mean()), "control_per_check": boot(C, lambda d: d.ctrl.mean()),
               "rw_minus_control": boot(C, lambda d: d.rw_fail.mean() - d.ctrl.mean()),
               "per_model_luck": {m: round(g[g["T"]].luck.mean(), 3) for m, g in F.groupby("model")}}
json.dump(R, open(ROOT / "results/disambig.json", "w"), indent=1)
for k, v in R.items(): print(k, "n_items", None, {a: b for a, b in v.items() if a != "per_model_luck"})
