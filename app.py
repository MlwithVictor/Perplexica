import os
from fastapi import FastAPI, Request
import httpx

# Load environment or fallback to config.toml
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

    # First do web search via SearXNG
    async with httpx.AsyncClient() as client:
        search_resp = await client.get(
            SEARX_URL,
            params={"q": prompt, "format": "json"}
        )
        results = search_resp.json().get("results", [])[:3]
        snippets = [r.get("content") for r in results]

        # Combine into LLM prompt
        llm_prompt = f"Web snippets: {snippets}\nUser query: {prompt}"

        llm_resp = await client.post(
            OLLAMA_URL,
            headers={
                "Authorization": OLLAMA_AUTH,
                "Content-Type": "application/json"
            },
            json={"model": MODEL, "prompt": llm_prompt}
        )
        llm_data = llm_resp.json()

    return {"search_results": results, "llm_response": llm_data}
