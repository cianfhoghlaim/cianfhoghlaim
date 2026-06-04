"""
FastAPI wrapper for the 3 pipeline modules.

Pipelines: dialect_classifier, irish_document_scanner, transcript_aligner.

GPU-accelerated via Apple Silicon MPS (M4 Max) or CUDA (Hetzner).
"""
from fastapi import FastAPI
app = FastAPI(title="meaisínfhoghlaim pipelines", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "ok", "pipelines": 3}
