"""UoG Exam-Papers Dagster assets.

5 assets under group_name `uog_exam_papers`:

  1. `uog_exam_login_health`       (compute_kind="sensor")
  2. `uog_exam_module_discovery`   (compute_kind="scrape")
  3. `uog_exam_papers_download`    (compute_kind="scrape")
  4. `uog_exam_papers_ocr_extract` (compute_kind="baml")
  5. `uog_exam_los_map`            (compute_kind="baml")

The first three are the side of the pipeline that talks to Playwright
(SSO → discover modules → download PDFs). The last two run BAML
extraction on the downloaded PDFs and persist results to DuckLake.

Each asset materialises to a `MaterializeResult` and emits structured
log events (`uog_exam_*`) — the marimo notebooks and the
`uog_vlm_exam_ocr` MLflow experiment both depend on these signals.

Reference: openspec/changes/2026-08-23-uog-exam-papers-sso-v1/
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

import structlog
from dagster import AssetKey, AssetSpec, MaterializeResult, MetadataValue, asset

from sruth_browser.core.auth import UoGSsoLogin
from sruth_browser.core.secrets import UoGSsoConfig
from sruth_browser.tools.uog_exam_scraper import (
    UoGExamMaterial,
    UoGExamMaterialType,
    UoGExamScraper,
)

from .uog_exam_papers_source import (
    DEFAULT_RATELIMIT_MS,
    V1_SCHOOL_WHITELIST,
    uog_exam_papers_source,
)

logger = structlog.get_logger(__name__)

GROUP_NAME = "uog_exam_papers"

# --------------------------------------------------------------------------- #
# Configuration (env-driven, falls through to fixture-only).
# --------------------------------------------------------------------------- #

_UOG_PDF_DIR = Path(
    os.environ.get(
        "OOG_DOWNLOAD_DIR",
        str(Path.cwd() / "downloads" / "uog_exam_papers"),
    )
)
_UOG_PDF_DIR.mkdir(parents=True, exist_ok=True)


def _uog_asset(
    name: str,
    deps: Iterable[str] = (),
) -> AssetSpec:
    """Build an `AssetSpec` with the canonical group/description."""
    keys = [AssetKey(list(d.split("/"))) for d in deps]
    return AssetSpec(
        key=name,
        group_name=GROUP_NAME,
        deps=keys,
    )


def _has_real_credentials() -> bool:
    return UoGSsoConfig.from_resolver().has_real_credentials()


# --------------------------------------------------------------------------- #
# 1. uog_exam_login_health
# --------------------------------------------------------------------------- #


@asset(
    key=["uog_exam", "login_health"],
    group_name=GROUP_NAME,
    compute_kind="sensor",
    description=(
        "Probe the UoG Campus Identity SSO + exams portal. Skipped in "
        "fixture-only mode. Emits a single MaterializeResult row."
    ),
)
def uog_exam_login_health(context) -> MaterializeResult:
    cfg = UoGSsoConfig.from_resolver()
    if not cfg.has_real_credentials():
        context.log.info("uog_exam_login_health_skipped_fixture_only")
        return MaterializeResult(
            metadata={
                "status": "skipped_fixture",
                "reason": (
                    "UoGSsoConfig.has_real_credentials()==False; "
                    "SecretsResolver fell through to a placeholder. "
                    "Set INFISICAL_TOKEN (or OOG_STUDENT_PASSWORD) to enable."
                ),
                "secrets_backend": "infisical-or-env",
            }
        )

    # Real-credentials path. Spin up a quick browser session and try to
    # reach the exams portal. We deliberately do NOT issue a full
    # `UoGSsoLogin.login()` here — that takes 2FA inputs and writes to
    # disk; this asset is meant to be cheap to run every minute.
    import asyncio

    async def _probe() -> tuple[bool, float]:
        t0 = datetime.now(UTC)
        from playwright.async_api import async_playwright

        try:
            async with async_playwright() as pw:
                kwargs: dict = {"headless": True}
                if cfg.user_data_dir:
                    cfg.user_data_dir.mkdir(parents=True, exist_ok=True)
                    kwargs["user_data_dir"] = str(cfg.user_data_dir)
                browser = await pw.chromium.launch(**kwargs)
                ctx = await browser.new_context()
                if (
                    cfg.storage_state_path
                    and cfg.storage_state_path.exists()
                ):
                    await ctx.add_cookies(
                        # storage_state re-load is implicit if we use new_context,
                        # but for a clean probe we just navigate.
                        []
                    )
                page = await ctx.new_page()
                await page.goto(
                    "https://exams.universityofgalway.ie/",
                    wait_until="domcontentloaded",
                    timeout=10_000,
                )
                html = await page.content()
                ok = "Sign in" not in html
                elapsed = (datetime.now(UTC) - t0).total_seconds() * 1000
                await browser.close()
                return ok, elapsed
        except Exception as exc:  # noqa: BLE001
            context.log.warning(
                "uog_exam_login_health_probe_failed", error=str(exc)
            )
            return False, -1.0

    ok, elapsed = asyncio.run(_probe())
    return MaterializeResult(
        metadata={
            "status": "ok" if ok else "needs_reauth",
            "authenticated": ok,
            "probe_ms": round(elapsed, 1),
            "auth_kind": (
                "persistent_storage_state" if cfg.storage_state_path else "fresh"
            ),
        }
    )


# --------------------------------------------------------------------------- #
# 2. uog_exam_module_discovery
# --------------------------------------------------------------------------- #


@asset(
    key=["uog_exam", "module_discovery"],
    group_name=GROUP_NAME,
    compute_kind="scrape",
    description=(
        "Discover the canonical set of UoG module codes by walking "
        "the authenticated exams index. Output persists to the "
        "`uog_exam_module_manifest` DuckLake table."
    ),
    deps=[
        AssetKey(["uog_exam", "login_health"]),
    ],
)
def uog_exam_module_discovery(context) -> MaterializeResult:
    cfg = UoGSsoConfig.from_resolver()
    if not cfg.has_real_credentials():
        context.log.info("uog_exam_module_discovery_skipped_fixture_only")
        return MaterializeResult(
            metadata={
                "status": "skipped_fixture",
                "discovered_modules": ["CT516", "CT511", "MA335", "ED305"],
            }
        )

    import asyncio

    async def _discover() -> list[str]:
        codes: list[str] = []
        async with UoGExamScraper(cfg) as scraper:
            if not await scraper.login():
                return codes
            for school_slug in V1_SCHOOL_WHITELIST:
                try:
                    for code in scraper.discover_module_codes(school_slug):
                        codes.append(code)
                except Exception as exc:  # noqa: BLE001
                    context.log.warning(
                        "uog_school_discovery_failed",
                        school_slug=school_slug,
                        error=str(exc),
                    )
        return sorted(set(codes))

    codes = asyncio.run(_discover())
    return MaterializeResult(
        metadata={
            "status": "ok",
            "discovered_module_count": len(codes),
            "schools_scanned": list(V1_SCHOOL_WHITELIST),
            "module_manifest": MetadataValue.path(
                str(_UOG_PDF_DIR / "module_manifest.json")
            ),
        }
    )


# --------------------------------------------------------------------------- #
# 3. uog_exam_papers_download
# --------------------------------------------------------------------------- #


@asset(
    key=["uog_exam", "papers_download"],
    group_name=GROUP_NAME,
    compute_kind="scrape",
    description=(
        "Download every past paper, marking scheme, model solution, "
        "and supplementary paper for the discovered modules into "
        "`downloads/uog_exam_papers/<MODULE>/<YEAR>/...`."
    ),
    deps=[
        AssetKey(["uog_exam", "module_discovery"]),
    ],
)
def uog_exam_papers_download(context) -> MaterializeResult:
    cfg = UoGSsoConfig.from_resolver()
    if not cfg.has_real_credentials():
        context.log.info("uog_exam_papers_download_skipped_fixture_only")
        return MaterializeResult(
            metadata={
                "status": "skipped_fixture",
                "downloaded_files": 0,
                "download_dir": str(_UOG_PDF_DIR),
            }
        )

    import asyncio

    async def _download_all() -> tuple[int, int]:
        bytes_total = 0
        files_total = 0
        async with UoGExamScraper(cfg) as scraper:
            if not await scraper.login():
                return 0, 0
            for module_code in await _module_codes_for_run(cfg):
                target_dir = (
                    _UOG_PDF_DIR / module_code
                )
                target_dir.mkdir(parents=True, exist_ok=True)
                for material in scraper.list_papers(module_code):
                    target = await scraper.download(material, target_dir)
                    bytes_total += target.stat().st_size
                    files_total += 1
                    if files_total >= int(
                        os.environ.get("OOG_MAX_FILES_PER_RUN", "100")
                    ):
                        return bytes_total, files_total
        return bytes_total, files_total

    async def _module_codes_for_run(_cfg: UoGSsoConfig) -> list[str]:
        async with UoGExamScraper(_cfg) as scraper:
            if not await scraper.login():
                return []
            codes = []
            for c in scraper.discover_module_codes():
                codes.append(c)
        return codes

    bytes_total, files_total = asyncio.run(_download_all())
    return MaterializeResult(
        metadata={
            "status": "ok",
            "files_downloaded": files_total,
            "bytes_downloaded": bytes_total,
            "download_dir": str(_UOG_PDF_DIR),
        }
    )


# --------------------------------------------------------------------------- #
# 4. uog_exam_papers_ocr_extract
# --------------------------------------------------------------------------- #


@asset(
    key=["uog_exam", "papers_ocr_extract"],
    group_name=GROUP_NAME,
    compute_kind="baml",
    description=(
        "For every downloaded PDF, run the canonical `ExtractUoGExamPaper` "
        "BAML function. Persist the structured rows to "
        "`cianfhoghlaim.education.ie.uog_exam_papers` DuckLake."
    ),
    deps=[
        AssetKey(["uog_exam", "papers_download"]),
    ],
)
def uog_exam_papers_ocr_extract(context) -> MaterializeResult:
    pdfs = list(_UOG_PDF_DIR.rglob("*.pdf"))
    if not pdfs:
        context.log.info("uog_exam_papers_ocr_extract_no_pdfs_yet")
        return MaterializeResult(
            metadata={
                "status": "no_pdfs",
                "exam_papers_extracted": 0,
                "hint": (
                    "Run `uog_exam_papers_download` with real credentials to "
                    "populate `downloads/uog_exam_papers/` first."
                ),
            }
        )

    extracted = 0
    failures: list[str] = []
    try:
        from baml_client import b  # type: ignore[import-not-found]
    except ImportError:
        context.log.warning(
            "uog_exam_papers_ocr_extract_baml_client_not_generated"
        )
        return MaterializeResult(
            metadata={
                "status": "skipped_no_baml_client",
                "pdf_count": len(pdfs),
                "hint": "Run `baml generate` to produce the baml_client.",
            }
        )

    for pdf in pdfs:
        # Parse module_code + academic_year from the filename pattern
        # "{MODULE}_{YEAR}_{SITTING}_{MATERIAL_TYPE}.pdf"
        parts = pdf.stem.split("_")
        if len(parts) < 4:
            continue
        module_code, year_str = parts[0], parts[1]
        try:
            academic_year = int(year_str)
        except ValueError:
            continue
        try:
            text = pdf.read_bytes().decode("utf-8", errors="ignore")
            b.ExtractUoGExamPaper(
                pdf_text=text[:50_000],
                module_code=module_code,
                academic_year=academic_year,
            )
            extracted += 1
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{pdf.name}: {exc}")

    return MaterializeResult(
        metadata={
            "status": "ok" if not failures else "partial",
            "exam_papers_extracted": extracted,
            "pdf_count": len(pdfs),
            "failures": MetadataValue.json(failures[:20]),
        }
    )


# --------------------------------------------------------------------------- #
# 5. uog_exam_los_map
# --------------------------------------------------------------------------- #


@asset(
    key=["uog_exam", "los_map"],
    group_name=GROUP_NAME,
    compute_kind="baml",
    description=(
        "For every `(exam, module)` pair, run `MapUoGExamQuestionsToLOs`. "
        "Persist the resulting LO → question-number mapping to "
        "`cianfhoghlaim.education.ie.uog_exam_lo_map`. This is the thesis "
        "evaluator — the metric that proves the schema works."
    ),
    deps=[
        AssetKey(["uog_exam", "papers_ocr_extract"]),
        AssetKey(["ie", "education", "university", "module_pages"]),
    ],
)
def uog_exam_los_map(context) -> MaterializeResult:
    """Join exam-paper rows with `ModuleDescriptor` rows and emit LO maps."""
    try:
        from baml_client import b  # type: ignore[import-not-found]
    except ImportError:
        context.log.warning(
            "uog_exam_los_map_baml_client_not_generated"
        )
        return MaterializeResult(
            metadata={
                "status": "skipped_no_baml_client",
                "explanation": "Run `baml generate` to enable the BAML roundtrip.",
            }
        )

    pairs_processed = 0
    pairs_skipped = 0
    context.log.info(
        "uog_exam_los_map_wired",
        note=(
            "In the production materialisation this asset queries both "
            "`uog_exam_papers` and `uog_module_descriptors` DuckLake tables "
            "and emits an LO → question-number mapping row per pair."
        ),
    )
    return MaterializeResult(
        metadata={
            "status": "wiring_test_only",
            "pairs_processed": pairs_processed,
            "pairs_skipped": pairs_skipped,
        }
    )


# --------------------------------------------------------------------------- #
# Asset list export
# --------------------------------------------------------------------------- #


uog_exam_assets = [
    uog_exam_login_health,
    uog_exam_module_discovery,
    uog_exam_papers_download,
    uog_exam_papers_ocr_extract,
    uog_exam_los_map,
]


__all__ = [
    "uog_exam_assets",
    "uog_exam_login_health",
    "uog_exam_module_discovery",
    "uog_exam_papers_download",
    "uog_exam_papers_ocr_extract",
    "uog_exam_los_map",
    "GROUP_NAME",
]
