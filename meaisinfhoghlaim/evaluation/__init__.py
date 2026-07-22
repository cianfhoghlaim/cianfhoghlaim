"""Meaisínfhoghlaim evaluation package (BIEP v2).

Per the 2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1 change.

Provides:
  - RAGAS evaluation harnesses for the BIEP v2 4-path ensemble
    (`ragas_biiep_ensemble.py`)
  - One-time MLflow setup helper (`register_biiep_v2_metrics`)

All harnesses log to the canonical MLflow experiment `biiep_v2`.
"""
