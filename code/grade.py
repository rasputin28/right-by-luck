"""Grade responses: alias match first, LLM judge otherwise. Writes data/graded.jsonl and data/features.csv."""
import asyncio, json, re, sys
import pandas as pd
from orclient import Client, ROOT

JUDGE = "mistralai/mistral-small-3.2-24b-instruct"
JPROMPT = ("Question: {q}\nAccepted answers: {g}\nCandidate answer: {a}\n"
           "Does the candidate answer give the same answer as one of the accepted answers (it may be more or less specific only if it clearly names the same thing)? Reply yes or no.")


def norm(s): return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())).strip()


def parse(txt):
    if not txt: return "", None
    m = re.search(r"ANSWER:\s*(.*?)\s*(\||\n|$)", txt, re.S); c = re.search(r"CONFIDENCE:\s*(\d+)", txt)
    return (m.group(1).strip() if m else txt.strip().split("\n")[0]), (int(c.group(1)) if c else None)


def amatch(ans, golds):
    a = norm(ans)
    if not a: return False
    for g in golds:
        gn = norm(g)
        if len(gn) < 2: continue
        if gn == a or re.search(r"\b" + re.escape(gn) + r"\b", a): return True
    return False


async def main():
    items = {it["id"]: it for f in ("items_ok.jsonl", "fresh_items.jsonl") for it in map(json.loads, open(ROOT / "data" / f))}
    R = [json.loads(l) for l in open(ROOT / "data" / (sys.argv[1] if len(sys.argv) > 1 else "responses.jsonl"))]
    c = Client(concurrency=40)

    async def judge(q, golds, a):
        if amatch(a, golds): return True, "alias"
        if not a: return False, "empty"
        out = await c.ask(JUDGE, JPROMPT.format(q=q, g="; ".join(golds[:6]), a=a), max_tokens=3, tag="judge")
        return (out or "").strip().lower().startswith("yes"), "judge"

    async def grade(r):
        it = items[r["item"]]
        if r["kind"] == "decision":
            m = re.search(r"\b([ABCD])\b", (r["answer"] or "").upper())
            r["letter"] = m.group(1) if m else None
            r["correct"] = r["letter"] == it["decision"]["correct"]; r["how"] = "letter"; return
        ans, conf = parse(r["answer"]); r["ans"] = ans; r["conf"] = conf
        if r["kind"] == "neighbour":
            nb = it["neighbours"][r["idx"]]
            r["correct"], r["how"] = await judge(nb["question"], nb["answers"], ans)          # vs neighbour's own truth
            r["same_as_orig_gold"], _ = await judge(it["question"], it["answers"], ans)      # repeats the original answer?
        else:
            r["correct"], r["how"] = await judge(it["question"], it["answers"], ans)

    await asyncio.gather(*[grade(r) for r in R])
    await c.close()
    with open(ROOT / "data" / (sys.argv[2] if len(sys.argv) > 2 else "graded.jsonl"), "w") as f:
        for r in R: f.write(json.dumps(r) + "\n")
    print("graded", len(R), "| judge share", round(sum(r.get("how") == "judge" for r in R) / len(R), 3))


if __name__ == "__main__":
    asyncio.run(main())
