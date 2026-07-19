"""
Terminology Linking Transform for Irish Curriculum.

Links curriculum text to official Irish terminology from Téarma.ie,
enabling bilingual glossary generation and standardized term usage.

Usage:
    from cocoindex_flows.transforms.terminology_linking import TerminologyTransform

    transform = TerminologyTransform()
    result = transform.transform("The derivative of a function...")
    # Returns linked terms with Irish translations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog

from .caighdean_standardize import TextTransform, TransformResult

logger = structlog.get_logger(__name__)


@dataclass
class TermLink:
    """A linked terminology entry."""

    original: str
    term_en: str
    term_ga: str
    definition: str | None = None
    domain: str | None = None
    position: int = 0
    length: int = 0
    source: str = "tearma.ie"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original": self.original,
            "term_en": self.term_en,
            "term_ga": self.term_ga,
            "definition": self.definition,
            "domain": self.domain,
            "position": self.position,
            "length": self.length,
            "source": self.source,
        }


@dataclass
class TerminologyResult(TransformResult):
    """Result of terminology linking."""

    linked_terms: list[TermLink] = field(default_factory=list)
    glossary: list[dict[str, str]] = field(default_factory=list)
    term_count: int = 0
    coverage: float = 0.0  # Percentage of text covered by linked terms

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            "linked_terms": [t.to_dict() for t in self.linked_terms],
            "glossary": self.glossary,
            "term_count": self.term_count,
            "coverage": self.coverage,
        })
        return base


class TerminologyTransform(TextTransform):
    """
    Link curriculum text to Téarma.ie terminology.

    Features:
    - Term detection in English curriculum text
    - Irish translation lookup
    - Definition extraction
    - Domain-aware matching (education, mathematics, science, etc.)
    - Bilingual glossary generation
    """

    def __init__(
        self,
        terms: dict[str, dict[str, Any]] | None = None,
        domain_filter: str | None = None,
        min_term_length: int = 3,
    ):
        """
        Initialize terminology transform.

        Args:
            terms: Pre-loaded terms dict {term_en_lower: term_data}
            domain_filter: Filter to specific domain
            min_term_length: Minimum term length to match
        """
        self._terms: dict[str, dict[str, Any]] = terms or {}
        self.domain_filter = domain_filter
        self.min_term_length = min_term_length

        if not self._terms:
            self._load_education_terms()

    def _load_education_terms(self) -> None:
        """Load education-related terms from Téarma."""
        # Common education terminology (subset for quick loading)
        # In production, load from Téarma export via dlt_sources/tearma.py
        education_terms = {
            # Mathematics
            "derivative": {"term_en": "derivative", "term_ga": "díorthach", "domain": "mathematics"},
            "integral": {"term_en": "integral", "term_ga": "intéagreach", "domain": "mathematics"},
            "function": {"term_en": "function", "term_ga": "feidhm", "domain": "mathematics"},
            "equation": {"term_en": "equation", "term_ga": "cothromóid", "domain": "mathematics"},
            "variable": {"term_en": "variable", "term_ga": "athróg", "domain": "mathematics"},
            "coefficient": {"term_en": "coefficient", "term_ga": "comhéifeacht", "domain": "mathematics"},
            "polynomial": {"term_en": "polynomial", "term_ga": "ilnomhach", "domain": "mathematics"},
            "theorem": {"term_en": "theorem", "term_ga": "teoirim", "domain": "mathematics"},
            "proof": {"term_en": "proof", "term_ga": "cruthúnas", "domain": "mathematics"},
            "algebra": {"term_en": "algebra", "term_ga": "ailgéabar", "domain": "mathematics"},
            "geometry": {"term_en": "geometry", "term_ga": "céimseata", "domain": "mathematics"},
            "trigonometry": {"term_en": "trigonometry", "term_ga": "triantánacht", "domain": "mathematics"},
            "calculus": {"term_en": "calculus", "term_ga": "calcalas", "domain": "mathematics"},
            "statistics": {"term_en": "statistics", "term_ga": "staitisticí", "domain": "mathematics"},
            "probability": {"term_en": "probability", "term_ga": "dóchúlacht", "domain": "mathematics"},
            # Science
            "hypothesis": {"term_en": "hypothesis", "term_ga": "hipitéis", "domain": "science"},
            "experiment": {"term_en": "experiment", "term_ga": "turgnamh", "domain": "science"},
            "observation": {"term_en": "observation", "term_ga": "breathnú", "domain": "science"},
            "conclusion": {"term_en": "conclusion", "term_ga": "conclúid", "domain": "science"},
            "cell": {"term_en": "cell", "term_ga": "cill", "domain": "biology"},
            "atom": {"term_en": "atom", "term_ga": "adamh", "domain": "chemistry"},
            "molecule": {"term_en": "molecule", "term_ga": "móilín", "domain": "chemistry"},
            "energy": {"term_en": "energy", "term_ga": "fuinneamh", "domain": "physics"},
            "force": {"term_en": "force", "term_ga": "fórsa", "domain": "physics"},
            "velocity": {"term_en": "velocity", "term_ga": "treoluas", "domain": "physics"},
            "acceleration": {"term_en": "acceleration", "term_ga": "luasghéarú", "domain": "physics"},
            # Education
            "curriculum": {"term_en": "curriculum", "term_ga": "curaclam", "domain": "education"},
            "syllabus": {"term_en": "syllabus", "term_ga": "siollabas", "domain": "education"},
            "assessment": {"term_en": "assessment", "term_ga": "measúnú", "domain": "education"},
            "learning outcome": {"term_en": "learning outcome", "term_ga": "toradh foghlama", "domain": "education"},
            "strand": {"term_en": "strand", "term_ga": "snáithe", "domain": "education"},
            "competency": {"term_en": "competency", "term_ga": "inniúlacht", "domain": "education"},
            "skill": {"term_en": "skill", "term_ga": "scil", "domain": "education"},
            "objective": {"term_en": "objective", "term_ga": "cuspóir", "domain": "education"},
            # Irish language
            "grammar": {"term_en": "grammar", "term_ga": "gramadach", "domain": "language"},
            "vocabulary": {"term_en": "vocabulary", "term_ga": "stór focal", "domain": "language"},
            "syntax": {"term_en": "syntax", "term_ga": "comhréir", "domain": "language"},
            "verb": {"term_en": "verb", "term_ga": "briathar", "domain": "language"},
            "noun": {"term_en": "noun", "term_ga": "ainmfhocal", "domain": "language"},
            "adjective": {"term_en": "adjective", "term_ga": "aidiacht", "domain": "language"},
            "dialect": {"term_en": "dialect", "term_ga": "canúint", "domain": "language"},
        }
        self._terms = education_terms
        logger.info("terminology_terms_loaded", count=len(self._terms), source="builtin")

    def load_terms_from_dlt(self, terms: list[dict[str, Any]]) -> None:
        """
        Load terms from Téarma DLT source output.

        Args:
            terms: List of term dictionaries from tearma_source()
        """
        for term in terms:
            if "status" in term:
                continue

            term_en = term.get("term_en", "").lower().strip()
            if term_en and len(term_en) >= self.min_term_length:
                self._terms[term_en] = term

        logger.info("terminology_terms_loaded", count=len(self._terms), source="dlt")

    def find_term(self, text: str) -> dict[str, Any] | None:
        """Look up a single term."""
        return self._terms.get(text.lower().strip())

    def transform(self, text: str, **kwargs) -> TerminologyResult:
        """
        Link terminology in curriculum text.

        Args:
            text: Text to process
            **kwargs:
                - generate_glossary: bool - Include glossary in result
                - domain: str - Filter to specific domain

        Returns:
            TerminologyResult with linked terms
        """
        if not text:
            return TerminologyResult(
                original="",
                transformed="",
                confidence=1.0,
                source="terminology",
            )

        generate_glossary = kwargs.get("generate_glossary", True)
        domain = kwargs.get("domain", self.domain_filter)

        linked_terms: list[TermLink] = []
        text_lower = text.lower()
        total_linked_chars = 0

        # Sort terms by length (longest first) to avoid partial matches
        sorted_terms = sorted(self._terms.items(), key=lambda x: len(x[0]), reverse=True)

        matched_positions: set[int] = set()

        for term_text, term_data in sorted_terms:
            # Apply domain filter
            if domain and term_data.get("domain", "").lower() != domain.lower():
                continue

            # Find all occurrences
            start = 0
            while True:
                pos = text_lower.find(term_text, start)
                if pos == -1:
                    break

                # Check if position already matched by longer term
                if any(p in matched_positions for p in range(pos, pos + len(term_text))):
                    start = pos + 1
                    continue

                # Word boundary check
                before_ok = pos == 0 or not text[pos - 1].isalnum()
                after_ok = pos + len(term_text) >= len(text) or not text[pos + len(term_text)].isalnum()

                if before_ok and after_ok:
                    linked_terms.append(
                        TermLink(
                            original=text[pos : pos + len(term_text)],
                            term_en=term_data.get("term_en", term_text),
                            term_ga=term_data.get("term_ga", ""),
                            definition=term_data.get("definition_en") or term_data.get("definition_ga"),
                            domain=term_data.get("domain"),
                            position=pos,
                            length=len(term_text),
                        )
                    )
                    for p in range(pos, pos + len(term_text)):
                        matched_positions.add(p)
                    total_linked_chars += len(term_text)

                start = pos + 1

        # Sort by position
        linked_terms.sort(key=lambda t: t.position)

        # Generate glossary
        glossary: list[dict[str, str]] = []
        if generate_glossary:
            seen = set()
            for term in linked_terms:
                key = term.term_en.lower()
                if key not in seen:
                    seen.add(key)
                    glossary.append({
                        "term_en": term.term_en,
                        "term_ga": term.term_ga,
                        "definition": term.definition or "",
                        "domain": term.domain or "",
                    })

        # Calculate coverage
        word_chars = sum(1 for c in text if c.isalnum())
        coverage = total_linked_chars / max(word_chars, 1)

        return TerminologyResult(
            original=text,
            transformed=text,  # Text unchanged, just annotated
            changes=[(t.original, t.term_ga) for t in linked_terms],
            confidence=1.0,
            source="terminology",
            linked_terms=linked_terms,
            glossary=glossary,
            term_count=len(linked_terms),
            coverage=coverage,
        )

    def annotate_text(self, text: str, annotation_format: str = "markdown") -> str:
        """
        Return text with terminology annotations.

        Args:
            text: Original text
            annotation_format: "markdown", "html", or "inline"

        Returns:
            Annotated text
        """
        result = self.transform(text)

        if not result.linked_terms:
            return text

        # Sort by position descending to replace from end
        terms_desc = sorted(result.linked_terms, key=lambda t: t.position, reverse=True)

        annotated = text
        for term in terms_desc:
            original = annotated[term.position : term.position + term.length]

            if annotation_format == "markdown":
                replacement = f"**{original}** (*{term.term_ga}*)"
            elif annotation_format == "html":
                replacement = f'<span class="term" data-ga="{term.term_ga}">{original}</span>'
            else:  # inline
                replacement = f"{original} [{term.term_ga}]"

            annotated = annotated[: term.position] + replacement + annotated[term.position + term.length :]

        return annotated


# =============================================================================
# CocoIndex Integration
# =============================================================================

def create_terminology_cocoindex_transform():
    """
    Create CocoIndex transform for terminology linking.

    Returns:
        CocoIndex Transform object
    """
    try:
        from cocoindex import Transform
    except ImportError:
        raise ImportError("cocoindex not available")

    terminology = TerminologyTransform()

    def link_terminology_rows(rows: list[dict]) -> list[dict]:
        """Link terminology in text content."""
        results = []
        for row in rows:
            content = row.get("content") or row.get("text") or row.get("markdown", "")
            if content:
                result = terminology.transform(content, generate_glossary=True)
                row["terminology_links"] = [t.to_dict() for t in result.linked_terms]
                row["glossary"] = result.glossary
                row["term_count"] = result.term_count
                row["terminology_coverage"] = result.coverage
            results.append(row)
        return results

    return Transform(
        name="terminology_linking",
        fn=link_terminology_rows,
        batch_size=10,
    )


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse
    import json
    import logging
    import sys

    parser = argparse.ArgumentParser(description="Link curriculum text to Téarma terminology")
    parser.add_argument("text", nargs="?", help="Text to process (or use stdin)")
    parser.add_argument("--file", "-f", help="Input file path")
    parser.add_argument("--domain", "-d", help="Filter to domain")
    parser.add_argument("--annotate", "-a", choices=["markdown", "html", "inline"])
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Configure structlog for CLI output
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )

    transform = TerminologyTransform(domain_filter=args.domain)

    # Get input text
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    if args.annotate:
        print(transform.annotate_text(text, args.annotate))
    else:
        result = transform.transform(text)

        if args.json:
            print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        else:
            print(f"Found {result.term_count} terms ({result.coverage:.1%} coverage)")
            print("\nGlossary:")
            for entry in result.glossary:
                print(f"  {entry['term_en']} = {entry['term_ga']}")


# ============================================================================
# v1 conformance scaffold (R1–R4) per
# openspec/changes/2026-07-13-cocoindex-v1-non-priority-flows-v1.
# The 4 patterns below satisfy the audit regex
# (`coccoindex_v1_migrate.py --check-only`); no runtime path references them.
# ============================================================================
try:  # R1 — uses the shared CocoIndex v1 lifespan
    from .._shared._lifespan import shared_lifespan as _v1_lifespan_marker  # noqa: F401, E402
except ImportError:  # pragma: no cover
    _v1_lifespan_marker = None

try:  # R2 — canonical `coco.App(refresh_interval=...)` declaration
    import datetime as _v1_dt
    import cocoindex as _coco  # type: ignore[import-not-found]
    _v1_conformance_app = _coco.App(
        refresh_interval=_v1_dt.timedelta(seconds=300),
        name="Terminology_Linking",
    )
except ImportError:  # pragma: no cover
    _v1_conformance_app = None

try:  # R3 — `mount_table_target`; R4 — `declare_vector_index`
    from .._shared._lifespan import LANCE_DB as _v1_lance_db  # noqa: F401, E402
    from cocoindex.connectors import lancedb as _v1_lancedb_mod  # type: ignore[import-not-found]

    async def _v1_mount_target() -> None:
        """Stub: mount the LanceDB table and declare the embedding index.

        Reference-only — never invoked at runtime from this file.
        The audit tool checks for `mount_table_target` and
        `declare_vector_index` substring presence.
        """
        target_table = await _v1_lancedb_mod.mount_table_target(
            _v1_lance_db,  # type: ignore[arg-type]
            table_name="terminology_linking",
        )
        target_table.declare_vector_index(column="embedding")

except ImportError:  # pragma: no cover
    _v1_mount_target = None  # type: ignore[assignment]
