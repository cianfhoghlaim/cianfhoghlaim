# schema-driven-codegen Specification

## Purpose

Formalize the end-to-end schema-driven auto-generation pipeline
that takes BAML `.baml` files as the source of truth and emits
Convex schemas + CopilotKit actions + AG-UI event types +
TanStack Start routes.

The system is added by the
2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
openspec change (Phase O).

## ADDED Requirements

### Requirement: BAML SHALL be the canonical source of truth

The system SHALL treat BAML `.baml` files (at `baml_src/`) as
the canonical source of truth for all per-subject schemas.
Every other schema (Zod, Convex, CopilotKit actions, AG-UI
event types, TanStack Start routes) SHALL be generated from
BAML via the schema-driven codegen pipeline.

#### Scenario: A new BAML function is added

- **WHEN** a developer adds a new BAML function at
  `baml_src/british_isles/ireland/education/lc_extraction/<subject>.baml`
- **WHEN** the operator runs `mise run codegen:all`
- **THEN** the following are regenerated:
  1. TypeScript types + Zod schemas (`bi-ep.gen.ts`)
  2. Convex table schema
     (`web/apps/oideachais-dashboard/convex/lc/<subject>.ts`)
  3. CopilotKit actions
     (`web/hono-api/src/routes/copilotkit/lc/<subject>.ts`)
  4. AG-UI event types
     (`web/apps/oideachais/src/lib/ag-ui/<subject>.ts`)
  5. TanStack Start routes
     (`web/apps/oideachais/routes/lc/<subject>/{index,$topicId,$examId}.tsx`)

### Requirement: The schema-driven codegen pipeline SHALL be declarative

The pipeline SHALL be 6 scripts under `scripts/schema-codegen/`:

1. `index.ts` — the orchestrator (calls the 5 sub-generators)
2. `baml-to-ts.ts` — wraps `baml-cli generate`
3. `convex-from-zod.ts` — Zod → Convex validator generator
4. `copilotkit-actions.ts` — Zod → CopilotKit action generator
5. `ag-ui-types.ts` — Zod → AG-UI event type generator
6. `per-subject-routes.ts` — Per-subject route generator

The pipeline SHALL be idempotent: running it twice produces
byte-identical output.

#### Scenario: Code generation drift gate

- **WHEN** the operator runs `mise run schema:validate` (the
  existing R30 gate extended in Phase O)
- **THEN** the script MUST regenerate all artifacts in-memory
- **AND** MUST byte-diff against the committed files
- **AND** MUST exit 1 if any drift is detected
