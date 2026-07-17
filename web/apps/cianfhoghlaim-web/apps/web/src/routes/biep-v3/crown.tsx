/**
 * TanStack Start route: /biep-v3/crown
 * Jersey + Guernsey + IoM cohorts dashboard (360).
 */
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/biep-v3/crown")({
  component: BIEPv3CrownPage,
  loader: async () => {
    return { jurisdictions: ["jersey", "guernsey", "isle_of_man"], expected_cohorts: 360 };
  },
});

function BIEPv3CrownPage() {
  const { jurisdictions, expected_cohorts } = Route.useLoaderData();
  return (
    <main className="biep-v3-crown">
      <h1>🇯🇪🇬🇬🇮🇲 BIEP v3 — Crown Dependencies</h1>
      <p>Expected: {expected_cohorts} cohorts across {jurisdictions.join(" + ")}.</p>
      <ul>
        <li>Jersey: 30 subjects × 4 levels = 120 cohorts</li>
        <li>Guernsey: 30 subjects × 4 levels = 120 cohorts</li>
        <li>Isle of Man: 30 subjects × 4 levels = 120 cohorts</li>
      </ul>
    </main>
  );
}
