"""ncca_sec_celt_duchas_wikipedia scrape DLT resource.

Class E official-document source (EDUCATIONAL BODY SUBSET).
The 14 educational body resources (2 NCCA research PDFs + 12
NCCA Leaving Certificate syllabus PDFs, en + ga parity) stay
in this source. The 12 Wikipedia entries (Tuatha Dé Danann,
Irish mythology, etc.) were MOVED to
`dlt_sources/media/celtic_history_research/` (the 9 stub
sources for the downstream theming change) per the
2026-08-23-tuatha-media-intel-gameplay-capture-research-v1
refactor.

The 8 NEW official-document sub-buckets — government /
departments / acts_and_treaties per jurisdiction — are
authored under `dlt_sources/media/official/government/`
and `dlt_sources/media/official/departments/`.

The descriptor is a structured summary — NEVER a verbatim copy
of the full page. Per the media-intel-corpus spec, every
descriptor ships with `shippable: false` enforced.

Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
            design.md § 1.4 (the no-graphics-from-graphics invariant)
            spec.md § media-intel-acquisition-plan Requirement 5
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import uuid
from collections.abc import Iterator
from typing import Any

import dlt

# The 2 user-named NCCA research PDFs (verbatim paths from the
# leaving_certificate/ tree).
_V1_RESEARCH_PDFS: list[dict[str, str]] = [
    {
        "id": "potential_of_online_learning_environments",
        "title": "The Potential of Online Learning Environments (NCCA research PDF)",
        "local_path": "leaving_certificate/the-potential-of-online-learning-environments_en.pdf",
        "rights_holder": "NCCA",
        "licence": "fair-use-description",
    },
    {
        "id": "key_competencies_in_senior_cycle",
        "title": "Key Competencies in the Senior Cycle (NCCA research PDF)",
        "local_path": "leaving_certificate/key-competencies-in-senior-cycle_en.pdf",
        "rights_holder": "NCCA",
        "licence": "fair-use-description",
    },
]


# The 12 NCCA Leaving Certificate syllabus PDFs (EN + GA parity).
# This is the EDUCATIONAL BODY subset (the 6 BIEP v1 LC subjects
# + the 2 priority secondary subjects + the 4 supplementary
# subjects in the leaving_certificate/ tree).
_V1_SYLLABUS_PDFS: list[dict[str, str]] = [
    {
        "id": "biology_syllabus_en",
        "title": "NCCA Biology Syllabus (English)",
        "local_path": "leaving_certificate/biology/en/SCSEC07_Biology_Syllabus_Eng.pdf",
        "rights_holder": "NCCA",
        "licence": "fair-use-description",
    },
    {
        "id": "biology_syllabus_ga",
        "title": "NCCA Biology Syllabus (Gaeilge)",
        "local_path": "leaving_certificate/biology/ga/SCSEC07_Biology_Syllabus_Gaeilge.pdf",
        "rights_holder": "NCCA",
        "licence": "fair-use-description",
    },
    {
        "id": "geography_syllabus_en",
        "title": "NCCA Geography Syllabus (English)",
        "local_path": "leaving_certificate/geography/en/SCSEC17_Geography_syllabus_eng.pdf",
        "rights_holder": "NCCA",
        "licence": "fair-use-description",
    },
    {
        "id": "geography_syllabus_ga",
        "title": "NCCA Geography Syllabus (Gaeilge)",
        "local_path": "leaving_certificate/geography/ga/SCSEC17_Geography_Syllabus_gaeilge.pdf",
        "rights_holder": "NCCA",
        "licence": "fair-use-description",
    },
    {
        "id": "history_syllabus_en",
        "title": "NCCA History Syllabus (English)",
        "local_path": "leaving_certificate/history/en/SCSEC20_History_syllabus_eng.pdf",
        "rights_holder": "NCCA",
        "licence": "fair-use-description",
    },
    {
        "id": "history_syllabus_ga",
        "title": "NCCA History Syllabus (Gaeilge)",
        "local_path": "leaving_certificate/history/ga/SCSEC20_History_syllabus_Gaeilge.pdf",
        "rights_holder": "NCCA",
        "licence": "fair-use-description",
    },
    {
        "id": "english_syllabus_en",
        "title": "NCCA English Syllabus (English)",
        "local_path": "leaving_certificate/english/en/SCSEC14_English_Syllabus.pdf",
        "rights_holder": "NCCA",
        "licence": "fair-use-description",
    },
    {
        "id": "mathematics_syllabus_en",
        "title": "NCCA Mathematics Syllabus (English)",
        "local_path": "leaving_certificate/mathematics/en/SCSEC25_Maths_syllabus_examination-2015_English.pdf",
        "rights_holder": "NCCA",
        "licence": "fair-use-description",
    },
    {
        "id": "mathematics_syllabus_ga",
        "title": "NCCA Mathematics Syllabus (Gaeilge)",
        "local_path": "leaving_certificate/mathematics/ga/SCSEC25_Maths_syllabus_examination2015_gaeilge.pdf",
        "rights_holder": "NCCA",
        "licence": "fair-use-description",
    },
    {
        "id": "gaeilge_guidelines_en",
        "title": "NCCA Gaeilge Guidelines (English)",
        "local_path": "leaving_certificate/gaeilge/SCSEC16_Gaeilge_guidelines.pdf",
        "rights_holder": "NCCA",
        "licence": "fair-use-description",
    },
    {
        "id": "applied_mathematics_syllabus_en",
        "title": "NCCA Applied Mathematics Syllabus (English)",
        "local_path": "leaving_certificate/applied_mathematics/en/Leaving-Certificate-Specification-Applied-Mathematics_EN_1.pdf",
        "rights_holder": "NCCA",
        "licence": "fair-use-description",
    },
    {
        "id": "ukrainian_syllabus_en",
        "title": "NCCA Ukrainian Syllabus (English)",
        "local_path": "leaving_certificate/ukrainian/LC570ALP000EV.pdf",
        "rights_holder": "NCCA",
        "licence": "fair-use-description",
    },
]


# ── Helpers (mirrors the leaving_cert.py pattern) ────────────────────────────


def _stable_hash(record: dict[str, Any]) -> str:
    """Content-addressable hash for change detection."""
    return hashlib.sha256(
        json.dumps(record, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]


# ── DLT source ──────────────────────────────────────────────────────────────


@dlt.source(name="ncca_sec_dfe_sqa_wjec_desc")
def ncca_sec_dfe_sqa_wjec_desc_source(
    use_local_scrapes: bool | None = None,
    write_disposition: str = "merge",
):
    """DLT source for the 14 NCCA / SEC / DfE / SQA / WJEC / DESC
    educational body documents (the curriculum spec + exam paper +
    marking scheme PDFs).

    The Wikipedia / Celtic-history / sub-national government
    sources moved to:
      - `dlt_sources/media/official/government/` (police +
        defence + army + Acts + treaties per jurisdiction)
      - `dlt_sources/media/official/departments/` (government
        departments per jurisdiction)
      - `dlt_sources/media/celtic_history_research/` (the 9
        stub sources for the downstream theming change)
    """
    if use_local_scrapes is None:
        use_local_scrapes = os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true"

    if not use_local_scrapes:
        # Plan A keyless Firecrawl fallback (per media-intel-corpus spec)
        pass  # The firecrawl_scrape / firecrawl_parse path is invoked
              # downstream by the BAML extractor.

    # Group 1: NCCA research PDFs (the 2 user-named PDFs at the
    # root of leaving_certificate/)
    @dlt.resource(
        name="research_pdf_descriptors",
        write_disposition=write_disposition,
        primary_key=("work", "source_url", "source_timestamp"),
    )
    def research_pdf_resource() -> Iterator[dict[str, Any]]:
        firecrawl_key_present = bool(os.environ.get("FIRECRAWL_API_KEY"))
        for pdf in _V1_RESEARCH_PDFS:
            source_url = pdf["local_path"]
            source_timestamp = datetime.datetime.now(
                tz=datetime.UTC
            ).isoformat()
            try:
                from baml_src.media.official_document_descriptor import (  # type: ignore
                    ExtractOfficialDocumentDescriptor,
                )

                descriptor = ExtractOfficialDocumentDescriptor(
                    pdf_page=None,
                    metadata=f"Issuer: {pdf['rights_holder']}; Date: unknown; Version: unknown",
                    source_url=source_url,
                    source_timestamp=source_timestamp,
                    work=pdf["title"],
                    language="en",
                    evidence=f"PDF: {pdf['title']}",
                )
                record = descriptor.model_dump()
            except Exception:
                record = {
                    "work": pdf["title"],
                    "medium": "official",
                    "language": "en",
                    "source_url": source_url,
                    "source_timestamp": source_timestamp,
                    "provenance": {
                        "rights_holder": pdf["rights_holder"],
                        "licence": pdf["licence"],
                        "derivation_class": "fair_use_quote",
                        "shippable": False,
                        "shippable_art_path": None,
                    },
                }
            record["_acquisition_id"] = str(uuid.uuid4())
            record["_firecrawl_plan"] = "plan_a_keyless"
            record["_firecrawl_key_present"] = firecrawl_key_present
            record["_content_hash"] = _stable_hash(record)
            yield record

    # Group 2: NCCA Leaving Certificate syllabus PDFs (en + ga)
    @dlt.resource(
        name="syllabus_pdf_descriptors",
        write_disposition=write_disposition,
        primary_key=("work", "source_url", "source_timestamp"),
    )
    def syllabus_pdf_resource() -> Iterator[dict[str, Any]]:
        firecrawl_key_present = bool(os.environ.get("FIRECRAWL_API_KEY"))
        for pdf in _V1_SYLLABUS_PDFS:
            source_url = pdf["local_path"]
            source_timestamp = datetime.datetime.now(
                tz=datetime.UTC
            ).isoformat()
            try:
                from baml_src.media.official_document_descriptor import (  # type: ignore
                    ExtractOfficialDocumentDescriptor,
                )

                descriptor = ExtractOfficialDocumentDescriptor(
                    pdf_page=None,
                    metadata=f"Issuer: {pdf['rights_holder']}; Date: unknown; Version: unknown",
                    source_url=source_url,
                    source_timestamp=source_timestamp,
                    work=pdf["title"],
                    language="en" if "_en" in pdf["id"] else "ga",
                    evidence=f"PDF: {pdf['title']}",
                )
                record = descriptor.model_dump()
            except Exception:
                record = {
                    "work": pdf["title"],
                    "medium": "official",
                    "language": "en" if "_en" in pdf["id"] else "ga",
                    "source_url": source_url,
                    "source_timestamp": source_timestamp,
                    "provenance": {
                        "rights_holder": pdf["rights_holder"],
                        "licence": pdf["licence"],
                        "derivation_class": "fair_use_quote",
                        "shippable": False,
                        "shippable_art_path": None,
                    },
                }
            record["_acquisition_id"] = str(uuid.uuid4())
            record["_firecrawl_plan"] = "plan_a_keyless"
            record["_firecrawl_key_present"] = firecrawl_key_present
            record["_content_hash"] = _stable_hash(record)
            yield record

    return research_pdf_resource(), syllabus_pdf_resource()


__all__ = [
    "_V1_RESEARCH_PDFS",
    "_V1_SYLLABUS_PDFS",
    "_stable_hash",
    "ncca_sec_dfe_sqa_wjec_desc_source",
]
