"""meaisinfhoghlaim.certificate — the LC/JC certificate pipeline (Phase 7, OSS-first).

The end-to-end pipeline that produces an official-style Leaving Certificate
(LC) or Junior Certificate (JC) certificate for a learner, grounded
in the 5 NCCA policy documents + the learner's mastery ledger.

Lifted + OSS-ified from
``~/dev/gemini_hackathon/gemini_hackathon/certificate/`` (the GCP-first
sister repo). The Phase 7 lift replaces GCP-only components
(Firestore + Flux + Imagen3) with OSS alternatives (Convex +
diffusiongemma + flux_schnell or fibo).

7 stages:

  1. ExtractCertificationCriteria — BAML extraction of the official
     certification criteria from the 5 NCCA PDFs.
  2. DecomposeOutcomes — split the learner's request into per-outcome
     parts.
  3. ExtractExamPaper + ExtractMarking — pull the relevant exam paper
     + marking scheme from the canonical data/ireland/ corpus.
  4. SearchOfficial — RAG over the 5 NCCA PDFs (the policy corpus).
  5. GenerateCertificateBackground — flux_schnell or fibo
     (subject × stage → visual prompt; OSS instead of Imagen3).
  6. ComposeCertificate — PIL: background + text overlay + seal
     + competency strip + provenance footer.
  7. SaveToProvenance — write the result to Convex + the mastery-vector
     store + markdown memory (the OSS replacement for Firestore).

The output is a CertificateRecord with:
  - learner_id + name + subject + stage
  - The certificate image (PNG bytes)
  - The PDF export (PDF bytes)
  - The full provenance footer (every cited page)
  - The skill-progression summary

Per the canonical NCCA contract: every claim on every certificate
cites a page from one of the 5 NCCA policy PDFs. The "UNOFFICIAL"
banner is always present (never an NCCA-issued credential).

Per the 2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1 change
(Phase 7 of the cianfhoghlaim-nua v6 era plan).
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CertificationCitation:
    """A single citation to a page in one of the 5 NCCA policy PDFs.

    Every claim on every generated certificate carries at least one of these.
    """

    source_pdf: str  # filename (e.g. "SC-L1-L2-Programme-Statement.pdf")
    page: int  # 1-indexed
    quote: str  # verbatim text from the page
    relevance: str  # 1-sentence explanation of how this page informed the claim


@dataclass(frozen=True)
class CertificationCriteria:
    """The official certification criteria (extracted from the 5 NCCA PDFs)."""

    stage: str  # "aistear" / "bunscoil" / "meanscoil" / "scoil_sinsearach" / "ollscoil"
    subject_slug: str
    award_descriptor: str  # NCCA descriptor (e.g. "Exceptional", "Above expectations")
    descriptor_vocabulary: list[str]  # the 4-6 canonical descriptors
    key_competencies: list[str]  # the 5 (or 6 with Staying Well) NCCA Key Competencies
    policy_citations: list[CertificationCitation]  # every cited page


@dataclass
class CertificateOutcomeRecord:
    """One learning-outcome mastery record that's on the certificate."""

    outcome_code: str  # e.g. "MA-LC-CH-2.1"
    subject_slug: str
    descriptor: str  # 1-line description
    mastery_score: float  # 0.0-1.0
    key_competency_codes: list[str] = field(default_factory=list)
    ncca_policy_citations: list[CertificationCitation] = field(default_factory=list)


@dataclass
class CertificateRecord:
    """The final certificate record produced by the pipeline.

    Contains everything needed to render the certificate image + PDF
    + the provenance footer + the skill-progression summary.
    """

    learner_id: str
    learner_name: str
    subject_slug: str
    stage: str  # "aistear" / "bunscoil" / "meanscoil" / "scoil_sinsearach" / "ollscoil"
    # The rendered outputs
    png_bytes: bytes
    pdf_bytes: bytes
    # The certification metadata
    criteria: CertificationCriteria = field(default=None)  # type: ignore[assignment]
    outcomes: list[CertificateOutcomeRecord] = field(default_factory=list)
    policy_citations: list[CertificationCitation] = field(default_factory=list)
    # The skill-progression summary (from the MasteryLedger)
    learner_state_summary: dict[str, Any] = field(default_factory=dict)
    # Timestamp
    issued_at: str = field(default_factory=lambda: datetime.now().isoformat())


__all__ = [
    "CertificateOutcomeRecord",
    "CertificateRecord",
    "CertificationCitation",
    "CertificationCriteria",
]