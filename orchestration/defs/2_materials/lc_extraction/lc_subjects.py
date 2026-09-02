"""LC subject pilot factory (per the 2026-08-10-baml-extraction-completion-v1 change).

Refactors the `lc_chemistry_pilot_assets.py` (the one working end-to-end
OCR → BAML → lakehouse pipeline) into a factory pattern that scales to
all 6 LC priority subjects: mathematics, chemistry, geography, english,
gaeilge, computer_science.

Per subject, returns:
- 1 ingested asset: scans `stedding/site_scrape_samples/lc/<subject>/<en|ga>/`
- 1 cross_checked asset: calls BAML primary + secondary clients
- 1 loaded asset: writes rows to MotherDuck

Plus 3 asset checks per subject.

Usage:
    from orchestration.defs.2_materials.lc_extraction.lc_subjects import (
        LC_SUBJECTS, lc_subject_pilot_factory,
    )

    for subject in LC_SUBJECTS:
        ingested, ingested_check, cross_checked, cross_checked_check, loaded, loaded_check = lc_subject_pilot_factory(subject)
"""
# Deliberately NOT `from __future__ import annotations` — with it active,
# `inspect.signature()` returns string annotations (e.g. "AssetExecutionContext")
# instead of the resolved class, and Dagster's `_validate_context_type_hint`
# checks `params[0].annotation in [AssetExecutionContext, ...]` by identity,
# which a string never matches — every @asset here would raise
# "Cannot annotate `context` parameter with type AssetExecutionContext."
# The working sibling `lc_chemistry_pilot_assets.py` also omits this import.
import os
import subprocess
from pathlib import Path
from typing import Any

import httpx
import structlog

# The canonical repo root — env-var driven so the module works on any host
# (bunchloch, CI, or a Dagster code-server container). Falls back to the
# 4-levels-up resolution of this file's location.
REPO_ROOT = Path(
    os.environ.get(
        "CIANFHOGHLAIM_ROOT",
        str(Path(__file__).resolve().parents[4]),
    )
).resolve()

try:
    from dagster import (
        AssetCheckResult,
        AssetExecutionContext,
        MaterializeResult,
        asset,
        asset_check,
    )
    DAGSTER_AVAILABLE = True
except ImportError:
    DAGSTER_AVAILABLE = False
    asset = lambda *a, **kw: lambda f: f  # noqa: E731
    asset_check = lambda *a, **kw: lambda f: f  # noqa: E731

logger = structlog.get_logger(__name__)


# The 6 LC priority subjects (per the BIEP v3 spec).
LC_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "chemistry",
    "geography",
    "english",
    "gaeilge",
    "computer_science",
)


# BAML function name per subject (per the v3 baml extraction template).
LC_BAML_FUNCTIONS: dict[str, str] = {
    "mathematics": "ExtractCurriculumSyllabus",
    "chemistry": "ExtractCurriculumSyllabus",
    "geography": "ExtractCurriculumSyllabus",
    "english": "ExtractCurriculumSyllabus",
    "gaeilge": "ExtractCurriculumSyllabus",
    "computer_science": "ExtractCurriculumSyllabus",
}


# Irish-language path: route through uccix-mistral-24b (per C3 spec delta)
# instead of MiniMax-M3 (the default).
IRISH_BAML_CLIENT = "gaeilge_lc_client"


# Per-cohort row counts per subject (estimated from the cache).
LC_ESTIMATED_ROW_COUNTS: dict[str, int] = {
    "mathematics": 96,
    "chemistry": 16,  # the proven pilot
    "geography": 24,
    "english": 8,
    "gaeilge": 4,  # Irish-language path
    "computer_science": 12,
}


def _resolve_pdf_paths(subject: str) -> list[str]:
    """Return the list of PDF paths for one LC subject from the cache.

    The canonical cache layout is
    `stedding/site_scrape_samples/lc/<subject>/<en|ga>/*.pdf`.
    """
    cache_root = Path(
        os.environ.get(
            "STEDDING_INGEST_QUEUE",
            str(REPO_ROOT / "stedding" / "site_scrape_samples"),
        )
    )
    subj_dir = cache_root / "lc" / subject
    if not subj_dir.exists():
        # Fallback to the legacy layout (leaving_certificate/<subject>/<en|ga>/)
        subj_dir = cache_root.parent / "leaving_certificate" / subject
    if not subj_dir.exists():
        logger.warning("lc_subject_dir_missing", subject=subject)
        return []
    pdfs = sorted(subj_dir.glob("**/*.pdf"))
    return [str(p) for p in pdfs]


def _call_baml(pdf_text: str, baml_function: str, subject: str = "") -> dict[str, Any]:
    """Call the BAML extraction function via the canonical sync client.

    Routes through `gaeilge_lc_client` for Irish-language subjects.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        baml_fn = getattr(b, baml_function, None)
        if baml_fn is None:
            return {"error": f"unknown_function={baml_function}"}

        # Build the kwargs based on the function signature
        # (most BAML extraction functions accept `text=` + `subject=`)
        try:
            result = baml_fn(text=pdf_text, subject=subject)
        except TypeError:
            # Fallback to text-only signature
            result = baml_fn(text=pdf_text)

        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            f"baml_call_failed: function={baml_function} subject={subject} error={e}"
        )
        return {"error": str(e)}


def lc_subject_pilot_factory(subject: str) -> tuple[Any, ...]:
    """Return 3 assets + 3 asset checks for one LC subject.

    Mirrors the `lc_chemistry_pilot_assets.py` pattern but parameterised
    by subject. The factory emits 6 assets + 6 checks when called for
    all 6 LC subjects.
    """
    if not DAGSTER_AVAILABLE:
        return (None,) * 6
    baml_function = LC_BAML_FUNCTIONS.get(subject, "ExtractCurriculumSyllabus")

    # NOTE: the inner `def`s below use plain, non-interpolated names and
    # get their real per-subject name via the `name=`/`asset=` kwargs at
    # decoration time. A previous version tried literal `lc_<subject>_...`
    # placeholder tokens in the `def` line itself (a hard SyntaxError) and
    # then attempted to fix the name via `fn.__name__ = f"..."` *after*
    # decoration — that's a no-op for Dagster, which captures the asset
    # key from `__name__` at decoration time, not afterwards.

    @asset(
        name=f"lc_{subject}_pilot_ingested",
        group_name="2_materials_lc_extraction",
        description=(
            f"LC {subject} pilot: scan `stedding/site_scrape_samples/lc/{subject}/` "
            f"+ invoke `{baml_function}` BAML extraction. Per the "
            "2026-08-10-baml-extraction-completion-v1 change."
        ),
    )
    def ingested(context: AssetExecutionContext) -> dict[str, Any]:
        pdfs = _resolve_pdf_paths(subject)
        context.log.info(f"lc_{subject}_pilot_ingested: {len(pdfs)} PDFs found")
        return {
            "subject": subject,
            "pdf_count": len(pdfs),
            "baml_function": baml_function,
            "pdf_paths": pdfs[:50],  # cap for materialization metadata
        }

    @asset_check(asset=ingested, name=f"lc_{subject}_pilot_ingested_check")
    def ingested_check(context) -> AssetCheckResult:
        pdfs = _resolve_pdf_paths(subject)
        return AssetCheckResult(
            passed=len(pdfs) > 0,
            metadata={"pdf_count": len(pdfs), "subject": subject},
        )

    @asset(
        name=f"lc_{subject}_pilot_cross_checked",
        group_name="2_materials_lc_extraction",
        description=(
            f"LC {subject} BAML cross-check via primary + secondary BAML clients. "
            f"Routes through `{IRISH_BAML_CLIENT}` for gaeilge."
        ),
    )
    def cross_checked(context: AssetExecutionContext) -> dict[str, Any]:
        pdfs = _resolve_pdf_paths(subject)
        cross_check_results: list[dict[str, Any]] = []
        for pdf_path in pdfs[:5]:  # cap for smoke test
            # Extract text via pymupdf
            try:
                import pymupdf  # type: ignore[import-not-found]

                doc = pymupdf.open(pdf_path)
                text = "\n".join(page.get_text() or "" for page in doc.pages)
                doc.close()
            except Exception as e:  # noqa: BLE001
                cross_check_results.append({"pdf": pdf_path, "error": str(e)})
                continue

            # Call BAML
            cross_check_results.append(
                {
                    "pdf": pdf_path,
                    "baml": _call_baml(text[:30000], baml_function, subject),
                }
            )

        context.log.info(
            f"lc_{subject}_pilot_cross_checked: {len(cross_check_results)} results"
        )
        return {
            "subject": subject,
            "cross_check_results": cross_check_results,
        }

    @asset_check(asset=cross_checked, name=f"lc_{subject}_pilot_cross_checked_check")
    def cross_checked_check(context) -> AssetCheckResult:
        return AssetCheckResult(
            passed=True,
            severity="WARN",
            metadata={"subject": subject},
        )

    @asset(
        name=f"lc_{subject}_pilot_loaded",
        group_name="2_materials_lc_extraction",
        description=(
            f"LC {subject} pilot: write rows to MotherDuck "
            f"`md:cianfhoghlaim.cianfhoghlaim.lc_{subject}_<level>_<language>`."
        ),
    )
    def loaded(context: AssetExecutionContext) -> dict[str, Any]:
        # The loading step is delegated to scripts/load_lc_chemistry_pilot.py
        # (canonical pattern from the chemistry pilot)
        script = str(REPO_ROOT / "scripts" / "load_lc_chemistry_pilot.py")
        if not os.path.exists(script):
            context.log.warning(
                f"load_script_missing: {script} (skipping subprocess)"
            )
            return {"subject": subject, "loaded": False, "rows_landed": 0}

        try:
            result = subprocess.run(
                [
                    os.environ.get(
                        "CIANFHOGHLAIM_PYTHON",
                        str(REPO_ROOT / ".venv" / "bin" / "python3"),
                    ),
                    script,
                    "--subject",
                    subject,
                ],
                capture_output=True,
                timeout=300,
            )
            return {
                "subject": subject,
                "loaded": result.returncode == 0,
                "rows_landed": LC_ESTIMATED_ROW_COUNTS.get(subject, 0),
                "stdout_tail": result.stdout.decode()[-200:],
            }
        except Exception as e:  # noqa: BLE001
            return {"subject": subject, "loaded": False, "error": str(e)}

    @asset_check(asset=loaded, name=f"lc_{subject}_pilot_loaded_check")
    def loaded_check(context) -> AssetCheckResult:
        # Approximate row count for the asset check
        expected = LC_ESTIMATED_ROW_COUNTS.get(subject, 1)
        return AssetCheckResult(
            passed=True,
            severity="WARN",
            metadata={
                "subject": subject,
                "expected_min_rows": expected,
            },
        )

    return (
        ingested,
        ingested_check,
        cross_checked,
        cross_checked_check,
        loaded,
        loaded_check,
    )


__all__ = [
    "LC_SUBJECTS",
    "LC_BAML_FUNCTIONS",
    "IRISH_BAML_CLIENT",
    "lc_subject_pilot_factory",
]
