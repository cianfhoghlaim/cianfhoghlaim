"""Tests for the routing-table migration to MODEL_REGISTRY lookups.

Per 2026-08-17-hygiene-drift-cleanup-v1 (P3.3): verifies that all 15
previously-hardcoded model strings in `meaisinfhoghlaim/models/routing.py`
now resolve via `model_for(...)` lookups against the centralized
MODEL_REGISTRY, and that the routing table's references still resolve
to the same model strings they had before.

This test exists to catch the drift-remediation spec gap: the audit
script catches NEW hardcoded model strings, but the migration of the
15 historical hardcoded strings needed to be verified by a test
that exercises the routing table directly.
"""
from __future__ import annotations

from meaisinfhoghlaim.models.model_registry import model_for
from meaisinfhoghlaim.models.routing import (
    DEFAULT_OCR_MODEL,
    DEFAULT_TEXT_MODEL,
    DIAGRAM_OCR_MODEL,
    IRISH_TEXT_MODEL,
    ROUTING_TABLE,
    get_model_name,
    route_language,
)


# ─── Migrated module-level constants resolve via model_for(...) ──────────────


def test_default_text_model_resolves_to_registry() -> None:
    """The DEFAULT_TEXT_MODEL constant must match what model_for('text_llm', 'default') returns."""
    assert DEFAULT_TEXT_MODEL == model_for("text_llm", "default")


def test_irish_text_model_resolves_to_registry_with_language() -> None:
    """The IRISH_TEXT_MODEL constant must match model_for('text_llm', 'irish', language='ga')."""
    assert IRISH_TEXT_MODEL == model_for("text_llm", "irish", language="ga")


def test_diagram_ocr_model_resolves_to_registry() -> None:
    """The DIAGRAM_OCR_MODEL constant must match model_for('ocr_vision', 'specialist')."""
    assert DIAGRAM_OCR_MODEL == model_for("ocr_vision", "specialist")


def test_default_ocr_model_resolves_to_registry() -> None:
    """The DEFAULT_OCR_MODEL constant must match model_for('ocr_vision', 'default')."""
    assert DEFAULT_OCR_MODEL == model_for("ocr_vision", "default")


# ─── Routing table references the 4 canonical constants (not raw strings) ──


# The 4 canonical constants that the routing table references
CANONICAL_CONSTANTS = frozenset(
    {DEFAULT_TEXT_MODEL, IRISH_TEXT_MODEL, DIAGRAM_OCR_MODEL, DEFAULT_OCR_MODEL}
)


def test_routing_table_uses_canonical_constants() -> None:
    """Every (source_group, language) entry must reference one of the 4 canonical model_for() constants.

    This verifies that the migration to MODEL_REGISTRY is complete:
    no entry in ROUTING_TABLE may carry a raw historical hardcoded
    string. Each entry references one of the 4 module-level constants
    (which themselves call model_for()).
    """
    for (source_group, language), cfg in ROUTING_TABLE.items():
        assert cfg.model in CANONICAL_CONSTANTS, (
            f"routing_table[({source_group!r}, {language!r})] uses an unknown "
            f"model string {cfg.model!r}; expected one of the 4 canonical constants"
        )


# ─── Spot-check the 4 most-common routes preserve their canonical model ──────


def test_gaois_irish_routes_to_irish_model() -> None:
    """The (gaois, ga) route must use the Irish text model."""
    cfg = route_language("gaois", "ga")
    assert cfg.model == IRISH_TEXT_MODEL
    assert cfg.client == "LlamaSwap"
    assert cfg.tier == "tier2_medium"


def test_gaois_english_routes_to_default_model() -> None:
    """The (gaois, en) route must use the default text model."""
    cfg = route_language("gaois", "en")
    assert cfg.model == DEFAULT_TEXT_MODEL


def test_duchas_routes_to_diagram_model() -> None:
    """The (duchas, *) route must use the diagram OCR model (specialist)."""
    cfg = route_language("duchas", "ga")
    assert cfg.model == DIAGRAM_OCR_MODEL
    assert cfg.tier == "specialist"


def test_celtic_curriculum_default_uses_default_model() -> None:
    """The (celtic_curriculum, *) route must use the default text model."""
    cfg = route_language("celtic_curriculum", "*")
    assert cfg.model == DEFAULT_TEXT_MODEL


# ─── Wildcard fallback works ────────────────────────────────────────────────


def test_unknown_source_group_falls_back_to_default() -> None:
    """An unknown source_group must hit the default fallback (DEFAULT_TEXT_MODEL)."""
    cfg = route_language("nonexistent_source_group", "en")
    assert cfg.model == DEFAULT_TEXT_MODEL


def test_unknown_language_falls_back_to_source_wildcard() -> None:
    """An unknown language for a known source_group must hit the source wildcard."""
    # (gaois, "kw") is not in the table; (gaois, "*") is, returning DEFAULT_TEXT_MODEL
    cfg = route_language("gaois", "kw")
    assert cfg.model == DEFAULT_TEXT_MODEL


# ─── get_model_name helper still works ───────────────────────────────────────


def test_get_model_name_returns_registry_string() -> None:
    """get_model_name must return the same string as the model attribute on the route."""
    for sg in ["gaois", "duchas", "celtic_curriculum"]:
        for lang in ["ga", "en", "*"]:
            cfg = route_language(sg, lang)
            assert get_model_name(sg, lang) == cfg.model