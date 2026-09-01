// "Digital Learning Profile" — a competency-mapped badge portfolio.
//
// New route per 2026-08-08-agui-generative-credential-ui-v1, modelled
// directly on the NCCA's own commissioned research into online
// certification and reporting
// (leaving_certificate/the-potential-of-technology-to-support-online-
// certification-and-reporting.pdf, H2 Learning for NCCA, Aug 2024),
// which reviews "Digital Learning Profiles" (Rethinking Assessment,
// IB Learner Profile, Mastery Transcript Consortium, International Big
// Picture Learning Credential) as the emerging best-practice format for
// presenting a student's credentials — grouped by demonstrated
// competency, not just a flat chronological achievement list. This
// route is that: badges grouped by the 7 NCCA senior-cycle key
// competencies (Figure 2 of the same source PDF), distinct from
// student/$id/badges.tsx's plain chronological wallet view.

import { createFileRoute, useParams, Link } from "@tanstack/react-router";
import { useQuery } from "convex/react";
import { api } from "../../../../convex/_generated/api";
import { BadgeCard, KEY_COMPETENCY_LABELS, type BadgeCardData } from "../../../components/BadgeCard";

export const Route = createFileRoute("/student/$id/profile")({
  component: DigitalLearningProfilePage,
});

// The 7 NCCA senior-cycle key competencies, in the order Figure 2 of
// the certification-and-reporting PDF presents them (bounded by
// literacies + numeracy, which this profile doesn't render as its own
// group since no badge is issued solely for them).
const KEY_COMPETENCY_ORDER = [
  "THINKING_AND_SOLVING_PROBLEMS",
  "BEING_CREATIVE",
  "COMMUNICATING",
  "WORKING_WITH_OTHERS",
  "PARTICIPATING_IN_SOCIETY",
  "CULTIVATING_WELLBEING",
  "MANAGING_LEARNING_AND_SELF",
] as const;

function DigitalLearningProfilePage() {
  const { id } = useParams({ from: "/student/$id/profile" });
  const badges = useQuery(api.badges.listByStudent, { studentId: id }) as
    | BadgeCardData[]
    | undefined;

  const bySubjectCount = new Map<string, number>();
  for (const badge of badges ?? []) {
    bySubjectCount.set(badge.subject, (bySubjectCount.get(badge.subject) ?? 0) + 1);
  }

  return (
    <div className="space-y-8">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold">Digital Learning Profile — student {id}</h1>
        <p className="text-sm text-muted-foreground">
          Badges grouped by NCCA key competency, per the online
          certification &amp; reporting research the credential design is
          grounded in. See also the{" "}
          <Link
            to="/student/$id/badges"
            params={{ id }}
            className="underline underline-offset-2"
          >
            chronological badge wallet
          </Link>
          .
        </p>
      </header>

      {badges === undefined ? (
        <p className="text-sm text-muted-foreground">Loading profile…</p>
      ) : badges.length === 0 ? (
        <div className="p-6 rounded-lg border bg-card">
          <p className="text-sm text-muted-foreground italic">
            No badges earned yet — nothing to group into a profile.
          </p>
        </div>
      ) : (
        <>
          <section className="flex flex-wrap gap-2">
            {[...bySubjectCount.entries()].map(([subject, count]) => (
              <span key={subject} className="text-xs rounded-full bg-muted px-3 py-1">
                {subject}: {count}
              </span>
            ))}
          </section>

          <div className="space-y-6">
            {KEY_COMPETENCY_ORDER.map((kc) => {
              const matches = badges.filter((b) => b.keyCompetencies?.includes(kc));
              if (matches.length === 0) return null;
              return (
                <section key={kc} className="space-y-3">
                  <h2 className="text-lg font-semibold">
                    {KEY_COMPETENCY_LABELS[kc]?.en ?? kc}
                    <span className="ml-2 text-sm text-muted-foreground italic font-normal">
                      {KEY_COMPETENCY_LABELS[kc]?.ga}
                    </span>
                  </h2>
                  <div className="grid gap-3 sm:grid-cols-2">
                    {matches.map((badge, i) => (
                      <BadgeCard key={i} badge={badge} />
                    ))}
                  </div>
                </section>
              );
            })}

            {(() => {
              const ungrouped = badges.filter((b) => !b.keyCompetencies?.length);
              if (ungrouped.length === 0) return null;
              return (
                <section className="space-y-3">
                  <h2 className="text-lg font-semibold text-muted-foreground">
                    Not yet mapped to a key competency
                  </h2>
                  <p className="text-xs text-muted-foreground">
                    Badges issued before key-competency grounding was added
                    to the schema.
                  </p>
                  <div className="grid gap-3 sm:grid-cols-2">
                    {ungrouped.map((badge, i) => (
                      <BadgeCard key={i} badge={badge} />
                    ))}
                  </div>
                </section>
              );
            })()}
          </div>
        </>
      )}
    </div>
  );
}
