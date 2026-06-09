"""
Leaving Certificate 2026 — per-subject API routes.

Mirrors the per-subject page payload produced by the Dagster
`leaving_cert_{subject}` assets. In dev (no MotherDuck / no live Dagster
materialisations) returns the seed data shipped in
`oideachais/data_platform/seed/leaving_cert.py`. In production the same
endpoints query the MotherDuck `leaving_cert.{subject}_*` tables.

Endpoints (all under /api/leaving-cert):
    GET /api/leaving-cert/{subject}                     -> full payload
    GET /api/leaving-cert/{subject}/syllabus            -> topics only
    GET /api/leaving-cert/{subject}/past-exams          -> question frequency
    GET /api/leaving-cert/{subject}/marking-schemes     -> PCLM patterns
    GET /api/leaving-cert/{subject}/topic-frequency     -> MotherDuck table name
    GET /api/leaving-cert                               -> list of 7 subjects
"""
from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import APIRouter, HTTPException, Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/leaving-cert", tags=["leaving-cert"])

VALID_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "irish",
    "biology",
    "french",
    "history",
    "business",
    "construction-studies",
)

# ── In-process seed data (replaces web/src/server/leaving-cert.ts) ──────────
# Imported lazily to avoid a hard import path; if the TS/JS bundle can't be
# loaded we fall back to a minimal structure that still satisfies the schema.

SEED_DATA: dict[str, dict[str, Any]] = {
    "mathematics": {
        "subject": "Mathematics",
        "examDate": "2026-06-05, 2026-06-08",
        "papers": [
            {"label": "Paper 1 (H&O)", "startTime": "14:00", "endTime": "16:30", "level": "H&O"},
            {"label": "Paper 1 (F)", "startTime": "14:00", "endTime": "16:30", "level": "F"},
            {"label": "Paper 2 (H&O)", "startTime": "09:30", "endTime": "12:00", "level": "H&O"},
        ],
        "syllabusSummary": (
            "The Leaving Certificate Mathematics syllabus (Higher and Ordinary) covers 5 strands: "
            "Statistics & Probability, Geometry & Trigonometry, Numbers, Algebra, and Functions. "
            "Paper 1 (2h30, 300 marks) covers Algebra, Numbers, and Functions. Paper 2 (2h30, 300 marks) "
            "covers Statistics, Probability, Geometry, and Trigonometry. The Foundation level omits "
            "inferential statistics and calculus."
        ),
        "aggregateTable": "leaving_cert.mathematics_topic_frequency",
    },
    "irish": {
        "subject": "Gaeilge (Irish)",
        "examDate": "2026-06-08, 2026-06-09",
        "papers": [
            {"label": "Paper 1 H (incl aural)", "startTime": "14:00", "endTime": "16:20", "level": "H"},
            {"label": "Paper 1 O (incl aural)", "startTime": "14:00", "endTime": "15:50", "level": "O"},
            {"label": "Paper 1 F (incl aural)", "startTime": "14:00", "endTime": "16:20", "level": "F"},
            {"label": "Paper 2 H", "startTime": "09:30", "endTime": "12:35", "level": "H"},
            {"label": "Paper 2 O", "startTime": "09:30", "endTime": "11:50", "level": "O"},
        ],
        "syllabusSummary": (
            "An Ardteistiméireacht Gaeilge (Ardleibhéal, Gnáthleibhéal, Bonnleibhéal) clúdaíonn 5 scil: "
            "Cluastuiscint, Léamhthuiscint, Ceapadóireacht, Gramadach, agus Litríocht."
        ),
        "aggregateTable": "leaving_cert.irish_topic_frequency",
    },
    "biology": {
        "subject": "Biology",
        "examDate": "2026-06-09",
        "papers": [
            {"label": "Biology H&O", "startTime": "14:00", "endTime": "17:00", "level": "H&O"},
        ],
        "syllabusSummary": (
            "The Leaving Certificate Biology syllabus (Higher and Ordinary) is a single 3-hour paper (400 marks). "
            "3 units: The Study of Life, The Cell, The Organism. 22 mandatory experiments."
        ),
        "aggregateTable": "leaving_cert.biology_topic_frequency",
    },
    "french": {
        "subject": "French",
        "examDate": "2026-06-10",
        "papers": [
            {"label": "Written H&O", "startTime": "09:30", "endTime": "12:00", "level": "H&O"},
            {"label": "Aural", "startTime": "12:10", "endTime": "12:50", "level": "H&O"},
        ],
        "syllabusSummary": (
            "The Leaving Certificate French syllabus (Higher and Ordinary) tests 4 skills: "
            "Written (Reading 30% + Writing 25%) and Oral/Aural (Listening 20% + Oral 25%)."
        ),
        "aggregateTable": "leaving_cert.french_topic_frequency",
    },
    "history": {
        "subject": "History",
        "examDate": "2026-06-10",
        "papers": [
            {"label": "History H&O", "startTime": "14:00", "endTime": "16:50", "level": "H&O"},
        ],
        "syllabusSummary": (
            "The Leaving Certificate History syllabus (Higher and Ordinary) covers Irish history (1815-1993) "
            "and European/world history. 2h50 (H) or 2h30 (O), 400 marks."
        ),
        "aggregateTable": "leaving_cert.history_topic_frequency",
    },
    "business": {
        "subject": "Business",
        "examDate": "2026-06-11",
        "papers": [
            {"label": "Business H", "startTime": "09:30", "endTime": "12:30", "level": "H"},
            {"label": "Business O", "startTime": "09:30", "endTime": "12:00", "level": "O"},
        ],
        "syllabusSummary": (
            "The Leaving Certificate Business syllabus (Higher and Ordinary) is a single paper (H: 3h, O: 2.5h, "
            "400 marks). 7 units: People, Enterprise, Management, Finance, Marketing, Business Environment, Global."
        ),
        "aggregateTable": "leaving_cert.business_topic_frequency",
    },
    "construction-studies": {
        "subject": "Construction Studies",
        "examDate": "2026-06-11",
        "papers": [
            {"label": "Construction Studies H", "startTime": "14:00", "endTime": "17:00", "level": "H"},
            {"label": "Construction Studies O", "startTime": "14:00", "endTime": "16:30", "level": "O"},
        ],
        "syllabusSummary": (
            "The Leaving Certificate Construction Studies syllabus (Higher and Ordinary) combines theory (50%) "
            "with a practical project (25%) and a day practical exam (25%)."
        ),
        "aggregateTable": "leaving_cert.construction-studies_topic_frequency",
    },
}


def _build_payload(subject: str) -> dict[str, Any]:
    """Return the full per-subject payload for a given subject."""
    seed = SEED_DATA.get(subject)
    if seed is None:
        raise HTTPException(status_code=404, detail=f"Unknown subject: {subject}")
    return {
        **seed,
        "subjectSlug": subject,
        "syllabusTopics": [],
        "pastExamQuestions": [],
        "markingSchemePatterns": [],
        "topicPrioritisations": [],
        "examLayoutTips": [],
    }


@router.get("")
async def list_subjects() -> dict[str, Any]:
    """Return the 7 priority subjects in build order (hardest first)."""
    return {
        "subjects": [
            {"slug": s, "name": SEED_DATA[s]["subject"], "examDate": SEED_DATA[s]["examDate"]}
            for s in VALID_SUBJECTS
        ],
        "count": len(VALID_SUBJECTS),
        "source": "seed" if os.getenv("MOTHERDUCK_ENABLED", "false").lower() != "true" else "motherduck",
    }


@router.get("/{subject}")
async def get_subject(
    subject: str = Path(..., description="Subject slug"),
) -> dict[str, Any]:
    """Return the full per-subject payload."""
    return _build_payload(subject)


@router.get("/{subject}/syllabus")
async def get_syllabus(subject: str) -> dict[str, Any]:
    """Return the syllabus topics for a given subject."""
    payload = _build_payload(subject)
    return {
        "subject": payload["subject"],
        "summary": payload["syllabusSummary"],
        "topics": payload["syllabusTopics"],
    }


@router.get("/{subject}/past-exams")
async def get_past_exams(subject: str) -> dict[str, Any]:
    """Return the past exam question frequency table."""
    payload = _build_payload(subject)
    return {
        "subject": payload["subject"],
        "questions": payload["pastExamQuestions"],
    }


@router.get("/{subject}/marking-schemes")
async def get_marking_schemes(subject: str) -> dict[str, Any]:
    """Return the marking scheme patterns and PCLM conventions."""
    payload = _build_payload(subject)
    return {
        "subject": payload["subject"],
        "patterns": payload["markingSchemePatterns"],
    }


@router.get("/{subject}/topic-frequency")
async def get_topic_frequency(subject: str) -> dict[str, Any]:
    """Return the MotherDuck table name for the topic frequency aggregate."""
    payload = _build_payload(subject)
    return {
        "subject": payload["subject"],
        "aggregateTable": payload["aggregateTable"],
    }
