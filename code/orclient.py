"""OpenRouter client: provider-pinned, temperature 0, cached and logged per call."""
import asyncio, hashlib, json, os, time
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "data" / "calls.jsonl"
URL = "https://openrouter.ai/api/v1/chat/completions"

PROVIDERS = {
    "openai/gpt-4o-mini-2024-07-18": "OpenAI",
    "meta-llama/llama-3.3-70b-instruct": "CoreWeave",
    "qwen/qwen-2.5-72b-instruct": "DeepInfra",
    "deepseek/deepseek-chat-v3.1": None,          # generator (not tested)
    "mistralai/mistral-small-3.2-24b-instruct": None,  # checker / judge (not tested)
}
TESTED = list(PROVIDERS)[:3]


def _key():
    k = os.environ.get("OPENROUTER_API_KEY")
    if not k:
        envf = next((p for p in (ROOT / ".env", ROOT.parents[1] / ".env") if p.exists()), None)
        for line in (envf.read_text().splitlines() if envf else []):
            if line.startswith("OPENROUTER_API_KEY="):
                k = line.split("=", 1)[1].strip()
    return k


def _load_cache():
    cache = {}
    if LOG.exists():
        for line in LOG.open():
            r = json.loads(line)
            if r.get("content") is not None:
                cache[r["key"]] = r
    return cache


class Client:
    def __init__(self, concurrency=24):
        self.sem = asyncio.Semaphore(concurrency)
        self.cache = _load_cache()
        self.http = httpx.AsyncClient(timeout=90, headers={"Authorization": f"Bearer {_key()}"})
        self.logf = LOG.open("a")

    async def ask(self, model, prompt, max_tokens=40, tag="", rep=0, temperature=0):
        body = {"model": model, "temperature": temperature, "top_p": 1, "seed": 0,
                "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}
        prov = PROVIDERS.get(model)
        if prov:
            body["provider"] = {"order": [prov], "allow_fallbacks": False}
        key = hashlib.sha256(json.dumps([body, rep], sort_keys=True).encode()).hexdigest()
        if key in self.cache:
            return self.cache[key]["content"]
        async with self.sem:
            for attempt in range(6):
                try:
                    r = await self.http.post(URL, json=body)
                    d = r.json()
                    if "choices" in d:
                        content = d["choices"][0]["message"]["content"] or ""
                        rec = {"key": key, "tag": tag, "rep": rep, "request": body, "content": content,
                               "provider": d.get("provider"), "response_model": d.get("model"),
                               "id": d.get("id"), "system_fingerprint": d.get("system_fingerprint"),
                               "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                        self.cache[key] = rec
                        self.logf.write(json.dumps(rec) + "\n"); self.logf.flush()
                        return content
                    err = d.get("error")
                except Exception as e:  # network
                    err = str(e)
                await asyncio.sleep(2 ** attempt)
            self.logf.write(json.dumps({"key": key, "tag": tag, "request": body, "content": None, "error": str(err)}) + "\n")
            return None

    async def close(self):
        await self.http.aclose(); self.logf.close()
