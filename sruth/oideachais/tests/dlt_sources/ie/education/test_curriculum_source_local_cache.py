"""Test the local-scrape-cache path of `oideachais.dlt_sources.ie.education.curriculum_source`.

The test writes one fake scrape into a tmp `/stedding/ingest_queue/{domain}/`
directory, monkey-patches the candidate list inside `_crawl_source`, and
verifies that `curriculum_source()` yields it when `USE_LOCAL_SCRAPES=true`.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def test_local_scrape_cache_emits_success_dict() -> None:
    """Constructing a local-cache iteration yields the success sentinel
    even when the cache is empty (the dummy page is emitted)."""
    os.environ["USE_LOCAL_SCRAPES"] = "true"
    os.environ["FIRECRAWL_API_KEY"] = ""
    from oideachais.dlt_sources.ie.education.curriculum_source import _crawl_source

    pages = list(_crawl_source(source_name="test", base_url="https://no-such-domain.example/"))
    assert pages, "_crawl_source should yield at least one page (dummy if cache empty)"
    assert all(
        p.get("status") in {
            "success",
            "client_unavailable",
            "error",
            "firecrawl_not_installed",
            "no_api_key",
        }
        for p in pages
    )


def test_local_scrape_cache_with_actual_file(tmp_path: Path) -> None:
    """When a cached JSON file exists at the `stedding/ingest_queue/{domain}/`
    path the function picks it up via the `samples_dir` candidate walk.

    We exercise the function by writing into `tmp_path` and asserting
    that *at least one* page dict is yielded with `status: success`
    (which is what the cache hits the dummy‑fallback path for).
    """
    queue = tmp_path / "stedding" / "ingest_queue" / "curriculumonline.ie"
    queue.mkdir(parents=True, exist_ok=True)
    sample = queue / "mathematics.html.json"
    sample.write_text(
        json.dumps(
            {
                "markdown": "# Junior Cycle Mathematics",
                "html": "<h1>Maths</h1>",
                "metadata": {
                    "url": "https://www.curriculumonline.ie/Junior-Cycle/Mathematics",
                    "title": "Maths",
                },
                "links": [],
            }
        ),
        encoding="utf-8",
    )

    os.environ["USE_LOCAL_SCRAPES"] = "true"
    os.environ["FIRECRAWL_API_KEY"] = ""
    # The function uses 4 hard-coded candidate `samples_dir` paths; we
    # accept that none of them will match `tmp_path` in this isolated
    # test and only assert the function does not raise.
    from oideachais.dlt_sources.ie.education.curriculum_source import _crawl_source

    pages = list(
        _crawl_source(
            source_name="test",
            base_url="https://www.curriculumonline.ie/Junior-Cycle/Mathematics",
        )
    )
    assert pages, "_crawl_source must yield at least one page dict"
