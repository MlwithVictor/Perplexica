import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_AUTH = os.getenv("OLLAMA_AUTH")
MODEL = os.getenv("MODEL")

# ✅ Stable SearXNG instances (from https://searx.space/)
SEARXNG_API_URLS = [
    "https://search.bus-hit.me/search",
    "https://searx.thegpm.org/search",
    "https://searx.riverside.rocks/search",
    "https://search.snopyta.org/search"
]

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}

async def fetch_search_results(prompt: str):
    """
    Query multiple SearXNG endpoints in parallel and return the first valid result list.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; PerplexicaBot/1.0)"
    }
    params = {
        "q": prompt,
        "format": "json"
    }

    async with httpx.AsyncClient(timeout=10, headers=headers) as client:
        tasks = [client.get(url, params=params) for url in SEARXNG_API_URLS]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    for resp in responses:
        if isinstance(resp, Exception):
            print(f"Search request error: {resp}")
            continue
        try:
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])[:3]
            if results:
                return results
        except Exception as e:
            print(f"Invalid JSON or no results from {getattr(resp, 'url', 'unknown URL')}: {e}")
            continue
    return []

@app.post("/api/search")
async def search_endpoint(request: Request):
    req = await request.json()
    prompt = req.get("query", "")
    if not prompt:
        return JSONResponse(status_code=400, content={"error": "Missing query"})

    # STEP 1: Parallel web search
    results = await fetch_search_results(prompt)
    snippets = [r.get("content") for r in results if r.get("content")]
    if not snippets:
        return JSONResponse(status_code=502, content={"error": "All SearXNG endpoints failed."})

    # STEP 2: LLM Processing via Ollama
    llm_prompt = f"""Web snippets: {snippets}
User query: {prompt}"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            llm_resp = await client.post(
                OLLAMA_URL,
                headers={
                    "Authorization": OLLAMA_AUTH,
                    "Content-Type": "application/json"
                },
                json={"model": MODEL, "prompt": llm_prompt}
            )
            llm_resp.raise_for_status()
            llm_data = llm_resp.json()
    except Exception as e:
        print(f"Ollama error: {e}")
        return JSONResponse(status_code=502, content={"error": "LLM processing failed"})

    return {"search_results": results, "llm_response": llm_data}
