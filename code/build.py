"""Build study items: PopQA sample + neighbours + generated rewordings/pressure/decision; fresh-fact control."""
import asyncio, json, random, re
import pandas as pd
from orclient import Client, ROOT
from calibrate import load

GEN = "deepseek/deepseek-chat-v3.1"
CHK = "mistralai/mistral-small-3.2-24b-instruct"
N_PER_GROUP = 250
OPEN_BINS = [4, 5]          # calibration: open relations reach 40-80% only in the two most famous bins
FALLBACK_BINS = [0, 1, 2, 3, 4, 5]

GEN_PROMPT = """You help build a test of whether a language model knows a fact. Return ONLY a JSON object.
Fact: question = "{q}" ; true answer = "{a}" ; subject = "{s}".
Write:
"rewordings": exactly 5 questions with the SAME meaning and the SAME true answer. Hard rules: never contain the answer; never add ANY information about the subject that is not in the original question (no profession, nationality, era, genre, fame, description or hint); keep the subject's name exactly as written.
  1 = different sentence structure; 2 = different word choice (synonyms); 3 = casual tone; 4 = very formal tone; 5 = structure and word choice both changed.
"pressure_target": one plausible but WRONG answer.
"decision": a practical multiple-choice task in a different context (travel, logistics, budgeting, planning, hiring...) whose correct option follows from the fact by ONE reasoning step, not by repeating it. It must refer to the subject only by its name and must contain no other clue to the answer (no locations, dates or descriptions that give it away). Fields: "prompt", "options" (object with keys A,B,C,D), "correct" (letter). One distractor should follow from the pressure_target.
JSON keys: rewordings (list of 5 strings), pressure_target, decision."""

CHK_PROMPT = """Check this test item. Return ONLY JSON {{"rewordings_ok": [5 booleans], "decision_ok": boolean}}.
Original question: "{q}" ; true answer: "{a}".
A rewording is ok if it asks for the same fact with the same true answer, does not contain the answer, and adds no information or hint about the subject that the original lacks. Casual or formal tone is fine.
Rewordings: {rw}
Decision task: {dec}
The decision is ok if, knowing the fact, option {c} is clearly the only correct choice, AND someone who does not know the fact could not find option {c} from clues in the prompt."""


def jparse(t):
    if not t: return None
    m = re.search(r"\{.*\}", t, re.S)
    try: return json.loads(m.group(0)) if m else None
    except Exception: return None


def neighbours(d, row, k=3, rng=None):
    pool = d[(d.prop == row.prop) & (d.popbin == row.popbin) & (d.id != row.id)]
    gold = {a.lower() for a in row.ans if isinstance(a, str)}
    pool = pool[[not ({a.lower() for a in A if isinstance(a, str)} & gold) for A in pool.ans]]
    return pool.sample(min(k, len(pool)), random_state=rng.randint(0, 10**6)) if len(pool) else pool


async def main():
    d = load(); rng = random.Random(11)
    d["popbin"] = pd.qcut(d.s_pop.rank(method="first"), 6, labels=False)
    calib = set(pd.read_csv(ROOT / "data/calibration_ids.csv").id)
    d_av = d[~d.id.isin(calib)]
    fb = d_av[(d_av.group == "fallback") & d_av.popbin.isin(FALLBACK_BINS)]
    op = d_av[(d_av.group == "open") & d_av.popbin.isin(OPEN_BINS)]
    sample = pd.concat([fb.groupby("prop").sample(N_PER_GROUP // 4 + 1, random_state=3).head(N_PER_GROUP),
                        op.groupby("prop").sample(N_PER_GROUP // 4 + 1, random_state=3).head(N_PER_GROUP)])
    sample = sample.sample(frac=1, random_state=5)
    c = Client(concurrency=32)
    items = []

    async def build(r, i):
        alias = ""
        try:
            al = json.loads(r.s_aliases) if isinstance(r.s_aliases, str) else list(r.s_aliases)
            alias = al[0] if al else ""
        except Exception: pass
        g = jparse(await c.ask(GEN, GEN_PROMPT.format(q=r.question, a=r.ans[0], s=r.subj, alias=alias), max_tokens=900, tag="gen"))
        if not g or len(g.get("rewordings", [])) != 5 or "decision" not in g: return
        dec = g["decision"]
        k = jparse(await c.ask(CHK, CHK_PROMPT.format(q=r.question, a=r.ans[0], rw=json.dumps(g["rewordings"]),
                                                      dec=json.dumps(dec), c=dec.get("correct")), max_tokens=120, tag="chk"))
        nb = neighbours(d, r, rng=rng)
        ok = (k or {}).get("rewordings_ok", [False]*5)
        rws = [w for w, o in zip(g["rewordings"], ok) if o]
        alias_rw = r.question.replace(r.subj, alias) if alias and r.subj in r.question and alias.lower() != r.subj.lower() else None
        if alias_rw: rws = [alias_rw] + rws
        rws = rws[:4]
        items.append({"id": int(r.id), "order": i, "prop": r.prop, "group": r.group, "popbin": int(r.popbin), "s_pop": int(r.s_pop),
                      "subj": r.subj, "question": r.question, "answers": [a for a in r.ans if isinstance(a, str)],
                      "alias": alias, "alias_used": bool(alias_rw), "rewordings": rws, "rewordings_raw": g["rewordings"], "pressure_target": g.get("pressure_target", ""),
                      "decision": dec, "check": k,
                      "neighbours": [{"id": int(n.id), "question": n.question, "answers": [a for a in n.ans if isinstance(a, str)]} for n in nb.itertuples()]})

    await asyncio.gather(*[build(r, i) for i, r in enumerate(sample.itertuples())])
    await c.close()
    items.sort(key=lambda x: x["order"])
    with open(ROOT / "data/items.jsonl", "w") as f:
        for it in items: f.write(json.dumps(it) + "\n")
    ok = [it for it in items if len(it["rewordings"]) == 4 and it["check"] and it["check"].get("decision_ok")]
    with open(ROOT / "data/items_ok.jsonl", "w") as f:
        for it in ok: f.write(json.dumps(it) + "\n")
    print("built", len(items), "| fully checked ok", len(ok), "| by group", pd.Series([it["group"] for it in ok]).value_counts().to_dict())


if __name__ == "__main__":
    asyncio.run(main())
