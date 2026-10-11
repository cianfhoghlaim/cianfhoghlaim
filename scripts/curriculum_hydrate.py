"""Operator CLI for hydrating the Cianfhoghlaim / Tuatha curriculum tables.

Per the 2026-10-10-media-intel-and-curriculum-hydration-v1 saga change
(Plan 2.5 of ``openspec/plans/2026-10-10-tuatha-curriculum-media-saga-v1.md``).
Hydrates four DuckLake tables from the Leaving Certificate corpus +
operator-provided hand-made examples:

    cianfhoghlaim.lc.geography.topics          (source: leaving_certificate/geography/** + stedding/geog.pdf)
    cianfhoghlaim.lc.gaeilge.poems_higher      (source: PastLC-IrishEnglish/page_00{1..3}.png)
    cianfhoghlaim.lc.english.poets_higher      (source: PastLC-IrishEnglish/page_00{1..3}.png)
    cianfhoghlaim.education.ie.policies        (source: 5 NCCA policy PDFs at leaving_certificate/ root)

DLT >= 1.29 conventions used throughout:
- one ``@dlt.resource(standalone=True, write_disposition="merge", primary_key=...)`` per table
- ``primary_key`` is the ``(source_pdf, source_page, source_url)`` provenance triple
- single ``@dlt.source`` builder so the filesystem scan is one pass
- lazy file IO (PDFs read inside the generator, not upfront)
- never uses ``dlt.sources.filesystem.read_csv/read_json`` (these are PDFs/PNGs)

In ``--dry-run`` mode (alias ``--no-dlt``) no DuckLake write happens; each
row is emitted as a JSONL line under ``stedding/ingest_queue/curriculum/``
for downstream enrichment.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Non-secret endpoint defaults — MUST be set before importing baml_client
# (the BAML runtime snapshots os.environ at import time). Never any *_API_KEY.
_ENDPOINT_DEFAULTS: dict[str, str] = {
    "MINIMAX_BASE_URL": "https://api.minimax.io/v1",
    "DASHSCOPE_BASE_URL": "https://coding.dashscope.aliyuncs.com/v1",
    "LANGFUSE_HOST": "http://localhost:3000",
    "USE_LOCAL_SCRAPES": "true",
}
for _name, _value in _ENDPOINT_DEFAULTS.items():
    if not os.environ.get(_name):
        os.environ[_name] = _value

import dlt  # noqa: E402
import structlog  # noqa: E402

logger = structlog.get_logger(__name__)


LC_PDF_ROOT = REPO_ROOT / "leaving_certificate"
GEOG_HANDMADE = REPO_ROOT / "stedding" / "geog.pdf"
PAST_LC_DIR = (
    Path.home()
    / "Library"
    / "Mobile Documents"
    / "com~apple~CloudDocs"
    / "insta_docs"
    / "PastLC-IrishEnglish"
)
DRY_RUN_QUEUE = REPO_ROOT / "stedding" / "ingest_queue" / "curriculum"
DEFAULT_DATASET = "cianfhoghlaim"
DEFAULT_OCR_BACKEND = "qwen3-vl-8b"
DEFAULT_LAKE_URI = (
    f"ducklake://{Path.home()}/.local/share/cianfhoghlaim/curriculum.ducklake"
)

_POLICY_FILENAME_TOKENS: tuple[str, ...] = (
    "programme-statement",
    "key-competencies",
    "advisory-report",
    "online-learning",
    "online-certification",
)

PROVENANCE_PK = ("source_pdf", "source_page", "source_url")


def _model_key(family: str, role: str, language: str | None = None) -> str:
    """Resolve a model key via the canonical MODEL_REGISTRY (graceful fallback)."""
    try:
        from typing import cast

        from meaisinfhoghlaim.models import ModelFamily, model_for

        return model_for(cast(ModelFamily, family), role, language=language)
    except (ImportError, KeyError, ValueError):
        return role


_BAML_CACHE: Any = None
_BAML_LOADED: bool = False


def _load_baml() -> Any:
    """Lazily import the generated BAML sync client (cached)."""
    global _BAML_CACHE, _BAML_LOADED
    if _BAML_LOADED:
        return _BAML_CACHE
    b: Any = None
    try:
        from baml_client import b as baml_b
        b = baml_b
    except ImportError:
        try:
            from baml_client.baml_client.sync_client import b as baml_b
            b = baml_b
        except ImportError:
            b = None
    if b is None:
        logger.warning("baml_client_unavailable")
    _BAML_CACHE = b
    _BAML_LOADED = True
    return b


def _table_schemas() -> dict[str, Any] | None:
    try:
        from scripts._curriculum_table_schemas import TABLE_SCHEMAS

        return TABLE_SCHEMAS
    except (ImportError, AttributeError):
        logger.warning("curriculum_table_schemas_unavailable")
        return None




def _policy_pdfs() -> list[Path]:
    """Return the NCCA policy PDFs at the leaving_certificate/ root."""
    if not LC_PDF_ROOT.exists():
        return []
    out: list[Path] = []
    for pdf in sorted(LC_PDF_ROOT.glob("*.pdf")):
        name = pdf.name.lower()
        if any(token in name for token in _POLICY_FILENAME_TOKENS):
            out.append(pdf)
    return out


def _geography_pdfs() -> list[Path]:
    out: list[Path] = []
    geog_dir = LC_PDF_ROOT / "geography"
    if geog_dir.exists():
        out.extend(sorted(geog_dir.rglob("*.pdf")))
    if GEOG_HANDMADE.exists():
        out.append(GEOG_HANDMADE)
    return out


def _past_lc_images() -> list[Path]:
    if not PAST_LC_DIR.exists():
        return []
    return sorted(p for p in PAST_LC_DIR.glob("*.png") if p.is_file())




def _pdf_pages(pdf_path: Path) -> list[str]:
    """Lazy PDF text extraction, one string per page."""
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    return [(page.extract_text() or "") for page in reader.pages]


def _image_data_url(image_path: Path) -> str:
    """Lazy PNG -> base64 data URL (the BAML clients accept this form)."""
    import base64

    return "data:image/png;base64," + base64.b64encode(image_path.read_bytes()).decode("ascii")




def _language_for_path(pdf_path: Path) -> str:
    """Heuristic: parent dir 'ga' or filename hint -> 'ga', else 'en'."""
    if pdf_path.parent.name.lower() == "ga":
        return "ga"
    if "gaeilge" in pdf_path.name.lower() or "_ga" in pdf_path.stem.lower():
        return "ga"
    return "en"


def _ncca_policy_url(pdf_path: Path) -> str:
    """Best-effort NCCA URL for the 5 root-level policy PDFs."""
    slug = pdf_path.stem.lower().replace(" ", "-")
    return f"https://ncca.ie/en/senior-cycle/key-documents/{slug}"


def _ncca_subject_url(subject_slug: str) -> str:
    return f"https://www.ncca.ie/en/senior-cycle/subjects/{subject_slug}"




def _base_row(
    *,
    source_pdf: str,
    source_page: int,
    source_url: str,
    subject: str,
    language: str,
    model_key: str,
    status: str,
    **extra: Any,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "source_pdf": source_pdf,
        "source_page": int(source_page),
        "source_url": source_url,
        "subject": subject,
        "language": language,
        "model_key": model_key,
        "extracted_at": datetime.now(UTC).isoformat(),
        "extraction_status": status,
    }
    row.update(extra)
    return row


def _apply_limit(seq: list[Path], limit: int | None) -> list[Path]:
    if limit is None or limit <= 0:
        return seq
    return seq[:limit]




@dlt.resource(
    name="geography_topics",
    table_name="geography_topics",
    write_disposition="merge",
    primary_key=list(PROVENANCE_PK),
    standalone=True,
)
def geography_topics_resource(
    limit: int | None = None,
    ocr_backend: str = DEFAULT_OCR_BACKEND,
    dry_run: bool = False,
    dataset: str = DEFAULT_DATASET,
) -> Iterator[dict[str, Any]]:
    """Yield rows for ``cianfhoghlaim.lc.geography.topics``."""
    pdfs = _apply_limit(_geography_pdfs(), limit)
    if not pdfs:
        logger.warning("geography_no_pdfs_found")
        return
    model_key = _model_key("ocr_vision", ocr_backend) or ocr_backend
    b = None if dry_run else _load_baml()
    yielded = 0
    for pdf_path in pdfs:
        try:
            pages = _pdf_pages(pdf_path)
        except Exception as exc:
            logger.warning(
                "geography_pdf_read_failed", pdf=str(pdf_path), error=str(exc)
            )
            if dry_run:
                pages = []
            else:
                continue
        if not pages:
            if dry_run:
                base = _base_row(
                    source_pdf=str(pdf_path),
                    source_page=1,
                    source_url=_ncca_subject_url("geography"),
                    subject="geography",
                    language=_language_for_path(pdf_path),
                    model_key=model_key,
                    status="dry_run",
                )
                yield {
                    **base,
                    "topic_id": f"{pdf_path.stem}-001",
                    "topic_phrase": pdf_path.name,
                    "summary": "",
                    "topic_count": 0,
                }
                yielded += 1
                if limit is not None and limit > 0 and yielded >= limit:
                    return
                continue
            logger.warning("geography_pdf_empty", pdf=str(pdf_path))
            continue
        language = _language_for_path(pdf_path)
        source_url = _ncca_subject_url("geography")
        for page_no, page_text in enumerate(pages, start=1):
            row = _geography_row(
                page_text=page_text,
                pdf_path=pdf_path,
                page_no=page_no,
                language=language,
                source_url=source_url,
                model_key=model_key,
                dry_run=dry_run,
                b=b,
            )
            if row is not None:
                yield row
                yielded += 1
                if limit is not None and limit > 0 and yielded >= limit:
                    return


def _geography_row(
    *,
    page_text: str,
    pdf_path: Path,
    page_no: int,
    language: str,
    source_url: str,
    model_key: str,
    dry_run: bool,
    b: Any,
) -> dict[str, Any] | None:
    base = _base_row(
        source_pdf=str(pdf_path),
        source_page=page_no,
        source_url=source_url,
        subject="geography",
        language=language,
        model_key=model_key,
        status="dry_run" if dry_run else "pending",
    )
    if dry_run:
        return {
            **base,
            "topic_id": f"{pdf_path.stem}-{page_no:03d}",
            "topic_phrase": pdf_path.name,
            "summary": "",
            "topic_count": 0,
        }
    if b is None:
        return {
            **base,
            "topic_id": f"{pdf_path.stem}-{page_no:03d}",
            "topic_phrase": "",
            "summary": "",
            "topic_count": 0,
            "extraction_status": "baml_unavailable",
        }
    try:
        syllabus = b.ExtractGeogSyllabus(page_text[:200_000], language)
        document = getattr(syllabus, "document", None)
        topic_phrase = ""
        summary = ""
        module_topics = getattr(document, "module_topics", None) if document else None
        if module_topics:
            first = module_topics[0]
            name = getattr(first, "name", None)
            if name is not None:
                topic_phrase = (
                    getattr(getattr(name, "text_en", None), "text_en", None)
                    or getattr(getattr(name, "text_en", None), "text", None)
                    or ""
                )
            summary = str(getattr(first, "type", "") or "")
        return {
            **base,
            "topic_id": f"{pdf_path.stem}-{page_no:03d}",
            "topic_phrase": topic_phrase,
            "summary": summary,
            "topic_count": getattr(syllabus, "topic_count", 0),
            "level": getattr(syllabus, "level", "") or "",
            "source_pages": getattr(syllabus, "source_pages", None),
            "extraction_status": "extracted",
        }
    except Exception as exc:
        logger.warning(
            "geography_extraction_failed",
            pdf=str(pdf_path),
            page=page_no,
            error=str(exc)[:200],
        )
        return {
            **base,
            "topic_id": f"{pdf_path.stem}-{page_no:03d}",
            "topic_phrase": "",
            "summary": "",
            "extraction_status": "failed",
            "error": str(exc)[:200],
        }


@dlt.resource(
    name="gaeilge_poems_higher",
    table_name="gaeilge_poems_higher",
    write_disposition="merge",
    primary_key=list(PROVENANCE_PK),
    standalone=True,
)
def gaeilge_poems_higher_resource(
    limit: int | None = None,
    ocr_backend: str = DEFAULT_OCR_BACKEND,
    dry_run: bool = False,
    dataset: str = DEFAULT_DATASET,
) -> Iterator[dict[str, Any]]:
    """Yield rows for ``cianfhoghlaim.lc.gaeilge.poems_higher`` from the 3 PastLC PNGs."""
    images = _apply_limit(_past_lc_images(), limit)
    if not images:
        logger.warning("gaeilge_no_images_found")
        return
    model_key = _model_key("ocr_vision", ocr_backend) or ocr_backend
    b = None if dry_run else _load_baml()
    yielded = 0
    for image_path in images:
        page_no = _page_number_from_filename(image_path.name)
        row = _gaeilge_or_english_row(
            image_path=image_path,
            page_no=page_no,
            language="ga",
            subject="gaeilge",
            level="higher",
            model_key=model_key,
            dry_run=dry_run,
            b=b,
            table="gaeilge_poems_higher",
        )
        if row is not None:
            yield row
            yielded += 1
            if limit is not None and limit > 0 and yielded >= limit:
                return


@dlt.resource(
    name="english_poets_higher",
    table_name="english_poets_higher",
    write_disposition="merge",
    primary_key=list(PROVENANCE_PK),
    standalone=True,
)
def english_poets_higher_resource(
    limit: int | None = None,
    ocr_backend: str = DEFAULT_OCR_BACKEND,
    dry_run: bool = False,
    dataset: str = DEFAULT_DATASET,
) -> Iterator[dict[str, Any]]:
    """Yield rows for ``cianfhoghlaim.lc.english.poets_higher`` from the 3 PastLC PNGs."""
    images = _apply_limit(_past_lc_images(), limit)
    if not images:
        logger.warning("english_no_images_found")
        return
    model_key = _model_key("ocr_vision", ocr_backend) or ocr_backend
    b = None if dry_run else _load_baml()
    yielded = 0
    for image_path in images:
        page_no = _page_number_from_filename(image_path.name)
        row = _gaeilge_or_english_row(
            image_path=image_path,
            page_no=page_no,
            language="en",
            subject="english",
            level="higher",
            model_key=model_key,
            dry_run=dry_run,
            b=b,
            table="english_poets_higher",
        )
        if row is not None:
            yield row
            yielded += 1
            if limit is not None and limit > 0 and yielded >= limit:
                return


def _page_number_from_filename(name: str) -> int:
    """Pull a 1-3 digit page number from a `page_NNN.png` style filename."""
    digits = "".join(ch for ch in name if ch.isdigit())
    return int(digits[:3] or "1")


def _gaeilge_or_english_row(
    *,
    image_path: Path,
    page_no: int,
    language: str,
    subject: str,
    level: str,
    model_key: str,
    dry_run: bool,
    b: Any,
    table: str,
) -> dict[str, Any]:
    base = _base_row(
        source_pdf=str(image_path),
        source_page=page_no,
        source_url="",
        subject=subject,
        language=language,
        model_key=model_key,
        status="dry_run" if dry_run else "pending",
    )
    poem_id = f"{subject}-{level}-{image_path.stem}-{page_no:03d}"
    if dry_run:
        return {
            **base,
            "poem_id": poem_id,
            "poet": "",
            "title_primary": image_path.stem,
            "theme_or_issue": "",
            "prescribed_year": 0,
            "table": table,
        }
    if b is None:
        return {
            **base,
            "poem_id": poem_id,
            "poet": "",
            "title_primary": "",
            "theme_or_issue": "",
            "prescribed_year": 0,
            "table": table,
            "extraction_status": "baml_unavailable",
        }
    try:
        data_url = _image_data_url(image_path)
        # The canonical LC extractor signature for Gaeilge/English is the
        # unified ExtractLC6Syllabus with the subject discriminator — same
        # shape as ExtractGaelSyllabus / ExtractEnglSyllabus, but the
        # unified entry point is the one guaranteed to exist in the
        # generated baml_client across schema refactors.
        syllabus = b.ExtractLC6Syllabus(subject, data_url, language)
        document = getattr(syllabus, "document", None)
        title_primary = ""
        theme = ""
        prescribed_texts = getattr(document, "prescribed_texts", None) if document else None
        if prescribed_texts:
            first = prescribed_texts[0]
            if isinstance(first, str):
                title_primary = first
            else:
                text_en = getattr(first, "text_en", None)
                if text_en is not None:
                    title_primary = getattr(text_en, "text_en", "") or getattr(text_en, "text", "") or ""
                else:
                    title_primary = getattr(first, "text", "") or ""
        return {
            **base,
            "poem_id": poem_id,
            "poet": "",
            "title_primary": title_primary,
            "theme_or_issue": theme,
            "prescribed_year": 0,
            "level": level,
            "topic_count": getattr(syllabus, "topic_count", 0),
            "table": table,
            "extraction_status": "extracted",
        }
    except Exception as exc:
        logger.warning(
            "pastlc_extraction_failed",
            table=table,
            image=str(image_path),
            error=str(exc)[:200],
        )
        return {
            **base,
            "poem_id": poem_id,
            "poet": "",
            "title_primary": "",
            "theme_or_issue": "",
            "prescribed_year": 0,
            "table": table,
            "extraction_status": "failed",
            "error": str(exc)[:200],
        }


@dlt.resource(
    name="education_ie_policies",
    table_name="education_ie_policies",
    write_disposition="merge",
    primary_key=list(PROVENANCE_PK),
    standalone=True,
)
def education_ie_policies_resource(
    limit: int | None = None,
    ocr_backend: str = DEFAULT_OCR_BACKEND,
    dry_run: bool = False,
    dataset: str = DEFAULT_DATASET,
) -> Iterator[dict[str, Any]]:
    """Yield rows for ``cianfhoghlaim.education.ie.policies`` from the 5 NCCA policy PDFs."""
    pdfs = _apply_limit(_policy_pdfs(), limit)
    if not pdfs:
        logger.warning("policies_no_pdfs_found")
        return
    model_key = _model_key("text_llm", "Primary") or ocr_backend
    b = None if dry_run else _load_baml()
    yielded = 0
    for pdf_path in pdfs:
        try:
            pages = _pdf_pages(pdf_path)
        except Exception as exc:
            logger.warning(
                "policy_pdf_read_failed", pdf=str(pdf_path), error=str(exc)
            )
            if dry_run:
                pages = []
            else:
                continue
        full_text = "\n".join(pages)
        source_url = _ncca_policy_url(pdf_path)
        if not pages:
            row = _policy_row(
                pdf_path=pdf_path,
                page_no=1,
                page_text="",
                full_text="",
                source_url=source_url,
                model_key=model_key,
                dry_run=dry_run,
                b=b,
                page_count=0,
            )
            yield row
            yielded += 1
            if limit is not None and limit > 0 and yielded >= limit:
                return
            continue
        for page_no, page_text in enumerate(pages, start=1):
            row = _policy_row(
                pdf_path=pdf_path,
                page_no=page_no,
                page_text=page_text,
                full_text=full_text,
                source_url=source_url,
                model_key=model_key,
                dry_run=dry_run,
                b=b,
                page_count=len(pages),
            )
            if row is not None:
                yield row
                yielded += 1
                if limit is not None and limit > 0 and yielded >= limit:
                    return


def _policy_row(
    *,
    pdf_path: Path,
    page_no: int,
    page_text: str,
    full_text: str,
    source_url: str,
    model_key: str,
    dry_run: bool,
    b: Any,
    page_count: int,
) -> dict[str, Any]:
    base = _base_row(
        source_pdf=str(pdf_path),
        source_page=page_no,
        source_url=source_url,
        subject="education_ie_policy",
        language="en",
        model_key=model_key,
        status="dry_run" if dry_run else "pending",
    )
    policy_id = f"{pdf_path.stem}-{page_no:03d}"
    if dry_run:
        return {
            **base,
            "policy_id": policy_id,
            "title_en": pdf_path.stem.replace("-", " ").title(),
            "summary": "",
            "publisher": "NCCA",
            "year": 0,
            "circular_id": "",
            "page_count": page_count,
        }
    if b is None:
        return {
            **base,
            "policy_id": policy_id,
            "title_en": pdf_path.stem.replace("-", " ").title(),
            "summary": "",
            "publisher": "NCCA",
            "year": 0,
            "circular_id": "",
            "page_count": page_count,
            "extraction_status": "baml_unavailable",
        }
    try:
        # ExtractCircular(text, page_no=1) is the LCEducationCircular shape;
        # we have a (url, html, pdf_text, language) signature on the BAML
        # function but downstream we only use pdf_text.
        circular = b.ExtractCircular(
            source_url, "", (full_text or page_text)[:200_000], "en"
        )
        return {
            **base,
            "policy_id": policy_id,
            "title_en": getattr(circular, "title_en", "") or "",
            "summary": (getattr(circular, "summary", "") or "")[:500],
            "publisher": "NCCA",
            "year": int(getattr(circular, "year", 0) or 0),
            "circular_id": getattr(circular, "circular_id", "") or "",
            "page_count": page_count,
            "extraction_confidence": float(
                getattr(circular, "extraction_confidence", 0.0) or 0.0
            ),
            "extraction_status": "extracted",
        }
    except Exception as exc:
        logger.warning(
            "policy_extraction_failed",
            pdf=str(pdf_path),
            page=page_no,
            error=str(exc)[:200],
        )
        return {
            **base,
            "policy_id": policy_id,
            "title_en": pdf_path.stem.replace("-", " ").title(),
            "summary": "",
            "publisher": "NCCA",
            "year": 0,
            "circular_id": "",
            "page_count": page_count,
            "extraction_status": "failed",
            "error": str(exc)[:200],
        }




@dlt.source(name="curriculum_hydration")
def curriculum_source(
    *,
    subject: str,
    limit: int | None,
    ocr_backend: str,
    dry_run: bool,
    dataset: str,
) -> list[Any]:
    """Build the per-subject DLT resources (one pass over the filesystem)."""
    match subject:
        case "geography":
            return [
                geography_topics_resource(
                    limit=limit,
                    ocr_backend=ocr_backend,
                    dry_run=dry_run,
                    dataset=dataset,
                )
            ]
        case "gaeilge":
            return [
                gaeilge_poems_higher_resource(
                    limit=limit,
                    ocr_backend=ocr_backend,
                    dry_run=dry_run,
                    dataset=dataset,
                )
            ]
        case "english":
            return [
                english_poets_higher_resource(
                    limit=limit,
                    ocr_backend=ocr_backend,
                    dry_run=dry_run,
                    dataset=dataset,
                )
            ]
        case "policies":
            return [
                education_ie_policies_resource(
                    limit=limit,
                    ocr_backend=ocr_backend,
                    dry_run=dry_run,
                    dataset=dataset,
                )
            ]
        case _:
            raise ValueError(f"unknown subject: {subject}")




def _build_destination(dataset: str, lake_uri: str | None = None) -> Any:
    """Build the local DuckLake destination (or MotherDuck opt-in — TODO)."""
    # TODO(motherduck): when MOTHERDUCK_TOKEN is set, return
    # ``dlt.destinations.motherduck(dataset_name=dataset, token=...)``
    # per the 2026-10-10 saga's MotherDuck opt-in path. Out of scope for v1.
    uri = lake_uri or os.environ.get("CURRICULUM_LAKE_URI") or DEFAULT_LAKE_URI
    os.makedirs(os.path.dirname(uri.removeprefix("ducklake://")), exist_ok=True)
    from dlt.destinations.impl.ducklake.configuration import DuckLakeCredentials
    creds = DuckLakeCredentials(ducklake_name="curriculum", catalog=uri)
    return dlt.destinations.ducklake(credentials=creds)




@dataclass
class DryRunSink:
    """Writes one JSONL file per resource under ``stedding/ingest_queue/curriculum/``."""

    root: Path
    count: int = 0
    path: Path | None = None

    def open(self, table_name: str) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
        self.path = self.root / f"{table_name}-{stamp}.jsonl"
        self.count = 0

    def write(self, row: dict[str, Any]) -> None:
        if self.path is None:
            return
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        self.count += 1


def _run_dry_run(
    subject: str,
    *,
    limit: int | None,
    ocr_backend: str,
    dataset: str,
) -> int:
    sink = DryRunSink(root=DRY_RUN_QUEUE)
    src = curriculum_source(
        subject=subject,
        limit=limit,
        ocr_backend=ocr_backend,
        dry_run=True,
        dataset=dataset,
    )
    for resource in src.selected_resources.values():
        sink.open(resource.name)
        for row in resource:
            sink.write(row)
        logger.info(
            "dry_run_written",
            table=resource.name,
            rows=sink.count,
            path=str(sink.path),
        )
        sink.path = None
    print(f"=== curriculum_hydrate ({subject}) dry-run complete ===")
    print(f"queue_dir: {DRY_RUN_QUEUE}")
    return 0


def _run_real(
    subject: str,
    *,
    limit: int | None,
    ocr_backend: str,
    dataset: str,
) -> int:
    src = curriculum_source(
        subject=subject,
        limit=limit,
        ocr_backend=ocr_backend,
        dry_run=False,
        dataset=dataset,
    )
    pipeline = dlt.pipeline(
        pipeline_name="curriculum_hydration",
        destination=_build_destination(dataset=dataset),
        dataset_name=dataset,
    )
    load_info = pipeline.run(src)
    print(f"=== curriculum_hydrate ({subject}) complete ===")
    print(f"load_info: {load_info}")
    return 0




SUBCOMMANDS: tuple[str, ...] = ("geography", "gaeilge", "english", "policies", "all")


def _shared_flags_parser() -> argparse.ArgumentParser:
    """Parent parser carrying the shared CLI flags (shared with every subcommand)."""
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument(
        "--dataset",
        default=os.environ.get("BI_EP_DUCKLAKE_DATASET", DEFAULT_DATASET),
        help=f"Target dataset/schema name (default: {DEFAULT_DATASET}; env: BI_EP_DUCKLAKE_DATASET).",
    )
    p.add_argument(
        "--ocr-backend",
        default=DEFAULT_OCR_BACKEND,
        help=f"OCR/VLM backend role for model resolution (default: {DEFAULT_OCR_BACKEND}).",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Cap rows/files per resource (smoke / dev).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Emit JSONL to stedding/ingest_queue/curriculum/ instead of writing to DuckLake.",
    )
    p.add_argument(
        "--no-dlt",
        action="store_true",
        dest="no_dlt",
        help="Alias for --dry-run.",
    )
    return p


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="curriculum_hydrate",
        description=(
            "Hydrate the Cianfhoghlaim curriculum DuckLake tables "
            "(geography topics / gaeilge poems / english poets / NCCA policies)."
        ),
        parents=[_shared_flags_parser()],
    )
    sub = parser.add_subparsers(dest="subcommand", required=True, metavar="SUBCOMMAND")
    for name in SUBCOMMANDS:
        sub.add_parser(
            name,
            help=f"Run the {name} resource(s).",
            parents=[_shared_flags_parser()],
        )
    return parser.parse_args(argv)


def _resolve_subjects(subcommand: str) -> list[str]:
    if subcommand == "all":
        return ["geography", "gaeilge", "english", "policies"]
    return [subcommand]


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    dry_run = bool(args.dry_run or args.no_dlt)
    subjects = _resolve_subjects(args.subcommand)
    table_schemas = _table_schemas()
    if table_schemas is not None:
        logger.info("curriculum_table_schemas_loaded", keys=list(table_schemas.keys()))

    rc = 0
    for subject in subjects:
        try:
            if dry_run:
                rc |= _run_dry_run(
                    subject,
                    limit=args.limit,
                    ocr_backend=args.ocr_backend,
                    dataset=args.dataset,
                )
            else:
                rc |= _run_real(
                    subject,
                    limit=args.limit,
                    ocr_backend=args.ocr_backend,
                    dataset=args.dataset,
                )
        except FileNotFoundError as exc:
            logger.warning("source_missing", subject=subject, error=str(exc))
            rc |= 0
    return rc


if __name__ == "__main__":
    sys.exit(main())
