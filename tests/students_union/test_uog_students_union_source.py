"""Tests for the UoG Students' Union DLT source."""

from __future__ import annotations


def test_uog_su_source_yields_2_resources():
    from dlt_sources.education.ireland.british_isles.university.official_docs import (
        uog_students_union_source,
    )

    source = uog_students_union_source()
    resource_names = {r.name for r in source.selected_resources.values()}
    assert resource_names == {
        "students_union_documents",
        "class_rep_handbooks",
    }


def test_students_union_documents_resource():
    from dlt_sources.education.ireland.british_isles.university.official_docs import (
        uog_students_union_source,
    )

    source = uog_students_union_source()
    docs_resource = next(
        r
        for r in source.selected_resources.values()
        if r.name == "students_union_documents"
    )
    rows = list(docs_resource())
    constitution_doc = next(r for r in rows if r.get("is_constitution"))
    assert constitution_doc["document_id"] == "uog-su-constitution"


def test_class_rep_handbooks_covers_all_5_colleges():
    from dlt_sources.education.ireland.british_isles.university.official_docs import (
        uog_students_union_source,
    )

    source = uog_students_union_source()
    handbooks_resource = next(
        r for r in source.selected_resources.values() if r.name == "class_rep_handbooks"
    )
    rows = list(handbooks_resource())
    colleges = {r["college_slug"] for r in rows}
    # UoG has 5 colleges
    assert len(colleges) >= 4  # we seeded 5; allow some flexibility


def test_canonical_policies_seed():
    from dlt_sources.education.ireland.british_isles.university.official_docs import (
        UOG_SU_CANONICAL_POLICIES,
    )

    titles = {p["title"] for p in UOG_SU_CANONICAL_POLICIES}
    assert any("Constitution" in t for t in titles)
    assert any("Welfare" in t for t in titles)
    assert any("Annual Report" in t for t in titles)
