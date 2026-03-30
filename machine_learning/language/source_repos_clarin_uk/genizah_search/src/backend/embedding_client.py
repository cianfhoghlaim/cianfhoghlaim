"""
Client for the embedding service microservice
"""
import os
import logging
from typing import Optional, List
import httpx
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """Client for interacting with the embedding service"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("EMBEDDING_SERVICE_URL", "http://embedding:8001")
        self.timeout = 60.0  # Longer timeout for model inference
        
    async def get_embedding(self, text: str, image: Optional[str] = None, use_cache: bool = True) -> np.ndarray:
        """
        Get embedding for a single text (and optionally an image)
        
        Args:
            text: Text to embed
            image: Optional image (base64 or URL)
            use_cache: Whether to use cached embeddings
            
        Returns:
            numpy array of the embedding vector
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/embed",
                    json={
                        "text": text,
                        "image": image,
                        "use_cache": use_cache
                    }
                )
                response.raise_for_status()
                data = response.json()
                return np.array(data["embedding"])
        except httpx.HTTPError as e:
            logger.error(f"Failed to get embedding from service: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting embedding: {e}")
            raise
    
    async def get_batch_embeddings(
        self,
        texts: List[str],
        images: Optional[List[Optional[str]]] = None,
        use_cache: bool = True
    ) -> np.ndarray:
        """
        Get embeddings for multiple texts (and optionally images)
        
        Args:
            texts: List of texts to embed
            images: Optional list of images (must match texts length)
            use_cache: Whether to use cached embeddings
            
        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "texts": texts,
                    "use_cache": use_cache
                }
                if images is not None:
                    payload["images"] = images
                
                response = await client.post(
                    f"{self.base_url}/embed/batch",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return np.array(data["embeddings"])
        except httpx.HTTPError as e:
            logger.error(f"Failed to get batch embeddings from service: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting batch embeddings: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if the embedding service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json().get("status") == "healthy"
        except Exception as e:
            logger.warning(f"Embedding service health check failed: {e}")
            return False


# Global client instance
embedding_client = EmbeddingClient()

