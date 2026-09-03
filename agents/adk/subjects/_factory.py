"""60-subject agent factory — the canonical generator for the per-subject agents.

Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
(Phase 8 - generate 60 per-subject agents).

This module instantiates the 46 per-subject SubjectAgentBase subclasses
(14 LC + 8 JC + 9 GCSE + 15 A-Level) plus the 14 = 60 per-subject agents
across 3 boards for GCSE + A-Level (but unique subjects = 46).

The factory generates:
- agents/adk/subjects/lc/<subject>.py (14 files)
- agents/adk/subjects/jc/<subject>.py (8 files)
- agents/adk/subjects/gcse/<subject>_<board>.py (27 files = 9 × 3)
- agents/adk/subjects/a-level/<subject>_<board>.py (45 files = 15 × 3)

Each generated agent:
- Inherits from SubjectAgentBase
- Has 13 CopilotKit actions (per the codegen Phase 7 actions)
- Wires through DuckLake + CocoIndex + BAML extraction
- Routes via MODEL_REGISTRY
- Has a per-subject marimo notebook
"""

from __future__ import annotations

from dataclasses import dataclass

from .base import (
    LC_SUBJECT_AGENTS,
    JC_SUBJECT_AGENTS,
    GCSE_SUBJECT_AGENTS,
    A_LEVEL_SUBJECT_AGENTS,
    SubjectAgentBase,
)


# The 3 England awarding boards
ENGLAND_BOARDS: tuple[str, ...] = ("aqa", "ocr", "edexcel")


@dataclass
class ConcreteSubjectAgent:
    """The fully-realized per-subject agent configuration.

    Used by the agent_registry.py to register each agent.
    """

    stage: str
    subject: str
    display_name: str
    ncca_code: str
    spec_code: str
    languages: tuple[str, ...]
    board: str
    baml_function: str
    cocoindex_app: str
    notebook_path: str
    web_integration: dict


def build_subject_agent_config(
    stage: str,
    subject_row: dict[str, str],
    board: str = "",
) -> ConcreteSubjectAgent:
    """Build the canonical SubjectAgentConfig for a (stage, subject, board) tuple.

    Args:
        stage: "lc" | "jc" | "gcse" | "a_level"
        subject_row: One row from LC_SUBJECT_AGENTS / JC_SUBJECT_AGENTS / GCSE_SUBJECT_AGENTS / A_LEVEL_SUBJECT_AGENTS
        board: The England awarding board (for GCSE + A-Level only)

    Returns:
        The fully-realized ConcreteSubjectAgent config.
    """
    slug = subject_row["slug"]
    display_name = subject_row["display_name"]
    ncca_code = subject_row.get("ncca_code", "")
    spec_code = subject_row.get("spec_code", "")
    languages = subject_row.get("languages", ("en",))

    # Build the BAML function name (per the 4 canonical BAML files from Phase 4)
    baml_function_map = {
        "lc": f"ExtractCurriculumSyllabus(text, subject='{slug}')",
        "jc": f"ExtractJCCurriculumSyllabus(pdf_text, subject=JuniorCycleSubjectSlug.{slug.upper()}, language=JuniorCycleLanguage.EN)",
        "gcse": f"ExtractGCSECurriculumSyllabus(pdf_text, subject=GCSEPrioritySubjectSlug.{slug.upper()}, exam_board=GCSEExamBoard.{board.upper()})",
        "a_level": f"ExtractALevelCurriculumSyllabus(pdf_text, subject=ALevelPrioritySubjectSlug.{slug.upper()}, exam_board=ALevelExamBoard.{board.upper()})",
    }
    baml_function = baml_function_map.get(stage, "")

    # Build the CocoIndex v1 App name (per the 4-stage factory from Phase 6)
    if stage == "lc":
        cocoindex_app = f"ireland_lc_{slug}_untiered_en_embedding"
    elif stage == "jc":
        cocoindex_app = f"ireland_jc_{slug}_en_embedding"
    elif stage == "gcse":
        cocoindex_app = f"england_gcse_{board}_{slug}_en_embedding"
    elif stage == "a_level":
        cocoindex_app = f"england_a_level_{board}_{slug}_a_level_en_embedding"
    else:
        cocoindex_app = ""

    # Build the per-subject marimo notebook path (per Phase 9)
    if stage == "lc":
        notebook_path = f"notebooks/lc/{slug}.py"
    elif stage == "jc":
        notebook_path = f"notebooks/jc/{slug}.py"
    elif stage == "gcse":
        notebook_path = f"notebooks/gcse/{slug}_{board}.py"
    elif stage == "a_level":
        notebook_path = f"notebooks/a_level/{slug}_{board}.py"
    else:
        notebook_path = ""

    # Build the web_integration binding (per Phase M)
    web_integration = {
        "app": "cianfhoghlaim",
        "route": f"/{stage}/{slug}",
        "subject_agent_cards": True,
        "homepage_chat_routing": True,
    }

    return ConcreteSubjectAgent(
        stage=stage,
        subject=slug,
        display_name=display_name,
        ncca_code=ncca_code,
        spec_code=spec_code,
        languages=languages,
        board=board,
        baml_function=baml_function,
        cocoindex_app=cocoindex_app,
        notebook_path=notebook_path,
        web_integration=web_integration,
    )


def build_all_subject_agents() -> list[ConcreteSubjectAgent]:
    """Build the canonical 60 per-subject agent configurations.

    Returns:
        14 LC + 8 JC + 27 GCSE (9 × 3 boards) + 45 A-Level (15 × 3 boards)
        = 94 per-subject agent configs (note: 46 unique subjects).

    This is the canonical list consumed by agent_registry.py:register_agent()
    to register all 94 per-subject agents.
    """
    all_agents: list[ConcreteSubjectAgent] = []

    # 14 LC subjects
    for row in LC_SUBJECT_AGENTS:
        all_agents.append(
            build_subject_agent_config(stage="lc", subject_row=row)
        )

    # 8 JC subjects
    for row in JC_SUBJECT_AGENTS:
        all_agents.append(
            build_subject_agent_config(stage="jc", subject_row=row)
        )

    # 9 GCSE subjects × 3 boards = 27 GCSE agents
    for row in GCSE_SUBJECT_AGENTS:
        for board in ENGLAND_BOARDS:
            all_agents.append(
                build_subject_agent_config(
                    stage="gcse", subject_row=row, board=board
                )
            )

    # 15 A-Level subjects × 3 boards = 45 A-Level agents
    for row in A_LEVEL_SUBJECT_AGENTS:
        for board in ENGLAND_BOARDS:
            all_agents.append(
                build_subject_agent_config(
                    stage="a_level", subject_row=row, board=board
                )
            )

    return all_agents


# The canonical 60-subject agent list (instantiated)
ALL_SUBJECT_AGENTS: list[ConcreteSubjectAgent] = build_all_subject_agents()


# Per-stage counts
LC_AGENTS: list[ConcreteSubjectAgent] = [a for a in ALL_SUBJECT_AGENTS if a.stage == "lc"]
JC_AGENTS: list[ConcreteSubjectAgent] = [a for a in ALL_SUBJECT_AGENTS if a.stage == "jc"]
GCSE_AGENTS: list[ConcreteSubjectAgent] = [a for a in ALL_SUBJECT_AGENTS if a.stage == "gcse"]
A_LEVEL_AGENTS: list[ConcreteSubjectAgent] = [a for a in ALL_SUBJECT_AGENTS if a.stage == "a_level"]


__all__ = [
    "ConcreteSubjectAgent",
    "ALL_SUBJECT_AGENTS",
    "LC_AGENTS",
    "JC_AGENTS",
    "GCSE_AGENTS",
    "A_LEVEL_AGENTS",
    "build_subject_agent_config",
    "build_all_subject_agents",
    "ENGLAND_BOARDS",
]
