"""baml_src/_shared/dltq_naming.py
The canonical schema-naming helper (per the 2026-10-30-platform-reset-saga-v1
saga, Umbrella 2 — BAML repair + schema-naming convergence).

Per the Stage 8 fresh-slate handoff Gap 1 (see
openspec/plans/2026-10-26-stage-8-fresh-slate-spec-handoff-v1.md),
3 conflicting naming conventions co-exist today:
  - cognee_dataset field: `oideachais_<agent>` (per agents/agent_registry.py:AGENT_REGISTRY, 13 entries)
  - LanceDB table names: `media.image_gen_chunks_<lang>` (per cocoindex_flows/media/{gaeilge,cymraeg,...}/asset_index.py, 6 entries)
  - DuckLake namespace: `ciianfhoghlaim` (per dlt_sources/destinations/_common.py:DUCKLAKE_NAMESPACE)

This helper introduces a single canonical pattern (`<quadrant>_<table>`)
with a 6-month deprecation grace period for the legacy aliases (see
baml_src/_shared/dltq_naming_legacy.py).

Canonical pattern: <quadrant>_<table>
  DuckLake:    ciianfhoghlaim.<quadrant>_<table>
  LanceDB:     cianhoghlaim.media_<lang>_<table>
  Cognee:      <quadrant>_<agent>

Usage (Python-side):
  from cianfhoghlaim.baml_src._shared.dltq_naming import (
      to_dlq_table_name,
      to_dlq_cognee_dataset,
      to_dlq_lance_table,
  )
  name = to_dlq_table_name("media", "image_gen_chunks", language="gaeilge")
  # => "ciianfhoghlaim.media_gaeilge_image_gen_chunks"
"""
from __future__ import annotations

import re

# Quadrants that are first-class in the platform. Each quadrant may have
# its own naming convention for child tables.
QUADRANTS: tuple[str, ...] = (
    "media",          # CocoIndex flows (the per-language image-gen + asset indexes)
    "agents",         # ADK agent cognee_datasets (replaces `oideachais_<agent>`)
    "lc",             # Leaving Certificate (mathematics, chemistry, geography, gaeilge, english, cs)
    "ie",             # Ireland (gov.ie circulars + NCCA policies)
    "bi",             # British Isles (en/wl/sct/ni/iom/jey/ggy)
    "meaisin",        # meaisinfhoghlaim services (bilingual concept registry, alignment, evaluation)
    "tuatha",         # the MMO (asset pool, palette registry, anam, retro captures)
    "croilar",        # croilar portal (croilar+ciandlithe converged surface)
    "ciandlithe",     # BIEP v3 jurisdiction surface
    "ciancheiltis",   # Celtic-language sister
    "cianchosaint",   # cross-jurisdiction sister
    "bonneagar",      # infrastructure stacks (compose + sidecar + secrets)
    "orchestration",  # Dagster assets + sensors
)


# Allowed character set for table names. Lowercase ASCII + underscore + dot.
# Segments are validated individually; a non-conforming name raises at
# helper-call time (LBYL — explicit check before letting the LLM throw).
_SEGMENT_RE = re.compile(r"^[a-z][a-z0-9_]{0,62}$")


def _validate_segment(value: str, name: str) -> None:
    """Raise ValueError if the segment is not a valid quadrant/table/lang token."""
    if not isinstance(value, str) or not _SEGMENT_RE.match(value):
        raise ValueError(
            f"dltq_naming: {name}={value!r} is not a valid segment "
            f"(must match {_SEGMENT_RE.pattern} - lowercase ASCII, "
            f"start with letter, <= 63 chars, [a-z0-9_] only)"
        )


def to_dlq_table_name(
    quadrant: str,
    table: str,
    language: str | None = None,
) -> str:
    """Return the canonical table name for a (quadrant, table[, language]) tuple.

    The 3 surfaces this helper routes:
      - DuckLake:    ciianfhoghlaim.<quadrant>_<table>[_<language>]
      - LanceDB:     cianhoghlaim.<quadrant>_<language>_<table>  (only when language is set)
      - Cognee:      <quadrant>_<table>                          (datasets are namespace-local)

    Args:
        quadrant: One of the QUADRANTS tokens (e.g. "media", "agents", "lc").
        table:    The table identifier within the quadrant (e.g. "image_gen_chunks", "root").
        language: Optional ISO 639-1 code (e.g. "ga", "en", "cy", "gd", "br", "kw", "gv")
                  - required for the per-language media quadrant.

    Returns:
        The canonical fully-qualified table name. For the DuckLake default
        the function returns the same form (DuckLake namespaces table names
        by `.`, so the legacy form is also accepted).

    Raises:
        ValueError: if any input segment fails validation.
    """
    _validate_segment(quadrant, "quadrant")
    _validate_segment(table, "table")
    if language is not None:
        _validate_segment(language, "language")
    if language is not None:
        return f"ciianfhoghlaim.{quadrant}_{language}_{table}"
    return f"ciianfhoghlaim.{quadrant}_{table}"


# Convenience wrappers for the 3 most common call sites (per the saga plan).
def to_dlq_cognee_dataset(agent: str) -> str:
    """Return the canonical cognee_dataset name for an agent.

    Replaces the legacy `oideachais_<agent>` form. During the 6-month
    deprecation grace period, both forms are accepted by the Cognee
    bridge (see dltq_naming_legacy.py).
    """
    return to_dlq_table_name("agents", agent)


def to_dlq_lance_table(language: str, table: str) -> str:
    """Return the canonical LanceDB table name for a per-language media table.

    Replaces the legacy `media.image_gen_chunks_<lang>` form. The
    canonical form uses underscores throughout (no dots) so the same
    helper works for both DuckLake and LanceDB.
    """
    return to_dlq_table_name("media", table, language=language)


# Backwards-compat: the 3 surface constants that pre-existed this helper.
# These are kept here so other code can import from one place; the
# `legacy_to_dlq_table_name` shim in dltq_naming_legacy.py maps the
# historical names to the canonical form.
DUCKLAKE_NAMESPACE: str = "ciianfhoghlaim"


__all__ = [
    "DUCKLAKE_NAMESPACE",
    "QUADRANTS",
    "to_dlq_cognee_dataset",
    "to_dlq_lance_table",
    "to_dlq_table_name",
]
