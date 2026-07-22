// /en/subjects/mathematics — Mathematics per-subject interactive landing page.
//
// Per openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/
// The per-subject interactive web surface for the 6 BIEP v1 LC subjects.
// This is the production landing page for the Mathematics subject,
// rendered alongside (and superseding for interactive use) the flat
// `routes/en/subjects/mathematics.tsx` file.
//
// Renders: subject header + 5×8 mastery matrix + the 4 sub-route cards
// (syllabus / exam-papers / marking-schemes / study-plan) + bilingual
// EN+GA mirror link.

import * as React from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { BIEPSubjectPage } from "../../../components/BIEPSubjectPage";
import { getBIEPSubject, isBIEPSubject } from "../../../lib/bi-ep";

export const Route = createFileRoute("/en/subjects/mathematics/")({
  component: MathematicsPerSubjectLanding,
});

function MathematicsPerSubjectLanding() {
  if (!isBIEPSubject("mathematics")) {
    return <div>Mathematics subject metadata not found.</div>;
  }
  const subject = getBIEPSubject("mathematics");
  if (!subject) {
    return <div>Mathematics subject metadata not found.</div>;
  }
  return (
    <div className="flex flex-col gap-6">
      <BIEPSubjectPage subject={subject} language="en" />
      <nav
        aria-label="Mathematics interactive sub-routes"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 px-6"
      >
        <SubRouteCard
          to="/en/subjects/mathematics/syllabus"
          title="Syllabus"
          blurb="NCCA syllabus topics + learning outcomes"
        />
        <SubRouteCard
          to="/en/subjects/mathematics/exam-papers"
          title="Past exam papers"
          blurb="All Mathematics past exam papers tagged by topic + paper + year"
        />
        <SubRouteCard
          to="/en/subjects/mathematics/marking-schemes"
          title="Marking schemes"
          blurb="PCLM (Partial Credit, Logical Marking) patterns"
        />
        <SubRouteCard
          to="/en/subjects/mathematics/study-plan"
          title="Study plan"
          blurb="Generate a per-subject study plan via the BAML backend"
        />
      </nav>
      <div className="px-6 text-sm text-slate-500">
        <Link to="/ga/subjects/mata">Gaeilge: Mata →</Link>
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
