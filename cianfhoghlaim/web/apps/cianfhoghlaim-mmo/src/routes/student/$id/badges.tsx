import { createFileRoute, useParams } from "@tanstack/react-router";

export const Route = createFileRoute("/student/$id/badges")({
  component: BadgeWalletPage,
});

function BadgeWalletPage() {
  const { id } = useParams({ from: "/student/$id/badges" });
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Badge wallet — student {id}</h1>
      <p className="text-sm text-muted-foreground">
        Off-chain SkillTreeBadge records (Convex + FalkorDB + LanceDB) plus
        on-chain Merkle anchors on Base L2.
      </p>
      <div className="p-6 rounded-lg border bg-card">
        <p className="text-sm text-muted-foreground italic">
          (Badge cards will be populated from Convex query.)
        </p>
      </div>
    </div>
  );
}