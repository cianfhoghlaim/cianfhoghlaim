"""
BIEP v2 cross-jurisdiction marimo notebooks (Change 4).

Per the 2026-07-23-biep-v2-marimo-portal-v1 change.

The 4 marimo notebooks at ``notebooks/04_biep_v2/``:

- ``00_biep_v2_overview.py`` — single-pane view across LC + JC + A-Level + GCSE
- ``01_junior_cycle_explorer.py`` — JC drill-down (18 subjects + 36 CBAs)
- ``02_england_explorer.py`` — AQA / OCR / Edexcel side-by-side
- ``03_ocr_ensemble_audit.py`` — full audit trail (PDF + Docling + Unstract +
  qwen3-vl-8b + gemma-4-26B-A4B + RAGAS score + BAML Pydantic + Langfuse)

All 4 notebooks use the **ibis-first contract** (no raw ``duckdb.connect()``).
"""
