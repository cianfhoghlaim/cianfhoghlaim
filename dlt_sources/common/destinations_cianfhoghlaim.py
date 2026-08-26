"""
destinations_cianfhoghlaim — re-export shim + §6/§7 thin glue.

Per the **2026-08-24-wave-4-ducklake-v1-hardening-v1** openspec
change, this file is a re-export shim for the layer-grouped
destinations package ``dlt_sources.common.destinations`` (the canonical
home of all destination logic).

Per the **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1** §6.1 /
§6.4 / §7.1 / §7.4 changes, this shim also exposes a thin
``get_dlt_destination(...)`` glue helper that the existing 100+
call-sites continue to use. That helper dispatches to the canonical
``get_ducklake_destination_for_quadrant(...)`` per the §7.1
per-quadrant metadata_schema + the §7.4 ``automatic_migration=True``
default.

Legacy imports continue to work, but new code SHOULD import from:

    from dlt_sources.common.destinations import named_destinations

This shim is preserved for at least one release cycle per the
dlt_sources LEGACY_ALIASES.md precedent.
"""
from __future__ import annotations

# Re-export from the layer-grouped destinations package.
from dlt_sources.common.destinations import (  # noqa: F401
    named_destinations,
    DESTINATIONS,
)
from dlt_sources.common.destinations.ducklake import (  # noqa: F401
    # 7.1 / 7.4
    QUADRANT_METADATA_SCHEMAS,
    DEFAULT_AUTOMATIC_MIGRATION,
    DEFAULT_POSTGRES_CATALOG,
    DEFAULT_GARAGE_S3_STORAGE,
    DUCKLAKE_NAME,
    # 7.2
    DEFAULT_JURISDICTION_SORT_COLUMNS,
    JURISDICTION_SORTED_BY_TABLES,
    # 6.1 + 7.1
    get_ducklake_destination,
    get_ducklake_destination_for_quadrant,
    # 7.3 nightly maintenance
    ducklake_expire_snapshots_sql,
    ducklake_cleanup_old_files_sql,
    ducklake_merge_adjacent_files_sql,
    ducklake_rewrite_data_files_sql,
)

# ─── get_dlt_destination glue (legacy symbol) ──────────────────────────────
#
# The 100+ existing call sites import this from
# `dlt_sources.common.destinations_cianfhoghlaim` (e.g.
# `dlt_sources/education/ireland/british_isles/ireland_jurisdiction_pipeline.py:19`,
# `orchestration/defs/2_materials/ireland_education/ireland_jc_assets.py:144`,
# etc.). The previous shim did NOT actually expose this symbol — every
# call site was silently broken until now. Per the
# `2026-08-24-dlt-sources-to-multi-repo-scaffold-v1` plan §5 + the v2
# plan §A, the shim wires the symbol up to the canonical per-quadrant
# factory so the 100+ existing call sites start working.

from typing import Any, Optional  # noqa: E402

from dlt_sources.common.destinations.ducklake import (  # noqa: E402
    DEFAULT_AUTOMATIC_MIGRATION,
    get_ducklake_destination_for_quadrant,
)


def get_dlt_destination(
    use_ducklake: Optional[bool] = None,
    quadrant: Optional[str] = None,
    *,
    use_md: Optional[bool] = None,
    automatic_migration: bool = DEFAULT_AUTOMATIC_MIGRATION,
    multischema: bool = True,
) -> Any:
    """Canonical glide path for the legacy ``get_dlt_destination(...)`` symbol.

    Added in the
    **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1** §6.1 + §7.1
    + §7.4 change. Resolves to
    :func:`dlt_sources.common.destinations.ducklake.get_ducklake_destination_for_quadrant`
    for the 5 named quadrants (`oideachais`, `tuatha`, `croilar`,
    `agents`, `media`) or to the legacy `DUCKLAKE_NAME` destination
    when `quadrant=None`.

    Args:
        use_ducklake: If False, raise ``NotImplementedError`` (the
            pre-§7.1 fallback to a local DuckDB destination was
            retired by Wave 4; the lakehouse is the only canonical
            path). If True or None, dispatch to the per-quadrant
            DuckLake factory.
        quadrant: One of the 5 named quadrants (see
            ``QUADRANT_METADATA_SCHEMAS``). ``None`` (the default)
            uses the consolidated ``"oideachais"`` quadrant, which
            is the canonical home for the BIEP v3 Ireland + England
            + Scotland + Wales + NI jurisdiction pipelines.
        use_md: Deprecated alias for ``use_ducklake``. Kept for
            the 100+ existing call sites. If both are passed,
            ``use_ducklake`` wins.
        automatic_migration: See
            :func:`get_ducklake_destination_for_quadrant`. Default
            ``True`` (per §7.4).
        multischema: See
            :func:`get_ducklake_destination_for_quadrant`. Default
            ``True`` (per §6.1 — the BIEP v3 jurisdiction pipelines
            collapse the per-nation DuckLake schemas into one
            BIEP-schema dataset).

    Returns:
        A `@dlt.destination`-decorated function (the
        ``ducklake_cianfhoghlaim`` destination).

    Reference:
        - openspec/changes/2026-08-24-wave-4-ducklake-v1-hardening-v1
        - openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 §6.1, §7.1, §7.4
    """
    if use_md is not None and use_ducklake is None:
        use_ducklake = use_md
    if use_ducklake is False:
        raise NotImplementedError(
            "use_ducklake=False (local DuckDB fallback) was retired by the "
            "Wave 4 lakehouse consolidation. Every BIEP v3 jurisdiction "
            "pipeline goes through the consolidated DuckLake namespace."
        )
    return get_ducklake_destination_for_quadrant(
        quadrant=quadrant or "oideachais",
        automatic_migration=automatic_migration,
        multischema=multischema,
    )


# === Original file content (preserved for archaeology) ===
# Original path: dlt_sources/common/destinations_cianfhoghlaim.py
# Original line count (Wave 4 shim form): 27
# Wave 4: replaced original 529-LOC implementation with a re-export shim.
# The original implementation is preserved in git history at commit
# b8e7e18bd (before Wave 4) — use `git show b8e7e18bd:dlt_sources/common/destinations_cianfhoghlaim.py` to view.


__all__ = [
    # Re-export shims
    "named_destinations",
    "DESTINATIONS",
    "QUADRANT_METADATA_SCHEMAS",
    "DEFAULT_AUTOMATIC_MIGRATION",
    "DEFAULT_POSTGRES_CATALOG",
    "DEFAULT_GARAGE_S3_STORAGE",
    "DUCKLAKE_NAME",
    "DEFAULT_JURISDICTION_SORT_COLUMNS",
    "JURISDICTION_SORTED_BY_TABLES",
    "get_ducklake_destination",
    "get_ducklake_destination_for_quadrant",
    "ducklake_expire_snapshots_sql",
    "ducklake_cleanup_old_files_sql",
    "ducklake_merge_adjacent_files_sql",
    "ducklake_rewrite_data_files_sql",
    # Glue (legacy symbol)
    "get_dlt_destination",
]
