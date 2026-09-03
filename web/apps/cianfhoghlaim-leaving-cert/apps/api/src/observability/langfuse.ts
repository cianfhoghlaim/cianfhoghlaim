// observability/langfuse.ts — Langfuse tracing for the agentic chat extract calls.
//
// Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/ R16.
//
// The "@langfuse/tracing" package provides the @observe decorator that
// wraps a function with a Langfuse trace. Every BAML extract call inside
// the leaving-cert agentic chat SHOULD be observable so the operator can
// inspect token usage + latency + scores in the Langfuse UI.
//
// To enable:
//   bun add @langfuse/tracing
//   cp .env.example .env       # set LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY
//   bun run dev               # Langfuse spans will appear in the UI

import { Langfuse } from "langfuse";
import { observe } from "@langfuse/tracing";

let _client: Langfuse | null = null;
function getClient(): Langfuse | null {
  if (_client) return _client;
  const pk = process.env.LANGFUSE_PUBLIC_KEY ?? "";
  const sk = process.env.LANGFUSE_SECRET_KEY ?? "";
  const host = process.env.LANGFUSE_HOST ?? "https://cloud.langfuse.com";
  if (!pk || !sk) {
    if (process.env.NODE_ENV === "production") {
      console.warn("[langfuse] LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY missing — traces disabled");
    }
    return null;
  }
  _client = new Langfuse({ publicKey: pk, secretKey: sk, baseUrl: host });
  return _client;
}

/**
 * Wrap a sync function with Langfuse observability. Falls back to
 * a passthrough when Langfuse is not configured.
 *
 * Usage:
 *   import { observed } from "./observability/langfuse";
 *   export const generateStudyPlan = observed(
 *     "math_agent.generate_study_plan",
 *     async (weeks: number) => b.WebStudyPlan(subject="mathematics", weeks_until_exam=weeks),
 *   );
 */
export function observed<TArgs extends unknown[], TReturn>(
  name: string,
  fn: (...args: TArgs) => Promise<TReturn>,
): (...args: TArgs) => Promise<TReturn> {
  const client = getClient();
  if (!client) return fn;
  // observe returns a wrapped function that emits a span to Langfuse
  // (name, input, output, latency, usage) every time it runs.
  // The @langfuse/tracing runtime handles this transparently in production.
  return observe(name, fn, { client });
}

/**
 * Hook used by RAGAS eval to push a numeric score into the matching trace.
 * The trace_id is returned from the @observe-wrapped function so the score
 * is correctly correlated.
 */
export async function pushScore(traceId: string, name: string, value: number, comment?: string) {
  const client = getClient();
  if (!client || !traceId) return;
  await client.score({ traceId, name, value, comment });
}
