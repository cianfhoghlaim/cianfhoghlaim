"""orchestration.pipelines._shared.dagster_dlt_integration

Wave 2 (per the 2026-08-24-master-refactor-v1 / Wave 2 tasks 2.2 +
2.4 + the canonical `dagster-pipeline-components` spec at
`openspec/changes/2026-08-24-master-refactor-v1/specs/dagster-pipeline-components/spec.md`).

The single source of truth for the Cianfhoghlaim `translation:` defaults that
every per-pipeline Component (`orchestration/pipelines/<mirror>/<source>/defs.yaml`)
inherits when it declares:

    type: dagster_dlt.DltLoadCollectionComponent
    attributes:
      loads:
        - pipeline: <python.path.to.dlt.pipeline>
          source: <python.path.to.dlt.source>

Per the Dagster dlt integration docs
(<https://docs.dagster.io/integrations/libraries/dlt>), the canonical
`DltLoadCollectionComponent.loads[*].translation` accepts a callable
`(AssetSpec, DltResourceTranslatorData) -> AssetSpec`. The default
`TranslationFnResolver` exposes `resource` + `pipeline` as kwargs to
the translation callable.

The Cianfhoghlaim canonical default — `kcg_default_translation` below — adds
the per-resource `group_name` (the canonical `<layer>_<domain>_<nation>_<kind>`
shape per the master plan §7.2 naming map) + the per-resource tags
(the canonical 5-tag pattern: `domain`, `nation`, `subject`,
`pipeline_kind`, `wave=2`) + the asset description.

The functions in this module are:
- `kcg_default_translation(spec, data)` — the canonical Cianfhoghlaim default
  callable; usable as `translation: orchestration.pipelines._shared.dagster_dlt_integration.kcg_default_translation`
  in any per-pipeline `defs.yaml`.
- `build_translation_for_pipeline(group_name, tags)` — factory that
  builds a custom translation callable for a specific pipeline group.
- `build_dlt_pipeline(source_module, dataset_name, destination)` —
  the canonical `dlt.Pipeline` factory used by the per-pipeline
  Components' `loads[*].pipeline` field.
- `high_churn_source_modules()` — the 5 modules that should default to
  `LOCAL_FILESYSTEM` state (per master plan §3.3 + the
  `state_helpers.LOCAL_FILESYSTEM_DEFAULTS` set).

The canonical `type: dagster_dlt.DltLoadCollectionComponent` line in
each per-pipeline `defs.yaml` is what wires the Cianfhoghlaim Component to the
canonical Dagster dlt integration pattern. The `DltLoadCollectionComponent`
is auto-discovered via `dagster_dlt.DltLoadCollectionComponent` (no
custom registration is required — it's a built-in Dagster component).
"""
from __future__ import annotations

import importlib
from collections.abc import Callable
from typing import Any

import dagster as dg
import dlt
from dagster_dlt import DagsterDltResource
from dagster_dlt.translator import DltResourceTranslatorData


# ---------------------------------------------------------------------------
# Cianfhoghlaim canonical group_name + tag conventions
# ---------------------------------------------------------------------------
#
# 2026-08-27 Cianfhoghlaim rename — accept legacy `kcg:` tags for one release
# cycle. Will be removed in the 2026-09-XX release. New assets MUST use the
# `cianfhoghlaim:` prefix. Any asset materialised before this change still
# carries `kcg:`-prefixed tags in the Dagster event log; its tags are only
# rewritten on the next materialisation.
# See openspec/changes/2026-08-27-kcg-rename-and-kcg-dir-merge-v1/tasks.md.
_LEGACY_TAG_PREFIX = "kcg:"
_NEW_TAG_PREFIX = "cianfhoghlaim:"
#
# Per master plan §7.2 (the "naming map"):
#
#   group_name: "{layer}_{domain}_{nation}_{kind}"
#     layer  ∈ {1_ingestion, 2_materials, 3_model_lifecycle, 4_asset_generation, 5_agent_ops}
#     domain ∈ {education, heritage, law, medicine, statistics, media_intel, ...}
#     nation ∈ {ie, gb_eng, gb_sct, gb_wls, gb_nir, fr, de, ...} (ISO-3166-1 alpha-2 + sub-jurisdiction)
#     kind   ∈ {syllabus, exam_papers, personal_archive, official_docs, comics, crypto, pdf, media}
#
#   canonical 5 tags (always present):
#     - cianfhoghlaim:domain=<domain>
#     - cianfhoghlaim:nation=<nation>
#     - cianfhoghlaim:subject=<subject>      # empty for non-subject pipelines
#     - cianfhoghlaim:pipeline_kind=<kind>
#     - cianfhoghlaim:wave=2                 # the master-refactor wave that authored the Component
# ---------------------------------------------------------------------------


def _has_tag(tags: dict[str, str], suffix: str) -> bool:
    """Return True if `tags` carries either the new or the legacy tag.

    2026-08-27 Cianfhoghlaim rename back-compat shim: a caller-supplied
    legacy `kcg:<suffix>` tag still wins over the canonical default, so a
    pipeline that has not yet been re-materialised does not gain a
    duplicate `cianfhoghlaim:<suffix>` tag with a different value.
    """
    return f"{_NEW_TAG_PREFIX}{suffix}" in tags or f"{_LEGACY_TAG_PREFIX}{suffix}" in tags


def _set_default_tag(tags: dict[str, str], suffix: str, value: str) -> None:
    """Set `cianfhoghlaim:<suffix>` unless the new or legacy tag is present."""
    if not _has_tag(tags, suffix):
        tags[f"{_NEW_TAG_PREFIX}{suffix}"] = value


def _classify_pipeline(source_module_path: str) -> dict[str, str]:
    """Classify a `dlt_sources.<...>` Python module path into the 4-field
    Cianfhoghlaim canonical group_name tuple.

    Per master plan §7.2, the canonical group_name is
    `{layer}_{domain}_{nation}_{kind}`. The default layer is
    `1_ingestion` (the per-pipeline Component is by definition a
    load-bearing pipeline; the L2/L3/L4/L5 layers live in
    `orchestration/defs/`).

    The classification is heuristic — for the 95% case the dlt source
    module path under `dlt_sources/` mirrors the canonical Cianfhoghlaim
    `orchestration/pipelines/` path; the `domain` is the first path
    component after `dlt_sources.`; the `nation` is the second (or the
    closest ISO-3166-1 alpha-2 / sub-jurisdiction code); the `kind`
    defaults to `pipeline` and is overridden by the `pipeline_kind`
    attribute on the per-pipeline `defs.yaml`.

    Examples:
        dlt_sources.education.ireland.british_isles.ncca_gaeilge
        → {domain: education, nation: ie, subject: gaeilge, kind: syllabus}

        dlt_sources.education.tertiary.uog.exam_papers
        → {domain: education, nation: ie, subject: uog, kind: exam_papers}

        dlt_sources.education.england.british_isles.education
        → {domain: education, nation: gb_eng, kind: pipeline}

        dlt_sources.media_intel
        → {domain: media_intel, nation: cross, kind: media}
    """
    # Strip the leading `dlt_sources.` prefix + the legacy aliases.
    path = source_module_path
    for prefix in ("dlt_sources.", "cianfhoghlaim.dlt_sources."):
        if path.startswith(prefix):
            path = path[len(prefix):]
            break

    parts = path.split(".")

    # The default classification is empty; each field is filled in if
    # the parts match a canonical Cianfhoghlaim layout.
    classification: dict[str, str] = {
        "domain": "unknown",
        "nation": "cross",
        "subject": "",
        "kind": "pipeline",
        "layer": "1_ingestion",
    }

    # First part = domain (education / british_isles / commonwealth / ...)
    if parts:
        classification["domain"] = parts[0]

    # Walk the path looking for the canonical nation + subject + kind.
    ISO_3166_2_BRITISH_ISLES = {
        "ireland", "england", "scotland", "wales", "northern_ireland",
        "sct_wls_ni", "isle_of_man", "jersey", "guernsey", "crown_dependencies",
    }
    COMMONWEALTH_NATIONS = {
        "australia", "canada", "india", "new_zealand", "nigeria",
        "south_africa",
    }
    EUROPEAN_NATIONS = {
        "albania", "austria", "belgium", "bosnia_and_herzegovina",
        "bulgaria", "croatia", "cyprus", "czechia", "denmark", "estonia",
        "finland", "france", "georgia", "germany", "greece", "hungary",
        "iceland", "italy", "kosovo", "latvia", "liechtenstein",
        "lithuania", "luxembourg", "malta", "moldova", "montenegro",
        "netherlands", "north_macedonia", "norway", "poland", "portugal",
        "romania", "serbia", "slovakia", "slovenia", "spain", "sweden",
        "switzerland", "turkey", "ukraine",
    }
    AMERICAN_NATIONS = {
        "brazil", "mexico", "venezuela", "united_states",
    }

    for part in parts[1:]:
        if part in ISO_3166_2_BRITISH_ISLES:
            # Map British Isles sub-jurisdictions to their canonical
            # 2-letter codes.
            nation_map = {
                "ireland": "ie",
                "england": "gb_eng",
                "scotland": "gb_sct",
                "wales": "gb_wls",
                "northern_ireland": "gb_nir",
                "sct_wls_ni": "gb_cross",
                "isle_of_man": "gb_iom",
                "jersey": "gb_jey",
                "guernsey": "gb_ggy",
                "crown_dependencies": "gb_cdp",
            }
            classification["nation"] = nation_map.get(part, part)
        elif part in COMMONWEALTH_NATIONS:
            classification["nation"] = part[:3]
        elif part in EUROPEAN_NATIONS:
            classification["nation"] = "eu_" + part
        elif part in AMERICAN_NATIONS:
            classification["nation"] = "am_" + part

    # The kind is the leaf part if it doesn't match a domain/nation.
    if parts:
        leaf = parts[-1]
        if leaf not in ISO_3166_2_BRITISH_ISLES | COMMONWEALTH_NATIONS | EUROPEAN_NATIONS | AMERICAN_NATIONS:
            # Strip the trailing `_source` / `_pipeline` suffix if present.
            for suffix in ("_source", "_pipeline"):
                if leaf.endswith(suffix):
                    leaf = leaf[: -len(suffix)]
                    break
            classification["kind"] = leaf
            # If the kind looks like a subject (ncca_*, sec_*, etc.), use it.
            if classification["domain"] == "education" and "_" in leaf:
                classification["subject"] = leaf

    return classification


def kcg_default_translation(
    spec: dg.AssetSpec,
    data: DltResourceTranslatorData,
) -> dg.AssetSpec:
    """The Cianfhoghlaim canonical translation callable for `DltLoadCollectionComponent`.

    Per master plan §7.2, this callable applies the canonical
    `{layer}_{domain}_{nation}_{kind}` group_name + the canonical
    5-tag pattern (`cianfhoghlaim:domain` + `cianfhoghlaim:nation` +
    `cianfhoghlaim:subject` + `cianfhoghlaim:pipeline_kind` +
    `cianfhoghlaim:wave=2`).

    The default `TranslationFnResolver` exposes `resource` + `pipeline`
    as kwargs, so we extract the source module from the pipeline
    attribute (set by `build_dlt_pipeline` below) and classify it.

    Usage in a per-pipeline `defs.yaml`:

        type: dagster_dlt.DltLoadCollectionComponent
        attributes:
          loads:
            - pipeline: orchestration.pipelines._shared.dagster_dlt_integration.build_dlt_pipeline|dlt_sources.education.tertiary.uog.exam_papers
              source: dlt_sources.education.tertiary.uog.exam_papers.exam_papers_source
              translation: orchestration.pipelines._shared.dagster_dlt_integration.kcg_default_translation
    """
    # Try to derive the classification from the dlt source module path.
    # The DagsterDltTranslator attaches the source module to the data
    # via `data.resource._factory_module` (set by @dlt.source decorator
    # introspection); fall back to a generic classification if unavailable.
    source_module_path = ""
    try:
        source_module_path = data.resource._factory_module  # type: ignore[attr-defined]
    except AttributeError:
        pass

    if not source_module_path:
        # Fallback: walk the resource's qualname.
        source_module_path = getattr(data.resource, "__module__", "") or ""

    classification = _classify_pipeline(source_module_path)

    layer = classification["layer"]
    domain = classification["domain"]
    nation = classification["nation"]
    kind = classification["kind"]
    subject = classification["subject"]

    group_name = f"{layer}_{domain}_{nation}_{kind}"
    if subject:
        group_name = f"{group_name}_{subject}"

    # Preserve any caller-supplied tags (the user-provided ones win — including
    # legacy `kcg:`-prefixed tags, per the 2026-08-27 rename back-compat shim).
    new_tags = dict(spec.tags or {})
    _set_default_tag(new_tags, "domain", domain)
    _set_default_tag(new_tags, "nation", nation)
    _set_default_tag(new_tags, "subject", subject)
    _set_default_tag(new_tags, "pipeline_kind", kind)
    _set_default_tag(new_tags, "wave", "2")

    return spec.replace_attributes(
        group_name=group_name,
        tags=new_tags,
        description=(
            spec.description
            or f"Cianfhoghlaim per-pipeline Component (Wave 2 master refactor) for "
            f"`{source_module_path}` — group `{group_name}`."
        ),
    )


def build_translation_for_pipeline(
    group_name: str,
    tags: dict[str, str] | None = None,
) -> Callable[[dg.AssetSpec, DltResourceTranslatorData], dg.AssetSpec]:
    """Build a custom translation callable for a specific pipeline group.

    Used by per-pipeline `defs.yaml` that need to override the default
    `group_name` (e.g., the BIEP v3 jurisdiction pipelines that want
    `group_name: 2_materials_<jurisdiction>_lc_<subject>` instead of
    the default `1_ingestion_<...>`).

    Args:
        group_name: The canonical `{layer}_{domain}_{nation}_{kind}` shape.
        tags: Optional extra tags to merge with the canonical 5-tag set.

    Returns:
        A callable suitable for `loads[*].translation` in a per-pipeline
        `defs.yaml`.
    """
    extra_tags = tags or {}

    def _translation(
        spec: dg.AssetSpec,
        data: DltResourceTranslatorData,
    ) -> dg.AssetSpec:
        new_tags = dict(spec.tags or {})
        _set_default_tag(new_tags, "wave", "2")
        new_tags.update(extra_tags)
        return spec.replace_attributes(
            group_name=group_name,
            tags=new_tags,
            description=(
                spec.description
                or f"Cianfhoghlaim per-pipeline Component (Wave 2) — group `{group_name}`."
            ),
        )

    return _translation


# ---------------------------------------------------------------------------
# Canonical dlt.Pipeline factory for the per-pipeline Components
# ---------------------------------------------------------------------------
#
# The `DltLoadCollectionComponent.loads[*].pipeline` field expects a
# `dlt.Pipeline` instance (resolved via Python path). The convention is
# to expose one factory function per pipeline module that returns a
# fresh `dlt.Pipeline`. The pipeline is constructed with a single
# canonical destination (the Cianfhoghlaim default is `ducklake` via the
# `named_destinations` factory from `dlt_sources.common.destinations`).
# ---------------------------------------------------------------------------


def build_dlt_pipeline(
    source_module: str,
    dataset_name: str | None = None,
    destination: str = "ducklake_cianfhoghlaim",
) -> dlt.Pipeline:
    """Build the canonical `dlt.Pipeline` for a per-pipeline Component.

    Args:
        source_module: The `dlt_sources.<...>` Python module path (the
            `@dlt.source` decorated function module).
        dataset_name: The destination dataset name. Defaults to the
            source module's last path component (the canonical Cianfhoghlaim
            convention).
        destination: The destination alias. Defaults to
            `ducklake_cianfhoghlaim` (the canonical Cianfhoghlaim DuckLake
            destination per `dlt_sources.common.destinations.named_destinations`).

    Returns:
        A `dlt.Pipeline` instance configured with the canonical Cianfhoghlaim
        dataset + destination.
    """
    # The module path is used purely for the dataset_name default; the
    # actual pipeline instance is constructed against the canonical
    # destination.
    if dataset_name is None:
        dataset_name = source_module.rsplit(".", 1)[-1]
        # Strip the trailing `_source` / `_pipeline` suffix.
        for suffix in ("_source", "_pipeline"):
            if dataset_name.endswith(suffix):
                dataset_name = dataset_name[: -len(suffix)]
                break

    return dlt.pipeline(
        pipeline_name=f"kcg_wave2_{dataset_name}",
        destination=destination,
        dataset_name=dataset_name,
        progress="log",
        dev_mode=False,
    )


# ---------------------------------------------------------------------------
# High-churn source modules — fed into state_helpers.LOCAL_FILESYSTEM_DEFAULTS
# ---------------------------------------------------------------------------
#
# Per master plan §3.3, the 5 high-churn sources (NCCA, SEC, CCEA, SQA,
# WJEC) should default to `LOCAL_FILESYSTEM` state (the Dagster 1.13+
# canonical state strategy). These modules are used by the per-pipeline
# Components' `defs_state` block via the `state_helpers` module.
# ---------------------------------------------------------------------------


def high_churn_source_modules() -> tuple[str, ...]:
    """Return the tuple of `dlt_sources.<...>` module paths that the
    per-pipeline Components should default to `LOCAL_FILESYSTEM` state
    backing for.

    Per master plan §3.3, these are the 5 high-churn sources whose
    `@dlt.source` function signature + table schema change frequently:

    - NCCA (Ireland's National Council for Curriculum and Assessment)
    - SEC (State Examinations Commission)
    - CCEA (Council for the Curriculum, Examinations and Assessment, NI)
    - SQA (Scottish Qualifications Authority)
    - WJEC (Welsh Joint Education Committee / CBAC)

    Returns:
        Tuple of `dlt_sources.<...>` Python module paths.
    """
    return (
        # NCCA — Ireland's NCCA syllabuses (the LC + JC + primary cycles)
        "dlt_sources.education.ireland.british_isles.education.ncca",
        "dlt_sources.education.ireland.british_isles.ncca_gaeilge",
        "dlt_sources.education.ireland.british_isles.ncca_mathematics",
        "dlt_sources.education.ireland.british_isles.ncca_english",
        "dlt_sources.education.ireland.british_isles.ncca_geography",
        "dlt_sources.education.ireland.british_isles.ncca_chemistry",
        "dlt_sources.education.ireland.british_isles.ncca_computer_science",
        # SEC — Ireland's State Examinations Commission (exam papers + marking schemes)
        "dlt_sources.education.ireland.british_isles.examinations",
        "dlt_sources.education.ireland.british_isles.examinations_papers",
        "dlt_sources.education.ireland.british_isles.examinations_marking_schemes",
        "dlt_sources.education.ireland.british_isles.sec_aural_transcripts",
        # CCEA — Northern Ireland Council for the Curriculum, Examinations and Assessment
        "dlt_sources.education.northern_ireland.british_isles.education",
        # SQA — Scottish Qualifications Authority
        "dlt_sources.education.scotland.british_isles.education",
        # WJEC — Welsh Joint Education Committee (Welsh-medium + bilingual)
        "dlt_sources.education.wales.british_isles.education",
    )


# ---------------------------------------------------------------------------
# Singleton DagsterDltResource — the canonical "dlt" resource key
# ---------------------------------------------------------------------------

_kcg_dlt_resource: DagsterDltResource | None = None


def get_kcg_dlt_resource() -> DagsterDltResource:
    """The canonical singleton DagsterDltResource (the "dlt" resource key).

    Per `orchestration/definitions.py`, the `dagster-dlt` resource is
    registered under the "dlt" key. This singleton is the same instance
    that `dg.load_defs()` injects into every `@dlt_assets`-decorated
    asset via the `dagster_dlt_translator`.
    """
    global _kcg_dlt_resource
    if _kcg_dlt_resource is None:
        _kcg_dlt_resource = DagsterDltResource()
    return _kcg_dlt_resource


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    # The canonical Cianfhoghlaim translation callable (used by per-pipeline defs.yaml)
    "kcg_default_translation",
    # The custom-translation factory (used when overriding group_name)
    "build_translation_for_pipeline",
    # The canonical dlt.Pipeline factory (used by per-pipeline defs.yaml)
    "build_dlt_pipeline",
    # The high-churn source modules (consumed by state_helpers)
    "high_churn_source_modules",
    # The canonical DagsterDltResource singleton
    "get_kcg_dlt_resource",
    # The internal classifier (exposed for testing + sister-repo reuse)
    "_classify_pipeline",
]
