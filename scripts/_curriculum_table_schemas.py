from __future__ import annotations

from typing import Literal, TypedDict

GeographyLevel = Literal["higher", "ordinary", "foundation"]
Language = Literal["en", "ga"]


class GeographyTopicRow(TypedDict):
    topic_id: str
    subject_slug: Literal["geography"]
    level: GeographyLevel
    language: Language
    title: str
    topic_phrase: str
    learning_outcomes: list[str]
    source_pdf: str
    source_page: int
    source_url: str
    extracted_at: str
    stub: bool


class GaeilgePoemRow(TypedDict):
    poem_id: str
    poet: str
    title_ga: str
    title_en: str
    collection: str
    year: int | None
    prescribed_period: str
    theme_or_issue: str
    source_pdf: str
    source_page: int
    source_url: str
    provenance_pdf: str | None
    extracted_at: str
    stub: bool


class EnglishPoetRow(TypedDict):
    poet_id: str
    poet_name: str
    work_title: str
    prescribed_period: str
    theme_or_issue: str
    cultural_context: str
    literary_genre: str
    general_vision: str
    source_pdf: str
    source_page: int
    extracted_at: str
    stub: bool


class EducationPolicyRow(TypedDict):
    policy_id: str
    policy_name: str
    policy_slug: str
    publish_year: int | None
    summary: str
    key_clauses: list[str]
    source_pdf: str
    source_url: str
    extracted_at: str
    stub: bool


TABLE_SCHEMAS: dict[str, type] = {
    "geography_topics": GeographyTopicRow,
    "gaeilge_poems_higher": GaeilgePoemRow,
    "english_poets_higher": EnglishPoetRow,
    "education_ie_policies": EducationPolicyRow,
}


PRIMARY_KEYS: dict[str, tuple[str, ...]] = {
    "geography_topics": (
        "source_pdf",
        "source_page",
        "source_url",
    ),
    "gaeilge_poems_higher": (
        "source_pdf",
        "source_page",
        "source_url",
    ),
    "english_poets_higher": (
        "source_pdf",
        "source_page",
        "source_url",
    ),
    "education_ie_policies": (
        "source_pdf",
        "source_page",
        "source_url",
    ),
}


CANONICAL_TABLE_NAMES: dict[str, str] = {
    "geography_topics": "cianfhoghlaim.lc.geography.topics",
    "gaeilge_poems_higher": "cianfhoghlaim.lc.gaeilge.poems_higher",
    "english_poets_higher": "cianfhoghlaim.lc.english.poets_higher",
    "education_ie_policies": "cianfhoghlaim.education.ie.policies",
}


__all__ = [
    "CANONICAL_TABLE_NAMES",
    "PRIMARY_KEYS",
    "TABLE_SCHEMAS",
    "EducationPolicyRow",
    "EnglishPoetRow",
    "GaeilgePoemRow",
    "GeographyLevel",
    "GeographyTopicRow",
    "Language",
]
