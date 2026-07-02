// /en/practice — Practice session start
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R5.

import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { CiTextbookPanel, CiBoonsChoice, CiDetailCell } from "@cianfhoghlaim/ui";
import { useState } from "react";

export const Route = createFileRoute("/en/practice")({
  component: PracticePage,
});

const SUBJECTS = [
  { slug: "mathematics", name_en: "Mathematics", color: "#2563eb" },
  { slug: "applied_mathematics", name_en: "Applied Mathematics", color: "#7c3aed" },
  { slug: "chemistry", name_en: "Chemistry", color: "#16a34a" },
  { slug: "geography", name_en: "Geography", color: "#ca8a04" },
  { slug: "history", name_en: "History", color: "#b91c1c" },
  { slug: "english", name_en: "English", color: "#ea580c" },
  { slug: "gaeilge", name_en: "Gaeilge", color: "#059669" },
  { slug: "computer_science", name_en: "Computer Science", color: "#475569" },
];

function PracticePage() {
  const navigate = useNavigate();
  const [selectedSubject, setSelectedSubject] = useState<string | null>(null);

  const handleStart = () => {
    if (selectedSubject) {
      navigate({
        to: "/en/leaving-cert/$subject/practice/$topic",
        params: { subject: selectedSubject, topic: "introduction" },
      });
    }
  };

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          Start a Practice Session
        </h1>
        <p className="text-slate-400 text-lg">
          Choose an NCCA subject + a topic to start a formative item practice
        </p>
      </div>

      <CiTextbookPanel title="Select a Subject" material="knotwork">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {SUBJECTS.map((s) => (
            <button
              key={s.slug}
              onClick={() => setSelectedSubject(s.slug)}
              className="p-3 rounded-xl bg-slate-900 border-2 transition-colors text-left"
              style={{
                borderColor: selectedSubject === s.slug ? s.color : "#334155",
              }}
            >
              <div className="text-sm font-medium text-slate-100">{s.name_en}</div>
              <div className="text-xs text-slate-400 mt-1 font-mono" style={{ color: s.color }}>
                {s.slug}
              </div>
            </button>
          ))}
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel title="Select a Topic" material="parchment">
        <CiBoonsChoice
          prompt="How would you like to start?"
          choices={[
            { id: "introduction", label: "Introduction", description: "Start with the basics" },
            { id: "core-topics", label: "Core Topics", description: "The 4 mandatory topics" },
            { id: "exam-prep", label: "Exam Prep", description: "Focused on the LC exam" },
          ]}
          onChoose={(choice) => {
            if (selectedSubject) {
              navigate({
                to: "/en/leaving-cert/$subject/practice/$topic",
                params: { subject: selectedSubject, topic: choice },
              });
            }
          }}
          subjectColor={selectedSubject?.replace("_", "-")}
        />
      </CiTextbookPanel>
    </div>
  );
}