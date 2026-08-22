## Implementation Tasks

- [x] 1. Fill in Purpose for `openspec/specs/americas-california-pipeline/spec.md`. (verification-id: americas-purpose-filled) (verification: inspection — `grep -c TBD openspec/specs/americas-california-pipeline/spec.md` returns 0 in the Purpose section)

- [x] 2. Fill in Purpose for `openspec/specs/celtic-language-pipeline/spec.md`. (verification-id: celtic-purpose-filled) (verification: inspection)

- [x] 3. Fill in Purpose for `openspec/specs/commonwealth-pipeline/spec.md`. (verification-id: commonwealth-purpose-filled) (verification: inspection)

- [x] 4. Fill in Purpose for `openspec/specs/european-nations-ukraine-pipeline/spec.md`. (verification-id: ukraine-purpose-filled) (verification: inspection)

- [x] 5. Fill in Purpose for `openspec/specs/european-union-official-language-pipeline/spec.md`. (verification-id: eu-official-purpose-filled) (verification: inspection)

- [x] 6. Fill in Purpose for `openspec/specs/firecrawl-corpus-and-portals/spec.md`. (verification-id: firecrawl-purpose-filled) (verification: inspection)

- [x] 7. Fill in Purpose for `openspec/specs/duckdb-ducklake-lakehouse-hydration/spec.md`. (verification-id: ducklake-purpose-filled) (verification: inspection)

- [x] 8. Fill in Purpose for `openspec/specs/motherduck-connections/spec.md`. (verification-id: motherduck-purpose-filled) (verification: inspection)

- [x] 9. Fill in Purpose for `openspec/specs/dlt-sync-loop/spec.md`. (verification-id: dlt-sync-purpose-filled) (verification: inspection)

- [x] 10. Fill in Purpose for `openspec/specs/baml-schemas/spec.md`. (verification-id: baml-purpose-filled) (verification: inspection)

- [x] 11. Add the `lint:spec:purpose` task to `mise.toml [tasks]`. Fails CI if any spec has a TBD Purpose. (verification-id: lint-spec-purpose-task) (verification: integration — `mise run lint:spec:purpose` exits 0 after the 10 fills above)

- [x] 12. Add `lint:spec:purpose` to the `depends` array of the `core:lint` task (it's the 6th sub-gate). (verification-id: core-lint-includes-spec-purpose) (verification: inspection — `grep -A 10 'tasks.\"core:lint\"' mise.toml` shows `lint:spec:purpose` in the depends list)

- [x] 13. Add `lint:spec:purpose` to the "Priority mise tasks" section in AGENTS.md. (verification-id: docs-list-spec-purpose) (verification: inspection — AGENTS.md contains `lint:spec:purpose` in the priority list)

## Final Validation

Expected archive gate: `openspec validate 2026-08-23-dev-tooling-tbd-purpose-refresh-batch-data-specs-v1 --archive-gate`

- [x] `openspec validate 2026-08-23-dev-tooling-tbd-purpose-refresh-batch-data-specs-v1 --strict` passes
- [x] All 10 data specs have non-TBD Purpose
- [x] `mise run lint:spec:purpose` exits 0
- [x] `mise run core:lint` exits 0 (includes the new gate)
- [x] The remaining 20 TBD Purpose fields are documented as Phase 5.1.2/5.1.3 follow-up
