// /en/foundations/$slug — 5 NCCA root-level PDF detail pages

import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { CiTextbookPanel, CiDetailCell } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/foundations/$slug")({
  component: FoundationDetail,
});

const FOUNDATIONS: Record<string, {
  name: string;
  file: string;
  color: string;
  description: string;
  keyTakeaways: string[];
  relatedSubjects: string[];
  relatedAgents: string[];
}> = {
  "key-competencies": {
    name: "5 NCCA Key Competencies",
    file: "key-competencies-in-senior-cycle_en.pdf",
    color: "#059669",
    description: "The 5 Key Competencies that frame the entire NCCA Senior Cycle. They appear in every subject specification as the cross-subject learning outcomes.",
    keyTakeaways: [
      "Communicating — reading, writing, speaking, listening in subject-specific contexts",
      "Information Processing — locating, evaluating, organising, applying information",
      "Critical & Creative Thinking — analysing, synthesising, generating novel ideas",
      "Personal Effectiveness — self-awareness, resilience, motivation, responsibility",
      "Working with Others — collaboration, communication, negotiation",
    ],
    relatedSubjects: ["mathematics", "english", "gaeilge", "computer_science"],
    relatedAgents: ["mathematics", "english"],
  },
  "sc-l1-l2-programme": {
    name: "SC L1/L2 Programme Statement",
    file: "SC-L1-L2-Programme-Statement.pdf",
    color: "#2563eb",
    description: "The Senior Cycle L1 (Foundation) and L2 (Ordinary) programme statement. The L1/L2 levels are designed for students who may not be aiming at L3 (Ordinary) or L4 (Higher).",
    keyTakeaways: [
      "L1 (Foundation Level) — designed for students with significant learning difficulties",
      "L2 (Ordinary Level) — designed for students targeting a pass in the LC",
      "Both L1 and L2 emphasise applied learning + vocational relevance",
      "Cross-curricular 5 Key Competencies underpin all subject specifications",
    ],
    relatedSubjects: ["mathematics", "english", "gaeilge"],
    relatedAgents: ["mathematics"],
  },
  "scr-advisory": {
    name: "SCR Advisory Report",
    file: "scr-advisory-report_en.pdf",
    color: "#b91c1c",
    description: "The State Examinations Commission Advisory Report — Chief Examiner commentary on past LC papers. Highlights common mistakes + marker expectations + paper-by-paper guidance.",
    keyTakeaways: [
      "Chief Examiner advice is the canonical source for exam layout tips",
      "Common mistakes are extracted into the practice page's exam layout tips",
      "Time per question + time per section + paper structure all derive from this",
      "Informs the BAML ExtractExamPaper + ExtractMarkingScheme schemas",
    ],
    relatedSubjects: ["english", "history", "geography", "mathematics"],
    relatedAgents: ["history", "english"],
  },
  "online-learning": {
    name: "Online Learning Potential",
    file: "the-potential-of-online-learning-environments_en.pdf",
    color: "#ca8a04",
    description: "The NCCA document on the potential of online learning environments. The cianfhoghlaim practice page is built on these pedagogical recommendations — formative assessment + iterative feedback + online content delivery.",
    keyTakeaways: [
      "Formative assessment with rapid feedback is more effective than summative",
      "Mixed online + offline learning paths (the 3-way boon choice pattern)",
      "Iteration over linear progression (the 4 feedback channels in the practice page)",
      "Self-paced practice with 4 graduated hint levels (the 'Show Answer' button + 4 channels)",
    ],
    relatedSubjects: ["computer_science", "gaeilge", "english"],
    relatedAgents: ["computer_science"],
  },
  "online-certification": {
    name: "Online Certification Potential",
    file: "the-potential-of-technology-to-support-online-certification-and-reporting.pdf",
    color: "#16a34a",
    description: "The NCCA document on the potential of technology to support online certification and reporting. The cianfhoghlaim certification flow + the daily Merkle anchor derive from this.",
    keyTakeaways: [
      "Hybrid online + in-person assessment (the 4 feedback channels)",
      "Digital badges (the 13 éraic tier progression) are a valid formative signal",
      "On-chain anchoring for transparency (the daily Merkle root, optional)",
      "Citation rigor + reproducibility + accessibility as design constraints",
    ],
    relatedSubjects: ["computer_science", "mathematics", "english"],
    relatedAgents: ["computer_science", "mathematics"],
  },
};

function FoundationDetail() {
  const { slug } = Route.useParams();
  const f = FOUNDATIONS[slug];

  if (!f) {
    throw notFound({ data: { slug } });
  }

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6 p-6">
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Link to="/en/foundations" className="hover:text-emerald-400">All foundations</Link>
          <span>›</span>
          <span className="text-slate-300">{f.name}</span>
        </div>
        <h1 className="font-cinzel text-4xl font-bold" style={{ color: f.color }}>
          {f.name}
        </h1>
        <p className="text-slate-400 text-sm font-mono">{f.file}</p>
        <p className="text-slate-300 text-lg">{f.description}</p>
      </div>

      <CiTextbookPanel title="Key Takeaways" material="parchment">
        <ul className="space-y-2">
          {f.keyTakeaways.map((k, i) => (
            <li key={i} className="flex items-start gap-2 text-slate-300">
              <span className="text-amber-400 font-bold">★</span>
              <span>{k}</span>
            </li>
          ))}
        </ul>
      </CiTextbookPanel>

      <CiTextbookPanel title="Related Subjects + ADK Agents" material="knotwork">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <h3 className="text-sm font-bold text-slate-100 mb-2">Related Subjects</h3>
            <div className="flex flex-wrap gap-2">
              {f.relatedSubjects.map((s) => (
                <Link
                  key={s}
                  to={`/en/subjects/${s}`}
                  className="px-2 py-1 rounded bg-slate-800 text-xs hover:underline"
                >
                  {s.replace("_", " ")}
                </Link>
              ))}
            </div>
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 mb-2">Related ADK Agents</h3>
            <div className="flex flex-wrap gap-2">
              {f.relatedAgents.map((a) => (
                <Link
                  key={a}
                  to={`/en/agents/${a}`}
                  className="px-2 py-1 rounded bg-slate-800 text-xs hover:underline"
                >
                  {a}_agent
                </Link>
              ))}
            </div>
          </div>
        </div>
      </CiTextbookPanel>
    </div>
  );
}