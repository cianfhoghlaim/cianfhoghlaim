// TODO: implement the CopilotKit action descriptors. Each action is a
// typed tool the AI chat can invoke: search protocols, get TVL, get
// funding rates, compare yields, query the knowledge graph, run a
// pipeline, etc.

import type { Action } from "@copilotkit/runtime";

export interface CopilotAction extends Action {
  name: string;
  description: string;
}

export const COPILOT_ACTIONS: CopilotAction[] = [
  {
    name: "search_protocols",
    description: "Search the Crypteolas knowledge graph for a DeFi protocol",
  },
  {
    name: "get_funding_rates",
    description: "Fetch live funding rates from Binance / Bybit / OKX",
  },
  {
    name: "compare_yields",
    description: "Compare yield opportunities across Aave, Pendle, etc.",
  },
  {
    name: "get_stablecoin_metrics",
    description: "Get stablecoin peg + supply metrics",
  },
  {
    name: "query_knowledge_graph",
    description: "Run a Cypher query against the temporal knowledge graph",
  },
  {
    name: "run_pipeline",
    description: "Trigger a Dagster pipeline materialization",
  },
  {
    name: "get_protocol_summary",
    description: "Summarise a protocol's TVL, risk, and recent events",
  },
];
