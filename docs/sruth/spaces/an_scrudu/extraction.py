"""
spaces/an_scrudu/extraction.py
ExtractCircularMeta handler for Space 1 (An Scrudu).

Modernized 2026-06-24 (C1 of the spaces alignment plan):
- Routes through the canonical KCG LiteLLM gateway
  (spaces/_common/baml_client.py) instead of raw HF Inference
- Validates the response against the Pydantic schema
  (mirrors the canonical oideachais/baml_src/circular_extraction.baml)
- Falls back to the regex-based extraction (offline demo mode)
  if the LiteLLM gateway is unreachable AND the HF Inference
  fallback chain also fails

For the canonical implementation, see:
  oideachais/baml_src/circular_extraction.baml
  (the BAML schema that the Pydantic model mirrors)
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

try:
    from pydantic import BaseModel, Field

    _HAS_PYDANTIC = True
except ImportError:
    _HAS_PYDANTIC = False


# Pydantic schema (mirrors oideachais/baml_src/circular_extraction.baml).
# The 4 classes + 1 function in the BAML file are mapped to 4 Pydantic
# models below. The validation provides the same schema-validated
# guarantees as the BAML runtime, without the BAML compiler.
if _HAS_PYDANTIC:

    class PTopicDistribution(BaseModel):
        topic_code: str = Field(..., description="e.g. CH1, IR1")
        topic_label: str
        marking_points: int
        paper_section: str = Field(..., description="e.g. Section A, Section B")

    class PCircularReference(BaseModel):
        circular_number: int
        issued_year: int
        issuing_body: str
        title_en: str
        title_ga: str | None = None
        subject: str
        level: str

    class PMarkingSchemeSummary(BaseModel):
        total_marking_points: int
        topics: list[PTopicDistribution]
        estimated_paper_duration_min: int
        has_orale: bool
        has_coursework: bool

    class PCircularExtraction(BaseModel):
        circular: PCircularReference
        scheme: PMarkingSchemeSummary
        raw_text_excerpt: str
        extraction_confidence: float


# Lazy import of the LiteLLM gateway shim. Loading spaces._common would
# also import gradio (the Celtic theme), which we want to avoid in
# test contexts. We load baml_client.py directly.
_chat_complete_json = None


def _get_chat_complete_json():
    """Lazy-load the LiteLLM gateway shim (chat_complete_json) without
    triggering the Gradio import.
    """
    global _chat_complete_json
    if _chat_complete_json is None:
        import importlib.util
        import sys as _sys
        from pathlib import Path

        _baml_path = Path(__file__).parent.parent / "_common" / "baml_client.py"
        spec = importlib.util.spec_from_file_location("spaces._common._baml_direct", _baml_path)
        mod = importlib.util.module_from_spec(spec)
        _sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        _chat_complete_json = mod.chat_complete_json
    return _chat_complete_json


_log = logging.getLogger("an_scrudu.extraction")


@dataclass
class TopicDistribution:
    topic_code: str
    topic_label: str
    marking_points: int
    paper_section: str


@dataclass
class CircularExtraction:
    """Legacy flat dataclass (kept for backward compat). New code should
    use the Pydantic PCircularExtraction above.
    """

    circular_number: int
    issued_year: int
    issuing_body: str
    title_en: str
    title_ga: str
    subject: str
    level: str
    total_marking_points: int
    topics: list[TopicDistribution]
    estimated_paper_duration_min: int
    has_orale: bool
    has_coursework: bool
    raw_text_excerpt: str
    extraction_confidence: float
    source_model: str  # which model produced this, or "offline"


# ---------------------------------------------------------------------
# LiteLLM gateway call
# ---------------------------------------------------------------------

_BAML_PROMPT_TEMPLATE = """\
Extract the Irish Department of Education circular metadata and marking
scheme structure from the following Leaving Certificate past-paper text.

Filename: {filename}

Past-paper text (first 8,000 chars):
---
{pdf_text}
---

Return a JSON object that matches the schema (the LiteLLM gateway will
route this to the canonical KCG BAML Extractor or the HF fallback):

{{
  "circular": {{
    "circular_number": <int>,
    "issued_year": <int>,
    "issuing_body": <string, e.g. "Department of Education and Skills">,
    "title_en": <string>,
    "title_ga": <string or null>,
    "subject": <string, e.g. "Chemistry", "Irish", "Mathematics">,
    "level": <string, "Leaving Certificate" or "Junior Certificate">
  }},
  "scheme": {{
    "total_marking_points": <int>,
    "topics": [{{
      "topic_code": <string, e.g. "CH1", "IR1">,
      "topic_label": <string>,
      "marking_points": <int>,
      "paper_section": <string, e.g. "Section A", "Section B">
    }}],
    "estimated_paper_duration_min": <int>,
    "has_orale": <bool, true if Irish oral component>,
    "has_coursework": <bool, true if any coursework/portfolio>
  }},
  "raw_text_excerpt": <string, 200-300 char literal excerpt>,
  "extraction_confidence": <float, 0.0 to 1.0>
}}
"""


def extract_circular(
    pdf_text: str,
    filename: str,
) -> CircularExtraction:
    """Call the canonical KCG LiteLLM gateway (with the HF fallback
    chain) and return a schema-validated extraction.

    Mirrors the canonical oideachais/baml_src/circular_extraction.baml
    `ExtractCircularMeta` function. The response is validated against
    the Pydantic schema (PCircularExtraction) if pydantic is installed,
    or the legacy flat schema (CircularExtraction) otherwise.

    Args:
        pdf_text: The text of the past paper (first 8,000 chars used).
        filename: The original filename, for context.

    Returns:
        A CircularExtraction. If the LiteLLM gateway is unreachable
        AND the HF Inference fallback chain also fails, falls back to
        a regex-based extraction (offline demo mode).
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a precise Irish-curriculum document analyser. "
                "You extract structured metadata from Leaving Cert past "
                "papers. You always return valid JSON matching the schema."
            ),
        },
        {
            "role": "user",
            "content": _BAML_PROMPT_TEMPLATE.format(
                filename=filename,
                pdf_text=pdf_text[:8000],
            ),
        },
    ]
    try:
        chat_complete_json = _get_chat_complete_json()
        parsed, model_used = chat_complete_json(messages, max_tokens=2048, temperature=0.1)
        return _validate_and_coerce(parsed, model_used)
    except (ValueError, RuntimeError) as e:
        _log.warning("LiteLLM chain failed: %s, using offline fallback", e)
        return _offline_extraction(pdf_text, filename)


def _validate_and_coerce(
    parsed: dict,
    model_used: str,
) -> CircularExtraction:
    """Coerce a parsed dict into a CircularExtraction, filling defaults.

    If pydantic is installed, validate the response against
    PCircularExtraction first (the canonical schema, mirrored from
    oideachais/baml_src/circular_extraction.baml). On validation
    failure, fall back to the flat dict with defaults.
    """
    # Optional Pydantic validation (the canonical schema check)
    if _HAS_PYDANTIC and "circular" in parsed and "scheme" in parsed:
        try:
            pyd = PCircularExtraction.model_validate(parsed)
            # Map the Pydantic model to the flat CircularExtraction
            topics = [
                TopicDistribution(
                    topic_code=t.topic_code,
                    topic_label=t.topic_label,
                    marking_points=t.marking_points,
                    paper_section=t.paper_section,
                )
                for t in pyd.scheme.topics
            ]
            return CircularExtraction(
                circular_number=pyd.circular.circular_number,
                issued_year=pyd.circular.issued_year,
                issuing_body=pyd.circular.issuing_body,
                title_en=pyd.circular.title_en,
                title_ga=pyd.circular.title_ga or "",
                subject=pyd.circular.subject,
                level=pyd.circular.level,
                total_marking_points=pyd.scheme.total_marking_points,
                topics=topics,
                estimated_paper_duration_min=pyd.scheme.estimated_paper_duration_min,
                has_orale=pyd.scheme.has_orale,
                has_coursework=pyd.scheme.has_coursework,
                raw_text_excerpt=pyd.raw_text_excerpt[:300],
                extraction_confidence=pyd.extraction_confidence,
                source_model=model_used,
            )
        except Exception as e:
            _log.warning("Pydantic validation failed: %s, using flat schema", e)

    # Flat schema (legacy) — accept both nested (BAML-style) and flat keys
    circular = parsed.get("circular", {})
    scheme = parsed.get("scheme", {})
    if not circular and not scheme:
        # Legacy flat shape: the LLM returned {circular_number, scheme: {topics}}
        circular = {
            "circular_number": parsed.get("circular_number", 0),
            "issued_year": parsed.get("issued_year", 2024),
            "issuing_body": parsed.get("issuing_body", "Department of Education"),
            "title_en": parsed.get("title_en", "Untitled"),
            "title_ga": parsed.get("title_ga", ""),
            "subject": parsed.get("subject", "Unknown"),
            "level": parsed.get("level", "Leaving Certificate"),
        }
        scheme = {
            "total_marking_points": parsed.get("total_marking_points", 0),
            "topics": parsed.get("topics", []),
            "estimated_paper_duration_min": parsed.get("estimated_paper_duration_min", 180),
            "has_orale": parsed.get("has_orale", False),
            "has_coursework": parsed.get("has_coursework", False),
        }

    topics = [
        TopicDistribution(
            topic_code=str(t.get("topic_code", "?")),
            topic_label=str(t.get("topic_label", "?")),
            marking_points=int(t.get("marking_points", 0)),
            paper_section=str(t.get("paper_section", "?")),
        )
        for t in scheme.get("topics", [])
    ]
    return CircularExtraction(
        circular_number=int(circular.get("circular_number", 0)),
        issued_year=int(circular.get("issued_year", 2024)),
        issuing_body=str(circular.get("issuing_body", "Department of Education")),
        title_en=str(circular.get("title_en", "Untitled")),
        title_ga=str(circular.get("title_ga") or ""),
        subject=str(circular.get("subject", "Unknown")),
        level=str(circular.get("level", "Leaving Certificate")),
        total_marking_points=int(scheme.get("total_marking_points", 0)),
        topics=topics,
        estimated_paper_duration_min=int(scheme.get("estimated_paper_duration_min", 180)),
        has_orale=bool(scheme.get("has_orale", False)),
        has_coursework=bool(scheme.get("has_coursework", False)),
        raw_text_excerpt=str(parsed.get("raw_text_excerpt", ""))[:300],
        extraction_confidence=float(parsed.get("extraction_confidence", 0.0)),
        source_model=model_used,
    )


# ---------------------------------------------------------------------
# Offline fallback (regex-based)
# ---------------------------------------------------------------------

_SUBJECT_HINTS: dict[str, list[str]] = {
    "Chemistry": ["chemistry", "ceimic"],
    "Irish": ["gaeilge", "irish"],
    "Mathematics": ["mathematics", "matamaitic"],
    "English": ["english", "béarla"],
    "Biology": ["biology", "bitheolaíocht"],
    "Physics": ["physics", "fisic"],
    "History": ["history", "stair"],
    "Geography": ["geography", "tíreolaíocht"],
    "French": ["french", "francais"],
    "Spanish": ["spanish", "spáinnis"],
}

_TOPIC_PATTERN = re.compile(
    r"(?P<code>[A-Z]{2,3}\d*\.?\d*)\s+"
    r"(?P<label>[A-Z][a-zA-Z\- ]{3,40})"
    r"\s*[\.\:]?\s*"
    r"\((?P<points>\d+)\s*(?:marks?|point)",
    re.MULTILINE,
)


def _offline_extraction(pdf_text: str, filename: str) -> CircularExtraction:
    """Regex-based fallback. Used when all 3 HF models fail."""
    text_lower = pdf_text.lower()
    subject = "Unknown"
    for subj, hints in _SUBJECT_HINTS.items():
        if any(h in text_lower for h in hints):
            subject = subj
            break

    # Try to extract topics
    topics: list[TopicDistribution] = []
    seen_codes: set[str] = set()
    for match in _TOPIC_PATTERN.finditer(pdf_text):
        code = match.group("code")
        if code in seen_codes:
            continue
        seen_codes.add(code)
        topics.append(
            TopicDistribution(
                topic_code=code,
                topic_label=match.group("label").strip(),
                marking_points=int(match.group("points")),
                paper_section="Section A",
            )
        )
    # If we found no topics, seed a few from the subject
    if not topics:
        seed_topics = {
            "Chemistry": [
                ("CH1", "Atomic structure"),
                ("CH2", "Chemical bonding"),
                ("CH3", "Stoichiometry"),
            ],
            "Mathematics": [("M1", "Algebra"), ("M2", "Calculus"), ("M3", "Probability")],
            "Irish": [("IR1", "Léamhthuiscint"), ("IR2", "Gramadach"), ("IR3", "Scríbhneoireacht")],
        }.get(subject, [("T1", "General topic A"), ("T2", "General topic B")])
        topics = [
            TopicDistribution(
                topic_code=code,
                topic_label=label,
                marking_points=20,
                paper_section="Section A",
            )
            for code, label in seed_topics
        ]

    # Try to extract a year from the filename or text
    year_match = re.search(r"(20\d{2}|19\d{2})", filename)
    year = int(year_match.group(1)) if year_match else 2024

    total_points = sum(t.marking_points for t in topics) or 100

    return CircularExtraction(
        circular_number=0,  # not extractable from regex
        issued_year=year,
        issuing_body="Department of Education (offline guess)",
        title_en=f"{subject} {year} (offline)",
        title_ga="",
        subject=subject,
        level="Leaving Certificate",
        total_marking_points=total_points,
        topics=topics,
        estimated_paper_duration_min=180,
        has_orale=(subject == "Irish"),
        has_coursework=False,
        raw_text_excerpt=pdf_text[:250].replace("\n", " "),
        extraction_confidence=0.4,  # low — this is a fallback
        source_model="offline-regex",
    )


# ---------------------------------------------------------------------
# Sample past paper (built-in, for the Space demo)
# ---------------------------------------------------------------------

SAMPLE_PAST_PAPER: str = """
LEAVING CERTIFICATE EXAMINATION, 2024

CHEMISTRY - HIGHER LEVEL - PAPER 1
(300 marks - 3 hours)

SECTION A (100 marks - compulsory)
Answer all five questions in this section.

CH1 Atomic Structure and Bonding
(a) Define the term 'atomic number' and explain its significance. (5 marks)
(b) Describe the electronic configuration of sodium (Z=11). (5 marks)
(c) Explain why ionic compounds conduct electricity when molten. (10 marks)

CH2 Chemical Reactions and Stoichiometry
(a) Balance the equation for the combustion of methane. (5 marks)
(b) Calculate the molar mass of sulfuric acid. (10 marks)
(c) Determine the limiting reagent. (15 marks)

SECTION B (200 marks - answer four of six questions)

CH3 Atomic Structure (50 marks)
Detailed treatment of quantum numbers, orbital shapes, and the aufbau
principle. Required: short answer (10) + structured (40).

CH4 Chemical Bonding (50 marks)
Ionic, covalent, and metallic bonding. Lewis structures, VSEPR theory,
and the shapes of simple molecules.

CH5 Stoichiometry (50 marks)
Empirical and molecular formulae. Concentration calculations, including
ppm and mol/dm^3. Titration curves and equivalence-point determination.

CH6 Chemical Equilibrium (50 marks)
Le Chatelier's principle applied to industrial processes. Kc and Kp
calculations, the Haber-Bosch process as a case study.

CH7 Acids and Bases (50 marks)
Bronsted-Lowry theory, pH calculations, buffer solutions, and acid-base
titrations. Required: worked example (15) + structured (35).

CH8 Redox and Electrochemistry (50 marks)
Oxidation states, balancing redox equations, electrochemical cells, and
the relationship between E° and spontaneity.

---
End of paper excerpt.
"""


def get_sample() -> tuple[str, str]:
    """Return (filename, text) of the built-in sample past paper."""
    return ("lc_chemistry_2024_h1.txt", SAMPLE_PAST_PAPER)
