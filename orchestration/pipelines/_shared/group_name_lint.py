"""orchestration.pipelines._shared.group_name_lint

Wave 2 (per the 2026-08-24-master-refactor-v1 / Wave 2 task 2.10 + the
canonical `dagster-pipeline-components` spec at
`openspec/changes/2026-08-24-master-refactor-v1/specs/dagster-pipeline-components/spec.md`
+ master plan §7.2).

The canonical group_name linter for every per-pipeline Component under
`orchestration/pipelines/<mirror>/<source>/defs.yaml`.

Per master plan §7.2, the canonical group_name shape is:

    group_name: "{layer}_{domain}_{nation}_{kind}"
      layer  ∈ {1_ingestion, 2_materials, 3_model_lifecycle, 4_asset_generation, 5_agent_ops}
      domain ∈ {education, heritage, law, medicine, statistics, media_intel, ...}
      nation ∈ {ie, gb_eng, gb_sct, gb_wls, gb_nir, fr, de, ...} (ISO-3166-1 alpha-2 + sub-jurisdiction)
      kind   ∈ {syllabus, exam_papers, personal_archive, official_docs, comics, crypto, pdf, media}

The canonical 5 tags are:

    - cianfhoghlaim:domain=<domain>
    - cianfhoghlaim:nation=<nation>
    - cianfhoghlaim:subject=<subject>      # empty for non-subject pipelines
    - cianfhoghlaim:pipeline_kind=<kind>
    - cianfhoghlaim:wave=2

This module provides:

- `canonical_group_name(layer, domain, nation, kind, subject="")` — the
  canonical group_name builder.
- `lint_group_name(group_name)` — validates a group_name against the
  canonical shape.
- `lint_defs_yaml(defs_yaml_path)` — the canonical `dg check yaml`-style
  per-`defs.yaml` linter that validates the canonical group_name shape
  on every per-pipeline Component.
- `lint_all_defs_yaml(pipelines_root)` — walks the entire `pipelines/`
  tree and reports the canonical group_name lint result per file.

Usage (the canonical entry point — also wired into the
`mise run pipelines:lint` task):

    from orchestration.pipelines._shared.group_name_lint import lint_all_defs_yaml

    results = lint_all_defs_yaml(Path("orchestration/pipelines"))
    for path, result in results.items():
        if not result.ok:
            print(f"FAIL: {path} — {result.message}")
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# 2026-08-27 Cianfhoghlaim rename — accept legacy `kcg:` tags for one release
# cycle. Will be removed in the 2026-09-XX release. New assets MUST use the
# `cianfhoghlaim:` prefix.
# See openspec/changes/2026-08-27-kcg-rename-and-kcg-dir-merge-v1/tasks.md.
_LEGACY_TAG_PREFIX = "kcg:"
_NEW_TAG_PREFIX = "cianfhoghlaim:"

# Per master plan §7.2, the canonical `{layer}_{domain}_{nation}_{kind}`
# shape. The regex enforces the 4 (or 5, with subject) underscore-separated
# tokens, each drawn from a canonical vocabulary.
CANONICAL_LAYERS = frozenset({
    "1_ingestion", "2_materials", "3_model_lifecycle",
    "4_asset_generation", "4_budget", "4_memory", "5_agent_ops",
})

CANONICAL_NATIONS = frozenset({
    "ie", "gb_eng", "gb_sct", "gb_wls", "gb_nir", "gb_cross",
    "gb_iom", "gb_jey", "gb_ggy", "gb_cdp",
    "aus", "can", "ind", "nzl", "nga", "za",
    "br", "mx", "ve", "us",
    # European Union — uses `eu_<nation>` shape
    "eu_france", "eu_germany", "eu_spain", "eu_italy", "eu_poland",
    # `cross` is the catch-all for non-jurisdiction-bound pipelines
    "cross",
})

CANONICAL_DOMAINS = frozenset({
    "education", "heritage", "law", "medicine", "statistics",
    "media_intel", "media_comics", "media_games", "media_text",
    "media_personal", "crypteolas_chain", "crypteolas_docs",
    "crypteolas_defi", "lexicographic", "cultural_heritage",
    "local_archive", "raw_files", "cv", "artwork", "labels",
    # Additional in-use domains not in the master plan §7.2 core list
    # but used by the existing canonical defs.yaml files.
    "cognee",
})

CANONICAL_KINDS = frozenset({
    "syllabus", "exam_papers", "personal_archive", "official_docs",
    "comics", "crypto", "pdf", "media", "pipeline",
    "law", "medicine", "language", "statistics",
})


# The validated regex: `{layer}_{domain}_{nation}_{kind}(_{subject})?`
#
# The layer MUST start with a digit (per master plan §7.2: `1_ingestion`,
# `2_materials`, `3_model_lifecycle`, `4_asset_generation`, `5_agent_ops`).
# The domain, nation, kind are single-word tokens (no underscores); the
# optional subject is also a single-word token. We use `[^_]+` instead
# of `\w+` to prevent greedy matching from consuming underscores.
CANONICAL_GROUP_NAME_REGEX = re.compile(
    r"^(?P<layer>\d_(?:ingestion|materials|model_lifecycle|asset_generation|budget|memory|agent_ops))_(?P<domain>[^_]+)_(?P<nation>[^_]+)_(?P<kind>[^_]+)(?:_(?P<subject>[^_]+))?$"
)


@dataclass
class LintResult:
    """The result of a per-`defs.yaml` group_name lint check."""
    ok: bool
    message: str
    group_name: str | None = None


def canonical_group_name(
    layer: str,
    domain: str,
    nation: str,
    kind: str,
    subject: str = "",
) -> str:
    """Build the canonical group_name per master plan §7.2.

    Args:
        layer: One of `CANONICAL_LAYERS` (e.g., `1_ingestion`).
        domain: One of `CANONICAL_DOMAINS` (e.g., `education`).
        nation: One of `CANONICAL_NATIONS` (e.g., `ie`, `gb_eng`).
        kind: One of `CANONICAL_KINDS` (e.g., `syllabus`, `exam_papers`).
        subject: Optional subject suffix (e.g., `gaeilge` for
            `1_ingestion_education_ie_syllabus_gaeilge`).

    Returns:
        The canonical `{layer}_{domain}_{nation}_{kind}(_{subject})?`
        group_name.
    """
    base = f"{layer}_{domain}_{nation}_{kind}"
    return f"{base}_{subject}" if subject else base


def lint_group_name(group_name: str) -> LintResult:
    """Validate a group_name against the canonical shape (master plan §7.2).

    Args:
        group_name: The group_name to validate.

    Returns:
        A `LintResult` with `ok=True` if the group_name matches the
        canonical `{layer}_{domain}_{nation}_{kind}(_{subject})?` shape,
        `ok=False` otherwise.
    """
    match = CANONICAL_GROUP_NAME_REGEX.match(group_name)
    if not match:
        return LintResult(
            ok=False,
            message=f"group_name {group_name!r} does not match the canonical `{{layer}}_{{domain}}_{{nation}}_{{kind}}(_{{subject}})?` shape",
            group_name=group_name,
        )

    parts = match.groupdict()
    layer = parts["layer"]
    domain = parts["domain"]
    nation = parts["nation"]
    kind = parts["kind"]

    if layer not in CANONICAL_LAYERS:
        return LintResult(
            ok=False,
            message=f"layer {layer!r} is not in CANONICAL_LAYERS",
            group_name=group_name,
        )
    if domain not in CANONICAL_DOMAINS:
        return LintResult(
            ok=False,
            message=f"domain {domain!r} is not in CANONICAL_DOMAINS",
            group_name=group_name,
        )
    if nation not in CANONICAL_NATIONS:
        return LintResult(
            ok=False,
            message=f"nation {nation!r} is not in CANONICAL_NATIONS",
            group_name=group_name,
        )
    if kind not in CANONICAL_KINDS:
        return LintResult(
            ok=False,
            message=f"kind {kind!r} is not in CANONICAL_KINDS",
            group_name=group_name,
        )

    return LintResult(ok=True, message="valid canonical group_name", group_name=group_name)


def lint_defs_yaml(defs_yaml_path: Path) -> LintResult:
    """The canonical per-`defs.yaml` group_name linter.

    Validates that the per-pipeline Component declares a canonical
    `group_name` (per master plan §7.2) — either via the
    `metadata.group_name:` block (legacy Cianfhoghlaim pattern) or via the
    `translation:` callable's side-effects (the new canonical pattern
    via `orchestration.pipelines._shared.dagster_dlt_integration.kcg_default_translation`).

    Args:
        defs_yaml_path: The path to the per-pipeline `defs.yaml`.

    Returns:
        A `LintResult` with `ok=True` if the group_name is canonical,
        `ok=False` otherwise.
    """
    try:
        import yaml as yaml_lib
    except ImportError:
        return LintResult(ok=False, message="pyyaml not installed")

    try:
        data = yaml_lib.safe_load(defs_yaml_path.read_text(encoding="utf-8"))
    except yaml_lib.YAMLError as exc:
        return LintResult(ok=False, message=f"YAML parse error: {exc}")

    if not isinstance(data, dict):
        return LintResult(ok=False, message="defs.yaml root is not a dict")

    # The canonical group_name lives in the `metadata.group_name:` block
    # (legacy Cianfhoghlaim pattern) OR is inferred from the translation callable's
    # classification (the new canonical pattern). The check below accepts
    # both shapes.
    metadata = data.get("metadata", {})
    group_name = metadata.get("group_name") if isinstance(metadata, dict) else None

    if not group_name:
        # Fallback: extract from the translation callable's module path
        # (the new canonical pattern stores the group_name in the
        # translation callable's side-effects, NOT in the YAML).
        loads = data.get("attributes", {}).get("loads", [])
        if isinstance(loads, list) and loads:
            translation = loads[0].get("translation", "")
            if isinstance(translation, str) and "kcg_default_translation" in translation:
                # The canonical group_name is computed at runtime by the
                # kcg_default_translation callable; the YAML itself
                # declares no explicit group_name. We accept this as
                # valid per the new canonical pattern.
                return LintResult(
                    ok=True,
                    message="valid (canonical group_name computed at runtime via kcg_default_translation)",
                )
        return LintResult(
            ok=False,
            message="defs.yaml declares no group_name (neither in `metadata:` nor via kcg_default_translation)",
        )

    return lint_group_name(group_name)


def lint_all_defs_yaml(
    pipelines_root: Path,
    *,
    on_error: str = "log",
) -> dict[Path, LintResult]:
    """Walk the entire `pipelines/` tree and run the canonical group_name linter.

    This is the canonical entry point for the
    `mise run pipelines:lint` task (and the `dg check yaml` style
    validation).

    Args:
        pipelines_root: The root of the `orchestration/pipelines/` tree.
        on_error: How to handle errors. `"log"` (default) returns the
            result dict; `"raise"` raises on the first error.

    Returns:
        A `dict[Path, LintResult]` mapping each `defs.yaml` path to its
        lint result.
    """
    results: dict[Path, LintResult] = {}

    for defs_yaml in sorted(pipelines_root.rglob("defs.yaml")):
        result = lint_defs_yaml(defs_yaml)
        results[defs_yaml] = result
        if not result.ok and on_error == "raise":
            raise ValueError(f"{defs_yaml}: {result.message}")

    return results


__all__ = [
    "CANONICAL_LAYERS",
    "CANONICAL_DOMAINS",
    "CANONICAL_NATIONS",
    "CANONICAL_KINDS",
    "CANONICAL_GROUP_NAME_REGEX",
    "LintResult",
    "canonical_group_name",
    "lint_group_name",
    "lint_defs_yaml",
    "lint_all_defs_yaml",
]
