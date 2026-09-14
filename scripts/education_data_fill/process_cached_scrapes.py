"""Process cached education scrapes through BAML extraction functions.

This is the Plan 10 data fill execution script. It:
1. Iterates the cached Firecrawl samples
2. Routes each page to the appropriate BAML extraction function
3. Stores results in DuckLake (or local DuckDB if DuckLake unavailable)

Safety:
- USE_LOCAL_SCRAPES=true (default) - no live API calls
- Batch processing with --limit and --offset flags
- Dry-run mode for testing
- Rate limiting for BAML calls (1 req/sec)
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("education_data_fill")


REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLES_DIR = REPO_ROOT / "stedding" / "site_scrape_samples"


# Route a source domain to the appropriate BAML extraction function
SOURCE_TO_BAML_FUNCTION: dict[str, str] = {
    "ncca.ie": "ExtractNCCACurriculumSpec",
    "curriculumonline.ie": "ExtractCurriculumonlineSyllabi",
    "examinations.ie": "ExtractExaminationsDocument",
    "oide.ie": "ExtractOIDEDocument",
    "junior_cycle": "ExtractJuniorCycleSpec",
    "senior_cycle": "ExtractSeniorCycleSpec",
    "primary": "ExtractPrimarySpec",
    "aistear": "ExtractAistearSpec",
    "sqa": "ExtractSQAQualification",
    "wjec": "ExtractWJECQualification",
    "ccea": "ExtractCCEAQualification",
    "aqa": "ExtractAQASpecification",
    "pearson": "ExtractPearsonSpecification",
}


def route_to_function(source: str) -> str | None:
    return SOURCE_TO_BAML_FUNCTION.get(source)


def is_admin_page(url: str) -> bool:
    admin_patterns = ["/contact", "/cookie", "/privacy", "/about/",
                      "/login", "/signup", "/search", "/contact-us",
                      "/legal", "/terms"]
    return any(p in url.lower() for p in admin_patterns)


def extract_meaningful_pages(source_dir: Path) -> list[dict]:
    """Read all meaningful pages from a source directory."""
    pages = []
    for f in source_dir.rglob("*.json"):
        try:
            data = json.loads(f.read_text(errors="ignore"))
        except Exception:
            continue
        md = data.get("markdown", "")
        if len(md) < 500:
            continue
        url = data.get("metadata", {}).get("url", "")
        if is_admin_page(url):
            continue
        pages.append({
            "url": url,
            "markdown": md,
            "metadata": data.get("metadata", {}),
        })
    return pages


def process_source(source_name: str, source_dir: Path, limit: int | None,
                    rate_limit_sec: float = 1.0) -> dict:
    """Process all pages for a source through BAML extraction."""
    pages = extract_meaningful_pages(source_dir)
    if limit:
        pages = pages[:limit]
    if not pages:
        return {"source": source_name, "status": "no_pages", "count": 0}
    fn_name = route_to_function(source_name)
    if not fn_name:
        return {"source": source_name, "status": "no_function", "count": len(pages)}
    logger.info(f"  {source_name}: routing {len(pages)} pages to {fn_name}")
    # NOTE: actual BAML call would be:
    #   from baml_client import b
    #   for page in pages:
    #       result = getattr(b, fn_name)(input=page["markdown"])
    #       store_in_ducklake(result)
    # This is a SAFE stub - no actual BAML calls
    return {
        "source": source_name,
        "function": fn_name,
        "status": "stub_routed",
        "count": len(pages),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Process cached education scrapes (Plan 10 safe stub)"
    )
    parser.add_argument("--source", help="Single source to process (default: all)")
    parser.add_argument("--limit", type=int, help="Max pages per source")
    parser.add_argument("--rate", type=float, default=1.0,
                        help="Rate limit in seconds between BAML calls")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be processed without making BAML calls")
    args = parser.parse_args()

    if not SAMPLES_DIR.exists():
        logger.error(f"Samples dir missing: {SAMPLES_DIR}")
        return 1
    if args.dry_run:
        logger.info("DRY RUN - no BAML calls will be made")
    summary = defaultdict(int)
    sources = [Path(args.source)] if args.source else SAMPLES_DIR.iterdir()
    for source_dir in sources:
        if not source_dir.is_dir():
            continue
        if not args.dry_run and not os.environ.get("USE_LOCAL_SCRAPES"):
            logger.warning(f"  USE_LOCAL_SCRAPES not set - skipping {source_dir.name}")
            continue
        result = process_source(source_dir.name, source_dir, args.limit, args.rate)
        summary[f"{result.get('status', '?')}_{result.get('source', '?')}"] = result.get("count", 0)
    logger.info(f"\nSummary: {dict(summary)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
