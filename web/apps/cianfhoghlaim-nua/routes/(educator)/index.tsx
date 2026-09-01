// routes/(educator)/index.tsx — the educator route group landing
// page in the consolidated cianfhoghlaim-nua app.
//
// Per the 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 change.
// Phase 4 ships the NCCE learning-graph showcase + pedagogy
// overlay + cross-jurisdiction equivalencies into this route
// group.

import * as React from "react";
import { createFileRoute } from "@tanstack/react-router";

import { SubjectCardGrid, type SubjectCardData } from "@cianfhoghlaim/a2ui";

export const Route = createFileRoute("/(educator)/")({
  component: EducatorLandingPage,
});

const NCCA_LC_SUBJECTS: SubjectCardData[] = [
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
    stage: "lc",
    jurisdiction: "ireland",
    ncca_code: "LC-GAEL-LO",
    lo_codes_count: 38,
    past_papers_count: 10,
    marking_schemes_count: 10,
    colour: "#28955e",
  },
  {
    slug: "english",
    display_name: "English",
    display_name_ga: "Bearla",
    stage: "lc",
    jurisdiction: "ireland",
    ncca_code: "LC-ENGL-LO",
    lo_codes_count: 35,
    past_papers_count: 12,
    marking_schemes_count: 12,
    colour: "#5a4fcf",
  },
  {
    slug: "geography",
    display_name: "Geography",
    display_name_ga: "Tíreolaíocht",
    stage: "lc",
    jurisdiction: "ireland",
    ncca_code: "LC-GEOG-LO",
    lo_codes_count: 40,
    past_papers_count: 12,
    marking_schemes_count: 12,
    colour: "#1e80c6",
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

function EducatorLandingPage(): React.ReactElement {
  return (
    <section className="space-y-6">
      <header>
        <h2 className="text-2xl font-bold text-slate-900">
          Educator — NCCA syllabus intelligence
        </h2>
        <p className="mt-2 text-slate-600">
          The NCCA syllabus intelligence surface for educators.
          Phase 4 ships the NCCE learning-graph showcase + pedagogy
          overlay + 48 cross-jurisdiction equivalencies. Phase 5
          broadens the 4 Phase 1 subjects to the 8 NCCA LC subjects
          + the 6 NCCA-adjacent subjects.
        </p>
      </header>

      <SubjectCardGrid
        subjects={NCCA_LC_SUBJECTS}
        onSelect={(slug) => {
          window.location.href = `/educator/subject/${slug}`;
        }}
      />

      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
        <h3 className="text-sm font-semibold text-amber-900">
          Phase 4 — coming soon
        </h3>
        <p className="mt-1 text-sm text-amber-800">
          The NCCE learning-graph showcase (5 NCCE PDFs → row × column
          graphs + equivalencies + pedagogy overlay) ships in Phase 4.
          Tracked via
          <code className="ml-1">2026-09-XX-biep-ncce-showcase-v1</code>
          (to be authored).
        </p>
      </div>
    </section>
  );
}

export default EducatorLandingPage;