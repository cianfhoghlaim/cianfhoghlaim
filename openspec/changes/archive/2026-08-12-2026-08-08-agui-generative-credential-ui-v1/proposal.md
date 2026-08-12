# Change: AG-UI generative credential UI

## Why

The MMO client's per-subject CopilotKit chat panel was literal
placeholder text: "CopilotKit chat panel will appear here." No
`ConvexProvider` or `CopilotKit` provider existed anywhere in the
route tree — `__root.tsx` wrapped every route in neither. The badge
wallet route (`student/$id/badges.tsx`) rendered "(Badge cards will be
populated from Convex query.)" — also static. None of this was
reachable until `2026-08-08-docs-informed-quest-and-credential-
generation-v1` made quest/badge content real; this change is what
actually renders it, generatively, in the places the operator asked
for: "generative UI to visualise the subject specific homework
completion badges or syllabus content."

The NCCA's own commissioned research
(`leaving_certificate/the-potential-of-technology-to-support-online-
certification-and-reporting.pdf`) reviews "Digital Learning Profiles"
(Rethinking Assessment, IB Learner Profile, Mastery Transcript
Consortium, International Big Picture Learning Credential) as the
emerging best-practice format for presenting a learner's verified
credentials — grouped by demonstrated competency, not a flat
chronological list. The badge wallet alone doesn't give that
presentation; this change adds it as a dedicated route.

## What Changes

- `__root.tsx`: wrap the route tree in `ConvexProvider` +
  `ConvexReactClient` and `CopilotKit`, replacing the previous
  no-provider state.
- `realm/$subject.tsx`: real `useQuery(api.questPacks.getBySubject,
  ...)` replacing the hardcoded item-count cards; a real `CopilotChat`
  wired with subject-specific instructions naming the subject's
  specialist agent, replacing the placeholder text;
  `useCopilotAction("renderBadgeCard", ...)` so a badge streams
  inline in the chat the instant the backend issues one — never
  fabricated client-side, only rendering what `issue_badge()` actually
  returned.
- New `components/BadgeCard.tsx` — one shared presentation component
  used by the chat action above, the badge wallet, and the new Digital
  Learning Profile route, so a badge looks identical wherever it
  renders.
- `student/$id/badges.tsx`: real `useQuery(api.badges.listByStudent,
  ...)` replacing the static placeholder.
- New `student/$id/profile.tsx` — "Digital Learning Profile": badges
  grouped by the 7 NCCA senior-cycle key competencies, modelled
  directly on the certification-and-reporting research above.
- Hand-patched `routeTree.gen.ts` to register the new profile route
  (no dev server available in this environment to regenerate it —
  see `.claude/rules/init-dlthub-workspace.md`-adjacent convention of
  documenting manual steps when tooling can't run).

## Dependencies

`Blocked by: 2026-08-08-docs-informed-quest-and-credential-generation-v1`
(nothing real to chat about, or a real badge to render, otherwise).
`Blocked by (soft): 2026-08-08-learn-to-earn-x402-credential-pipeline-v1`
(badge cards should reflect real issuance — the fixed import path —
not the previously-dead trigger; this change's own badge rendering
works regardless, since it queries whatever Convex already has).
`Affected repos: cianfhoghlaim (single repo)`

## Impact

- Capabilities: MODIFIED `cianfhoghlaim-educational-mmo` (the "2D
  TanStack Start game client" requirement's client-side behaviour).
  `agentic-frontend-frameworks`'s existing "Agent UI streaming"
  requirement already covers the generic AG-UI/CopilotKit streaming
  contract concretely — not modified here, since this change is a
  concrete instance of that requirement, not a change to it.
- Code: `web/apps/cianfhoghlaim-mmo/src/routes/__root.tsx`,
  `web/apps/cianfhoghlaim-mmo/src/routes/realm/$subject.tsx`, new
  `web/apps/cianfhoghlaim-mmo/src/components/BadgeCard.tsx`,
  `web/apps/cianfhoghlaim-mmo/src/routes/student/$id/badges.tsx`, new
  `web/apps/cianfhoghlaim-mmo/src/routes/student/$id/profile.tsx`,
  `web/apps/cianfhoghlaim-mmo/src/routeTree.gen.ts`.
