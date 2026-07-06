// /en/foundations — 5 NCCA root-level PDFs landing page

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel, CiDetailCell } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/foundations")({
  component: FoundationsIndex,
});

const FOUNDATIONS = [
  {
    slug: "key-competencies",
    name: "5 NCCA Key Competencies",
    file: "key-competencies-in-senior-cycle_en.pdf",
    color: "#059669",
    description: "The 5 Key Competencies that frame the entire NCCA Senior Cycle: Communicating, Information Processing, Critical & Creative Thinking, Personal Effectiveness, Working with Others.",
  },
  {
    slug: "sc-l1-l2-programme",
    name: "SC L1/L2 Programme Statement",
    file: "SC-L1-L2-Programme-Statement.pdf",
    color: "#2563eb",
    description: "The Senior Cycle L1 (Foundation) + L2 (Ordinary) programme statement — the rationale, aims, expectations for students.",
  },
  {
    slug: "scr-advisory",
    name: "SCR Advisory Report",
    file: "scr-advisory-report_en.pdf",
    color: "#b91c1c",
    description: "The State Examinations Commission Advisory Report — Chief Examiner commentary on the past LC papers, common mistakes, marker expectations.",
  },
  {
    slug: "online-learning",
    name: "Online Learning Potential",
    file: "the-potential-of-online-learning-environments_en.pdf",
    color: "#ca8a04",
    description: "The NCCA document on the potential of online learning environments — informs the practice page's online pedagogy recommendations.",
  },
  {
    slug: "online-certification",
    name: "Online Certification Potential",
    file: "the-potential-of-technology-to-support-online-certification-and-reporting.pdf",
    color: "#16a34a",
    description: "The NCCA document on the potential of technology to support online certification and reporting — informs the CIANFHLOGHLAIM OS practice page certification flow.",
  },
];

function FoundationsIndex() {
  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-6 p-6">
      <div className="flex flex-col gap-2">
        <div className="text-sm text-slate-500 font-mono">cianfhoghlaim / foundations</div>
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          5 Foundations
        </h1>
        <p className="text-slate-400 text-lg">
          The 5 NCCA root-level programme PDFs at{" "}
          <code className="text-amber-400">cianfhoghlaim/leaving_certificate/</code>.
        </p>
      </div>

      <CiTextbookPanel title="The 5 Foundations" material="parchment">
        <div className="space-y-3">
          {FOUNDATIONS.map((f) => (
            <Link
              key={f.slug}
              to={`/en/foundations/${f.slug}`}
              className="block p-4 rounded-lg bg-slate-900 border-2 hover:border-amber-400 transition-colors"
              style={{ borderColor: f.color }}
            >
              <div className="flex items-center justify-between">
                <div className="text-lg font-bold" style={{ color: f.color }}>{f.name}</div>
                <div className="text-xs text-slate-500 font-mono">{f.file}</div>
              </div>
              <div className="text-sm text-slate-300 mt-2">{f.description}</div>
            </Link>
          ))}
        </div>
      </CiTextbookPanel>
    </div>
  );
}