# frontend-tanstack-modernisation Specification

## Purpose

`frontend-tanstack-modernisation` is a capability of the Cianfhoghlaim
platform that codifies the 2026 frontend stack. After this spec is
implemented:

- 5 web packages at root `web/packages/{auth,db,ui-kit,api-client,contracts}/`
- AG-UI SSE handler at `web/hono-api/src/routes/agui/index.ts`
- Convex schema stub at `web/packages/db/convex/schema.ts`
- The 5 consolidated web apps consume from these packages
- The hono-api gateway is the single source of truth for auth + AG-UI

This spec captures Wave 6 of the 2026-08-24 master refactor plan.

## Requirements

### Requirement: 5 web packages

`web/packages/` SHALL contain exactly 5 packages:

- `auth/` — Better Auth 1.7 + Convex integration
- `db/` — Convex reactive backend (`^1.19.0`)
- `ui-kit/` — Radix UI + Tailwind 4
- `api-client/` — TanStack AI + TanStack DB + TanStack Form + CopilotKit v2 + AG-UI
- `contracts/` — shared TS types + Zod schemas (BIEP axis, jurisdiction, pipeline events)

#### Scenario: All 5 packages have package.json + README

- **WHEN** `ls web/packages/*/package.json web/packages/*/README.md` runs
- **THEN** 10 files exist (5 × 2)

### Requirement: AG-UI SSE handler

`web/hono-api/src/routes/agui/index.ts` SHALL define an `aguiRouter`
Hono sub-router that exposes a `GET /agui/sse` endpoint streaming AG-UI
events as Server-Sent Events.

#### Scenario: /agui/sse returns SSE

- **WHEN** `curl -N ${CIANFHOGHLAIM_RUNTIME_URL}/agui/sse` runs
- **THEN** the response is `Content-Type: text/event-stream` with a
  `RUN_STARTED` event followed by a `TEXT_MESSAGE_END` event

### Requirement: Convex schema stub

`web/packages/db/convex/schema.ts` SHALL define a Convex `defineSchema({...})`
call. The stub has 1 placeholder table; the real schema lands in a
Wave 6 follow-up PR.

#### Scenario: Convex schema parses

- **WHEN** `bun run convex:dev` runs
- **THEN** the dev deployment starts without error

### Requirement: Canonical runtime URL

`web/packages/api-client/src/copilotkit.ts` SHALL define a
`CIANFHOGHLAIM_RUNTIME_URL` constant that points to the hono-api
gateway. The default SHALL be `http://localhost:4000` in dev and an
environment-specific URL in prod.

#### Scenario: Default runtime URL

- **WHEN** `createCianfhoghlaimAgent()` runs without env vars
- **THEN** the agent connects to `http://localhost:4000/agui/sse`

### Requirement: 12 AG-UI event types

The `PipelineEventSchema` in `web/packages/contracts/src/index.ts` SHALL
define the 12 AG-UI event types:
- `RUN_STARTED`, `RUN_FINISHED`
- `STEP_STARTED`, `STEP_FINISHED`
- `TEXT_MESSAGE_START`, `TEXT_MESSAGE_CONTENT`, `TEXT_MESSAGE_END`
- `TOOL_CALL_START`, `TOOL_CALL_ARGS`, `TOOL_CALL_END`, `TOOL_CALL_RESULT`
- `STATE_DELTA`, `MESSAGES_SNAPSHOT`

#### Scenario: All 12 event types validate

- **WHEN** `PipelineEventSchema.parse({event_type: <each>, run_id: "x", thread_id: "y", timestamp: ...})` runs for each event type
- **THEN** each parse succeeds

### Requirement: 8 pipeline kinds + 15 destinations

The `SourceKindSchema` and `DestinationSchema` in
`web/packages/contracts/src/index.ts` SHALL enumerate the 8 pipeline
kinds (from Wave 2) + the 15 destinations (from Wave 4).

#### Scenario: All kinds + destinations validate

- **WHEN** `SourceKindSchema.parse("exam_papers")` + `DestinationSchema.parse("ducklake_cianfhoghlaim")` run
- **THEN** both parse successfully

### Requirement: 5 web apps consume from the 5 packages

The 5 consolidated web apps (`cianfhoghlaim`, `oideachais`, `croilar`,
`tuatha`, `game_showcase`) SHALL consume from the 5 packages instead
of installing their own copies of Better Auth, Convex, CopilotKit, AG-UI,
Radix UI, Tailwind 4, etc.

#### Scenario: Single install per dep

- **WHEN** `grep -c '"better-auth":' web/apps/*/package.json web/packages/auth/package.json` runs
- **THEN** exactly 1 entry (the canonical `web/packages/auth/`)
