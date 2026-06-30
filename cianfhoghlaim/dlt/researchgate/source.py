"""ResearchGate DLT pipeline for Croilar Streams.

ResearchGate has no public REST API; this source uses sruth-browser
(Browserbase CDP) to scrape the public profile page, then emits a
single record suitable for downstream BAML extraction via the
`researchgate_extraction.baml` schema.

Mirrors the structure of `pipelines/linkedin/source.py` so the Stream
registry's `RESEARCHGATE` source type can be wired through the same
generic asset factory.

Usage:
    from pipelines.researchgate import researchgate_profile_resource

    load_info = pipeline.run(researchgate_profile_resource(
        profile_url="https://www.researchgate.net/profile/Cian_Mac_An_Deisigh",
        stream_id="teaching",
        owner_display_name="Cian Mac an Déisigh Uí Liatháin",
    ))
"""

from __future__ import annotations

import json
import os
from typing import Any

import dlt
from _shared.config import get_repo_root

REPO_ROOT = get_repo_root()
USE_LOCAL = os.environ.get("USE_LOCAL_SCRAPES", "true").lower() in ("1", "true", "yes")


@dlt.resource(table_name="researchgate_profiles", write_disposition="merge", primary_key="profile_id")
def researchgate_profile_resource(
    profile_url: str,
    stream_id: str,
    owner_display_name: str = "",
    use_mock: bool = True,
) -> Any:
    """Yield a single ResearchGate profile record per profile URL.

    In mock mode, reads from a pre-saved JSON file. In live mode,
    uses the sruth-browser (Browserbase CDP) to scrape the profile.

    Args:
        profile_url: Full ResearchGate profile URL.
        stream_id: The croilar Stream id (e.g. "teaching", "music").
        owner_display_name: Canonical human-readable name.
        use_mock: If True, read from local JSON. If False, use live scraping.
    """
    profile_slug = (
        profile_url.rstrip("/")
        .split("/profile/")[-1]
        .split("?")[0]
        .replace("/", "_")
    )
    profile_id = f"researchgate_{stream_id}_{profile_slug}"

    if use_mock or USE_LOCAL:
        mock_dir = (
            REPO_ROOT
            / "stedding"
            / "dev"
            / "cianfhoghlaim"
            / "croilar-team-workflow"
            / "dummy-data"
            / "researchgate"
        )
        mock_file = mock_dir / f"{stream_id}_{profile_slug}.json"

        if mock_file.exists():
            with open(mock_file, encoding="utf-8") as f:
                data = json.load(f)
            data["profile_id"] = profile_id
            data["stream_id"] = stream_id
            data["owner_display_name"] = owner_display_name
            data["source_url"] = profile_url
            data["extraction_mode"] = "mock"
            yield data
            return

        yield {
            "profile_id": profile_id,
            "stream_id": stream_id,
            "owner_display_name": owner_display_name,
            "source_url": profile_url,
            "extraction_mode": "mock_placeholder",
            "name": profile_slug.replace("-", " ").replace("_", " ").title(),
            "headline": "ResearchGate profile mock data not yet created",
            "institution": "",
            "location": "",
            "about": "",
            "fields_of_study": [],
            "skills_and_expertise": [],
            "publications": [],
            "followers": 0,
            "following": 0,
            "h_index": None,
            "total_reads": 0,
            "total_citations": 0,
        }
        return

    # Live mode — use Browserbase CDP
    from sruth.browser import scrape_researchgate_profile

    data = scrape_researchgate_profile(profile_url)
    data["profile_id"] = profile_id
    data["stream_id"] = stream_id
    data["owner_display_name"] = owner_display_name
    data["source_url"] = profile_url
    data["extraction_mode"] = "live"
    yield data


def run_researchgate_pipeline(
    profile_url: str,
    stream_id: str,
    owner_display_name: str = "",
    destination: str | Any | None = None,
    dataset_name: str = "researchgate_data",
    use_mock: bool = True,
) -> Any:
    """Run the full ResearchGate profile ingestion pipeline."""
    if destination is None:
        from dlt_utils import get_dlt_destination
        destination = get_dlt_destination()

    pipeline = dlt.pipeline(
        pipeline_name="researchgate_croilar",
        destination=destination,
        dataset_name=dataset_name,
        progress="log",
    )

    return pipeline.run([
        researchgate_profile_resource(profile_url, stream_id, owner_display_name, use_mock)
    ])
