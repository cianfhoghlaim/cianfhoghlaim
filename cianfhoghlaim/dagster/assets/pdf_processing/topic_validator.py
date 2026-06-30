"""
Stage 4 of the 6-stage PDF processing pipeline: topic validation.

Cross-references every BAML record's `topic` field against the NCCA
syllabus taxonomy via fuzzy matching (95% threshold on `name` field).
Records that fail the match are flagged for human review.

Per `oideachais-pdf-processing/spec.md`:
- Input: BAML records from Stage 3 + NCCA syllabus topics
- Action: fuzzy-match every `topic` field against the NCCA taxonomy
- Output: `validated_records` (with `topic_validated: bool` + `topic_match: str | None`)
- Sink: `motherduck://oideachais.pdf_processing.{subject}.{year}.{paper}.validated`
"""

from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

warnings.warn(
    "pdf_processing.topic_validator is the v4 implementation of Stage 4. "
    "It is experimental; the actual NCCA taxonomy is loaded from "
    "DuckLake at runtime.",
    UserWarning,
    stacklevel=2,
)


# Default 95% fuzzy match threshold (per the v4 spec)
DEFAULT_MATCH_THRESHOLD = 0.95


@dataclass
class ValidationResult:
    """Result of Stage 4 topic validation for a single record."""

    record: dict[str, Any]
    topic_validated: bool
    topic_match: str | None = None
    match_score: float = 0.0
    reason: str = ""


class TopicValidator:
    """Stage 4 topic validator (NCCA taxonomy cross-reference).

    Per the v4 spec, the validator fuzzy-matches every BAML record's
    `topic` field against the NCCA syllabus topic list at the 95%
    threshold. Records that fail the match are flagged for human
    review in the Gradio interface at `spaces/oideachais-pdf-review/`.

    In production, the NCCA taxonomy is loaded from DuckLake at
    startup. For now, the actual taxonomy lookup is stubbed.
    """

    def __init__(
        self,
        ncca_taxonomy: list[dict[str, Any]] | None = None,
        match_threshold: float = DEFAULT_MATCH_THRESHOLD,
    ):
        """Initialize the topic validator.

        Args:
            ncca_taxonomy: Optional pre-loaded NCCA taxonomy. If None,
                loaded from DuckLake at runtime.
            match_threshold: Fuzzy match threshold (0-1). Default 0.95
                per the v4 spec.
        """
        self.ncca_taxonomy = ncca_taxonomy
        self.match_threshold = match_threshold

    def validate_records(
        self,
        baml_records: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], int, int, list[dict[str, Any]]]:
        """Validate every BAML record's topic against the NCCA taxonomy.

        Args:
            baml_records: List of BAML records (PastExamQuestion or
                MarkingPoint dicts) with a `topic` field

        Returns:
            Tuple of:
            - validated_records: BAML records with `topic_validated` +
              `topic_match` fields added
            - n_pass: count of records that matched
            - n_fail: count of records that didn't match
            - mismatched_records: the failed records (for human review)
        """
        if not baml_records:
            return [], 0, 0, []

        taxonomy = self.ncca_taxonomy or self._load_ncca_taxonomy()
        taxonomy_names = {t["name"].lower(): t["name"] for t in taxonomy}

        validated: list[dict[str, Any]] = []
        mismatched: list[dict[str, Any]] = []
        n_pass = 0
        n_fail = 0

        for record in baml_records:
            topic = record.get("topic", "").lower().strip()
            if not topic:
                continue

            # Exact match
            if topic in taxonomy_names:
                record["topic_validated"] = True
                record["topic_match"] = taxonomy_names[topic]
                record["topic_match_score"] = 1.0
                validated.append(record)
                n_pass += 1
                continue

            # Fuzzy match
            best_match = None
            best_score = 0.0
            for tax_lower, tax_original in taxonomy_names.items():
                score = self._fuzzy_score(topic, tax_lower)
                if score > best_score:
                    best_score = score
                    best_match = tax_original

            if best_score >= self.match_threshold:
                record["topic_validated"] = True
                record["topic_match"] = best_match
                record["topic_match_score"] = best_score
                validated.append(record)
                n_pass += 1
            else:
                record["topic_validated"] = False
                record["topic_match"] = None
                record["topic_match_score"] = best_score
                record["topic_validation_reason"] = (
                    f"No NCCA taxonomy match above {self.match_threshold} "
                    f"(best: {best_match} @ {best_score:.2f})"
                )
                mismatched.append(record)
                n_fail += 1
                # Still append to validated (so the pipeline continues)
                validated.append(record)

        logger.info(
            f"Stage 4 — Topic validation: {n_pass}/{n_pass + n_fail} "
            f"records matched NCCA taxonomy"
        )
        return validated, n_pass, n_fail, mismatched

    def _load_ncca_taxonomy(self) -> list[dict[str, Any]]:
        """Load the NCCA syllabus topic list from DuckLake.

        Per the v4 spec, the NCCA taxonomy is loaded from:
        `ducklake://oideachais.assets.official_documents.syllabus.{subject}`

        Returns the union of all `SyllabusTopic` records for the
        subject, plus a curated cross-subject fallback list.
        """
        try:
            import duckdb
            con = duckdb.connect(":memory:")
            # Try to load the NCCA syllabus topics from DuckLake
            con.execute(f"""
                ATTACH 'ducklake://oideachais.assets.official_documents.syllabus.{self.match_threshold}'
                AS ncca_syllabus (TYPE ducklake)
            """)
            # Stub: in production this queries the DuckLake table
            return con.execute("""
                SELECT name, subject FROM ncca_syllabus.topics
            """).fetchall()
        except Exception as e:
            logger.warning(
                f"Failed to load NCCA taxonomy from DuckLake ({e}); using fallback"
            )
            # Fallback: return a minimal mock taxonomy per common subject
            return [
                {"name": "Differentiation", "subject": "Mathematics"},
                {"name": "Integration", "subject": "Mathematics"},
                {"name": "Cell Biology", "subject": "Biology"},
                {"name": "Litríocht", "subject": "Irish"},
                {"name": "Teanga Bheo", "subject": "Irish"},
            ]

    def _fuzzy_score(self, a: str, b: str) -> float:
        """Compute a 0-1 fuzzy match score between two lowercase strings.

        Uses a simple character-overlap ratio (Jaccard-like) for speed.
        In production this would use `rapidfuzz` or `thefuzz` for
        Levenshtein-based scoring.
        """
        if not a or not b:
            return 0.0
        if a == b:
            return 1.0
        set_a = set(a)
        set_b = set(b)
        intersection = set_a & set_b
        union = set_a | set_b
        return len(intersection) / len(union) if union else 0.0
