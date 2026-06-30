"""Generator script: emit one L5 CelticAgentOpsComponent YAML defs file
per agent in the 12-agent fleet. Run as
`python3 scripts/_gen_l5_agent_ops_defs.py`.

Each emitted file lives at
`cianfhoghlaim/dagster/defs/5_agent_ops/{framework}/<agent_name>/defs.yaml`
and contains the canonical CelticAgentOpsComponent YAML.
"""
from __future__ import annotations

from pathlib import Path


# The 12-agent fleet (per the agent-fleet-orchestration skill).
# Each tuple: (framework, agent_name, tools, routing_keywords).
# (pipecat / voice_agent is deferred to a follow-on change.)
AGENTS = [
    # 1 custom
    ("custom", "root_agent", [], []),
    # 8 ADK
    ("adk", "curriculum_agent",
     ["search_curriculum_tool", "get_vocabulary_tool", "translate_text_tool", "get_learning_outcomes_tool"],
     ["curriculum", "spec", "learning outcome", "ncca", "cfe", "cfw", "ccea", "sqa", "leaving cert", "gcse", "a-level"]),
    ("adk", "translation_agent",
     ["translate_text_tool", "detect_language_tool"],
     ["translate", "gaeilge", "irish", "scottish gaelic", "welsh", "cymraeg", "brezhoneg", "cornish", "manx"]),
    ("adk", "corpus_agent",
     ["search_corpus_tool", "get_duchas_entry_tool", "get_tearma_term_tool"],
     ["corpus", "duchas", "gaois", "tearma", "logainm", "canuint", "foclóir"]),
    ("adk", "research_agent",
     ["search_arxiv_tool", "search_doi_tool", "cite_paper_tool"],
     ["research", "paper", "cite", "doi", "arxiv"]),
    ("adk", "geospatial_agent",
     ["map_query_tool", "school_location_tool", "dialect_region_tool"],
     ["geospatial", "lsoa", "data zone", "map", "school location"]),
    ("adk", "statistics_agent",
     ["education_metric_tool", "benchmark_tool", "kpi_query_tool"],
     ["statistics", "metric", "benchmark", "performance", "kpi"]),
    ("adk", "curriculum_comparison_agent",
     ["compare_curricula_tool", "cross_nation_lookup_tool"],
     ["compare", "cross-nation", "side-by-side", "uk vs ireland"]),
    ("adk", "mcp_curriculum_agent",
     ["mcp_tool_dispatch_tool", "mcp_session_manager_tool"],
     ["mcp", "model context protocol", "tool"]),
    # 3 Agno
    ("agno", "education_research_agent",
     ["policy_search_tool", "report_search_tool", "oecd_lookup_tool"],
     ["policy", "report", "oecd", "european commission", "unesco"]),
    ("agno", "bunchloch_research_agent",
     ["local_model_query_tool", "federated_search_tool"],
     ["m4", "macbook", "local model", "federated", "on-device"]),
    ("agno", "agui_curriculum_agent",
     ["agui_streaming_tool", "copilot_kit_bridge_tool"],
     ["ag-ui", "streaming", "copilot", "react"]),
]


OUT_ROOT = Path(
    "/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/dagster/defs/5_agent_ops"
)


TEMPLATE = """# defs/5_agent_ops/{framework}/{agent_name}/defs.yaml
#
# L5 CelticAgentOpsComponent for the {agent_name} ({framework}) agent.
# The Component emits 5 Dagster assets:
# - agent_health_{agent_name}
# - agent_routing_{agent_name}
# - agent_memory_{agent_name}
# - agent_event_{agent_name}
# - agent_trace_{agent_name}
type: cianfhoghlaim.dagster.components.CelticAgentOpsComponent
attributes:
  agent_name: {agent_name}
  framework: {framework}
  tools: {tools}
  memory_backend: letta
  event_stream: risingwave
  event_stream_endpoint: risingwave.cianfhoghlaim.ie:4566
  langfuse_trace_tag: agent.{agent_name_short}
  langfuse_drop_smoke_spans: true
  routing_keywords: {routing_keywords}
"""


def main() -> int:
    written = 0
    for framework, agent_name, tools, routing_keywords in AGENTS:
        agent_name_short = agent_name.replace("_agent", "")
        target_dir = OUT_ROOT / framework / agent_name
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "defs.yaml"
        target_file.write_text(
            TEMPLATE.format(
                framework=framework,
                agent_name=agent_name,
                agent_name_short=agent_name_short,
                tools=tools,
                routing_keywords=routing_keywords,
            )
        )
        written += 1
    print(f"Wrote {written} agent YAML defs files under {OUT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
