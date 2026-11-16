"""Pre-registered analysis. Writes data/features.csv, results/results.json, results/*.png."""
import json
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict, GroupKFold
from sklearn.metrics import roc_auc_score
from orclient import ROOT

OUT = ROOT / "results"; OUT.mkdir(exist_ok=True)
B = int(__import__("os").environ.get("BOOT", 2000)); rng = np.random.default_rng(0)
SHORT = {"openai/gpt-4o-mini-2024-07-18": "GPT-4o-mini", "meta-llama/llama-3.3-70b-instruct": "Llama-3.3-70B", "qwen/qwen-2.5-72b-instruct": "Qwen2.5-72B"}


def features():
    items = {it["id"]: it for f in ("items_ok.jsonl", "fresh_items.jsonl") for it in map(json.loads, open(ROOT / "data" / f))}
    G = pd.DataFrame([json.loads(l) for l in open(ROOT / "data/graded.jsonl")])
    rows = []
    for (m, iid), g in G.groupby(["model", "item"]):
        it = items[iid]; k = lambda kind: g[g.kind == kind].sort_values(["idx", "rep"])
        n0 = k("neutral").iloc[0]; rw = k("rewording"); nb = k("neighbour"); ct = k("control"); rp = k("repeat")
        T = bool(n0.correct)
        row = {"model": SHORT[m], "item": iid, "group": it["group"], "prop": it["prop"], "popbin": it.get("popbin", -1),
               "practice": it.get("order", 999) < 30 and it["group"] != "fresh",
               "T": T, "conf": n0.conf, "rw_n": len(rw), "rw_correct": int(rw.correct.sum()),
               "rw_pass": bool(rw.correct.all()) if len(rw) else np.nan,
               "nb_same": int(nb.same_as_orig_gold.sum()), "nb_pass": bool((~nb.same_as_orig_gold.astype(bool)).all()),
               "nb_correct": int(nb.correct.sum()),
               "control_changed": bool(ct.iloc[0].correct) != T,
               "repeat_changed": (float((rp.correct.astype(bool) != T).mean()) if len(rp) else np.nan)}
        row["local_rel"] = (row["rw_correct"] + row["nb_correct"]) / max(1, len(rw) + len(nb))
        row["luck"] = T and not (row["rw_pass"] and row["nb_pass"])
        row["luck_rw"] = T and not row["rw_pass"]; row["luck_nb"] = T and not row["nb_pass"]
        row["wrong_by_luck"] = (not T) and row["rw_correct"] >= 3
        row["strong_trace"] = row["luck"] and row["nb_same"] > 0
        if it["group"] != "fresh":
            row["H"] = bool(k("pressure").iloc[0].correct); row["D"] = bool(k("decision").iloc[0].correct)
        # H4: confidence on wrong nearby answers vs original
        if row["luck"]:
            wrong_nearby = pd.concat([rw[~rw.correct.astype(bool)], nb[nb.same_as_orig_gold.astype(bool)]])
            cw = wrong_nearby.conf.dropna()
            row["conf_wrong_nearby"] = cw.mean() if len(cw) else np.nan
        rows.append(row)
    F = pd.DataFrame(rows); F.to_csv(ROOT / "data/features.csv", index=False); return F


def boot(df, stat, by="item"):
    groups = [g for _, g in df.groupby(by)]
    vals = []
    for _ in range(B):
        s = rng.integers(0, len(groups), len(groups)); d = pd.concat([groups[i] for i in s])
        try: vals.append(stat(d))
        except Exception: pass
    v = np.array([x for x in vals if x is not None and not np.isnan(x)])
    return float(stat(df)), float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def main():
    F = features(); R = {}
    P = F[(F.group != "fresh") & ~F.practice]          # confirmatory set
    R["n_items"] = int(P.item.nunique()); R["n_rows"] = len(P)
    # noise floor: per-check instability from control + repeat, among correct answers
    per_model = {}
    for m, g in P.groupby("model"):
        c = g[g["T"]]
        e_ctrl = c.control_changed.mean(); e_rep = c.repeat_changed.dropna().mean() if c.repeat_changed.notna().any() else 0.0
        e = min(1, e_ctrl + e_rep); floor = 1 - (1 - e) ** 7
        acc = boot(g, lambda d: d["T"].mean())
        lr = boot(c, lambda d: d.luck.mean())
        net = boot(c, lambda d: d.luck.mean() - (1 - (1 - min(1, d.control_changed.mean() + (d.repeat_changed.dropna().mean() if d.repeat_changed.notna().any() else 0))) ** 7))
        per_model[m] = {"accuracy": acc, "luck_rate": lr, "noise_per_check_control": e_ctrl, "noise_per_check_repeat": e_rep,
                        "noise_floor_item": floor, "luck_net": net, "n_correct": int(len(c)),
                        "luck_rw_only": float(c.luck_rw.mean()), "luck_nb_only": float(c.luck_nb.mean()),
                        "strong_trace_share": float(c[c.luck].strong_trace.mean()) if c.luck.any() else None,
                        "wrong_by_luck_share_of_wrong": float(g[~g["T"]].wrong_by_luck.mean()),
                        "share_no_luck_found": float((g["T"] & ~g.luck).mean())}
        for grp in ("fallback", "open"):
            cg = c[c.group == grp]
            per_model[m][f"luck_rate_{grp}"] = boot(cg, lambda d: d.luck.mean()) if len(cg) > 5 else None
    R["per_model"] = per_model
    C0 = P[P["T"]]
    # POST-HOC (not pre-registered): per-check failure rates, rewording vs control
    R["posthoc_per_check"] = {
        "rewording_fail_per_check": boot(C0, lambda d: 1 - (d.rw_correct / d.rw_n).mean()),
        "control_fail_per_check": boot(C0, lambda d: d.control_changed.mean()),
        "repeat_fail_per_call": boot(C0[C0.repeat_changed.notna()], lambda d: d.repeat_changed.mean()),
        "neighbour_same_answer_per_check": boot(C0, lambda d: (d.nb_same / 3).mean()),
        "rw_minus_control": boot(C0, lambda d: (1 - (d.rw_correct / d.rw_n).mean()) - d.control_changed.mean())}
    R["posthoc_luck_nb_by_group"] = {g: boot(C0[C0.group == g], lambda d: d.luck_nb.mean()) for g in ("fallback", "open")}
    R["posthoc_luck_nb_fallback_minus_open"] = boot(C0, lambda d: d[d.group == "fallback"].luck_nb.mean() - d[d.group == "open"].luck_nb.mean())
    C = P[P["T"]].copy()
    R["pooled_luck_rate"] = boot(C, lambda d: d.luck.mean())
    R["pos_control_fallback_minus_open"] = boot(C, lambda d: d[d.group == "fallback"].luck.mean() - d[d.group == "open"].luck.mean())
    # fresh-fact control
    Fr = F[F.group == "fresh"]
    R["fresh"] = {"accuracy": float(Fr["T"].mean()), "n_correct": int(Fr["T"].sum()),
                  "flagged_luck_among_correct": float(Fr[Fr["T"]].luck.mean()) if Fr["T"].any() else None,
                  "by_model": {m: {"acc": float(g["T"].mean()), "flag": (float(g[g["T"]].luck.mean()) if g["T"].any() else None)} for m, g in Fr.groupby("model")}}
    # H1: decision accuracy, luck vs no-luck, stratified by group x fame tercile
    C["fame3"] = pd.qcut(C.popbin.rank(method="first"), 3, labels=False)
    def h1(d):
        diffs, w = [], []
        for _, s in d.groupby(["group", "fame3"]):
            a, b = s[~s.luck].D, s[s.luck].D
            if len(a) > 2 and len(b) > 2: diffs.append(a.mean() - b.mean()); w.append(min(len(a), len(b)))
        return np.average(diffs, weights=w) if diffs else np.nan
    R["H1_diff_noluck_minus_luck"] = boot(C, h1)
    R["H1_raw"] = {"D_noluck": float(C[~C.luck].D.mean()), "D_luck": float(C[C.luck].D.mean()), "n_luck": int(C.luck.sum()), "n_noluck": int((~C.luck).sum())}
    # H2: CV AUC, base vs +luck vs +H
    X = pd.get_dummies(C[["model", "group"]]).astype(float); X["popbin"] = C.popbin
    Xl = X.assign(rw_pass=C.rw_pass.astype(float), nb_pass=C.nb_pass.astype(float), local_rel=C.local_rel)
    Xh = X.assign(H=C.H.astype(float))
    Xl1 = X.assign(rw1=[0.0] * len(C))
    y = C.D.astype(int).values; groups = C.item.values; cv = GroupKFold(5)
    pred = lambda Z: cross_val_predict(LogisticRegression(max_iter=2000), Z.values, y, cv=cv, groups=groups, method="predict_proba")[:, 1]
    C["p_base"], C["p_luck"], C["p_H"] = pred(X), pred(Xl), pred(Xh)
    auc = lambda d, col: roc_auc_score(d.D.astype(int), d[col])
    R["H2_auc"] = {"base": auc(C, "p_base"), "luck": auc(C, "p_luck"), "honesty": auc(C, "p_H")}
    R["H2_delta_luck_minus_H"] = boot(C, lambda d: auc(d, "p_luck") - auc(d, "p_H"))
    # H3: AUROC of confidence separating no-luck (1) from luck (0)
    Cc = C[C.conf.notna()]
    R["H3_auroc"] = boot(Cc, lambda d: roc_auc_score((~d.luck).astype(int), d.conf))
    R["H3_distinct_conf_values"] = int(Cc.conf.nunique())
    # H4: confidence on wrong nearby answers minus original confidence
    L = C[C.luck & C.conf_wrong_nearby.notna() & C.conf.notna()].copy() if "conf_wrong_nearby" in C else C.iloc[:0]
    R["H4_conf_diff"] = boot(L, lambda d: (d.conf_wrong_nearby - d.conf).mean()) if len(L) > 10 else None
    R["H4_n"] = int(len(L))
    # contamination indicator: accuracy original vs rewordings
    R["contamination_orig_minus_rewording_acc"] = {m: float(g["T"].mean() - (g.rw_correct / g.rw_n).mean()) for m, g in P.groupby("model")}
    json.dump(R, open(OUT / "results.json", "w"), indent=1, default=float)
    print(json.dumps(R, indent=1, default=lambda x: round(float(x), 3)))


if __name__ == "__main__":
    main()
