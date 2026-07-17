# Tasks: 2026-07-11-global-region-source-contract-v1

## 1. Create the umbrella spec

- [ ] 1.1 Create `openspec/specs/cross-region-pipeline/spec.md`
- [ ] 1.2 Add the 6 regions + their jurisdiction code policies
  (`british_isles | european_union | european_nations | commonwealth
   | americas | global_official`)
- [ ] 1.3 Add the canonical DLT path contract Requirement (1
  Requirement + 2 Scenarios)
- [ ] 1.4 Add the canonical `source_id` shape Requirement (1
  Requirement + 2 Scenarios)
- [ ] 1.5 Add the canonical partition contract Requirement (1
  Requirement + 2 Scenarios)
- [ ] 1.6 Add the canonical DuckLake namespace shape Requirement (1
  Requirement + 1 Scenario)
- [ ] 1.7 Add the cross-nation BAML classifier Requirement (1
  Requirement + 1 Scenario)

## 2. Spec deltas

- [ ] 2.1 Add a MODIFIED delta on `cianfhoghlaim-pipeline/spec.md`
  introducing the cross-region path contract (an ADDED Requirement)
- [ ] 2.2 Add a MODIFIED delta on
  `british-isles-education-pipeline/spec.md` introducing the
  cross-reference (an ADDED Requirement pointing at the new umbrella
  spec)
- [ ] 2.3 Both deltas reference the new umbrella spec in the
  `## Cross-references` section

## 3. Hard-rule invariants (the grep gate)

- [ ] 3.1 Add a new CI gate script at
  `scripts/check_cross_region_contract.sh` that runs the 4 grep
  invariants listed in the proposal §3
- [ ] 3.2 The script exits 0 on a clean tree + 1 on any violation
- [ ] 3.3 The script is wired into `mise run lint:skills` so a
  violation fails the CI gate

## 4. Cross-link the new spec from existing skills + READMEs

- [ ] 4.1 Update `openspec/AGENTS.md` Priority specs table to include
  `cross-region-pipeline`
- [ ] 4.2 Update `AGENTS.md` (root) Priority openspec specs table to
  include `cross-region-pipeline`
- [ ] 4.3 Cross-reference `.agents/skills/dlt/SKILL.md` (add a
  "Cross-region source contract" section linking to the new spec)
- [ ] 4.4 Cross-reference `.agents/skills/cocoindex/SKILL.md` (add
  the new umbrella spec to the cross-references)

## 5. Validate

- [ ] 5.1 `openspec validate 2026-07-11-global-region-source-contract-v1 --strict` passes
- [ ] 5.2 `dg list specs` lists `cross-region-pipeline`
- [ ] 5.3 The grep-gate script `scripts/check_cross_region_contract.sh` exits 0 on the current tree (the
  existing British Isles contract is forward-compatible — no rename
  required)
- [ ] 5.4 `mise run lint:skills` still passes

## 6. Commit + push

- [ ] 6.1 Single commit with message
  `feat(cross-region): lock the canonical path + source_id + partition contract (Phase 0)`
- [ ] 6.2 `git push origin main`
