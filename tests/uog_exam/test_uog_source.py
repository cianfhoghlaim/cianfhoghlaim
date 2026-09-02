"""Tests for the UoG DLT source in fixture-only mode.

The pipeline MUST short-circuit safely when no real Campus Identity
credentials are configured (the CI scenario). These tests cover that
contract.
"""

from __future__ import annotations

from sruth_browser.core.secrets import UoGSsoConfig


def test_uog_sso_config_is_fixture_only_by_default(monkeypatch):
    """Default CI env has `OOG_STUDENT_PASSWORD=fixture-only`."""
    monkeypatch.setenv("OOG_STUDENT_ID", "fixture-only")
    monkeypatch.setenv("OOG_STUDENT_PASSWORD", "fixture-only")
    cfg = UoGSsoConfig.from_resolver()
    assert cfg.has_real_credentials() is False


def test_dlt_source_yields_skipped_fixture_rows(monkeypatch, uog_fixture_modules):
    """With fixture-only credentials, every resource still yields one row.

    The resources may use either `status="scraped"` (a real
    scraper-fixture row) or `status="skipped_fixture"` (the empty
    sentinel) depending on whether the user passed explicit
    `modules=` or is relying on the auto-discovered whitelist.
    """
    from dlt_sources.education.ireland.british_isles.university.exam_papers import (
        uog_exam_papers_source,
    )

    monkeypatch.setenv("OOG_STUDENT_ID", "fixture-only")
    monkeypatch.setenv("OOG_STUDENT_PASSWORD", "fixture-only")

    source = uog_exam_papers_source(modules=uog_fixture_modules)
    resource_names = {"exam_papers", "marking_schemes", "model_solutions", "supplementary_papers", "all_exam_materials"}
    seen_resources = set()
    for resource in source.selected_resources.values():
        name = resource.name
        seen_resources.add(name)
        rows = list(resource())
        assert len(rows) >= 1, f"resource {name} yielded no rows"
        for row in rows:
            assert row.get("status") in {"scraped", "skipped_fixture"}
    assert seen_resources == resource_names


def test_msc_ai_source_with_no_credentials_yields_fixture_rows(monkeypatch):
    """The M.Sc. AI convenience source resolves fixture mode without
    raising. The actual rows are status="scraped" (the
    `_fixture_material` helper from the scraper)."""
    from dlt_sources.education.ireland.british_isles.university.exam_papers import (
        msc_ai_source,
    )

    monkeypatch.setenv("OOG_STUDENT_ID", "fixture-only")
    monkeypatch.setenv("OOG_STUDENT_PASSWORD", "fixture-only")

    source = msc_ai_source(years=[2023])
    exam_papers = next(
        (r for r in source.selected_resources.values() if r.name == "exam_papers"),
        None,
    )
    assert exam_papers is not None
    rows = list(exam_papers())
    assert len(rows) >= 1
    for r in rows:
        # In fixture mode we get either a skipped_fixture sentinel
        # (modules=[] case) or a scraper-issued row (modules=[..] case).
        assert r.get("status") in {"scraped", "skipped_fixture"}


def test_v1_school_whitelist_is_explicit():
    """The v1 source only touches the 6 whitelisted schools."""
    from dlt_sources.education.ireland.british_isles.university.exam_papers import (
        V1_SCHOOL_WHITELIST,
    )

    expected_schools = {
        "computer-science",
        "mathematical-statistical-sciences",
        "physics",
        "education",
        "business",
        "languages-literatures",
    }
    assert set(V1_SCHOOL_WHITELIST) == expected_schools
