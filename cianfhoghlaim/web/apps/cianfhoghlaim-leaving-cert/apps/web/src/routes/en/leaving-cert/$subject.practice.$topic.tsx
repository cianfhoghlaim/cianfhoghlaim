// /en/leaving-cert/$subject/practice/$topic — Practice page
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R5.

import { createFileRoute } from "@tanstack/react-router";
import { CiButton, CiProgressRing, CiBoonsChoice } from "@cianfhoghlaim/ui";
import { CiTextbookPanel } from "@cianfhoghlaim/ui";
import { CiStreakFlame } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/leaving-cert/$subject/practice/$topic")({
  component: PracticePage,
});

function PracticePage() {
  const { subject, topic } = Route.useParams();

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-cinzel text-2xl font-bold text-slate-100">
            {subject.replace("_", " ")} — {topic.replace("-", " ")}
          </h1>
          <p className="text-slate-400 text-sm">
            NCCA Leaving Certificate · 3-way boon choice · tactile press feedback
          </p>
        </div>
        <CiStreakFlame days={42} />
      </div>

      {/* Éraic tier progress */}
      <CiTextbookPanel title="Éraic Tier Progress" material="gold-leaf">
        <div className="flex items-center gap-4">
          <CiProgressRing value={75} tier="proficient" eiraicTier={4} label="Spear of Assal" />
          <div className="flex-1">
            <div className="text-sm text-slate-300 mb-1">
              You are working toward Éraic tier 4/13 (Spear of Assal — Precise Reasoning)
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2">
              <div className="bg-emerald-500 h-2 rounded-full" style={{ width: "75%" }} />
            </div>
          </div>
        </div>
      </CiTextbookPanel>

      {/* The 3-way boon choice (Hades pattern) */}
      <CiTextbookPanel title="Question 1 of 5 — Choose Your Approach" material="parchment">
        <CiBoonsChoice
          prompt="How would you like to demonstrate mastery of this topic?"
          choices={[
            {
              id: "choice-1",
              label: "Worked Solution",
              description: "Multi-step solution with marking-scheme points",
              color: "#2563eb",
              difficulty: "medium",
            },
            {
              id: "choice-2",
              label: "Visual Proof",
              description: "Read from a graph, table, or diagram",
              color: "#10b981",
              difficulty: "high",
            },
            {
              id: "choice-3",
              label: "Word Problem",
              description: "Real-world contextual application",
              color: "#f59e0b",
              difficulty: "low",
            },
          ]}
          subjectColor={subject.replace("_", "-")}
        />
      </CiTextbookPanel>

      {/* Feedback channel */}
      <CiTextbookPanel title="Feedback Channel (the 4 Brown Ajah members)" material="ink-wash">
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-slate-800 rounded-lg">
            <div className="text-sm font-medium text-blue-400">Math Tutor (concrete + worked-example)</div>
            <p className="text-xs text-slate-400 mt-1">Step-by-step worked solution</p>
          </div>
          <div className="p-3 bg-slate-800 rounded-lg">
            <div className="text-sm font-medium text-amber-400">Quest Guide (graduated hints)</div>
            <p className="text-xs text-slate-400 mt-1">4 levels: nudge → step-by-step</p>
          </div>
          <div className="p-3 bg-slate-800 rounded-lg">
            <div className="text-sm font-medium text-emerald-400">Curriculum Lookup (NCCA LO)</div>
            <p className="text-xs text-slate-400 mt-1">Direct NCCA learning outcome citation</p>
          </div>
          <div className="p-3 bg-slate-800 rounded-lg">
            <div className="text-sm font-medium text-purple-400">Research Assistant (cross-topic)</div>
            <p className="text-xs text-slate-400 mt-1">Cross-topic + cross-subject synthesis</p>
          </div>
        </div>
      </CiTextbookPanel>

      {/* Submit button */}
      <div className="flex justify-end">
        <CiButton variant="primary" size="lg">
          Submit Response
        </CiButton>
      </div>
    </div>
  );
}