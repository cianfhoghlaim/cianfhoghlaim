// /en/leaving-cert/$subject/$section — Per-section page (the 6-section shell)
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R2.
// The 6 sections: syllabus / past-exams / marking-schemes / prioritisation / exam-tips / pdf-library

import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import {
  CiTextbookPanel,
  CiSemanticPill,
  CiProgressRing,
  CiDetailCell,
  CiBoonsChoice,
} from "@cianfhoghlaim/ui";
import {
  CiConceptMapDiagram,
  CiTopicHeatmapDiagram,
  CiPCLMFlowDiagram,
  CiQuestionSankeyDiagram,
} from "@cianfhoghlaim/ui";
import type { ConceptNode } from "@cianfhoghlaim/ui/concept-map-diagram";
import type { HeatmapCell } from "@cianfhoghlaim/ui/topic-heatmap-diagram";
import type { PCLMNode } from "@cianfhoghlaim/ui/pclm-flow-diagram";
import type { SankeyNode, SankeyFlow } from "@cianfhoghlaim/ui/question-sankey-diagram";
import { getMasteryForSubject } from "@cianfhoghlaim/i18n/mastery";

export const Route = createFileRoute("/en/leaving-cert/$subject/$section")({
  component: SectionPage,
});

const SECTIONS: Record<string, { title: string; description: string }> = {
  syllabus: {
    title: "Syllabus Analysis",
    description: "The NCCA syllabus topics + learning outcomes + weightings",
  },
  "past-exams": {
    title: "Past Exam Questions",
    description: "All past exam questions (2017-2025) tagged by topic + paper + year",
  },
  "marking-schemes": {
    title: "Marking Schemes",
    description: "PCLM (Partial Credit, Logical Marking) patterns + common mistakes",
  },
  prioritisation: {
    title: "Topic Prioritisation",
    description: "Ranked by marks ÷ study-hours (the Attempted + Familiar + Proficient + Mastered ladder)",
  },
  "exam-tips": {
    title: "Exam Layout Tips",
    description: "Paper structure + time per question + common traps + marker expectations (per the SCR Advisory)",
  },
  "pdf-library": {
    title: "PDF Library",
    description: "Original NCCA syllabus + SEC exam papers + marking schemes (R2-signed URLs)",
  },
};

// Sample concept-map data (Mathematics)
const SAMPLE_CONCEPT_MAP: ConceptNode = {
  id: "mathematics-root",
  label: "Mathematics",
  type: "root",
  children: [
    {
      id: "math-communicating",
      label: "Communicating · Brigid",
      type: "subject",
      children: [
        { id: "math-lo-1-1", label: "LC-MA-LO-1.1", type: "lo" },
        { id: "math-lo-1-2", label: "LC-MA-LO-1.2", type: "lo" },
      ],
    },
    {
      id: "math-information-processing",
      label: "Information Processing · Ogma",
      type: "subject",
      children: [
        { id: "math-lo-2-1", label: "LC-MA-LO-2.1", type: "lo" },
        { id: "math-lo-2-2", label: "LC-MA-LO-2.2", type: "lo" },
      ],
    },
  ],
};

const SAMPLE_HEATMAP: HeatmapCell[] = [
  { topic: "Algebra", paper: "P1", year: 2020, value: 80 },
  { topic: "Algebra", paper: "P1", year: 2021, value: 90 },
  { topic: "Algebra", paper: "P1", year: 2022, value: 85 },
  { topic: "Calculus", paper: "P1", year: 2020, value: 70 },
  { topic: "Calculus", paper: "P1", year: 2021, value: 75 },
  { topic: "Calculus", paper: "P1", year: 2022, value: 80 },
  { topic: "Probability", paper: "P2", year: 2020, value: 60 },
  { topic: "Probability", paper: "P2", year: 2021, value: 65 },
  { topic: "Probability", paper: "P2", year: 2022, value: 70 },
];

const SAMPLE_PCLM: PCLMNode = {
  id: "q-2022-p1-1",
  label: "Question 1 (Paper 1, 2022)",
  type: "question",
  children: [
    {
      id: "criterion-1a",
      label: "Setup · 2 marks",
      type: "criterion",
      children: [
        { id: "mistake-1a-1", label: "Common mistake: off-by-one in setup", type: "mistake" },
      ],
    },
    {
      id: "criterion-1b",
      label: "Working · 5 marks",
      type: "criterion",
    },
    {
      id: "criterion-1c",
      label: "Final answer · 3 marks",
      type: "criterion",
      children: [
        { id: "mistake-1c-1", label: "Common mistake: unit error", type: "mistake" },
      ],
    },
  ],
};

const SAMPLE_SANKEY_NODES: SankeyNode[] = [
  { id: "q-2020-1", label: "Q1-2020", layer: "question" },
  { id: "q-2021-1", label: "Q1-2021", layer: "question" },
  { id: "q-2022-1", label: "Q1-2022", layer: "question" },
  { id: "topic-algebra", label: "Algebra", layer: "topic" },
  { id: "topic-calculus", label: "Calculus", layer: "topic" },
  { id: "diff-easy", label: "Easy", layer: "difficulty" },
  { id: "diff-hard", label: "Hard", layer: "difficulty" },
  { id: "year-2020", label: "2020", layer: "year" },
  { id: "year-2022", label: "2022", layer: "year" },
];

const SAMPLE_SANKEY_FLOWS: SankeyFlow[] = [
  { source: "q-2020-1", target: "topic-algebra", value: 30 },
  { source: "q-2021-1", target: "topic-algebra", value: 40 },
  { source: "q-2022-1", target: "topic-calculus", value: 50 },
  { source: "topic-algebra", target: "diff-easy", value: 70 },
  { source: "topic-calculus", target: "diff-hard", value: 50 },
  { source: "diff-easy", target: "year-2020", value: 70 },
  { source: "diff-hard", target: "year-2022", value: 50 },
];

function SectionPage() {
  const { subject, section } = Route.useParams();
  const sec = SECTIONS[section];

  if (!sec) {
    throw notFound({ data: { subject, section } });
  }

  const mastery = getMasteryForSubject(subject);

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Link to="/en/subjects" className="hover:text-emerald-400">All subjects</Link>
          <span>›</span>
          <Link to={`/en/leaving-cert/${subject}`} className="hover:text-emerald-400">{subject.replace("_", " ")}</Link>
          <span>›</span>
          <span className="text-slate-300">{sec.title}</span>
        </div>
        <h1 className="font-cinzel text-3xl font-bold text-slate-100">
          {subject.replace("_", " ")} — {sec.title}
        </h1>
        <p className="text-slate-400">{sec.description}</p>
      </div>

      {section === "syllabus" && (
        <>
          <CiTextbookPanel title="Concept-map (5 NCCA Key Competencies)" material="parchment">
            <CiConceptMapDiagram data={SAMPLE_CONCEPT_MAP} subjectColor={subject.replace("_", "-")} />
          </CiTextbookPanel>

          <CiTextbookPanel title="5×8 Mastery Matrix" material="knotwork">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="text-left text-slate-400 p-2">Key Competency</th>
                    <th className="text-center text-slate-400 p-2">Mastery</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(mastery).map(([kc, value]) => (
                    <tr key={kc} className="border-t border-slate-700">
                      <td className="p-2 text-slate-300">
                        {kc.split("-").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ")}
                      </td>
                      <td className="p-2 text-center">
                        <CiProgressRing
                          value={value as number}
                          tier={
                            (value as number) >= 80 ? "mastered" :
                            (value as number) >= 60 ? "proficient" :
                            (value as number) >= 40 ? "familiar" : "attempted"
                          }
                          size={50}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CiTextbookPanel>
        </>
      )}

      {section === "past-exams" && (
        <>
          <CiTextbookPanel title="Topic-frequency Heatmap (2017-2025)" material="knotwork">
            <CiTopicHeatmapDiagram data={SAMPLE_HEATMAP} subjectColor={subject.replace("_", "-")} />
          </CiTextbookPanel>

          <CiTextbookPanel title="Question → Topic → Difficulty → Year Sankey" material="ink-wash">
            <CiQuestionSankeyDiagram nodes={SAMPLE_SANKEY_NODES} flows={SAMPLE_SANKEY_FLOWS} subjectColor={subject.replace("_", "-")} />
          </CiTextbookPanel>
        </>
      )}

      {section === "marking-schemes" && (
        <CiTextbookPanel title="PCLM Marking Flow" material="ink-wash">
          <CiPCLMFlowDiagram data={SAMPLE_PCLM} subjectColor={subject.replace("_", "-")} />
        </CiTextbookPanel>
      )}

      {section === "prioritisation" && (
        <CiTextbookPanel title="Topic Prioritisation (marks ÷ study-hours)" material="gold-leaf">
          <div className="space-y-2">
            {Object.entries(mastery)
              .sort(([, a], [, b]) => (b as number) - (a as number))
              .map(([kc, value], i) => (
                <CiDetailCell
                  key={kc}
                  icon={<span className="text-lg font-mono">{i + 1}</span>}
                  title={kc.split("-").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ")}
                  metadata={`${value}% mastery`}
                  description={`Prioritise this competency — based on the Attempted + Familiar + Proficient + Mastered ladder.`}
                />
              ))}
          </div>
        </CiTextbookPanel>
      )}

      {section === "exam-tips" && (
        <CiTextbookPanel title="Exam Layout Tips (per the SCR Advisory)" material="knotwork">
          <div className="space-y-2">
            <CiDetailCell
              icon={<span className="text-lg">⏱</span>}
              title="Time per question"
              metadata="6 minutes per 10 marks"
              description="Allocate approximately 6 minutes per 10 marks. For a 10-mark question, spend ~1 minute on planning, ~4 minutes on working, ~1 minute on review."
            />
            <CiDetailCell
              icon={<span className="text-lg">🎯</span>}
              title="Marker expectations"
              metadata="PCLM conventions"
              description="The marker looks for: clear setup + working + final answer. Partial credit is awarded for correct reasoning even if the final answer is wrong."
            />
            <CiDetailCell
              icon={<span className="text-lg">⚠</span>}
              title="Common traps"
              metadata="Avoid these"
              description="Unit errors + off-by-one + sign errors. The most common mistake in PCLM is the setup; the second most common is the final answer unit."
            />
          </div>
        </CiTextbookPanel>
      )}

      {section === "pdf-library" && (
        <CiTextbookPanel title="PDF Library (R2-signed URLs)" material="parchment">
          <div className="space-y-2">
            {[
              { name: "NCCA Syllabus (Mathematics, HL)", url: "s3://cianfhoghlaim-leaving-cert/syllabus/mathematics/2025.pdf" },
              { name: "2024 Paper 1 (Mathematics, HL)", url: "s3://cianfhoghlaim-leaving-cert/exam-papers/mathematics/2024-paper-1.pdf" },
              { name: "2024 Paper 2 (Mathematics, HL)", url: "s3://cianfhoghlaim-leaving-cert/exam-papers/mathematics/2024-paper-2.pdf" },
              { name: "2024 Marking Scheme (Paper 1)", url: "s3://cianfhoghlaim-leaving-cert/marking-schemes/mathematics/2024-paper-1-ms.pdf" },
              { name: "2024 Marking Scheme (Paper 2)", url: "s3://cianfhoghlaim-leaving-cert/marking-schemes/mathematics/2024-paper-2-ms.pdf" },
            ].map((pdf) => (
              <CiDetailCell
                key={pdf.name}
                icon={<span className="text-lg">📄</span>}
                title={pdf.name}
                metadata={pdf.url}
                description="Click to download (R2-signed URL — expires in 1 hour)"
              />
            ))}
          </div>
        </CiTextbookPanel>
      )}
    </div>
  );
}