import { createFileRoute, useParams } from "@tanstack/react-router";

export const Route = createFileRoute("/anchor/$date")({
  component: AnchorVerificationPage,
});

function AnchorVerificationPage() {
  const { date } = useParams({ from: "/anchor/$date" });
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">
        Merkle anchor verification — {date}
      </h1>
      <p className="text-sm text-muted-foreground">
        Verifies the daily Merkle root of SkillTreeBadge records published
        to Base L2 on {date}. Any third party (employer, university) can
        verify a badge by entering its <code>id</code> + <code>evidence_hash</code>.
      </p>
      <div className="p-6 rounded-lg border bg-card">
        <p className="text-sm text-muted-foreground italic">
          (Merkle root + Base L2 tx_hash will be loaded from the daily
          credential anchor Dagster asset.)
        </p>
      </div>
    </div>
  );
}