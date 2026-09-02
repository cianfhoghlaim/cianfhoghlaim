"""Shared BAML-Extract helpers for the 5 per-jurisdiction orchestrators.

Per the 2026-09-XX-orchestration-integration-v1 change
(Phase 11 §2 of the cianfhoghlaim-nua v6 era plan). Each of the 5
jurisdiction orchestrators at
``orchestration/defs/2_materials/{england,wales,scotland,
northern_ireland,isle_of_man}_education/<jur>_assets.py`` previously
used ``getattr(b, baml_fn_name, None)`` as a fallback — which silently
produced ``rows_extracted: 0`` when the per-jurisdiction BAML function
wasn't registered.

Phase 11 replaces that fallback with the canonical
``b.Extract<Jurisdiction>SubjectSpec(...)`` invocation. The functions
live at:

- ``baml_src/british_isles/en/education/en_extraction.baml::ExtractEnglandSubjectSpec``
- ``baml_src/british_isles/wl/education/wl_extraction.baml::ExtractWalesSubjectSpec``
- ``baml_src/british_isles/sc/education/sc_extraction.baml::ExtractScotlandSubjectSpec``
- ``baml_src/british_isles/ni/education/ni_extraction.baml::ExtractNorthernIrelandSubjectSpec``
- ``baml_src/british_isles/im/education/im_extraction.baml::ExtractIsleOfManSubjectSpec``

Each takes ``(pdf_text, subject_slug, stage, source_url) -> <Jur>SubjectSpec``.

This helper provides:

1. ``read_pdf_text(path)`` — extract raw text from a canonical PDF
   via ``pypdf`` (the canonical LC PDF reader; the same one the
   ``quest_pack_assets.py`` module uses).
2. ``materialise_subject_spec_to_convex(spec, ...)`` — write the
   extracted ``<Jur>SubjectSpec`` to the canonical Convex
   ``<jur>_subject_specs`` table. Degrades gracefully when the Convex
   client isn't available — matches the
   ``tuatha/badges/ledger.py`` graceful-degradation pattern used in
   ``orchestration/defs/2_materials/lc_extraction/quest_pack_assets.py``.
3. ``invoke_jurisdiction_extractor(...)`` — the thin async wrapper
   that wires the 3 steps together: read PDF → call
   ``b.Extract<Jurisdiction>SubjectSpec`` → materialise to Convex.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional imports — degrade gracefully when the canonical client isn't
# present (CI / dev / non-Dagster environments).
# ---------------------------------------------------------------------------

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
    from pypdf import PdfReader  # type: ignore[import-not-found]

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    PdfReader = None  # type: ignore[assignment,misc]


# ---------------------------------------------------------------------------
# Per-jurisdiction canonical BAML function names.
#
# Mirrors the function names declared in
# baml_src/british_isles/{en,wl,sc,ni,im}/education/<jur>_extraction.baml
# (each one is PascalCase + the suffix "SubjectSpec").
# ---------------------------------------------------------------------------

JURISDICTION_BAML_FUNCTIONS: dict[str, str] = {
    "england": "ExtractEnglandSubjectSpec",
    "wales": "ExtractWalesSubjectSpec",
    "scotland": "ExtractScotlandSubjectSpec",
    "northern_ireland": "ExtractNorthernIrelandSubjectSpec",
    "isle_of_man": "ExtractIsleOfManSubjectSpec",
}

# Per-jurisdiction Convex table names. Phase 11 adds 5 new tables to
# web/apps/cianfhoghlaim-nua/convex/schema.ts (the canonical Convex
# schema). The 13 currently-declared tables stay; the 5 new ones
# carry the extracted <Jur>SubjectSpec rows.
JURISDICTION_CONVEX_TABLES: dict[str, str] = {
    "england": "england_subject_specs",
    "wales": "wales_subject_specs",
    "scotland": "scotland_subject_specs",
    "northern_ireland": "northern_ireland_subject_specs",
    "isle_of_man": "isle_of_man_subject_specs",
}


def read_pdf_text(pdf_path: str | os.PathLike[str]) -> str:
    """Extract raw text from a PDF on disk.

    Raises FileNotFoundError if the file is missing; raises RuntimeError
    if pypdf isn't installed. Returns an empty string on pages that
    yield no extractable text (scanned image PDFs without OCR).
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"canonical PDF not found: {path}")
    if not PYPDF_AVAILABLE or PdfReader is None:
        raise RuntimeError("pypdf is not installed — cannot read PDF")
    reader = PdfReader(str(path))
    chunks: list[str] = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:  # noqa: BLE001
            text = ""
        if text:
            chunks.append(text)
    return "\n\n".join(chunks)


def get_jurisdiction_baml_fn(jurisdiction: str) -> Any:
    """Return ``b.Extract<Jurisdiction>SubjectSpec`` (or ``None`` if missing).

    This replaces the previous ``getattr(b, fn_name, None)`` fallback.
    Raises ValueError for unknown jurisdictions.
    """
    fn_name = JURISDICTION_BAML_FUNCTIONS.get(jurisdiction.lower())
    if not fn_name:
        raise ValueError(f"unknown jurisdiction: {jurisdiction!r}")
    if not BAML_AVAILABLE or b is None:
        logger.warning(
            "get_jurisdiction_baml_fn: baml_client is not importable; "
            "returning None for %s", jurisdiction,
        )
        return None
    fn = getattr(b, fn_name, None)
    if fn is None:
        logger.warning(
            "get_jurisdiction_baml_fn: b.%s is not registered in the "
            "BAML client (baml-cli generate may be needed)",
            fn_name,
        )
    return fn


def serialise_spec(spec: Any) -> dict[str, Any]:
    """Serialise a ``<Jur>SubjectSpec`` to a Convex-friendly dict.

    Handles both Pydantic v2 (``model_dump``) + v1 (``dict``), and
    returns ``{}`` for falsy / unknown types.
    """
    if spec is None:
        return {}
    if hasattr(spec, "model_dump"):
        try:
            return dict(spec.model_dump(exclude_none=True))
        except Exception:  # noqa: BLE001
            return {}
    if hasattr(spec, "dict"):
        try:
            return dict(spec.dict(exclude_none=True))
        except Exception:  # noqa: BLE001
            return {}
    if isinstance(spec, dict):
        return dict(spec)
    return {}


def materialise_subject_spec_to_convex(
    jurisdiction: str,
    subject_slug: str,
    spec: Any,
    *,
    pdf_path: Optional[str] = None,
    source_url: Optional[str] = None,
) -> bool:
    """Materialise an extracted ``<Jur>SubjectSpec`` into Convex.

    Returns True when the row was written, False on every graceful-
    degradation path (missing client, unreachable Convex, validator
    mismatch — all of these are logged + ignored, matching the
    ``quest_pack_assets.py::_write_quest_pack_to_convex`` pattern).
    """
    table_name = JURISDICTION_CONVEX_TABLES.get(jurisdiction.lower())
    if not table_name:
        logger.warning(
            "materialise_subject_spec_to_convex: unknown jurisdiction %r",
            jurisdiction,
        )
        return False
    serialised = serialise_spec(spec)
    if not serialised:
        logger.info(
            "materialise_subject_spec_to_convex: empty serialisation for "
            "%s/%s — skipping Convex write", jurisdiction, subject_slug,
        )
        return False

    try:
        from convex import ConvexClient  # type: ignore[import-not-found]
    except ImportError:
        return False

    try:
        client = ConvexClient(
            os.environ.get("CONVEX_URL", "http://localhost:3210"),
        )
        # Map the canonical SDK fields. Convex validators use camelCase
        # per the convex/server convention; the SDK serialises the
        # dict to the Convex mutation as JSON over HTTP.
        payload = {
            "subjectSlug": subject_slug,
            "jurisdiction": jurisdiction.lower(),
            "sourcePdf": pdf_path or "",
            "sourceUrl": source_url or "",
            "stage": serialised.get("stage", "LEAVING_CERT"),
            "displayName": serialised.get("display_name", ""),
            "displayNameGa": serialised.get("display_name_ga", ""),
            "displayNameLocal": serialised.get("display_name_local", ""),
            "awardDescriptor": serialised.get("award_descriptor", ""),
            "descriptorVocabulary": serialised.get(
                "descriptor_vocabulary", []
            ),
            "keyCompetencies": serialised.get("key_competencies", []),
            "language": serialised.get("language", "en"),
            "year": serialised.get("year", 0),
            "page": serialised.get("page", 0),
            "payloadJson": json.dumps(serialised),
            "createdAt": int(__import__("time").time() * 1000),
        }
        client.mutation(f"{table_name}:create", payload)
        return True
    except Exception as exc:  # noqa: BLE001
        # Convex reachable-but-erroring (e.g. schema mismatch before
        # deployment) must not fail the Dagster asset — the extraction
        # itself already succeeded and is returned in the asset's own
        # materialised output.
        logger.debug(
            "materialise_subject_spec_to_convex: Convex write skipped for "
            "%s/%s: %s", jurisdiction, subject_slug, exc,
        )
        return False


def invoke_jurisdiction_extractor(
    jurisdiction: str,
    pdf_path: str | os.PathLike[str],
    subject_slug: str,
    *,
    source_url: Optional[str] = None,
    stage: str = "LEAVING_CERT",
) -> dict[str, Any]:
    """Phase 11 orchestrator hot-path: read PDF → BAML extract → Convex.

    Returns a dict with:
      - "extracted": True/False
      - "spec": the serialised <Jur>SubjectSpec (or {})
      - "convex_written": True/False
      - "reason": human-readable reason when extracted=False
    """
    jur = jurisdiction.lower()
    fn = get_jurisdiction_baml_fn(jur)
    if fn is None:
        return {
            "extracted": False,
            "spec": {},
            "convex_written": False,
            "reason": "baml_function_not_registered",
        }
    try:
        pdf_text = read_pdf_text(pdf_path)
    except FileNotFoundError as exc:
        return {
            "extracted": False,
            "spec": {},
            "convex_written": False,
            "reason": str(exc),
        }
    except RuntimeError as exc:
        return {
            "extracted": False,
            "spec": {},
            "convex_written": False,
            "reason": str(exc),
        }
    if not pdf_text.strip():
        return {
            "extracted": False,
            "spec": {},
            "convex_written": False,
            "reason": "pdf_text_empty (scanned or encrypted PDF)",
        }
    try:
        spec = fn(
            pdf_text=pdf_text,
            subject_slug=subject_slug,
            stage=stage,
            source_url=source_url or "",
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "invoke_jurisdiction_extractor: b.%s failed for %s/%s: %s",
            JURISDICTION_BAML_FUNCTIONS.get(jur, "?"), jur, subject_slug, exc,
        )
        return {
            "extracted": False,
            "spec": {},
            "convex_written": False,
            "reason": f"baml_call_failed:{type(exc).__name__}",
        }
    serialised = serialise_spec(spec)
    convex_ok = materialise_subject_spec_to_convex(
        jur, subject_slug, spec,
        pdf_path=str(pdf_path), source_url=source_url,
    )
    return {
        "extracted": True,
        "spec": serialised,
        "convex_written": convex_ok,
        "reason": None,
    }


__all__ = [
    "BAML_AVAILABLE",
    "PYPDF_AVAILABLE",
    "JURISDICTION_BAML_FUNCTIONS",
    "JURISDICTION_CONVEX_TABLES",
    "read_pdf_text",
    "serialise_spec",
    "get_jurisdiction_baml_fn",
    "materialise_subject_spec_to_convex",
    "invoke_jurisdiction_extractor",
]
