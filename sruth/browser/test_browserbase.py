#!/usr/bin/env python3
"""
Direct Browserbase test for SEC exam scraper.

Uses Browserbase API directly without local Docker stack.

Set environment variables:
    BROWSERBASE_API_KEY=your_key
    BROWSERBASE_PROJECT_ID=your_project_id
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_browserbase_direct():
    """Test Browserbase backend directly for SEC scraping."""
    print("\n" + "=" * 60)
    print("SEC Exam Scraper - Browserbase Direct Test")
    print("=" * 60)

    # Check credentials
    api_key = os.getenv("BROWSERBASE_API_KEY")
    project_id = os.getenv("BROWSERBASE_PROJECT_ID")

    if not api_key or not project_id:
        # Try loading from .env
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("BROWSERBASE_API_KEY")
            project_id = os.getenv("BROWSERBASE_PROJECT_ID")
        except ImportError:
            pass

    if not api_key or "op://" in str(api_key):
        print("\n⚠️  BROWSERBASE_API_KEY not set or uses 1Password reference")
        print("\nTo test, set credentials directly:")
        print("  export BROWSERBASE_API_KEY='your_key'")
        print("  export BROWSERBASE_PROJECT_ID='your_project_id'")
        print("\nOr get them from 1Password and run:")
        print("  BROWSERBASE_API_KEY='xxx' BROWSERBASE_PROJECT_ID='yyy' python3 sruth/browser/test_browserbase.py")
        return []

    print(f"\n✓ Credentials loaded (project: {project_id[:8]}...)")

    # Import and test
    try:
        from sruth.browser.sruth_browser.backends.paid.browserbase import (
            BrowserbaseBackend,
        )
        from sruth.browser.sruth_browser.config import BrowserConfig

        # Override config with credentials
        config = BrowserConfig(
            browserbase_api_key=api_key,
            browserbase_project_id=project_id,
        )

        backend = BrowserbaseBackend(config=config)
        await backend.initialize()
        print("✓ Browserbase session created")

        # Test navigation to examinations.ie
        print("\n📍 Navigating to examinations.ie...")
        nav_result = await backend.navigate(
            "https://www.examinations.ie/exammaterialarchive/"
        )
        print(f"  {'✓' if nav_result.success else '✗'} Navigation: {nav_result.success}")
        if nav_result.title:
            print(f"  Title: {nav_result.title}")

        if nav_result.success:
            # Take screenshot to see the page
            print("\n📸 Taking screenshot...")
            shot = await backend.screenshot()
            if shot.success:
                print(f"  ✓ Screenshot captured ({shot.width}x{shot.height})")

            # Extract page content
            print("\n🔍 Extracting dropdowns...")
            extract_result = await backend.extract(
                instruction="Extract all dropdown options for Year, Level, and Subject from this page",
            )
            if extract_result.success:
                print(f"  ✓ Extracted content")

        await backend.close()
        print("\n✓ Session closed")
        print("\n" + "=" * 60)
        print("SUCCESS: Browserbase backend working!")
        print("=" * 60 + "\n")

        return [nav_result]

    except Exception as e:
        print(f"\n{'=' * 60}")
        print(f"ERROR: {e}")
        print(f"{'=' * 60}\n")
        import traceback
        traceback.print_exc()
        return []


async def main():
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

    await test_browserbase_direct()


if __name__ == "__main__":
    asyncio.run(main())
