// /en/subjects/gaeilge — Gaeilge per-subject interactive landing page.
//
// Per openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/
// The per-subject interactive web surface for the 6 BIEP v1 LC subjects.
// This is the production landing page for the Gaeilge subject,
// rendered alongside (and superseding for interactive use) the flat
// `routes/en/subjects/gaeilge.tsx` file.
//
// Renders: subject header + 5×8 mastery matrix + the 4 sub-route cards
// (syllabus / exam-papers / marking-schemes / study-plan) + bilingual
// EN+GA mirror link.

import * as React from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { BIEPSubjectPage } from "../../../components/BIEPSubjectPage";
import { getBIEPSubject, isBIEPSubject } from "../../../lib/bi-ep";

export const Route = createFileRoute("/en/subjects/gaeilge/")({
  component: GaeilgePerSubjectLanding,
});

function GaeilgePerSubjectLanding() {
  if (!isBIEPSubject("gaeilge")) {
    return <div>Gaeilge subject metadata not found.</div>;
  }
  const subject = getBIEPSubject("gaeilge");
  if (!subject) {
    return <div>Gaeilge subject metadata not found.</div>;
  }
  return (
    <div className="flex flex-col gap-6">
      <BIEPSubjectPage subject={subject} language="en" />
      <nav
        aria-label="Gaeilge interactive sub-routes"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 px-6"
      >
        <SubRouteCard
          to="/en/subjects/gaeilge/syllabus"
          title="Syllabus"
          blurb="NCCA syllabus topics + learning outcomes"
        />
        <SubRouteCard
          to="/en/subjects/gaeilge/exam-papers"
          title="Past exam papers"
          blurb="All Gaeilge past exam papers tagged by topic + paper + year"
        />
        <SubRouteCard
          to="/en/subjects/gaeilge/marking-schemes"
          title="Marking schemes"
          blurb="PCLM (Partial Credit, Logical Marking) patterns"
        />
        <SubRouteCard
          to="/en/subjects/gaeilge/study-plan"
          title="Study plan"
          blurb="Generate a per-subject study plan via the BAML backend"
        />
      </nav>
      <div className="px-6 text-sm text-slate-500">
        <Link to="/ga/subjects/gaeilge">Gaeilge: Gaeilge →</Link>
      </div>
    </div>
  );
}

interface SubRouteCardProps {
  to: string;
  title: string;
  blurb: string;
}

function SubRouteCard({ to, title, blurb }: SubRouteCardProps) {
  return (
    <Link
      to={to}
      className="rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm hover:shadow-md transition"
    >
      <div className="text-base font-semibold text-slate-900">{title}</div>
      <div className="text-sm text-slate-600">{blurb}</div>
    </Link>
  );
}
