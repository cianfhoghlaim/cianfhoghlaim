// Shared badge-card presentation component.
//
// Used two places:
// - student/$id/badges.tsx (a static grid of earned badges)
// - realm/$subject.tsx's useCopilotAction("renderBadgeCard", ...) (an
//   inline card streamed into the CopilotKit chat the moment a badge
//   is earned)
//
// Per 2026-08-08-agui-generative-credential-ui-v1: keeping this as one
// component, not two near-duplicates, is what makes "the badge card
// that renders in chat" and "the badge card on the student's wallet
// page" the same visual object rather than a UI the student has to
// learn twice.

const KEY_COMPETENCY_LABELS: Record<string, { en: string; ga: string }> = {
  THINKING_AND_SOLVING_PROBLEMS: { en: "Thinking & solving problems", ga: "Smaointeoireacht agus fadhbanna a réiteach" },
  BEING_CREATIVE: { en: "Being creative", ga: "A bheith cruthaitheach" },
  COMMUNICATING: { en: "Communicating", ga: "Cumarsáid" },
  WORKING_WITH_OTHERS: { en: "Working with others", ga: "Obair le daoine eile" },
  PARTICIPATING_IN_SOCIETY: { en: "Participating in society", ga: "Rannpháirteachas sa tsochaí" },
  CULTIVATING_WELLBEING: { en: "Cultivating wellbeing", ga: "Folláine a chothú" },
  MANAGING_LEARNING_AND_SELF: { en: "Managing learning and self", ga: "Foghlaim a bhainistiú agus féinbhainistiú" },
};

// Matches the shape badges.ts's queries return (Convex row, camelCase).
export interface BadgeCardData {
  subject: string;
  level: string;
  competencyCode: string;
  competencyTextEn: string;
  competencyTextGa?: string | null;
  keyCompetencies: string[];
  evidenceType: string;
  evidenceScorePct: number;
  agentIssuer: string;
  dateEarned: number; // epoch ms
  onChainAnchor?: string | null;
}

export function BadgeCard({ badge }: { badge: BadgeCardData }) {
  const earnedDate = new Date(badge.dateEarned).toLocaleDateString("en-IE", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  return (
    <div className="p-4 rounded-lg border bg-card space-y-2">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground">
            {badge.subject} · {badge.level.toUpperCase()} · {badge.competencyCode}
          </p>
          <p className="font-semibold">{badge.competencyTextEn}</p>
          {badge.competencyTextGa && (
            <p className="text-sm text-muted-foreground italic">{badge.competencyTextGa}</p>
          )}
        </div>
        <span className="shrink-0 rounded-full bg-primary/10 text-primary text-xs font-medium px-2 py-1">
          {Math.round(badge.evidenceScorePct)}%
        </span>
      </div>

      {badge.keyCompetencies.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {badge.keyCompetencies.map((kc) => (
            <span
              key={kc}
              className="text-xs rounded bg-muted px-1.5 py-0.5"
              title={KEY_COMPETENCY_LABELS[kc]?.ga}
            >
              {KEY_COMPETENCY_LABELS[kc]?.en ?? kc}
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between text-xs text-muted-foreground pt-1 border-t">
        <span>
          Earned {earnedDate} · {badge.agentIssuer}
        </span>
        <span>{badge.onChainAnchor ? "⛓ anchored" : "pending anchor"}</span>
      </div>
    </div>
  );
}

export { KEY_COMPETENCY_LABELS };
