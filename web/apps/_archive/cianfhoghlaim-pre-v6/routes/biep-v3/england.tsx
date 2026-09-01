/**
 * TanStack Start route: /biep-v3/england
 * England cohorts dashboard (276 = 3 boards × 92 subjects).
 */
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/biep-v3/england")({
  component: BIEPv3EnglandPage,
  loader: async () => {
    return { jurisdiction: "england", expected_cohorts: 276 };
  },
});

function BIEPv3EnglandPage() {
  const { jurisdiction, expected_cohorts } = Route.useLoaderData();
  return (
    <main className="biep-v3-england">
      <h1>🏴󠁧󠁢󠁥󠁮󠁧󠁿 BIEP v3 — England cohorts</h1>
      <p>Expected: {expected_cohorts} cohorts across AQA + OCR + Edexcel (43 GCSE + 49 A-Level × 3 boards).</p>
    </main>
  );
}
