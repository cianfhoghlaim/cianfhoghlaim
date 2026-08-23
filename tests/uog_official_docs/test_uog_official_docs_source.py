"""Tests for the UoG official docs DLT source."""

from __future__ import annotations


def test_source_yields_5_resources():
    """GIVEN the uog_official_docs_source() factory
    WHEN it is constructed
    THEN it emits exactly 5 resource names."""
    from dlt_sources.british_isles.ireland.education.university.official_docs import (
        uog_official_docs_source,
    )

    source = uog_official_docs_source()
    resource_names = {r.name for r in source.selected_resources.values()}
    assert resource_names == {
        "official_documents",
        "key_pages",
        "url_discovery_log",
        "academic_register",
        "exam_board_minutes",
    }


def test_each_resource_yields_fixture_row_when_no_credentials():
    """GIVEN the Firecrawl audit credentials are fixture-only
    WHEN the source runs
    THEN every resource yields a single skipped_fixture row."""
    from dlt_sources.british_isles.ireland.education.university.official_docs import (
        uog_official_docs_source,
    )

    # Create a fresh source per test to avoid dlt's "parametrised
    # resource callable only once" exception.
    source = uog_official_docs_source()
    for name in (
        "official_documents",
        "key_pages",
        "url_discovery_log",
        "academic_register",
        "exam_board_minutes",
    ):
        rows = list(source.selected_resources[name]())
        assert len(rows) >= 1, f"resource {name} yielded no rows"
        for row in rows:
            assert row.get("status") == "skipped_fixture"


def test_uog_official_homempages_lists_5_homepages():
    from dlt_sources.british_isles.ireland.education.university.official_docs import (
        UOG_OFFICIAL_HOMEPAGES,
    )

    assert len(UOG_OFFICIAL_HOMEPAGES) == 5
    for url in UOG_OFFICIAL_HOMEPAGES:
        assert url.startswith("https://www.universityofgalway.ie")
