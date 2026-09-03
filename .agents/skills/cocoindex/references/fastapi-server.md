# FastAPI Server + CocoIndex v1 App

The canonical pattern for a CocoIndex v1 App that exposes a query
endpoint over HTTP. The CocoIndex app runs in live mode in the
background; the FastAPI server serves queries on top.

## Pattern

```python
# main.py
import asyncio
import pathlib
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cocoindex as coco
from cocoindex.connectors import localfs, lancedb
# ... (CocoIndex app defined as in SKILL.md Step 4)

# 1. Start the CocoIndex app in live mode in a background task
@asynccontextmanager
async def lifespan(app: FastAPI):
    coco.init()
    app_main_task = asyncio.create_task(app_main_flow.update_async(...))  # pseudo
    yield
    app_main_task.cancel()

app = FastAPI(lifespan=lifespan)

class Query(BaseModel):
    text: str
    top_k: int = 5

class Hit(BaseModel):
    filename: str
    text: str
    score: float

@app.post("/search", response_model=list[Hit])
async def search(query: Query) -> list[Hit]:
    # Embed the query
    embedder = await coco.use_context(EMBEDDER)
    query_vec = await embedder.embed(query.text)

    # Open the LanceDB table and search
    conn = await coco.use_context(LANCE_DB)
    table = await conn.open_table("my_table")
    results = await (await table.search(query_vec, vector_column_name="embedding")).limit(query.top_k).to_list()
    return [
        Hit(filename=r["filename"], text=r["text"], score=1.0 - r["_distance"])
        for r in results
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## KCG examples

- `cocoindex/image_search/pipeline.py` (deleted
  with the docs but the pattern is the same) — CLIP embeddings +
  Qdrant + FastAPI
- `cocoindex/image_search_colpali/pipeline.py` —
  ColPali multi-vector + Qdrant MaxSim + FastAPI
- `agents/api/_cianfhoghlaim_api/routes/search.py` — the KCG `/search/semantic`
  endpoint (FastAPI route that hits the v1 leabharlann embeddings)

## Deployment

The FastAPI server + CocoIndex app can be deployed via:

- Docker (recommended; the `agents/api/_cianfhoghlaim_api` ships a `Dockerfile`)
- `dagster-modal` (the Dagster integration that runs the code on
  Modal — see the `dagster` skill)
- Plain `uvicorn main:app` for local dev
