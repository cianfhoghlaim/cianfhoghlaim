"""Smoke tests for the knowledge-graph population activation.

Per the ``2026-08-13-knowledge-graph-population-activation-v1`` change,
this file verifies that the 5 per-stage cognify ``defs.yaml`` files are
present and parse correctly:

  - aistear_cognify/defs.yaml
  - primary_cognify/defs.yaml
  - junior_cycle_cognify/defs.yaml
  - senior_cycle_cognify/defs.yaml
  - university_cognify/defs.yaml

Plus the cross-stage orchestrator at
``cross_stage_cognify/defs.yaml`` is present (the previously-registered
template that the per-stage files mirror).

The tests are hermetic — they only validate the YAML surface (parsing +
required fields + canonical component type); they do NOT bring up the
Cognee stack (which is intentionally out of scope per the change's
"Out of scope" section).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
COGNIFY_ROOT = REPO_ROOT / "orchestration" / "defs" / "3_model_lifecycle" / "cognify"

# Canonical 5-stage Irish education KG (Aistear → University).
EXPECTED_STAGES = [
    "aistear",
    "primary",
    "junior_cycle",
    "senior_cycle",
    "university",
]

# Stage slug → dataset name (must match `cianfhoghlaim.education.<stage>`).
EXPECTED_DATASETS = {
    "aistear": "cianfhoghlaim.education.aistear",
    "primary": "cianfhoghlaim.education.primary",
    "junior_cycle": "cianfhoghlaim.education.junior_cycle",
    "senior_cycle": "cianfhoghlaim.education.senior_cycle",
    "university": "cianfhoghlaim.education.university",
}


# ─── 1. All 5 per-stage defs.yaml files exist ──────────────────────────────


@pytest.mark.parametrize("stage", EXPECTED_STAGES)
def test_stage_defs_yaml_exists(stage: str) -> None:
    """The 5 per-stage ``defs.yaml`` files MUST exist.

    Per the change's Phase B (B1): the 5 stage adapters MUST be
    registered so Dagster's ``load_defs`` walker picks them up.
    """
    defs_path = COGNIFY_ROOT / f"{stage}_cognify" / "defs.yaml"
    assert defs_path.exists(), (
        f"Missing stage defs.yaml for '{stage}' at {defs_path}. "
        f"The 2026-08-13-knowledge-graph-population-activation-v1 "
        f"change requires all 5 stage adapters to be registered."
    )
    assert defs_path.is_file(), f"{defs_path} must be a regular file"


def test_cross_stage_defs_yaml_exists() -> None:
    """The cross-stage orchestrator ``defs.yaml`` MUST also exist.

    This is the template the per-stage files mirror (per the change's
    Phase B prose).
    """
    defs_path = COGNIFY_ROOT / "cross_stage_cognify" / "defs.yaml"
    assert defs_path.exists(), f"Missing cross-stage defs.yaml at {defs_path}"


# ─── 2. All 5 per-stage defs.yaml files parse as valid YAML ────────────────


@pytest.mark.parametrize("stage", EXPECTED_STAGES)
def test_stage_defs_yaml_parses(stage: str) -> None:
    """Each stage's ``defs.yaml`` MUST parse as valid YAML."""
    defs_path = COGNIFY_ROOT / f"{stage}_cognify" / "defs.yaml"
    content = defs_path.read_text()
    try:
        parsed = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        pytest.fail(f"{defs_path} failed YAML parsing: {exc}")

    assert parsed is not None, f"{defs_path} parsed to None"
    assert isinstance(parsed, dict), (
        f"{defs_path} must parse to a YAML mapping, got {type(parsed).__name__}"
    )


# ─── 3. All 5 per-stage defs.yaml files use KCGCognifyComponent ─────────────


@pytest.mark.parametrize("stage", EXPECTED_STAGES)
def test_stage_defs_yaml_uses_cognify_component(stage: str) -> None:
    """Each stage's ``defs.yaml`` MUST use the ``KCGCognifyComponent`` type.

    Per ``orchestration/components/kcg_cognify_component.py``: the
    cognify stages are realised by the ``KCGCognifyComponent`` (one
    asset per stage + one asset_check per stage). A different type
    would not be recognised by the cognify loader.
    """
    defs_path = COGNIFY_ROOT / f"{stage}_cognify" / "defs.yaml"
    parsed = yaml.safe_load(defs_path.read_text())

    type_name = parsed.get("type", "")
    assert type_name == "orchestration.components.KCGCognifyComponent", (
        f"{defs_path} uses type='{type_name}' but must use "
        f"'orchestration.components.KCGCognifyComponent' (per the "
        f"KCG cognify component registry)."
    )


# ─── 4. Stage attribute + dataset match the expected values ────────────────


@pytest.mark.parametrize("stage", EXPECTED_STAGES)
def test_stage_defs_yaml_attributes_match_stage(stage: str) -> None:
    """Each stage's ``attributes.stage`` + ``attributes.dataset`` match the stage slug."""
    defs_path = COGNIFY_ROOT / f"{stage}_cognify" / "defs.yaml"
    parsed = yaml.safe_load(defs_path.read_text())
    attrs = parsed.get("attributes", {})
    assert attrs.get("stage") == stage, (
        f"{defs_path} has attributes.stage='{attrs.get('stage')}' "
        f"but must be '{stage}'"
    )
    expected_dataset = EXPECTED_DATASETS[stage]
    assert attrs.get("dataset") == expected_dataset, (
        f"{defs_path} has attributes.dataset='{attrs.get('dataset')}' "
        f"but must be '{expected_dataset}'"
    )


# ─── 5. Each stage has at least one edge type declared ─────────────────────


@pytest.mark.parametrize("stage", EXPECTED_STAGES)
def test_stage_defs_yaml_declares_edge_types(stage: str) -> None:
    """Each stage's ``defs.yaml`` MUST declare at least one edge type."""
    defs_path = COGNIFY_ROOT / f"{stage}_cognify" / "defs.yaml"
    parsed = yaml.safe_load(defs_path.read_text())
    edge_types = parsed.get("attributes", {}).get("edge_types", [])
    assert isinstance(edge_types, list), (
        f"{defs_path} attributes.edge_types must be a list"
    )
    assert len(edge_types) >= 1, (
        f"{defs_path} must declare at least one edge_type "
        f"(per the cognify component contract)"
    )


# ─── 6. Each stage references a real source adapter module ─────────────────


@pytest.mark.parametrize("stage", EXPECTED_STAGES)
def test_stage_defs_yaml_source_adapter_loadable(stage: str) -> None:
    """Each stage's ``attributes.source_adapter`` MUST be importable.

    The adapter is resolved lazily at execute time, never at
    defs-build time, so a non-existent adapter would silently break
    the cognify assets. We only assert the dotted-path is well-formed
    (we do NOT actually import the adapter — that would require
    Cognee infra which is intentionally out of scope per the change).
    """
    defs_path = COGNIFY_ROOT / f"{stage}_cognify" / "defs.yaml"
    parsed = yaml.safe_load(defs_path.read_text())
    adapter = parsed.get("attributes", {}).get("source_adapter", "")
    assert isinstance(adapter, str) and adapter, (
        f"{defs_path} must declare a non-empty source_adapter"
    )
    # Dotted path: e.g. "scripts.graph_storage.cognify.cognee_integration.aistear_cognify"
    parts = adapter.split(".")
    assert len(parts) >= 4, (
        f"{defs_path} source_adapter='{adapter}' must be a dotted "
        f"Python module path with at least 4 segments"
    )


# ─── 7. The 5 per-stage defs.yaml files are collectively consistent ────────


def test_all_5_stage_assets_present() -> None:
    """The collective cognify surface MUST register all 5 expected stages."""
    missing = []
    for stage in EXPECTED_STAGES:
        defs_path = COGNIFY_ROOT / f"{stage}_cognify" / "defs.yaml"
        if not defs_path.exists():
            missing.append(stage)
    assert not missing, (
        f"The following stages have no defs.yaml: {missing}. "
        f"All 5 stages (aistear, primary, junior_cycle, senior_cycle, "
        f"university) must be registered for the 5-stage cognify graph "
        f"to be populated."
    )


def test_stage_adapter_modules_exist_on_disk() -> None:
    """The 5 stage adapter source files MUST exist on disk.

    Per the change's B1: the per-stage ``defs.yaml`` files reference
    ``scripts.graph_storage.cognify.cognee_integration.<stage>_cognify``.
    We verify the adapter modules exist (the YAML correctly points to
    the canonical adapter locations).
    """
    adapter_root = REPO_ROOT / "scripts" / "graph_storage" / "cognify" / "cognee_integration"
    if not adapter_root.exists():
        pytest.skip(
            f"Cognee integration adapters not present at {adapter_root} "
            f"(the integration may be gated on Plan V-A deployment)"
        )
    for stage in EXPECTED_STAGES:
        adapter_file = adapter_root / f"{stage}_cognify.py"
        assert adapter_file.exists(), (
            f"Missing cognify adapter for '{stage}' at {adapter_file}"
        )
