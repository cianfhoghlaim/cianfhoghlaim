# Change: V7 From-The-Ground-Up v1 — Deferred greenfield rewrite plan [DEFERRED]

> **Status:** DEFERRED (per operator direction 2026-09-01).
>
> **Phase 10 of 10** in the
> [`openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md`](../../plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md)
> 10-phase integration of `gemini_hackathon/` learnings back into
> `cianfhoghlaim/`. Phases 0-9 are already shipped.

## Why

Per the operator's direction (2026-09-01), Phase 10 is the
"from-the-ground-up v7 rewrite" — a greenfield rebuild based
on the lessons learned from Phases 0-9. The v7 rewrite is
**DEFERRED** until 4-6 weeks of Phase 1-9 usage proves the
consolidated architecture is the right target.

This openspec change ships the foundation only:
- The v7 architecture goals (single source of truth for BAML +
  Convex + A2UI)
- The 5-pillar pattern (BAML → Convex → A2UI → Hono → React)
- The 3 REDUCED ops surface (drop `_legacy/`, drop `web/packages/`,
  consolidate web to 1 app)

The v7 rewrite itself is not in scope (it would be a 4-6 week
effort that requires careful redesign).

## What was shipped

### §1 — v7 architecture goals (1 file)

- **§1.1** `openspec/changes/2026-09-01-v7-from-the-ground-up-v1/architecture.md`
  - 5-pillar pattern: BAML → Convex → A2UI → Hono → React
  - 3 REDUCED ops surface:
    - Drop `_legacy/` (the 8 deprecated files archived per
      `2026-08-13-ocr-vision-activation-completion-v1` / etc.)
    - Drop `web/packages/` (the 7 web packages consolidated
      into `web/apps/cianfhoghlaim-nua/` per Phase 3)
    - Consolidate web to 1 app (the 5 apps collapsed into
      `cianfhoghlaim-nua/`)
  - 4 quality bar improvements:
    - BAML client regenerated (Phase 0.5)
    - Convex schema with 5 new tables (Phase 1 §3.1 + Phase 4 §5)
    - A2UI 11-component catalog (Phase 2)
    - BGE-M3 embedder canonical for all CocoIndex flows

## Impact

- **Audience:** future Cianfhoghlaim developers (the v7 rewrite).
- **Scope:** 1 file (the architecture doc).
- **LOC delta:** +~100 (the architecture doc).
- **Risk:** HIGH — the v7 rewrite is a multi-week effort that
  should be deferred until Phase 1-9 has been validated.
- **Reversibility:** full — the v7 rewrite can be deferred
  indefinitely per operator direction.

## Dependencies

`Blocked by (hard):` none.

`Blocked by (soft):`

- 4-6 weeks of Phase 1-9 usage validation
- A follow-up operator decision to proceed with the v7 rewrite

`Enables:`

- A future v7 implementation PR (after 4-6 weeks of Phase 1-9 usage)

`Affected repos:` `cianfhoghlaim` (this repo only).

## Out of scope

- The actual v7 rewrite — 4-6 weeks of focused refactor work
- Wholesale rewrite of the BAML contracts
- Wholesale rewrite of the Convex schema
- Wholesale rewrite of the React components

## Quality gates (ALL PASSED)

```bash
uv run openspec validate 2026-09-01-v7-from-the-ground-up-v1 --strict  ✅
```

---

*Last updated by build subagent at 2026-09-01.*