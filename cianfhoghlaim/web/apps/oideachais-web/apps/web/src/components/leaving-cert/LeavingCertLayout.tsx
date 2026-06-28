/**
 * Leaving Certificate per-subject page layout.
 *
 * Shared shell for all 7 subject pages. Renders the Hero, 7 content
 * sections (in order), and the CopilotKit chat panel.
 *
 * Route: /leaving-cert/{subject}/
 */

"use client";

import { useParams } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import type {
  LeavingCertSubjectPayload,
  Subject,
} from "../../server/leaving-cert";
import {
  getSubjectName,
  getExamDate,
  getSubjectSchedule,
  getPdfUrl,
} from "../../server/leaving-cert";

// Shared section components (defined inline for now, will be extracted
// to separate files once the design stabilises)
import { Card, Badge, Progress, Skeleton, Separator, Tabs } from "@croilar/ui";

// ── Hero section ──────────────────────────────────────────────────────────

function LeavingCertHero({ subject, examDate, papers }: {
  subject: string;
  examDate: string;
  papers: Array<{ label: string; startTime: string; endTime: string; level: string }>;
}) {
  const [countdown, setCountdown] = useState("");

  useEffect(() => {
    const update = () => {
      const now = Date.now();
      const dates = examDate.split(", ").map((d) => new Date(`${d}T00:00:00+01:00`));
      const nextDate = dates.find((d) => d.getTime() > now) ?? dates[0];
      if (!nextDate) return;
      const diff = nextDate.getTime() - now;
      if (diff <= 0) {
        setCountdown("Exam day — good luck! 🍀");
        return;
      }
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      setCountdown(`${days}d ${hours}h until the exam`);
    };
    update();
    const interval = setInterval(update, 60_000);
    return () => clearInterval(interval);
  }, [examDate]);

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      <h1 className="text-4xl font-bold mb-2">{subject}</h1>
      <p className="text-lg text-muted-foreground mb-4">Leaving Certificate 2026</p>
      <Badge variant="outline" className="text-lg px-4 py-2">
        {countdown}
      </Badge>
      <div className="flex flex-wrap gap-2 justify-center mt-4">
        {papers.map((p) => (
          <Badge key={p.label} variant="secondary">
            {p.label}: {p.startTime}–{p.endTime}
          </Badge>
        ))}
      </div>
    </div>
  );
}

// ── Syllabus analysis section ─────────────────────────────────────────────

function SyllabusAnalysis({ topics, summary }: {
  topics: Array<{ name: string; weightPct: number; learningOutcomes: string[] }>;
  summary: string;
}) {
  return (
    <section className="py-8 px-4 max-w-4xl mx-auto">
      <h2 className="text-2xl font-semibold mb-4">Syllabus Analysis</h2>
      <p className="text-muted-foreground mb-4">{summary}</p>
      <div className="grid gap-3">
        {topics.map((topic) => (
          <Card key={topic.name} className="p-4">
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-medium">{topic.name}</h3>
              <Badge>{topic.weightPct}% of marks</Badge>
            </div>
            <Progress value={topic.weightPct} className="h-2" />
            <ul className="text-sm text-muted-foreground mt-2 space-y-1">
              {topic.learningOutcomes.slice(0, 3).map((lo, i) => (
                <li key={i}>• {lo}</li>
              ))}
            </ul>
          </Card>
        ))}
      </div>
    </section>
  );
}

// ── Section skeletons ─────────────────────────────────────────────────────

function SyllabusSkeleton() {
  return (
    <section className="py-8 px-4 max-w-4xl mx-auto">
      <Skeleton className="h-8 w-48 mb-4" />
      <Skeleton className="h-4 w-full mb-2" />
      <Skeleton className="h-4 w-3/4 mb-4" />
      {[1, 2, 3].map((i) => (
        <Skeleton key={i} className="h-24 w-full mb-3" />
      ))}
    </section>
  );
}

// ── Page shell ────────────────────────────────────────────────────────────

interface LeavingCertLayoutProps {
  subject: Subject;
  payload: LeavingCertSubjectPayload | null;
  isLoading: boolean;
}

export function LeavingCertLayout({ subject, payload, isLoading }: LeavingCertLayoutProps) {
  const name = getSubjectName(subject);
  const examDate = getExamDate(subject);
  const papers = getSubjectSchedule(subject);

  if (isLoading || !payload) {
    return (
      <main className="min-h-screen">
        <LeavingCertHero subject={name} examDate={examDate} papers={papers} />
        <SyllabusSkeleton />
      </main>
    );
  }

  return (
    <main className="min-h-screen">
      {/* Hero */}
      <LeavingCertHero subject={name} examDate={examDate} papers={papers} />

      <Separator />

      {/* Content tabs */}
      <div className="max-w-4xl mx-auto px-4">
        <Tabs defaultValue="syllabus" className="py-6">
          {/* Tab triggers — 8 sections */}
          <div className="flex flex-wrap gap-2 mb-6">
            {[
              "syllabus",
              "past-exams",
              "marking-schemes",
              "prioritisation",
              "exam-tips",
              "chat",
              "pdfs",
            ].map((tab) => (
              <Badge key={tab} variant="outline" className="cursor-pointer">
                {tab.replace(/-/g, " ")}
              </Badge>
            ))}
          </div>

          {/* Syllabus tab */}
          <SyllabusAnalysis
            topics={payload.syllabusTopics}
            summary={payload.syllabusSummary}
          />

          {/* Past exam tab — placeholder; will be a table + Recharts chart */}
          <section className="py-8">
            <h2 className="text-2xl font-semibold mb-4">Past Exam Analysis</h2>
            <p className="text-muted-foreground">
              {payload.pastExamQuestions.length} questions from 2017–2025 across{" "}
              {payload.papers.length} papers. Loading table…
            </p>
          </section>

          {/* Marking schemes tab */}
          <section className="py-8">
            <h2 className="text-2xl font-semibold mb-4">Marking Scheme Patterns</h2>
            <div className="grid gap-3">
              {payload.markingSchemePatterns.map((p) => (
                <Card key={p.patternId} className="p-4">
                  <div className="flex justify-between mb-2">
                    <h3 className="font-medium">{p.topic}</h3>
                    <Badge>{p.frequencyPct}%</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{p.description}</p>
                  <div className="text-xs">
                    <strong>Common mistakes:</strong>{" "}
                    {p.commonMistakes.slice(0, 3).join("; ")}
                  </div>
                </Card>
              ))}
            </div>
          </section>

          {/* Topic prioritisation tab */}
          <section className="py-8">
            <h2 className="text-2xl font-semibold mb-4">Topic Prioritisation</h2>
            <p className="text-muted-foreground mb-4">
              Topics ranked by expected marks per hour of study. Focus on the top 5 for
              maximum return.
            </p>
            <div className="grid gap-3">
              {payload.topicPrioritisations.map((tp) => (
                <Card key={tp.topic} className="p-4">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-medium">{tp.topic}</h3>
                    <Badge
                      variant={
                        tp.difficulty === "low"
                          ? "secondary"
                          : tp.difficulty === "medium"
                            ? "default"
                            : "destructive"
                      }
                    >
                      {tp.marksPerHour.toFixed(1)} marks/hr
                    </Badge>
                  </div>
                  <Progress value={tp.marksPerHour * 10} className="h-2 mb-2" />
                  <p className="text-sm text-muted-foreground">{tp.recommendation}</p>
                </Card>
              ))}
            </div>
          </section>

          {/* Exam layout tips tab */}
          <section className="py-8">
            <h2 className="text-2xl font-semibold mb-4">Exam Layout Tips</h2>
            <div className="grid gap-3">
              {payload.examLayoutTips.map((tip) => (
                <Card key={tip.tipId} className="p-4">
                  <Badge variant="outline" className="mb-2">
                    {tip.category}
                  </Badge>
                  <p className="text-sm">{tip.tip}</p>
                </Card>
              ))}
            </div>
          </section>

          {/* CopilotKit chat tab */}
          <section className="py-8">
            <h2 className="text-2xl font-semibold mb-4">Ask Me Anything</h2>
            <p className="text-muted-foreground mb-4">
              Ask the MiniMax M3 agent about {subject} topics, exam strategy, or
              specific past paper questions. The agent has access to all the analysis
              above.
            </p>
            {/* CopilotKit chat panel — wired in the root layout */}
            <Card className="p-4">
              <p className="text-muted-foreground text-sm text-center">
                Chat panel loads here. (CopilotKit wiring in __root.tsx.)
              </p>
            </Card>
          </section>

          {/* Original PDFs tab */}
          <section className="py-8">
            <h2 className="text-2xl font-semibold mb-4">Original Exam Papers</h2>
            <p className="text-muted-foreground mb-4">
              PDFs hosted in Cloudflare R2 (downloadable). Click to open in a new tab.
            </p>
            <div className="grid gap-2">
              {[2025, 2024, 2023].map((year) =>
                payload.papers.map((p) => (
                  <div key={`${year}-${p.label}`} className="flex items-center gap-4">
                    <span className="text-sm font-medium w-32">{year}</span>
                    <a
                      href={getPdfUrl(
                        subject,
                        "exam-paper",
                        year,
                        p.label.replace(/[()&]/g, "").replace(/\s+/g, "-").toLowerCase(),
                      )}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary hover:underline"
                    >
                      {p.label} (.pdf)
                    </a>
                  </div>
                )),
              )}
            </div>
          </section>
        </Tabs>
      </div>
    </main>
  );
}
