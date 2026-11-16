"""Fresh-fact control: Wikidata organisations founded after all tested models' cutoffs."""
import asyncio, json, random, re
from orclient import Client, ROOT
from build import jparse, GEN

SRC = ROOT / "data/sources/wikidata_orgs_2026.json"
ALIASES = {"United States": ["United States", "United States of America", "USA", "US", "U.S.", "America"],
           "United Kingdom": ["United Kingdom", "UK", "U.K.", "Britain", "Great Britain", "England", "Scotland", "Wales", "Northern Ireland"],
           "Germany": ["Germany", "Deutschland"], "Netherlands": ["Netherlands", "Holland"],
           "People's Republic of China": ["China", "People's Republic of China", "PRC"],
           "Czech Republic": ["Czech Republic", "Czechia"], "South Korea": ["South Korea", "Korea", "Republic of Korea"]}
DEMONYMS = {"United States": ["american", "us ", "usa"], "United Kingdom": ["uk", "british", "england", "scotland", "london"],
            "France": ["france", "french", "paris"], "Germany": ["german", "deutsch", "berlin"], "Japan": ["japan", "tokyo", "nippon"],
            "Sweden": ["swed", "stockholm"], "Australia": ["austral", "sydney"], "Canada": ["canad"], "Italy": ["ital"], "Spain": ["spain", "españa", "spanish"]}
REW = """Return ONLY a JSON list of 4 questions that ask the same thing as "In what country is {x}?" with the same answer, using different structure, word choice, casual tone and formal tone. Keep the name "{x}" exactly. Add no information."""


def leaks(name, country):
    n = name.lower()
    if country.lower() in n: return True
    return any(t in n for t in DEMONYMS.get(country, []))


async def main():
    b = json.load(open(SRC))["results"]["bindings"]
    rows = [(x["itemLabel"]["value"], x["countryLabel"]["value"]) for x in b]
    rows = [(n, c) for n, c in rows if not re.fullmatch(r"Q\d+", n) and not leaks(n, c)]
    seen, uniq = set(), []
    for n, c in rows:
        if n not in seen: seen.add(n); uniq.append((n, c))
    rnd = random.Random(13); rnd.shuffle(uniq)
    pick = uniq[:100]
    c = Client(concurrency=32)
    out = []
    async def one(i, n, ctry):
        rws = jparse("{\"r\":" + (await c.ask(GEN, REW.format(x=n), max_tokens=300, tag="fresh_gen") or "[]").strip().strip("`").replace("json", "", 1) + "}")
        rws = (rws or {}).get("r", [])[:4]
        nbs = [u for u in uniq[100:] if u[1] != ctry]
        nb = rnd.sample(nbs, 3)
        out.append({"id": f"fresh_{i}", "order": i, "group": "fresh", "prop": "country", "subj": n,
                    "question": f"In what country is {n}?", "answers": ALIASES.get(ctry, [ctry]), "rewordings": rws,
                    "neighbours": [{"id": f"fresh_nb_{i}_{j}", "question": f"In what country is {m}?", "answers": ALIASES.get(k, [k])} for j, (m, k) in enumerate(nb)]})
    await asyncio.gather(*[one(i, n, ct) for i, (n, ct) in enumerate(pick)])
    await c.close()
    out.sort(key=lambda x: x["order"])
    with open(ROOT / "data/fresh_items.jsonl", "w") as f:
        for it in out: f.write(json.dumps(it) + "\n")
    print("fresh", len(out), "with 4 rewordings", sum(len(x["rewordings"]) == 4 for x in out), "| eligible pool", len(uniq))


if __name__ == "__main__":
    asyncio.run(main())
