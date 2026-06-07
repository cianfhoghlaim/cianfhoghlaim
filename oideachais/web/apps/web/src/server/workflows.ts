/**
 * Durable workflows for the Leaving Certificate resource pipeline.
 *
 * Pattern adapted from tanmaxx-17's @tanstack/workflow-core generateProgram
 * workflow (4-step: fetchHistory → proposeStructure → validate → persist).
 *
 * Each workflow is a typed async generator that produces step-level
 * telemetry (step name, elapsed ms, outcome) so the CopilotKit agent
 * can display progress in the chat UI and the Croilar portal can
 * show pipeline status.
 *
 * No external dependencies beyond what's already in the monorepo.
 */

// ── Types ─────────────────────────────────────────────────────────────────

export type WorkflowStep = {
  name: string;
  description: string;
  status: "pending" | "running" | "done" | "failed";
  elapsedMs?: number;
  error?: string;
  output?: unknown;
};

export type WorkflowResult<T> = {
  steps: WorkflowStep[];
  output: T;
  totalElapsedMs: number;
};

// ── Step runner ───────────────────────────────────────────────────────────

async function runStep(
  steps: WorkflowStep[],
  name: string,
  description: string,
  fn: () => Promise<unknown>,
): Promise<unknown> {
  const start = Date.now();
  steps.push({ name, description, status: "running" });
  try {
    const output = await fn();
    steps[steps.length - 1] = {
      name,
      description,
      status: "done",
      elapsedMs: Date.now() - start,
      output,
    };
    return output;
  } catch (err) {
    steps[steps.length - 1] = {
      name,
      description,
      status: "failed",
      elapsedMs: Date.now() - start,
      error: err instanceof Error ? err.message : String(err),
    };
    throw err;
  }
}

// ── Workflow 1: Generate Subject Analysis ────────────────────────────────

export type GenerateAnalysisInput = {
  subject: string;
  year: number;
  model?: "minimax-m3" | "deepseek-v4-pro";
};

export type GenerateAnalysisOutput = {
  subject: string;
  syllabusSummary: string;
  topicFrequencies: unknown[];
  markingPatterns: unknown[];
  prioritisation: unknown[];
  examTips: unknown[];
};

/**
 * 4-step workflow: fetch syllabus → extract topics → generate analysis → persist.
 *
 * This mirrors the tanmaxx-17 generateProgram workflow pattern:
 *   1. Fetch the NCCA syllabus from R2 (network / I/O)
 *   2. Extract topics and learning outcomes via BAML (LLM call, can fail)
 *   3. Generate analysis via MiniMax M3 (LLM call, most expensive step)
 *   4. Persist the payload to MotherDuck / the portal page cache
 */
export async function generateSubjectAnalysis(
  input: GenerateAnalysisInput,
): Promise<WorkflowResult<GenerateAnalysisOutput>> {
  const steps: WorkflowStep[] = [];
  const start = Date.now();

  // Step 1: Fetch syllabus PDF key from R2
  const r2Key = await runStep(
    steps,
    "fetch_syllabus",
    `Retrieve the NCCA syllabus for ${input.subject} (${input.year}) from Cloudflare R2`,
    async () => {
      // In production, this calls the R2 signed URL endpoint.
      // For now, returns the expected R2 key pattern.
      return `syllabus/${input.subject}/${input.year}-syllabus.pdf`;
    },
  );

  // Step 2: Extract topics via BAML
  const topics = await runStep(
    steps,
    "extract_topics",
    `BAML extraction: parse ${input.subject} syllabus into topics and learning outcomes`,
    async () => {
      // In production, calls the BAML client with the syllabus PDF text.
      // For now, returns seeded topics from the metadata registry.
      const { getSubjectPayload } = await import("./leaving-cert");
      const payload = await getSubjectPayload(input.subject as any);
      return payload.syllabusTopics;
    },
  );

  // Step 3: Generate analysis via MiniMax M3
  const analysis = await runStep(
    steps,
    "generate_analysis",
    `MiniMax M3: generate topic prioritisation and exam layout tips for ${input.subject}`,
    async () => {
      // In production, calls MiniMax M3 via LiteLLM.
      // For now, returns the seeded analysis.
      const { getSubjectPayload } = await import("./leaving-cert");
      const payload = await getSubjectPayload(input.subject as any);
      return {
        topicPrioritisations: payload.topicPrioritisations,
        examLayoutTips: payload.examLayoutTips,
        markingSchemePatterns: payload.markingSchemePatterns,
        pastExamQuestions: payload.pastExamQuestions,
      };
    },
  );

  // Step 4: Persist payload
  await runStep(
    steps,
    "persist_payload",
    `Write the per-subject analysis to the portal page cache (MotherDuck + local DuckDB)`,
    async () => {
      // In production, writes to leaving_cert.{subject}_portal_page_payload in MotherDuck.
      // For now, a no-op (the seeded data is already available).
      return true;
    },
  );

  const totalElapsedMs = Date.now() - start;

  return {
    steps,
    output: {
      subject: input.subject,
      syllabusSummary: `Syllabus analysis for ${input.subject} — pipeline complete (${totalElapsedMs}ms)`,
      topicFrequencies: topics as unknown[],
      markingPatterns: (analysis as any).markingSchemePatterns,
      prioritisation: (analysis as any).topicPrioritisations,
      examTips: (analysis as any).examLayoutTips,
    },
    totalElapsedMs,
  };
}

// ── Workflow 2: Refresh All 7 Subjects ────────────────────────────────────

export type RefreshAllOutput = {
  subjects: string[];
  results: Array<{ subject: string; steps: number; elapsedMs: number }>;
  totalElapsedMs: number;
};

/**
 * Runs generateSubjectAnalysis for all 7 priority subjects in parallel.
 * Used by the `leaving_cert_full` Dagster job and the manual refresh
 * button on the Croilar portal Leaving Cert Pipeline page.
 */
export async function refreshAllSubjects(): Promise<WorkflowResult<RefreshAllOutput>> {
  const subjects = [
    "mathematics",
    "irish",
    "biology",
    "french",
    "history",
    "business",
    "construction-studies",
  ] as const;

  const start = Date.now();
  const steps: WorkflowStep[] = [];

  // Run all 7 in parallel
  const results = await Promise.all(
    subjects.map(async (subject) => {
      try {
        const wf = await generateSubjectAnalysis({ subject, year: 2026 });
        return { subject, steps: wf.steps.length, elapsedMs: wf.totalElapsedMs };
      } catch {
        return { subject, steps: 0, elapsedMs: 0 };
      }
    }),
  );

  const totalElapsedMs = Date.now() - start;
  steps.push({
    name: "refresh_all",
    description: `Generated analysis for ${results.filter((r) => r.steps > 0).length}/${subjects.length} subjects`,
    status: results.every((r) => r.steps > 0) ? "done" : "failed",
    elapsedMs: totalElapsedMs,
  });

  return {
    steps,
    output: {
      subjects: [...subjects],
      results,
      totalElapsedMs,
    },
    totalElapsedMs,
  };
}
