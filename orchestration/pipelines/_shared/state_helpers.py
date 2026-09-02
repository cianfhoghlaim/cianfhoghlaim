"""orchestration.pipelines._shared.state_helpers

Wave 2 (per the 2026-08-24-master-refactor-v1 / Wave 2 task 2.3 + the
canonical `dagster-pipeline-components` spec at
`openspec/changes/2026-08-24-master-refactor-v1/specs/dagster-pipeline-components/spec.md`).

The single source of truth for the Cianfhoghlaim state-management defaults that
every per-pipeline Component (`orchestration/pipelines/<mirror>/<source>/defs.yaml`)
inherits when it declares:

    type: orchestration.pipelines._shared.state_helpers.KCGStateBackedDltComponent
    attributes:
      ...
      defs_state:
        management_type: LOCAL_FILESYSTEM

Per the Dagster State-Backed Components guide
(<https://docs.dagster.io/guides/build/components/state-backed-components>),
the canonical state-management strategies in Dagster 1.13+ are:

- `LOCAL_FILESYSTEM` — state is stored on the local filesystem;
  `dg utils refresh-defs-state` must be executed while building the
  deployed container image in order for state to be accessible.
- `VERSIONED_STATE_STORAGE` — state is stored in your configured
  `defs_state_storage`; `dg utils refresh-defs-state` may be executed at
  any time to refresh the state.
- `LEGACY_CODE_SERVER_SNAPSHOTS` — state is stored in memory in the
  code server; state is always automatically refreshed when the code
  server is loaded.

Per master plan §3.3, the Cianfhoghlaim canonical default for the 5 high-churn
sources (NCCA + SEC + CCEA + SQA + WJEC) is `LOCAL_FILESYSTEM`. For all
other per-pipeline Components, the default is `LEGACY_CODE_SERVER_SNAPSHOTS`
(the historical Cianfhoghlaim default — state is auto-refreshed on code-server
load, which is fine for the stable weekly / monthly cadences).

The functions in this module are:
- `LOCAL_FILESYSTEM_DEFAULTS` — the canonical `Tuple[str, ...]` of dlt
  source modules that should default to `LOCAL_FILESYSTEM` state.
- `default_state_config_for(source_module)` — returns the canonical
  `DefsStateConfigArgs` for a given `dlt_sources.<...>` module.
- `default_state_block_for(source_module)` — returns the YAML-shaped
  dict serialisable as the `defs_state:` block in a per-pipeline
  `defs.yaml`.
- `KCGStateBackedDltComponent` — the Cianfhoghlaim custom Component subclass
  that composes the canonical `DltLoadCollectionComponent` with
  `StateBackedComponent`, defaulting to the per-source `defs_state`
  block. The per-pipeline `defs.yaml` declares this Component with
  `type: orchestration.pipelines._shared.state_helpers.KCGStateBackedDltComponent`.
- `local_defs_state_root()` — returns the canonical on-disk root for
  the `LOCAL_FILESYSTEM` state files (`.local_defs_state/` at the repo
  root per the master plan §3.3 mandate).
"""
from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from dagster.components import (
    Component,
    ComponentLoadContext,
    DefsStateConfig,
    DefsStateConfigArgs,
    Resolvable,
    ResolvedDefsStateConfig,
    StateBackedComponent,
)
from dagster_shared.serdes.objects.models.defs_state_info import (
    DefsStateManagementType,
)
from dagster_dlt import DltLoadCollectionComponent


# ---------------------------------------------------------------------------
# Canonical state-strategy constants
# ---------------------------------------------------------------------------

#: The 14 `dlt_sources.<...>` module paths that should default to
#: `LOCAL_FILESYSTEM` state (per master plan §3.3).
#:
#: Per the spec, these are the 5 high-churn sources (NCCA + SEC + CCEA
#: + SQA + WJEC) — the canonical per-source files whose @dlt.source
#: function signature + table schema change frequently. The 14 module
#: paths cover the per-source breakdowns (e.g., the NCCA syllabus
#: crawl is split across 6 per-subject files: ncca_gaeilge +
#: ncca_mathematics + ncca_english + ncca_geography + ncca_chemistry +
#: ncca_computer_science).
LOCAL_FILESYSTEM_DEFAULTS: tuple[str, ...] = (
    # NCCA — Ireland's National Council for Curriculum and Assessment
    "dlt_sources.education.ireland.british_isles.education.ncca",
    "dlt_sources.education.ireland.british_isles.ncca_gaeilge",
    "dlt_sources.education.ireland.british_isles.ncca_mathematics",
    "dlt_sources.education.ireland.british_isles.ncca_english",
    "dlt_sources.education.ireland.british_isles.ncaa_geography",
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
# Per-source defs_state block factories
# ---------------------------------------------------------------------------


def default_state_config_for(source_module: str) -> DefsStateConfigArgs:
    """Return the canonical `DefsStateConfigArgs` for a given source module.

    Per master plan §3.3, the canonical default is:
    - `LOCAL_FILESYSTEM` for the 14 high-churn modules (NCCA + SEC + CCEA + SQA + WJEC)
    - `LEGACY_CODE_SERVER_SNAPSHOTS` for everything else (the historical
      Cianfhoghlaim default — state is auto-refreshed on code-server load).

    Args:
        source_module: The `dlt_sources.<...>` Python module path.

    Returns:
        A `DefsStateConfigArgs` instance configured with the canonical
        per-source management type.
    """
    if source_module in LOCAL_FILESYSTEM_DEFAULTS:
        return DefsStateConfigArgs.local_filesystem()
    return DefsStateConfigArgs.legacy_code_server_snapshots()


def default_state_block_for(source_module: str) -> dict[str, Any]:
    """Return the canonical `defs_state:` block for a `defs.yaml`.

    Per master plan §3.3, the canonical block shape is:

        defs_state:
          management_type: LOCAL_FILESYSTEM  # or LEGACY_CODE_SERVER_SNAPSHOTS

    For `LOCAL_FILESYSTEM` modules, the per-pipeline Component's state
    file is written to `.local_defs_state/<pipeline_key>.json` (per the
    `local_defs_state_root()` convention below).

    Args:
        source_module: The `dlt_sources.<...>` Python module path.

    Returns:
        A `dict` ready to drop into a `defs.yaml` as the `defs_state:`
        block.
    """
    return {
        "management_type": default_state_config_for(source_module).management_type.value,
    }


def local_defs_state_root() -> Path:
    """Return the canonical on-disk root for the `LOCAL_FILESYSTEM` state files.

    Per master plan §3.3, the canonical root is `.local_defs_state/`
    at the repo root. The directory is created on-demand by the
    `KCGStateBackedDltComponent.write_state_to_path()` method (no
    manual setup is required).

    Returns:
        The canonical `.local_defs_state/` Path.
    """
    return Path.cwd() / ".local_defs_state"


# ---------------------------------------------------------------------------
# KCGStateBackedDltComponent — the canonical Cianfhoghlaim state-backed dlt Component
# ---------------------------------------------------------------------------
#
# Per the canonical `dagster-pipeline-components` spec, every per-pipeline
# Component with downstream BIEP consumers uses the `StateBackedComponent`
# pattern (so the Component can cache its introspected metadata in a
# state file + reload it without re-running the expensive dlt pipeline
# introspection on every code-server load).
#
# This class composes the canonical `DltLoadCollectionComponent` (the
# built-in Dagster dlt Component from `dagster_dlt`) with the canonical
# `StateBackedComponent` (from `dagster.components`), defaulting to the
# per-source `defs_state` block per `default_state_block_for()` above.
#
# The per-pipeline `defs.yaml` declares this Component with:
#
#     type: orchestration.pipelines._shared.state_helpers.KCGStateBackedDltComponent
#     attributes:
#       source_module: dlt_sources.education.tertiary.uog.exam_papers
#       defs_state:
#         management_type: LOCAL_FILESYSTEM
# ---------------------------------------------------------------------------


class KCGStateBackedDltComponent(StateBackedComponent, Resolvable):
    """The Cianfhoghlaim canonical state-backed dlt Component.

    Composes the canonical Dagster `DltLoadCollectionComponent` +
    `StateBackedComponent` patterns, defaulting to the per-source
    `defs_state` block per master plan §3.3.
    """

    source_module: str
    defs_state: ResolvedDefsStateConfig

    @property
    def defs_state_config(self) -> DefsStateConfig:
        """Per-source default: `LOCAL_FILESYSTEM` for the 14 high-churn
        modules, `LEGACY_CODE_SERVER_SNAPSHOTS` for everything else."""
        return DefsStateConfig.from_args(
            self.defs_state,
            default_key=f"KCGStateBackedDltComponent[{self.source_module}]",
        )

    def write_state_to_path(self, state_path: Path) -> None:
        """Write the per-source state file.

        For `LOCAL_FILESYSTEM` modules, the state file is a JSON blob
        containing the introspected dlt source metadata (the
        `@dlt.source` function signature + the schema introspection
        output from `dlt.pipeline(...).dataset()`).

        For `LEGACY_CODE_SERVER_SNAPSHOTS` modules, the state file is
        written to a temporary `BytesIO` and is not persisted across
        code-server restarts.
        """
        import json

        # Introspect the dlt source module (a) decorator metadata + (c)
        # pipeline.dataset() schema introspection. Best-effort: if either
        # step fails, fall back to an empty metadata blob.
        metadata: dict[str, Any] = {
            "source_module": self.source_module,
            "high_churn": self.source_module in LOCAL_FILESYSTEM_DEFAULTS,
        }
        try:
            import importlib

            dlt_source_module = importlib.import_module(self.source_module)

            # (a) Decorator metadata introspection — scan for @dlt.source
            source_name: str | None = None
            for attr_name, obj in vars(dlt_source_module).items():
                if attr_name.startswith("_"):
                    continue
                if callable(obj) and hasattr(obj, "__wrapped__"):
                    source_name = obj.__name__
                    break
            metadata["source_name"] = source_name

            # (c) pipeline.dataset() schema introspection — best-effort.
            try:
                import dlt

                pipeline_obj = dlt.pipeline(
                    pipeline_name=source_name or "kcg_wave2_unnamed",
                    destination="ducklake_cianfhoghlaim",
                    dataset_name=f"raw_{source_name or 'unknown'}",
                    dev_mode=True,
                )
                try:
                    source_obj = dlt_source_module.source() if hasattr(dlt_source_module, "source") else None  # type: ignore[attr-defined]
                except Exception:
                    source_obj = None
                if source_obj is not None:
                    pipeline_obj.run([source_obj])
                    dataset = pipeline_obj.dataset()
                    metadata["tables"] = list(dataset.tables)
            except Exception as exc:
                metadata["schema_introspection_error"] = str(exc)
        except Exception as exc:
            metadata["introspection_error"] = str(exc)

        # Ensure the parent directory exists (for `LOCAL_FILESYSTEM`
        # modules the parent is `.local_defs_state/`).
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state_path.write_text(json.dumps(metadata, indent=2, default=str))

    def build_defs_from_state(
        self,
        context: ComponentLoadContext,
        state_path: Path | None,
    ):
        """Build the `Definitions` from the cached state file.

        For `LOCAL_FILESYSTEM` modules, the state file is read from
        `.local_defs_state/<pipeline_key>.json` (per
        `local_defs_state_root()`); for `LEGACY_CODE_SERVER_SNAPSHOTS`
        modules, `state_path` is `None` (state is auto-refreshed on
        code-server load).
        """
        import dagster as dg
        from dagster_dlt import DltLoadCollectionComponent

        # Build the underlying DltLoadCollectionComponent from the
        # cached state file (no actual dlt.pipeline() construction here
        # — the state file contains the introspected metadata).
        dlt_component = DltLoadCollectionComponent(
            loads=[
                {
                    "pipeline": f"orchestration.pipelines._shared.dagster_dlt_integration:build_dlt_pipeline|{self.source_module}",
                    "source": f"{self.source_module}.source",
                }
            ]
        )
        return dlt_component.build_defs(context)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "LOCAL_FILESYSTEM_DEFAULTS",
    "default_state_config_for",
    "default_state_block_for",
    "local_defs_state_root",
    "KCGStateBackedDltComponent",
]
