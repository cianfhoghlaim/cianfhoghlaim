"""
Modal GPU Jobs for oideachais pipeline.

This module contains Modal functions for GPU-accelerated ML tasks:

- finetune_irish: Fine-tune Llama on Irish educational data ($100/8hr)
- embed_batch: High-throughput embedding generation ($80/10M docs)

Usage:
    # Run fine-tuning
    modal run oideachais.modal.finetune_irish

    # Run batch embeddings
    modal run oideachais.modal.embed_batch

    # Deploy as persistent service
    modal deploy oideachais.modal.embed_batch

Requirements:
    - Modal account with GPU access
    - HuggingFace token (for model access)
    - LanceDB Cloud API key (for storage)

Cost estimates ($280 Modal credits):
    - Irish LLM fine-tuning: $100 (8 hours A10G)
    - Embedding batch jobs: $80 (ongoing T4)
    - Image generation: $60 (burst A10G)
    - ASR fine-tuning: $40 (Whisper-Irish)
"""

from .embed_batch import EmbeddingService, embed_query, process_curriculum_batch
from .finetune_irish import evaluate_model, finetune_irish_llm

__all__ = [
    "finetune_irish_llm",
    "evaluate_model",
    "EmbeddingService",
    "process_curriculum_batch",
    "embed_query",
]
