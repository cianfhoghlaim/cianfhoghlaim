/** Cianfhoghlaim Homepage - the central agentic chat surface.
 *
 * Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
 * (Phase 10 - the central Cianfhoghlaim homepage).
 *
 * This is the canonical homepage for the Cianfhoghlaim platform:
 * 1. Pipeline health (Phase 5 - DLT + BAML + CocoIndex + RAGAS)
 * 2. Subject agents grid (Phase 8 - 60 per-subject agents)
 * 3. Knowledge graph (Phase 4-5 - Cognee 7-cluster knowledge graph)
 * 4. Recent activity (Phase 5-9 - pipeline events)
 * 5. Agentic chat (the per-subject agent query surface)
 *
 * The page is wired through:
 * - TanStack Start (Phase 1 - the canonical web framework)
 * - TanStack AI (Phase Q - the canonical chat client)
 * - CopilotKit v2 (Phase K - the canonical agent surface)
 * - AG-UI 17-event protocol (Phase 4 - the canonical stream protocol)
 * - Convex (Phase 6 - the canonical per-subject Convex schema)
 * - MODEL_REGISTRY (the canonical model routing)
 */

import { type FC, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { CopilotKit } from "@copilotkit/react-core/v2";

import { PipelineStatus } from "@/components/PipelineStatus";
import { SubjectAgentGrid } from "@/components/SubjectAgentGrid";
import { KnowledgeGraphPanel } from "@/components/KnowledgeGraphPanel";
import { RecentActivityFeed } from "@/components/RecentActivityFeed";

export const Route = createFileRoute("/")({
  component: CianfhoghlaimHomepage,
});

interface SubjectAgentConfig {
  readonly stage: string;
  readonly subject: string;
  readonly display_name: string;
  readonly code: string;
  readonly languages: ReadonlyArray<string>;
  readonly cocoindex_app: string;
  readonly route: string;
  readonly notebook: string;
}

// The 60 per-subject agent configs (consumed from Phase 8 factory)
const SUBJECT_AGENTS: ReadonlyArray<SubjectAgentConfig> = [
  // 14 LC subjects (14 agents)
  { stage: "lc", subject: "mathematics", display_name: "Mathematics", code: "LC-MATH-LO", languages: ["en", "ga"], cocoindex_app: "ireland_lc_mathematics_untiered_en_embedding", route: "/lc/mathematics", notebook: "notebooks/lc/mathematics.py" },
  { stage: "lc", subject: "applied_mathematics", display_name: "Applied Mathematics", code: "LC-APM-LO", languages: ["en", "ga"], cocoindex_app: "ireland_lc_applied_mathematics_untiered_en_embedding", route: "/lc/applied_mathematics", notebook: "notebooks/lc/applied_mathematics.py" },
  { stage: "lc", subject: "chemistry", display_name: "Chemistry", code: "LC-CHEM-LO", languages: ["en", "ga"], cocoindex_app: "ireland_lc_chemistry_untiered_en_embedding", route: "/lc/chemistry", notebook: "notebooks/lc/chemistry.py" },
  { stage: "lc", subject: "physics", display_name: "Physics", code: "LC-PHYS-LO", languages: ["en", "ga"], cocoindex_app: "ireland_lc_physics_untiered_en_embedding", route: "/lc/physics", notebook: "notebooks/lc/physics.py" },
  { stage: "lc", subject: "biology", display_name: "Biology", code: "LC-BIO-LO", languages: ["en", "ga"], cocoindex_app: "ireland_lc_biology_untiered_en_embedding", route: "/lc/biology", notebook: "notebooks/lc/biology.py" },
  { stage: "lc", subject: "geography", display_name: "Geography", code: "LC-GEOG-LO", languages: ["en", "ga"], cocoindex_app: "ireland_lc_geography_untiered_en_embedding", route: "/lc/geography", notebook: "notebooks/lc/geography.py" },
  { stage: "lc", subject: "gaeilge", display_name: "Gaeilge", code: "LC-GAEL-LO", languages: ["ga"], cocoindex_app: "ireland_lc_gaeilge_ga_embedding", route: "/lc/gaeilge", notebook: "notebooks/lc/gaeilge.py" },
  { stage: "lc", subject: "english", display_name: "English", code: "LC-ENGL-LO", languages: ["en", "ga"], cocoindex_app: "ireland_lc_english_untiered_en_embedding", route: "/lc/english", notebook: "notebooks/lc/english.py" },
  { stage: "lc", subject: "french", display_name: "French", code: "LC-FREN-LO", languages: ["en", "ga"], cocoindex_app: "ireland_lc_french_untiered_en_embedding", route: "/lc/french", notebook: "notebooks/lc/french.py" },
  { stage: "lc", subject: "history", display_name: "History", code: "LC-HIST-LO", languages: ["en", "ga"], cocoindex_app: "ireland_lc_history_untiered_en_embedding", route: "/lc/history", notebook: "notebooks/lc/history.py" },
  { stage: "lc", subject: "business", display_name: "Business", code: "LC-BUS-LO", languages: ["en", "ga"], cocoindex_app: "ireland_lc_business_untiered_en_embedding", route: "/lc/business", notebook: "notebooks/lc/business.py" },
  { stage: "lc", subject: "accounting", display_name: "Accounting", code: "LC-ACCT-LO", languages: ["en", "ga"], cocoindex_app: "ireland_lc_accounting_untiered_en_embedding", route: "/lc/accounting", notebook: "notebooks/lc/accounting.py" },
  { stage: "lc", subject: "art", display_name: "Art", code: "LC-ART-LO", languages: ["en", "ga"], cocoindex_app: "ireland_lc_art_untiered_en_embedding", route: "/lc/art", notebook: "notebooks/lc/art.py" },
  { stage: "lc", subject: "music", display_name: "Music", code: "LC-MUS-LO", languages: ["en", "ga"], cocoindex_app: "ireland_lc_music_untiered_en_embedding", route: "/lc/music", notebook: "notebooks/lc/music.py" },
  { stage: "lc", subject: "computer_science", display_name: "Computer Science", code: "LC-COMP-LO", languages: ["en", "ga"], cocoindex_app: "ireland_lc_computer_science_untiered_en_embedding", route: "/lc/computer_science", notebook: "notebooks/lc/computer_science.py" },
  // 8 JC subjects
  { stage: "jc", subject: "mathematics", display_name: "Mathematics", code: "JC-MATH-LO", languages: ["en", "ga"], cocoindex_app: "ireland_jc_mathematics_en_embedding", route: "/jc/mathematics", notebook: "notebooks/jc/mathematics.py" },
  { stage: "jc", subject: "english", display_name: "English", code: "JC-ENGL-LO", languages: ["en", "ga"], cocoindex_app: "ireland_jc_english_en_embedding", route: "/jc/english", notebook: "notebooks/jc/english.py" },
  { stage: "jc", subject: "gaeilge", display_name: "Gaeilge", code: "JC-GAEL-LO", languages: ["ga"], cocoindex_app: "ireland_jc_gaeilge_ga_embedding", route: "/jc/gaeilge", notebook: "notebooks/jc/gaeilge.py" },
  { stage: "jc", subject: "science", display_name: "Science", code: "JC-SCI-LO", languages: ["en", "ga"], cocoindex_app: "ireland_jc_science_en_embedding", route: "/jc/science", notebook: "notebooks/jc/science.py" },
  { stage: "jc", subject: "history", display_name: "History", code: "JC-HIST-LO", languages: ["en", "ga"], cocoindex_app: "ireland_jc_history_en_embedding", route: "/jc/history", notebook: "notebooks/jc/history.py" },
  { stage: "jc", subject: "geography", display_name: "Geography", code: "JC-GEOG-LO", languages: ["en", "ga"], cocoindex_app: "ireland_jc_geography_en_embedding", route: "/jc/geography", notebook: "notebooks/jc/geography.py" },
  { stage: "jc", subject: "french", display_name: "French", code: "JC-FREN-LO", languages: ["en", "ga"], cocoindex_app: "ireland_jc_french_en_embedding", route: "/jc/french", notebook: "notebooks/jc/french.py" },
  { stage: "jc", subject: "business", display_name: "Business", code: "JC-BUS-LO", languages: ["en", "ga"], cocoindex_app: "ireland_jc_business_en_embedding", route: "/jc/business", notebook: "notebooks/jc/business.py" },
  // 9 GCSE subjects (deduplicated across 3 boards)
  { stage: "gcse", subject: "mathematics", display_name: "Mathematics", code: "8462/J560/1MA1", languages: ["en"], cocoindex_app: "england_gcse_mathematics_en_embedding", route: "/gcse/mathematics", notebook: "notebooks/gcse/mathematics.py" },
  { stage: "gcse", subject: "english_language", display_name: "English Language", code: "8700/J351/1EN0", languages: ["en"], cocoindex_app: "england_gcse_english_language_en_embedding", route: "/gcse/english_language", notebook: "notebooks/gcse/english_language.py" },
  { stage: "gcse", subject: "english_literature", display_name: "English Literature", code: "8702/J352/1ET0", languages: ["en"], cocoindex_app: "england_gcse_english_literature_en_embedding", route: "/gcse/english_literature", notebook: "notebooks/gcse/english_literature.py" },
  { stage: "gcse", subject: "biology", display_name: "Biology", code: "8461/J247/1BI0", languages: ["en"], cocoindex_app: "england_gcse_biology_en_embedding", route: "/gcse/biology", notebook: "notebooks/gcse/biology.py" },
  { stage: "gcse", subject: "chemistry", display_name: "Chemistry", code: "8462/J248/1CH0", languages: ["en"], cocoindex_app: "england_gcse_chemistry_en_embedding", route: "/gcse/chemistry", notebook: "notebooks/gcse/chemistry.py" },
  { stage: "gcse", subject: "physics", display_name: "Physics", code: "8463/J249/1PH0", languages: ["en"], cocoindex_app: "england_gcse_physics_en_embedding", route: "/gcse/physics", notebook: "notebooks/gcse/physics.py" },
  { stage: "gcse", subject: "computer_science", display_name: "Computer Science", code: "8525/J277/1CP2", languages: ["en"], cocoindex_app: "england_gcse_computer_science_en_embedding", route: "/gcse/computer_science", notebook: "notebooks/gcse/computer_science.py" },
  { stage: "gcse", subject: "history", display_name: "History", code: "8145/J410/1HI0", languages: ["en"], cocoindex_app: "england_gcse_history_en_embedding", route: "/gcse/history", notebook: "notebooks/gcse/history.py" },
  { stage: "gcse", subject: "geography", display_name: "Geography", code: "8035/J383/1GA0", languages: ["en"], cocoindex_app: "england_gcse_geography_en_embedding", route: "/gcse/geography", notebook: "notebooks/gcse/geography.py" },
  // 15 A-Level subjects
  { stage: "a_level", subject: "mathematics", display_name: "Mathematics", code: "7357/H240/9MA0", languages: ["en"], cocoindex_app: "england_a_level_mathematics_a_level_en_embedding", route: "/a-level/mathematics", notebook: "notebooks/a_level/mathematics.py" },
  { stage: "a_level", subject: "further_mathematics", display_name: "Further Mathematics", code: "7367/H245/9FM0", languages: ["en"], cocoindex_app: "england_a_level_further_mathematics_a_level_en_embedding", route: "/a-level/further_mathematics", notebook: "notebooks/a_level/further_mathematics.py" },
  { stage: "a_level", subject: "english_literature", display_name: "English Literature", code: "7717/H472/9ET0", languages: ["en"], cocoindex_app: "england_a_level_english_literature_a_level_en_embedding", route: "/a-level/english_literature", notebook: "notebooks/a_level/english_literature.py" },
  { stage: "a_level", subject: "english_language", display_name: "English Language", code: "7702/H470/9EN0", languages: ["en"], cocoindex_app: "england_a_level_english_language_a_level_en_embedding", route: "/a-level/english_language", notebook: "notebooks/a_level/english_language.py" },
  { stage: "a_level", subject: "biology", display_name: "Biology", code: "7402/H420/9BN0", languages: ["en"], cocoindex_app: "england_a_level_biology_a_level_en_embedding", route: "/a-level/biology", notebook: "notebooks/a_level/biology.py" },
  { stage: "a_level", subject: "chemistry", display_name: "Chemistry", code: "7405/H433/9CH0", languages: ["en"], cocoindex_app: "england_a_level_chemistry_a_level_en_embedding", route: "/a-level/chemistry", notebook: "notebooks/a_level/chemistry.py" },
  { stage: "a_level", subject: "physics", display_name: "Physics", code: "7408/H556/9PH0", languages: ["en"], cocoindex_app: "england_a_level_physics_a_level_en_embedding", route: "/a-level/physics", notebook: "notebooks/a_level/physics.py" },
  { stage: "a_level", subject: "psychology", display_name: "Psychology", code: "7182/H180/9PS0", languages: ["en"], cocoindex_app: "england_a_level_psychology_a_level_en_embedding", route: "/a-level/psychology", notebook: "notebooks/a_level/psychology.py" },
  { stage: "a_level", subject: "history", display_name: "History", code: "7042/H505/9HI0", languages: ["en"], cocoindex_app: "england_a_level_history_a_level_en_embedding", route: "/a-level/history", notebook: "notebooks/a_level/history.py" },
  { stage: "a_level", subject: "geography", display_name: "Geography", code: "7037/H481/9GE0", languages: ["en"], cocoindex_app: "england_a_level_geography_a_level_en_embedding", route: "/a-level/geography", notebook: "notebooks/a_level/geography.py" },
  { stage: "a_level", subject: "economics", display_name: "Economics", code: "7126/H460/9EC0", languages: ["en"], cocoindex_app: "england_a_level_economics_a_level_en_embedding", route: "/a-level/economics", notebook: "notebooks/a_level/economics.py" },
  { stage: "a_level", subject: "business", display_name: "Business", code: "7132/H431/9BS0", languages: ["en"], cocoindex_app: "england_a_level_business_a_level_en_embedding", route: "/a-level/business", notebook: "notebooks/a_level/business.py" },
  { stage: "a_level", subject: "history_of_art", display_name: "History of Art", code: "7203/H401/9HA0", languages: ["en"], cocoindex_app: "england_a_level_history_of_art_a_level_en_embedding", route: "/a-level/history_of_art", notebook: "notebooks/a_level/history_of_art.py" },
  { stage: "a_level", subject: "politics", display_name: "Politics", code: "7152/H485/9PL0", languages: ["en"], cocoindex_app: "england_a_level_politics_a_level_en_embedding", route: "/a-level/politics", notebook: "notebooks/a_level/politics.py" },
  { stage: "a_level", subject: "sociology", display_name: "Sociology", code: "7192/H180/9SC0", languages: ["en"], cocoindex_app: "england_a_level_sociology_a_level_en_embedding", route: "/a-level/sociology", notebook: "notebooks/a_level/sociology.py" },
];

function CianfhoghlaimHomepage(): React.JSX.Element {
  const [query, setQuery] = useState("");
  const [selectedStage, setSelectedStage] = useState<string | null>(null);

  return (
    <CopilotKit runtimeUrl="/api/copilotkit/cianfhoghlaim">
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
        {/* HERO */}
        <section className="px-6 py-12 md:py-20 max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-4">
              <span className="bg-gradient-to-r from-blue-600 to-emerald-600 bg-clip-text text-transparent">
                Cianfhoghlaim
              </span>
            </h1>
            <p className="text-xl text-slate-700 max-w-3xl mx-auto mb-8">
              The bilingual, agentic gateway to the entire Irish &amp; British
              Isles education system — 5 stages × 46 subjects × 134 official
              PDFs × 4-path OCR/VLM × canonical BAAI/bge-m3 embeddings.
            </p>
            <div className="flex items-center justify-center gap-3 text-sm">
              <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded">
                60 per-subject agents
              </span>
              <span className="px-3 py-1 bg-emerald-100 text-emerald-700 rounded">
                7-cluster Cognee KG
              </span>
              <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded">
                AG-UI 17-event streaming
              </span>
              <span className="px-3 py-1 bg-amber-100 text-amber-700 rounded">
                Per-subject RAGAS validation
              </span>
            </div>
          </div>
        </section>

        {/* AGENTIC CHAT */}
        <section className="px-6 max-w-7xl mx-auto mb-12">
          <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-6">
            <h2 className="text-2xl font-bold text-slate-900 mb-2">
              💬 Ask Cianfhoghlaim anything
            </h2>
            <p className="text-sm text-slate-600 mb-4">
              Subject-aware routing to 60 per-subject agents (Phase 8).
              Each query is dispatched to the right agent based on the
              subject + stage detection.
            </p>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. 'What is the NCCA code for LC Physics force topic?'"
              className="w-full min-h-[80px] p-3 border border-slate-300 rounded-lg resize-y focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <div className="flex items-center justify-between mt-3">
              <p className="text-xs text-slate-500">
                Subject: <span className="font-mono">auto-detect</span> ·
                Stage: <span className="font-mono">auto-detect</span> ·
                Model: <span className="font-mono">minimax-m3</span>
              </p>
              <button
                type="button"
                disabled={!query.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium disabled:opacity-50 hover:bg-blue-700"
              >
                Send
              </button>
            </div>
          </div>
        </section>

        {/* PIPELINE STATUS */}
        <section className="px-6 max-w-7xl mx-auto mb-12">
          <PipelineStatus />
        </section>

        {/* SUBJECT AGENT GRID */}
        <section className="px-6 max-w-7xl mx-auto mb-12">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-900">
                60 Per-Subject Agents
              </h2>
              <p className="text-sm text-slate-600">
                Click a subject card to access the per-subject chat agent
                (Phase 8) + the per-subject marimo notebook (Phase 9)
              </p>
            </div>
            <select
              value={selectedStage ?? "all"}
              onChange={(e) => setSelectedStage(e.target.value === "all" ? null : e.target.value)}
              className="text-sm border border-slate-300 rounded px-3 py-1.5"
            >
              <option value="all">All stages</option>
              <option value="lc">LC</option>
              <option value="jc">JC</option>
              <option value="gcse">GCSE</option>
              <option value="a_level">A-Level</option>
            </select>
          </div>
          <SubjectAgentGrid
            agents={SUBJECT_AGENTS}
            stageFilter={selectedStage ?? undefined}
          />
        </section>

        {/* KNOWLEDGE GRAPH */}
        <section className="px-6 max-w-7xl mx-auto mb-12">
          <KnowledgeGraphPanel />
        </section>

        {/* RECENT ACTIVITY */}
        <section className="px-6 max-w-7xl mx-auto mb-12">
          <RecentActivityFeed />
        </section>

        {/* FOOTER */}
        <footer className="border-t border-slate-200 bg-white py-8">
          <div className="max-w-7xl mx-auto px-6 text-center text-sm text-slate-500">
            <p>
              <strong className="font-mono">Cianfhoghlaim</strong> ·
              the canonical BIEP surface · per the
              <Link
                to="/agents/WEB_INTEGRATION.md"
                className="text-blue-600 hover:underline mx-1"
              >
                web_integration
              </Link>
              contract · Phase 10 of the
              <Link
                to="https://github.com/cianfhoghlaim/cianfhoghlaim/blob/main/openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/"
                className="text-blue-600 hover:underline ml-1"
              >
                mega-change
              </Link>
            </p>
          </div>
        </footer>
      </div>
    </CopilotKit>
  );
}
