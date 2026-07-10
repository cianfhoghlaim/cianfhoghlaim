## REMOVED Requirements

### Requirement: Circular extraction BAML

**Reason**: The circular extraction BAML contract was a legacy oideachais-quadrant concern that has been moved into the British-Isles Education Pipeline (BIEP) spec under `ExtractCircularMeta` (`gov_circulars`).
**Migration**: See `specs/british-isles-education-pipeline/spec.md` Requirement "Circular extraction BAML" for the canonical home.

## ADDED Requirements

### Requirement: baml-cli test gate (deferred)

The system SHALL support `baml-cli test` invocation against the 10+ existing `test` blocks across `cianfhoghlaim/baml/` as a hard CI gate.

#### Scenario: local baml-cli test passes

- **GIVEN** the 10 existing `test XxxTest { ... }` blocks under `cianfhoghlaim/baml/processing/{portfolio_extraction,email,author_archive,...}.baml` plus the new `test ExtractDocSkillTagTest { ... }` block at `cianfhoghlaim/baml/processing/docs_skills_extraction.baml`
- **WHEN** `mise run baml:test` is run locally
- **THEN** every `test` block executes against the BAML-generated `baml_client/` and reports `passed = true`
- **AND** the exit code is `0`

#### Scenario: CI gate unwired — deferred to follow-up

- **GIVEN** a `.github/workflows/baml-test.yaml` is not yet authored
- **WHEN** a PR is opened against `pick-4-biep-v1`
- **THEN** no `baml-cli test` job runs in CI; the test pass is verified only locally
- **AND** wiring the CI gate is tracked as a Phase B6 follow-up under `2026-07-12-baml-cli-test-ci-gate-v1`

### Requirement: Delete legacy shared/baml_src/ duplicates

The system SHALL remove the 4 legacy `.baml` files at `cianfhoghlaim/baml/shared/baml_src/` (clients.baml, clients_llama_swap.baml, generators.baml, leaving_cert_marking_scheme_extraction.baml).

#### Scenario: shared/baml_src/ contains 0 .baml files

- **GIVEN** the 4 deletes in `openspec/changes/2026-07-11-baml-cocoindex-modernization-v1/tasks.md` step 2
- **WHEN** `ls cianfhoghlaim/baml/shared/baml_src/*.baml | wc -l` is run
- **THEN** the count is `0`
- **AND** the canonical post-v4 versions at `cianfhoghlaim/baml/clients.baml`, `clients_llama_swap.baml`, `baml/baml.toml`, and `education/pdfs/leaving_cert_marking_scheme.baml` remain the single source of truth

### Requirement: Delete ireland_legal_extraction.baml duplicate

The system SHALL remove `cianfhoghlaim/baml/processing/ireland_legal_extraction.baml` (621 LOC) and consolidate the 5 legal classes + `CourtLevel` enum into `cianfhoghlaim/baml/education/law/`.

#### Scenario: ireland_legal_extraction.baml absent

- **GIVEN** the delete in step 3 of `tasks.md`
- **WHEN** `ls cianfhoghlaim/baml/processing/ireland_legal_extraction.baml` is run
- **THEN** the shell returns "No such file or directory"
- **AND** the 5 classes (`CourtForm`, `CourtFee`, `CourtRule`, `Judgement`, `PIABPage`) + `CourtLevel` enum are reachable via `cianfhoghlaim/baml/education/law/{shared_legal_enums,courts,court_rules,judgements,piab}.baml`

### Requirement: docs_skills_extraction.baml re-creation

The system SHALL provide a BAML source file at `cianfhoghlaim/baml/processing/docs_skills_extraction.baml` that defines the 2 functions + 2 classes referenced from `cianfhoghlaim/cocoindex/docs_skills_consolidation.py`.

#### Scenario: dangling imports resolve

- **GIVEN** the new file from step 5 of `tasks.md`
- **WHEN** `baml-cli generate` is run after `cocoindex/docs_skills_consolidation.py:247,273,293` calls `_baml().ExtractDocSkillTag(...)` / `_baml().ExtractTriples(...)`
- **THEN** the BAML-generated `baml_client.types.DocSkillTag` + `baml_client.types.Triple` + the async `b.ExtractDocSkillTag` + `b.ExtractTriples` are reachable
- **AND** the call sites no longer raise `AttributeError: module 'baml_client' has no attribute 'ExtractDocSkillTag'`

### Requirement: baml version bump 0.223.0

The system SHALL pin BAML generator version `0.223.0` in `cianfhoghlaim/baml/baml.toml` (project + 2 generator blocks).

#### Scenario: version field matches across the 3 places

- **GIVEN** the bump in step 7 of `tasks.md`
- **WHEN** `grep -E "version" cianfhoghlaim/baml/baml.toml` is run
- **THEN** the 3 occurrences (`[project]` + `[generators.lang_py]` + `[generators.lang_ts]`) all return `"0.223.0"`
- **AND** `mise run baml:generate` runs the `baml-cli 0.223.0` codegen

### Requirement: timeout 60s on all 8 generators

The system SHALL add a `timeout { total_ms 60000 }` block to each of the 8 BAML `generator` declarations in `cianfhoghlaim/baml/clients.baml`.

#### Scenario: 8 timeout blocks present

- **GIVEN** the adds in step 8 of `tasks.md`
- **WHEN** `grep -c "timeout { total_ms 60000 }" cianfhoghlaim/baml/clients.baml` is run
- **THEN** the count is `≥ 8`
- **AND** every `generator default`, `local_vision_{qwen,glm,moondream}`, `gemini_{2_flash,1_5_pro,pro,2_5_flash}` block carries the timeout

#### Scenario: retry_policy Exponential is already present

- **GIVEN** the 8 generators already carry `retry_policy Exponential` (added by T4 of the agent-fleet + observability facade change)
- **WHEN** `grep -c "retry_policy Exponential" cianfhoghlaim/baml/clients.baml` is run
- **THEN** the count is `≥ 8`
- **AND** this change re-verifies the existing state — no rewrite required
