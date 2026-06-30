"""meaisínfhoghlaim.marimo — Statistical analysis notebooks for the meaisínfhoghlaim quadrant.

This sub-package provides marimo notebooks that read from the
`md:oideachais` MotherDuck database (the lakehouse) and expose
reactive descriptive + time-series analysis. It is the AI/ML-quadrant
counterpart to the existing `oideachais-marimo-dashboards` capability
(11 marimo notebooks under `oideachais/marimo/`).

Two reference notebooks are shipped:

- `01_leabharlann_descriptive.py` — descriptive statistics on the
  leabharlann/ corpus (token length, fada-preservation rate, lexical
  diversity, per-language counts).
- `02_dpre_lag_analysis.py` — time-series of `DynamicPartitionsDefinition`
  materialization lags across the 10 OCR models; correlation heatmap
  of BAML extraction confidence vs OCR WER.

Run locally:

    uv pip install -e "meaisinfhoghlaim[marimo]"
    marimo edit meaisinfhoghlaim/marimo/01_leabharlann_descriptive.py

See also:
- `openspec/changes/celtic-data-engineering-patterns/specs/celtic-data-engineering-pipeline/spec.md`
  (the canonical capability spec for this sub-package)
- `meaisinfhoghlaim/AGENTS.md` "Quick routing" table (the marimo row)
"""

from __future__ import annotations

__all__ = [
    "NOTEBOOKS",
]

NOTEBOOKS: list[str] = [
    "01_leabharlann_descriptive",
    "02_dpre_lag_analysis",
]
