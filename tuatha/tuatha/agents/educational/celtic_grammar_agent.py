"""tuatha.agents.educational.celtic_grammar_agent — the Celtic grammar specialist agent.

Handles queries about the grammar of the 6 Celtic languages
(Irish + Welsh + Scottish Gaelic + Breton + Cornish + Manx).
Routes via the BAML `qpack_celtic_grammar.baml` contract.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent

from ...config import TuathaConfig
from ...routing import build_wire

_wire = build_wire(
    ncca_subject="celtic_grammar",
    module_slug="celtic_grammar",
    display_name="Celtic Grammar",
    baml_prefix="CeltGram",
    langfuse_trace_name="agent.celtic_grammar.<verb>",
    cognee_dataset="oideachais_celtic_grammar",
    letta_agent_id="kcg-celtic-grammar-agent",
)

config = TuathaConfig.from_env()


celtic_grammar_agent = LlmAgent(
    name="celtic_grammar_agent",
    model=config.litellm.resolve_model("text_llm", "default"),
    description=(
        "Celtic grammar specialist agent for the 6 Celtic "
        "languages (Irish + Welsh + Scottish Gaelic + Breton + "
        "Cornish + Manx). Grammar forms + dialectical variants + "
        "literary citations."
    ),
    instruction=(
        "You are the Celtic grammar specialist agent. You handle "
        "queries about the grammar of the 6 Celtic languages. "
        "Route keyword-level traffic and emit typed BAML responses "
        "per the `qpack_celtic_grammar.baml` contract."
    ),
    output_key="celtic_grammar_response",
)


__all__ = ["_wire", "celtic_grammar_agent", "config"]
