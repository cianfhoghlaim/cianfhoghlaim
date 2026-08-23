"""Tests for the Cognee `UoGExamPaper-COVERS-UoGModuleDescriptor` rule.

Reference: scripts/graph_storage/cognify/rules/uog_exam_cross_archive.py
"""

from __future__ import annotations


def test_text_overlap_ratio_perfect():
    from scripts.graph_storage.cognify.rules.uog_exam_cross_archive import (
        _text_overlap_ratio,
    )

    assert _text_overlap_ratio("backpropagation gradient descent", "gradient descent backpropagation") == 1.0


def test_text_overlap_ratio_zero_disjoint():
    from scripts.graph_storage.cognify.rules.uog_exam_cross_archive import (
        _text_overlap_ratio,
    )

    assert _text_overlap_ratio("transformer attention", "calculus integral") == 0.0


def test_text_overlap_ratio_handles_empty():
    from scripts.graph_storage.cognify.rules.uog_exam_cross_archive import (
        _text_overlap_ratio,
    )

    assert _text_overlap_ratio("", "transformer attention") == 0.0
    assert _text_overlap_ratio("transformer attention", "") == 0.0


def test_is_valid_module_code():
    from scripts.graph_storage.cognify.rules.uog_exam_cross_archive import (
        _is_valid_module_code,
    )

    # Valid UoG module codes span the 2-4 letter prefix x 3-4 digit suffix ranges.
    assert _is_valid_module_code("CT516") is True       # 2 letters + 3 digits
    assert _is_valid_module_code("MA335") is True       # 2 letters + 3 digits
    assert _is_valid_module_code("BCT1234") is True     # 3 letters + 4 digits
    assert _is_valid_module_code("EDUC100") is True     # 4 letters + 3 digits
    # Invalid
    assert _is_valid_module_code("ct516") is False      # uppercase only
    assert _is_valid_module_code("CT51") is False       # too few digits
    assert _is_valid_module_code("X") is False
    assert _is_valid_module_code("") is False
    assert _is_valid_module_code("CT-516") is False     # punctuation


def test_query_builder_returns_empty_for_invalid_inputs():
    from scripts.graph_storage.cognify.rules.uog_exam_cross_archive import (
        build_uog_exam_covers_module_query,
    )

    cypher, params = build_uog_exam_covers_module_query(
        exam_papers=[],
        module_descriptors=[],
    )
    assert cypher == ""
    assert params == {}


def test_query_builder_emits_cypher_for_matching_inputs():
    from scripts.graph_storage.cognify.rules.uog_exam_cross_archive import (
        build_uog_exam_covers_module_query,
    )

    papers = [
        {
            "module_code": "CT516",
            "academic_year": 2023,
            "sitting": "AUTUMN",
            "title": "CT516 — Deep Learning",
            "questions": [
                {"text": "derive the backpropagation algorithm"},
            ],
            "source_kind": "AUTH_PDF",
            "source_url": "https://exams.universityofgalway.ie/CT516/2023/AUT.pdf",
            "scraped_at": "2026-08-23T00:00:00Z",
        }
    ]
    modules = [
        {
            "module_code": "CT516",
            "academic_year": 2025,
            "learning_outcomes": [
                {"text": "derive backpropagation and discuss vanishing gradients"},
            ],
        }
    ]
    cypher, params = build_uog_exam_covers_module_query(papers, modules)
    assert "MERGE" in cypher
    assert "COVERS" in cypher
    assert params["papers"] == papers
    assert params["modules"] == modules


def test_query_builder_filters_invalid_module_codes():
    from scripts.graph_storage.cognify.rules.uog_exam_cross_archive import (
        build_uog_exam_covers_module_query,
    )

    papers = [{"module_code": "not-a-code", "academic_year": 0, "sitting": "AUTUMN", "questions": []}]
    modules = [{"module_code": "CT516", "academic_year": 2023, "learning_outcomes": []}]
    cypher, _params = build_uog_exam_covers_module_query(papers, modules)
    assert cypher == ""


def test_populate_returns_stub_when_no_inputs():
    """GIVEN no exam papers OR no module descriptors
    WHEN populate is called
    THEN it returns an empty stub without contacting FalkorDB."""
    from scripts.graph_storage.cognify.rules.uog_exam_cross_archive import (
        populate_uog_exam_covers_module,
    )

    result = populate_uog_exam_covers_module(
        exam_papers=[],
        module_descriptors=[],
    )
    assert result["queries_executed"] == 0
    assert result["edges_created"] == 0
    assert result["stub"] is False
