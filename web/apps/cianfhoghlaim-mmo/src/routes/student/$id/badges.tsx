import { createFileRoute, useParams } from "@tanstack/react-router";
import { useQuery } from "convex/react";
import { api } from "../../../../convex/_generated/api";
import { BadgeCard, type BadgeCardData } from "../../../components/BadgeCard";

export const Route = createFileRoute("/student/$id/badges")({
  component: BadgeWalletPage,
});

function BadgeWalletPage() {
  const { id } = useParams({ from: "/student/$id/badges" });
  // Real query, replacing the "(Badge cards will be populated from
  // Convex query.)" placeholder — per
  // 2026-08-08-docs-informed-quest-and-credential-generation-v1.
  const badges = useQuery(api.badges.listByStudent, { studentId: id }) as
    | BadgeCardData[]
    | undefined;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Badge wallet — student {id}</h1>
      <p className="text-sm text-muted-foreground">
        Off-chain SkillTreeBadge records (Convex + FalkorDB + LanceDB) plus
        on-chain Merkle anchors on Base L2.
      </p>

      {badges === undefined ? (
        <p className="text-sm text-muted-foreground">Loading badges…</p>
      ) : badges.length === 0 ? (
        <div className="p-6 rounded-lg border bg-card">
          <p className="text-sm text-muted-foreground italic">
            No badges earned yet — complete a formative item in any subject
            realm to earn your first one.
          </p>
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {badges.map((badge, i) => (
            <BadgeCard key={i} badge={badge} />
          ))}
        </div>
      )}
    </div>
  );
}
