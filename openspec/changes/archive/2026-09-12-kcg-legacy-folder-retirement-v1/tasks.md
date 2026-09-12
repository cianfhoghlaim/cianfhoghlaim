# Tasks: KCG Legacy Folder Retirement

## Stage 0 — Pre-flight audit (verification of the no-port claim)

- [x] T0.1 — Confirm KCG top-level contains nothing substantive beyond
      the 6 stale stack duplicates + 2 HuggingFace caches + empty
      `notebooks/` + `.DS_Store` (per `proposal.md` audit table)
- [x] T0.2 — Confirm every KCG stack file also exists in
      `cianfhoghlaim/bonneagar/stacks/<name>/` (the canonical home)
- [x] T0.3 — Confirm the canonical KCG `bonneagar/stacks/litellm/config/config.yaml`
      is strictly newer (carries `glm-4.6v-flash` + `deepseek-ocr-2`
      entries that the KCG copy lacks)
- [x] T0.4 — Confirm no openspec changes, scripts, agents, baml_src,
      cocoindex_flows, orchestration, dlt_sources, motherduck, web, or
      packages directories remain in KCG

## Stage 1 — Spec deltas

- [x] T1.1 — Add MODIFIED requirement to
      `openspec/changes/2026-09-12-kcg-legacy-folder-retirement-v1/specs/infrastructure-stacks/spec.md`
      swapping the host path
      `/Users/cianmacandeisigh/dev/kings_college_galway`
      → `/Users/cianmacandeisigh/dev/cianfhoghlaim`
      in the "Identical absolute repository mount" requirement + its
      "Session project paths resolve identically" scenario, plus a new
      "Legacy KCG mount path is retired" scenario
- [x] T1.2 — Add MODIFIED requirement to
      `openspec/changes/2026-09-12-kcg-legacy-folder-retirement-v1/specs/agent-platform-cluster/spec.md`
      swapping the same host path in the "Existing sessions are visible
      through OpenChamber" scenario, plus a new "Legacy KCG session paths
      are not consulted" scenario

## Stage 2 — Validation

- [x] T2.1 — Run `openspec validate 2026-09-12-kcg-legacy-folder-retirement-v1 --strict`
      and confirm exit 0 (output: `Change '2026-09-12-kcg-legacy-folder-retirement-v1' is valid`)

## Stage 3 — Archive

- [x] T3.1 — Run `openspec archive 2026-09-12-kcg-legacy-folder-retirement-v1 --yes`
      so the MODIFIED deltas fold back into
      `openspec/specs/infrastructure-stacks/spec.md` and
      `openspec/specs/agent-platform-cluster/spec.md`
      (output: `Specs updated successfully. Change '...' archived as '...'.`)

## Stage 4 — Single-purpose git commit for the directory deletion

- [x] T4.1 — Confirm the cianfhoghlaim openspec archive commit is in place
      (commit 294c601c archived the spec deltas)
- [x] T4.1a — Confirm the sibling
      `2026-09-12-kcg-port-path-references-v1` archive (commit 8d63898d)
      ports the 12 live-code hardcoded paths so deletion does not
      surface FileNotFoundError at runtime
- [x] T4.2 — `rm -rf /Users/cianmacandeisigh/dev/kings_college_galway/`
      (filesystem op; KCG is outside the cianfhoghlaim git repo so
      this is not a tracked-file removal)
- [x] T4.3 — Verify the directory is gone: `ls /Users/cianmacandeisigh/dev/kings_college_galway`
      returns `No such file or directory` (exit code 1)
- [x] T4.4 — `mise run lint:drift-docs` (run). 9 pre-existing drift
      violations reported, NONE related to KCG retirement (all are
      stale count claims: stacks 89→95, skills 65→167, specs 94→102,
      notebooks 54→65 — all predating the retirement). The retirement
      itself adds no new drift.

## Stage 5 — Push

- [ ] T5.1 — `git push origin openspec/cianchosaint-handoff-v1`
      (or whichever branch the workspace is on)