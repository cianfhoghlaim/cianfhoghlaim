// /index — cianfhoghlaim landing page
// Khan-style 4 entry points + the 6 content types + the 9 ADK agents
// Per openspec/changes/cianfhoghlaim-website-rewrite/specs/.../spec.md R2

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel } from "@cianfhoghlaim/ui";
import { CONTENT_TYPES_LIST, TOTAL_CONTENT_COUNT } from "@/lib/content-types";
import { AGENTS } from "@/lib/registry";

export const Route = createFileRoute("/")({
  component: HomePage,
});

const ENTRY_POINTS = [
  {
    id: "student",
    title: "Student",
    title_ga: "Mac Léinn",
    blurb: "Learning for myself — explore the 8 NCCA subjects + the 5×8 mastery matrix + practice items.",
    href: "/en/subjects/mathematics",
    color: "emerald",
    icon: "🎓",
  },
  {
    id: "teacher",
    title: "Teacher",
    title_ga: "Múinteoir",
    blurb: "Educator with a classroom — class management tools + curriculum-aligned content + AI tutor (cianfhoghlaim operator agent).",
    href: "/en/agents",
    color: "blue",
    icon: "👩‍🏫",
  },
  {
    id: "family",
    title: "Family",
    title_ga: "Teaghlach",
    blurb: "Supporting my child — dashboard to track progress + 6 content types per subject.",
    href: "/en/foundations",
    color: "amber",
    icon: "🏠",
  },
  {
    id: "school",
    title: "School / District",
    title_ga: "Scoil / Ceantar",
    blurb: "AI-powered solutions — school-wide insights + 9 ADK agents + data engineering pipeline.",
    href: "/en/self-host",
    color: "purple",
    icon: "🏛️",
  },
];

function HomePage() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8 p-6">
      {/* Hero */}
      <section className="text-center pt-12 pb-8">
        <h1 className="font-cinzel text-5xl font-bold text-emerald-400 mb-3">
          cianfhoghlaim
        </h1>
        <p className="text-xl text-slate-300 max-w-3xl mx-auto">
          A self-hostable consolidation of Leaving Certificate education system resources.
        </p>
        <p className="text-base text-slate-400 max-w-3xl mx-auto mt-3">
          8 NCCA subjects + 5 root-level PDFs + 6 content types + 9 ADK agents. Built on the open-source agentic stack.
        </p>
        <div className="mt-6 flex items-center justify-center gap-3">
          <Link
            to="/en/self-host"
            className="px-5 py-2.5 rounded-lg bg-emerald-600 text-white hover:bg-emerald-500 transition-colors"
          >
            Self-host in 5 minutes →
          </Link>
          <Link
            to="/en/subjects/mathematics"
            className="px-5 py-2.5 rounded-lg bg-slate-800 text-slate-100 border border-slate-700 hover:border-emerald-700 transition-colors"
          >
            Explore a subject
          </Link>
        </div>
        <p className="text-xs text-slate-500 mt-3 font-mono italic">
          Reduce barriers to education · open source · TanStack Start + CopilotKit v2 AG-UI + A2UI
        </p>
      </section>

      {/* 4 entry points (Khan-style) */}
      <CiTextbookPanel
        title="I am a..."
        material="parchment"
      >
        <p className="text-slate-300 mb-4">
          Choose how you want to use cianfhoghlaim.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {ENTRY_POINTS.map((ep) => (
            <Link
              key={ep.id}
              to={ep.href}
              className="p-4 rounded-lg bg-slate-900 border-2 transition-colors hover:border-emerald-400"
              style={{ borderColor: `var(--ci-subject-${ep.color === "emerald" ? "mathematics" : ep.color === "blue" ? "english" : ep.color === "amber" ? "history" : "computer_science"})` }}
            >
              <div className="text-3xl mb-2">{ep.icon}</div>
              <div className="text-base font-bold text-slate-100">{ep.title}</div>
              <div className="text-xs text-slate-500 italic mb-2">{ep.title_ga}</div>
              <div className="text-sm text-slate-300">{ep.blurb}</div>
            </Link>
          ))}
        </div>
      </CiTextbookPanel>

      {/* 6 content types (Khan-style + iximiuz-style) */}
      <CiTextbookPanel
        title={`${CONTENT_TYPES_LIST.length} content types · ${TOTAL_CONTENT_COUNT}+ resources`}
        material="knotwork"
      >
        <p className="text-slate-300 mb-4">
          Each subject has all 6 content types. Borrowed from Khan Academy's mastery-based learning + iximiuz Labs' 6-content-type model.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {CONTENT_TYPES_LIST.map((ct) => (
            <div
              key={ct.slug}
              className="p-3 rounded-lg bg-slate-900 border border-slate-700 text-center"
            >
              <div className="text-2xl mb-1">{ct.icon}</div>
              <div className="text-sm font-bold text-slate-100">{ct.name}</div>
              <div className="text-xs text-slate-500 mt-1">{ct.count}+ resources</div>
            </div>
          ))}
        </div>
      </CiTextbookPanel>

      {/* 8 NCCA subjects */}
      <CiTextbookPanel
        title="8 NCCA subjects"
        material="knotwork"
      >
        <p className="text-slate-300 mb-4">
          The 8 NCCA Leaving Certificate subjects + their Cianfhoghlaim
          ADK agent + the BAML extraction schema + the CocoIndex
          embeddings. Each subject has its own syllabus + past papers +
          marking schemes + ADK agent + practice page.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {AGENTS.filter((a) => a.id !== "cianfhoghlaim").map((s) => (
            <Link
              key={s.id}
              to={`/en/leaving-cert/${s.id}`}
              className="p-3 rounded-lg bg-slate-900 border-2 transition-colors hover:border-amber-400"
              style={{ borderColor: s.color }}
            >
              <div className="text-sm font-medium" style={{ color: s.color }}>{s.name}</div>
              <div className="text-xs text-slate-500 italic">{s.name_ga}</div>
              <div className="text-xs text-slate-400 mt-1">
                Éraic tier {s.eiraic_tier}/13
              </div>
            </Link>
          ))}
        </div>
      </CiTextbookPanel>

      {/* CTA */}
      <section className="text-center pt-8 pb-12">
        <p className="text-lg text-slate-300 mb-4">
          cianfhoghlaim is licensed under the BUSL-1.1 with a 4-year
          transition to AGPL v3. Anyone can fork + self-host + adapt the
          system for their own country / curriculum / language.
        </p>
        <Link
          to="/en/self-host"
          className="inline-block px-6 py-3 rounded-lg bg-emerald-600 text-white hover:bg-emerald-500 transition-colors"
        >
          Get started in 5 minutes →
        </Link>
      </section>
    </div>
  );
}