# 2026-07-27-biep-v3-canonical-registry-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify Phase 0 (root-namespace-rename) merged
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — BAML schema

- [ ] Create `baml_src/british_isles/_cross/biep_subject.baml` with:
  - 8 canonical enums (Jurisdiction, EducationalStage, AwardingBody,
    QualificationLevel, Language, CrossJurisdictionConcept,
    RegistrySource, RegistryStatus)
  - `SubjectSlug`, `SubjectRegistryRow`, `JurisdictionOverride`,
    `CrossJurisdictionBridge` classes
  - 2 query functions: `QueryRegistryByJurisdiction`,
    `QueryRegistryByConcept`
- [ ] Run `cd baml_src && uv run baml-cli generate`

## Stage 2 — DuckDB migration

- [ ] Create `dlt/common/migrations/2026-07-27-cianfhoghlaim-subject-registry.sql`
  with 3 tables + 12 seeded cross-jurisdiction bridges + 2 auto-update
  triggers
- [ ] Test: `python3 -c "from dlt.british_isles._cross.registry_loader import apply_migration; apply_migration()"`
  (assumes the lakehouse stack is running)

## Stage 3 — Python API

- [ ] Create `dlt/british_isles/_cross/__init__.py`
- [ ] Create `dlt/british_isles/_cross/registry_api.py` with:
  - 5 type aliases (Jurisdiction, EducationalStage, AwardingBody,
    QualificationLevel, Language)
  - `SubjectRegistryRow` dataclass
  - 4 query functions (all ibis-first)
  - 1 insert function
- [ ] Create `dlt/british_isles/_cross/registry_loader.py` with:
  - `load_ireland_subjects()` (minimal 4-row seed for Phase 1)
  - `load_england_subjects()` (minimal 4-row seed for Phase 1)
  - `seed_registry()` (calls loaders + inserts)
  - `apply_migration()` (runs the SQL migration)

## Stage 4 — 4-tab companion notebook

- [ ] Create `notebooks/18_cianfhoghlaim_subject_registry.py` with 4 tabs:
  - Tab 1 (Format doc): BAML schema + DuckDB table descriptions + canonical
    namespace shape
  - Tab 2 (Nation comparison): ibis query → subject count by jurisdiction
  - Tab 3 (Bridge explorer): concept multiselect → all registry rows matching
  - Tab 4 (Drift detector): static status table + drift-detection invocation
- [ ] Verify: `marimo edit notebooks/18_cianfhoghlaim_subject_registry.py`
  opens + all 4 tabs render

## Stage 5 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-07-27-biep-v3-canonical-registry-v1/specs/cross-region-pipeline/spec.md`
  with the new registry requirement
- [ ] Run `openspec validate 2026-07-27-biep-v3-canonical-registry-v1 --strict`
- [ ] Commit the change on a dedicated branch
- [ ] Open a PR on `origin/main` referencing this change
- [ ] Run `mise run lint:skills` — must remain 53/53
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-07-27-biep-v3-canonical-registry-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Update `docs/cianfhoghlaim-registry.md` with the migration notes
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol