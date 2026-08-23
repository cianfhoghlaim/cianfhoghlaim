# `dlt_sources/apple_photos/`

> `apple_photos/`: the 5th leabharlann corpus (macOS Photos library) — 1 .py file (the DLT source is in flight per Phase D).

## Quick start

- `__init__.py` — the only file (the osxphotos-based DLT source for the Photos library export)

## Status

This subtree is mostly empty — the 3 CocoIndex v1 Apps + 3 Dagster `defs.yaml` exist in `cocoindex_flows/media/` and `orchestration/defs/3_model_lifecycle/cocoindex_v1/`, but the DLT source is in flight (per `apple-photos-ingestion` spec). Phase D will add the missing DLT sources (`library_export.py`, `document_scans.py`, `vehicles.py`).
