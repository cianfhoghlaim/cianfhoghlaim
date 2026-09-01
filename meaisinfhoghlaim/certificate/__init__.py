"""meaisinfhoghlaim.certificate.__init__ — the LC/JC certificate pipeline.

Per the 2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1 change
(Phase 7 of the cianfhoghlaim-nua v6 era plan). The OSS replacement
for the GCP-first sister repo.
"""

from meaisinfhoghlaim.certificate.pipeline import (
    CertificateSaveResult,
    ExamPaperReference,
    compose_certificate,
    decompose_outcomes,
    extract_certification_criteria,
    extract_exam_paper,
    generate_certificate_background,
    run_certificate_pipeline,
    save_to_provenance,
    search_official,
)
from meaisinfhoghlaim.certificate.rubric import (
    NCCA_AWARD_DESCRIPTORS,
    NCCA_KEY_COMPETENCIES,
    check_award_descriptor_coverage,
    check_key_competency_coverage,
    compute_ssim,
)
from meaisinfhoghlaim.certificate.types import (
    CertificateOutcomeRecord,
    CertificateRecord,
    CertificationCitation,
    CertificationCriteria,
)

__all__ = [
    # types
    "CertificateOutcomeRecord",
    "CertificateRecord",
    "CertificationCitation",
    "CertificationCriteria",
    # rubric
    "NCCA_AWARD_DESCRIPTORS",
    "NCCA_KEY_COMPETENCIES",
    "compute_ssim",
    "check_award_descriptor_coverage",
    "check_key_competency_coverage",
    # pipeline
    "ExamPaperReference",
    "CertificateSaveResult",
    "extract_certification_criteria",
    "decompose_outcomes",
    "extract_exam_paper",
    "search_official",
    "generate_certificate_background",
    "compose_certificate",
    "save_to_provenance",
    "run_certificate_pipeline",
]