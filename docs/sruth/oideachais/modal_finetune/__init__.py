"""
Modal GPU Jobs for oideachais pipeline.

This module contains Modal functions for GPU-accelerated ML tasks:

- finetune_irish: Fine-tune Llama on Irish educational data ($100/8hr)
- embed_batch: High-throughput embedding generation ($80/10M docs)

Usage:
    # Run fine-tuning
    modal run sruth.oideachais.modal.finetune_irish

    # Run batch embeddings
    modal run sruth.oideachais.modal.embed_batch

    # Deploy as persistent service
    modal deploy sruth.oideachais.modal.embed_batch

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

from .finetune_irish import finetune_irish_llm, evaluate_model
from .embed_batch import EmbeddingService, process_curriculum_batch, embed_query

__all__ = [
    "finetune_irish_llm",
    "evaluate_model",
    "EmbeddingService",
    "process_curriculum_batch",
    "embed_query",
]
