"""
Scraper Comparison Runner - Stagehand (AI) vs CDP (CSS Selectors).

Runs both scrapers in parallel and compares:
- Success rate (items found)
- Latency
- URL overlap (consistency)
- Unique findings (each scraper's strengths)
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncIterator, Awaitable

import structlog

from .examinations_scraper import ExamMaterial, scrape_exam_materials
from .examinations_cdp import scrape_exam_materials_cdp

logger = structlog.get_logger(__name__)


@dataclass
class ScraperComparison:
    """Result of comparing two scrapers on a single subject/year."""

    subject: str
    year: int
    level: str

    # Stagehand results
    stagehand_count: int = 0
    stagehand_urls: set[str] = field(default_factory=set)
    stagehand_latency_ms: float = 0.0
    stagehand_error: str | None = None

    # CDP results
    cdp_count: int = 0
    cdp_urls: set[str] = field(default_factory=set)
    cdp_latency_ms: float = 0.0
    cdp_error: str | None = None

    # Overlap analysis
    @property
    def common_urls(self) -> set[str]:
        return self.stagehand_urls & self.cdp_urls

    @property
    def stagehand_only(self) -> set[str]:
        return self.stagehand_urls - self.cdp_urls

    @property
    def cdp_only(self) -> set[str]:
        return self.cdp_urls - self.stagehand_urls

    @property
    def overlap_percentage(self) -> float:
        """Calculate overlap percentage (Jaccard-like)."""
        total_unique = len(self.stagehand_urls | self.cdp_urls)
        if total_unique == 0:
            return 0.0
        return len(self.common_urls) / total_unique * 100

    @property
    def stagehand_success(self) -> bool:
        return self.stagehand_error is None

    @property
    def cdp_success(self) -> bool:
        return self.cdp_error is None

    def to_report(self) -> str:
        """Generate a human-readable comparison report."""
        status_symbols = {
            (True, True): "✓",
            (True, False): "S",
            (False, True): "C",
            (False, False): "✗",
        }
        status = status_symbols.get((self.stagehand_success, self.cdp_success), "?")

        return f"""
{status} {self.subject} {self.year} ({self.level})
{'─' * 60}
  Stagehand (AI): {self.stagehand_count} items @ {self.stagehand_latency_ms:.0f}ms
  CDP (CSS):       {self.cdp_count} items @ {self.cdp_latency_ms:.0f}ms
  Overlap:         {len(self.common_urls)} URLs ({self.overlap_percentage:.1f}%)
  Stagehand only:  {len(self.stagehand_only)} URLs
  CDP only:        {len(self.cdp_only)} URLs
"""

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "subject": self.subject,
            "year": self.year,
            "level": self.level,
            "stagehand_count": self.stagehand_count,
            "stagehand_latency_ms": self.stagehand_latency_ms,
            "stagehand_success": self.stagehand_success,
            "stagehand_error": self.stagehand_error,
            "cdp_count": self.cdp_count,
            "cdp_latency_ms": self.cdp_latency_ms,
            "cdp_success": self.cdp_success,
            "cdp_error": self.cdp_error,
            "common_count": len(self.common_urls),
            "stagehand_only_count": len(self.stagehand_only),
            "cdp_only_count": len(self.cdp_only),
            "overlap_percentage": self.overlap_percentage,
            "timestamp": datetime.utcnow().isoformat(),
        }


async def _collect_materials(
    async_generator: AsyncIterator[ExamMaterial],
) -> list[ExamMaterial]:
    """Collect materials from an async generator into a list."""
    materials = []
    async for m in async_generator:
        materials.append(m)
    return materials


async def compare_scrapers(
    subjects: list[str],
    years: list[int],
    level: str = "leaving_certificate",
    language: str = "en",
) -> list[ScraperComparison]:
    """
    Run Stagehand and CDP scrapers in parallel and compare results.

    Args:
        subjects: List of subject slugs to test
        years: List of years to scrape
        level: Exam level (leaving_certificate, junior_cycle)
        language: Language code

    Returns:
        List of ScraperComparison objects, one per subject/year combination
    """
    results = []

    for subject in subjects:
        for year in years:
            logger.info("starting_comparison", subject=subject, year=year)

            comparison = ScraperComparison(
                subject=subject,
                year=year,
                level=level,
            )

            # Run both scrapers concurrently
            stagehand_task = asyncio.create_task(_collect_materials(
                scrape_exam_materials(subject, [year], level, language)
            ))
            cdp_task = asyncio.create_task(_collect_materials(
                scrape_exam_materials_cdp(subject, [year], level, language)
            ))

            # Track timing separately for each
            stagehand_start = time.perf_counter()
            cdp_start = time.perf_counter()

            try:
                stagehand_materials = await stagehand_task
                comparison.stagehand_latency_ms = (time.perf_counter() - stagehand_start) * 1000
                comparison.stagehand_count = len(stagehand_materials)
                comparison.stagehand_urls = {m.pdf_url for m in stagehand_materials}
            except Exception as e:
                comparison.stagehand_latency_ms = (time.perf_counter() - stagehand_start) * 1000
                comparison.stagehand_error = str(e)
                logger.error("stagehand_scraper_failed", subject=subject, year=year, error=str(e))

            try:
                cdp_materials = await cdp_task
                comparison.cdp_latency_ms = (time.perf_counter() - cdp_start) * 1000
                comparison.cdp_count = len(cdp_materials)
                comparison.cdp_urls = {m.pdf_url for m in cdp_materials}
            except Exception as e:
                comparison.cdp_latency_ms = (time.perf_counter() - cdp_start) * 1000
                comparison.cdp_error = str(e)
                logger.error("cdp_scraper_failed", subject=subject, year=year, error=str(e))

            results.append(comparison)

            # Log summary for this comparison
            logger.info(
                "comparison_complete",
                subject=subject,
                year=year,
                stagehand_count=comparison.stagehand_count,
                cdp_count=comparison.cdp_count,
                overlap=len(comparison.common_urls),
                overlap_pct=comparison.overlap_percentage,
            )

            # Rate limit between scrapes
            await asyncio.sleep(1)

    return results


async def compare_scrapers_summary(
    subjects: list[str] | None = None,
    years: list[int] | None = None,
    level: str = "leaving_certificate",
) -> dict[str, any]:
    """
    Run comparison and return aggregated summary statistics.

    Args:
        subjects: List of subjects (default: sample of 3)
        years: List of years (default: 2024)
        level: Exam level

    Returns:
        Dict with aggregated statistics
    """
    if subjects is None:
        subjects = ["mathematics", "english", "gaeilge"]
    if years is None:
        years = [2024]

    comparisons = await compare_scrapers(subjects, years, level)

    # Aggregate statistics
    total_stagehand = sum(c.stagehand_count for c in comparisons)
    total_cdp = sum(c.cdp_count for c in comparisons)
    total_common = sum(len(c.common_urls) for c in comparisons)
    avg_latency_stagehand = sum(c.stagehand_latency_ms for c in comparisons if c.stagehand_success) / max(1, sum(1 for c in comparisons if c.stagehand_success))
    avg_latency_cdp = sum(c.cdp_latency_ms for c in comparisons if c.cdp_success) / max(1, sum(1 for c in comparisons if c.cdp_success))

    stagehand_success_rate = sum(1 for c in comparisons if c.stagehand_success) / len(comparisons) * 100
    cdp_success_rate = sum(1 for c in comparisons if c.cdp_success) / len(comparisons) * 100

    return {
        "total_comparisons": len(comparisons),
        "total_items_stagehand": total_stagehand,
        "total_items_cdp": total_cdp,
        "total_common_items": total_common,
        "avg_latency_stagehand_ms": avg_latency_stagehand,
        "avg_latency_cdp_ms": avg_latency_cdp,
        "stagehand_success_rate_pct": stagehand_success_rate,
        "cdp_success_rate_pct": cdp_success_rate,
        "comparisons": [c.to_dict() for c in comparisons],
    }


def print_comparison_report(comparisons: list[ScraperComparison]) -> None:
    """Print a formatted comparison report to stdout."""
    print("\n" + "=" * 60)
    print("SEC EXAM SCRAPER COMPARISON REPORT")
    print("=" * 60)
    print("\nLegend: ✓=Both succeeded, S=Stagehand only, C=CDP only, ✗=Both failed")
    print()

    for comparison in comparisons:
        print(comparison.to_report())

    # Summary statistics
    total_stagehand = sum(c.stagehand_count for c in comparisons)
    total_cdp = sum(c.cdp_count for c in comparisons)
    total_common = sum(len(c.common_urls) for c in comparisons)
    avg_latency_stagehand = sum(c.stagehand_latency_ms for c in comparisons if c.stagehand_success) / max(1, sum(1 for c in comparisons if c.stagehand_success))
    avg_latency_cdp = sum(c.cdp_latency_ms for c in comparisons if c.cdp_success) / max(1, sum(1 for c in comparisons if c.cdp_success))

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total items found:")
    print(f"  Stagehand (AI):  {total_stagehand} items")
    print(f"  CDP (CSS):       {total_cdp} items")
    print(f"  Common:          {total_common} items")
    print(f"\nAverage latency:")
    print(f"  Stagehand: {avg_latency_stagehand:.0f}ms")
    print(f"  CDP:       {avg_latency_cdp:.0f}ms")
    print()


# Synchronous wrapper for convenience
def compare_scrapers_sync(
    subjects: list[str] | None = None,
    years: list[int] | None = None,
    level: str = "leaving_certificate",
) -> list[ScraperComparison]:
    """Synchronous wrapper for compare_scrapers."""
    return asyncio.run(compare_scrapers(subjects, years, level))
