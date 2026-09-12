"""tests.biep_parity_lc — the BIEP v3 per-subject pytest suite.

Exercises the 6 per-subject CocoIndex v1 Apps in
`cocoindex_flows/british_isles/ireland/education/lc/` end-to-end:
load → embed → store → query against a 3-row per-subject fixture.

The pytests do NOT require a live LanceDB / Dagster / BAML
runtime. They use:
- `pure_python_embed` (deterministic numpy substitute for BGE-M3)
- `python_baml_fallback_extract` (regex-based fallback for BAML)
- An in-memory list as the "LanceDB table"

If/when defects #2, #3 are remediated (baml_client regenerated,
defs/__init__.py wired), the same test surface continues to work —
the real BAML function and real LanceDB target become drop-in
substitutes for the stand-ins.

Run:
    uv run pytest tests/biep_parity_lc/ -v
"""
