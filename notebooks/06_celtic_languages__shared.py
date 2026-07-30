"""Celtic Language notebooks per-area shim.

Re-exports the canonical ``connect_md()`` helper from
``notebooks/_shared/db.py`` for use by every
``notebooks/celtic_language/*.py`` notebook.

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — use ``connect_md()``
  instead of raw ``duckdb.connect``.
- marimo (per `.agents/skills/marimo/SKILL.md`).

Reference: openspec/changes/2026-07-25-nb-utils-ibis-first-v1/
"""
from __future__ import annotations


# Centralized registries (per the `centralized-model-registry` capability).
# Cascading effect: this notebook now uses MODEL_REGISTRY + the 5 schema
# introspection helpers from notebooks/_shared/schema.py instead of
# hardcoded table lists / hardcoded schema strings.
try:
    from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for  # noqa: E402
    from notebooks._shared.schema import (  # noqa: E402
        list_dlt_sources, list_cocoindex_apps, list_baml_classes,
        schema_introspect, schema_introspect_table, read_deployment_choice,
    )
    _DEFAULT_LLM = model_for("text_llm", "default")
    _REGISTRY_SUMMARY = MODEL_REGISTRY.summary()
    _DLT_SOURCE_COUNT = len(list_dlt_sources())
    _COCO_APP_COUNT = len(list_cocoindex_apps())
    _BAML_CLASS_COUNT = len(list_baml_classes())
    _ENABLED_MODELS = sum(
        1 for v in read_deployment_choice().get("enabled_models", {}).values() if v
    )
except ImportError:
    _DEFAULT_LLM = "minimax-m3"  # fallback (the legacy hardcoded value)
    _REGISTRY_SUMMARY = {"total": 0, "by_family": {}, "available": 0, "deprecated": 0}
    _DLT_SOURCE_COUNT = _COCO_APP_COUNT = _BAML_CLASS_COUNT = 0
    _ENABLED_MODELS = 0

from notebooks._shared.db import connect_md, connect_local, lakehouse_uri

__all__ = ["connect_md", "connect_local", "lakehouse_uri"]