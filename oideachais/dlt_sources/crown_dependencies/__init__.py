"""
DLT sources for Crown Dependencies education data.

DEPRECATED LOCATION (2026-06-24): This directory is a backward-compat
re-export shim. The canonical home for Crown Dependencies education
sources is `oideachais/dlt_sources/domains/education/{iom,jey,ggy}/`.
New code MUST import from the canonical location; this shim will
be removed in a follow-up openspec change.

NOTE: The canonical `domains/education/{jey,ggy}/` packages
currently have a circular import with this legacy package (they
re-export from each other). The shim below therefore re-exports
from the legacy path directly. When the canonical packages are
migrated to use the new file-move-based layout (Phase 2 of this
change), the circular import will be resolved and this shim can
be updated to re-export from the canonical path.

See `openspec/changes/lateralise-dlt-sources-to-domains/`.
"""

# Re-export from the legacy path to avoid the circular import
# (the canonical ggy/jey __init__.py currently imports from this
# legacy path).
from oideachais.dlt_sources.crown_dependencies.channel_islands import (
    guernsey_source,
    jersey_source,
)
from oideachais.dlt_sources.crown_dependencies.isle_of_man import (
    isle_of_man_source,
)

__all__ = [
    "isle_of_man_source",
    "jersey_source",
    "guernsey_source",
]
