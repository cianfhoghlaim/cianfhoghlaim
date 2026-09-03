#!/usr/bin/env python3
"""
Quick test for SEC exam scraper using Browserbase MCP.

This bypasses the local browser stack and uses Browserbase directly.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_browserbase_stagehand():
    """Test Stagehand scraper via Browserbase MCP."""
    print("\n" + "=" * 60)
    print("Testing SEC Exam Scraper via Browserbase MCP")
    print("=" * 60)

    try:
        from sruth.browser.sruth_browser.tools.examinations_scraper import (
            scrape_exam_materials,
        )

        subject = "mathematics"
        year = 2024
        level = "leaving_certificate"

        print(f"\nScraping: {subject} {year} ({level})")
        print("This may take 30-60 seconds...\n")

        materials = []
        async for material in scrape_exam_materials(
            subject=subject,
            years=[year],
            level=level,
            language="en",
        ):
            materials.append(material)
            print(f"  ✓ [{material.material_type}] {material.title}")
            print(f"    URL: {material.pdf_url[:80]}...")

        print(f"\n{'=' * 60}")
        print(f"SUCCESS: Found {len(materials)} materials")
        print(f"{'=' * 60}\n")

        return materials

    except Exception as e:
        print(f"\n{'=' * 60}")
        print(f"ERROR: {e}")
        print(f"{'=' * 60}\n")
        import traceback
        traceback.print_exc()
        return []


async def main():
    # Configure logging
    import structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="%H:%M:%S"),
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    await test_browserbase_stagehand()


if __name__ == "__main__":
    asyncio.run(main())
