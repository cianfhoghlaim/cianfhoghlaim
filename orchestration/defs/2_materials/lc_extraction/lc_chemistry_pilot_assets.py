"""LC chemistry pilot Dagster assets (ADDITIVE — token-plan APIs).

Additive pilot asset group for the
``2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1``
openspec change (§5.5). This module is purely additive: it is
auto-discovered by ``dg.load_defs()`` (which recursively walks the
``orchestration/defs/`` tree) and modifies NOTHING else.

## Scope — exactly 2 extraction paths (NOT the full BIEP v3 ensemble)

The pilot has exactly 2 extraction paths:

- PRIMARY: MiniMax-M3 via the BAML client ``ExtractEn`` (the default
  client of ``ExtractLC6Syllabus`` / ``ExtractChemSyllabus``).
- SECONDARY: qwen3.7-plus via the BAML client
  ``ExtractQwenCrossCheck`` (selected Python-side with
  ``baml_options={"client": "ExtractQwenCrossCheck"}``).

This is NOT the full 4-path RAGAS ensemble the general BIEP v3 spec
(``openspec/specs/british-isles-education-pipeline-v3``) describes —
the pilot deliberately narrows the extraction surface to these 2
paths. Phase C (CocoIndex/LanceDB embedding) and Phase E (marimo
notebook) are DEFERRED and are not built here.

## Untouched neighbours

The existing ``lc5_chemistry_ingested`` asset in
``orchestration/defs/2_materials/lc_extraction/lc5_assets.py`` and the
chemistry cohort in
``orchestration/defs/2_materials/ireland_education/generic_ireland_assets.py``
are untouched — both are scrape-cache-sourced and out of scope for
this pilot.

## The 3 assets + 1 check

- ``lc_chem_pilot_ingested`` — Layer 1 ingestion: the 16 chemistry
  rows from Phase 2a (``lc5_documents(subjects=("chemistry",))``).
- ``lc_chem_pilot_cross_checked`` — Layer 2 materials: the 3 Phase 2b
  cross-check runs (MiniMax primary + Qwen secondary). Degrades
  gracefully (stub statuses, never raises) when BAML or API keys are
  unavailable.
- ``lc_chem_pilot_loaded`` — Layer 2 materials: runs the Phase 2c
  loader (``scripts/load_lc_chemistry_pilot.py``) as a subprocess;
  raises ``Failure`` with the stdout tail on non-zero exit (explicit
  failure, no silent data loss — per the spec scenario "Token-plan
  endpoint unavailable during extraction").
- ``lc_chem_pilot_documents_check`` — asset check on the ingestion
  asset: exactly 16 rows and both languages present.

Secret hygiene: this module NEVER sets, reads, or prints ``*_API_KEY``
values. It sets only non-secret, publicly documented endpoint defaults
(tasks.md §1.6 of the openspec change) and only via
``os.environ.setdefault``.
"""

import os

# ---------------------------------------------------------------------------
# Non-secret endpoint defaults — MUST be set BEFORE any baml_client import:
# the BAML runtime snapshots os.environ at import time. These are public,
# documented endpoint URLs (openspec change
# 2026-08-06-token-plan-apis-..., tasks.md §1.6). NEVER any *_API_KEY —
# keys are hydrated exclusively by the Infisical/mise secret pipeline.
# ---------------------------------------------------------------------------
os.environ.setdefault("MINIMAX_BASE_URL", "https://api.minimax.io/v1")
os.environ.setdefault(
    "DASHSCOPE_BASE_URL", "https://coding.dashscope.aliyuncs.com/v1"
)
os.environ.setdefault("LANGFUSE_HOST", "http://localhost:3000")

import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

from dagster import (  # noqa: E402
    AssetCheckResult,
    AssetExecutionContext,
    Failure,
    asset,
    asset_check,
)

try:
    from baml_client import b  # type: ignore[import-not-found]  # noqa: E402

    BAML_AVAILABLE = True
except ImportError:
    # The generated client may live under the baml_client.baml_client
    # namespace package instead (same two-step fallback as
    # dlt_sources/filesystem/lc6_cross_check.py:_load_baml).
    try:
        from baml_client.baml_client.sync_client import (  # type: ignore[import-not-found]  # noqa: E402
            b,
        )

        BAML_AVAILABLE = True
    except ImportError:
        BAML_AVAILABLE = False
        b = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parents[4]

# -----------------------------------------------------------------------------
# 5-layer group_name convention
# (per openspec/specs/dagster-5-layer-component-architecture/spec.md)
# -----------------------------------------------------------------------------

LC_CHEM_PILOT_INGESTION_GROUP = "1_ingestion_education_lc_chemistry_pilot"
LC_CHEM_PILOT_MATERIALS_GROUP = "2_materials_education_lc_chemistry_pilot"

# Expected Phase 2a row count (8 en + 8 ga chemistry files).
EXPECTED_DOCUMENT_COUNT = 16
EXPECTED_LANGUAGES = ("en", "ga")

# The 2 syllabus PDFs + the 3 cross-check runs (identical to the Phase 2b
# dev runner in dlt_sources/filesystem/lc6_cross_check.py:main() and the
# Phase 2c loader scripts/load_lc_chemistry_pilot.py:CROSS_CHECK_RUNS).
CHEM_EN_PDF = (
    REPO_ROOT / "leaving_certificate/chemistry/en/SCSEC09_Chemistry_syllabus_Eng.pdf"
)
CHEM_GA_PDF = (
    REPO_ROOT
    / "leaving_certificate/chemistry/ga/SCSEC09_Chemistry_syllabus_Gaeilge.pdf"
)
CROSS_CHECK_RUNS: tuple[tuple[Path, str, str], ...] = (
    (CHEM_EN_PDF, "en", "ExtractLC6Syllabus"),
    (CHEM_GA_PDF, "ga", "ExtractLC6Syllabus"),
    (CHEM_EN_PDF, "en", "ExtractChemSyllabus"),
)

PILOT_TABLES = (
    "leaving_cert.chemistry_pilot_documents",
    "leaving_cert.chemistry_pilot_cross_check",
)

LOADER_SCRIPT = REPO_ROOT / "scripts" / "load_lc_chemistry_pilot.py"
# The loader runs extraction + load + verification in ~6 minutes; cap the
# subprocess defensively so a wedged run fails explicitly instead of hanging.
LOADER_TIMEOUT_SECONDS = 1800
LOADER_TAIL_CHARS = 2000


# -----------------------------------------------------------------------------
# Layer 1: Ingestion (Phase 2a — the 16 chemistry rows)
# -----------------------------------------------------------------------------


@asset(
    group_name=LC_CHEM_PILOT_INGESTION_GROUP,
    description=(
        "LC chemistry pilot ingestion (Phase 2a). "
        "Runs lc5_documents(subjects=('chemistry',)) from "
        "dlt_sources/filesystem/leaving_cert_source.py and returns the 16 "
        "chemistry rows (8 en + 8 ga) with resolved_backend/backend_reason. "
        "Additive pilot asset for the 2026-08-06-token-plan-apis change "
        "(§5.5); does NOT replace lc5_chemistry_ingested."
    ),
)
def lc_chem_pilot_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 — filesystem scan of the chemistry pilot cohort."""
    try:
        from dlt_sources.filesystem.leaving_cert_source import lc5_documents
    except ImportError as exc:
        raise Failure(
            description=(
                "dlt_sources.filesystem.leaving_cert_source is not "
                f"importable: {exc}"
            )
        ) from exc

    rows = list(lc5_documents(subjects=("chemistry",)))

    languages: dict[str, int] = {}
    backend_distribution: dict[str, int] = {}
    for row in rows:
        language = row.get("language") or "unknown"
        languages[language] = languages.get(language, 0) + 1
        backend = row.get("resolved_backend") or "unknown"
        backend_distribution[backend] = backend_distribution.get(backend, 0) + 1

    context.log.info(
        "lc_chem_pilot_ingested: %d rows, languages=%s, backends=%s",
        len(rows),
        languages,
        backend_distribution,
    )
    context.add_output_metadata(
        {
            "row_count": len(rows),
            "backend_distribution": backend_distribution,
        }
    )
    return {
        "rows": len(rows),
        "languages": languages,
        "backend_distribution": backend_distribution,
    }


# -----------------------------------------------------------------------------
# Layer 2: Materials (Phase 2b — the 3 cross-check runs, 2 extraction paths)
# -----------------------------------------------------------------------------


@asset(
    group_name=LC_CHEM_PILOT_MATERIALS_GROUP,
    deps=[lc_chem_pilot_ingested],
    description=(
        "LC chemistry pilot cross-check extraction (Phase 2b). "
        "Runs the 3 cross-check runs (ExtractLC6Syllabus on EN + GA "
        "syllabus PDFs, ExtractChemSyllabus on EN) with exactly 2 "
        "extraction paths: MiniMax-M3 primary (client ExtractEn) + "
        "qwen3.7-plus secondary (client ExtractQwenCrossCheck). NOT the "
        "full 4-path RAGAS ensemble. Degrades gracefully (stub statuses, "
        "never raises) when BAML or API keys are unavailable."
    ),
)
def lc_chem_pilot_cross_checked(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 2 — MiniMax-primary / Qwen-secondary cross-check runs.

    The PRIMARY result is canonical. The Qwen secondary is expected to
    fail auth until a real DASHSCOPE_API_KEY lands in the Infisical
    vault; that is expected, not a bug, and must not fail the asset.
    """
    run_stubs = [
        {
            "source_pdf": pdf_path.name,
            "language": language,
            "baml_function": baml_function,
        }
        for pdf_path, language, baml_function in CROSS_CHECK_RUNS
    ]

    if not BAML_AVAILABLE:
        context.log.warning(
            "lc_chem_pilot_cross_checked: baml_client not importable; "
            "returning stub statuses"
        )
        return {
            "runs": [
                {**stub, "status": "skipped_baml_unavailable"}
                for stub in run_stubs
            ]
        }

    try:
        from dlt_sources.filesystem.lc6_cross_check import (
            MAX_TEXT_CHARS,
            CrossCheckResult,
            _call_baml,
            _diff_syllabus,
            _log_to_langfuse,
        )
    except ImportError as exc:
        context.log.warning(
            "lc_chem_pilot_cross_checked: lc6_cross_check not importable "
            "(%s); returning stub statuses",
            exc,
        )
        return {
            "runs": [
                {**stub, "status": "skipped_cross_check_unavailable"}
                for stub in run_stubs
            ]
        }

    try:
        from pypdf import PdfReader
    except ImportError as exc:
        context.log.warning(
            "lc_chem_pilot_cross_checked: pypdf not importable (%s); "
            "returning stub statuses",
            exc,
        )
        return {
            "runs": [{**stub, "status": "skipped_pypdf_unavailable"} for stub in run_stubs]
        }

    def _extract_pdf_text(pdf_path: Path) -> str:
        reader = PdfReader(str(pdf_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    texts: dict[Path, str] = {}
    for pdf_path, _, _ in CROSS_CHECK_RUNS:
        if pdf_path in texts:
            continue
        if not pdf_path.exists():
            context.log.warning(
                "lc_chem_pilot_cross_checked: syllabus PDF missing: %s", pdf_path
            )
            texts[pdf_path] = ""
            continue
        try:
            texts[pdf_path] = _extract_pdf_text(pdf_path)
        except Exception as exc:  # noqa: BLE001 — pypdf raises assorted errors
            context.log.warning(
                "lc_chem_pilot_cross_checked: pypdf failed for %s: %s",
                pdf_path.name,
                exc,
            )
            texts[pdf_path] = ""

    runs: list[dict[str, Any]] = []
    for pdf_path, language, baml_function in CROSS_CHECK_RUNS:
        run: dict[str, Any] = {
            "source_pdf": pdf_path.name,
            "language": language,
            "baml_function": baml_function,
            "status": "primary_failed",
            "primary_topic_count": None,
            "primary_learning_outcome_count": None,
            "secondary_error_class": None,
        }
        text = texts.get(pdf_path, "")
        if not text.strip():
            run["status"] = "skipped_no_text"
            context.log.warning(
                "lc_chem_pilot_cross_checked: no extractable text layer in "
                "%s; not fabricating text",
                pdf_path.name,
            )
            runs.append(run)
            continue
        if len(text) > MAX_TEXT_CHARS:
            context.log.info(
                "lc_chem_pilot_cross_checked: truncating %s to %d chars",
                pdf_path.name,
                MAX_TEXT_CHARS,
            )
            text = text[:MAX_TEXT_CHARS]

        result = CrossCheckResult(
            source_pdf=pdf_path.name,
            language=language,
            baml_function=baml_function,
            status="primary_failed",
        )
        try:
            result.primary = _call_baml(baml_function, "chemistry", text, language)
        except Exception as exc:  # noqa: BLE001 — BAML error types are not stable API
            result.primary_error = str(exc)
            run["primary_error"] = result.primary_error[:200]
            context.log.warning(
                "lc_chem_pilot_cross_checked: primary failed for %s [%s]: %s",
                pdf_path.name,
                baml_function,
                result.primary_error[:200],
            )
            runs.append(run)
            continue

        run["primary_topic_count"] = result.primary.topic_count
        run["primary_learning_outcome_count"] = (
            result.primary.learning_outcome_count
        )
        try:
            result.secondary = _call_baml(
                baml_function,
                "chemistry",
                text,
                language,
                client_override="ExtractQwenCrossCheck",
            )
        except Exception as exc:  # noqa: BLE001 — BAML error types are not stable API
            result.secondary_error = str(exc)
            run["secondary_error_class"] = type(exc).__name__
            result.status = "secondary_failed"
            context.log.warning(
                "lc_chem_pilot_cross_checked: secondary failed for %s [%s] "
                "(%s): %s",
                pdf_path.name,
                baml_function,
                run["secondary_error_class"],
                result.secondary_error[:200],
            )
        else:
            result.disagreements = _diff_syllabus(result.primary, result.secondary)
            result.status = "disagree" if result.disagreements else "agree"

        run["status"] = result.status
        run["disagreements"] = result.disagreements
        # Langfuse observability (never raises; degrades to structlog).
        _log_to_langfuse(result)
        runs.append(run)

    status_counts: dict[str, int] = {}
    for run in runs:
        status_counts[run["status"]] = status_counts.get(run["status"], 0) + 1
    context.log.info("lc_chem_pilot_cross_checked: statuses=%s", status_counts)
    context.add_output_metadata({"status_counts": status_counts})
    return {"runs": runs}


# -----------------------------------------------------------------------------
# Layer 2: Materials (Phase 2c — the canonical lakehouse load)
# -----------------------------------------------------------------------------


@asset(
    group_name=LC_CHEM_PILOT_MATERIALS_GROUP,
    deps=[lc_chem_pilot_ingested, lc_chem_pilot_cross_checked],
    description=(
        "LC chemistry pilot lakehouse load (Phase 2c). Runs the "
        "self-contained loader scripts/load_lc_chemistry_pilot.py as a "
        "subprocess (~6 min): re-runs extraction idempotently, loads "
        "leaving_cert.chemistry_pilot_documents (16 rows) + "
        "leaving_cert.chemistry_pilot_cross_check (3 rows) into "
        "md:cianfhoghlaim via ibis, and verifies via "
        "notebooks/_shared/schema.py:schema_introspect. Raises Failure "
        "with the stdout tail on non-zero exit (explicit failure, no "
        "silent data loss — per the spec scenario 'Token-plan endpoint "
        "unavailable during extraction')."
    ),
)
def lc_chem_pilot_loaded(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 2 — run the Phase 2c loader subprocess and verify its exit."""
    command = [sys.executable, str(LOADER_SCRIPT)]
    context.log.info("lc_chem_pilot_loaded: running %s", " ".join(command))
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=LOADER_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        tail = stdout[-LOADER_TAIL_CHARS:]
        raise Failure(
            description=(
                f"loader timed out after {LOADER_TIMEOUT_SECONDS}s; "
                f"stdout tail: {tail}"
            )
        ) from exc
    except OSError as exc:
        raise Failure(
            description=f"failed to spawn loader subprocess: {exc}"
        ) from exc

    if proc.returncode != 0:
        tail = (proc.stdout or "")[-LOADER_TAIL_CHARS:]
        context.log.error(
            "lc_chem_pilot_loaded: loader exited %d; stdout tail: %s",
            proc.returncode,
            tail,
        )
        raise Failure(
            description=(
                f"loader exited with returncode {proc.returncode}; "
                f"stdout tail: {tail}"
            )
        )

    context.log.info("lc_chem_pilot_loaded: loader succeeded")
    context.add_output_metadata({"tables": list(PILOT_TABLES)})
    return {"loaded": True, "tables": list(PILOT_TABLES)}


# -----------------------------------------------------------------------------
# Asset check (pilot acceptance gate)
# -----------------------------------------------------------------------------


@asset_check(asset=lc_chem_pilot_ingested)
def lc_chem_pilot_documents_check(
    context, lc_chem_pilot_ingested: dict[str, Any]
) -> AssetCheckResult:
    """Dagster asset_check: exactly 16 chemistry rows, both languages."""
    rows = lc_chem_pilot_ingested.get("rows", 0)
    languages = lc_chem_pilot_ingested.get("languages", {})
    both_languages_present = all(
        languages.get(language, 0) > 0 for language in EXPECTED_LANGUAGES
    )
    return AssetCheckResult(
        passed=rows == EXPECTED_DOCUMENT_COUNT and both_languages_present,
        metadata={
            "rows": rows,
            "expected_rows": EXPECTED_DOCUMENT_COUNT,
            "languages": str(languages),
            "expected_languages": str(EXPECTED_LANGUAGES),
            "both_languages_present": both_languages_present,
        },
    )


__all__ = [
    "BAML_AVAILABLE",
    "LC_CHEM_PILOT_INGESTION_GROUP",
    "LC_CHEM_PILOT_MATERIALS_GROUP",
    "lc_chem_pilot_ingested",
    "lc_chem_pilot_cross_checked",
    "lc_chem_pilot_loaded",
    "lc_chem_pilot_documents_check",
]
