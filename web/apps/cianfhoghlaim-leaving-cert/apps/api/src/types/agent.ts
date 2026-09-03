// apps/api/src/types/agent.ts (shared type for ADK agent definitions)

export type ContentType = "Subject" | "PastPaper" | "MarkingScheme" | "PracticeItem" | "Foundation" | "Notebook";

export type AgentId = "mathematics" | "applied_mathematics" | "chemistry" | "geography" | "history" | "english" | "gaeilge" | "computer_science" | "cianfhoghlaim";

export interface AgentDef {
  id: AgentId;
  name: string;
  name_ga: string;
  role: string;
  color: string;
  eiraic_tier: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13;
  baml_schema: string;
  dlt_source: string;
  cocoindex_path: string;
  notebook_path: string;
  system_prompt: string;
  tools: string[];
  content_types: ContentType[];
}