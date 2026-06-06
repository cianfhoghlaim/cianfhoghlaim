"""LinkedIn Profile DLT Pipeline — Croilar Flows.

Extracts structured profile data from LinkedIn public profiles
for the three Croilar flows: aleyum, cianfhoghlaim, carlcashman.

Two extraction modes:
  1. Mock mode (USE_LOCAL_SCRAPES=true) — reads from pre-saved JSON
     files in stedding/dev/cianfhoghlaim/croilar-team-workflow/dummy-data/
  2. Live mode — uses sruth-browser (Browserbase CDP) to authenticate
     and scrape the public profile page.

The output is a DuckDB table (one row per scrape) suitable for
downstream BAML extraction via the linkedin_profile_extraction schema.

Usage:
    import dlt
    from pipelines.linkedin import linkedin_profile_resource

    pipeline = dlt.pipeline(
        pipeline_name="linkedin_croilar",
        destination="duckdb",
        dataset_name="linkedin_data",
    )
    load_info = pipeline.run(linkedin_profile_resource(
        profile_url="https://www.linkedin.com/in/cllr-carl-cashman-cemap-89a491144/",
        flow_id="carlcashman",
    ))
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import dlt

from _shared.config import get_repo_root

REPO_ROOT = get_repo_root()
USE_LOCAL = os.environ.get("USE_LOCAL_SCRAPES", "true").lower() in ("1", "true", "yes")


@dlt.resource(table_name="linkedin_profiles", write_disposition="merge", primary_key="profile_id")
def linkedin_profile_resource(
    profile_url: str,
    flow_id: str,
    use_mock: bool = True,
) -> Any:
    """Yield a single LinkedIn profile record per profile URL.

    In mock mode, reads from a pre-saved JSON file. In live mode,
    uses the sruth-browser (Browserbase CDP) to scrape the profile.

    Args:
        profile_url: Full LinkedIn profile URL (e.g. https://www.linkedin.com/in/...)
        flow_id: The croilar flow ID (e.g. "carlcashman", "cianfhoghlaim")
        use_mock: If True, read from local JSON. If False, use live scraping.
    """
    # Extract a unique-ish identifier from the URL
    profile_slug = profile_url.rstrip("/").split("/in/")[-1].split("?")[0].replace("/", "_")
    profile_id = f"linkedin_{flow_id}_{profile_slug}"

    if use_mock or USE_LOCAL:
        mock_dir = (
            REPO_ROOT
            / "stedding"
            / "dev"
            / "cianfhoghlaim"
            / "croilar-team-workflow"
            / "dummy-data"
            / "linkedin"
        )
        mock_file = mock_dir / f"{flow_id}_{profile_slug}.json"

        if mock_file.exists():
            with open(mock_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["profile_id"] = profile_id
            data["flow_id"] = flow_id
            data["source_url"] = profile_url
            data["extraction_mode"] = "mock"
            yield data
            return

        # No mock file found — yield a minimal placeholder
        yield {
            "profile_id": profile_id,
            "flow_id": flow_id,
            "source_url": profile_url,
            "extraction_mode": "mock_placeholder",
            "name": profile_slug.replace("-", " ").title(),
            "headline": "Profile mock data not yet created",
            "location": "",
            "about": "",
            "experience": [],
            "education": [],
            "skills": [],
            "recommendations": [],
        }
        return

    # Live mode — use Browserbase CDP
    from sruth.browser import scrape_linkedin_profile

    data = scrape_linkedin_profile(profile_url)
    data["profile_id"] = profile_id
    data["flow_id"] = flow_id
    data["source_url"] = profile_url
    data["extraction_mode"] = "live"
    yield data


def run_linkedin_pipeline(
    profile_url: str,
    flow_id: str,
    destination: str | Any | None = None,
    dataset_name: str = "linkedin_data",
    use_mock: bool = True,
) -> Any:
    """Run the full LinkedIn profile ingestion pipeline.

    Args:
        profile_url: LinkedIn profile URL to scrape
        flow_id: Croilar flow ID
        destination: DLT destination (default: DuckDB)
        dataset_name: Dataset name in the destination
        use_mock: Use mock data or live scraping

    Returns:
        LoadInfo from the pipeline run
    """
    if destination is None:
        from dlt_utils import get_dlt_destination
        destination = get_dlt_destination()

    pipeline = dlt.pipeline(
        pipeline_name="linkedin_croilar",
        destination=destination,
        dataset_name=dataset_name,
        progress="log",
    )

    return pipeline.run([linkedin_profile_resource(profile_url, flow_id, use_mock)])
