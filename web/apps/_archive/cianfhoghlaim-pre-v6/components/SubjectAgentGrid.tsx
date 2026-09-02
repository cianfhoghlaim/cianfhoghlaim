/** SubjectAgentGrid - The 60 per-subject agent cards grid.
 *
 * Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
 * (Phase 10 - the central Cianfhoghlaim homepage).
 *
 * Surfaces the 60 per-subject agents (Phase 8) as interactive cards.
 * Each card links to the per-subject route (`/<stage>/<subject>/`) and
 * the per-subject marimo notebook (Phase 9).
 *
 * Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change: the
 * subject grid uses the canonical SubjectGridSurface (the A2UI
 * surface generator wrapper from a2ui/SubjectGridSurface.tsx) for
 * the per-stage rendering.
 */

"use client";

import { type FC, useState } from "react";
import Link from "next/link";
import { SubjectGridSurface } from "./a2ui/SubjectGridSurface";

export interface SubjectAgent {
  /** The stage ID (lc | jc | gcse | a_level) */
  readonly stage: string;
  /** The subject slug */
  readonly subject: string;
  /** The human-readable display name */
  readonly display_name: string;
  /** The NCCA LO code (for LC + JC) or England spec code (for GCSE + A-Level) */
  readonly code: string;
  /** The languages this subject is offered in */
  readonly languages: ReadonlyArray<string>;
  /** The canonical CocoIndex v1 app name */
  readonly cocoindex_app: string;
  /** The canonical web route (e.g. /lc/mathematics) */
  readonly route: string;
  /** The canonical marimo notebook path */
  readonly notebook: string;
}

export interface SubjectAgentGridProps {
  /** The 60 per-subject agent configs (consumed from Phase 8 factory) */
  readonly agents: ReadonlyArray<SubjectAgent>;
  /** The stage filter (default: all 4 stages) */
  readonly stageFilter?: string;
  /** The language filter (default: all languages) */
  readonly languageFilter?: string;
}

const STAGE_LABELS: Record<string, string> = {
  lc: "Leaving Certificate",
  jc: "Junior Cycle",
  gcse: "GCSE",
  a_level: "A-Level",
};

// The canonical subject → icon mapping (per the A2UI surface generator)
const SUBJECT_ICONS: Record<string, string> = {
  mathematics: "∑",
  english: "✎",
  gaeilge: "á",
  science: "⚛",
  geography: "⛰",
  history: "⏳",
  cspE: "★",
  sphe: "♥",
  physics: "⚙",
  chemistry: "⚗",
  biology: "🌱",
  french: "✓",
  business: "📊",
  accounting: "$",
  art: "✦",
  music: "♪",
  computer_science: "▦",
  economics: "📈",
  history_of_art: "🖼",
  politics: "⚐",
  psychology: "ψ",
  sociology: "⚖",
};

function getSubjectIcon(slug: string): string {
  return SUBJECT_ICONS[slug] ?? "■";
}

const STAGE_ORDER: ReadonlyArray<string> = ["lc", "jc", "gcse", "a_level"];

export const SubjectAgentGrid: FC<SubjectAgentGridProps> = ({
  agents,
  stageFilter,
  languageFilter,
}) => {
  const [hoveredAgent, setHoveredAgent] = useState<string | null>(null);

  // Group agents by stage
  const grouped: Record<string, SubjectAgent[]> = {};
  for (const agent of agents) {
    if (stageFilter && agent.stage !== stageFilter) continue;
    if (languageFilter && !agent.languages.includes(languageFilter)) continue;
    if (!grouped[agent.stage]) grouped[agent.stage] = [];
    grouped[agent.stage].push(agent);
  }

  return (
    <div className="space-y-8">
      {/* The A2UI subject_grid surface (per the 2026-09-30-mega-3b change) */}
      <SubjectGridSurface
        data={{
          subjects: Object.values(grouped).flat().map((agent) => ({
            slug: agent.subject,
            display_name: agent.display_name,
            icon: getSubjectIcon(agent.subject),
            ncca_lo_prefix: agent.code,
          })),
        }}
      />
      {STAGE_ORDER.map((stage) => {
        const stageAgents = grouped[stage] ?? [];
        if (stageAgents.length === 0) return null;
        return (
          <div key={stage}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-slate-900">
                {STAGE_LABELS[stage]}
              </h3>
              <span className="text-sm text-slate-500">
                {stageAgents.length} subjects
              </span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {stageAgents.map((agent) => {
                const cardKey = `${agent.stage}-${agent.subject}`;
                return (
                  <Link
                    key={cardKey}
                    href={agent.route}
                    className="group block"
                    onMouseEnter={() => setHoveredAgent(cardKey)}
                    onMouseLeave={() => setHoveredAgent(null)}
                  >
                    <div
                      className={`bg-white rounded-lg border p-4 transition cursor-pointer ${
                        hoveredAgent === cardKey
                          ? "border-slate-400 shadow-md"
                          : "border-slate-200"
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <p className="text-sm font-semibold text-slate-900 group-hover:text-blue-600">
                            {agent.display_name}
                          </p>
                          <p className="text-xs text-slate-500 mt-1">
                            <code className="text-xs">{agent.code}</code>
                          </p>
                        </div>
                        <span className="text-xs px-2 py-0.5 bg-slate-100 text-slate-600 rounded uppercase tracking-wider">
                          {agent.stage}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 mt-2">
                        {agent.languages.map((lang) => (
                          <span
                            key={lang}
                            className="text-xs px-1.5 py-0.5 bg-slate-50 text-slate-500 rounded"
                          >
                            {lang}
                          </span>
                        ))}
                      </div>
                      <p className="text-xs text-slate-400 mt-2 truncate">
                        {agent.cocoindex_app}
                      </p>
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
};
