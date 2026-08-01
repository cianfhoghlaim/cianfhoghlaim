"""
CDP-based SEC Exam Materials Scraper (Deterministic CSS Selector Approach).

This scraper uses direct CSS selectors for dropdown interaction, providing:
- Deterministic behavior (no AI ambiguity)
- Faster execution (no LLM calls for interactions)
- CSS-based extraction (pattern matching)

Compare with:
- Stagehand scraper (AI-powered interactions)
"""

from __future__ import annotations

import asyncio
import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncIterator

from ..backends.selfhosted.cdp_backend import CDPBackend
from ...config import get_config
from .examinations_scraper import (
    ExamMaterial,
    ExamMaterialType,
    _classify_material_type,
    _extract_exam_level,
    _extract_paper_number,
)

logger = __import__("structlog").get_logger(__name__)

# URLs
EXAM_ARCHIVE_URL = "https://www.examinations.ie/exammaterialarchive/"
EXAMINATIONS_BASE_URL = "https://www.examinations.ie"

# CSS Selectors for examinations.ie dropdowns
# These are deterministic selectors based on the page structure
SELECTORS = {
    # Level dropdown (Leaving Certificate vs Junior Cycle)
    "level_dropdown": "#ctl00_ctl00_ContentPlaceHolder1_cboYearGroup",
    # Subject dropdown (all subjects)
    "subject_dropdown": "#ctl00_ctl00_ContentPlaceHolder1_cboSubject",
    # Year dropdown (exam year)
    "year_dropdown": "#ctl00_ctl00_ContentPlaceHolder1_cboYear",
    # Search/View button
    "search_button": "#ctl00_ctl00_ContentPlaceholder1_btnSearch",
    # Results table with PDF links
    "results_table": "#ctl00_ctl00_ContentPlaceholder1_grdExamMaterial",
    # Individual PDF links within table
    "pdf_links": "a[href$='.pdf']",
}

# Rate limiting (1 req/sec for government site)
RATE_LIMIT_SECONDS = 1.0


async def _select_dropdown_value(page, selector: str, value: str) -> bool:
    """Select a value from a dropdown using JavaScript.

    Args:
        page: Playwright page object
        selector: CSS selector for dropdown
        value: Value to select

    Returns:
        True if successful, False otherwise
    """
    try:
        # Try using the select_option method
        await page.select_option(selector, value=value)
        return True
    except Exception:
        # Fallback to JavaScript execution
        try:
            result = await page.evaluate(
                f"""
                () => {{
                    const select = document.querySelector("{selector}");
                    if (!select) return false;
                    select.value = "{value}";
                    select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return true;
                }}
                """
            )
            return result
        except Exception as e:
            logger.warning("dropdown_selection_failed", selector=selector, value=value, error=str(e))
            return False


async def _wait_for_results(page, timeout_ms: int = 5000) -> bool:
    """Wait for the results table to appear and load.

    Args:
        page: Playwright page object
        timeout_ms: Maximum time to wait

    Returns:
        True if results appeared, False otherwise
    """
    try:
        await page.wait_for_selector(SELECTORS["results_table"], timeout=timeout_ms)
        # Additional wait for table content to load
        await page.wait_for_timeout(1000)
        return True
    except Exception:
        return False


async def _extract_pdf_links_from_results(page) -> list[dict]:
    """Extract all PDF links from the results table.

    Args:
        page: Playwright page object

    Returns:
        List of dicts with 'href' and 'text' keys
    """
    try:
        # Get all PDF links in the results table
        links = await page.evaluate("""
            () => {
                const table = document.querySelector("#ctl00_ctl00_ContentPlaceholder1_grdExamMaterial");
                if (!table) return [];

                const links = Array.from(table.querySelectorAll("a[href$='.pdf']"));
                return links.map(a => ({
                    href: a.href,
                    text: a.innerText?.trim() || a.textContent?.trim() || ""
                })).filter(l => l.href);
            }
        """)

        return links if isinstance(links, list) else []

    except Exception as e:
        logger.error("pdf_link_extraction_failed", error=str(e))
        return []


async def _get_dropdown_options(page, selector: str) -> list[dict]:
    """Get all available options from a dropdown.

    Args:
        page: Playwright page object
        selector: CSS selector for dropdown

    Returns:
        List of dicts with 'value' and 'text' keys
    """
    try:
        options = await page.evaluate(f"""
            () => {{
                const select = document.querySelector("{selector}");
                if (!select) return [];

                return Array.from(select.options).map(opt => ({{
                    value: opt.value,
                    text: opt.text
                }}));
            }}
        """)
        return options if isinstance(options, list) else []

    except Exception as e:
        logger.warning("dropdown_options_failed", selector=selector, error=str(e))
        return []


async def scrape_exam_materials_cdp(
    subject: str,
    years: list[int] | None = None,
    level: str = "leaving_certificate",
    language: str = "en",
) -> AsyncIterator[ExamMaterial]:
    """
    Scrape exam materials using CDP with CSS selectors.

    This is a deterministic approach using direct CSS selectors
    instead of AI-powered understanding (Stagehand).

    Args:
        subject: Subject slug (e.g., "mathematics")
        years: Years to scrape (default: 2020-2024)
        level: Exam level (leaving_certificate, junior_cycle)
        language: Language code (en, ga)

    Yields:
        ExamMaterial objects
    """
    if years is None:
        years = list(range(2020, 2025))

    # Get SEC subject name from the existing mapping
    from .examinations_scraper import SEC_SUBJECT_MAPPING
    sec_subject = SEC_SUBJECT_MAPPING.get(subject, subject.replace("-", " ").title())

    backend = CDPBackend(config=get_config())

    try:
        await backend.initialize()

        # Navigate to exam archive
        logger.info(f"navigating_to_exam_archive", subject=sec_subject)
        nav_result = await backend.navigate(EXAM_ARCHIVE_URL)

        if not nav_result.success:
            logger.error("navigation_failed", error=nav_result.error)
            return

        page = backend._page
        await page.wait_for_load_state("networkidle", timeout=10000)
        await asyncio.sleep(2)  # Additional wait for dynamic content

        # First, we need to find the correct level value by checking dropdown options
        level_options = await _get_dropdown_options(page, SELECTORS["level_dropdown"])
        level_value = None
        for opt in level_options:
            opt_text = opt.get("text", "").lower()
            if "leaving" in opt_text and level == "leaving_certificate":
                level_value = opt.get("value")
                break
            elif "junior" in opt_text and level == "junior_cycle":
                level_value = opt.get("value")
                break

        if not level_value:
            logger.warning("level_value_not_found", level=level, available=level_options)
            # Try common values
            level_value = "L" if level == "leaving_certificate" else "J"

        # Select level
        logger.info("selecting_level", level=level, value=level_value)
        if not await _select_dropdown_value(page, SELECTORS["level_dropdown"], level_value):
            logger.warning("level_selection_failed", level=level)
        await asyncio.sleep(RATE_LIMIT_SECONDS)

        # Find the correct subject value
        subject_options = await _get_dropdown_options(page, SELECTORS["subject_dropdown"])
        subject_value = None
        for opt in subject_options:
            opt_text = opt.get("text", "").lower()
            if sec_subject.lower() in opt_text:
                subject_value = opt.get("value")
                break

        if not subject_value:
            logger.warning("subject_value_not_found", subject=sec_subject, trying_first=True)
            if subject_options:
                subject_value = subject_options[0].get("value")
                logger.info("using_first_subject_option", value=subject_value)

        if subject_value:
            # Select subject
            logger.info("selecting_subject", subject=sec_subject, value=subject_value)
            if not await _select_dropdown_value(page, SELECTORS["subject_dropdown"], subject_value):
                logger.warning("subject_selection_failed", subject=sec_subject)
        await asyncio.sleep(RATE_LIMIT_SECONDS)

        for year in years:
            logger.info(f"scraping_year", subject=sec_subject, year=year)

            # Select year
            year_str = str(year)
            year_options = await _get_dropdown_options(page, SELECTORS["year_dropdown"])
            year_value = None
            for opt in year_options:
                if year_str in opt.get("value", "") or year_str in opt.get("text", ""):
                    year_value = opt.get("value")
                    break

            if year_value:
                if not await _select_dropdown_value(page, SELECTORS["year_dropdown"], year_value):
                    logger.warning("year_selection_failed", year=year)
            await asyncio.sleep(RATE_LIMIT_SECONDS)

            # Click search button
            logger.debug("clicking_search_button")
            try:
                await page.click(SELECTORS["search_button"], timeout=5000)
            except Exception as e:
                logger.warning("search_button_click_failed", error=str(e))
                # Try pressing Enter instead
                await page.keyboard.press("Enter")

            # Wait for results
            await asyncio.sleep(2)  # Initial wait for response
            if not await _wait_for_results(page):
                logger.warning("no_results_found", subject=sec_subject, year=year)
                continue

            # Extract PDF links
            links = await _extract_pdf_links_from_results(page)

            if not links:
                logger.warning("no_pdf_links_found", subject=sec_subject, year=year)
                continue

            logger.info(f"found_pdf_links", count=len(links), subject=sec_subject, year=year)

            # Process each link
            for link in links:
                href = link.get("href", "")
                title = link.get("text", "")

                if not href or not href.endswith(".pdf"):
                    continue

                # Make absolute URL if relative
                if href.startswith("/"):
                    href = EXAMINATIONS_BASE_URL + href

                # Classify material type
                material_type = _classify_material_type(href, title)

                yield ExamMaterial(
                    subject=subject,
                    year=year,
                    level=level,
                    material_type=material_type,
                    pdf_url=href,
                    title=title,
                    paper_number=_extract_paper_number(href, title),
                    exam_level=_extract_exam_level(href, title),
                    language=language,
                    content_hash=hashlib.sha256(href.encode()).hexdigest()[:16],
                )

            # Rate limiting between years
            await asyncio.sleep(RATE_LIMIT_SECONDS)

    finally:
        await backend.close()


async def scrape_exam_materials_cdp_sync(
    subject: str,
    years: list[int] | None = None,
    level: str = "leaving_certificate",
    language: str = "en",
) -> list[ExamMaterial]:
    """Synchronous wrapper for CDP scraper."""
    materials = []
    async for m in scrape_exam_materials_cdp(subject, years, level, language):
        materials.append(m)
    return materials
