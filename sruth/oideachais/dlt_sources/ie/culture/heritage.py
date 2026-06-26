"""
oideachais.dlt_sources.ie.culture.heritage — Ireland
cultural-heritage DLT source.

Phase 1 of the `ingest-culture-heritage` openspec change.

Sources:

1. **6 filesystem PDFs** at `leabharlann/gemini_deep_research/culture/` —
   the personal-heritage Gemini Deep Research reports. Yielded as the
   `culture_pdfs` resource (one row per PDF page; primary_key
   `(pdf_sha256, page_number)`).
2. **3 Wikipedia fixtures** at
   `oideachais/dlt_sources/official_media/fixtures/identity_*.json` —
   the dual-written canonical URL + first-paragraph extract for each
   Wikipedia article. Yielded as the `wikipedia_fixtures` resource
   (one row per fixture; primary_key `url`).

Both resources are loaded lazily (the file system is not touched at
import time); the asset pipeline reads them via the standard DLT
`@dlt.resource` generator pattern.

The schema is enforced by the BAML `ExtractCultureClaims` function
defined in `oideachais/baml_src/culture_extraction.baml`.

Reference: openspec/changes/ingest-culture-heritage/proposal.md
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from pathlib import Path

import dlt

logger_module_name = __name__


CULTURE_PDFS_DIR = Path("leabharlann/gemini_deep_research/culture")
WIKIPEDIA_FIXTURES_DIR = Path(
    "oideachais/dlt_sources/official_media/fixtures"
)


def _sha256_file(path: Path, chunk_size: int = 65536) -> str:
    """Return the SHA-256 hex digest of the file at *path*."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


@dlt.source(name="ie_culture_heritage")
def ie_culture_heritage_source(
    pdfs_dir: Path = CULTURE_PDFS_DIR,
    fixtures_dir: Path = WIKIPEDIA_FIXTURES_DIR,
) -> list:
    """Ireland cultural-heritage DLT source.

    Yields two resources:

    - `culture_pdfs`         — one row per PDF file in *pdfs_dir*.
    - `wikipedia_fixtures`   — one row per identity_*.json file in
                              *fixtures_dir*.
    """

    @dlt.resource(
        name="culture_pdfs",
        write_disposition="merge",
        primary_key=["pdf_sha256", "page_number"],
    )
    def culture_pdfs() -> Iterator[dict]:
        """Walk *pdfs_dir* and yield one row per PDF.

        The row schema is intentionally minimal — the heavy lifting
        (BAML extraction, embedding, cognify) happens downstream in the
        Dagster asset graph.
        """
        if not pdfs_dir.exists():
            return
        for pdf_path in sorted(pdfs_dir.glob("*.pdf")):
            pdf_sha = _sha256_file(pdf_path)
            yield {
                "pdf_sha256": pdf_sha,
                "page_number": 0,  # placeholder — full per-page extraction
                "filename": pdf_path.name,
                "size_bytes": pdf_path.stat().st_size,
                "relpath": str(pdf_path),
            }

    @dlt.resource(
        name="wikipedia_fixtures",
        write_disposition="merge",
        primary_key=["url"],
    )
    def wikipedia_fixtures() -> Iterator[dict]:
        """Walk *fixtures_dir* and yield one row per identity_*.json."""
        if not fixtures_dir.exists():
            return
        for fixture_path in sorted(fixtures_dir.glob("identity_*.json")):
            with fixture_path.open(encoding="utf-8") as f:
                data = json.load(f)
            data["fixture_path"] = str(fixture_path)
            yield data

    return [culture_pdfs, wikipedia_fixtures]