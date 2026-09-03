"""Tests for the unified `MODEL_REGISTRY` API.

Verifies the 8 canonical scenarios for
``meaisinfhoghlaim/models/model_registry.py`` (introduced by the
2026-08-15 ``centralized-model-registry`` openspec change):

1. ``model_for("text_llm", "default")`` returns ``"minimax-m3"`` —
   the canonical plan alias for the 12-agent fleet.
2. ``model_for("text_llm", "irish", language="ga")`` returns
   ``"uccix-mistral-24b"`` — the Modern Irish path (replaces the
   deprecated ``uccix-llama2-13b``).
3. ``model_for("embedder", "default")`` returns ``"BAAI/bge-m3"`` —
   the canonical 1024-d embedder used by CocoIndex v1 Apps.
4. ``MODEL_REGISTRY.summary()`` returns a dict with ``total >= 50``.
5. ``MODEL_REGISTRY.filter(family="text_llm")`` returns >= 5
   entries.
6. No two entries share the same ``key``.
7. No two entries share the same ``display_name``.
8. Every entry has ``key``, ``family``, ``role``, ``display_name``,
   ``available``.

All tests are deterministic — no network, no live DB.
"""

from __future__ import annotations

from dataclasses import fields

# ─── Module-level imports (kept inside fixtures to allow pytest
#     collection even if the package isn't on sys.path yet). ───


def _import_registry():
    """Lazy import so a missing module surfaces per-test, not at
    collection time."""
    from meaisinfhoghlaim.models.model_registry import (
        MODEL_REGISTRY,
        ModelRegistryEntry,
        filter_models,
        model_for,
    )
    return MODEL_REGISTRY, ModelRegistryEntry, filter_models, model_for


# ─── 1+2+3 — model_for() returns the canonical model keys ────────


def test_model_for_default_text_llm() -> None:
    """``model_for("text_llm", "default")`` returns ``"minimax-m3"``."""
    _, _, _, model_for = _import_registry()
    assert model_for("text_llm", "default") == "minimax-m3"


def test_model_for_irish_text_llm() -> None:
    """``model_for("text_llm", "irish", language="ga")`` returns
    ``"uccix-mistral-24b"`` — the Modern Irish path.
    """
    _, _, _, model_for = _import_registry()
    assert model_for("text_llm", "irish", language="ga") == "uccix-mistral-24b"


def test_model_for_default_embedder() -> None:
    """``model_for("embedder", "default")`` returns
    ``"BAAI/bge-m3"`` — the canonical 1024-d embedder.
    """
    _, _, _, model_for = _import_registry()
    assert model_for("embedder", "default") == "BAAI/bge-m3"


# ─── 4 — summary() returns a dict with total >= 50 ──────────────


def test_summary_total() -> None:
    """``MODEL_REGISTRY.summary()`` returns ``{"total": int, ...}``
    with ``total >= 50``.
    """
    MODEL_REGISTRY, _, _, _ = _import_registry()
    summary = MODEL_REGISTRY.summary()
    assert isinstance(summary, dict)
    assert "total" in summary
    assert summary["total"] >= 50, (
        f"Expected MODEL_REGISTRY.summary()['total'] >= 50, "
        f"got {summary['total']}"
    )


# ─── 5 — filter(family=...) returns >= 5 entries ────────────────


def test_filter_models_by_family() -> None:
    """``MODEL_REGISTRY.filter(family="text_llm")`` returns a list
    with >= 5 entries (the M3 chokepoint + agent defaults + UCCIX
    paths + hackathon fallbacks).
    """
    MODEL_REGISTRY, _, _, _ = _import_registry()
    entries = MODEL_REGISTRY.filter(family="text_llm")
    assert isinstance(entries, list)
    assert len(entries) >= 5, (
        f"Expected >= 5 text_llm entries, got {len(entries)}"
    )
    for entry in entries:
        assert entry.family == "text_llm"


# ─── 6 — no duplicate keys ──────────────────────────────────────


def test_no_duplicate_keys() -> None:
    """No two ``ModelRegistryEntry`` share the same ``key``."""
    MODEL_REGISTRY, _, _, _ = _import_registry()
    keys: list[str] = [e.key for e in MODEL_REGISTRY.entries()]
    duplicates = {k for k in keys if keys.count(k) > 1}
    assert not duplicates, (
        f"Found duplicate keys in MODEL_REGISTRY: {sorted(duplicates)}"
    )


# ─── 7 — no duplicate display_names ─────────────────────────────


def test_no_duplicate_display_names() -> None:
    """No two ``ModelRegistryEntry`` share the same ``display_name``."""
    MODEL_REGISTRY, _, _, _ = _import_registry()
    names: list[str] = [e.display_name for e in MODEL_REGISTRY.entries()]
    duplicates = {n for n in names if names.count(n) > 1}
    assert not duplicates, (
        f"Found duplicate display_names in MODEL_REGISTRY: "
        f"{sorted(duplicates)}"
    )


# ─── 8 — every entry has the required fields populated ─────────


_REQUIRED_FIELDS = ("key", "family", "role", "display_name", "available")


def test_all_models_have_required_fields() -> None:
    """Every entry has ``key``, ``family``, ``role``,
    ``display_name``, ``available`` populated.
    """
    MODEL_REGISTRY, ModelRegistryEntry, _, _ = _import_registry()
    # First, sanity check: every actual field on the dataclass is
    # part of the required set, or the test below is meaningless.
    actual_fields = {f.name for f in fields(ModelRegistryEntry)}
    missing_required = set(_REQUIRED_FIELDS) - actual_fields
    assert not missing_required, (
        f"ModelRegistryEntry is missing required fields: "
        f"{sorted(missing_required)}"
    )

    entries = MODEL_REGISTRY.entries()
    assert entries, "MODEL_REGISTRY is empty — no entries to validate"

    for entry in entries:
        for field_name in _REQUIRED_FIELDS:
            value = getattr(entry, field_name)
            assert value is not None, (
                f"{entry!r}: field {field_name!r} is None"
            )
            if isinstance(value, str):
                assert value, (
                    f"{entry!r}: field {field_name!r} is an empty string"
                )
