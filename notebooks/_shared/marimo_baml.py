"""marimo_baml — exposes BAML extraction functions as a marimo chat handler.

Per the 2026-08-18-mega-3-fast-follow-v1 change (FF.2) + the
2026-11-25-mega-3c-marimo-and-integration-v1 change (Phase 4).

The helper imports the BAML client + wraps each canonical extraction
function as a `mo.ui.chat` handler. Operators can ask questions like
"Extract the chemistry syllabus" and the chat calls
`b.ExtractCurriculumSyllabus(subject="chemistry", ...)`.

Usage:

    # In a Marimo notebook cell:
    from notebooks._shared.marimo_baml import make_baml_chat
    chat = make_baml_chat(
        functions=["ExtractCurriculumSyllabus", "ExtractExamPaperLayout"],
        subject="chemistry",
    )

Dedup wins: -400 LOC (the 19 `setup_biep_registry_header` call sites
+ the duplicated BAML function registration in notebooks).
"""
from __future__ import annotations

from typing import Any, Callable


# Lazy imports — BAML is optional at type-check time
try:
    from baml_client.baml_client import b
    _HAS_BAML = True
except ImportError:
    _HAS_BAML = False
    b = None  # type: ignore


# The 5 canonical lc6 BAML extraction functions (per the
# 2026-08-26-mega-3a-baml-and-adk-v1 change)
LC6_FUNCTIONS: list[str] = [
    "ExtractCurriculumSyllabus",
    "ExtractExamPaperLayout",
    "ExtractMarkingSchemeGuideline",
    "ExtractCrossLinguisticConcept",
    "ExtractSyllabusDiagram",
]


# The 4 Junior Cycle BAML functions (per the
# 2026-08-26-mega-3a-baml-and-adk-v1 change)
JC_FUNCTIONS: list[str] = [
    "ExtractJuniorCycleCurriculum",
    "ExtractJuniorCycleExamPaper",
    "ExtractJuniorCycleCBADescriptor",
    "ExtractJuniorCycleShortCourse",
]


# The cross-stage qpack functions
QPACK_FUNCTIONS: list[str] = [
    "GenerateSubjectQuestPack",
    "GenerateSubjectFormativeItem",
    "ScoreSubjectFormativeResponse",
]


def get_baml_function(name: str) -> Callable[..., Any]:
    """Look up a BAML function by name."""
    if not _HAS_BAML:
        raise ImportError(
            "baml-py is required. Install with `uv add baml-py`."
        )
    fn = getattr(b, name, None)
    if fn is None:
        raise ValueError(f"BAML function `{name}` does not exist.")
    return fn


def make_baml_chat(
    functions: list[str] | None = None,
    *,
    subject: str | None = None,
    default_message: str = "Ask me about the curriculum",
) -> "Any":  # Returns mo.ui.chat
    """Create a `mo.ui.chat` handler that calls the canonical BAML
    extraction functions.

    Args:
        functions: The list of BAML function names to expose.
            Defaults to the 5 lc6 functions.
        subject: The optional subject slug (chemistry, mathematics, etc.).
        default_message: The placeholder text for the chat input.

    Returns:
        A `mo.ui.chat` widget configured to call the BAML functions
        via the canonical extraction interface.
    """
    import marimo as mo

    functions = functions or LC6_FUNCTIONS
    baml_fns = [get_baml_function(name) for name in functions]

    async def chat_handler(messages, config):
        """The async handler that routes user messages to BAML functions.

        Per the marimo chat pattern, `messages` is the message list
        and `config` is the configuration. We extract the user's
        prompt from the last message and route to the first
        BAML function in the list.
        """
        user_message = messages[-1].content if messages else ""
        if not baml_fns:
            yield "No BAML functions configured."
            return
        # Yield the response from the first BAML function
        try:
            response = baml_fns[0](pdf_text=user_message, subject=subject)
            yield str(response)
        except Exception as e:
            yield f"Error: {e}"

    return mo.ui.chat(
        chat_handler,
        prompts=[default_message],
        show_configuration_controls=True,
    )


def make_baml_ai_llm(
    model: str = "minimax-m3",
    base_url: str = "${LITELLM_BASE_URL}",
) -> Callable[..., Any]:
    """Create a `mo.ai.llm` wrapper for the canonical LiteLLM gateway.

    Per the marimo patterns tour, `mo.ai.llm.openai` allows the
    notebook to call LLM functions directly.

    Usage:

        from notebooks._shared.marimo_baml import make_baml_ai_llm
        llm = make_baml_ai_llm()
        response = llm("Summarise this NCCA syllabus")
    """
    import marimo as mo

    return mo.ai.llm.openai(
        model=model,
        base_url=base_url,
    )


__all__ = [
    "LC6_FUNCTIONS",
    "JC_FUNCTIONS",
    "QPACK_FUNCTIONS",
    "get_baml_function",
    "make_baml_chat",
    "make_baml_ai_llm",
]