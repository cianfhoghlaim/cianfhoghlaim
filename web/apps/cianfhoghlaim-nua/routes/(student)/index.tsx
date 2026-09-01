// routes/(student)/index.tsx — the student route group landing page
// in the consolidated cianfhoghlaim-nua app.
//
// Per the 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 change
// (Phase 3 of the cianfhoghlaim-nua v6 era plan). The Phase 1
// study-plan routes are mounted under (student)/lc/<subject>/.

import * as React from "react";
import { createFileRoute, Link } from "@tanstack/react-router";

import { SubjectCardGrid, type SubjectCardData } from "@cianfhoghlaim/a2ui";

export const Route = createFileRoute("/(student)/")({
  component: StudentLandingPage,
});

const PHASE_1_SUBJECTS: SubjectCardData[] = [
  {
    slug: "chemistry",
    display_name: "Chemistry",
    display_name_ga: "Ceimic",
    stage: "lc",
    jurisdiction: "ireland",
    ncca_code: "LC-CHEM-LO",
    lo_codes_count: 45,
    past_papers_count: 12,
    marking_schemes_count: 12,
    colour: "#1e80c6",
  },
  {
    slug: "mathematics",
    display_name: "Mathematics",
    display_name_ga: "Matamaitic",
    stage: "lc",
    jurisdiction: "ireland",
    ncca_code: "LC-MATH-LO",
    lo_codes_count: 52,
    past_papers_count: 12,
    marking_schemes_count: 12,
    colour: "#cc9966",
  },
  {
    slug: "gaeilge",
    display_name: "Gaeilge",
    display_name_ga: "Gaeilge",
    stage: "lc",
    jurisdiction: "ireland",
    ncca_code: "LC-GAEL-LO",
    lo_codes_count: 38,
    past_papers_count: 10,
    marking_schemes_count: 10,
    colour: "#28955e",
  },
  {
    slug: "computer_science",
    display_name: "Computer Science",
    display_name_ga: "Ríomheolaíocht",
    stage: "lc",
    jurisdiction: "ireland",
    ncca_code: "LC-COMP-LO",
    lo_codes_count: 42,
    past_papers_count: 8,
    marking_schemes_count: 8,
    colour: "#5a4fcf",
  },
];

function StudentLandingPage(): React.ReactElement {
  return (
    <section className="space-y-6">
      <header>
        <h2 className="text-2xl font-bold text-slate-900">
          Student — Leaving Certificate subjects
        </h2>
        <p className="mt-2 text-slate-600">
          The chat-with-syllabus + oral study-plan surface for the 4
          Phase 1 LC subjects (chemistry + mathematics + gaeilge +
          computer_science). Phase 5 broadens to the 8 NCCA LC
          subjects + the 6 NCCA-adjacent subjects.
        </p>
      </header>

      <SubjectCardGrid
        subjects={PHASE_1_SUBJECTS}
        onSelect={(slug) => {
          window.location.href = `/lc/${slug}/study-plan`;
        }}
      />

      <div className="rounded-lg border border-slate-200 bg-white p-4">
        <h3 className="text-sm font-semibold text-slate-800">
          Phase 1 status
        </h3>
        <ul className="mt-2 space-y-1 text-sm text-slate-600">
          <li>• Study-plan generator: live (canonical Phase 1 planner)</li>
          <li>• Oral study plans: stub (Phase 6 wires Pipecat + Chatterbox)</li>
          <li>• Quest packs: live (consolidated qpack template)</li>
          <li>• Convex persistence: live (5 new tables)</li>
          <li>• A2UI catalog: live (11 components via @cianfhoghlaim/a2ui)</li>
        </ul>
      </div>
    </section>
  );
}

export default StudentLandingPage;