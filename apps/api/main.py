from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Aletheia API", version="0.1.0")

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@app.get('/health')
def health():
    return {"status": "ok", "service": "aletheia-api"}

@app.post('/search')
def search(req: SearchRequest):
    # Placeholder response (to wire frontend/integration early)
    return {
        "query": req.query,
        "results": [
            {
                "text": "Placeholder chunk. Implement hybrid retrieval next.",
                "source_id": "demo-source",
                "title": "Demo Book",
                "chapter": "1",
                "page_start": 1,
                "page_end": 1,
                "score": 0.0,
            }
        ][: req.top_k],
    }
