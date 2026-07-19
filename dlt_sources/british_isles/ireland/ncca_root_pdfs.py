"""DLT source for the 5 NCCA root-level programme PDFs.

Reads the 5 root-level PDFs from `cianfhoghlaim/leaving_certificate/*.pdf`
and emits a `ncca_root_pdfs` DLT resource. The BAML extraction is wired
in `dagster/defs/2_materials/root_pdf_assets.py`.

Per `openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
ncca-leaving-cert-root-pdfs/spec.md` Requirement R1.
"""

from __future__ import annotations
import dlt


import hashlib
import pathlib
from typing import Iterator

import dlt_sources


_ROOT_PDFS = (
    "key-competencies-in-senior-cycle_en.pdf",
    "the-potential-of-online-learning-environments_en.pdf",
    "the-potential-of-technology-to-support-online-certification-and-reporting.pdf",
    "scr-advisory-report_en.pdf",
    "SC-L1-L2-Programme-Statement.pdf",
)


@dlt.resource(write_disposition="replace", name="ncca_root_pdfs")
def ncca_root_pdfs(
    leaving_certificate_dir: str = "cianfhoghlaim/leaving_certificate",
) -> Iterator[dict]:
    """Yield one row per NCCA root-level programme PDF.

    Each row carries:
      - pdf_path (str): absolute path to the PDF
      - pdf_name (str): filename only
      - sha256 (str): SHA-256 hash of the file contents (for SHA-256 dedup)
      - byte_size (int): file size in bytes
      - page_count (int): number of pages (estimated from /Type /Page count)
      - ingested_at (str): ISO 8601 timestamp of ingestion
    """
    from datetime import datetime, timezone

    base = pathlib.Path(leaving_certificate_dir)
    for pdf_name in _ROOT_PDFS:
        pdf_path = base / pdf_name
        if not pdf_path.exists():
            continue
        contents = pdf_path.read_bytes()
        sha256 = hashlib.sha256(contents).hexdigest()
        # Estimate page count from the PDF /Type /Page /Count tag
        page_count = _estimate_page_count(contents)
        yield {
            "pdf_path": str(pdf_path.resolve()),
            "pdf_name": pdf_name,
            "sha256": sha256,
            "byte_size": len(contents),
            "page_count": page_count,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }


def _estimate_page_count(pdf_bytes: bytes) -> int:
    """Estimate the page count of a PDF from its /Type /Page /Count tag.

    This is a cheap heuristic; the actual page count requires parsing the
    PDF. The estimate is good enough for DLT metadata; the CocoIndex v1
    App reads the actual pages.
    """
    # Look for `/Count <integer>` near the start of the file
    head = pdf_bytes[:8192]
    marker = b"/Count"
    idx = head.find(marker)
    if idx == -1:
        return 0
    # Read the integer that follows
    after = head[idx + len(marker): idx + len(marker) + 16]
    digits = b""
    for b in after:
        if b in b"0123456789":
            digits += bytes([b])
        elif digits:
            break
    return int(digits) if digits else 0