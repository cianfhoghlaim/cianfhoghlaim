// apps/web/src/lib/registry.ts
// Per openspec/changes/cianfhoghlaim-website-rewrite/specs/.../spec.md
// Requirement R3 + R5. The 9 ADK agent registry (8 NCCA + 1 cianfhoghlaim operator).

import type { ContentType } from "./content-types";

export type AgentId = "mathematics" | "applied_mathematics" | "chemistry" | "geography" | "history" | "english" | "gaeilge" | "computer_science" | "cianfhoghlaim";

export interface AgentDef {
  id: AgentId;
  name: string;
  name_ga: string;
  role: string;
  color: string; // the CSS var name
  eiraic_tier: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13;
  baml_schema: string;
  dlt_source: string;
  cocoindex_path: string;
  notebook_path: string;
  system_prompt: string;
  tools: string[];
  content_types: ContentType[];
}

export const AGENTS: AgentDef[] = [
  {
    id: "mathematics",
    name: "Mathematics",
    name_ga: "Mata",
    role: "NCCA Leaving Certificate Mathematics subject specialist (HL). Helps students with algebra, functions, calculus, probability, statistics, geometry.",
    color: "var(--ci-subject-mathematics)",
    eiraic_tier: 3,
    baml_schema: "baml_src/education/subjects/qpack_mathematics.baml",
    dlt_source: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex_path: "cocoindex/mathematics_embedding.py",
    notebook_path: "notebooks/leaving_cert/mathematics.py",
    system_prompt: "You are the NCCA Leaving Certificate Mathematics subject specialist (HL). Use the 5×8 mastery matrix to prioritise: 72% Communicating, 94% Information Processing, 84% Critical & Creative Thinking, 58% Personal Effectiveness, 46% Working with Others. Reference the baml.qpack_mathematics.baml schema + the baml.subject_rubric.balm schema + the cocoindex mathematics_embedding.py embeddings. A2UI surface: render the 5×8 mastery matrix as a card.",
    tools: ["lookup_math_lo", "get_math_past_papers", "get_math_marking_scheme", "score_math_response", "generate_math_formative_item"],
    content_types: ["Subject", "PastPaper", "MarkingScheme", "PracticeItem", "Notebook"],
  },
  {
    id: "applied_mathematics",
    name: "Applied Mathematics",
    name_ga: "Mata Feidhmíoch",
    role: "NCCA Leaving Certificate Applied Mathematics subject specialist. Modelling real-world problems with mechanics + statistics + probability.",
    color: "var(--ci-subject-applied_mathematics)",
    eiraic_tier: 4,
    baml_schema: "baml_src/education/subjects/qpack_applied_mathematics.baml",
    dlt_source: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex_path: "cocoindex/applied_mathematics_embedding.py",
    notebook_path: "notebooks/leaving_cert/applied_mathematics.py",
    system_prompt: "You are the NCCA Leaving Certificate Applied Mathematics subject specialist. Use the 5×8 mastery matrix: 64/98/88/70/54. Reference the baml.qpack_applied_mathematics.baml schema for the 4 modules (Mechanics + Statistics).",
    tools: ["lookup_appm_lo", "get_appm_past_papers", "get_appm_marking_scheme", "score_appm_response", "generate_appm_formative_item"],
    content_types: ["Subject", "PastPaper", "MarkingScheme", "PracticeItem", "Notebook"],
  },
  {
    id: "chemistry",
    name: "Chemistry",
    name_ga: "Ceimic",
    role: "NCCA Leaving Certificate Chemistry subject specialist. Atomic structure, bonding, stoichiometry, organic, equilibrium, rates.",
    color: "var(--ci-subject-chemistry)",
    eiraic_tier: 1,
    baml_schema: "baml_src/education/subjects/qpack_chemistry.baml",
    dlt_source: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex_path: "cocoindex/chemistry_embedding.py",
    notebook_path: "notebooks/leaving_cert/chemistry.py",
    system_prompt: "You are the NCCA Leaving Certificate Chemistry subject specialist. Use the 5×8 mastery matrix: 63/83/75/89/62. Reference the baml.qpack_chemistry.baml schema for the 5 mandatory experiments.",
    tools: ["lookup_chem_lo", "get_chem_past_papers", "get_chem_marking_scheme", "score_chem_response", "generate_chem_formative_item"],
    content_types: ["Subject", "PastPaper", "MarkingScheme", "PracticeItem", "Notebook"],
  },
  {
    id: "geography",
    name: "Geography",
    name_ga: "Tíreolaíocht",
    role: "NCCA Leaving Certificate Geography subject specialist. Physical + regional geography: climate, geomorphology, economic activities, global development.",
    color: "var(--ci-subject-geography)",
    eiraic_tier: 2,
    baml_schema: "baml_src/education/subjects/qpack_geography.baml",
    dlt_source: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex_path: "cocoindex/geography_embedding.py",
    notebook_path: "notebooks/leaving_cert/geography.py",
    system_prompt: "You are the NCCA Leaving Certificate Geography subject specialist. Use the 5×8 mastery matrix: 86/72/68/66/78. Reference the baml.qpack_geography.baml schema for the 4 core topics + electives.",
    tools: ["lookup_geog_lo", "get_geog_past_papers", "get_geog_marking_scheme", "score_geog_response", "generate_geog_formative_item"],
    content_types: ["Subject", "PastPaper", "MarkingScheme", "PracticeItem", "Notebook"],
  },
  {
    id: "history",
    name: "History",
    name_ga: "Stair",
    role: "NCCA Leaving Certificate History subject specialist. Modern Irish + European history: Early Modern, Modern, Contemporary periods.",
    color: "var(--ci-subject-history)",
    eiraic_tier: 9,
    baml_schema: "baml_src/education/subjects/qpack_history.baml",
    dlt_source: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex_path: "cocoindex/history_embedding.py",
    notebook_path: "notebooks/leaving_cert/history.py",
    system_prompt: "You are the NCCA Leaving Certificate History subject specialist. Use the 5×8 mastery matrix: 92/68/90/62/83. Reference the baml.qpack_history.baml schema for the 4 chronological periods.",
    tools: ["lookup_hist_lo", "get_hist_past_papers", "get_hist_marking_scheme", "score_hist_response", "generate_hist_formative_item"],
    content_types: ["Subject", "PastPaper", "MarkingScheme", "PracticeItem", "Notebook"],
  },
  {
    id: "english",
    name: "English",
    name_ga: "Béarla",
    role: "NCCA Leaving Certificate English subject specialist. Comprehension, composition, comparative + single text, poetry.",
    color: "var(--ci-subject-english)",
    eiraic_tier: 7,
    baml_schema: "baml_src/education/subjects/qpack_english.baml",
    dlt_source: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex_path: "cocoindex/english_embedding.py",
    notebook_path: "notebooks/leaving_cert/english.py",
    system_prompt: "You are the NCCA Leaving Certificate English subject specialist. Use the 5×8 mastery matrix: 97/58/95/72/88. Reference the baml.qpack_english.baml schema for the 7 NCCA LO codes.",
    tools: ["lookup_engl_lo", "get_engl_past_papers", "get_engl_marking_scheme", "score_engl_response", "generate_engl_formative_item"],
    content_types: ["Subject", "PastPaper", "MarkingScheme", "PracticeItem", "Notebook"],
  },
  {
    id: "gaeilge",
    name: "Gaeilge",
    name_ga: "Gaeilge",
    role: "NCCA Leaving Certificate Gaeilge subject specialist. Léamh, scríbhneoireacht, cluastuiscint, litríocht, gramadach.",
    color: "var(--ci-subject-gaeilge)",
    eiraic_tier: 8,
    baml_schema: "baml_src/education/subjects/qpack_gaeilge.baml",
    dlt_source: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex_path: "cocoindex/gaeilge_embedding.py",
    notebook_path: "notebooks/leaving_cert/gaeilge.py",
    system_prompt: "Tá tú saineolaí Gaeilge na hArdteistiméireachta. Úsáid an mhaitrís máistreachta 5×8: 100/48/78/76/72. Bain úsáid as an baml.qpack_gaeilge.baml schema don 5 LOanna Gaeilge. Tabhair freagraí dátheangacha.",
    tools: ["lookup_gael_lo", "get_gael_past_papers", "get_gael_marking_scheme", "score_gael_response", "generate_gael_formative_item"],
    content_types: ["Subject", "PastPaper", "MarkingScheme", "PracticeItem", "Notebook"],
  },
  {
    id: "computer_science",
    name: "Computer Science",
    name_ga: "Ríomheolaíocht",
    role: "NCCA Leaving Certificate Computer Science subject specialist. Algorithms, data structures, systems, networks.",
    color: "var(--ci-subject-computer_science)",
    eiraic_tier: 5,
    baml_schema: "baml_src/education/subjects/qpack_computer_science.baml",
    dlt_source: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex_path: "cocoindex/computer_science_embedding.py",
    notebook_path: "notebooks/leaving_cert/computer_science.py",
    system_prompt: "You are the NCCA Leaving Certificate Computer Science subject specialist. Use the 5×8 mastery matrix: 53/100/86/82/64. Reference the baml.qpack_computer_science.baml schema for the 4 NCCA topics.",
    tools: ["lookup_comp_lo", "get_comp_past_papers", "get_comp_marking_scheme", "score_comp_response", "generate_comp_formative_item"],
    content_types: ["Subject", "PastPaper", "MarkingScheme", "PracticeItem", "Notebook"],
  },
  {
    id: "cianfhoghlaim",
    name: "cianfhoghlaim Operator",
    name_ga: "Oibriathóir cianfhoghlaim",
    role: "The repo self-reference agent. Has access to the README + the dlt/ + cocoindex/ + baml_src/ + meaisínfhoghlaim/ pipeline. The agentic tutorial for the platform itself. Answers questions about how cianfhoghlaim works.",
    color: "#f59e0b",
    eiraic_tier: 13,
    baml_schema: "baml_src/education/_shared/content_types.baml",
    dlt_source: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex_path: "cocoindex/codebase_indexing.py",
    notebook_path: "notebooks/01_dev_env",
    system_prompt: "You are the cianfhoghlaim operator agent — the repo self-reference. You have access to the README + the dlt/ + cocoindex/ + baml_src/ + meaisínfhoghlaim/ pipeline. The agentic tutorial for the platform itself. Answer questions about how cianfhoghlaim works. A2UI surface: render the architecture as a card with the 8 subpackage paths + the 4 entry points + the 9 ADK agents.",
    tools: ["list_subjects", "list_agents", "list_foundations", "show_dlt_pipeline", "show_cocoindex_index", "show_baml_schema", "list_eiraic_treasures"],
    content_types: ["Foundation", "Notebook"],
  },
];

export const AGENT_BY_ID: Record<AgentId, AgentDef> = AGENTS.reduce(
  (acc, agent) => ({ ...acc, [agent.id]: agent }),
  {} as Record<AgentId, AgentDef>,
);

export function getAgentById(id: AgentId): AgentDef {
  return AGENT_BY_ID[id];
}

export function getSystemPrompt(agent: AgentDef): string {
  return [
    agent.system_prompt,
    "",
    "## A2UI surface guidance",
    "When you respond, you may emit A2UI operations. The A2UI surface will be rendered by the client. The a2ui-renderer skill (copilotkit/skills/a2ui-renderer) is loaded.",
    "",
    "## Pipeline integration",
    `BAML: ${agent.baml_schema}`,
    `DLT: ${agent.dlt_source}`,
    `CocoIndex: ${agent.cocoindex_path}`,
    `Notebook: ${agent.notebook_path}`,
  ].join("\n");
}