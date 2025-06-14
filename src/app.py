import os
import toml
from fastapi import FastAPI, Request
import httpx

# Load config
config = toml.load(os.path.join(os.path.dirname(__file__), "config.toml"))
ollama_url = config["llm"]["api"]
ollama_header = config["llm"]["header"]

app = FastAPI()

@app.post("/api/search")
async def search_handler(req: Request):
    data = await req.json()
    query = data.get("query", "")

    # Call Ollama LLM for summarization
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            ollama_url,
            headers={"Authorization": ollama_header, "Content-Type": "application/json"},
            json={"prompt": f"Summarize and cite for query: {query}", "max_tokens": 300}
        )
        resp.raise_for_status()
        return {"llm_response": resp.json()}
