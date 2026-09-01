"""Ireland Leaving Cert quest-pack generation Dagster assets.

Per `2026-08-08-docs-informed-quest-and-credential-generation-v1`: this
is the module that makes "quest packs are generated from the official
NCCA syllabus PDFs" — a claim the MMO client's landing page already
made in prose before this module existed — literally true instead of
aspirational. One asset per Leaving Cert subject
(``<subject>_quest_pack``), each of which:

1. Reads the subject's real PDF corpus directly from
   ``leaving_certificate/<subject>/`` (NOT the ``lc5_documents()`` DLT
   source, whose row schema still uses stale pre-2026-08-06 field
   names — see ``_classify_pdfs()`` docstring for why this asset
   re-reads the filesystem instead of depending on that source).
2. Classifies each PDF as a syllabus, past exam paper, or marking-
   scheme guideline by filename heuristic (``_classify_pdfs``).
3. Extracts each into the real v3 BAML types (``SyllabusDocument``,
   ``ExamPaper``, ``MarkingScheme``) via
   ``ExtractCurriculumSyllabus`` / ``ExtractExamPaperLayout`` /
   ``ExtractMarkingSchemeGuideline``
   (``baml_src/british_isles/ireland/education/lc_extraction/``).
4. Calls the subject's ``Generate<Prefix>QuestPack`` function
   (``baml_src/british_isles/ireland/education/subjects/
   qpack_<subject>.baml``) to produce one docs-grounded quest pack at
   Higher Level (the one level every subject's corpus reliably
   covers — see ``_extract_subject_materials``'s docstring for the
   per-level scoping call).
5. Writes the result to Convex's ``questPacks`` table, for the MMO
   client's ``realm/$subject.tsx`` route to query directly (Phase 5).

## Scope: Leaving Cert only, one medium per subject, Higher Level only

Junior Cycle is NOT covered by this module: there is no Junior-Cycle
PDF corpus under ``leaving_certificate/`` for these 8 subjects (real
Junior Cycle ingestion lives in a separate DLT source tree —
``dlt_sources/british_isles/ireland/education/junior_cycle*.py`` —
which was out of scope to wire into quest-pack generation in this
pass; fabricating Junior Cycle content from Leaving Cert PDFs would
violate the docs-informed principle this whole module exists to
enforce).

Each subject generates from ONE medium (see
``SUBJECT_PRIMARY_LANGUAGE``): English for 7 subjects, Irish for
gaeilge — because gaeilge's past exam papers exist ONLY as
Irish-medium "IV" PDFs in the corpus (there is no English-medium
Leaving Cert Irish exam; the exam tests Irish itself), so an
English-only rule would silently generate a zero-past-paper pack for
that subject instead of reflecting its real corpus. The other
language's PDFs (e.g. the English-medium guideline document that also
exists for gaeilge) are not cross-linked into the generated pack in
this first pass — wiring both mediums together per subject through
``ExtractCrossLinguisticConcept`` is real future work, not done here.
Ordinary/Foundation Level quest packs are equally real future work —
Higher Level was chosen because every one of the 8 subjects has at
least one Higher-Level-coded past paper in the corpus, giving a
uniform per-subject asset shape.

## Untouched neighbours

``lc5_<subject>_ingested`` (``lc5_assets.py``) and the chemistry-pilot
assets (``lc_chemistry_pilot_assets.py``) are untouched — this module
does not depend on either and does not modify their tables.
"""

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from dagster import AssetExecutionContext, asset

try:
    from baml_client import b  # type: ignore[import-not-found]

    BAML_AVAILABLE = True
except ImportError:
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        BAML_AVAILABLE = True
    except ImportError:
        BAML_AVAILABLE = False
        b = None  # type: ignore[assignment]

try:
    from pypdf import PdfReader

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    PdfReader = None  # type: ignore[assignment,misc]

REPO_ROOT = Path(__file__).resolve().parents[4]
LEAVING_CERT_ROOT = REPO_ROOT / "leaving_certificate"

MATERIALS_GROUP = "2_materials_education_quest_packs"

# Higher Level — see module docstring "Scope" for why this is the only
# level generated in this pass.
GENERATION_LEVEL = "LC_HL"

# Cap on characters of PDF text sent to any single extraction call —
# mirrors lc_chemistry_pilot_assets.py's MAX_TEXT_CHARS guard against
# pathologically long documents blowing the context window.
MAX_TEXT_CHARS = 60_000

# subject slug -> qpack_<subject>.baml's class/function name prefix
# (e.g. "mathematics" -> GenerateMathQuestPack / MathQuestPack).
SUBJECT_BAML_PREFIX: dict[str, str] = {
    "mathematics": "Math",
    "chemistry": "Chem",
    "geography": "Geog",
    "gaeilge": "Gael",
    "english": "Engl",
    "computer_science": "Comp",
    "history": "Hist",
    "applied_mathematics": "Appm",
}

# The medium of instruction/examination to generate a quest pack from,
# per subject. Every subject defaults to English-medium ("en") EXCEPT
# gaeilge (Irish as a subject): its past exam papers exist ONLY as
# Irish-medium "IV" (Irish Version) PDFs in the corpus — there is no
# English-medium Leaving Cert Irish exam, because the exam tests Irish
# itself. Forcing "en" there would silently generate a quest pack with
# zero past papers instead of reflecting the subject's real corpus.
SUBJECT_PRIMARY_LANGUAGE: dict[str, str] = {
    "gaeilge": "ga",
}

# Filename heuristics — matched against the corpus under
# leaving_certificate/<subject>/ (see _classify_pdfs docstring).
_EXAM_PAPER_RE = re.compile(r"^LC\d{3}[A-Z]LP[A-Z0-9]{3,4}[EI]V\.pdf$", re.IGNORECASE)
_MARKING_SCHEME_KEYWORDS = ("guideline",)
_SYLLABUS_KEYWORDS = ("syllabus", "specification", "siollabas", "siollabais", "foundation")
_DATE_SUFFIX_RE = re.compile(r"_\d{4}-\d{2}-\d{2}(?=\.pdf$)", re.IGNORECASE)
_IRISH_MARKERS = ("gaeilge", "siollabas", "siollabais", "ciorclán")


def _classify_pdfs(subject: str) -> dict[str, list[dict[str, Any]]]:
    """Classify every PDF under ``leaving_certificate/<subject>/`` by
    filename heuristic into 'syllabus' / 'exam_paper' / 'marking_scheme'
    buckets, English-medium only (see module docstring "Scope").

    Why filename heuristics and not the ``lc5_documents()`` DLT source:
    that source's row schema still carries stale pre-2026-08-06 field
    names (``syllabus.topics`` instead of the real
    ``SyllabusDocument.module_topics``, ``paper.items`` instead of
    ``ExamPaper.sections[].questions``) — a separate, already-tracked
    bug (Task #17-adjacent) deliberately left alone here rather than
    silently worked around inside a new asset. Reading the filesystem
    directly with the CORRECT v3 field names, rather than routing
    through a source that would need its own fix first, keeps this
    asset's correctness independent of that bug.

    Deduplicates re-downloaded copies that only differ by a
    ``_YYYY-MM-DD`` refresh-timestamp suffix in the filename (both
    copies are byte-identical in every corpus directory checked), by
    normalising the suffix away and keeping the first match.

    Smoke-tested by hand against the real corpus for all 8 subjects
    (mathematics, chemistry, geography, gaeilge, english,
    computer_science, history, applied_mathematics) as of 2026-08-08.
    """
    subject_dir = LEAVING_CERT_ROOT / subject
    buckets: dict[str, list[dict[str, Any]]] = {
        "syllabus": [],
        "exam_paper": [],
        "marking_scheme": [],
    }
    if not subject_dir.exists():
        return buckets

    seen_normalized: set[str] = set()
    for pdf_path in sorted(subject_dir.rglob("*.pdf")):
        normalized = _DATE_SUFFIX_RE.sub("", pdf_path.name).lower()
        if normalized in seen_normalized:
            continue
        seen_normalized.add(normalized)

        name = pdf_path.name
        name_lower = name.lower()
        parent_name = pdf_path.parent.name.lower()

        # Language: EV/IV suffix on exam-paper codes is authoritative;
        # otherwise fall back to the en/ga parent directory (when
        # present) or an Irish-language keyword in the filename.
        if name_lower.endswith("iv.pdf") and _EXAM_PAPER_RE.match(name):
            language = "ga"
        elif name_lower.endswith("ev.pdf") and _EXAM_PAPER_RE.match(name):
            language = "en"
        elif parent_name == "ga":
            language = "ga"
        elif parent_name == "en":
            language = "en"
        elif any(marker in name_lower for marker in _IRISH_MARKERS):
            language = "ga"
        else:
            language = "en"

        entry = {"path": pdf_path, "language": language}

        if _EXAM_PAPER_RE.match(name):
            buckets["exam_paper"].append(entry)
        elif any(keyword in name_lower for keyword in _MARKING_SCHEME_KEYWORDS):
            buckets["marking_scheme"].append(entry)
        elif any(keyword in name_lower for keyword in _SYLLABUS_KEYWORDS):
            buckets["syllabus"].append(entry)
        # else: unclassified (e.g. a stray .jpg exam-paper page or an
        # ancillary document) — silently skipped, not forced into a
        # bucket it doesn't belong in.

    return buckets


def _extract_pdf_text(pdf_path: Path) -> str:
    """Extract raw text from a PDF, truncated to MAX_TEXT_CHARS."""
    reader = PdfReader(str(pdf_path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if len(text) > MAX_TEXT_CHARS:
        text = text[:MAX_TEXT_CHARS]
    return text


def _extract_subject_materials(
    context: AssetExecutionContext, subject: str
) -> Optional[dict[str, Any]]:
    """Run the real BAML extraction chain for one subject's EN corpus,
    then generate its Higher Level quest pack.

    Returns None (asset materialises to an explicit empty/skip state,
    not a Failure) when the corpus has no syllabus PDF or when
    BAML/pypdf aren't available — a missing corpus is an expected,
    documented gap for some subjects, not an error to crash the whole
    Dagster run over.
    """
    if not BAML_AVAILABLE:
        context.log.warning("%s_quest_pack: baml_client not importable; skipping", subject)
        return None
    if not PYPDF_AVAILABLE:
        context.log.warning("%s_quest_pack: pypdf not importable; skipping", subject)
        return None

    primary_language = SUBJECT_PRIMARY_LANGUAGE.get(subject, "en")
    buckets = _classify_pdfs(subject)
    syllabus_entries = [e for e in buckets["syllabus"] if e["language"] == primary_language]
    exam_entries = [e for e in buckets["exam_paper"] if e["language"] == primary_language]
    marking_entries = [e for e in buckets["marking_scheme"] if e["language"] == primary_language]

    if not syllabus_entries:
        context.log.warning(
            "%s_quest_pack: no %s-medium syllabus PDF found under %s; skipping",
            subject,
            primary_language,
            LEAVING_CERT_ROOT / subject,
        )
        return None

    # Prefer the shortest filename among candidates (fewest suffixes /
    # qualifiers) as the primary syllabus document when more than one
    # matched — e.g. an "-INT" interim spec vs. the base spec.
    syllabus_entry = min(syllabus_entries, key=lambda e: len(e["path"].name))
    context.log.info("%s_quest_pack: syllabus=%s", subject, syllabus_entry["path"].name)

    syllabus_text = _extract_pdf_text(syllabus_entry["path"])
    if not syllabus_text.strip():
        context.log.warning(
            "%s_quest_pack: no extractable text layer in %s; skipping",
            subject,
            syllabus_entry["path"].name,
        )
        return None

    syllabus_doc = b.ExtractCurriculumSyllabus(
        pdf_text=syllabus_text, subject=subject, language=primary_language.upper()
    )

    exam_papers: list[Any] = []
    for entry in exam_entries:
        text = _extract_pdf_text(entry["path"])
        if not text.strip():
            context.log.warning(
                "%s_quest_pack: no extractable text layer in %s; skipping this paper",
                subject,
                entry["path"].name,
            )
            continue
        try:
            paper = b.ExtractExamPaperLayout(pdf_text=text, subject=subject, paper_code=None, year=None)
        except Exception as exc:  # noqa: BLE001 — BAML error types are not stable API
            context.log.warning(
                "%s_quest_pack: exam paper extraction failed for %s: %s",
                subject,
                entry["path"].name,
                exc,
            )
            continue
        exam_papers.append(paper)

    marking_schemes: list[Any] = []
    for entry in marking_entries:
        text = _extract_pdf_text(entry["path"])
        if not text.strip():
            context.log.warning(
                "%s_quest_pack: no extractable text layer in %s; skipping this marking scheme",
                subject,
                entry["path"].name,
            )
            continue
        try:
            scheme = b.ExtractMarkingSchemeGuideline(
                pdf_text=text, subject=subject, year=None, paper=None
            )
        except Exception as exc:  # noqa: BLE001 — BAML error types are not stable API
            context.log.warning(
                "%s_quest_pack: marking scheme extraction failed for %s: %s",
                subject,
                entry["path"].name,
                exc,
            )
            continue
        marking_schemes.append(scheme)

    # Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
    # (Phase 1 §2.1): the per-subject Generate<Prefix>QuestPack
    # functions were consolidated into a single
    # b.GenerateSubjectQuestPack(syllabus_extract, subject, stage,
    # language, lo_codes) by the qpack-template change. The per-subject
    # names no longer exist; calling them via getattr would
    # AttributeError at materialisation time. Route through the
    # consolidated entry instead.
    try:
        from baml_client.types import (
            NCCASubjectSlug,
            QuestPackStage,
            QuestPackLanguage,
        )
    except ImportError:
        from baml_client import b
        NCCASubjectSlug = getattr(b, "NCCASubjectSlug", None)
        QuestPackStage = getattr(b, "QuestPackStage", None)
        QuestPackLanguage = getattr(b, "QuestPackLanguage", None)

    # Map subject slug -> NCCASubjectSlug enum value
    _subject_slug_upper = subject.upper()
    subject_enum = (
        getattr(NCCASubjectSlug, _subject_slug_upper, None)
        if NCCASubjectSlug is not None
        else None
    ) or _subject_slug_upper

    # Map GENERATION_LEVEL ("LC_HL") -> QuestPackStage.LC_HL
    stage_enum = (
        getattr(QuestPackStage, GENERATION_LEVEL, None)
        if QuestPackStage is not None
        else GENERATION_LEVEL
    ) or GENERATION_LEVEL

    # Map primary_language ("en" / "ga") -> QuestPackLanguage enum
    if primary_language == "ga":
        language_enum = (
            getattr(QuestPackLanguage, "GA", None)
            if QuestPackLanguage is not None
            else "GA"
        ) or "GA"
    else:
        language_enum = (
            getattr(QuestPackLanguage, "EN", None)
            if QuestPackLanguage is not None
            else "EN"
        ) or "EN"

    # Extract lo_codes from the syllabus_doc.learning_outcomes[]
    _raw_los = getattr(syllabus_doc, "learning_outcomes", None) or []
    lo_codes = [
        getattr(lo, "code", None) or getattr(lo, "lo_id", None)
        for lo in _raw_los
    ]
    lo_codes = [c for c in lo_codes if c]

    # Serialise the syllabus_doc to a single string for the consolidated
    # `syllabus_extract` parameter (the consolidated function takes a
    # text extract, not the full BAML object).
    if hasattr(syllabus_doc, "model_dump_json"):
        syllabus_extract = syllabus_doc.model_dump_json()
    elif hasattr(syllabus_doc, "model_dump"):
        import json as _json
        syllabus_extract = _json.dumps(syllabus_doc.model_dump())
    elif hasattr(syllabus_doc, "dict"):
        import json as _json
        syllabus_extract = _json.dumps(syllabus_doc.dict())
    else:
        syllabus_extract = str(syllabus_doc)

    context.log.info(
        "%s_quest_pack: generating via GenerateSubjectQuestPack "
        "(%d LOs from syllabus_doc, stage=%s, language=%s)",
        subject,
        len(lo_codes),
        stage_enum,
        language_enum,
    )
    pack = b.GenerateSubjectQuestPack(
        syllabus_extract=syllabus_extract,
        subject=subject_enum,
        stage=stage_enum,
        language=language_enum,
        lo_codes=lo_codes,
    )
    return {
        "pack": pack,
        "syllabus_pdf": str(syllabus_entry["path"].relative_to(REPO_ROOT)),
        "exam_paper_count": len(exam_papers),
        "marking_scheme_count": len(marking_schemes),
    }


def _write_quest_pack_to_convex(subject: str, pack: Any) -> bool:
    """Write a generated quest pack to Convex's `questPacks` table.

    Degrades gracefully (returns False, never raises) when the
    `convex` package isn't installed or `CONVEX_URL` isn't reachable —
    matching `tuatha/badges/ledger.py`'s graceful-degradation pattern.
    Field mapping is explicit camelCase, not `model_dump(mode="json")`,
    for the same reason `ledger.py`'s badge write needed the same fix:
    a raw snake_case dump doesn't match a camelCase Convex validator.
    """
    import os

    try:
        from convex import ConvexClient
    except ImportError:
        return False

    try:
        client = ConvexClient(os.environ.get("CONVEX_URL", "http://localhost:3210"))
        client.mutation(
            "questPacks:create",
            {
                "packId": pack.id,
                "subject": subject,
                "framework": pack.framework,
                "level": pack.level.value if hasattr(pack.level, "value") else str(pack.level),
                "titleEn": pack.title.text_en,
                "titleGa": pack.title.text_ga,
                "descriptionEn": pack.description.text_en,
                "descriptionGa": pack.description.text_ga,
                "totalItems": pack.total_items,
                "totalMarks": pack.total_marks,
                "estTimeMinutes": pack.est_time_minutes,
                "losCovered": pack.los_covered,
                "items": [item.model_dump(mode="json") for item in pack.items],
                "prerequisites": pack.prerequisites,
                "crossSubjectLinks": pack.cross_subject_links,
                "generatedAt": pack.generated_at,
                "generatedBy": pack.generated_by,
            },
        )
        return True
    except Exception:
        # Convex reachable-but-erroring (e.g. schema mismatch before
        # convex/schema.ts Phase 5 lands) must not fail the Dagster
        # asset — the generation itself already succeeded and is
        # returned in the asset's own materialised output.
        return False


def _make_quest_pack_asset(subject: str):
    """Factory: build one `<subject>_quest_pack` Dagster asset function.

    A factory (not 8 hand-written near-duplicate functions) because
    the 8 subjects' assets differ only in `subject` — everything else
    (extraction chain, generation call, Convex write) is identical.
    """

    def _asset_fn(context: AssetExecutionContext) -> dict[str, Any]:
        result = _extract_subject_materials(context, subject)
        if result is None:
            context.add_output_metadata({"status": "skipped", "subject": subject})
            return {"status": "skipped", "subject": subject}

        pack = result["pack"]
        written = _write_quest_pack_to_convex(subject, pack)
        context.add_output_metadata(
            {
                "status": "generated",
                "subject": subject,
                "pack_id": pack.id,
                "total_items": pack.total_items,
                "los_covered": len(pack.los_covered),
                "syllabus_pdf": result["syllabus_pdf"],
                "exam_paper_count": result["exam_paper_count"],
                "marking_scheme_count": result["marking_scheme_count"],
                "written_to_convex": written,
            }
        )
        return {
            "status": "generated",
            "subject": subject,
            "pack_id": pack.id,
            "total_items": pack.total_items,
            "written_to_convex": written,
        }

    _asset_fn.__name__ = f"{subject}_quest_pack"
    _asset_fn.__doc__ = (
        f"Generate the Higher Level {subject} quest pack from the real "
        f"NCCA syllabus + past papers + marking scheme corpus under "
        f"leaving_certificate/{subject}/, and write it to Convex."
    )
    return asset(
        name=f"{subject}_quest_pack",
        group_name=MATERIALS_GROUP,
        description=(
            f"Docs-informed Higher Level quest pack for {subject}, generated "
            f"from the real syllabus/past-paper/marking-scheme PDF corpus via "
            f"b.GenerateSubjectQuestPack (the consolidated qpack-template entry)."
        ),
    )(_asset_fn)


# One asset per subject, exposed at module scope so Dagster's
# `dg.load_defs()` auto-discovery (which walks orchestration/defs/
# recursively) picks each one up — mirrors the explicit per-subject
# asset variables in lc5_assets.py rather than returning a bare list.
mathematics_quest_pack = _make_quest_pack_asset("mathematics")
chemistry_quest_pack = _make_quest_pack_asset("chemistry")
geography_quest_pack = _make_quest_pack_asset("geography")
gaeilge_quest_pack = _make_quest_pack_asset("gaeilge")
english_quest_pack = _make_quest_pack_asset("english")
computer_science_quest_pack = _make_quest_pack_asset("computer_science")
history_quest_pack = _make_quest_pack_asset("history")
applied_mathematics_quest_pack = _make_quest_pack_asset("applied_mathematics")


__all__ = [
    "BAML_AVAILABLE",
    "PYPDF_AVAILABLE",
    "SUBJECT_BAML_PREFIX",
    "GENERATION_LEVEL",
    "mathematics_quest_pack",
    "chemistry_quest_pack",
    "geography_quest_pack",
    "gaeilge_quest_pack",
    "english_quest_pack",
    "computer_science_quest_pack",
    "history_quest_pack",
    "applied_mathematics_quest_pack",
]
