#!/usr/bin/env python3
"""
Test script for SEC exam materials scraper.

Tests both Stagehand (AI) and CDP (CSS selectors) scrapers
and compares their results on a sample subject.

Usage:
    # Test Stagehand only
    python test_examinations_scraper.py --method stagehand

    # Test CDP only
    python test_examinations_scraper.py --method cdp

    # Run comparison (default)
    python test_examinations_scraper.py --compare

    # Test specific subject/year
    python test_examinations_scraper.py --subject mathematics --year 2024
"""

import asyncio
import argparse
from datetime import datetime

import structlog

from sruth.browser.sruth_browser.tools.examinations_scraper import (
    scrape_exam_materials,
    scrape_exam_materials_sync as stagehand_sync,
)
from sruth.browser.sruth_browser.tools.examinations_cdp import (
    scrape_exam_materials_cdp,
    scrape_exam_materials_cdp_sync as cdp_sync,
)
from sruth.browser.sruth_browser.tools.examinations_comparison import (
    compare_scrapers,
    print_comparison_report,
)

logger = structlog.get_logger(__name__)


async def test_stagehand(subject: str, year: int, level: str = "leaving_certificate"):
    """Test Stagehand scraper."""
    print(f"\n{'=' * 60}")
    print(f"Testing Stagehand (AI) Scraper")
    print(f"{'=' * 60}")
    print(f"Subject: {subject}")
    print(f"Year: {year}")
    print(f"Level: {level}")
    print()

    start = asyncio.get_event_loop().time()
    materials = []

    try:
        async for material in scrape_exam_materials(subject, [year], level, "en"):
            materials.append(material)
            print(f"  [{material.material_type}] {material.title}")
            print(f"    URL: {material.pdf_url}")
            if material.paper_number:
                print(f"    Paper: {material.paper_number}")
            if material.exam_level:
                print(f"    Level: {material.exam_level}")

        elapsed = (asyncio.get_event_loop().time() - start) * 1000
        print(f"\n✓ Stagehand: Found {len(materials)} materials in {elapsed:.0f}ms")
        return materials

    except Exception as e:
        elapsed = (asyncio.get_event_loop().time() - start) * 1000
        print(f"\n✗ Stagehand failed after {elapsed:.0f}ms: {e}")
        logger.error("stagehand_test_failed", error=str(e))
        return []


async def test_cdp(subject: str, year: int, level: str = "leaving_certificate"):
    """Test CDP scraper."""
    print(f"\n{'=' * 60}")
    print(f"Testing CDP (CSS Selectors) Scraper")
    print(f"{'=' * 60}")
    print(f"Subject: {subject}")
    print(f"Year: {year}")
    print(f"Level: {level}")
    print()

    start = asyncio.get_event_loop().time()
    materials = []

    try:
        async for material in scrape_exam_materials_cdp(subject, [year], level, "en"):
            materials.append(material)
            print(f"  [{material.material_type}] {material.title}")
            print(f"    URL: {material.pdf_url}")
            if material.paper_number:
                print(f"    Paper: {material.paper_number}")
            if material.exam_level:
                print(f"    Level: {material.exam_level}")

        elapsed = (asyncio.get_event_loop().time() - start) * 1000
        print(f"\n✓ CDP: Found {len(materials)} materials in {elapsed:.0f}ms")
        return materials

    except Exception as e:
        elapsed = (asyncio.get_event_loop().time() - start) * 1000
        print(f"\n✗ CDP failed after {elapsed:.0f}ms: {e}")
        logger.error("cdp_test_failed", error=str(e))
        return []


async def run_comparison(subjects: list[str], years: list[int]):
    """Run comparison between Stagehand and CDP scrapers."""
    print(f"\n{'=' * 60}")
    print(f"SEC Exam Scraper Comparison")
    print(f"{'=' * 60}")
    print(f"Subjects: {', '.join(subjects)}")
    print(f"Years: {', '.join(map(str, years))}")
    print(f"Time: {datetime.utcnow().isoformat()}")
    print()

    comparisons = await compare_scrapers(subjects, years)
    print_comparison_report(comparisons)

    return comparisons


async def main():
    parser = argparse.ArgumentParser(
        description="Test SEC exam materials scraper"
    )
    parser.add_argument(
        "--method",
        choices=["stagehand", "cdp", "compare"],
        default="compare",
        help="Which scraper to test",
    )
    parser.add_argument(
        "--subject",
        default="mathematics",
        help="Subject slug (default: mathematics)",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2024,
        help="Exam year (default: 2024)",
    )
    parser.add_argument(
        "--level",
        default="leaving_certificate",
        choices=["leaving_certificate", "junior_cycle"],
        help="Exam level (default: leaving_certificate)",
    )
    parser.add_argument(
        "--subjects",
        nargs="+",
        default=["mathematics", "english", "gaeilge"],
        help="Multiple subjects for comparison",
    )
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=[2024],
        help="Multiple years for comparison",
    )

    args = parser.parse_args()

    # Configure logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_processor(
                structlog.dev.ConsoleRenderer(colors=True)
            ),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    if args.method == "stagehand":
        await test_stagehand(args.subject, args.year, args.level)
    elif args.method == "cdp":
        await test_cdp(args.subject, args.year, args.level)
    else:
        await run_comparison(args.subjects, args.years)


if __name__ == "__main__":
    asyncio.run(main())
