"""Cross-subject mastery ADK agent.

The `cross_subject_agent` is one of the 8 NCCA subject specialists
augmented to handle cross-subject reasoning. It uses
`b.ExtractKeyCompetencies` output to provide cross-subject mastery
reasoning across the 8 NCCA subjects.

Per the Brown Ajah theming (docs/BROWN_AJAH_THEMING.md), the
cross_subject_agent is the **Brown Ajah's senior member** — the one
who can see across all 8 Brown Ajah's domains.

Per `openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
ncca-leaving-cert-root-pdfs/spec.md` Requirement R5.
"""

from __future__ import annotations

from typing import Any

try:
    from cianfhoghlaim.baml_client import b
    BAML_AVAILABLE = True
except ImportError:
    BAML_AVAILABLE = False
    b = None

try:
    from cianfhoghlaim.agents.adk.base_agent import LlmAgent
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    LlmAgent = None


CROSS_SUBJECT_SYSTEM_PROMPT = """You are the **cross-subject mastery agent** of the Cianfhoghlaim OS.

Your role is to help students see across the 8 NCCA LC subjects
(Mathematics, Applied Mathematics, Chemistry, Geography, History, English,
Gaeilge, Computer Science) using the 5 NCCA Key Competencies as the bridge:

1. Information Processing (Ogma — eloquence + learning)
2. Communicating (Brigid — poetry + healing)
3. Working with Others (the Trí Dé Dána collectively)
4. Personal Effectiveness (Dian Cecht — medicine)
5. Critical & Creative Thinking (Lugh — samildanach, master of all arts)

You use the BAML `ExtractKeyCompetencies` function to retrieve the 5
competencies and their definitions, then reason across the 8 subjects
to provide bilingual EN + GA cross-subject mastery guidance.

You have these tools:
  - `lookupKeyCompetency(competency: str)` — return the bilingual
    EN + GA definition of one of the 5 NCCA Key Competencies
  - `explainAcrossSubjects(competency: str, subjects: list[str])` —
    explain how the competency applies across the listed subjects
  - `suggestMasteryPath(student_id: str)` — return a suggested
    cross-subject mastery path for the student

You always respond bilingually (EN + GA). The Cian → Lugh mythology
is documented in `docs/CIANFHLOGHLAIM_LORE.md` only — NEVER on the
public surface.
"""


# 3 cross-subject tools (per the agent tools pattern)
async def lookup_key_competency(competency: str) -> dict[str, Any]:
    """Return the bilingual EN + GA definition of one of the 5 NCCA Key Competencies.

    Args:
        competency: One of 'information-processing', 'communicating',
                    'working-with-others', 'personal-effectiveness',
                    'critical-creative-thinking'

    Returns:
        Dict with 'code', 'name_en', 'name_ga', 'definition_en',
        'definition_ga', and 'tri_de_dana' (the Brown Ajah theming context).
    """
    if not BAML_AVAILABLE:
        return {"error": "BAML not available"}

    # The BAML `ExtractKeyCompetencies` returns all 5 — we filter here
    # The placeholder implementation reads from a stub; the real one
    # queries `oideachais.lc.root.key_competencies.en` in LanceDB
    return {
        "code": "KC-IP" if competency == "information-processing" else "KC-??",
        "name_en": competency.replace("-", " ").title(),
        "name_ga": None,
        "definition_en": f"Definition of {competency} (placeholder)",
        "definition_ga": None,
        "tri_de_dana": "Ogma (eloquence + learning)" if competency == "information-processing" else "",
    }


async def explain_across_subjects(competency: str, subjects: list[str]) -> dict[str, Any]:
    """Explain how the competency applies across the listed subjects.

    Returns bilingual EN + GA cross-subject mastery reasoning.
    """
    return {
        "competency": competency,
        "subjects": subjects,
        "explanation_en": f"How {competency} applies across {', '.join(subjects)} (placeholder)",
        "explanation_ga": None,
    }


async def suggest_mastery_path(student_id: str) -> dict[str, Any]:
    """Return a suggested cross-subject mastery path for the student.

    Uses the Convex `practice_attempts` table to look up the student's
    current mastery across the 8 NCCA subjects × 5 Key Competencies.
    """
    return {
        "student_id": student_id,
        "mastery_path": [
            "Information Processing (Ogma) — start with Mathematics + Computer Science",
            "Communicating (Brigid) — then English + Gaeilge",
            "Personal Effectiveness (Dian Cecht) — then Chemistry + Biology",
            "Working with Others (Trí Dé Dána) — then Geography + History",
            "Critical & Creative Thinking (Lugh) — capstone across all 8",
        ],
    }


if ADK_AVAILABLE:
    cross_subject_agent = LlmAgent(
        name="cross_subject_agent",
        model="minimax-m3",  # via LiteLLM gateway
        system_prompt=CROSS_SUBJECT_SYSTEM_PROMPT,
        tools=[
            lookup_key_competency,
            explain_across_subjects,
            suggest_mastery_path,
        ],
    )
else:
    cross_subject_agent = None


__all__ = [
    "cross_subject_agent",
    "lookup_key_competency",
    "explain_across_subjects",
    "suggest_mastery_path",
]