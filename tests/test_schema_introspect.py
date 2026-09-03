"""Tests for ``notebooks/_shared/schema.py`` introspection helpers.

Verifies the 5 canonical scenarios for the
``centralized-schema-registry`` capability's lakehouse introspectors:

1. ``list_dlt_sources()`` returns >= 1000 entries (actual: 1963).
2. ``list_cocoindex_apps()`` returns >= 30 entries (actual: ~41).
3. ``list_baml_classes()`` returns >= 800 entries (actual: ~844).
4. ``read_deployment_choice()`` returns a dict with the 3
   canonical sections (``enabled_models``, ``enabled_pipelines``,
   ``enabled_stacks``).
5. ``write_deployment_choice()`` + ``read_deployment_choice()``
   round-trip: writing a small choice and reading it back yields
   an equal dict.

All tests are deterministic — no network, no live DuckDB. The
helpers themselves do read the filesystem (DLT sources, CocoIndex
apps, BAML files, ``deployment-choice.yaml``), but those are local
files under the repo root.
"""

from __future__ import annotations

from pathlib import Path


def _import_schema():
    """Lazy import so a missing module surfaces per-test."""
    from notebooks._shared import schema as schema_mod

    return schema_mod


# ─── 1 — list_dlt_sources() returns >= 1000 entries ────────────


def test_list_dlt_sources_returns_count() -> None:
    """``list_dlt_sources()`` returns >= 1000 entries.

    The actual count is 1963 (per the audit). The sanity check is
    1000 to allow for growth / shrinkage as DLT sources are added
    or removed.
    """
    schema_mod = _import_schema()
    sources = schema_mod.list_dlt_sources()
    assert isinstance(sources, list)
    assert len(sources) >= 1000, (
        f"Expected >= 1000 DLT sources, got {len(sources)}"
    )


# ─── 2 — list_cocoindex_apps() returns >= 30 entries ───────────


def test_list_cocoindex_apps_returns_count() -> None:
    """``list_cocoindex_apps()`` returns >= 30 entries.

    The actual count is ~41 (per the audit). The sanity check is
    30 to allow for growth / shrinkage.
    """
    schema_mod = _import_schema()
    apps = schema_mod.list_cocoindex_apps()
    assert isinstance(apps, list)
    assert len(apps) >= 30, (
        f"Expected >= 30 CocoIndex Apps, got {len(apps)}"
    )


# ─── 3 — list_baml_classes() returns >= 800 entries ────────────


def test_list_baml_classes_returns_count() -> None:
    """``list_baml_classes()`` returns >= 800 entries.

    The actual count is ~844 (per the audit). The sanity check is
    800 to allow for growth / shrinkage.
    """
    schema_mod = _import_schema()
    classes = schema_mod.list_baml_classes()
    assert isinstance(classes, list)
    assert len(classes) >= 800, (
        f"Expected >= 800 BAML classes, got {len(classes)}"
    )


# ─── 4 — read_deployment_choice() returns a dict with 3 keys ───


def test_read_deployment_choice_returns_dict() -> None:
    """``read_deployment_choice()`` returns a dict containing the
    3 canonical sections: ``enabled_models``, ``enabled_pipelines``,
    ``enabled_stacks``.
    """
    schema_mod = _import_schema()
    choice = schema_mod.read_deployment_choice()
    assert isinstance(choice, dict), (
        f"Expected dict, got {type(choice)}"
    )
    # The canonical 3 sections. Some deployments also carry
    # ``version`` + ``enabled_datasets`` + ``monitoring``, but the
    # 3 core sections MUST be present.
    for required_key in ("enabled_models", "enabled_pipelines", "enabled_stacks"):
        assert required_key in choice, (
            f"Expected {required_key!r} in deployment-choice.yaml, "
            f"got keys: {list(choice.keys())}"
        )


# ─── 5 — write_deployment_choice() round-trip ──────────────────


def test_write_deployment_choice_round_trip(tmp_path: Path, monkeypatch) -> None:
    """``write_deployment_choice(data)`` followed by
    ``read_deployment_choice()`` returns an equal dict.

    We use ``monkeypatch`` to redirect ``deployment_choice_path()``
    to a temp file so we don't mutate the real
    ``deployment-choice.yaml`` in the repo.
    """
    schema_mod = _import_schema()

    # Point the deployment-choice path at a temp file for this test.
    tmp_choice = tmp_path / "deployment-choice.yaml"
    monkeypatch.setattr(schema_mod, "_DEPLOYMENT_CHOICE_PATH", tmp_choice)
    monkeypatch.setattr(
        schema_mod,
        "deployment_choice_path",
        lambda: tmp_choice,
    )

    payload = {
        "version": 1,
        "enabled_models": {
            "minimax-m3": True,
            "uccix-mistral-24b": True,
        },
        "enabled_pipelines": {
            "biemath_v1": True,
        },
        "enabled_stacks": {
            "lakehouse": True,
        },
    }

    schema_mod.write_deployment_choice(payload)
    assert tmp_choice.exists(), "write_deployment_choice did not create the file"

    # Read it back (the module reads the path we monkeypatched).
    read_back = schema_mod.read_deployment_choice()
    assert read_back == payload, (
        f"Round-trip mismatch.\n"
        f"wrote: {payload}\n"
        f"read:  {read_back}"
    )
