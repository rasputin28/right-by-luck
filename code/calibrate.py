"""Calibration: accuracy of tested models by fame bin, on items NOT used in the study."""
import asyncio, json, random, re, sys
import pandas as pd
from orclient import Client, TESTED, ROOT

FALLBACK = ["sport", "religion", "country", "occupation"]
OPEN = ["director", "author", "composer", "place of birth"]
NEUTRAL = ("Answer the question with a short answer, then give your confidence from 0 to 100 that your answer is correct. "
           "Format: ANSWER: <answer> | CONFIDENCE: <0-100>\nQuestion: {q}")


def load():
    d = pd.read_parquet(ROOT / "data/sources/popqa_test.parquet")
    d["ans"] = d["possible_answers"].apply(json.loads)
    d["leak"] = [any(isinstance(a, str) and len(a) > 3 and a.lower() in str(s).lower() for a in A) for s, A in zip(d.subj, d.ans)]
    d = d[~d.leak & d.prop.isin(FALLBACK + OPEN)].copy()
    d["group"] = d.prop.map(lambda p: "fallback" if p in FALLBACK else "open")
    return d


def parse(txt):
    if not txt: return "", None
    m = re.search(r"ANSWER:\s*(.*?)\s*(\||$)", txt, re.S); c = re.search(r"CONFIDENCE:\s*(\d+)", txt)
    return (m.group(1).strip() if m else txt.strip()), (int(c.group(1)) if c else None)


def match(ans, golds):
    a = re.sub(r"[^a-z0-9 ]", "", ans.lower()).strip()
    return any(g and (re.sub(r"[^a-z0-9 ]", "", g.lower()).strip() in a) for g in golds if isinstance(g, str) and len(g) > 1)


async def main():
    d = load(); random.seed(7)
    d["popbin"] = pd.qcut(d.s_pop.rank(method="first"), 6, labels=False)
    cal = d.sample(frac=1, random_state=7).groupby(["prop", "popbin"]).head(6)
    cal[["id"]].to_csv(ROOT / "data/calibration_ids.csv", index=False)
    c = Client()
    rows = []
    async def one(r, m):
        out = await c.ask(m, NEUTRAL.format(q=r.question), tag="calib")
        a, conf = parse(out); rows.append({"id": r.id, "model": m, "prop": r.prop, "group": r.group, "popbin": r.popbin, "correct": match(a, r.ans)})
    await asyncio.gather(*[one(r, m) for r in cal.itertuples() for m in TESTED])
    await c.close()
    res = pd.DataFrame(rows); res.to_csv(ROOT / "data/calibration.csv", index=False)
    print(len(cal), "items")
    print(res.groupby(["group", "popbin"]).correct.mean().unstack().round(2))
    print(res.groupby(["model"]).correct.mean().round(2))


if __name__ == "__main__":
    asyncio.run(main())
