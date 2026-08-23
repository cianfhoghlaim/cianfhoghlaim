"""UoG Examinations Portal Scraper.

Drives the authenticated University of Galway Campus Identity SSO + the
`exams.universityofgalway.ie` portal to discover and download:

  - Past exam papers (PDF / written-online / MCQ-bank)
  - Marking schemes
  - Model solutions
  - Supplementary papers (resits)

Rate-limited to 1.0 s/req (UoG acceptable-use policy is unknown; we
start conservative and let `OOG_RATELIMIT_MS` shrink it later if we
get an explicit OK).

The scraper knows nothing about DLT, Dagster, or BAML. The DLT source
at `dlt_sources/british_isles/ireland/education/university/exam_papers/
 uog_exam_papers_source.py` wraps it.

Usage (async, fixture-mode safe):
    from sruth_browser.tools.uog_exam_scraper import UoGExamScraper, UoGSsoConfig

    cfg = UoGSsoConfig.from_resolver()
    async with UoGExamScraper(cfg) as scraper:
        if not await scraper.login(page):
            return  # fixture-only mode; the DLT wrapper handles this
        for code in await scraper.discover_module_codes("computer-science"):
            for paper in await scraper.list_papers(code):
                yield paper
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import structlog

from ..core.auth import UoGSsoLogin
from ..core.secrets import UoGSsoConfig
from ..exceptions import UoGAuthExpired

logger = structlog.get_logger(__name__)


# Base URLs
EXAMS_PORTAL_BASE: str = "https://exams.universityofgalway.ie"
EXAMS_PORTAL_PAST_PAPERS_PATH: str = "/my-exams/past-papers"
PUBLIC_MODULE_REGISTRY_URL: str = (
    "https://www.universityofgalway.ie/academic-schools/"
)

# Rate limiting (1 req/sec; configurable via OOG_RATELIMIT_MS)
DEFAULT_RATELIMIT_MS: int = 1_000


class UoGExamMaterialType(StrEnum):
    PAPER = "paper"
    MARKING_SCHEME = "marking_scheme"
    MODEL_SOLUTION = "model_solution"
    SUPPLEMENTARY_PAPER = "supplementary_paper"
    MARKING_INSTRUCTIONS = "marking_instructions"


@dataclass
class UoGExamMaterial:
    """A single exam material row."""

    module_code: str  # e.g. "CT516"
    module_title: str | None = None
    programme_codes: list[str] = field(default_factory=list)  # e.g. ["MSCAI"]
    school_slug: str | None = None
    academic_year: int = 0  # e.g. 2023
    sitting: str = "AUTUMN"  # see baml_src UoGSitting
    material_type: UoGExamMaterialType = UoGExamMaterialType.PAPER
    paper_format: str = "PDF_UPLOAD"  # see baml_src UoGPaperFormat
    language: str = "en"
    source_url: str = ""
    title: str | None = None
    content_hash: str = ""
    downloaded_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    bytes: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_code": self.module_code,
            "module_title": self.module_title,
            "programme_codes": self.programme_codes,
            "school_slug": self.school_slug,
            "academic_year": self.academic_year,
            "sitting": self.sitting,
            "material_type": self.material_type.value,
            "paper_format": self.paper_format,
            "language": self.language,
            "source_url": self.source_url,
            "title": self.title,
            "content_hash": self.content_hash,
            "downloaded_at": self.downloaded_at.isoformat(),
            "bytes": self.bytes,
        }


# Whitelist of school slugs we support in v1. Mirrors
# `_university_deep_factory.UOG_CONFIG.school_subdomain_paths` so the
# discovery step doesn't fire on every school at once.
V1_SCHOOL_WHITELIST: tuple[str, ...] = (
    "computer-science",
    "mathematical-statistical-sciences",
    "physics",
    "education",
    "business",
    "languages-literatures",
)


class UoGExamScraper:
    """Async context manager; one instance per DLT pipeline run."""

    def __init__(self, config: UoGSsoConfig | None = None) -> None:
        self.config = config or UoGSsoConfig.from_resolver()
        self._sso = UoGSsoLogin(self.config)
        self._page: Any = None
        self._context: Any = None
        self._browser: Any = None
        self._playwright: Any = None
        self._ratelimit_ms = int(os.environ.get("OOG_RATELIMIT_MS", DEFAULT_RATELIMIT_MS))
        self._known_real_credentials: bool = self.config.has_real_credentials()

    async def __aenter__(self) -> UoGExamScraper:
        if not self._known_real_credentials:
            # Skip browser entirely in fixture-only mode.
            logger.info("uog_scraper_fixture_only_skip")
            return self
        await self._open_browser()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._browser:
            try:
                await self._browser.close()
            except Exception:  # noqa: BLE001
                pass
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:  # noqa: BLE001
                pass

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    async def login(self) -> bool:
        """Drive the SSO flow.

        Returns True on success, False in fixture-only mode, raises
        `UoGAuthExpired` if the cookies have gone stale and a single
        refresh attempt failed.
        """
        if not self._known_real_credentials:
            return False
        if self._page is None:
            await self._open_browser()
        result = await self._sso.login(self._page)
        return result.authenticated

    async def discover_module_codes(
        self, school_slug: str | None = None
    ) -> AsyncIterator[str]:
        """Discover every module code visible on the authenticated index.

        Without real credentials this is a fixture-mode generator that
        yields a curated whitelist (so the DLT source can still
        exercise the resource code paths in CI).
        """
        if not self._known_real_credentials:
            whitelist = self._fixture_module_codes()
            for code in whitelist:
                yield code
            return

        # Real-credential path. We hit `/my-exams/past-papers` and
        # scrape the module code table. The page is authenticated so
        # we route through the persistent context, not the public
        # registry (which only lists a subset).
        await self._navigate(
            urljoin(EXAMS_PORTAL_BASE, EXAMS_PORTAL_PAST_PAPERS_PATH)
        )
        await self._throttle()
        rows = await self._extract_module_code_rows()
        for row in rows:
            yield row

    async def list_papers(self, module_code: str) -> AsyncIterator[UoGExamMaterial]:
        """List every paper / marking scheme / model solution for one module.

        Fixture-mode safe: returns a `skipped_fixture` material if no
        real credentials are configured.
        """
        if not self._known_real_credentials:
            yield self._fixture_material(module_code)
            return

        await self._navigate(
            urljoin(EXAMS_PORTAL_BASE, f"/my-exams/past-papers/{module_code}")
        )
        await self._throttle()
        rows = await self._extract_paper_rows(module_code)
        for row in rows:
            yield row

    async def download(
        self, material: UoGExamMaterial, target_dir: Path
    ) -> Path:
        """Download the PDF referenced by `material.source_url`.

        Returns the local file path. The DLT row's `bytes` and
        `content_hash` fields are populated in place.
        """
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = (
            f"{material.module_code}_{material.academic_year}"
            f"_{material.sitting.lower()}_{material.material_type.value}.pdf"
        )
        target_path = target_dir / filename
        if target_path.exists():
            # Already on disk; just hash it.
            material.bytes = target_path.stat().st_size
            material.content_hash = hashlib.sha256(
                target_path.read_bytes()
            ).hexdigest()[:16]
            return target_path

        # Drive the browser to download via the CDP download API
        # (Playwright does not expose a synchronous `download_url()`
        # for authenticated PDFs, so we use a `<a download>` click).
        async with self._page.expect_download() as dl_info:
            await self._page.evaluate(
                """
                ([url]) => {
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = '';
                    document.body.appendChild(a);
                    a.click();
                }
                """,
                material.source_url,
            )
        dl = await dl_info.value
        await dl.save_as(str(target_path))

        material.bytes = target_path.stat().st_size
        material.content_hash = hashlib.sha256(
            target_path.read_bytes()
        ).hexdigest()[:16]
        return target_path

    # ------------------------------------------------------------------ #
    # Browser plumbing
    # ------------------------------------------------------------------ #

    async def _open_browser(self) -> None:
        from playwright.async_api import async_playwright

        self._playwright = await async_playwright().start()
        kwargs: dict[str, Any] = {"viewport": {"width": 1920, "height": 1080}}
        if self.config.user_data_dir is not None:
            self.config.user_data_dir.mkdir(parents=True, exist_ok=True)
            kwargs["user_data_dir"] = str(self.config.user_data_dir)
        if (
            self.config.storage_state_path is not None
            and self.config.storage_state_path.exists()
        ):
            kwargs["storage_state"] = str(self.config.storage_state_path)
        self._browser = await self._playwright.chromium.launch(
            headless=os.environ.get("OOG_HEADLESS", "true").lower() == "true",
            **kwargs,
        )
        self._context = self._browser.new_context()
        self._page = await self._context.new_page()

    async def _navigate(self, url: str) -> None:
        if self._page is None:
            await self._open_browser()
        try:
            await self._page.goto(url, wait_until="load", timeout=30_000)
        except Exception as exc:  # noqa: BLE001
            raise UoGAuthExpired(f"Navigate failed: {exc}") from exc

    async def _throttle(self) -> None:
        await asyncio.sleep(self._ratelimit_ms / 1000.0)

    async def _extract_module_code_rows(self) -> list[str]:
        """Extract every `module_code` from the authenticated index page."""
        try:
            from bs4 import BeautifulSoup  # type: ignore

            html = await self._page.content()
            soup = BeautifulSoup(html, "html.parser")
        except Exception:  # noqa: BLE001 — bs4 may be missing in some envs
            # Fall back to a regex extraction of the rendered HTML.
            html = await self._page.content()
            return sorted(set(re.findall(r"([A-Z]{2,4}\d{3,4})", html)))

        codes: set[str] = set()
        for tag in soup.find_all(href=re.compile(r"/my-exams/past-papers/[A-Z]{2,4}\d{3,4}")):
            m = re.search(r"/([A-Z]{2,4}\d{3,4})/?$", tag["href"])
            if m:
                codes.add(m.group(1))
        return sorted(codes)

    async def _extract_paper_rows(self, module_code: str) -> list[UoGExamMaterial]:
        """Extract every paper-level row from the module-specific page."""
        try:
            from bs4 import BeautifulSoup  # type: ignore

            html = await self._page.content()
            soup = BeautifulSoup(html, "html.parser")
        except Exception:  # noqa: BLE001
            # Without bs4 we can't reliably extract structured rows;
            # return one synthetic row using the page URL so the
            # downstream BAML extractor still has something to chew on.
            return [
                UoGExamMaterial(
                    module_code=module_code,
                    source_url=await self._page.url(),
                )
            ]

        rows: list[UoGExamMaterial] = []
        for table in soup.find_all("table"):
            for tr in table.find_all("tr"):
                cells = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
                if len(cells) < 2:
                    continue
                year_match = re.search(r"\b(20\d{2})\b", cells[0])
                if not year_match:
                    continue
                anchor = tr.find("a", href=re.compile(r"\.pdf($|\?)"))
                if not anchor:
                    continue
                href = anchor["href"]
                if not href.startswith("http"):
                    href = urljoin(EXAMS_PORTAL_BASE, href)
                rows.append(
                    UoGExamMaterial(
                        module_code=module_code,
                        academic_year=int(year_match.group(1)),
                        sitting="AUTUMN",  # table doesn't always say; refine from page later
                        material_type=UoGExamMaterialType.PAPER,
                        source_url=href,
                        title=cells[1] if len(cells) > 1 else None,
                    )
                )
        return rows

    # ------------------------------------------------------------------ #
    # Fixture-mode helpers
    # ------------------------------------------------------------------ #

    def _fixture_module_codes(self) -> list[str]:
        """Curated whitelist for fixture mode (no real creds)."""
        return [
            "CT516",  # Deep Learning
            "CT511",  # Software Engineering
            "MA335",  # Mathematical Statistics
            "ED305",  # ? (legacy author archive uses this)
        ]

    def _fixture_material(
        self,
        module_code: str,
        *,
        material_type: UoGExamMaterialType = UoGExamMaterialType.PAPER,
    ) -> UoGExamMaterial:
        suffix_map = {
            UoGExamMaterialType.PAPER: "AUT",
            UoGExamMaterialType.MARKING_SCHEME: "MS",
            UoGExamMaterialType.MODEL_SOLUTION: "SOL",
            UoGExamMaterialType.SUPPLEMENTARY_PAPER: "SUPP",
        }
        suffix = suffix_map.get(material_type, "AUT").lower()
        return UoGExamMaterial(
            module_code=module_code,
            module_title=f"[fixture] {module_code}",
            programme_codes=["MSCAI"],
            school_slug="computer-science",
            academic_year=2023,
            sitting="AUTUMN",
            material_type=material_type,
            paper_format="PDF_UPLOAD",
            source_url=(
                f"https://exams.universityofgalway.ie/fixture/"
                f"{module_code}/2023/{suffix}.pdf"
            ),
            title=f"[fixture] {material_type.value}",
            content_hash=hashlib.sha256(
                f"{module_code}:{material_type.value}".encode()
            ).hexdigest()[:16],
            bytes=0,
        )


# --------------------------------------------------------------------------- #
# Sync wrappers for DLT (DLT synchronous generator sources)
# --------------------------------------------------------------------------- #


def discover_module_codes_sync(school_slug: str | None = None) -> list[str]:
    """Synchronous wrapper around `UoGExamScraper.discover_module_codes`."""
    async def _collect() -> list[str]:
        async with UoGExamScraper() as s:
            return [code async for code in s.discover_module_codes(school_slug)]

    return asyncio.run(_collect())


def list_papers_sync(module_code: str) -> list[UoGExamMaterial]:
    """Synchronous wrapper around `UoGExamScraper.list_papers`."""

    async def _collect() -> list[UoGExamMaterial]:
        async with UoGExamScraper() as s:
            return [m async for m in s.list_papers(module_code)]

    return asyncio.run(_collect())


__all__ = [
    "UoGExamScraper",
    "UoGExamMaterial",
    "UoGExamMaterialType",
    "V1_SCHOOL_WHITELIST",
    "EXAMS_PORTAL_BASE",
    "PUBLIC_MODULE_REGISTRY_URL",
    "discover_module_codes_sync",
    "list_papers_sync",
]
