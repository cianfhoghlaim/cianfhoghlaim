#!/usr/bin/env python3
"""
Pilot test script for curriculum DLT pipelines.

Tests the per-subject DLT sources with real Firecrawl API calls.
Run with a single subject to verify the pipeline works before full-scale execution.

Usage:
    # Test with Mathematics (English)
    uv run python scripts/test_curriculum_pipeline.py --subject mathematics --language en

    # Test with Irish (Irish language)
    uv run python scripts/test_curriculum_pipeline.py --subject gaeilge --language ga

    # Test SEC examinations
    uv run python scripts/test_curriculum_pipeline.py --mode examinations --subject mathematics --year 2024

    # Dry run (no API calls)
    uv run python scripts/test_curriculum_pipeline.py --dry-run

Environment Variables:
    FIRECRAWL_API_KEY: Required for real crawling
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_subject_source(
    subject: str,
    cycle: str,
    language: str,
    dry_run: bool = False,
) -> dict:
    """Test a single subject source."""
    import dlt

    from dlt_sources.ie.education.subjects.base import create_subject_source

    print(f"\n{'='*60}")
    print(f"Testing: {subject} ({cycle}, {language})")
    print(f"{'='*60}")

    if dry_run:
        print("DRY RUN: Skipping API calls")
        pages_resource, pdfs_resource = create_subject_source(subject, cycle, language)
        print(f"✓ Created resources: {pages_resource.name}, {pdfs_resource.name}")
        return {"status": "dry_run", "subject": subject}

    # Check API key
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("⚠ FIRECRAWL_API_KEY not set - will return placeholder data")

    # Create pipeline with temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        pipeline = dlt.pipeline(
            pipeline_name=f"test_{subject}_{language}",
            destination="duckdb",
            dataset_name=f"curriculum_{cycle}",
            pipelines_dir=tmpdir,
        )

        # Create source
        pages_resource, pdfs_resource = create_subject_source(subject, cycle, language)

        # Create a source wrapper
        @dlt.source(name=f"test_{subject}")
        def test_source():
            return pages_resource, pdfs_resource

        # Run pipeline
        print(f"\nRunning pipeline for {subject}...")
        start_time = datetime.now()

        try:
            info = pipeline.run(test_source())
            elapsed = (datetime.now() - start_time).total_seconds()

            print(f"\n✓ Pipeline completed in {elapsed:.2f}s")
            print(f"  - Failed jobs: {info.has_failed_jobs}")

            # Show loaded data
            with pipeline.sql_client() as client:
                # Count pages
                try:
                    pages_count = client.execute_sql(
                        f"SELECT COUNT(*) FROM {subject}_pages"
                    )
                    print(f"  - Pages loaded: {list(pages_count)[0][0]}")
                except Exception:
                    print("  - Pages loaded: 0 (table not created)")

                # Count PDFs (may not exist if no PDFs found)
                try:
                    pdfs_count = client.execute_sql(
                        f"SELECT COUNT(*) FROM {subject}_pdfs"
                    )
                    print(f"  - PDFs found: {list(pdfs_count)[0][0]}")
                except Exception:
                    print("  - PDFs found: 0 (no PDFs discovered)")

                # Sample data
                try:
                    sample = client.execute_sql(
                        f"SELECT url, title, status FROM {subject}_pages LIMIT 3"
                    )
                    print("\n  Sample pages:")
                    for row in sample:
                        print(f"    - {row[1] or 'No title'}: {row[2]}")
                except Exception:
                    print("\n  No sample pages available")

            return {
                "status": "success",
                "subject": subject,
                "elapsed_seconds": elapsed,
                "has_failed_jobs": info.has_failed_jobs,
            }

        except Exception as e:
            print(f"\n✗ Pipeline failed: {e}")
            return {"status": "error", "subject": subject, "error": str(e)}


def test_examinations_source(
    subject: str,
    year: int,
    level: str = "leaving_certificate",
    dry_run: bool = False,
) -> dict:
    """Test SEC examinations source."""
    import dlt

    from dlt_sources.ie.education.sec_examinations_browser import sec_examinations_browser_source

    print(f"\n{'='*60}")
    print(f"Testing SEC Examinations: {subject} ({year}, {level})")
    print(f"{'='*60}")

    if dry_run:
        print("DRY RUN: Skipping browser automation")
        source = sec_examinations_browser_source(
            subjects=[subject],
            years=[year],
            level=level,
        )
        print(f"✓ Created source: {source.name}")
        print(f"  Resources: {[r.name for r in source.resources.values()]}")
        return {"status": "dry_run", "subject": subject, "year": year}

    print("⚠ Browser automation requires Stagehand backend")
    print("  This test will attempt to use the browser scraper")

    with tempfile.TemporaryDirectory() as tmpdir:
        pipeline = dlt.pipeline(
            pipeline_name=f"test_sec_{subject}_{year}",
            destination="duckdb",
            dataset_name="sec_examinations",
            pipelines_dir=tmpdir,
        )

        source = sec_examinations_browser_source(
            subjects=[subject],
            years=[year],
            level=level,
        )

        print("\nRunning pipeline...")
        start_time = datetime.now()

        try:
            # Only run the all_exam_materials resource for testing
            info = pipeline.run(source.with_resources("all_exam_materials"))
            elapsed = (datetime.now() - start_time).total_seconds()

            print(f"\n✓ Pipeline completed in {elapsed:.2f}s")

            return {
                "status": "success",
                "subject": subject,
                "year": year,
                "elapsed_seconds": elapsed,
            }

        except Exception as e:
            print(f"\n✗ Pipeline failed: {e}")
            return {"status": "error", "subject": subject, "error": str(e)}


def test_full_cycle_source(
    cycle: str,
    language: str,
    limit_subjects: int = 3,
    dry_run: bool = False,
) -> dict:
    """Test full cycle source with limited subjects."""
    if cycle == "senior_cycle":
        from dlt_sources.ie.education.subjects.senior_cycle import (
            SENIOR_CYCLE_SUBJECTS,
            senior_cycle_source,
        )
        subjects = SENIOR_CYCLE_SUBJECTS
        source_fn = senior_cycle_source
    else:
        from dlt_sources.ie.education.subjects.junior_cycle import (
            JUNIOR_CYCLE_SUBJECTS,
            junior_cycle_source,
        )
        subjects = JUNIOR_CYCLE_SUBJECTS
        source_fn = junior_cycle_source

    print(f"\n{'='*60}")
    print(f"Testing Full {cycle.replace('_', ' ').title()} Source")
    print(f"Language: {language}")
    print(f"Total subjects: {len(subjects)}")
    print(f"Testing first {limit_subjects} subjects")
    print(f"{'='*60}")

    if dry_run:
        print("\nDRY RUN: Creating source...")
        source = source_fn(language=language)
        print(f"✓ Created source: {source.name}")
        print(f"  Total resources: {len(source.resources)}")
        print(f"  First {limit_subjects} subjects:")
        for subj in list(subjects.keys())[:limit_subjects]:
            print(f"    - {subj}")
        return {"status": "dry_run", "cycle": cycle, "subject_count": len(subjects)}

    # For real test, just test one subject at a time
    results = []
    for i, subject_slug in enumerate(list(subjects.keys())[:limit_subjects]):
        result = test_subject_source(subject_slug, cycle, language, dry_run=False)
        results.append(result)

    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\n{'='*60}")
    print(f"Summary: {success_count}/{len(results)} subjects successful")
    print(f"{'='*60}")

    return {
        "status": "completed",
        "cycle": cycle,
        "subjects_tested": len(results),
        "successful": success_count,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Test curriculum DLT pipelines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--mode",
        choices=["subject", "examinations", "full-cycle"],
        default="subject",
        help="Test mode (default: subject)",
    )

    parser.add_argument(
        "--subject",
        default="mathematics",
        help="Subject slug to test (default: mathematics)",
    )

    parser.add_argument(
        "--cycle",
        choices=["senior_cycle", "junior_cycle"],
        default="senior_cycle",
        help="Education cycle (default: senior_cycle)",
    )

    parser.add_argument(
        "--language",
        choices=["en", "ga"],
        default="en",
        help="Language (default: en)",
    )

    parser.add_argument(
        "--year",
        type=int,
        default=2024,
        help="Exam year for examinations mode (default: 2024)",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Limit subjects for full-cycle mode (default: 3)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run without API calls",
    )

    args = parser.parse_args()

    print("\n" + "="*60)
    print("Curriculum Pipeline Test")
    print("="*60)
    print(f"Mode: {args.mode}")
    print(f"Dry run: {args.dry_run}")

    # Check environment
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    print(f"FIRECRAWL_API_KEY: {'set' if firecrawl_key else 'NOT SET'}")

    if args.mode == "subject":
        result = test_subject_source(
            args.subject,
            args.cycle,
            args.language,
            dry_run=args.dry_run,
        )
    elif args.mode == "examinations":
        result = test_examinations_source(
            args.subject,
            args.year,
            dry_run=args.dry_run,
        )
    elif args.mode == "full-cycle":
        result = test_full_cycle_source(
            args.cycle,
            args.language,
            limit_subjects=args.limit,
            dry_run=args.dry_run,
        )
    else:
        print(f"Unknown mode: {args.mode}")
        sys.exit(1)

    print(f"\nFinal result: {result}")

    if result.get("status") == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
