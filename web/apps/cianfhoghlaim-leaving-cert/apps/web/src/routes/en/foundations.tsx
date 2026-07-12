// /en/foundations — 5 NCCA root-level programme PDFs
// Per openspec/changes/cianfhoghlaim-website-rewrite/tasks.md B.9

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel, CiSemanticPill } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/foundations")({
  component: FoundationsIndex,
});

const FOUNDATIONS = [
  {
    slug: "key-competencies",
    title: "5 NCCA Key Competencies",
    file: "key-competencies-in-senior-cycle_en.pdf",
    color: "#10b981",
    pages: 14,
    blurb: "The 5 Key Competencies that frame the entire NCCA Senior Cycle. BAML ExtractedKeyCompetencies gives you a per-subject 5×8 mastery matrix.",
    source_pdf: "leaving_certificate/key-competencies-in-senior-cycle_en.pdf",
  },
  {
    slug: "sc-l1-l2-programme",
    title: "SC L1/L2 Programme Statement",
    file: "SC-L1-L2-Programme-Statement.pdf",
    color: "#3b82f6",
    pages: 12,
    blurb: "The Senior Cycle L1 (Foundation) and L2 (Ordinary) programme statement. Defines the rationale + aims + expectations for students targeting these levels.",
    source_pdf: "leaving_certificate/SC-L1-L2-Programme-Statement.pdf",
  },
  {
    slug: "scr-advisory",
    title: "SCR Advisory",
    file: "scr-advisory-report_en.pdf",
    color: "#b91c1c",
    pages: 11,
    blurb: "The State Examinations Commission Advisory Report. Chief Examiner commentary on past LC papers, common mistakes, marker expectations. BAML ExtractedMarkingScheme.",
    source_pdf: "leaving_certificate/scr-advisory-report_en.pdf",
  },
  {
    slug: "online-learning",
    title: "Online Learning Potential",
    file: "the-potential-of-online-learning-environments_en.pdf",
    color: "#f59e0b",
    pages: 8,
    blurb: "The NCCA document on the potential of online learning environments. Informs the practice page's online pedagogy recommendations.",
    source_pdf: "leaving_certificate/the-potential-of-online-learning-environments_en.pdf",
  },
  {
    slug: "online-certification",
    title: "Online Certification Potential",
    file: "the-potential-of-technology-to-support-online-certification-and-reporting.pdf",
    color: "#a855f7",
    pages: 10,
    blurb: "The NCCA document on the potential of technology to support online certification and reporting. Informs the cianfhoghlaim certification flow.",
    source_pdf: "leaving_certificate/the-potential-of-technology-to-support-online-certification-and-reporting.pdf",
  },
];

function FoundationsIndex() {
  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-6 p-6">
      <div className="flex flex-col gap-2">
        <h1 className="font-cinzel text-3xl font-bold text-slate-100">
          5 Foundations
        </h1>
        <p className="text-slate-300 max-w-3xl">
          The 5 NCCA root-level programme PDFs at the root of
          leaving_certificate/. The dlt ncca_root_pdfs.py extraction
          ingests them + the baml ExtractKeyCompetencies + ExtractProgramme
          + ExtractSCRAdvisory + ExtractOnlineLearning + ExtractOnlineCertification
          functions process them. Each is rendered as a marimo notebook
          for the teachers.
        </p>
      </div>

      <CiTextbookPanel title="5 NCCA root-level PDFs" material="parchment">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {FOUNDATIONS.map((f) => (
            <Link
              key={f.slug}
              to={`/en/foundations/${f.slug}`}
              className="p-4 rounded-lg bg-slate-900 border-2 transition-colors hover:border-emerald-400"
              style={{ borderColor: f.color }}
            >
              <div className="text-lg font-bold text-slate-100">{f.title}</div>
              <div className="text-xs text-slate-500 font-mono mt-1">{f.file}</div>
              <div className="text-sm text-slate-300 mt-2">{f.blurb}</div>
              <div className="mt-2 flex items-center gap-2 text-xs">
                <CiSemanticPill kind="eiraic" label={`${f.pages} pages`} />
              </div>
            </Link>
          ))}
        </div>
      </CiTextbookPanel>
    </div>
  );
}