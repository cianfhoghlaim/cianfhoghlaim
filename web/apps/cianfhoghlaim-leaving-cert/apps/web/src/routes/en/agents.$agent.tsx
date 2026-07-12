// /en/agents/$agent — Per-agent detail page (8 NCCA + 1 operator)
// Per the user's instruction: cianfhoghlaim website is the agentic tutorial for the repo

import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { CiTextbookPanel, CiDetailCell, CiTextbookPanel as _CP } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/agents/$agent")({
  component: AgentDetail,
});

const AGENT_DATA: Record<string, {
  name: string;
  color: string;
  role: string;
  systemPromptSnippet: string;
  tools: string[];
  cocoindexPath: string;
  dltSource: string;
  bamlSchema: string;
}> = {
  mathematics: {
    name: "Mathematics Agent", color: "var(--ci-subject-mathematics)",
    role: "NCCA Leaving Certificate Mathematics subject specialist (HL). Helps students with algebra, functions, calculus, probability, statistics, geometry.",
    systemPromptSnippet: "You are the NCCA Leaving Certificate Mathematics subject specialist (HL). Use the 5×8 mastery matrix to prioritise: 72% Communicating, 94% Information Processing, 84% Critical & Creative Thinking, 58% Personal Effectiveness, 46% Working with Others. Reference the BAML ExtractLeavingCertSyllabus + ExtractMarkingScheme + ScoreMathFormativeResponse schemas.",
    tools: ["lookup_math_lo", "get_math_past_papers", "get_math_marking_scheme", "score_math_response", "generate_math_formative_item"],
    cocoindexPath: "cocoindex/mathematics_embedding.py",
    dltSource: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    bamlSchema: "baml_src/education/subjects/qpack_mathematics.baml",
  },
  applied_mathematics: {
    name: "Applied Mathematics Agent", color: "var(--ci-subject-applied_mathematics)",
    role: "NCCA Leaving Certificate Applied Mathematics subject specialist. Modelling real-world problems with mechanics + statistics + probability.",
    systemPromptSnippet: "You are the NCCA Leaving Certificate Applied Mathematics subject specialist. Use the 5×8 mastery matrix: 64/98/88/70/54. Reference the BAML AppM schema for the 4 modules (Mechanics + Statistics).",
    tools: ["lookup_appm_lo", "get_appm_past_papers", "get_appm_marking_scheme", "score_appm_response", "generate_appm_formative_item"],
    cocoindexPath: "cocoindex/applied_mathematics_embedding.py",
    dltSource: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    bamlSchema: "baml_src/education/subjects/qpack_applied_mathematics.baml",
  },
  chemistry: {
    name: "Chemistry Agent", color: "var(--ci-subject-chemistry)",
    role: "NCCA Leaving Certificate Chemistry subject specialist. Atomic structure, bonding, stoichiometry, organic, equilibrium, rates.",
    systemPromptSnippet: "You are the NCCA Leaving Certificate Chemistry subject specialist. Use the 5×8 mastery matrix: 63/83/75/89/62. Reference the BAML Chem schema for the 5 mandatory experiments.",
    tools: ["lookup_chem_lo", "get_chem_past_papers", "get_chem_marking_scheme", "score_chem_response", "generate_chem_formative_item"],
    cocoindexPath: "cocoindex/chemistry_embedding.py",
    dltSource: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    bamlSchema: "baml_src/education/subjects/qpack_chemistry.baml",
  },
  geography: {
    name: "Geography Agent", color: "var(--ci-subject-geography)",
    role: "NCCA Leaving Certificate Geography subject specialist. Physical + regional geography.",
    systemPromptSnippet: "You are the NCCA Leaving Certificate Geography subject specialist. Use the 5×8 mastery matrix: 86/72/68/66/78. Reference the BAML Geog schema for the 4 core topics + electives.",
    tools: ["lookup_geog_lo", "get_geog_past_papers", "get_geog_marking_scheme", "score_geog_response", "generate_geog_formative_item"],
    cocoindexPath: "cocoindex/geography_embedding.py",
    dltSource: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    bamlSchema: "baml_src/education/subjects/qpack_geography.baml",
  },
  history: {
    name: "History Agent", color: "var(--ci-subject-history)",
    role: "NCCA Leaving Certificate History subject specialist. Modern Irish + European history.",
    systemPromptSnippet: "You are the NCCA Leaving Certificate History subject specialist. Use the 5×8 mastery matrix: 92/68/90/62/83. Reference the BAML History schema for the 4 chronological periods.",
    tools: ["lookup_hist_lo", "get_hist_past_papers", "get_hist_marking_scheme", "score_hist_response", "generate_hist_formative_item"],
    cocoindexPath: "cocoindex/history_embedding.py",
    dltSource: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    bamlSchema: "baml_src/education/subjects/qpack_history.baml",
  },
  english: {
    name: "English Agent", color: "var(--ci-subject-english)",
    role: "NCCA Leaving Certificate English subject specialist. Comprehension, composition, comparative + single text, poetry.",
    systemPromptSnippet: "You are the NCCA Leaving Certificate English subject specialist. Use the 5×8 mastery matrix: 97/58/95/72/88. Reference the BAML Engl schema for the 7 NCCA LO codes.",
    tools: ["lookup_engl_lo", "get_engl_past_papers", "get_engl_marking_scheme", "score_engl_response", "generate_engl_formative_item"],
    cocoindexPath: "cocoindex/english_embedding.py",
    dltSource: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    bamlSchema: "baml_src/education/subjects/qpack_english.baml",
  },
  gaeilge: {
    name: "Gaeilge Agent", color: "var(--ci-subject-gaeilge)",
    role: "NCCA Leaving Certificate Gaeilge subject specialist. Léamh, scríbhneoireacht, cluastuiscint, litríocht, gramadach.",
    systemPromptSnippet: "Tá tú saineolaí Gaeilge na hArdteistiméireachta. Úsáid an mhaitrís máistreachta 5×8: 100/48/78/76/72. Bain úsáid as an BAML Gael schema don 5 LOanna.",
    tools: ["lookup_gael_lo", "get_gael_past_papers", "get_gael_marking_scheme", "score_gael_response", "generate_gael_formative_item"],
    cocoindexPath: "cocoindex/gaeilge_embedding.py",
    dltSource: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    bamlSchema: "baml_src/education/subjects/qpack_gaeilge.baml",
  },
  computer_science: {
    name: "Computer Science Agent", color: "var(--ci-subject-computer_science)",
    role: "NCCA Leaving Certificate Computer Science subject specialist. Algorithms, data structures, systems, networks.",
    systemPromptSnippet: "You are the NCCA Leaving Certificate Computer Science subject specialist. Use the 5×8 mastery matrix: 53/100/86/82/64. Reference the BAML CS schema for the 4 NCCA topics.",
    tools: ["lookup_comp_lo", "get_comp_past_papers", "get_comp_marking_scheme", "score_comp_response", "generate_comp_formative_item"],
    cocoindexPath: "cocoindex/computer_science_embedding.py",
    dltSource: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    bamlSchema: "baml_src/education/subjects/qpack_computer_science.baml",
  },
  cianfhoghlaim: {
    name: "cianfhoghlaim Operator Agent", color: "#f59e0b",
    role: "The repo self-reference agent. Has access to the README + dlt/ + cocoindex/ + baml_src/ + meaisinfhoghlaim/. Answers questions about how the repo works. The 9th ADK agent.",
    systemPromptSnippet: "You are the cianfhoghlaim operator agent. You have access to the README + the 6 subpackage READMEs + the openspec/ tree. You explain the architecture: dlt/ extraction → cocoindex/ embeddings → baml_src/ schemas → meaisinfhoghlaim/ OCR/VLM → dagster/ orchestration → apps/web/ TanStack Start + apps/api/ Hono. The 8 NCCA subject ADK agents are in agents/tuatha/agents/ + are exposed via the CopilotKit runtime at /api/copilotkit.",
    tools: ["list_subjects", "read_file", "list_agents", "show_dlt_pipeline", "show_cocoindex_index", "show_baml_schema", "list_eiraic_treasures"],
    cocoindexPath: "N/A (operator agent — has tools, not embeddings)",
    dltSource: "N/A (operator agent — does its own tool calls)",
    bamlSchema: "N/A (operator agent — uses BAML schemas as data, not as the agent's contract)",
  },
};

function AgentDetail() {
  const { agent } = Route.useParams();
  const a = AGENT_DATA[agent];

  if (!a) {
    throw notFound({ data: { agent } });
  }

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6 p-6">
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Link to="/en/agents" className="hover:text-emerald-400">All agents</Link>
          <span>›</span>
          <span className="text-slate-300">{a.name}</span>
        </div>
        <h1 className="font-cinzel text-4xl font-bold" style={{ color: a.color }}>
          {a.name}
        </h1>
        <p className="text-slate-400 font-mono text-sm">{agent}_agent</p>
      </div>

      <CiTextbookPanel title="Role" material="knotwork">
        <p className="text-slate-300">{a.role}</p>
      </CiTextbookPanel>

      <CiTextbookPanel title="System Prompt Snippet" material="parchment">
        <pre className="text-xs text-slate-300 font-mono whitespace-pre-wrap bg-slate-950 p-3 rounded">
{a.systemPromptSnippet}
        </pre>
      </CiTextbookPanel>

      <CiTextbookPanel title="5 Tools" material="ink-wash">
        <ul className="space-y-1">
          {a.tools.map((t) => (
            <li key={t} className="text-slate-300 font-mono text-sm">• {t}</li>
          ))}
        </ul>
      </CiTextbookPanel>

      <CiTextbookPanel title="Pipeline Integration" material="gold-leaf">
        <div className="space-y-2 text-sm">
          <div>
            <span className="text-slate-500 font-mono">CocoIndex: </span>
            <code className="text-amber-400">{a.cocoindexPath}</code>
          </div>
          <div>
            <span className="text-slate-500 font-mono">DLT: </span>
            <code className="text-amber-400">{a.dltSource}</code>
          </div>
          <div>
            <span className="text-slate-500 font-mono">BAML: </span>
            <code className="text-amber-400">{a.bamlSchema}</code>
          </div>
        </div>
      </CiTextbookPanel>
    </div>
  );
}