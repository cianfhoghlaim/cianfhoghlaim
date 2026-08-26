# post-cascade-followups Specification

## Purpose

`post-cascade-followups` is the post-cascade gate that delivers the
3 highest-impact follow-up items from the Wave 8 deferred list:

1. Real Convex schema (replaces the Wave 6 1-table stub)
2. Real AG-UI SSE handler (replaces the Wave 6 hello-event stub)
3. .env.example wire-up (adds the 4 missing env vars)

After this spec is implemented, the 7 deferred items in Wave 8 are
reduced to 4: per-app migrations, Lakekeeper deployment, DuckLake data
migration, Cloudflare Pages deployment.

## Requirements

### Requirement: 7-table Convex schema

`web/packages/db/convex/schema.ts` SHALL define exactly 7 tables:
`users`, `agents`, `threads`, `runs`, `messages`,
`knowledge_graph_nodes`, `subject_caches`.

#### Scenario: All 7 tables present

- **WHEN** `grep -E "defineTable\(" web/packages/db/convex/schema.ts | wc -l` runs
- **THEN** the count is ≥ 7

### Requirement: 4-endpoint AG-UI router

`web/hono-api/src/routes/agui/index.ts` SHALL define a Hono router with
exactly 4 endpoints: `GET /sse`, `POST /run`, `GET /threads`,
`GET /health`.

#### Scenario: All 4 endpoints registered

- **WHEN** `grep -E "\.(get|post)\(" web/hono-api/src/routes/agui/index.ts | wc -l` runs
- **THEN** the count is ≥ 4

### Requirement: 4 new env vars in .env.example

`.env.example` SHALL contain the 4 new env vars at the bottom (in the
"Post-cascade follow-ups" section):
- `CIANFHOGHLAIM_MOTHERDUCK_TOKEN`
- `CONVEX_URL`
- `CIANFHOGHLAIM_RUNTIME_URL`
- `MLFLOW_TRACKING_URI`

#### Scenario: All 4 env vars present

- **WHEN** `grep -E "CIANFHOGHLAIM_MOTHERDUCK_TOKEN|CONVEX_URL|CIANFHOGHLAIM_RUNTIME_URL|MLFLOW_TRACKING_URI" .env.example | wc -l` runs
- **THEN** the count is ≥ 4

### Requirement: AG-UI SSE streams events from Convex

The `GET /agui/sse` endpoint SHALL stream AG-UI events. Each event
follows the `PipelineEvent` schema from `@cianfhoghlaim/contracts`
(event_type + run_id + thread_id + timestamp + payload).

#### Scenario: SSE event format

- **WHEN** `curl -N '${CIANFHOGHLAIM_RUNTIME_URL}/agui/sse?thread_id=test'` runs
- **THEN** the response is `Content-Type: text/event-stream` with a
  `RUN_STARTED` event first, then heartbeat `MESSAGES_SNAPSHOT` events
  every 30 seconds

### Requirement: OTel semantic conventions on AG-UI events

Every AG-UI event SHALL be tagged with the Wave 7 OTel semantic
conventions (via `apply_otel_semantic_conventions` from
`observability/unified_tracer.py`).

#### Scenario: OTel tags on AG-UI events

- **WHEN** an AG-UI event is emitted (heartbeat or message event)
- **THEN** the event's `payload` contains `object_store.system: s3` (per
  the heartbeat convention) or the appropriate `db.system` / `gen_ai.system`
  tags

### Requirement: 12-agent fleet

The `agents` table SHALL support the 12-agent Cianfhoghlaim fleet
per Wave 2 + Wave 3 (6 framework values: ag-ui, adk, crewai, langgraph,
pydantic-ai, mastra, claude-sdk).

#### Scenario: All 7 framework values supported

- **WHEN** the `agents.framework` field is queried
- **THEN** the 7 values listed above are all valid options
