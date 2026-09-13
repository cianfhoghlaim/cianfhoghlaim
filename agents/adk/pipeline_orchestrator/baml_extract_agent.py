"""BAML extract agent — calls a BAML extraction function on each row.

Per the openspec change
`2026-09-06-adk-gemini-deep-research-control-plane-v1`. Pairs with the
:class:`pipeline_orchestrator` LoopAgent quality loop.
"""

from __future__ import annotations

from typing import Any

from google.adk.tools import FunctionTool

from ..litellm_agent import make_litellm_agent

DEFAULT_BAML_FUNCTION = "ExtractGeminiDeepResearchReport"


def extract_baml_function(
    function_name: str,
    text: str,
    *,
    client_alias: str | None = None,
) -> dict[str, Any]:
    """Invoke a BAML extraction function on a single text input.

    Args:
        function_name: The BAML function name (e.g.
            ``"ExtractGeminiDeepResearchReport"``).
        text: The raw text to extract from.
        client_alias: Optional BAML client alias (defaults to the
            ``ExtractEn`` LiteLlm client that routes through the
            canonical 7-tier fallback chain).

    Returns:
        ``dict`` with ``function``, ``result`` (the BAML-extracted
        object as a dict), and ``quality_score`` (0.0-1.0).

    Raises:
        ImportError: If the BAML client module is not generated yet.
    """
    try:
        from baml_client import b
    except ImportError as exc:
        raise ImportError(
            "baml_client module not generated. Run `mise run baml:generate` "
            "from the repo root before invoking BAMLFunctionTool."
        ) from exc

    func = getattr(b, function_name, None)
    if func is None:
        raise ValueError(
            f"BAML function '{function_name}' not found in baml_client.b. "
            f"Available functions: {[n for n in dir(b) if not n.startswith('_')][:20]}..."
        )

    if client_alias:
        result = func(input=text, baml_options={"client_alias": client_alias})
    else:
        result = func(text)

    quality_score = _estimate_quality_score(result)

    return {
        "function": function_name,
        "result": result.model_dump() if hasattr(result, "model_dump") else dict(result),
        "quality_score": quality_score,
    }


def _estimate_quality_score(result: Any) -> float:
    """Estimate an extraction quality score in [0.0, 1.0].

    The BAML function's own assertions / catch blocks contribute most
    of the signal; this is a defensive estimate for the
    `extract_quality_loop` retry trigger.
    """
    if result is None:
        return 0.0
    if hasattr(result, "quality_score") and result.quality_score is not None:
        return float(result.quality_score)
    if hasattr(result, "model_dump"):
        data = result.model_dump()
    elif isinstance(result, dict):
        data = result
    else:
        data = {"value": result}

    total_fields = 0
    populated_fields = 0
    for key, value in data.items():
        if key.startswith("_"):
            continue
        total_fields += 1
        if value not in (None, "", [], {}):
            populated_fields += 1
    if total_fields == 0:
        return 1.0
    return populated_fields / total_fields


baml_extract_agent = make_litellm_agent(
    name="baml_extract_agent",
    description=(
        "Invokes a BAML extraction function on a single text input and "
        "estimates an extraction quality score. Per the "
        "2026-09-06-adk-gemini-deep-research-control-plane-v1 change."
    ),
    model_alias="minimax",
    temperature=0.2,
    max_output_tokens=4096,
    instruction=(
        "You are the BAML extract agent. Given a `function_name` (e.g. "
        "`ExtractGeminiDeepResearchReport`) and a `text` input, call the "
        "BAML function via the `baml_client.b` module. "
        "If the returned `quality_score < 0.6`, escalate to the "
        "`extract_quality_loop` which retries through the 4-tier provider "
        "chain (Unsloth → LiteLLM → MiniMax → Gemini). "
        "Every invocation MUST be wrapped in a Langfuse `@observe` "
        "decorator so the BAML function call appears as a child span."
    ),
    tools=[FunctionTool(extract_baml_function)],
    output_key="baml_extraction_result",
)


__all__ = ["DEFAULT_BAML_FUNCTION", "baml_extract_agent", "extract_baml_function"]
