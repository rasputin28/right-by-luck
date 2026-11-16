"""POST-HOC robustness (not pre-registered): rerun the luck battery with each subject disambiguated
by its Wikidata description, e.g. "Alexander I (emperor of Russia)". Writes data/responses_disambig.jsonl."""
import asyncio, json
import httpx, pandas as pd
from orclient import Client, TESTED, ROOT
from run import NEUTRAL, control

DIS_NOTE = " (If the name could refer to more than one entity, say which one you mean.)"


async def descriptions(qids):
    out = {}
    async with httpx.AsyncClient(timeout=120, headers={"User-Agent": "research-script/0.1 (github.com/rasputin28/right-by-luck)",
                                                       "Accept": "application/sparql-results+json"}) as h:
        for i in range(0, len(qids), 300):
            vals = " ".join("wd:" + q for q in qids[i:i + 300])
            query = f'SELECT ?item ?d WHERE {{ VALUES ?item {{ {vals} }} ?item schema:description ?d . FILTER(lang(?d)="en") }}'
            r = await h.post("https://query.wikidata.org/sparql", data={"query": query})
            for b in r.json()["results"]["bindings"]:
                out[b["item"]["value"].rsplit("/", 1)[-1]] = b["d"]["value"]
    return out


async def main():
    pq = pd.read_parquet(ROOT / "data/sources/popqa_test.parquet")
    uri = {int(i): u.rsplit("/", 1)[-1] for i, u in zip(pq.id, pq.s_uri)}
    subj = {int(i): s for i, s in zip(pq.id, pq.subj)}
    items = [json.loads(l) for l in open(ROOT / "data/items_ok.jsonl")]
    ids = {it["id"] for it in items} | {n["id"] for it in items for n in it["neighbours"]}
    desc = await descriptions(sorted({uri[i] for i in ids}))
    json.dump({str(i): desc.get(uri[i], "") for i in ids}, open(ROOT / "data/sources/wikidata_descriptions.json", "w"))

    def dis(text, iid, name):
        d = desc.get(uri[iid], "")
        return text.replace(name, f"{name} ({d})", 1) if d and isinstance(name, str) and name and name in text else text

    c = Client(concurrency=40); out = []
    async def q(m, it, kind, idx, prompt):
        a = await c.ask(m, prompt, max_tokens=40, tag="dis_" + kind)
        out.append({"model": m, "item": it["id"], "group": it["group"], "kind": kind, "idx": idx, "rep": 0, "prompt": prompt, "answer": a})
    jobs = []
    for m in TESTED:
        for it in items:
            s = subj[it["id"]]
            jobs.append(q(m, it, "neutral", 0, NEUTRAL.format(q=dis(it["question"], it["id"], s))))
            jobs.append(q(m, it, "control", 0, NEUTRAL.format(q=control(dis(it["question"], it["id"], s)))))
            for i, r in enumerate(it["rewordings"]):
                name = it["alias"] if it.get("alias_used") and i == 0 else s
                jobs.append(q(m, it, "rewording", i, NEUTRAL.format(q=dis(r, it["id"], name))))
            for i, n in enumerate(it["neighbours"]):
                jobs.append(q(m, it, "neighbour", i, NEUTRAL.format(q=dis(n["question"], n["id"], subj[n["id"]]))))
    print("calls", len(jobs), "| subjects with description", sum(bool(desc.get(uri[i])) for i in ids), "/", len(ids), flush=True)
    await asyncio.gather(*jobs); await c.close()
    with open(ROOT / "data/responses_disambig.jsonl", "w") as f:
        for r in out: f.write(json.dumps(r) + "\n")
    print("done; missing", sum(r["answer"] is None for r in out))


if __name__ == "__main__":
    asyncio.run(main())
