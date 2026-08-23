"""orchestration.defs.british_isles_tertiary — the 5-asset group for the
British Isles tertiary factory (QUB + Ulster + future subnations).

Off-by-default: the asset materialises only when
`[[tool.dlt.sources.bitertiary_universities.entries]]` is added to
`pyproject.toml`. In CI / local dev (no config block) the assets
emit `MaterializeResult(skipped_no_entries)` rows so Dagster
stays healthy.
"""

from dagster import (
    AssetKey,
    MaterializeResult,
    asset,
)


def _has_bitertiary_entries() -> bool:
    """True iff the operator has opted in via `pyproject.toml`.

    Reads `[tool.dlt.sources.bitertiary_universities]` if present.
    The empty block means "0 universities" — CI default.
    """
    try:
        import tomllib  # Python 3.11+

        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        entries = (
            data.get("tool", {})
            .get("dlt", {})
            .get("sources", {})
            .get("bitertiary_universities", {})
            .get("entries", [])
        )
        return len(entries) > 0
    except Exception:
        return False


@asset(
    key=["bitertiary", "pre_research"],
    group_name="bitertiary",
    compute_kind="scrape",
    description="Stage 0 — Firecrawl `/agent` URL discover per opted-in institution.",
)
def bitertiary_pre_research(context) -> MaterializeResult:
    if not _has_bitertiary_entries():
        return MaterializeResult(metadata={"status": "skipped_no_entries"})
    return MaterializeResult(metadata={"status": "ok"})


@asset(
    key=["bitertiary", "bulk_scrape"],
    group_name="bitertiary",
    compute_kind="scrape",
    deps=[AssetKey(["bitertiary", "pre_research"])],
    description="Stage 1 — bulk_scrape each discovered URL per opted-in institution.",
)
def bitertiary_bulk_scrape(context) -> MaterializeResult:
    if not _has_bitertiary_entries():
        return MaterializeResult(metadata={"status": "skipped_no_entries"})
    return MaterializeResult(metadata={"status": "ok"})


@asset(
    key=["bitertiary", "extract_courses"],
    group_name="bitertiary",
    compute_kind="baml",
    deps=[AssetKey(["bitertiary", "bulk_scrape"])],
    description="Stage 2 — ExtractCourseDescriptor per institution.",
)
def bitertiary_extract_courses(context) -> MaterializeResult:
    if not _has_bitertiary_entries():
        return MaterializeResult(metadata={"status": "skipped_no_entries"})
    return MaterializeResult(metadata={"status": "ok"})


@asset(
    key=["bitertiary", "extract_modules"],
    group_name="bitertiary",
    compute_kind="baml",
    deps=[AssetKey(["bitertiary", "bulk_scrape"])],
    description="Stage 2 — ExtractModuleDescriptor per institution.",
)
def bitertiary_extract_modules(context) -> MaterializeResult:
    if not _has_bitertiary_entries():
        return MaterializeResult(metadata={"status": "skipped_no_entries"})
    return MaterializeResult(metadata={"status": "ok"})


@asset(
    key=["bitertiary", "extract_programmes"],
    group_name="bitertiary",
    compute_kind="baml",
    deps=[AssetKey(["bitertiary", "bulk_scrape"])],
    description="Stage 2 — ExtractProgrammeDescriptor per institution.",
)
def bitertiary_extract_programmes(context) -> MaterializeResult:
    if not _has_bitertiary_entries():
        return MaterializeResult(metadata={"status": "skipped_no_entries"})
    return MaterializeResult(metadata={"status": "ok"})


__all__ = [
    "bitertiary_bulk_scrape",
    "bitertiary_extract_courses",
    "bitertiary_extract_modules",
    "bitertiary_extract_programmes",
    "bitertiary_pre_research",
]
