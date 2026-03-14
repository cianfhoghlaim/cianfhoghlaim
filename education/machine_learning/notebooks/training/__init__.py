"""
Meaisínfhoghlaim Training Modules.

Cloud-based ML training pipelines for Celtic language education:

- PyLaia HTR (Modal): Irish historical handwriting recognition
- Chatterbox TTS (Modal): Irish dialect speech synthesis
- Curriculum LLM (Anyscale): Bilingual education model

Cloud Credits Allocation:
    - Modal: $280 (HTR + TTS training)
    - Anyscale: $100 (Distributed LLM training)

Usage:
    # HTR Training (Modal)
    modal run pylaia_modal.py

    # TTS Training (Modal)
    modal run chatterbox_modal.py --dialect connacht

    # LLM Training (Anyscale)
    anyscale job submit -f curriculum_config.yaml
"""

from .train_distributed import train_func as distributed_train_func

__all__ = [
    "distributed_train_func",
]

# Module metadata
__version__ = "0.1.0"
__credits_budget__ = {
    "modal": 280,  # PyLaia HTR + Chatterbox TTS
    "anyscale": 100,  # Curriculum LLM distributed training
    "total": 380,
}
