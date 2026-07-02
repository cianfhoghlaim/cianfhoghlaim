// /en/leaving-cert/$subject/practice/$topic — Practice detail page
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R5.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel, CiBoonsChoice, CiProgressRing, CiStreakFlame } from "@cianfhoghlaim/ui";
import { useState } from "react";

export const Route = createFileRoute("/en/leaving-cert/$subject/practice/$topic")({
  component: PracticeDetailPage,
});

const SAMPLE_QUESTIONS = [
  {
    id: "q1",
    prompt: "Find the complex number z such that z² = -1 and Im(z) > 0.",
    type: "WORKED_SOLUTION",
    difficulty: 3,
    expected_answer: "z = i",
    marking_scheme: "Setup (1 mark) + Working (2 marks) + Final (1 mark)",
  },
  {
    id: "q2",
    prompt: "Prove that for any complex number z, |z|² = z · z̄ (where z̄ is the complex conjugate).",
    type: "PROOF",
    difficulty: 4,
    expected_answer: "Let z = a + bi, then z̄ = a - bi, so z · z̄ = (a + bi)(a - bi) = a² + b² = |z|²",
    marking_scheme: "Setup (2 marks) + Working (4 marks) + QED (1 mark)",
  },
  {
    id: "q3",
    prompt: "Differentiate f(x) = x² sin(x) with respect to x.",
    type: "WORD_PROBLEM",
    difficulty: 2,
    expected_answer: "f'(x) = 2x sin(x) + x² cos(x)",
    marking_scheme: "Product rule (2 marks) + Application (2 marks) + Final (1 mark)",
  },
];

function PracticeDetailPage() {
  const { subject, topic } = Route.useParams();
  const [questionIndex, setQuestionIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);

  const currentQuestion = SAMPLE_QUESTIONS[questionIndex % SAMPLE_QUESTIONS.length];
  const isFirstQuestion = questionIndex === 0;

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Link to="/en/practice" className="hover:text-emerald-400">Practice</Link>
          <span>›</span>
          <Link to={`/en/leaving-cert/${subject}`} className="hover:text-emerald-400">{subject.replace("_", " ")}</Link>
          <span>›</span>
          <span className="text-slate-300">{topic.replace("-", " ")}</span>
        </div>
        <div className="flex items-center justify-between">
          <h1 className="font-cinzel text-2xl font-bold text-slate-100">
            {subject.replace("_", " ")} — {topic.replace("-", " ")}
          </h1>
          <CiStreakFlame days={42} />
        </div>
        <div className="flex items-center gap-2">
          <CiProgressRing value={75} tier="proficient" eiraicTier={4} size={40} />
          <span className="text-sm text-slate-400">
            Tier 4/13 (Spear of Assal — Precise Reasoning) ·{" "}
            <span className="text-amber-400">★ Brown Ajah</span>
          </span>
        </div>
      </div>

      <CiTextbookPanel title={`Question ${questionIndex + 1} of ${SAMPLE_QUESTIONS.length}`} material="parchment">
        <div className="space-y-4">
          <div>
            <span className="text-xs uppercase tracking-wider text-slate-500">Prompt</span>
            <p className="text-lg text-slate-100 mt-1">
              {currentQuestion.prompt}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400">
              {currentQuestion.type.replace("_", " ")}
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400">
              Difficulty {currentQuestion.difficulty}/5
            </span>
          </div>
          {!showAnswer ? (
            <button
              onClick={() => setShowAnswer(true)}
              className="px-4 py-2 rounded-lg bg-amber-700 text-amber-100 hover:bg-amber-600 transition-colors"
            >
              Show Answer
            </button>
          ) : (
            <div className="space-y-3 p-4 rounded-lg bg-slate-900 border border-amber-700">
              <div>
                <span className="text-xs uppercase tracking-wider text-amber-400">Expected Answer</span>
                <p className="text-base text-slate-100 mt-1 font-mono">
                  {currentQuestion.expected_answer}
                </p>
              </div>
              <div>
                <span className="text-xs uppercase tracking-wider text-amber-400">Marking Scheme</span>
                <p className="text-sm text-slate-300 mt-1">
                  {currentQuestion.marking_scheme}
                </p>
              </div>
            </div>
          )}
        </div>
      </CiTextbookPanel>

      <div className="flex justify-between">
        <button
          onClick={() => {
            setQuestionIndex(Math.max(0, questionIndex - 1));
            setShowAnswer(false);
          }}
          disabled={isFirstQuestion}
          className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-50 transition-colors"
        >
          ← Previous
        </button>
        <button
          onClick={() => {
            setQuestionIndex(questionIndex + 1);
            setShowAnswer(false);
          }}
          className="px-4 py-2 rounded-lg bg-emerald-700 text-emerald-100 hover:bg-emerald-600 transition-colors"
        >
          Next →
        </button>
      </div>

      <CiTextbookPanel title="Feedback Channels (4 Brown Ajah members)" material="ink-wash">
        <div className="grid grid-cols-2 gap-2">
          {[
            { name: "Math Tutor", desc: "Concrete + worked-example feedback" },
            { name: "Quest Guide", desc: "4 graduated hint levels" },
            { name: "Curriculum Lookup", desc: "Direct NCCA LO citation" },
            { name: "Research Assistant", desc: "Cross-topic synthesis" },
          ].map((f) => (
            <CiBoonsChoice
              key={f.name}
              prompt={`${f.name}: ${f.desc}`}
              choices={[
                { id: `${f.name}-start`, label: "Start", description: "Begin this feedback channel" },
              ]}
              onChoose={() => {}}
            />
          ))}
        </div>
      </CiTextbookPanel>
    </div>
  );
}