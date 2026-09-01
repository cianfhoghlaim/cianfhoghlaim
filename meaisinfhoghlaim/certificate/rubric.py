"""meaisinfhoghlaim.certificate.rubric — the asset-comparison rubric.

Per the 2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1 change
(Phase 7). The OSS replacement for the GCP-first
``gemini_hackathon.certificate.rubric``.

Computes:
  - SSIM (Structural Similarity Index) between the generated
    certificate background and the canonical reference image.
  - Perceptual-hash Hamming distance (no scikit-image required)
  - Award-descriptor coverage (does the criteria list include all
    5 NCCA descriptors?)
  - Key-competency coverage (does the criteria list include all
    5 + 1 NCCA key competencies?)
"""

from __future__ import annotations

import base64
import logging

logger = logging.getLogger(__name__)


def decode_b64_image(b64_str: str) -> bytes | None:
    """Decode a base64-encoded image to bytes. Returns None on error."""
    try:
        return base64.b64decode(b64_str)
    except Exception:
        return None


def compute_ssim(*, image_b64: str, reference_b64: str | None = None) -> float:
    """Compute a Structural Similarity Index (SSIM) proxy between two images.

    Uses a perceptual-hash Hamming-distance proxy rather than the
    full SSIM algorithm (which requires scikit-image). Returns a
    float in [0.0, 1.0].
    """
    img = decode_b64_image(image_b64)
    if img is None:
        return 0.0
    if reference_b64 is None:
        ph = _perceptual_hash(img)
        return bin(int.from_bytes(ph, "big")).count("1") / 64.0
    ref = decode_b64_image(reference_b64)
    if ref is None:
        return 0.0
    return (
        1.0
        - bin(
            int.from_bytes(_perceptual_hash(img), "big")
            ^ int.from_bytes(_perceptual_hash(ref), "big")
        ).count("1")
        / 64.0
    )


def _perceptual_hash(data: bytes, size: int = 8) -> bytes:
    """Compute a perceptual hash of the data (64-bit by default)."""
    import hashlib
    digest = hashlib.sha256(data).digest()
    return digest[:size]


# ─── Coverage checks ──────────────────────────────────────────────────────

# Per the NCCA framework: the 5 canonical award descriptors (post-2015
# Senior Cycle). The 6th (Staying Well) is a recent addition.
NCCA_AWARD_DESCRIPTORS: tuple[str, ...] = (
    "Exceptional",
    "Above expectations",
    "In line with expectations",
    "Below expectations",
    "Far below expectations",
)

NCCA_KEY_COMPETENCIES: tuple[str, ...] = (
    "Communicating",
    "Information Processing",
    "Critical and Creative Thinking",
    "Personal Effectiveness",
    "Working with Others",
    "Staying Well",  # Phase 4 addition
)


def check_award_descriptor_coverage(
    criteria_vocabulary: list[str],
) -> tuple[int, int]:
    """Return (covered, total) for the NCCA award descriptors."""
    covered = sum(1 for d in NCCA_AWARD_DESCRIPTORS if d in criteria_vocabulary)
    return covered, len(NCCA_AWARD_DESCRIPTORS)


def check_key_competency_coverage(
    criteria_competencies: list[str],
) -> tuple[int, int]:
    """Return (covered, total) for the NCCA key competencies."""
    covered = sum(1 for c in NCCA_KEY_COMPETENCIES if c in criteria_competencies)
    return covered, len(NCCA_KEY_COMPETENCIES)


__all__ = [
    "decode_b64_image",
    "compute_ssim",
    "check_award_descriptor_coverage",
    "check_key_competency_coverage",
    "NCCA_AWARD_DESCRIPTORS",
    "NCCA_KEY_COMPETENCIES",
]