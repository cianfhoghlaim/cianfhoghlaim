"""
Embedding Microservice.

FastAPI service for text embedding generation with batching support.
Based on genizah_search embedding service pattern.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# =============================================================================
# Request/Response Models
# =============================================================================


class EmbedRequest(BaseModel):
    """Request for batch embedding."""

    texts: list[str] = Field(..., description="Texts to embed", max_length=100)
    model: str = Field(
        default="multilingual-e5-large",
        description="Embedding model name",
    )


class EmbedResponse(BaseModel):
    """Response with embeddings."""

    embeddings: list[list[float]]
    model: str
    dimension: int
    texts_processed: int


class QueryEmbedRequest(BaseModel):
    """Request for single query embedding."""

    text: str = Field(..., description="Query text")
    model: str = Field(
        default="multilingual-e5-large",
        description="Embedding model name",
    )


class QueryEmbedResponse(BaseModel):
    """Response with single embedding."""

    embedding: list[float]
    model: str
    dimension: int


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    models_loaded: list[str]
    version: str = "1.0.0"


# =============================================================================
# Model Manager
# =============================================================================


class EmbeddingModelManager:
    """Manages embedding models with lazy loading."""

    SUPPORTED_MODELS = {
        "multilingual-e5-large": "intfloat/multilingual-e5-large",
        "multilingual-e5-base": "intfloat/multilingual-e5-base",
        "bge-m3": "BAAI/bge-m3",
        "gabert": "DCU-NLP/bert-base-irish-cased-v1",
    }

    def __init__(self):
        self._models: dict[str, Any] = {}
        self._default_model = "multilingual-e5-large"

    def load_model(self, name: str) -> Any:
        """Load a model by name."""
        if name in self._models:
            return self._models[name]

        if name not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unknown model: {name}")

        try:
            from sentence_transformers import SentenceTransformer

            model_path = self.SUPPORTED_MODELS[name]
            model = SentenceTransformer(model_path)
            self._models[name] = model
            logger.info(f"Loaded model: {name}")
            return model

        except Exception as e:
            logger.error(f"Failed to load model {name}: {e}")
            raise

    def get_model(self, name: Optional[str] = None) -> Any:
        """Get a model, loading if necessary."""
        name = name or self._default_model
        return self.load_model(name)

    def list_loaded(self) -> list[str]:
        """List currently loaded models."""
        return list(self._models.keys())

    async def encode(
        self,
        texts: list[str],
        model_name: Optional[str] = None,
    ) -> list[list[float]]:
        """Encode texts using specified model."""
        model = self.get_model(model_name)

        # Add query prefix for e5 models
        if model_name and "e5" in model_name:
            texts = [f"query: {t}" for t in texts]

        embeddings = model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    async def encode_query(
        self,
        text: str,
        model_name: Optional[str] = None,
    ) -> list[float]:
        """Encode a single query text."""
        embeddings = await self.encode([text], model_name)
        return embeddings[0]

    def get_dimension(self, model_name: Optional[str] = None) -> int:
        """Get embedding dimension for a model."""
        model = self.get_model(model_name)
        return model.get_sentence_embedding_dimension()


# =============================================================================
# FastAPI Application
# =============================================================================


model_manager = EmbeddingModelManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Preload default model
    default_model = os.getenv("DEFAULT_EMBEDDING_MODEL", "multilingual-e5-large")
    try:
        model_manager.load_model(default_model)
        logger.info(f"Preloaded model: {default_model}")
    except Exception as e:
        logger.warning(f"Failed to preload model: {e}")

    yield

    # Cleanup
    logger.info("Shutting down embedding service")


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="Oideachais Embedding Service",
        description="Text embedding microservice for curriculum RAG",
        version="1.0.0",
        lifespan=lifespan,
    )

    @app.post("/embed", response_model=EmbedResponse)
    async def embed_texts(request: EmbedRequest) -> EmbedResponse:
        """Embed multiple texts."""
        if not request.texts:
            raise HTTPException(status_code=400, detail="No texts provided")

        if len(request.texts) > 100:
            raise HTTPException(
                status_code=400,
                detail="Maximum 100 texts per request",
            )

        try:
            embeddings = await model_manager.encode(request.texts, request.model)
            dimension = model_manager.get_dimension(request.model)

            return EmbedResponse(
                embeddings=embeddings,
                model=request.model,
                dimension=dimension,
                texts_processed=len(request.texts),
            )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise HTTPException(status_code=500, detail="Embedding failed")

    @app.post("/embed/query", response_model=QueryEmbedResponse)
    async def embed_query(request: QueryEmbedRequest) -> QueryEmbedResponse:
        """Embed a single query text with instruction prefix."""
        try:
            embedding = await model_manager.encode_query(request.text, request.model)
            dimension = model_manager.get_dimension(request.model)

            return QueryEmbedResponse(
                embedding=embedding,
                model=request.model,
                dimension=dimension,
            )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Query embedding failed: {e}")
            raise HTTPException(status_code=500, detail="Embedding failed")

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        """Health check endpoint."""
        return HealthResponse(
            status="healthy",
            models_loaded=model_manager.list_loaded(),
        )

    @app.get("/models")
    async def list_models() -> dict[str, Any]:
        """List available models."""
        return {
            "available": list(EmbeddingModelManager.SUPPORTED_MODELS.keys()),
            "loaded": model_manager.list_loaded(),
        }

    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
