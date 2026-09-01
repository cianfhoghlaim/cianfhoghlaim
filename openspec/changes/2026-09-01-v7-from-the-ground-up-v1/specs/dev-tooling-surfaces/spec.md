## ADDED Requirements

### Requirement: v7 architecture MUST consolidate to 5-pillar pattern

The Cianfhoghlaim dev-tooling-surfaces capability MUST target a
greenfield v7 architecture that consolidates the 4 web apps + 7
web packages into a single `web/apps/cianfhoghlaim-nua/` app with
the canonical 5-pillar pattern: BAML → Convex → A2UI → Hono → React.

Per the 2026-09-01-v7-from-the-ground-up-v1 change (Phase 10 of
the cianfhoghlaim-nua v6 era plan, **DEFERRED** per operator
direction 2026-09-01).

#### Scenario: The v7 rewrite proceeds

- **WHEN** 4-6 weeks of Phase 1-9 usage has validated the
  consolidated architecture as the right target
- **THEN** the v7 rewrite may proceed per the 5-pillar pattern
- **AND** the 3 REDUCED ops surface (drop `_legacy/` + drop
  `web/packages/` + consolidate web to 1 app) becomes canonical
