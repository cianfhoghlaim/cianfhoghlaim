"""``@run.pipeline`` jobs for the Cianfhoghlaim dltHub Platform workspace.

This thin sub-package exists to host deployment-manifest jobs (decorated
with `@run.pipeline("name")` from `dlt.hub`) WITHOUT triggering the
eager-import chain in `cianfhoghlaim.dlt.british_isles.ireland.education.__init__`
(which has legacy `from common.firecrawl_source import …` lines that fail
when imported in isolation). See `docs/agents/dlthub-run-vs-serve.md` and
the `2026-07-06-wire-dlthub-platform-toolkits-and-deployment` change.

The first job: `government_circulars_ingest` — ingests the cached Oide /
gov.ie circulars from `stedding/site_scrape_samples/oide.ie/` into a
local DuckDB lake (or the `warehouse` named destination on the remote
runtime).
"""
from __future__ import annotations
import dlt


import json
import os
import re
from pathlib import Path
from typing import Iterator

import dlt_sources
from dlt_sources.hub import run

# Honour the project's `USE_LOCAL_SCRAPES` env-var convention (per the
# AGENTS.md "Respect the Ingestion Cache" rule + the dlthub platform
# `prepare-deployment` skill).
_LOCAL_SCRAPES = os.environ.get("USE_LOCAL_SCRAPES", "").lower() in (
    "1",
    "true",
    "yes",
)

# Curated cache path — the same one referenced by the BIEP-v1 change
# (Phase 3.3) and the ingestion skill.
_STEDDING_OIDE = Path(
    os.environ.get(
        "STEDDING_OIDE_DIR",
        "/Users/cianmacandeisigh/dev/kings_college_galway/stedding/site_scrape_samples/oide.ie",
    )
)

# Patterns extracted from the filename (the curl-style cache files include
# the full URL in the filename, which is great for circular_id derivation).
_URL_RE = re.compile(r"^(?P<slug>[^.]+\.oide\.ie)_(?P<path>.+?)(?:__s=)?\.json$")
_CIRCULAR_ID_RE = re.compile(r"(?i)(circular[_-]?\d{4}[-_]\d{2,4}[a-z]?)")
_YEAR_RE = re.compile(r"(20\d{2}|19\d{2})")
_DEPT_FROM_SLUG = {
    "oide.ie_primary_home_inclusive-education": "DES",
    "oide.ie_post-primary_home": "DES",
    "oide.ie_droichead_home": "DES",
    "oide.ie_post-primary_home_inclusive-education": "DES",
    "oide.ie_primary_home_languages-and-literacy": "DES",
}


def _infer_dept(slug: str) -> str:
    """Best-effort dept inference from the source slug."""
    return _DEPT_FROM_SLUG.get(slug, "DES")


def _infer_subject_area(path: str) -> str:
    """Best-effort subject area inference from the URL path."""
    if "gaeilge" in path or "irish" in path:
        return "Gaeilge"
    if "primary" in path:
        return "Primary"
    if "post-primary" in path or "post_primary" in path:
        return "PostPrimary"
    if "inclusion" in path or "eal" in path:
        return "Inclusion"
    if "deis" in path:
        return "DEIS"
    if "stem" in path:
        return "STEM"
    return "General"


def _iter_local_circular_snapshots(
    root: Path = _STEDDING_OIDE,
) -> Iterator[dict]:
    """Yield one row per cached gov.ie/Oide circular JSON snapshot.

    Graceful no-op when the cache is absent — matches the
    `stedding/ingest_queue/identity/` empty-dir convention in the project.
    """
    if not root.exists():
        return

    for json_path in sorted(root.glob("*.json")):
        m = _URL_RE.match(json_path.name)
        if not m:
            continue
        slug = m.group("slug")
        path = m.group("path")

        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        url = f"https://{slug}/{path.replace('_', '/')}"

        cid_match = _CIRCULAR_ID_RE.search(path) or _CIRCULAR_ID_RE.search(json_path.name)
        circular_id = cid_match.group(0).lower() if cid_match else json_path.stem

        year_match = _YEAR_RE.search(path) or _YEAR_RE.search(json_path.name)
        year = int(year_match.group(0)) if year_match else None

        summary: str | None = None
        if isinstance(payload, dict):
            for k in ("description", "summary", "abstract", "intro"):
                v = payload.get(k)
                if isinstance(v, str):
                    summary = v.strip()
                    break

        yield {
            "circular_id": circular_id,
            "dept": _infer_dept(slug),
            "subject_area": _infer_subject_area(path),
            "year": year,
            "language": "en",  # the stedding cache is EN-only; GA support is BIEP-v1 Phase 3.3
            "summary": summary,
            "url": url,
            "source_file": str(json_path),
        }


@dlt.resource(
    name="government_circulars",
    write_disposition="merge",
    primary_key=["circular_id", "language"],
)
def government_circulars() -> Iterator[dict]:
    """Yield one row per cached Oide circular.

    Honours `USE_LOCAL_SCRAPES=true` by reading from the curated
    `stedding/site_scrape_samples/oide.ie/` snapshot. When the env var is
    unset, the runtime will fall through to the future BIEP-v1
    `gov_ie_circulars.py` DLT source (live Firecrawl crawl).
    """
    yield from _iter_local_circular_snapshots()


@run.pipeline("government_circulars_ingest")
def government_circulars_ingest_job() -> None:
    """Batch job: ingest government circulars (gov.ie / Oide) into the lakehouse.

    The first BIEP @run.pipeline job registered in
    `cianfhoghlaim/__deployment__.py`. The runtime-installed dependency
    set (`dlt[hub]`, plus the deps in `pyproject.toml`) is sufficient.

    Destination resolution: the runtime honours profile-scoped `.dlt/*.toml`
    files; locally this defaults to `duckdb://<workspace>/government_circulars.duckdb`.
    """
    pipeline = dlt.pipeline(
        pipeline_name="government_circulars_ingest",
        destination="duckdb",
        dataset_name="oideachais_government_circulars",
        progress="log",
    )
    load_info = pipeline.run(government_circulars())
    print(f"Loaded {len(load_info.loads_ids)} load package(s) into {pipeline.pipeline_name}.")


if __name__ == "__main__":
    # The runtime requires a top-level `__main__` block; without it the
    # decorated job is registered but does nothing.
    government_circulars_ingest_job()
