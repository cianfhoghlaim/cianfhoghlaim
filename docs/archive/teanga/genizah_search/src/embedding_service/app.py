"""
FastAPI microservice for NOMIC embedding generation
"""
import os
import logging
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager
import numpy as np

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from embedding_models import NomicsEmbedding

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize embedding model
embedding_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup embedding model"""
    global embedding_model
    try:
        model_name = os.getenv("EMBEDDING_MODEL_NAME", "nomic-ai/colnomic-embed-multimodal-7b")
        text_only = os.getenv("EMBEDDING_TEXT_ONLY", "false").lower() == "true"
        image_only = os.getenv("EMBEDDING_IMAGE_ONLY", "false").lower() == "true"
        
        logger.info(f"Initializing embedding model: {model_name}")
        embedding_model = NomicsEmbedding(
            model_name=model_name,
            text_only=text_only,
            image_only=image_only
        )
        logger.info("Embedding model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize embedding model: {e}")
        raise
    
    yield
    
    # Cleanup (if needed)
    logger.info("Shutting down embedding service")


app = FastAPI(
    title="Embedding Service",
    version="1.0.0",
    lifespan=lifespan
)


class EmbeddingRequest(BaseModel):
    """Request model for embedding generation"""
    text: str = Field(..., min_length=1, description="Text to embed")
    image: Optional[str] = Field(default=None, description="Base64 encoded image or image URL (optional)")
    use_cache: bool = Field(default=True, description="Whether to use cached embeddings")


class EmbeddingResponse(BaseModel):
    """Response model for embedding generation"""
    embedding: List[float] = Field(..., description="Embedding vector")
    dimension: int = Field(..., description="Dimension of the embedding vector")
    cached: bool = Field(default=False, description="Whether the embedding was retrieved from cache")


class BatchEmbeddingRequest(BaseModel):
    """Request model for batch embedding generation"""
    texts: List[str] = Field(..., min_items=1, description="List of texts to embed")
    images: Optional[List[Optional[str]]] = Field(default=None, description="List of images (optional, must match texts length)")
    use_cache: bool = Field(default=True, description="Whether to use cached embeddings")


class BatchEmbeddingResponse(BaseModel):
    """Response model for batch embedding generation"""
    embeddings: List[List[float]] = Field(..., description="List of embedding vectors")
    dimension: int = Field(..., description="Dimension of the embedding vectors")
    cached_count: int = Field(default=0, description="Number of embeddings retrieved from cache")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": embedding_model is not None
    }


@app.post("/embed", response_model=EmbeddingResponse)
async def get_embedding(request: EmbeddingRequest):
    """
    Generate embedding for a single text (and optionally an image)
    """
    if embedding_model is None:
        raise HTTPException(status_code=503, detail="Embedding model not initialized")
    
    try:
        # Check cache first
        cached = False
        if request.use_cache:
            import hashlib
            doc_identifier = hashlib.md5(request.text.encode()).hexdigest()[:10]
            cache_path = embedding_model.get_cache_path(
                embedding_model.model_name,
                f"doc_{doc_identifier}"
            )
            if embedding_model.check_cache(cache_path):
                embedding = embedding_model.load_from_cache(cache_path)
                cached = True
            else:
                embedding = embedding_model.get_embeddings(
                    request.image,
                    request.text,
                    use_cache=request.use_cache
                )
        else:
            embedding = embedding_model.get_embeddings(
                request.image,
                request.text,
                use_cache=request.use_cache
            )
        
        # Convert numpy array to list
        if isinstance(embedding, np.ndarray):
            embedding_list = embedding.flatten().tolist()
        else:
            embedding_list = embedding
        
        return EmbeddingResponse(
            embedding=embedding_list,
            dimension=len(embedding_list),
            cached=cached
        )
    
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {str(e)}")


@app.post("/embed/batch", response_model=BatchEmbeddingResponse)
async def get_batch_embeddings(request: BatchEmbeddingRequest):
    """
    Generate embeddings for multiple texts (and optionally images)
    """
    if embedding_model is None:
        raise HTTPException(status_code=503, detail="Embedding model not initialized")
    
    if request.images is not None and len(request.images) != len(request.texts):
        raise HTTPException(
            status_code=400,
            detail="Number of images must match number of texts"
        )
    
    try:
        embeddings = []
        cached_count = 0
        
        for i, text in enumerate(request.texts):
            image = request.images[i] if request.images else None
            
            # Check cache
            cached = False
            if request.use_cache:
                import hashlib
                doc_identifier = hashlib.md5(text.encode()).hexdigest()[:10]
                cache_path = embedding_model.get_cache_path(
                    embedding_model.model_name,
                    f"doc_{doc_identifier}"
                )
                if embedding_model.check_cache(cache_path):
                    embedding = embedding_model.load_from_cache(cache_path)
                    cached = True
                    cached_count += 1
                else:
                    embedding = embedding_model.get_embeddings(
                        image,
                        text,
                        use_cache=request.use_cache
                    )
            else:
                embedding = embedding_model.get_embeddings(
                    image,
                    text,
                    use_cache=request.use_cache
                )
            
            # Convert numpy array to list
            if isinstance(embedding, np.ndarray):
                embedding_list = embedding.flatten().tolist()
            else:
                embedding_list = embedding
            
            embeddings.append(embedding_list)
        
        dimension = len(embeddings[0]) if embeddings else 0
        
        return BatchEmbeddingResponse(
            embeddings=embeddings,
            dimension=dimension,
            cached_count=cached_count
        )
    
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate batch embeddings: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)

