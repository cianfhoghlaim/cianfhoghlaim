"""
LC-subject Dagster asset module — per-subject pipeline, originally for
the 6 NCCA Leaving Certificate "LC6" subjects, widened per the
lakehouse-multi-subject-multi-model-rollout change to all 13 subjects
with a real local PDF corpus under leaving_certificate/:
  - chemistry (LC022), computer_science (LC219), english (LC002),
    gaeilge (LC001), geography (LC005), mathematics (LC003)  [original 6]
  - biology, business, history, applied_mathematics, french, technology,
    ukrainian  [7 more, added this change]

Pipeline stages (per openspec/changes/2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams/,
updated for english by openspec/changes/2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1/,
widened to 13 subjects by the lakehouse-multi-subject-multi-model-rollout change):

  Layer 1 (Ingestion):  13 per-subject dlt assets
                         - lc5_<subject>_ingested (one per LC_ALL_SUBJECTS entry)
                         (each runs cianfhoghlaim.dlt.filesystem.leaving_cert_source
                          filtered by subject)

  Layer 2 (Materials):  13 subjects × 4 BAML extraction assets
                         - lc5_<subject>_syllabus_extracted (ExtractCurriculumSyllabus) — real for all 13
                         - lc5_<subject>_papers_extracted    (ExtractExamPaperLayout) — real for all 13
                         - lc5_<subject>_marking_extracted   (ExtractMarkingSchemeGuideline) — real for all 13
                         - lc5_<subject>_diagrams_extracted  (ExtractSyllabusDiagram) — real for chemistry
                           only; the other 12 subjects remain stubs (same proven
                           pdf_to_image_bridge.py pattern, ~12x the per-subject
                           effort, explicitly scoped as follow-up, not required
                           for "fully populate" since diagrams are bonus signal)

  Layer 3 (Lifecycle):  6 cognify assets (original LC6 scope, not yet widened)
                         + 1 cross-subject Graphiti stream
                         - lc5_<subject>_cognified
                         - lc5_cross_subject_graphiti_stream

Each asset is keyed by the 5-layer group_name convention
"<N>_<layer>/<domain>/<slug>" with lc5_ prefix.

The actual BAML functions live in:
  cianfhoghlaim/baml_src/education/lc_extraction/{curriculum_syllabus,
                                                  exam_paper_layout,
                                                  marking_scheme,
                                                  cross_linguistic,
                                                  syllabus_diagram}.baml
"""


from typing import Any

from dagster import AssetExecutionContext, asset

try:
    from baml_client import b  # type: ignore[import-not-found]
    BAML_AVAILABLE = True
except ImportError:
    try:
        # Per the 2026-08-08-lakehouse-extensive-hydration-v1 change:
        # the bare `from baml_client import b` form above doesn't
        # resolve in every environment (the generated client's actual
        # importable path is `baml_client.baml_client.sync_client`) --
        # matching the fallback already used by the sibling
        # quest_pack_assets.py and tuatha/asset_generation/fibo/assets.py
        # in this same codebase, rather than leaving BAML_AVAILABLE
        # permanently False (and every one of these 24 assets a
        # permanent stub) whenever only the first form fails.
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]
        BAML_AVAILABLE = True
    except ImportError:
        BAML_AVAILABLE = False
        b = None

try:
    from dlt_sources.filesystem.leaving_cert_source import LC_ALL_SUBJECTS, lc5_documents
    DLT_AVAILABLE = True
except ImportError:
    DLT_AVAILABLE = False
    lc5_documents = None
    # Fallback so LC_ALL_SUBJECTS below still has the real 13-subject
    # value even if dlt_sources isn't importable in this environment
    # (matches this module's existing graceful-degradation convention).
    LC_ALL_SUBJECTS = (
        "chemistry", "computer_science", "english", "gaeilge", "geography",
        "mathematics", "biology", "business", "history",
        "applied_mathematics", "french", "technology", "ukrainian",
    )

try:
    import cognee
    COGNEE_AVAILABLE = True
except ImportError:
    COGNEE_AVAILABLE = False
    cognee = None

try:
    from graphiti_core import Graphiti
    GRAPHITI_AVAILABLE = True
except ImportError:
    GRAPHITI_AVAILABLE = False
    Graphiti = None


# Per the lakehouse-multi-subject-multi-model-rollout change: this used
# to be a hand-duplicated 6-subject tuple (this file's own prior comment
# flagged the duplication risk: "must match ... LC6_SUBJECTS"). Now
# imported directly from dlt_sources.filesystem.leaving_cert_source so
# there's exactly one source of truth for "all real local LC subjects" —
# confirmed live: all 13 subjects have a real local PDF corpus under
# leaving_certificate/<subject>/.
LC6_SUBJECTS: tuple[str, ...] = LC_ALL_SUBJECTS

# The original 6 subjects the Layer 1 ingestion assets below were
# hand-written for, kept separate from the 7 new ones (added via a
# factory further down) to avoid touching the 6 already-working,
# individually-named assets' behavior/identity.
_ORIGINAL_LC6_SUBJECTS: tuple[str, ...] = (
    "chemistry",
    "computer_science",
    "english",
    "gaeilge",
    "geography",
    "mathematics",
)
_NEW_LC_SUBJECTS: tuple[str, ...] = tuple(
    s for s in LC_ALL_SUBJECTS if s not in _ORIGINAL_LC6_SUBJECTS
)


# ─────────────────────────────────────────────────────────────────────────────
# Layer 1: Ingestion (13 per-subject assets: 6 original, hand-written below,
# + 7 new, factory-generated further down to avoid touching the originals)
# ─────────────────────────────────────────────────────────────────────────────


@asset(group_name="1_ingestion_curriculum_lc5", description="Ingest chemistry LC PDFs + JPG via select_ocr_backend() routing")
def lc5_chemistry_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 ingestion for chemistry (LC022) — 16 PDFs across en/ga."""
    if not DLT_AVAILABLE:
        context.log.warning("DLT source not available; returning stub")
        return {"rows": 0, "subject": "chemistry"}
    context.log.info("ingesting chemistry LC PDFs")
    rows = list(lc5_documents())  # type: ignore[misc]
    chemistry_rows = [r for r in rows if r["subject"] == "chemistry"]
    context.add_output_metadata({"row_count": len(chemistry_rows)})
    return {"rows": len(chemistry_rows), "subject": "chemistry"}


@asset(group_name="1_ingestion_curriculum_lc5", description="Ingest computer_science LC PDFs")
def lc5_computer_science_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 ingestion for computer_science (LC219) — 11 PDFs across en/ga."""
    if not DLT_AVAILABLE:
        return {"rows": 0, "subject": "computer_science"}
    rows = list(lc5_documents())  # type: ignore[misc]
    cs_rows = [r for r in rows if r["subject"] == "computer_science"]
    context.add_output_metadata({"row_count": len(cs_rows)})
    return {"rows": len(cs_rows), "subject": "computer_science"}


@asset(group_name="1_ingestion_curriculum_lc5", description="Ingest english LC PDFs (en-only at root; LC002 syllabus + ALP/GLP exam papers)")
def lc5_english_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 ingestion for english (LC002) — 8 PDFs at root (en-only),
    routed via qwen3-vl-8b for exam papers and gemma-4-26B-A4B for syllabi."""
    if not DLT_AVAILABLE:
        return {"rows": 0, "subject": "english"}
    context.log.info("ingesting english LC PDFs")
    rows = list(lc5_documents())  # type: ignore[misc]
    en_rows = [r for r in rows if r["subject"] == "english"]
    context.add_output_metadata({"row_count": len(en_rows)})
    return {"rows": len(en_rows), "subject": "english"}


@asset(group_name="1_ingestion_curriculum_lc5", description="Ingest gaeilge LC PDFs (no en/ subdir; Irish-only at root)")
def lc5_gaeilge_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 ingestion for gaeilge (LC001) — 11 PDFs at root, GLM-4.6V routing."""
    if not DLT_AVAILABLE:
        return {"rows": 0, "subject": "gaeilge"}
    rows = list(lc5_documents())  # type: ignore[misc]
    ga_rows = [r for r in rows if r["subject"] == "gaeilge"]
    context.add_output_metadata({"row_count": len(ga_rows)})
    return {"rows": len(ga_rows), "subject": "gaeilge"}


@asset(group_name="1_ingestion_curriculum_lc5", description="Ingest geography LC PDFs + 1 JPG scanned exam page")
def lc5_geography_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 ingestion for geography (LC005) — 18 PDFs + 1 JPG across en/ga."""
    if not DLT_AVAILABLE:
        return {"rows": 0, "subject": "geography"}
    rows = list(lc5_documents())  # type: ignore[misc]
    geo_rows = [r for r in rows if r["subject"] == "geography"]
    context.add_output_metadata({"row_count": len(geo_rows)})
    return {"rows": len(geo_rows), "subject": "geography"}


@asset(group_name="1_ingestion_curriculum_lc5", description="Ingest mathematics LC PDFs (LaTeX + formula heavy)")
def lc5_mathematics_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 ingestion for mathematics (LC003) — 16 PDFs across en/ga."""
    if not DLT_AVAILABLE:
        return {"rows": 0, "subject": "mathematics"}
    rows = list(lc5_documents())  # type: ignore[misc]
    math_rows = [r for r in rows if r["subject"] == "mathematics"]
    context.add_output_metadata({"row_count": len(math_rows)})
    return {"rows": len(math_rows), "subject": "mathematics"}


def _make_ingestion_asset(subject: str):
    """Factory for the 7 new Layer 1 ingestion assets (biology, business,
    history, applied_mathematics, french, technology, ukrainian), added
    per the lakehouse-multi-subject-multi-model-rollout change. The
    original 6 subjects keep their hand-written functions above
    unchanged (same asset identity/behavior, lower regression risk) —
    this factory only covers the 7 new ones.
    """

    @asset(
        name=f"lc5_{subject}_ingested",
        group_name="1_ingestion_curriculum_lc5",
        description=f"Ingest {subject} LC PDFs via select_ocr_backend() routing",
    )
    def lc5_ingestion_asset(context: AssetExecutionContext) -> dict[str, Any]:
        if not DLT_AVAILABLE:
            context.log.warning("DLT source not available; returning stub")
            return {"rows": 0, "subject": subject}
        context.log.info(f"ingesting {subject} LC PDFs")
        rows = list(lc5_documents())  # type: ignore[misc]
        subject_rows = [r for r in rows if r["subject"] == subject]
        context.add_output_metadata({"row_count": len(subject_rows)})
        return {"rows": len(subject_rows), "subject": subject}

    lc5_ingestion_asset.__name__ = f"lc5_{subject}_ingested"
    return lc5_ingestion_asset


for _new_subject in _NEW_LC_SUBJECTS:
    globals()[f"lc5_{_new_subject}_ingested"] = _make_ingestion_asset(_new_subject)


# ─────────────────────────────────────────────────────────────────────────────
# Layer 2: BAML materials extraction (13 subjects × 4 BAML functions = 52 assets)
# ─────────────────────────────────────────────────────────────────────────────


def _make_subject_extraction_asset(subject: str, kind: str):
    """Factory for the per-subject BAML extraction assets (4 kinds × 13 subjects).

    Per the 2026-08-08-lakehouse-extensive-hydration-v1 change, exactly
    one of these 52 assets (lc5_chemistry_diagrams_extracted) was
    un-stubbed into a real implementation, defined separately below and
    excluded from this factory's loop.

    Per the lakehouse-multi-subject-multi-model-rollout change: "syllabus"
    / "papers" / "marking" are now ALSO real for every subject here —
    `ExtractCurriculumSyllabus` / `ExtractExamPaperLayout` /
    `ExtractMarkingSchemeGuideline` all take free-text `subject: string?`
    (no enum, unlike `ExtractLC6Syllabus`), and were already proven
    working via `quest_pack_assets.py`'s real call sites, which this
    factory mirrors (same `_classify_pdfs`/`_extract_pdf_text`/
    `SUBJECT_PRIMARY_LANGUAGE` reuse, same directory/layer, not a
    cross-layer import). Only "diagrams" remains a stub here for the 12
    non-chemistry subjects — same proven pattern as
    `lc5_chemistry_diagrams_extracted` below, but ~12x the per-subject
    effort (image rendering per page), explicitly scoped as follow-up
    rather than attempted for all 13 in this pass.
    """
    baml_function_map = {
        "syllabus": "ExtractCurriculumSyllabus",
        "papers": "ExtractExamPaperLayout",
        "marking": "ExtractMarkingSchemeGuideline",
        "diagrams": "ExtractSyllabusDiagram",
    }
    baml_function = baml_function_map[kind]
    # Maps this asset's "kind" to _classify_pdfs()'s bucket key.
    bucket_key_map = {"syllabus": "syllabus", "papers": "exam_paper", "marking": "marking_scheme"}

    @asset(
        name=f"lc5_{subject}_{kind}_extracted",
        group_name=f"2_materials_lc_{kind}_lc5_{subject}",
        description=f"BAML {baml_function} for the {subject} LC subject",
    )
    def lc5_extraction_asset(context: AssetExecutionContext) -> dict[str, Any]:
        """Real {baml_function} extraction for {subject} (diagrams: still a stub except chemistry)."""
        if not BAML_AVAILABLE:
            context.log.warning(f"lc5_{subject}_{kind}_extracted: baml_client not importable; skipping")
            return {"rows": 0, "subject": subject, "kind": kind}

        if kind == "diagrams":
            # Stub for every subject except chemistry (see
            # lc5_chemistry_diagrams_extracted below) — explicitly scoped
            # follow-up, not silently claimed done.
            context.log.info(
                f"lc5_{subject}_diagrams_extracted: diagram extraction not yet "
                "wired for this subject (chemistry-only so far)"
            )
            return {"rows": 0, "subject": subject, "kind": kind}

        context.log.info(f"running {baml_function} for {subject}")

        # Leading-digit directory name ("2_materials") makes a static
        # import illegal Python syntax -- importlib.import_module() is
        # the established pattern for this in the repo (see
        # lc5_chemistry_diagrams_extracted below, orchestration/definitions.py).
        import importlib

        _qpack = importlib.import_module(
            "orchestration.defs.2_materials.lc_extraction.quest_pack_assets"
        )
        _classify_pdfs = _qpack._classify_pdfs
        _extract_pdf_text = _qpack._extract_pdf_text
        primary_language = _qpack.SUBJECT_PRIMARY_LANGUAGE.get(subject, "en")

        try:
            buckets = _classify_pdfs(subject)
        except Exception as exc:  # noqa: BLE001 — filesystem/glob errors, not a stable API
            context.log.warning(f"lc5_{subject}_{kind}_extracted: _classify_pdfs failed: {exc}")
            return {"rows": 0, "subject": subject, "kind": kind}

        bucket_key = bucket_key_map[kind]
        entries = [e for e in buckets.get(bucket_key, []) if e["language"] == primary_language]
        if not entries:
            context.log.warning(
                f"lc5_{subject}_{kind}_extracted: no {primary_language}-medium "
                f"{bucket_key} PDF found"
            )
            return {"rows": 0, "subject": subject, "kind": kind}

        results: list[Any] = []
        if kind == "syllabus":
            # Single canonical document — prefer the shortest filename
            # among candidates, same tie-break quest_pack_assets.py uses.
            entry = min(entries, key=lambda e: len(e["path"].name))
            text = _extract_pdf_text(entry["path"])
            if not text.strip():
                context.log.warning(
                    f"lc5_{subject}_{kind}_extracted: no extractable text layer "
                    f"in {entry['path'].name}"
                )
                return {"rows": 0, "subject": subject, "kind": kind}
            try:
                results.append(
                    b.ExtractCurriculumSyllabus(
                        pdf_text=text, subject=subject, language=primary_language.upper()
                    )
                )
            except Exception as exc:  # noqa: BLE001 — BAML error types are not stable API
                context.log.error(f"lc5_{subject}_{kind}_extracted: extraction failed: {exc}")
                return {"rows": 0, "subject": subject, "kind": kind}
        else:
            # papers / marking — potentially multiple documents per subject.
            for entry in entries:
                text = _extract_pdf_text(entry["path"])
                if not text.strip():
                    context.log.warning(
                        f"lc5_{subject}_{kind}_extracted: no extractable text "
                        f"layer in {entry['path'].name}; skipping this document"
                    )
                    continue
                try:
                    if kind == "papers":
                        item = b.ExtractExamPaperLayout(
                            pdf_text=text, subject=subject, paper_code=None, year=None
                        )
                    else:  # marking
                        item = b.ExtractMarkingSchemeGuideline(
                            pdf_text=text, subject=subject, year=None, paper=None
                        )
                except Exception as exc:  # noqa: BLE001 — BAML error types are not stable API
                    context.log.warning(
                        f"lc5_{subject}_{kind}_extracted: extraction failed for "
                        f"{entry['path'].name}: {exc}"
                    )
                    continue
                results.append(item)

        context.add_output_metadata({"row_count": len(results)})
        return {"rows": len(results), "subject": subject, "kind": kind}

    lc5_extraction_asset.__name__ = f"lc5_{subject}_{kind}_extracted"
    return lc5_extraction_asset


@asset(
    name="lc5_chemistry_diagrams_extracted",
    group_name="2_materials_lc_diagrams_lc5_chemistry",
    description="Real ExtractSyllabusDiagram (image + text) for chemistry LC",
    deps=["lc5_chemistry_ingested"],
)
def lc5_chemistry_diagrams_extracted(context: AssetExecutionContext) -> dict[str, Any]:
    """The one un-stubbed diagram-extraction asset (per the
    2026-08-08-lakehouse-extensive-hydration-v1 change) — calls the real,
    now image-capable `ExtractSyllabusDiagram` against chemistry's actual
    English-medium syllabus PDF, rendering page images via
    `meaisinfhoghlaim.document_factory.pdf_to_image_bridge` alongside the
    extracted text (mirrors `tuatha/asset_generation/fibo/assets.py::
    fibo_configs_from_syllabus_diagrams`, which does the same thing for
    the FIBO diagram-generation pipeline). Reuses the sibling
    `quest_pack_assets.py`'s `_classify_pdfs`/`_extract_pdf_text`/
    `LEAVING_CERT_ROOT` — same directory, same layer, not a cross-layer
    import.

    Returns an explicit empty/skip result (not a Failure) when BAML,
    pypdf, or the syllabus PDF itself aren't available — matching this
    module's and quest_pack_assets.py's existing graceful-degradation
    convention.
    """
    if not BAML_AVAILABLE:
        context.log.warning("lc5_chemistry_diagrams_extracted: baml_client not importable; skipping")
        return {"rows": 0, "subject": "chemistry", "kind": "diagrams"}

    # Leading-digit directory name ("2_materials") makes a static
    # `from orchestration.defs.2_materials... import` illegal Python
    # syntax -- importlib.import_module() is the established pattern
    # for this in the repo (see orchestration/definitions.py,
    # orchestration/components/biep_subject_component.py).
    import importlib

    _qpack = importlib.import_module(
        "orchestration.defs.2_materials.lc_extraction.quest_pack_assets"
    )
    _classify_pdfs = _qpack._classify_pdfs
    _extract_pdf_text = _qpack._extract_pdf_text

    buckets = _classify_pdfs("chemistry")
    syllabus_entries = [e for e in buckets["syllabus"] if e["language"] == "en"]
    if not syllabus_entries:
        context.log.warning(
            "lc5_chemistry_diagrams_extracted: no English-medium syllabus PDF found"
        )
        return {"rows": 0, "subject": "chemistry", "kind": "diagrams"}

    syllabus_path = min(syllabus_entries, key=lambda e: len(e["path"].name))["path"]
    text = _extract_pdf_text(syllabus_path)
    if not text.strip():
        context.log.warning(
            "lc5_chemistry_diagrams_extracted: no extractable text layer in %s",
            syllabus_path.name,
        )
        return {"rows": 0, "subject": "chemistry", "kind": "diagrams"}

    rendered_images = []
    try:
        from pypdf import PdfReader

        from meaisinfhoghlaim.document_factory.pdf_to_image_bridge import (
            pdf_page_to_baml_image,
        )

        page_count = len(PdfReader(str(syllabus_path)).pages)
        for page_number in range(1, min(page_count, 8) + 1):
            img = pdf_page_to_baml_image(syllabus_path, page_number)
            if img is not None:
                rendered_images.append(img)
    except ImportError:
        context.log.warning(
            "lc5_chemistry_diagrams_extracted: pdf_to_image_bridge/pypdf not "
            "importable; falling back to text-only diagram detection"
        )

    try:
        diagrams = b.ExtractSyllabusDiagram(
            pdf_text=text,
            page_text=None,
            page_number=None,
            subject="chemistry",
            subject_language="EN",
            image=rendered_images or None,
        )
    except Exception as exc:  # BAML error types are not stable API
        context.log.error("lc5_chemistry_diagrams_extracted: extraction failed: %s", exc)
        return {"rows": 0, "subject": "chemistry", "kind": "diagrams"}

    context.add_output_metadata({
        "row_count": len(diagrams),
        "images_rendered": len(rendered_images),
        "syllabus_pdf": syllabus_path.name,
    })
    return {"rows": len(diagrams), "subject": "chemistry", "kind": "diagrams"}


# Generate the remaining 51 BAML extraction assets (13 subjects × 4
# kinds, minus lc5_chemistry_diagrams_extracted defined above as the one
# real diagrams implementation). syllabus/papers/marking are real for
# all 13; diagrams is real for chemistry only, stub for the other 12
# (see _make_subject_extraction_asset's docstring).
for _subject in LC6_SUBJECTS:
    for _kind in ("syllabus", "papers", "marking", "diagrams"):
        if _subject == "chemistry" and _kind == "diagrams":
            continue
        globals()[f"lc5_{_subject}_{_kind}_extracted"] = _make_subject_extraction_asset(_subject, _kind)


# ─────────────────────────────────────────────────────────────────────────────
# Layer 3: Model Lifecycle (6 per-subject cognify + 1 cross-subject Graphiti)
# ─────────────────────────────────────────────────────────────────────────────


@asset(group_name="3_model_lifecycle_lc_cognify_lc5_chemistry", description="Cognee cognify for chemistry LC")
def lc5_chemistry_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    """Per-subject Cognee cognify (cianfhoghlaim_chemistry dataset)."""
    if not COGNEE_AVAILABLE:
        return {"entities": 0, "subject": "chemistry"}
    # Real call would be: await cognee.cognify(dataset_name=f"cianfhoghlaim_{subject}")
    return {"entities": 0, "subject": "chemistry"}


@asset(group_name="3_model_lifecycle_lc_cognify_lc5_computer_science", description="Cognee cognify for computer_science LC")
def lc5_computer_science_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    if not COGNEE_AVAILABLE:
        return {"entities": 0, "subject": "computer_science"}
    return {"entities": 0, "subject": "computer_science"}


@asset(group_name="3_model_lifecycle_lc_cognify_lc5_english", description="Cognee cognify for english LC (text-heavy, monolingual dataset)")
def lc5_english_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    """Per-subject Cognee cognify (cianfhoghlaim_english dataset)."""
    if not COGNEE_AVAILABLE:
        return {"entities": 0, "subject": "english"}
    # Real call would be: await cognee.cognify(dataset_name="cianfhoghlaim_english")
    return {"entities": 0, "subject": "english"}


@asset(group_name="3_model_lifecycle_lc_cognify_lc5_gaeilge", description="Cognee cognify for gaeilge LC (multilingual Irish dataset)")
def lc5_gaeilge_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    if not COGNEE_AVAILABLE:
        return {"entities": 0, "subject": "gaeilge"}
    return {"entities": 0, "subject": "gaeilge"}


@asset(group_name="3_model_lifecycle_lc_cognify_lc5_geography", description="Cognee cognify for geography LC (diagram-heavy)")
def lc5_geography_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    if not COGNEE_AVAILABLE:
        return {"entities": 0, "subject": "geography"}
    return {"entities": 0, "subject": "geography"}


@asset(group_name="3_model_lifecycle_lc_cognify_lc5_mathematics", description="Cognee cognify for mathematics LC (formula-heavy)")
def lc5_mathematics_cognified(context: AssetExecutionContext) -> dict[str, Any]:
    if not COGNEE_AVAILABLE:
        return {"entities": 0, "subject": "mathematics"}
    return {"entities": 0, "subject": "mathematics"}


@asset(group_name="3_model_lifecycle_lc_cross_subject_lc5", description="Bi-temporal Graphiti stream + FalkorDB cross-subject graph")
def lc5_cross_subject_graphiti_stream(context: AssetExecutionContext) -> dict[str, Any]:
    """Cross-subject Graphiti temporal stream — 6 subjects merged into a FalkorDB graph.

    Still scoped to the original 6 subjects (Layer 3/cognify wasn't
    widened to 13 this pass, unlike Layers 1-2) — uses
    _ORIGINAL_LC6_SUBJECTS rather than the now-13-subject LC6_SUBJECTS so
    this doesn't misreport a subject count Layer 3 doesn't actually cover.

    Nodes: Subject, Topic, LearningOutcome, Question, Year, ModuleKind
    Edges: HAS_TOPIC, ASSESSED_BY, EVOLVED_TO, EN_CORRESPONDS_TO_GA (cross-linguistic)
    """
    if not GRAPHITI_AVAILABLE:
        return {"episodes": 0, "subjects": len(_ORIGINAL_LC6_SUBJECTS)}
    return {"episodes": 0, "subjects": len(_ORIGINAL_LC6_SUBJECTS)}
