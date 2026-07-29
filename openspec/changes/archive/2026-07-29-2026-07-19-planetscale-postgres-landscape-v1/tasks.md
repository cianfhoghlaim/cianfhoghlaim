# Tasks — PlanetScale Postgres Landscape v1

> **Scope:** Text/Intelligence only — no code, no IaC, no Python. Validation via `openspec validate --strict`. Komodo entirely deferred (per operator choice).

## Phase 0 — Survey + skeleton (1.5 h)

- [x] `openspec/changes/2026-07-19-planetscale-postgres-landscape-v1/` created
- [x] `proposal.md` written
- [ ] `tasks.md` (this file)
- [ ] `cross-repo-sync.md`
- [ ] `specs/planetscale-postgres-data-strategy/spec.md` (NEW umbrella spec — R1–R8)
- [ ] `specs/infrastructure-stacks/spec.md` (MODIFIED)
- [ ] `specs/agent-platform-cluster/spec.md` (MODIFIED)
- [ ] `specs/agent-observability/spec.md` (MODIFIED)
- [ ] `specs/agent-memory-systems/spec.md` (MODIFIED)
- [ ] `specs/bonneagar-iac-merge/spec.md` (MODIFIED)
- [ ] `specs/bonneagar-komodo-gitops/spec.md` (MODIFIED + deferral note)
- [ ] `specs/dagster-5-layer-component-architecture/spec.md` (MODIFIED)
- [ ] `specs/croilar-data-engineering/spec.md` (MODIFIED)
- [ ] `specs/indexing-and-cognition/spec.md` (MODIFIED)
- [ ] `specs/cianfhoghlaim-cognify-knowledge-graph/spec.md` (MODIFIED)
- [ ] `specs/meaisinfhoghlaim-platform/spec.md` (MODIFIED)
- [ ] `specs/agent-registry/spec.md` (MODIFIED)
- [ ] `specs/agentic-frontend-frameworks/spec.md` (MODIFIED)
- [ ] `specs/cianfhoghlaim-pipeline/spec.md` (MODIFIED)
- [ ] `specs/croilar-portfolio/spec.md` (MODIFIED)
- [ ] `specs/documentation/spec.md` (MODIFIED)
- [ ] `specs/dagger-pipelines/spec.md` (MODIFIED)
- [ ] `openspec/architecture-decisions/0005-planetscale-postgres-centralisation.md` (NEW ADR)
- [ ] `openspec validate 2026-07-19-planetscale-postgres-landscape-v1 --strict` passes

## Phase 1 — Write the umbrella spec (R1–R8)

The new spec at `openspec/specs/planetscale-postgres-data-strategy/spec.md` ships 8 Requirements:

- **R1 — Data Substrate Decision Tree**: pseudocode for `pick_data_substrate(stack)` (PlanetScale PG default → Cloudflare D1 SQLite for serverless read-mostly → local Postgres for exotic extensions)
- **R2 — PlanetScale Postgres as primary substrate**: the canonical target for new + migration candidates
- **R3 — Cloudflare D1 SQLite as secondary substrate**: serverless, read-mostly
- **R4 — Local Postgres as tertiary substrate**: only when extensions outside PlanetScale are needed
- **R5 — PlanetScale MySQL Sunset**: the existing MySQL usage is sunsetted at the end of Phase C
- **R6 — Connection Conventions**: `?sslmode=verify-full`, PgBouncer pool mode for serverless, direct for long-running, Locket-injected secrets
- **R7 — Per-Stack Decision Matrix**: the canonical 28-row table from `proposal.md` § "Per-stack decision matrix"
- **R8 — Out of Scope / Komodo Deferral**: Komodo re-architecture deferred to a separate future change

## Phase 2 — Write 17 MODIFIED spec deltas

Each MODIFIED delta is a single ADDED Requirement titled `### Requirement: PlanetScale Postgres Centralisation (`<spec>`)` + 1–2 Scenarios. The Requirements are intentionally minimal — they just cross-reference the umbrella spec.

### Reusable delta template

```markdown
## ADDED Requirements

### Requirement: PlanetScale Postgres Centralisation

The system SHALL migrate its data substrate to PlanetScale PostgreSQL according to
the canonical decision matrix in `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7.

#### Scenario: Migration is declared in the umbrella spec

- **GIVEN** the operator has read `planetscale-postgres-data-strategy/spec.md`
- **WHEN** they look at this spec's R7 row for the relevant stack
- **THEN** they see the substrate decision + the env var name + the per-stack migration effort
- **AND** they find a `[Phase B]` link indicating the follow-up change that performs the migration
```

### Per-spec notes (Phase 0 — read these before writing)

- **infrastructure-stacks**: the 94-stack catalogue — explicit cross-ref to the umbrella spec's R7 + the ADR. May also need to add 1 new requirement: `### Requirement: PlanetScale MySQL Sunset`
- **agent-platform-cluster**: the 8-stack observability cluster — cross-ref to the umbrella's substrate row for langfuse, mlflow, cognee, etc.
- **agent-observability**: explicit cross-ref for langfuse + mlflow
- **agent-memory-systems**: explicit cross-ref for cognee (pgvector confirmed)
- **bonneagar-iac-merge**: the IaC umbrella — note that the Locket-side `PLANETSCALE_DATABASE_URL` secret pattern becomes the canonical pattern (refers to existing `bonneagar/iac/auth-pocketid.ts`)
- **bonneagar-komodo-gitops**: deferral note — explicitly call out that Komodo + FerretDB is **out-of-scope** per the operator's choice
- **dagster-5-layer-component-architecture**: cross-ref for `DUCKLAKE_POSTGRES_HOST` PlanetScale swap
- **croilar-data-engineering**: cross-ref for the croilar Postgres substrate
- **indexing-and-cognition**: cross-ref for CCC/Cognee (pgvector)
- **cianfhoghlaim-cognify-knowledge-graph**: cross-ref for the cognify PostgreSQL backend
- **meaisinfhoghlaim-platform**: cross-ref for the 10 sub-packages (Cognee + Logfire + etc.)
- **agent-registry**: cross-ref for observability substrate (logfire + langfuse)
- **agentic-frontend-frameworks**: cross-ref for Convex (`POSTGRES_URL`) + the Hono oRPC env-vars
- **cianfhoghlaim-pipeline**: the main 50-req spec — umbrella-level cross-ref for the lakehouse + dagster + dagster orchestration database
- **croilar-portfolio**: cross-ref for the croilar-portfolio + croilar-hono-api stacks
- **documentation**: cross-ref from the frontmatter schema in `docs/`
- **dagger-pipelines**: cross-ref for the 8 callable Dagger functions that depend on stack DBs

## Phase 3 — Write the ADR (1 h)

`openspec/architecture-decisions/0005-planetscale-postgres-centralisation.md` records:

- **Context**: 24+ local-Postgres containers + PlanetScale MySQL legacy
- **Decision**: PlanetScale PG as primary; Cloudflare D1 SQLite as secondary; local Postgres as tertiary; Komodo deferred
- **Status**: Accepted (2026-07-19)
- **Consequences**: ✅ centralised managed DB + backups; ⚠ Komodo stays local; ⚠ 6 Bytebase-managed schemas need migration
- **Alternatives Considered**: self-host Postgres on arm1-oci; Neon/Supabase; keep-everything-local
- **References**: PlanetScale PG extension docs; FerretDB v2 docs; the prior PlanetScale MySQL research doc

## Phase 4 — Validate + commit + push (1 h)

- [ ] `openspec validate 2026-07-19-planetscale-postgres-landscape-v1 --strict` PASSES
- [ ] `git status -uall` reviewed (only the 19 files in this change)
- [ ] `git add openspec/changes/2026-07-19-planetscale-postgres-landscape-v1/` + `openspec/architecture-decisions/`
- [ ] `git commit -m "$(...)"` with the standard openspec change commit message format
- [ ] `git push` (only if user explicitly asks; default is no push)

## Open follow-up changes (NOT in this change)

When this change archives, the operator opens these in sequence:

| Order | Change ID | Description |
|---|---|---|
| 1 | `2026-07-XX-planetscale-postgres-migration-phase-b-v1` | ~18 ⭐-easy stack compose deltas; per-stack DATABASE_URL swap; Locket config update |
| 2 | `2026-07-XX-planetscale-mysql-sunset-v1` | 6 Bytebase-managed schemas migrate from MySQL → PG; drops PlanetScale MySQL |
| 3 | `2026-07-XX-komodo-ferretdb-rebuild-v1` | A *separate* future change for Komodo architecture (out-of-scope here) |

## Cross-repo-sync plan

This change touches a single repo (`cianfhoghlaim` only). The IaC half (Phase B + C) will live on the `bonneagar/` worktree at that time. No `cross-repo-sync.md` branch plan needed now — the analysis change is text-only and is contained in this repo.
