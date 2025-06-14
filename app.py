import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_AUTH = os.getenv("OLLAMA_AUTH")
MODEL = os.getenv("MODEL")
SEARX_URL = os.getenv("SEARXNG_API_URL")

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/api/search")
async def search(query: Request):
    body = await query.json()
    prompt = body.get("query", "")

    if not prompt:
        return JSONResponse(status_code=400, content={"error": "Missing query"})

    # STEP 1: Web Search via SearXNG
    try:
        async with httpx.AsyncClient() as client:
            search_resp = await client.get(
                SEARX_URL,
                params={"q": prompt, "format": "json"},
                timeout=15
            )
            search_resp.raise_for_status()
            print("SearXNG raw response:", search_resp.text)  # DEBUG
            data = search_resp.json()
            results = data.get("results", [])[:3]
            snippets = [r.get("content") for r in results if r.get("content")]
    except Exception as e:
        print("SearXNG error:", str(e))
        return JSONResponse(status_code=502, content={"error": "SearXNG lookup failed"})

    # STEP 2: LLM Processing via Ollama
    try:
        llm_prompt = f"Web snippets: {snippets}\nUser query: {prompt}"
        async with httpx.AsyncClient() as client:
            llm_resp = await client.post(
                OLLAMA_URL,
                headers={
                    "Authorization": OLLAMA_AUTH,
                    "Content-Type": "application/json"
                },
                json={"model": MODEL, "prompt": llm_prompt},
                timeout=30
            )
            llm_resp.raise_for_status()
            print("Ollama raw response:", llm_resp.text)  # DEBUG
            llm_data = llm_resp.json()
    except Exception as e:
        print("Ollama error:", str(e))
        return JSONResponse(status_code=502, content={"error": "LLM processing failed"})

    return {
        "search_results": results,
        "llm_response": llm_data
    }
