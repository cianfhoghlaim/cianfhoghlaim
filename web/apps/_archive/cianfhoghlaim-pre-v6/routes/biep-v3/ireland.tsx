/**
 * TanStack Start route: /biep-v3/ireland
 * Ireland cohorts dashboard (544 = 384 LC + 108 JC + 16 short courses + 36 CBAs).
 */
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/biep-v3/ireland")({
  component: BIEPv3IrelandPage,
  loader: async () => {
    return { jurisdiction: "ireland", expected_cohorts: 544 };
  },
});

function BIEPv3IrelandPage() {
  const { jurisdiction, expected_cohorts } = Route.useLoaderData();
  return (
    <main className="biep-v3-ireland">
      <h1>🇮🇪 BIEP v3 — Ireland cohorts</h1>
      <p>Expected: {expected_cohorts} cohorts (canonical from the British Isles subject registry).</p>
      <ul>
        <li>Leaving Certificate: 384 (64 subjects × 3 levels × 2 langs)</li>
        <li>Junior Cycle: 108 (18 subjects × 3 years × 2 langs)</li>
        <li>Short courses: 16</li>
        <li>CBAs: 36</li>
      </ul>
    </main>
  );
}
