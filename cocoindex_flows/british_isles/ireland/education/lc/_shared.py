"""cocoindex_flows.british_isles.ireland.education.lc._shared
-- the BIEP v3 per-subject shared scaffolding for the 6 Irish
Leaving Certificate subjects (Mathematics, Chemistry, Geography,
English, Gaeilge, Computer Science).

Scope
-----
This module is the single source of truth for the cross-subject
plumbing that the 6 per-subject CocoIndex v1 Apps
(`mathematics.py`, `chemistry.py`, `geography.py`, `english.py`,
`gaeilge.py`, `computer_science.py`) share. Keeping it in one
place is the BIEP v3 factory pattern (per the
`cocoindex_flows/AGENTS.md` factory-pattern section).

The 6 modules MUST follow the canonical BIEP v3 contract:
- R1: import `shared_lifespan` + `LANCE_DB` + `EMBEDDER` from
  `....._shared._lifespan`
- R3: declare `app = coco.App(coco.AppConfig(name=...))` at
  module scope (R3 enforced by `cocoindex_v1_conformance.py`)
- R4: at least one `@coco.fn(...)` decorator present

BAML status (per the kcg-runtime-inert-layers memory)
-----------------------------------------------------
The `baml_client/` generated client is currently unavailable
(`baml-cli generate --from baml_src` fails on duplicate class
definitions in `baml_src/_shared/templates/`). Each per-subject
module therefore declares a `_BAML_AVAILABLE = False` fallback
path that calls `python_baml_fallback_extract(subject_slug, text)`
below. Once the duplicate-class defect in `baml_src/` is
remediated and `baml_client/` regenerates, the per-subject
modules will automatically pick up the BAML path (the
`try: from baml_client.baml_client import b` import is the only
piece that needs to succeed).

Test status
-----------
`tests/biep_parity_lc/test_<subject>.py` exercises the full
load → embed → store → query pipeline against a 3-row fixture
per subject, using the `pure_python_embed` helper (a
deterministic numpy-based substitute for BGE-M3 that does not
require the SentenceTransformer model download). 6 pytests pass.

Reference
---------
- openspec/specs/british-isles-education-pipeline-v3/spec.md
  (the BIEP v3 umbrella spec; the per-subject changes add
   deltas to its 5-milestone Ireland-LC M1 milestone)
- openspec/specs/cianfhoghlaim-cocoindex-v1-migration/spec.md
  (the R1-R4 conformance contract)
- cocoindex_flows/subjects/lc_subject_embedding.py (the
  parameterised BIEP v1 app this layer refines for v3)
- cocoindex_flows/biep_parity/ireland_lc_factory.py (the
  BIEP v3 factory that this layer parallels for the
  per-subject openspec changes)
"""
from __future__ import annotations

import hashlib
import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# The 6 canonical BIEP v3 LC subjects (per lc_subject_config.yaml)
# ============================================================================

@dataclass(frozen=True)
class LCSubjectSpec:
    """The canonical per-subject configuration for one BIEP v3 LC subject.

    Per the `centralized-schema-registry` capability (post-2026-08-15),
    this row is the single source of truth for a subject's identity,
    BAML function name, table suffix, and language scope.
    """

    slug: str                     # the BIEP v3 slug (e.g. "mathematics")
    display_name: str             # English display name (e.g. "Mathematics")
    irish_display_name: str       # Irish-language display name (e.g. "Matamaitic")
    languages: tuple[str, ...]    # which languages to build Apps for
    baml_function: str            # the canonical BAML extraction function name
    table_suffix: str             # the per-subject LanceDB table suffix
    dagster_asset_key: str        # the canonical Dagster asset key


# The 6-row canonical NCCA LC subject table (post-v3 centralization).
# Preserved in dependency-order (Mathematics → Computer Science) for the
# openspec change numbering (pipeline-mathematics-v1 ... pipeline-computer-science-v1).
LC_SUBJECTS: tuple[LCSubjectSpec, ...] = (
    LCSubjectSpec(
        slug="mathematics",
        display_name="Mathematics",
        irish_display_name="Matamaitic",
        languages=("en", "ga"),
        baml_function="ExtractLCSyllabusMathematics",
        table_suffix="mathematics",
        dagster_asset_key="lc_mathematics_embedding",
    ),
    LCSubjectSpec(
        slug="chemistry",
        display_name="Chemistry",
        irish_display_name="Ceimic",
        languages=("en", "ga"),
        baml_function="ExtractLCSyllabusChemistry",
        table_suffix="chemistry",
        dagster_asset_key="lc_chemistry_embedding",
    ),
    LCSubjectSpec(
        slug="geography",
        display_name="Geography",
        irish_display_name="Tíreolaíocht",
        languages=("en", "ga"),
        baml_function="ExtractLCSyllabusGeography",
        table_suffix="geography",
        dagster_asset_key="lc_geography_embedding",
    ),
    LCSubjectSpec(
        slug="english",
        display_name="English",
        irish_display_name="Béarla",
        languages=("en", "ga"),
        baml_function="ExtractLCSyllabusEnglish",
        table_suffix="english",
        dagster_asset_key="lc_english_embedding",
    ),
    LCSubjectSpec(
        slug="gaeilge",
        display_name="Gaeilge",
        irish_display_name="Gaeilge",
        languages=("ga",),
        baml_function="ExtractLCSyllabusGaeilge",
        table_suffix="gaeilge",
        dagster_asset_key="lc_gaeilge_embedding",
    ),
    LCSubjectSpec(
        slug="computer_science",
        display_name="Computer Science",
        irish_display_name="Ríomheolaíocht",
        languages=("en", "ga"),
        baml_function="ExtractLCSyllabusComputerScience",
        table_suffix="computer_science",
        dagster_asset_key="lc_computer_science_embedding",
    ),
)


def get_subject_spec(slug: str) -> LCSubjectSpec:
    """Return the canonical LCSubjectSpec for a slug (e.g. "mathematics").

    Raises KeyError if the slug is not one of the canonical 6.
    """
    for spec in LC_SUBJECTS:
        if spec.slug == slug:
            return spec
    raise KeyError(
        f"Unknown BIEP v3 LC subject slug: {slug!r}. "
        f"Canonical slugs: {[s.slug for s in LC_SUBJECTS]}"
    )


# ============================================================================
# Pure-Python helpers (BAML fallback + embedder substitute + chunker)
# ============================================================================

# The default embedder dim matches EMBED_DIM in
# cocoindex_flows/_shared/_lifespan.py (BAAI/bge-m3 = 1024).
DEFAULT_EMBED_DIM = 1024


def pure_python_embed(text: str, dim: int = DEFAULT_EMBED_DIM) -> list[float]:
    """Deterministic 1024-d embedder substitute for tests.

    The real embedder is `BAAI/bge-m3` (1024-d, multilingual) per
    `cocoindex_flows/_shared/_lifespan.py:107`. We don't load the
    SentenceTransformer model in pytest (it's a 2.3 GB download),
    so we substitute a deterministic numpy-backed vector that:

    - Is seeded by SHA-256(text) (same text → same vector)
    - Returns a list of `dim` floats in roughly [-0.5, 0.5]
    - Round-trips through numpy ↔ list (so the LanceDB vector
      type contract is exercised)

    Not semantically meaningful — just exercises the pipeline
    shape so we know end-to-end wiring works. The production
    CocoIndex App uses `coco.use_context(EMBEDDER).embed(text)`
    directly; this is only used by the per-subject pytests.
    """
    try:
        import numpy as np

        h = hashlib.sha256(text.encode("utf-8")).digest()
        seed = int.from_bytes(h[:8], "big")
        rng = np.random.default_rng(seed)
        vec = (rng.standard_normal(dim).astype(np.float32) * 0.1).tolist()
        return vec
    except ImportError:
        # numpy not installed — degrade to a pure-python list (slower, but OK).
        h = hashlib.sha256(text.encode("utf-8")).digest()
        seed = int.from_bytes(h[:8], "big")
        rng_state = seed
        out: list[float] = []
        for _ in range(dim):
            rng_state = (rng_state * 1103515245 + 12345) & 0x7FFFFFFF
            out.append(((rng_state / 0x7FFFFFFF) - 0.5) * 0.1)
        return out


def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> list[str]:
    """Pure-Python recursive-style text splitter.

    Mirrors the canonical chunker behaviour used by
    `cocoindex.ops.text.RecursiveSplitter` (chunk_size=2000,
    overlap=200) — same defaults as the BIEP v3 factory's
    `_splitter.split(...)` call.
    """
    if not text or not text.strip():
        return []
    step = max(1, chunk_size - overlap)
    chunks: list[str] = []
    for i in range(0, len(text), step):
        chunk = text[i : i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
        if i + chunk_size >= len(text):
            break
    return chunks


# ============================================================================
# BAML fallback (per-subject keyword/regex extraction)
# ============================================================================

# Per-subject keyword maps for the Python BAML fallback. Each subject
# has a small dictionary of (regex, extracted_field) pairs that
# approximate what the BAML function would return. This is NOT a
# semantically rich extraction — it's a wiring test: if BAML is
# unavailable, the pipeline still produces a non-empty
# `extracted_fields` dict for each chunk, so the load → embed →
# store → query round-trip can be verified.

_PER_SUBJECT_KEYWORDS: dict[str, dict[str, re.Pattern[str]]] = {
    "mathematics": {
        "topic": re.compile(
            r"\b(algebra|calculus|geometry|trigonometry|statistics|probability|"
            r"complex\s+numbers|matrices|functions|sequences|series|"
            r"differentiation|integration|coordinate\s+geometry)\b",
            re.IGNORECASE,
        ),
        "level": re.compile(r"\b(Higher|Ordinary|Foundation)\b", re.IGNORECASE),
        "year": re.compile(r"\b(20\d{2})\b"),
    },
    "chemistry": {
        "topic": re.compile(
            r"\b(atomic\s+structure|periodic\s+table|bonding|stoichiometry|"
            r"acids\s+and\s+bases|redox|organic\s+chemistry|thermodynamics|"
            r"equilibrium|kinetics|electrochemistry)\b",
            re.IGNORECASE,
        ),
        "level": re.compile(r"\b(Higher|Ordinary|Foundation)\b", re.IGNORECASE),
        "year": re.compile(r"\b(20\d{2})\b"),
    },
    "geography": {
        "topic": re.compile(
            r"\b(tectonics|geomorphology|climate|weather|demography|"
            r"urban\s+geography|rural\s+geography|economic\s+geography|"
            r"globalisation|cultural\s+geography|environmental\s+geography)\b",
            re.IGNORECASE,
        ),
        "level": re.compile(r"\b(Higher|Ordinary|Foundation)\b", re.IGNORECASE),
        "year": re.compile(r"\b(20\d{2})\b"),
    },
    "english": {
        "topic": re.compile(
            r"\b(poetry|prose|drama|film|novel|short\s+story|drama|"
            r"comparative\s+study|composition|comprehension|literary\s+genre)\b",
            re.IGNORECASE,
        ),
        "level": re.compile(r"\b(Higher|Ordinary|Foundation)\b", re.IGNORECASE),
        "year": re.compile(r"\b(20\d{2})\b"),
    },
    "gaeilge": {
        "topic": re.compile(
            r"\b(gramadach|litríocht|filíocht|prós|drama|"
            r"comhrá|scríbhneoireacht|éisteacht|léamh|tuiscint|"
            r"saíocht|nuachlasaiceach)\b",
            re.IGNORECASE,
        ),
        "level": re.compile(r"\b(Ardleibhéal|Gnáthleibhéal|Bonnleibhéal)\b"),
        "year": re.compile(r"\b(20\d{2})\b"),
    },
    "computer_science": {
        "topic": re.compile(
            r"\b(algorithms|data\s+structures|programming|databases|"
            r"networking|operating\s+systems|software\s+engineering|"
            r"computational\s+thinking|boolean\s+logic|machine\s+learning)\b",
            re.IGNORECASE,
        ),
        "level": re.compile(r"\b(Higher|Ordinary|Foundation)\b", re.IGNORECASE),
        "year": re.compile(r"\b(20\d{2})\b"),
    },
}


def python_baml_fallback_extract(subject_slug: str, text: str) -> dict[str, Any]:
    """Python fallback for the per-subject BAML extraction function.

    Returns a dict matching the BAML function's return shape
    (minus the strictly-typed Pydantic wrapping). Each
    `_PER_SUBJECT_KEYWORDS[slug]` regex is applied to `text`;
    the union of all matches becomes the value of the field.
    Multiple matches → list. No matches → empty list.

    This is intentionally NOT semantically rich — it exists only
    so the per-subject pytest can exercise the full load →
    embed → store → query round-trip without needing the
    `baml_client/` generated module (which is currently
    unavailable per the kcg-runtime-inert-layers memory).

    Once `baml_client/` regenerates, the per-subject modules
    will use the real BAML function and this fallback will
    become dead code.
    """
    keywords = _PER_SUBJECT_KEYWORDS.get(subject_slug)
    if keywords is None:
        return {
            "subject": subject_slug,
            "extraction_source": "python_fallback_unknown_subject",
            "fields": {},
        }
    out: dict[str, Any] = {
        "subject": subject_slug,
        "extraction_source": "python_fallback",
        "fields": {},
    }
    for field_name, pattern in keywords.items():
        matches = sorted(set(m.group(0) for m in pattern.finditer(text)))
        out["fields"][field_name] = matches
    return out


# ============================================================================
# BAML availability probe
# ============================================================================

def baml_available() -> bool:
    """Return True iff the `baml_client.baml_client` module imports cleanly.

    Per the kcg-runtime-inert-layers memory (defect #3), the
    generated client is currently unavailable because
    `baml-cli generate --from baml_src` fails on duplicate class
    definitions in `baml_src/_shared/templates/`. Each per-subject
    module calls `baml_available()` once at module import time to
    decide whether to wire the BAML function or the Python
    fallback into its `_process` function.
    """
    try:
        from baml_client.baml_client import b  # noqa: F401

        return True
    except ImportError:
        return False


# ============================================================================
# Fixture builder (used by tests/biep_parity_lc/)
# ============================================================================

# The 6 canonical subjects, in the order the BIEP v3 milestones
# expect (Mathematics → ... → Computer Science).
SUBJECT_SLUGS: tuple[str, ...] = tuple(s.slug for s in LC_SUBJECTS)


def build_subject_fixture(
    subject_slug: str,
    num_rows: int = 5,
) -> list[dict[str, Any]]:
    """Build a small (≤ num_rows) fixture of mock LC subject documents.

    Each row is a dict with the shape the CocoIndex process
    function consumes: `{"filename": str, "text": str, "level": str,
    "language": str, "source_url": str}`. The `text` field is
    hand-written to be semantically aligned with the subject (so
    the BAML fallback extraction actually fires and produces a
    non-empty `fields` dict — exercising the full round-trip).

    Used by `tests/biep_parity_lc/test_<subject>.py` to exercise
    the load → embed → store → query pipeline end-to-end without
    needing real PDF downloads.
    """
    spec = get_subject_spec(subject_slug)
    language = "ga" if spec.languages == ("ga",) else "en"
    fixture: list[dict[str, Any]] = []

    # 5 per-subject snippets that exercise the keyword patterns
    # above (so the BAML fallback extraction is non-empty).
    snippets: dict[str, list[str]] = {
        "mathematics": [
            "Leaving Certificate Mathematics (Higher Level) — Algebra and Functions. "
            "Students study complex numbers, matrices, sequences, and series. "
            "Differentiation and integration form the core of calculus. "
            "Examination: 2024 Higher Level Paper 1.",
            "Ordinary Level Mathematics focuses on coordinate geometry, "
            "trigonometry, probability, and statistics. The 2023 exam included "
            "questions on sequences and series.",
            "Foundation Level Mathematics covers basic algebra, geometry, "
            "and arithmetic. Paper 2 (2022) tested statistics and probability.",
        ],
        "chemistry": [
            "Leaving Certificate Chemistry (Higher Level) — Atomic Structure and "
            "Periodic Table. Topics include bonding, stoichiometry, acids and "
            "bases, redox reactions, organic chemistry, thermodynamics, and "
            "equilibrium. 2024 Higher Level Paper 2.",
            "Ordinary Level Chemistry covers atomic structure, periodic table, "
            "bonding, and stoichiometry. Kinetics and electrochemistry form "
            "the practical component. 2023 Ordinary Level exam.",
            "Foundation Level Chemistry: acids and bases, redox, and basic "
            "organic chemistry. 2022 Foundation Level Paper 1.",
        ],
        "geography": [
            "Leaving Certificate Geography (Higher Level) — Tectonics, "
            "geomorphology, climate, weather, demography, urban geography, "
            "rural geography, economic geography. 2024 Higher Level exam.",
            "Ordinary Level Geography: globalisation, cultural geography, "
            "and environmental geography. The 2023 exam focused on "
            "globalisation and economic geography.",
            "Foundation Level Geography covers basic climate, weather, and "
            "demography. 2022 Foundation Paper 1.",
        ],
        "english": [
            "Leaving Certificate English (Higher Level) — Poetry, prose, drama, "
            "film, novel, short story, comparative study, composition, "
            "comprehension. The 2024 Higher Level exam focused on the "
            "comparative study.",
            "Ordinary Level English: poetry, prose, drama, composition, and "
            "comprehension. Literary genre is tested in the 2023 exam.",
            "Foundation Level English covers basic comprehension, composition, "
            "and short prose. 2022 Foundation Level Paper 1.",
        ],
        "gaeilge": [
            "Ardleibhéal Gaeilge — Gramadach, Litríocht, Filíocht, Prós, Drama. "
            "Spriocanna: éisteacht, léamh, tuiscint, scríbhneoireacht, comhrá. "
            "Scrúdú 2024 Ardleibhéal.",
            "Gnáthleibhéal Gaeilge: gramadach, litríocht, prós. Scrúdú 2023 "
            "Gnáthleibhéal.",
            "Bonnleibhéal Gaeilge: bungramadach, saíocht, nuachlasaiceach. "
            "Scrúdú 2022 Bonnleibhéal.",
        ],
        "computer_science": [
            "Leaving Certificate Computer Science (Higher Level) — Algorithms, "
            "data structures, programming, databases, networking, operating "
            "systems, software engineering, computational thinking, boolean "
            "logic, machine learning. 2024 Higher Level exam.",
            "Ordinary Level Computer Science: algorithms, data structures, "
            "programming, databases. The 2023 exam focused on boolean logic "
            "and computational thinking.",
            "Foundation Level Computer Science: basic algorithms, programming, "
            "and computational thinking. 2022 Foundation Paper 1.",
        ],
    }

    raw = snippets.get(subject_slug, [])
    for i in range(min(num_rows, len(raw))):
        text = raw[i]
        fixture.append(
            {
                "filename": f"{spec.dagster_asset_key}_fixture_{i:02d}.txt",
                "text": text,
                "level": "hl" if i == 0 else ("ol" if i == 1 else "fl"),
                "language": language,
                "source_url": f"fixture://lc/{subject_slug}/{language}/{i:02d}.txt",
                "subject": subject_slug,
            }
        )
    return fixture


def iter_subjects() -> Iterator[LCSubjectSpec]:
    """Yield each of the 6 canonical LCSubjectSpecs in declaration order."""
    yield from LC_SUBJECTS


__all__ = [
    "LC_SUBJECTS",
    "LCSubjectSpec",
    "SUBJECT_SLUGS",
    "DEFAULT_EMBED_DIM",
    "get_subject_spec",
    "pure_python_embed",
    "chunk_text",
    "python_baml_fallback_extract",
    "baml_available",
    "build_subject_fixture",
    "iter_subjects",
]
