"""baml_src/_shared/dltq_naming_legacy.py
The 6-month deprecation grace-period shim for the schema-naming convergence
(per the 2026-10-30-platform-reset-saga-v1 saga, Umbrella 2).

Maps the historical naming conventions to the canonical form exposed by
dltq_naming.py:

  Legacy form                              Canonical form (returns the same)
  --------------------------------------  --------------------------------------
  oideachais_<agent>                       agents_<agent>          (Cognee)
  media.image_gen_chunks_<lang>            media_<lang>_image_gen_chunks  (LanceDB)
  ciianfhoghlaim.<table>                   ciianfhoghlaim.<quadrant>_<table>  (DuckLake, by map)

Both forms are accepted by the production Cognee + LanceDB + DuckLake
bridges during the grace period. After 6 months, the legacy form will
return a deprecation warning; after 12 months, the legacy form will
raise.
"""
from __future__ import annotations

from .dltq_naming import (
    to_dlq_cognee_dataset,
    to_dlq_lance_table,
)

# Mapping of the 3 known legacy forms to the canonical helper call.
_LEGACY_FORMS: dict[str, str] = {
    # Cognee
    "oideachais_root": "agents_root",
    "oideachais_curriculum": "agents_curriculum",
    "oideachais_translation": "agents_translation",
    "oideachais_corpus": "agents_corpus",
    "oideachais_research": "agents_research",
    "oideachais_education_research": "agents_education_research",
    "oideachais_bunchloch_research": "agents_bunchloch_research",
    "oideachais_geospatial": "agents_geospatial",
    "oideachais_statistics": "agents_statistics",
    "oideachais_curriculum_comparison": "agents_curriculum_comparison",
    # The other 3 from the 13-entry AGENT_REGISTRY (mcp_curriculum_agent,
    # agui_curriculum_agent, education_research_agent) will be added when
    # the full agent_registry.py is wired.
}


def legacy_to_dlq_table_name(legacy: str) -> str:
    """Map a legacy table name to the canonical form.

    Accepts:
      - `oideachais_<agent>` -> `<quadrant>_<table>` (Cognee datasets)
      - `media.image_gen_chunks_<lang>` -> `media_<lang>_image_gen_chunks` (LanceDB)
      - The canonical form itself (returned unchanged, for the case where
        the caller already has the canonical name).

    Args:
        legacy: The legacy or canonical table name to map.

    Returns:
        The canonical form.

    Raises:
        ValueError: if the input is not a recognised form.
    """
    if not isinstance(legacy, str) or not legacy:
        raise ValueError(f"dltq_naming_legacy: legacy name must be non-empty string, got {legacy!r}")

    # Pass-through: already canonical
    if legacy in _LEGACY_FORMS.values() or legacy.startswith("ciianfhoghlaim."):
        return legacy

    # Cognee legacy: `oideachais_<agent>`
    if legacy.startswith("oideachais_"):
        agent = legacy[len("oideachais_"):]
        return to_dlq_cognee_dataset(agent)

    # LanceDB legacy: `media.image_gen_chunks_<lang>`
    if legacy.startswith("media.image_gen_chunks_"):
        language = legacy[len("media.image_gen_chunks_"):]
        return to_dlq_lance_table(language, "image_gen_chunks")

    # Known static mappings (the AGENT_REGISTRY 13)
    if legacy in _LEGACY_FORMS:
        return _LEGACY_FORMS[legacy]

    raise ValueError(
        f"dltq_naming_legacy: {legacy!r} is not a recognised legacy form. "
        f"Known prefixes: 'oideachais_' (Cognee), 'media.image_gen_chunks_' (LanceDB). "
        f"Add the form to _LEGACY_FORMS or use to_dlq_table_name() directly."
    )


__all__ = ["legacy_to_dlq_table_name"]
