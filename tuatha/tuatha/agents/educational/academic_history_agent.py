"""tuatha.agents.educational.academic_history_agent — the cross-archive academic history agent.

Per the parent's `agents/meaisinfhoghlaim/educational/academic_history_agent.py`
pattern: the cross-subject + cross-jurisdiction history research
agent. Routes queries to the Wikipedia + CELT + Dúchas / Gaois
corpora via the BAML `qpack_academic_history.baml` contract.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent

from ...config import TuathaConfig
from ...routing import build_wire

_wire = build_wire(
    ncca_subject="academic_history",
    module_slug="academic_history",
    display_name="Academic History",
    baml_prefix="AcadHist",
    langfuse_trace_name="agent.academic_history.<verb>",
    cognee_dataset="oideachais_academic_history",
    letta_agent_id="kcg-academic-history-agent",
)

config = TuathaConfig.from_env()


academic_history_agent = LlmAgent(
    name="academic_history_agent",
    model=config.litellm.resolve_model("text_llm", "default"),
    description=(
        "Cross-archive academic history research agent for the "
        "British Isles MMO. Routes queries to the Wikipedia + CELT + "
        "Dúchas / Gaois corpora via the BAML "
        "`qpack_academic_history.baml` contract."
    ),
    instruction=(
        "You are the academic history specialist agent. You "
        "handle cross-archive academic history research queries "
        "for the British Isles MMO. Route keyword-level traffic "
        "to the Wikipedia + CELT + Dúchas / Gaois corpora and "
        "emit typed BAML responses per the `qpack_academic_history.baml` "
        "contract."
    ),
    output_key="academic_history_response",
)


__all__ = ["_wire", "academic_history_agent", "config"]
