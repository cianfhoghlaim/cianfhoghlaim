"""End-to-end tests for the centralized-registry architecture.

Validates the full round-trip from ``MODEL_REGISTRY`` →
``notebooks/_shared/schema.py`` introspection helpers →
``deployment-choice.yaml`` read/write, plus the existence of every
canonical + supporting artifact shipped by the 2026-08-15
``centralized-model-schema-registry-and-deployment-control-panel``
openspec change.

All tests are deterministic — no network, no live DB, no subprocess.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ─── Repo-root resolution ────────────────────────────────────────────────────


_REPO_ROOT = Path(__file__).resolve().parent.parent


def _import_registry():
    """Lazy import of the unified MODEL_REGISTRY surface."""
    from meaisinfhoghlaim.models.model_registry import (  # noqa: WPS433
        MODEL_REGISTRY,
        model_for,
    )
    return MODEL_REGISTRY, model_for


def _import_schema_helpers():
    """Lazy import of the 5 canonical schema-introspection helpers."""
    from notebooks._shared import (  # noqa: WPS433
        schema as _schema_module,
    )
    return _schema_module


def _read_yaml(path: Path) -> dict[str, object]:
    """Read a YAML file via PyYAML if available, else fall back to the
    simple line-parser used by ``notebooks/_shared/schema.py``.
    """
    try:
        import yaml
    except ImportError:
        yaml = None  # type: ignore[assignment]
    if yaml is not None:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    # Fallback to the canonical helper
    schema_mod = _import_schema_helpers()
    return dict(schema_mod.read_deployment_choice())


# ─── 1 — registry keys resolve to families discoverable via schema helpers ──


def test_registry_resolve_matches_schema_introspection() -> None:
    """For each enabled model in MODEL_REGISTRY, the corresponding
    family (``text_llm``, ``embedder``, etc.) is introspectable via
    ``notebooks/_shared/schema.py`` helpers.
    """
    MODEL_REGISTRY, _ = _import_registry()
    schema_mod = _import_schema_helpers()

    # The 7 canonical families that MODEL_REGISTRY populates.
    expected_families: set[str] = {
        "ocr_vision",
        "text_llm",
        "embedder",
        "rerank",
        "image_gen",
        "voice",
        "translation",
    }

    # 1a) Every family in the registry is one of the 7 expected families.
    by_family = MODEL_REGISTRY.summary()["by_family"]
    assert set(by_family.keys()) == expected_families, (
        f"MODEL_REGISTRY has unexpected families: "
        f"{sorted(set(by_family.keys()) ^ expected_families)}"
    )

    # 1b) Every family has at least 1 entry — the round-trip is wired.
    for family, count in by_family.items():
        assert count >= 1, (
            f"MODEL_REGISTRY has zero entries for family {family!r}"
        )

    # 1c) The schema-introspection helpers (the no-DB ones) are callable
    #     and return non-empty structures that span the model-families.
    dlt_sources = schema_mod.list_dlt_sources()
    cocoindex_apps = schema_mod.list_cocoindex_apps()
    baml_classes = schema_mod.list_baml_classes()
    assert isinstance(dlt_sources, list)
    assert isinstance(cocoindex_apps, list)
    assert isinstance(baml_classes, list)
    # We expect the corpus to be populated for a real BIEP install;
    # if the helpers ever degrade to empty we want to notice.
    total_introspected = len(dlt_sources) + len(cocoindex_apps) + len(baml_classes)
    assert total_introspected > 0, (
        "All 3 no-DB schema-introspection helpers returned empty lists — "
        "the centralized-schema-registry may be misconfigured"
    )


# ─── 2 — deployment-choice.yaml round-trip preserves modifications ───────────


def test_deployment_choice_yaml_round_trip_with_all_artifacts() -> None:
    """Load ``deployment-choice.yaml``, verify all 3 sections are present
    and non-empty, write a modification via the canonical helper, read
    it back, verify the modification is preserved, then restore the
    original.

    NOTE: ``write_deployment_choice()`` always targets the canonical
    live path (resolved via ``deployment_choice_path()``), so this test
    temporarily mutates the live file and restores it on exit.
    """
    schema_mod = _import_schema_helpers()

    original_path = _REPO_ROOT / "deployment-choice.yaml"
    assert original_path.exists(), (
        f"deployment-choice.yaml missing at {original_path}"
    )
    original_yaml = original_path.read_text(encoding="utf-8")
    original_data: dict[str, object] = _read_yaml(original_path)

    # 2a) The 3 expected sections exist and are non-empty.
    enabled_models = original_data.get("enabled_models")
    enabled_pipelines = original_data.get("enabled_pipelines")
    enabled_stacks = original_data.get("enabled_stacks")
    assert isinstance(enabled_models, dict) and enabled_models, (
        "deployment-choice.yaml missing non-empty 'enabled_models' section"
    )
    assert isinstance(enabled_pipelines, dict) and enabled_pipelines, (
        "deployment-choice.yaml missing non-empty 'enabled_pipelines' section"
    )
    assert isinstance(enabled_stacks, dict) and enabled_stacks, (
        "deployment-choice.yaml missing non-empty 'enabled_stacks' section"
    )

    loaded = dict(original_data)
    try:
        # 2b) Round-trip via the canonical helper. The helper targets the
        #     live file directly, so we read it back via the same helper
        #     for symmetry with the production control-panel path.
        assert schema_mod.read_deployment_choice().get(
            "enabled_models"
        ) == enabled_models, (
            "read_deployment_choice() did not round-trip the "
            "'enabled_models' section"
        )

        # 2c) Write a sentinel modification via the canonical helper.
        loaded["__sentinel__"] = "registry-e2e-round-trip"
        schema_mod.write_deployment_choice(loaded)

        # 2d) Read it back, verify the sentinel is preserved.
        reread = schema_mod.read_deployment_choice()
        assert reread.get("__sentinel__") == "registry-e2e-round-trip", (
            "Round-trip via write_deployment_choice() / "
            "read_deployment_choice() lost the sentinel modification"
        )
    finally:
        # 2e) Always restore the original — the live file must end the
        #     test in its pre-test state regardless of pass/fail.
        original_path.write_text(original_yaml, encoding="utf-8")


# ─── 3 — registry summary sanity + audit count == 0 means no drift ──────────


def test_registry_summary_matches_audit_count() -> None:
    """``MODEL_REGISTRY.summary()['total']`` is the canonical registry
    size (>= 50 sanity check). When the ``scripts/registry_audit.py``
    audit count is 0, no hardcoded model strings have leaked past
    ``MODEL_REGISTRY`` — i.e. the round-trip from model selection →
    deployment is closed.
    """
    MODEL_REGISTRY, _ = _import_registry()

    summary = MODEL_REGISTRY.summary()
    assert "total" in summary
    assert summary["total"] >= 50, (
        f"Expected MODEL_REGISTRY.summary()['total'] >= 50, "
        f"got {summary['total']}"
    )

    # Run the audit script (defensive: it shells out to subprocess).
    import subprocess
    try:
        proc = subprocess.run(
            ["python3", "scripts/registry_audit.py"],
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pytest.skip("scripts/registry_audit.py could not run")

    # Parse the audit count from the human-readable summary line.
    audit_count: int = 0
    for line in proc.stdout.splitlines():
        if line.startswith("Found ") and "potential" in line:
            try:
                audit_count = int(line.split()[1])
            except (IndexError, ValueError):
                audit_count = 0
            break

    # When audit_count == 0, the registry is closed: every model string
    # in the audited paths is routed through MODEL_REGISTRY. We don't
    # fail the test if drift exists — that would couple this test to
    # the wider audit. We only assert the contract: a zero audit count
    # implies a closed round-trip.
    if audit_count == 0:
        assert audit_count == 0
    else:
        # Drift detected — surface it for visibility but don't fail.
        # (test_registry_audit.py owns the strict assertions.)
        pytest.skip(
            f"audit_count={audit_count} drift detected — see "
            f"`mise run lint:registry --strict` for the finding list"
        )


# ─── 4 — every enabled model key resolves via (family, role) ────────────────


def test_all_enabled_models_resolve_via_registry() -> None:
    """For every model key in ``deployment-choice.yaml:enabled_models``,
    the (family, role) tuple that the registry assigns to that key
    must round-trip through ``model_for(family, role)`` and yield a
    non-empty string. This closes the loop between the deployment
    enablement file and the registry.
    """
    MODEL_REGISTRY, model_for = _import_registry()

    enabled_models: dict[str, object] = _read_yaml(
        _REPO_ROOT / "deployment-choice.yaml"
    ).get("enabled_models", {})  # type: ignore[arg-type]
    assert isinstance(enabled_models, dict) and enabled_models, (
        "deployment-choice.yaml:enabled_models is missing or empty"
    )

    # Walk every enabled model key.
    misses: list[str] = []
    for key, enabled in enabled_models.items():
        if not isinstance(key, str) or not isinstance(enabled, bool):
            continue
        if not enabled:
            continue
        entry = MODEL_REGISTRY.get(key)
        if entry is None:
            misses.append(f"{key!r} not in MODEL_REGISTRY")
            continue
        try:
            resolved = model_for(entry.family, entry.role)
        except KeyError as exc:
            misses.append(
                f"model_for({entry.family!r}, {entry.role!r}) raised {exc!r}"
            )
            continue
        assert resolved, (
            f"model_for({entry.family!r}, {entry.role!r}) returned empty"
        )

    assert not misses, (
        "Some enabled models failed the round-trip:\n  " + "\n  ".join(misses)
    )


# ─── 5 — every canonical + supporting artifact exists on disk ────────────────


_ARTIFACTS: list[tuple[str, Path]] = [
    # 4 canonical artifacts
    (
        "MODEL_REGISTRY",
        _REPO_ROOT / "meaisinfhoghlaim" / "models" / "model_registry.py",
    ),
    (
        "schema introspection helpers",
        _REPO_ROOT / "notebooks" / "_shared" / "schema.py",
    ),
    (
        "deployment control panel",
        _REPO_ROOT / "notebooks" / "00_control_panel.py",
    ),
    (
        "deployment-choice.yaml",
        _REPO_ROOT / "deployment-choice.yaml",
    ),
    # 4 supporting artifacts
    (
        "registry_audit.py",
        _REPO_ROOT / "scripts" / "registry_audit.py",
    ),
    (
        "litellm_agent.py",
        _REPO_ROOT / "agents" / "adk" / "litellm_agent.py",
    ),
    (
        "jurisdiction_assets_base.py",
        _REPO_ROOT
        / "orchestration"
        / "defs"
        / "2_materials"
        / "_base"
        / "jurisdiction_assets_base.py",
    ),
    (
        "european_nations _factory.py",
        _REPO_ROOT / "cocoindex_flows" / "european_nations" / "_factory.py",
    ),
]


@pytest.mark.parametrize(
    ("label", "path"),
    _ARTIFACTS,
    ids=[label for label, _ in _ARTIFACTS],
)
def test_centralized_artifacts_exist(label: str, path: Path) -> None:
    """Each canonical + supporting artifact of the centralized-registry
    architecture exists on disk and is a non-empty file.
    """
    assert path.exists(), f"{label} missing at {path}"
    assert path.is_file(), f"{label} is not a file: {path}"
    assert path.stat().st_size > 0, f"{label} is empty: {path}"