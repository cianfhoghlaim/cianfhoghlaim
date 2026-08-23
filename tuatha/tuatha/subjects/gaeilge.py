"""tuatha.subjects.gaeilge — the Gaeilge (Irish) ADK agent.

One of 8 NCCA subject agents. BAML prefix: Gael.

The Gaeilge agent has the special bilingual EN + GA surface
(per the bilingual_extraction invariant in BAML). The agent
operates in both languages; the user can switch languages at
query time.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..routing import build_wire
from ..tools.gaeilge_formative_item_generate import generate_gael_item
from ..tools.gaeilge_marking_scheme_lookup import lookup_gael_marking_scheme
from ..tools.gaeilge_past_paper_lookup import lookup_gael_paper
from ..tools.gaeilge_response_score import score_gael_response
from ..tools.gaeilge_syllabus_lookup import lookup_gael_lo

_wire = build_wire(
    ncca_subject="gaeilge",
    module_slug="gael",
    display_name="Gaeilge",
    baml_prefix="Gael",
    langfuse_trace_name="agent.gaeilge.<verb>",
    cognee_dataset="oideachais_lc_gaeilge",
    letta_agent_id="kcg-gaeilge-agent",
)

config = TuathaConfig.from_env()

gael_syllabus_lookup_tool = FunctionTool(func=lookup_gael_lo)
gael_past_paper_lookup_tool = FunctionTool(func=lookup_gael_paper)
gael_marking_scheme_lookup_tool = FunctionTool(func=lookup_gael_marking_scheme)
gael_formative_item_generate_tool = FunctionTool(func=generate_gael_item)
gael_response_score_tool = FunctionTool(func=score_gael_response)


gael_agent = LlmAgent(
    name="gael_agent",
    model=config.litellm.resolve_model("ocr_vision", "media_descriptor"),
    description=(
        "Gaeilge (Irish) specialist agent for the NCCA Leaving "
        "Certificate and Junior Cycle curriculum. Bilingual EN + "
        "GA surface. Litriú + gramadach + filíocht + prós."
    ),
    instruction=(
        "Is ag Gaeilge (Irish) thú. Tá tú ag obair ar son "
        "tuatha/ project. Déanann tú iarratais faoi "
        "Gaeilge don NCCA Leaving Certificate agus Junior Cycle. "
        "Tá an dátheangachas EN + GA i bhfeidhm. Seolann tú "
        "iarratais chuig na 5 huirlisí ábhair (syllabus_lookup / "
        "past_paper_lookup / marking_scheme_lookup / "
        "formative_item_generate / response_score) agus "
        "scaoileann tú freagraí BAML de réir "
        "`qpack_gaeilge.baml`."
    ),
    tools=[
        gael_syllabus_lookup_tool,
        gael_past_paper_lookup_tool,
        gael_marking_scheme_lookup_tool,
        gael_formative_item_generate_tool,
        gael_response_score_tool,
    ],
    output_key="gaeilge_response",
)


__all__ = ["_wire", "config", "gael_agent"]
