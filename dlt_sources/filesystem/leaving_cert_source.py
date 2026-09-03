"""
Leaving Certificate 6-subject filesystem DLT source.

Ingests every PDF (and JPG for the scanned geography exam page) in
`cianfhoghlaim/leaving_certificate/{chemistry,computer_science,english,
gaeilge,geography,mathematics}/{en,ga}/` into 6 per-subject DuckLake tables:

  - lc_chemistry_papers,    lc_chemistry_syllabus,    lc_chemistry_marking
  - lc_computer_science_*,  lc_computer_science_marking
  - lc_english_*,           lc_english_marking        (english dir is
                                                       en-only at root,
                                                       similar to gaeilge)
  - lc_gaeilge_*,           lc_gaeilge_marking        (the gaeilge dir has
                                                       no en/ subdir; files
                                                       live at the root)
  - lc_geography_*,         lc_geography_marking
  - lc_mathematics_*,       lc_mathematics_marking

Each PDF is routed through the v4 `select_ocr_backend()` heuristic
(per cianfhoghlaim/meaisinfhoghlaim/models/registry.py):
  - Irish-language (gaeilge) → glm-4.6v-flash (MLX-preferred)
  - exam papers (LC###ALP/EV/IV.pdf) → qwen3-vl-8b (workhorse)
  - syllabi (SC###Syllabus or SC-Chemistry-Specification-*.pdf) →
    gemma-4-26B-A4B (M4 default)
  - marking schemes (SCSEC##_guideline_material_eng.pdf) →
    molmo2-8b (diagram-pointing specialist)
  - scanned JPG → docling-serve (DocTags layout fallback)
"""

from __future__ import annotations
import dlt


import hashlib
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt_sources
import httpx
import structlog

logger = structlog.get_logger(__name__)

DEFAULT_LC_ROOT = Path(
    os.environ.get(
        "CIANFHOGHLAIM_LC_ROOT",
        str(Path(__file__).resolve().parents[2] / "leaving_certificate"),
    )
)

# The 6 target subjects of the LC6-subject pipeline (added 2026-07-10:
# english, per openspec/changes/2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1)
# Kept unchanged (not renamed/extended in place) because
# lc_chemistry_pilot_assets.py and other Dagster assets reference it
# directly as the canonical 6-subject cohort.
LC6_SUBJECTS: tuple[str, ...] = (
    "chemistry",
    "computer_science",
    "english",
    "gaeilge",
    "geography",
    "mathematics",
)

# 7 more subjects confirmed to have real local PDFs under
# leaving_certificate/<subject>/ that were never wired into a scan list
# (biology/business/history/applied_mathematics have an en/ga split like
# the LC6 subjects; french/technology/ukrainian are root-level single-
# language like gaeilge/english below).
LC_ADDITIONAL_SUBJECTS: tuple[str, ...] = (
    "biology",
    "business",
    "history",
    "applied_mathematics",
    "french",
    "technology",
    "ukrainian",
)

# All 13 subjects with a real local PDF corpus today.
LC_ALL_SUBJECTS: tuple[str, ...] = LC6_SUBJECTS + LC_ADDITIONAL_SUBJECTS

# Subjects whose files live directly at the subject dir root rather than
# split into en/ga subdirs, mapped to the default language to record for
# them. gaeilge and english were the only 2 originally handled (as
# hardcoded special cases in _scan_subject()); french/technology/ukrainian
# have the identical root-level layout and are folded into the same
# general-purpose lookup instead of adding 3 more special cases.
LC_ROOT_LEVEL_SUBJECT_LANGUAGES: dict[str, str] = {
    "gaeilge": "ga",
    "english": "en",
    "french": "en",
    "technology": "en",
    "ukrainian": "en",
}

# Maps each PDF kind (regex on filename) to the v4 registry model key
# that `select_ocr_backend()` would select. Used downstream by the
# Dagster layer-2 asset to pick the right model for VLM/OCR extraction.
LC_PDF_KIND_REGISTRY: dict[str, str] = {
    # LC###ALP###EV.pdf / LC###GLP###IV.pdf — exam papers
    r"^LC\d{3}[AG]LP\d{3,4}[EI]V\.pdf$": "qwen3-vl-8b",
    # LC002ALP200EV.pdf — LC English Annual Leaving Programme exam paper
    r"^LC002ALP\d{3}[EI]V\.pdf$": "qwen3-vl-8b",
    # SCSEC##_Syllabus_*.pdf / SC-Chemistry-Specification-*.pdf
    r"^SC.*[Ss]yllabus.*\.pdf$": "gemma-4-26B-A4B",
    r"^SC.*[Ss]pecification.*\.pdf$": "gemma-4-26B-A4B",
    # SC-English-Spec-ENG-INT*.pdf — LC English spec constitution
    r"^SC-English-Spec-ENG-INT.*\.pdf$": "gemma-4-26B-A4B",
    # Siollabais-Nuashonraithe-* — Irish syllabus
    r"^Siollabais.*\.pdf$": "gemma-4-26B-A4B",
    # SCSEC##_guideline_material_*.pdf — marking scheme guidelines
    r"^SCSEC\d+_guideline.*\.pdf$": "molmo2-8b",
    # LC-Computer-Science-specification-*.pdf / Geography-syllabus-*.pdf
    r"^LC-.*[Ss]pecification.*\.pdf$": "gemma-4-26B-A4B",
    # lc_irish_foundation / LC001ALP100IV — gaeilge exam papers
    r"^lc_irish_foundation.*\.pdf$": "glm-4.6v-flash",
    # Default fallback
    r".*\.pdf$": "qwen3-vl-8b",
}

# Per-language model override (used for Irish-language PDFs)
GAEILGE_MODEL_KEY = "glm-4.6v-flash"

# Supported image extensions (geography includes 1 JPG scanned exam page)
IMAGE_EXTENSIONS: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".tiff")

# ---------------------------------------------------------------------------
# qwen3-vl-8b availability + MiniMax-M3 fallback
# ---------------------------------------------------------------------------
# qwen3-vl-8b runs as a llama-swap-managed llama-server process on port 8086
# (LLAMA_ARG_PORT default in meaisinfhoghlaim/models/llama_swap_config.yaml).
# llama-server exposes the standard llama.cpp `/health` endpoint; that is the
# only health-check convention for this model in the repo (grepped "8086"
# and "health" under meaisinfhoghlaim/models/ — no bespoke client exists),
# so it is used here directly rather than inventing a new one.
#
# Per openspec/changes/2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-
# tls-remediation-v1/tasks.md §5.2 + specs/british-isles-education-pipeline-
# v3/spec.md: qwen3-vl-8b is the OCR primary, MiniMax-M3 (multimodal,
# OpenAI-compatible endpoint) is the fallback when the local backend is
# unavailable. Only qwen3-vl-8b needs this fallback — the other 3 backend
# choices (glm-4.6v-flash, gemma-4-26B-A4B, molmo2-8b, docling-serve) are
# left untouched.
LLAMA_SWAP_QWEN3_VL_8B_PORT = os.environ.get("LLAMA_SWAP_QWEN3_VL_8B_PORT", "8086")
LLAMA_SWAP_QWEN3_VL_8B_HEALTH_URL = os.environ.get(
    "LLAMA_SWAP_QWEN3_VL_8B_HEALTH_URL",
    f"http://localhost:{LLAMA_SWAP_QWEN3_VL_8B_PORT}/health",
)

# Per tasks.md §1.6 / specs/centralized-model-registry: MiniMax token-plan
# endpoint is OpenAI-compatible at https://api.minimax.io/v1.
MINIMAX_DEFAULT_BASE_URL = "https://api.minimax.io/v1"
MINIMAX_MODEL = "MiniMax-M3"


def _llama_swap_qwen_healthy(timeout: float = 2.0) -> bool:
    """GET the llama-server `/health` endpoint for qwen3-vl-8b on :8086.

    Returns False (never raises) on connection-refused, timeout, or any
    other transport error — the caller treats False as "fall back to
    MiniMax-M3".
    """
    try:
        resp = httpx.get(LLAMA_SWAP_QWEN3_VL_8B_HEALTH_URL, timeout=timeout)
        return resp.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException, httpx.TransportError, OSError) as e:
        logger.info(
            "llama_swap_qwen3_vl_8b_unhealthy",
            url=LLAMA_SWAP_QWEN3_VL_8B_HEALTH_URL,
            error=str(e),
        )
        return False


def _minimax_multimodal_fallback(
    file_name: str, prompt: str = "OCR fallback health probe. Reply with OK."
) -> dict[str, Any]:
    """Call the MiniMax-M3 multimodal endpoint as the qwen3-vl-8b fallback.

    Uses MINIMAX_API_KEY / MINIMAX_BASE_URL (already-hydrated env vars).
    This is a minimal live probe (not a full-document OCR call) — it
    exists to confirm the fallback path is reachable and functioning for
    a given file, per the 2026-08-06 token-plan openspec change.

    Never raises; returns a dict describing success/failure so the
    pipeline can keep going (backend selection must degrade gracefully,
    not hard-fail a whole load).
    """
    api_key = os.environ.get("MINIMAX_API_KEY")
    base_url = os.environ.get("MINIMAX_BASE_URL", MINIMAX_DEFAULT_BASE_URL)

    if not api_key:
        logger.warning("minimax_fallback_no_api_key", file_name=file_name)
        return {"ok": False, "error": "MINIMAX_API_KEY not set"}

    try:
        resp = httpx.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": MINIMAX_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 16,
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        content = (
            data.get("choices", [{}])[0].get("message", {}).get("content", "")
        )
        logger.info(
            "minimax_fallback_ok",
            file_name=file_name,
            model=MINIMAX_MODEL,
            reply_preview=content[:40],
        )
        return {"ok": True, "reply": content}
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as e:
        logger.warning("minimax_fallback_failed", file_name=file_name, error=str(e))
        return {"ok": False, "error": str(e)}


def select_ocr_backend(model_key: str, file_name: str = "") -> dict[str, Any]:
    """Resolve the actual backend to dispatch a file's OCR/extraction to.

    `model_key` is the v4 registry key already picked by `_classify_pdf()`
    (e.g. "qwen3-vl-8b", "glm-4.6v-flash", "gemma-4-26B-A4B", "molmo2-8b",
    "docling-serve"). Only "qwen3-vl-8b" is health-checked + has a
    fallback wired up — it is the one confirmed unavailable in this
    (no-Docker) environment. The other 3 backend choices are returned
    unchanged.
    """
    if model_key != "qwen3-vl-8b":
        return {"backend": model_key, "reason": "no fallback configured for this backend"}

    if _llama_swap_qwen_healthy():
        return {"backend": "qwen3-vl-8b", "reason": "llama-swap :8086 /health OK"}

    probe = _minimax_multimodal_fallback(file_name)
    if probe["ok"]:
        return {
            "backend": "minimax-m3",
            "reason": "llama-swap :8086 unreachable -> MiniMax-M3 multimodal fallback",
        }
    return {
        "backend": "minimax-m3-failed",
        "reason": f"llama-swap :8086 unreachable AND MiniMax-M3 fallback failed: {probe['error']}",
    }


def _classify_pdf(pdf_path: Path, language: str) -> str:
    """Pick the v4 registry model key for a given PDF based on its name + language.

    Args:
        pdf_path: The PDF file.
        language: 'en' or 'ga'.

    Returns:
        A v4 registry model key (e.g. 'qwen3-vl-8b').
    """
    name = pdf_path.name
    # Irish-language PDFs always use the GLM (multilingual + fast)
    if language == "ga":
        return GAEILGE_MODEL_KEY
    # English PDFs: regex-based classification
    for pattern, model_key in LC_PDF_KIND_REGISTRY.items():
        if pattern != r".*\.pdf$" and __import__("re").match(pattern, name):
            return model_key
    # Fallback
    return "qwen3-vl-8b"


def _scan_subject(subject_dir: Path) -> Iterator[dict[str, Any]]:
    """Yield (file_path, language) tuples for one LC subject.

    Handles 2 layouts:
    - Root-level, single-language (gaeilge, english, and — extended here —
      french/technology/ukrainian): no en/ga split, files live directly in
      the subject dir. Default language comes from
      LC_ROOT_LEVEL_SUBJECT_LANGUAGES.
    - en/ga split (chemistry, computer_science, geography, mathematics,
      biology, business, history, applied_mathematics): files live under
      <subject>/en/ and/or <subject>/ga/.
    """
    if not subject_dir.exists():
        logger.warning(f"lc_subject_dir_missing: {subject_dir}")
        return

    root_language = LC_ROOT_LEVEL_SUBJECT_LANGUAGES.get(subject_dir.name)
    if root_language is not None:
        for ext in (".pdf",) + IMAGE_EXTENSIONS:
            for f in subject_dir.glob(f"*{ext}"):
                yield {
                    "file_path": f,
                    "language": root_language,
                    "subject": subject_dir.name,
                }
    else:
        for lang in ("en", "ga"):
            lang_dir = subject_dir / lang
            if not lang_dir.exists():
                continue
            for ext in (".pdf",) + IMAGE_EXTENSIONS:
                for f in lang_dir.glob(f"*{ext}"):
                    yield {
                        "file_path": f,
                        "language": lang,
                        "subject": subject_dir.name,
                    }


def _row(record: dict[str, Any]) -> dict[str, Any]:
    """Build the DuckLake row for one PDF (or image) ingestion."""
    file_path: Path = record["file_path"]
    language: str = record["language"]
    subject: str = record["subject"]

    file_hash = ""
    try:
        file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
    except OSError:
        # Some files may be unreadable (permissions / missing)
        pass

    is_image = file_path.suffix.lower() in IMAGE_EXTENSIONS
    model_key = _classify_pdf(file_path, language)
    backend_selection = select_ocr_backend(model_key, file_path.name)
    return {
        "id": hashlib.sha256(
            f"{file_hash}:{file_path.name}:{language}".encode("utf-8")
        ).hexdigest()[:16],
        "file_hash": file_hash,
        "file_name": file_path.name,
        "file_path": str(file_path),
        "file_size_bytes": file_path.stat().st_size if file_path.exists() else 0,
        "is_image": is_image,
        "language": language,
        "subject": subject,
        # The v4 registry model key chosen for this file
        "model_key": model_key,
        # The backend actually selected after health-check/fallback
        # resolution (see select_ocr_backend()) — may differ from
        # model_key when qwen3-vl-8b is unavailable and MiniMax-M3 was
        # used instead.
        "resolved_backend": backend_selection["backend"],
        "backend_reason": backend_selection["reason"],
        # Classification by filename pattern
        "is_exam_paper": bool(
            __import__("re").match(r"^LC.*[AG]LP.*\.pdf$", file_path.name)
        ),
        "is_syllabus": bool(
            __import__("re").match(
                r"^(SCSEC.*Syllabus|SC-Chemistry-Specification|LC-.*[Ss]pecification|Siollabais).*\.pdf$",
                file_path.name,
            )
        ),
        "is_marking_scheme": bool(
            __import__("re").match(r"^SCSEC\d+_guideline.*\.pdf$", file_path.name)
        ),
    }


@dlt.resource(
    name="lc5_documents",
    write_disposition="replace",
    primary_key="id",
    columns={
        "id": {"data_type": "text"},
        "file_hash": {"data_type": "text"},
        "file_name": {"data_type": "text"},
        "file_path": {"data_type": "text"},
        "file_size_bytes": {"data_type": "bigint"},
        "is_image": {"data_type": "bool"},
        "language": {"data_type": "text"},
        "subject": {"data_type": "text"},
        "model_key": {"data_type": "text"},
        "resolved_backend": {"data_type": "text"},
        "backend_reason": {"data_type": "text"},
        "is_exam_paper": {"data_type": "bool"},
        "is_syllabus": {"data_type": "bool"},
        "is_marking_scheme": {"data_type": "bool"},
    },
)
def lc5_documents(
    root_path: str = str(DEFAULT_LC_ROOT),
    subjects: tuple[str, ...] | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield one row per LC PDF (or image) across the 6 subjects × 2 languages.

    Default root: `cianfhoghlaim/leaving_certificate/`.
    Override via the `CIANFHOGHLAIM_LC_ROOT` env var.

    `subjects`: restrict the scan to a subset of LC6_SUBJECTS (e.g.
    `("chemistry",)` for a dev-mode single-subject dry run). Defaults to
    all 6 subjects. Combine with dlt's `.add_limit()` on the returned
    resource for a defensive row cap in dev mode.
    """
    root = Path(root_path)
    if not root.exists():
        logger.error(f"lc5_root_missing: {root}")
        return

    scan_subjects = subjects if subjects is not None else LC6_SUBJECTS
    n = 0
    for subject in scan_subjects:
        subject_dir = root / subject
        for record in _scan_subject(subject_dir):
            row = _row(record)
            yield row
            n += 1
    logger.info(f"lc5_ingested: {n} documents across {len(scan_subjects)} subjects")


def main() -> int:
    """CLI entry — runs the pipeline against the local DuckLake bronze layer.

    Previously wrote to an ad-hoc `lc5_ingest.duckdb` file in the current
    working directory (untracked, not part of the running local lakehouse
    stack). Repointed to the proven local DuckLake destination
    (get_dlt_destination(use_ducklake=True) — Postgres:5433 catalog +
    Garage S3:3900, already used by JurisdictionPipelineBase) so this
    ingestion actually lands in the lakehouse rather than a scratch file.
    Scans all 13 subjects with a real local PDF corpus (LC_ALL_SUBJECTS),
    not just the original LC6.
    """
    from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination

    pipeline = dlt.pipeline(
        pipeline_name="lc_leaving_cert",
        destination=get_dlt_destination(use_ducklake=True),
        dataset_name="cianfhoghlaim.bronze.ireland_leaving_cert",
    )
    load_info = pipeline.run(lc5_documents(subjects=LC_ALL_SUBJECTS))
    print(load_info)
    # Show the row count per subject/language via the pipeline's own
    # destination client rather than a second, separate raw duckdb
    # connection to a file dlt itself already manages.
    with pipeline.sql_client() as client:
        df = client.execute_sql(
            "SELECT subject, language, COUNT(*) AS n FROM lc5_documents "
            "GROUP BY subject, language ORDER BY subject, language"
        )
        for row in df:
            print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
