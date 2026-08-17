/** RecentActivityFeed - The 24h pipeline activity feed.
 *
 * Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
 * (Phase 10 - the central Cianfhoghlaim homepage).
 *
 * Surfaces the live pipeline activity (Phase 4-9 outputs) for the
 * last 24 hours. Feeds from the per-subject BAML extraction runs
 * + the CocoIndex embed events + the RAGAS validation cycles.
 */

"use client";

import { type FC, useState } from "react";

export type ActivityKind =
  | "syllabus_extraction"
  | "exam_paper_extraction"
  | "marking_scheme_extraction"
  | "embedding"
  | "ragas_validation"
  | "cognee_node_added"
  | "subject_agent_query"
  | "user_annotation";

export interface ActivityEvent {
  /** The unique event ID */
  readonly id: string;
  /** The activity kind */
  readonly kind: ActivityKind;
  /** The subject (e.g. "mathematics" | "biology" | ...) */
  readonly subject: string;
  /** The per-subject agent that triggered the event (Phase 8) */
  readonly agent: string;
  /** The human-readable message */
  readonly message: string;
  /** The ISO 8601 timestamp */
  readonly timestamp: string;
  /** The RAGAS consensus score (if applicable) */
  readonly ragas_score?: number;
}

export interface RecentActivityFeedProps {
  /** The activity events (default: sample data from the BIEP run) */
  readonly events?: ReadonlyArray<ActivityEvent>;
  /** The max number of events to display (default: 20) */
  readonly maxItems?: number;
}

const DEFAULT_EVENTS: ReadonlyArray<ActivityEvent> = [
  {
    id: "1",
    kind: "syllabus_extraction",
    subject: "mathematics",
    agent: "mathematics_lc_agent",
    message: "Extracted 23 syllabus topics for LC Mathematics (Higher)",
    timestamp: "2026-08-13T21:30:00Z",
    ragas_score: 0.95,
  },
  {
    id: "2",
    kind: "embedding",
    subject: "mathematics",
    agent: "mathematics_lc_agent",
    message: "Embedded 1024 chunks (BAAI/bge-m3) for LC Mathematics",
    timestamp: "2026-08-13T21:29:00Z",
  },
  {
    id: "3",
    kind: "ragas_validation",
    subject: "chemistry",
    agent: "chemistry_lc_agent",
    message: "RAGAS consensus validation: 16 LC Chemistry chunks (consensus 0.92)",
    timestamp: "2026-08-13T21:25:00Z",
    ragas_score: 0.92,
  },
  {
    id: "4",
    kind: "subject_agent_query",
    subject: "physics",
    agent: "physics_lc_agent",
    message: "User query: 'What is the NCCA code for LC Physics force topic?'",
    timestamp: "2026-08-13T21:20:00Z",
  },
  {
    id: "5",
    kind: "cognee_node_added",
    subject: "biology",
    agent: "biology_lc_agent",
    message: "Added 12 Cognee knowledge graph nodes for LC Biology (force topic cross-subject)",
    timestamp: "2026-08-13T21:15:00Z",
  },
  {
    id: "6",
    kind: "syllabus_extraction",
    subject: "geography",
    agent: "geography_lc_agent",
    message: "Extracted 18 syllabus topics for LC Geography (Higher + Ordinary)",
    timestamp: "2026-08-13T21:10:00Z",
    ragas_score: 0.91,
  },
  {
    id: "7",
    kind: "user_annotation",
    subject: "english",
    agent: "english_lc_agent",
    message: "User saved annotation on LC English topic LC-ENGL-LO-002",
    timestamp: "2026-08-13T21:05:00Z",
  },
  {
    id: "8",
    kind: "marking_scheme_extraction",
    subject: "biology",
    agent: "biology_lc_agent",
    message: "Extracted 12 marking schemes for LC Biology (2015-2024)",
    timestamp: "2026-08-13T21:00:00Z",
    ragas_score: 0.89,
  },
];

const ACTIVITY_ICONS: Record<ActivityKind, string> = {
  syllabus_extraction: "📚",
  exam_paper_extraction: "📄",
  marking_scheme_extraction: "✍️",
  embedding: "🔢",
  ragas_validation: "✅",
  cognee_node_added: "🕸️",
  subject_agent_query: "💬",
  user_annotation: "📝",
};

const ACTIVITY_COLORS: Record<ActivityKind, string> = {
  syllabus_extraction: "bg-blue-50 text-blue-700",
  exam_paper_extraction: "bg-amber-50 text-amber-700",
  marking_scheme_extraction: "bg-emerald-50 text-emerald-700",
  embedding: "bg-purple-50 text-purple-700",
  ragas_validation: "bg-green-50 text-green-700",
  cognee_node_added: "bg-indigo-50 text-indigo-700",
  subject_agent_query: "bg-pink-50 text-pink-700",
  user_annotation: "bg-orange-50 text-orange-700",
};

export const RecentActivityFeed: FC<RecentActivityFeedProps> = ({
  events = DEFAULT_EVENTS,
  maxItems = 20,
}) => {
  const [filter, setFilter] = useState<ActivityKind | "all">("all");

  const filteredEvents =
    filter === "all" ? events : events.filter((e) => e.kind === filter);

  const displayedEvents = filteredEvents.slice(0, maxItems);

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">
            Recent Activity
          </h2>
          <p className="text-sm text-slate-600">
            Live feed of BIEP pipeline activity (last 24h)
          </p>
        </div>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value as ActivityKind | "all")}
          className="text-sm border border-slate-300 rounded px-3 py-1.5"
        >
          <option value="all">All activities</option>
          <option value="syllabus_extraction">Syllabus extraction</option>
          <option value="embedding">Embedding</option>
          <option value="ragas_validation">RAGAS validation</option>
          <option value="subject_agent_query">Subject agent query</option>
          <option value="user_annotation">User annotation</option>
        </select>
      </div>

      <div className="space-y-2">
        {displayedEvents.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-6">
            No activities in the last 24 hours
          </p>
        ) : (
          displayedEvents.map((event) => (
            <ActivityRow key={event.id} event={event} />
          ))
        )}
      </div>

      {filteredEvents.length > maxItems && (
        <p className="text-xs text-slate-500 text-center mt-4">
          Showing {maxItems} of {filteredEvents.length} events
        </p>
      )}
    </div>
  );
};

const ActivityRow: FC<{ event: ActivityEvent }> = ({ event }) => {
  const date = new Date(event.timestamp);
  return (
    <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-50 transition border border-slate-100">
      <div
        className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center text-lg ${ACTIVITY_COLORS[event.kind]}`}
      >
        {ACTIVITY_ICONS[event.kind]}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-semibold text-slate-900 truncate">
            {event.message}
          </span>
          {event.ragas_score !== undefined && (
            <span className="text-xs px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded">
              RAGAS {(event.ragas_score * 100).toFixed(0)}%
            </span>
          )}
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-500">
          <span className="font-mono">{event.agent}</span>
          <span>·</span>
          <span>{event.subject}</span>
          <span>·</span>
          <span>{date.toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  );
};
