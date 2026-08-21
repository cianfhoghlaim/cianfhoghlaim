"""
Embedding Microservice.

Decoupled embedding service for scalable text embedding generation.
"""

from .main import create_app

__all__ = ["create_app"]
