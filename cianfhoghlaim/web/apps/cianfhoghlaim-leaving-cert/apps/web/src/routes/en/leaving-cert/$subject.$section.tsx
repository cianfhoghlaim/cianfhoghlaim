// /en/leaving-cert/$subject/$section — per-section page (syllabus/past-exams/etc)
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R2.

import { createFileRoute } from "@tanstack/react-router";
import { CiTextbookPanel } from "@cianfhoghlaim/ui";
import { CiConceptMapDiagram, type ConceptNode } from "@cianfhoghlaim/ui/concept-map-diagram";
import { CiTopicHeatmapDiagram, type HeatmapCell } from "@cianfhoghlaim/ui/topic-heatmap-diagram";
import { CiPCLMFlowDiagram, type PCLMNode } from "@cianfhoghlaim/ui/pclm-flow-diagram";
import { CiQuestionSankeyDiagram, type SankeyNode, type SankeyFlow } from "@cianfhoghlaim/ui/question-sankey-diagram";

export const Route = createFileRoute("/en/leaving-cert/$subject/$section")({
  component: SectionPage,
});

// Sample data (real data comes from BAML + Dagster)
const SAMPLE_CONCEPT_MAP: ConceptNode = {
  id: "mathematics-root",
  label: "Mathematics — 5 NCCA Key Competencies",
  type: "root",
  children: [
    {
      id: "communicating",
      label: "Communicating · Brigid",
      type: "subject",
      children: [
        { id: "math-lo-1", label: "LC-MATHS-LO-1.1", type: "lo" },
        { id: "math-lo-2", label: "LC-MATHS-LO-1.2", type: "lo" },
      ],
    },
    {
      id: "information-processing",
      label: "Information Processing · Ogma",
      type: "subject",
      children: [
        { id: "math-lo-3", label: "LC-MATHS-LO-2.1", type: "lo" },
        { id: "math-lo-4", label: "LC-MATHS-LO-2.2", type: "lo" },
      ],
    },
    {
      id: "critical-creative-thinking",
      label: "Critical & Creative · Lugh",
      type: "subject",
      children: [
        { id: "math-lo-5", label: "LC-MATHS-LO-3.1", type: "lo" },
      ],
    },
    {
      id: "personal-effectiveness",
      label: "Personal Effectiveness · Dian Cecht",
      type: "subject",
      children: [
        { id: "math-lo-6", label: "LC-MATHS-LO-4.1", type: "lo" },
      ],
    },
    {
      id: "working-with-others",
      label: "Working with Others · Trí Dé Dána",
      type: "subject",
      children: [
        { id: "math-lo-7", label: "LC-MATHS-LO-5.1", type: "lo" },
      ],
    },
  ],
};

const SAMPLE_HEATMAP: HeatmapCell[] = [
  // 8 topics × 2 papers × 3 years (sample)
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
        {
          id: "mistake-1a-1",
          label: "Common mistake: off-by-one in setup",
          type: "mistake",
        },
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
        {
          id: "mistake-1c-1",
          label: "Common mistake: unit error",
          type: "mistake",
        },
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

  // Diagram route (per T6.6 + R3)
  if (section === "syllabus") {
    return (
      <div className="max-w-6xl mx-auto flex flex-col gap-6">
        <h1 className="font-cinzel text-2xl font-bold text-slate-100">
          {subject.replace("_", " ")} — Syllabus (with Concept-map diagram)
        </h1>
        <CiTextbookPanel title="Concept-map · 5 NCCA Key Competencies" material="parchment">
          <CiConceptMapDiagram
            data={SAMPLE_CONCEPT_MAP}
            subjectColor={subject.replace("_", "-")}
          />
        </CiTextbookPanel>
      </div>
    );
  }

  if (section === "past-exams") {
    return (
      <div className="max-w-6xl mx-auto flex flex-col gap-6">
        <h1 className="font-cinzel text-2xl font-bold text-slate-100">
          {subject.replace("_", " ")} — Past Exams (with Topic-heatmap diagram)
        </h1>
        <CiTextbookPanel title="Topic-frequency Heatmap · Question × Paper × Topic × Year" material="knotwork">
          <CiTopicHeatmapDiagram
            data={SAMPLE_HEATMAP}
            subjectColor={subject.replace("_", "-")}
          />
        </CiTextbookPanel>
        <CiTextbookPanel title="Question → Topic → Difficulty → Year Sankey" material="gold-leaf">
          <CiQuestionSankeyDiagram
            nodes={SAMPLE_SANKEY_NODES}
            flows={SAMPLE_SANKEY_FLOWS}
            subjectColor={subject.replace("_", "-")}
          />
        </CiTextbookPanel>
      </div>
    );
  }

  if (section === "marking-schemes") {
    return (
      <div className="max-w-6xl mx-auto flex flex-col gap-6">
        <h1 className="font-cinzel text-2xl font-bold text-slate-100">
          {subject.replace("_", " ")} — Marking Schemes (with PCLM flow)
        </h1>
        <CiTextbookPanel title="PCLM Flow · Partial Credit, Logical Marking" material="ink-wash">
          <CiPCLMFlowDiagram
            data={SAMPLE_PCLM}
            subjectColor={subject.replace("_", "-")}
          />
        </CiTextbookPanel>
      </div>
    );
  }

  // Default fallback
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-2xl font-bold text-slate-100">
        {subject.replace("_", " ")} — {section.replace("-", " ")}
      </h1>
      <CiTextbookPanel title={`${section.replace("-", " ")} content`} material="parchment">
        <p className="text-slate-300">
          The {section.replace("-", " ")} section for {subject.replace("_", " ")}.
        </p>
        <p className="text-slate-500 text-sm italic mt-4">
          (This is a placeholder; the real content is wired to the BAML extraction + Dagster asset)
        </p>
      </CiTextbookPanel>
    </div>
  );
}