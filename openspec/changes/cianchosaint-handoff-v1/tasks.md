# Tasks — `cianchosaint-handoff-v1`

> **Verification rule:** every action below is paired with a REAL verification command. No `[x]` marks until the verification command actually exits 0 AND the output is the expected substring. Per the trust-gap memory `kcg-fabricated-openspec-archive-biep-v3`, archive tasks are NOT marked complete without a working command.

## Phase 0 — Inventory verification (filesystem-proven, 2026-09-12)

These are the verifications that MUST be re-runnable on any clean checkout to claim this change as evidence-based.

- [ ] 1. `du -sh /Users/cianmacandeisigh/dev/cianfhoghlaim /Users/cianmacandeisigh/dev/cianchosaint /Users/cianmacandeisigh/dev/ciancheiltis /Users/cianmacandeisigh/dev/ciandlithe /Users/cianmacandeisigh/dev/gemini_hackathon /Users/cianmacandeisigh/dev/tuatha /Users/cianmacandeisigh/repos/bonneagar` returns: `104G / 1.5G / ~1M / 1.9G / 5.1G / 1.7G / 2.4G` (within ±10%).
- [ ] 2. `find /Users/cianmacandeisigh/dev/cianfhoghlaim/dlt_sources -name "*.py" -not -path "*/__pycache__/*" | wc -l` returns `1994` (±50).
- [ ] 3. `find /Users/cianmacandeisigh/dev/cianchosaint/dlt_sources -name "*.py" -not -path "*/__pycache__/*" | wc -l` returns `246` (±10).
- [ ] 4. `find /Users/cianmacandeisigh/dev/cianfhoghlaim/baml_src -name "*.baml" | wc -l` returns `333` (±10).
- [ ] 5. `find /Users/cianmacandeisigh/dev/cianchosaint/baml_src -name "*.baml" | wc -l` returns `36` (±3).
- [ ] 6. `find /Users/cianmacandeisigh/dev/cianfhoghlaim/cocoindex_flows -name "*.py" -not -path "*/__pycache__/*" | wc -l` returns `120` (±10).
- [ ] 7. `find /Users/cianmacandeisigh/dev/cianfhoghlaim/orchestration/defs -name "*.py" -not -path "*/__pycache__/*" | wc -l` returns `77` (±5).
- [ ] 8. `find /Users/cianmacandeisigh/dev/cianfhoghlaim/orchestration/defs \( -name "*.yaml" -o -name "*.yml" \) | wc -l` returns `213` (±10).
- [ ] 9. `find /Users/cianmacandeisigh/dev/cianfhoghlaim/bonneagar/stacks -mindepth 1 -maxdepth 1 -type d | wc -l` returns `95` (the stack dirs; the top-level files `GOLD_STANDARD.md`/`HEALTH_REPORT.md`/`INDEX.md`/`README.md`/`GOLD_STANDARD.md` are not stacks).
- [ ] 10. `ls /Users/cianmacandeisigh/dev/cianchosaint/bonneagar/stacks | wc -l` returns `15` (±1).
- [ ] 11. `ls /Users/cianmacandeisigh/dev/cianchosaint/web/apps | wc -l` returns `9` (no ciafagent-* may be missing or extra).
- [ ] 12. `ls /Users/cianmacandeisigh/dev/ciandlithe/web/apps | wc -l` returns `7`.
- [ ] 13. `ls /Users/cianmacandeisigh/dev/gemini_hackathon/cocoindex_flows/education` shows exactly `lc6_extraction_app.py` (1 file).
- [ ] 14. `ls /Users/cianmacandeisigh/dev/ciancheiltis/baml_src` fails with `No such file or directory` (verifies ciancheiltis has NO baml_src — deliberately lean).
- [ ] 15. `ls /Users/cianmacandeisigh/dev/ciandlithe/orchestration` returns empty (verifies ciandlithe has NO orchestration — drift #4).
- [ ] 16. `ls /Users/cianmacandeisigh/repos/bonne/.git_disabled` succeeds (verifies bonneagar is intentionally disabled).
- [ ] 17. `git -C /Users/cianmacandeisigh/dev/cianchosaint log -1 --format='%h %ad %s' --date=short` returns `075b1499 2026-08-27 refactor(kcg-rename): rename kcg_subapp_manifest.yaml → cianfhoghlaim_subapp_manifest.yaml` (no commits since 2026-08-27 = cianchosaint is stale).
- [ ] 18. `git -C /Users/cianmacandeisigh/dev/tuatha log -1 --format='%h %ad %s' --date=short` returns a 2026-09-12 commit (verifies tuatha is the most-active sister).
- [ ] 19. `grep -c 'CIANCHOSAINT wholesale-copy' /Users/cianmacandeisigh/dev/cianchosaint/bonneagar/stacks/litellm/config/config.yaml` returns `≥1` (verifies the wholesale-copy header is present).
- [ ] 20. `diff /Users/cianmacandeisigh/dev/cianfhoghlaim/dlt_sources/british_isles/_cross/jurisdiction_pipeline_base.py /Users/cianmacandeisigh/dev/cianchosaint/dlt_sources/_cross/jurisdiction_pipeline_base.py` returns non-empty diff (verifies cianchosaint has sister-local extensions, NOT a byte-identical copy).

## Phase 1 — Sister-repo drift detection (catalogued in proposal §4)

Each drift below has been DETECTED (filesystem-verified) and is documented in `proposal.md` §4. These are NOT in scope for this change but are recorded for follow-up openspec changes.

### Drift 1 — `baml_src/_shared/provider_router.py` missing in cianfhoghlaim

- [ ] 21. `ls /Users/cianmacandeisigh/dev/cianfhoghlaim/baml_src/_shared/provider_router.py` returns `No such file or directory`.
- [ ] 22. `ls /Users/cianmacandeisigh/dev/cianchosaint/baml_src/_shared/provider_router.py` succeeds (cianchosaint has it).
- [ ] 23. Follow-up openspec change: **`2026-09-XX-shared-provider-router-bridge-v1`** (out of scope for this change).

### Drift 2 — `orchestration/defs/__init__.py` missing in cianchosaint

- [ ] 24. `ls /Users/cianmacandeisigh/dev/cianchosaint/orchestration/defs/__init__.py` returns `No such file or directory`.
- [ ] 25. `ls /Users/cianmacandeisigh/dev/cianchosaint/orchestration/defs/licence_enforcement_sensor.py` succeeds (the only file present).
- [ ] 26. Follow-up openspec change: **`2026-09-XX-cianchosaint-orchestration-init-v1`** (out of scope).

### Drift 3 — `import dlt_sources` instead of `import dlt` in 3 cianfhoghlaim files

- [ ] 27. `grep -lE "^import dlt_sources$" /Users/cianmacandeisigh/dev/cianfhoghlaim/orchestration/defs -r | grep -v __pycache__ | wc -l` returns `4` (3 in `eu_multilingual/` + 1 in `root_pdf_assets.py` which uses no `dlt.*`).
- [ ] 28. `grep -lE "^import dlt_sources$" /Users/cianmacandeisigh/dev/cianfhoghlaim/orchestration/defs -r | grep -v __pycache__ | xargs grep -lE "@dlt\.resource\(|dlt\.pipeline\(" | wc -l` returns `3` (the 3 broken files).
- [ ] 29. Already tracked by **`2026-08-24-wave-1-dlt-sources-domain-restructure-v1`** (out of scope for this change).

### Drift 4 — `ciandlithe/orchestration/` is empty

- [ ] 30. `find /Users/cianmacandeisigh/dev/ciandlithe/orchestration -type f | wc -l` returns `0`.
- [ ] 31. `find /Users/cianmacandeisigh/dev/ciandlithe/motherduck -type f | wc -l` returns `0`.
- [ ] 32. `find /Users/cianmacandeisigh/dev/ciandlithe/notebooks -type f | wc -l` returns `0`.
- [ ] 33. Follow-up openspec change: **`2026-09-XX-ciandlithe-orchestration-init-v1`** (out of scope).

### Drift 5 — `gemini_hackathon` uses different layout (NOT a defect)

- [ ] 34. `ls -la /Users/cianmacandeisigh/dev/gemini_hackathon/baml_src` shows `baml_src -> baml_extracts` (symlink).
- [ ] 35. `ls /Users/cianmacandeisigh/dev/gemini_hackathon/dlt_pipelines | wc -l` returns ≥10.
- [ ] 36. `ls /Users/cianmacandeisigh/dev/gemini_hackathon/dlt_sources` returns `No such file or directory` (gemini_hackathon does NOT use `dlt_sources/`).
- [ ] 37. Follow-up openspec change: **`2026-09-XX-gemini-hackathon-sister-umbrella-v1`** (out of scope, codifies the divergent layout).

### Drift 6 — `baml_client/` not in cianfhoghlaim working tree

- [ ] 38. `ls /Users/cianmacandeisigh/dev/cianfhoghlaim/baml_client` returns `No such file or directory` (NOT a defect — `baml-py` generates it on `baml-cli generate`).
- [ ] 39. Trust-gap memory `kcg-runtime-inert-layers` claim #3 (`baml_client/` has no `__init__.py`) is **moot** — the directory is generated, not committed.
- [ ] 40. No follow-up openspec change required.

### Drift 7 — `stedding/` content divergence

- [ ] 41. `du -sh /Users/cianmacandeisigh/dev/cianfhoghlaim/stedding` returns ≥5 GB.
- [ ] 42. `ls /Users/cianmacandeisigh/dev/cianchosaint/stedding` shows `gaffer_graph.json` + `sync-reports/` + `trl-assessments/` only.
- [ ] 43. `stedding/` is local cache, NEVER canonical — do not lift it.

## Phase 2 — OpenSpec spec authoring

### Spec: `openspec/specs/cianfhoghlaim/spec.md` (the canonical surface)

- [ ] 44. Create `openspec/changes/cianchosaint-handoff-v1/specs/cianfhoghlaim/spec.md` with `## ADDED Requirements` block + 4 Requirements (`Canonical-1` BIEP, `Canonical-2` Ciancheiltis, `Canonical-3` Tuatha BI MMO, `Canonical-4` Bonneagar IaC) + ≥1 Scenario per Requirement.
- [ ] 45. Each Requirement uses `SHALL`/`MUST` in the body (the `--strict` validator enforces this).
- [ ] 46. Each Scenario uses `#### Scenario: <name>` (4 hashtags) + `- **WHEN** ... - **THEN** ... - **AND** ...` triple.

### Spec: `openspec/specs/sister-shared/spec.md` (the shared-stack contract)

- [ ] 47. Create `openspec/changes/cianchosaint-handoff-v1/specs/sister-shared/spec.md` with `## ADDED Requirements` block + 5 Requirements (`Shared-1` ProviderRouter, `Shared-2` JurisdictionPipelineBase, `Shared-3` cocoindex_flows/_shared, `Shared-4` openspec workflow, `Shared-5` GOLD_STANDARD stacks) + ≥1 Scenario per Requirement.
- [ ] 48. Same strict-mode rules as above.

### Validation

- [ ] 49. `openspec validate cianchosaint-handoff-v1 --strict` exits 0.
- [ ] 50. `openspec validate --all --strict` still passes (no regression in the other 38 pending changes).

## Phase 3 — Commit + push

- [ ] 51. `git -C /Users/cianmacandeisigh/dev/cianfhoghlaim status --short | grep -E "openspec/changes/cianchosaint-handoff-v1"` returns the 4 expected modified/new paths.
- [ ] 52. `git -C /Users/cianmacandeisigh/dev/cianfhoghlaim add openspec/changes/cianchosaint-handoff-v1/`.
- [ ] 53. `git -C /Users/cianmacandeisigh/dev/cianfhoghlaim commit -m "feat(openspec): record cianchosaint handoff + canonical surface + sister-shared contract"` exits 0.
- [ ] 54. `git -C /Users/cianmacandeisigh/dev/cianfhoghlaim log -1 --format='%h'` returns the new commit hash.
- [ ] 55. `git -C /Users/cianmacandeisigh/dev/cianfhoghlaim push origin openspec/cianchosaint-handoff-v1` exits 0.

## DO NOT (per openspec/AGENTS.md hard rules)

- Do NOT fabricate `[x]` marks without the verification command exiting 0.
- Do NOT edit `openspec/specs/<spec>/spec.md` directly — only the deltas under `openspec/changes/<id>/specs/`.
- Do NOT use "should" or "may" in Requirement bodies — `SHALL`/`MUST` only.
- Do NOT archive this change before `openspec validate --strict` passes.

## Cross-references

- [`proposal.md`](./proposal.md) — the WHY + WHAT + 3-bucket categorization
- [`specs/cianfhoghlaim/spec.md`](./specs/cianfhoghlaim/spec.md) — the canonical surface (4 Requirements)
- [`specs/sister-shared/spec.md`](./specs/sister-shared/spec.md) — the shared-stack contract (5 Requirements)
- [`openspec/AGENTS.md`](../../AGENTS.md) — the cianfhoghlaim openspec convention