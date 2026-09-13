# Tasks: pipeline-naming-taxonomy

> Canonical data-platform naming law.
> In-progress (1/17). Established by the `pipeline-naming-taxonomy`
> proposal as the umbrella for all rename work.

## 1. Establishing the naming law (in progress)

- [x] **N1.1** Write the proposal + this tasks.md (done)
- [x] **N1.2** Verify `design.md` (cross-references the 2026-08-27 kcg-rename commit sequence)
- [ ] **N1.3** Add `openspec/specs/pipeline-naming-taxonomy/spec.md` with the full 17 Requirements

## 2. Five naming-law Requirements (R1–R5)

- [ ] **N2.1** R1: Canonical BIEP spelling (`biep`, NOT `biiep`/`bie`)
- [ ] **N2.2** R2: `pipeline_name=` template (`<domain>_<source>_pipeline`) — add a `linter` script that fails CI if a string literal violates the template
- [ ] **N2.3** R3: `orchestration/defs/` vs `orchestration/pipelines/` two-tree split — add a `validate-tree-split.sh` script
- [ ] **N2.4** R4: Deprecation-shim expiry policy (dated, not indefinite — add `SHIM_EXPIRY=` env var + a 90-day reminder cron)
- [ ] **N2.5** R5: Sibling-sprawl nesting threshold (max 3 levels deep per cohort) — add `lsp.check-sibling-depth` CI gate

## 3. Apply the law to the 7 high-volume surfaces

- [ ] **N3.1** `dlt_sources/**/` — adopt canonical `pipeline_name=` for every `pipeline.build_pipeline_resource()` (currently 30+ un-normalised literals)
- [ ] **N3.2** `orchestration/defs/` — apply the defs vs pipelines split (currently mixing the two in `defs/`)
- [ ] **N3.3** `cocoindex_flows/` — adopt canonical flow name template
- [ ] **N3.4** `baml_src/` — apply canonical client-name template
- [ ] **N3.5** `agents/adk/` — apply canonical agent-name template (per the `sister-shared` contract)
- [ ] **N3.6** `mise.toml` — apply canonical task-name template
- [ ] **N3.7** `openspec/specs/` — apply canonical spec-name template

## 4. Verification

- [ ] Run `openspec validate pipeline-naming-taxonomy --strict` — pass
- [ ] Run `mise run lint:naming-taxonomy` (the new CI gate) — pass

## Verification

```bash
cd ~/dev/cianchosaint-laim 2>/dev/null || cd ~/dev/cianchoshlaim
openspec validate pipeline-naming-taxonomy --strict
```
