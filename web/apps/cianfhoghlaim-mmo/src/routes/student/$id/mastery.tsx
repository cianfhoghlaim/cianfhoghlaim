import { createFileRoute, useParams } from "@tanstack/react-router";

export const Route = createFileRoute("/student/$id/mastery")({
  component: MasteryDashboardPage,
});

function MasteryDashboardPage() {
  const { id } = useParams({ from: "/student/$id/mastery" });
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Mastery dashboard — student {id}</h1>
      <p className="text-sm text-muted-foreground">
        Cross-subject mastery heat-map across the 8 NCCA subjects.
        FalkorDB-backed visualisation of badge accumulation × subject × level.
      </p>
      <div className="p-6 rounded-lg border bg-card">
        <p className="text-sm text-muted-foreground italic">
          (Mastery heat-map will be populated from FalkorDB query.)
        </p>
      </div>
    </div>
  );
}