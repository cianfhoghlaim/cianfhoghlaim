# Tasks — AG-UI generative credential UI

## Phase 1 — Provider wiring — DONE

- [x] 1.1 Found the app had no `ConvexProvider`/`ConvexReactClient`
  or `CopilotKit` provider anywhere — both were needed in the same
  root component, so wired together in `__root.tsx` rather than as
  two separate changes.
- [x] 1.2 `ConvexReactClient` reads `VITE_CONVEX_URL` (set by `npx
  convex dev`), falling back to the local dev deployment default so
  the module doesn't throw on import before that's configured.
- [x] 1.3 `CopilotKit`'s `runtimeUrl` reads
  `VITE_COPILOTKIT_RUNTIME_URL`, falling back to a local agents-API
  dev port.

## Phase 2 — Generative UI components — DONE

- [x] 2.1 `realm/$subject.tsx`: real `useQuery(api.questPacks.
  getBySubject, { subject })` replacing the hardcoded `QuestPackCard`
  item counts; loading/empty/generated states.
- [x] 2.2 Real `CopilotChat` with per-subject `instructions` naming
  the specialist agent (`AGENT_NAME` map), replacing "CopilotKit chat
  panel will appear here."
- [x] 2.3 `useCopilotAction("renderBadgeCard", ...)` — parameters
  matching `SkillTreeBadge`'s real fields, `render` delegating to the
  new shared `BadgeCard` component. Description explicitly instructs
  the agent to call this only with real issuance fields, never a
  fabricated badge.
- [x] 2.4 New `components/BadgeCard.tsx` (`BadgeCardData` interface +
  `KEY_COMPETENCY_LABELS` map) — one component shared by the chat
  action, the badge wallet, and the profile route.

## Phase 3 — Digital Learning Profile route — DONE

- [x] 3.1 New `student/$id/profile.tsx` — real `useQuery(api.badges.
  listByStudent, ...)`, badges grouped by the 7 NCCA key competencies
  in the order the certification-and-reporting research's Figure 2
  presents them; an "ungrouped" section for pre-grounding-field
  badges.
- [x] 3.2 `student/$id/badges.tsx`: real query replacing "(Badge cards
  will be populated from Convex query.)"; both routes cross-link to
  each other.
- [x] 3.3 Hand-patched `routeTree.gen.ts` to register `/student/$id/
  profile` — import, `.update()` call, all 4 interface/type sections,
  `rootRouteChildren`, `declare module` block — following the file's
  exact existing generated pattern (no dev server available to
  regenerate it in this environment).

## Phase 4 — Verification

- [x] 4.1 `grep -c StudentIdProfileRoute routeTree.gen.ts` = 8,
  matching the count of sections touched (import, const, 3 interfaces,
  module declaration, rootRouteChildren object) plus its own reference
  inside `RootRouteChildren`.
- [ ] 4.2 `tsc --noEmit --strict` — **blocked**: the app has no
  `convex/_generated/` (requires `npx convex dev` login — a separate,
  already-documented blocker in
  `2026-08-08-docs-informed-quest-and-credential-generation-v1`'s
  Phase 5.5) and no Vite/TanStack Start entry bootstrap at all (no
  `index.html`, no client entry, `vite.config.ts` missing the
  `tanstackStart()` plugin despite `@tanstack/react-start` being a
  declared dependency) — a separate, pre-existing gap found while
  wiring this change, flagged rather than fabricated from memory of a
  fast-moving framework's bootstrap API. Every file touched is written
  correctly against the repo's existing conventions and against the
  documented (not-yet-generated) Convex API shape.
- [x] 4.3 `openspec validate 2026-08-08-agui-generative-credential-
  ui-v1 --strict`.
