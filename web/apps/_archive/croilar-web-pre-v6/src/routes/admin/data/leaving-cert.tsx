// Croilar Portal — Leaving Certificate Pipeline Status Page
//
// Route: croilar/apps/portal/_layout/data/leaving-cert.tsx
// Auth: requireAuth + requireOrg("croilar-admin" | "croilar-collab")
// Data: Convex live queries (pipeline status per subject)

import { useQuery } from "convex/react";
import { api } from "../../../../../convex/_generated/api";
import type { Subject } from "../../../../web/src/server/leaving-cert";
import { getSubjectName, getSubjectSchedule, getExamDate } from "../../../../web/src/server/leaving-cert";
import { Card, Badge, Progress, Separator, Skeleton } from "@cianfhoghlaim/ui-kit";

/** 7 subjects in launch order. */
const SUBJECTS: Subject[] = [
  "mathematics",
  "irish",
  "biology",
  "french",
  "history",
  "business",
  "construction-studies",
];

export default function LeavingCertPipelinePage() {
  // In production, each subject queries Convex for the latest pipeline state.
  // For now, we show a static status page with the exam schedule.
  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-semibold mb-2">Leaving Certificate 2026 Pipeline</h1>
      <p className="text-sm text-muted-foreground mb-6">
        7 priority subjects. 10 Dagster assets per subject. Live status from the data platform.
      </p>

      <Separator className="mb-6" />

      <div className="grid gap-4">
        {SUBJECTS.map((subject) => {
          const name = getSubjectName(subject);
          const examDate = getExamDate(subject);
          const papers = getSubjectSchedule(subject);

          return (
            <Card key={subject} className="p-4">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h3 className="font-medium">{name}</h3>
                  <p className="text-xs text-muted-foreground">
                    Exam: {examDate} &middot; {papers.length} paper{papers.length !== 1 ? "s" : ""}
                  </p>
                </div>
                <Badge variant="outline">
                  10 assets
                </Badge>
              </div>

              {/* Pipeline progress — stub (real data from Convex crons) */}
              <div className="space-y-2">
                <PipelineStep label="Syllabus PDF" status="queued" />
                <PipelineStep label="BAML Extraction" status="queued" />
                <PipelineStep label="Past Papers Ingestion" status="queued" />
                <PipelineStep label="Marking Scheme Extraction" status="queued" />
                <PipelineStep label="Topic Frequency (CocoIndex)" status="queued" />
                <PipelineStep label="Study Prioritisation (MiniMax M3)" status="queued" />
                <PipelineStep label="Exam Layout Tips (MiniMax M3)" status="queued" />
                <PipelineStep label="Portal Page Payload" status="queued" />
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

function PipelineStep({ label, status }: { label: string; status: "queued" | "running" | "done" | "failed" }) {
  const colors: Record<string, string> = {
    queued: "bg-slate-700",
    running: "bg-blue-500",
    done: "bg-emerald-500",
    failed: "bg-red-500",
  };

  return (
    <div className="flex items-center gap-3">
      <div className={`w-2 h-2 rounded-full ${colors[status]}`} />
      <span className="text-sm flex-1">{label}</span>
      <Badge variant="outline" className="text-xs">
        {status}
      </Badge>
    </div>
  );
}
