"""Tests for the NUI federation DLT source."""

from __future__ import annotations


def test_nui_federation_lists_4_current_constituents():
    """GIVEN no Firecrawl creds
    WHEN the nui_members resource runs
    THEN 4 current constituents + 1 historical QUB member are emitted."""
    from dlt_sources.education.ireland.british_isles.university.official_docs import (
        nui_federation_source,
    )

    source = nui_federation_source()
    members_resource = next(
        r for r in source.selected_resources.values() if r.name == "nui_members"
    )
    rows = list(members_resource())
    current_members = [r for r in rows if r.get("kind") == "CONSTITUENT_UNIVERSITY"]
    historical = [r for r in rows if r.get("kind") == "HISTORICAL_MEMBER"]
    assert len(current_members) == 4
    assert len(historical) >= 1


def test_nui_historical_member_is_qub_pre_1908():
    """GIVEN the canonical NUI_HISTORICAL_MEMBERS seed
    WHEN the historical member is emitted
    THEN `member_name` mentions 'Queen's University Belfast'."""
    from dlt_sources.education.ireland.british_isles.university.official_docs import (
        NUI_HISTORICAL_MEMBERS,
    )

    qub = next(m for m in NUI_HISTORICAL_MEMBERS if "belfast" in m["member_name"].lower())
    assert qub["joined_nui_year"] == 1849
    assert qub["left_nui_year"] == 1908


def test_nui_constituent_circulars_emits_one_per_member():
    from dlt_sources.education.ireland.british_isles.university.official_docs import (
        NUI_CURRENT_CONSTITUENTS,
        nui_federation_source,
    )

    source = nui_federation_source()
    circulars_resource = next(
        r
        for r in source.selected_resources.values()
        if r.name == "nui_constituent_circulars"
    )
    rows = list(circulars_resource())
    assert len(rows) == len(NUI_CURRENT_CONSTITUENTS)


def test_nui_archive_lists_pre_1908_links():
    from dlt_sources.education.ireland.british_isles.university.official_docs import (
        nui_federation_source,
    )

    source = nui_federation_source()
    archive_resource = next(
        r for r in source.selected_resources.values() if r.name == "nui_archive"
    )
    rows = list(archive_resource())
    urls = [r["url"] for r in rows]
    assert any("qub" in u for u in urls)
    assert any("royal" in u for u in urls)
    assert any("queens_colleges" in u for u in urls)
