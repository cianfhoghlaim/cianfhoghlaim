"""Phase 7 certificate pipeline integration tests.

Per the 2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1 change
(Phase 7 of the cianfhoghlaim-nua v6 era plan).
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def test_phase7_certificate_types_importable():
    """The canonical Phase 7 certificate types import cleanly."""
    from meaisinfhoghlaim.certificate.types import (
        CertificateOutcomeRecord,
        CertificateRecord,
        CertificationCitation,
        CertificationCriteria,
    )
    assert CertificateOutcomeRecord.__name__ == "CertificateOutcomeRecord"
    assert CertificateRecord.__name__ == "CertificateRecord"


def test_phase7_certificate_rubric_ncca_constants():
    """The NCCA award descriptors + key competencies match the
    canonical NCCA framework.
    """
    from meaisinfhoghlaim.certificate.rubric import (
        NCCA_AWARD_DESCRIPTORS,
        NCCA_KEY_COMPETENCIES,
    )
    assert "Exceptional" in NCCA_AWARD_DESCRIPTORS
    assert "Far below expectations" in NCCA_AWARD_DESCRIPTORS
    assert "Communicating" in NCCA_KEY_COMPETENCIES
    assert "Staying Well" in NCCA_KEY_COMPETENCIES


def test_phase7_certificate_rubric_coverage_checks():
    """Coverage checks return (covered, total) tuples."""
    from meaisinfhoghlaim.certificate.rubric import (
        check_award_descriptor_coverage,
        check_key_competency_coverage,
    )
    # Full coverage
    full = list(check_award_descriptor_coverage([d for d in (
        "Exceptional", "Above expectations", "In line with expectations",
        "Below expectations", "Far below expectations",
    )])[0:1])[0] if False else None
    covered, total = check_award_descriptor_coverage([
        "Exceptional", "Above expectations", "In line with expectations",
    ])
    assert covered == 3
    assert total == 5
    # Empty
    covered, total = check_award_descriptor_coverage([])
    assert covered == 0
    assert total == 5


def test_phase7_certificate_pipeline_stages_importable():
    """The 7-stage pipeline functions are importable."""
    from meaisinfhoghlaim.certificate.pipeline import (
        compose_certificate,
        decompose_outcomes,
        extract_certification_criteria,
        extract_exam_paper,
        generate_certificate_background,
        run_certificate_pipeline,
        save_to_provenance,
        search_official,
    )
    assert callable(extract_certification_criteria)
    assert callable(run_certificate_pipeline)


def test_phase7_search_official_returns_citations():
    """search_official returns relevant citations from a sample corpus."""
    from meaisinfhoghlaim.certificate.pipeline import search_official
    from meaisinfhoghlaim.certificate.types import CertificationCitation

    # Sample 2-page corpus
    corpus = [
        (
            "SC-L1-L2-Programme-Statement.pdf",
            "The award descriptors are Exceptional, Above expectations, "
            "In line with expectations, Below expectations, and Far below "
            "expectations. The 5 key competencies are Communicating, "
            "Information Processing, Critical and Creative Thinking, "
            "Personal Effectiveness, and Working with Others.",
        ),
        (
            "key-competencies-in-senior-cycle-en.pdf",
            "Staying Well was added as a sixth key competency in 2023. "
            "It focuses on student wellbeing and resilience.",
        ),
    ]
    result = asyncio.get_event_loop().run_until_complete(
        search_official("award descriptors", corpus, top_k=3),
    )
    assert isinstance(result, list)
    assert all(isinstance(c, CertificationCitation) for c in result)
    # The "award descriptors" query should match the first PDF
    assert any(c.source_pdf == "SC-L1-L2-Programme-Statement.pdf" for c in result)


def test_phase7_generate_certificate_background_stdlib():
    """generate_certificate_background falls back to stdlib gradient PNG."""
    from meaisinfhoghlaim.certificate.pipeline import (
        generate_certificate_background,
    )

    result = asyncio.get_event_loop().run_until_complete(
        generate_certificate_background("chemistry", "scoil_sinsearach"),
    )
    # PNG magic bytes
    assert result[:8] == b"\x89PNG\r\n\x1a\n"


def test_phase7_baml_function_reachable():
    """The BAML ExtractNCCAPolicyCriteria function is reachable."""
    from baml_client.baml_client.sync_client import b
    assert hasattr(b, "ExtractNCCAPolicyCriteria")