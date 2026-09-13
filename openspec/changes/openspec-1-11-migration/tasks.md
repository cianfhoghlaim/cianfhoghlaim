# Tasks: openspec-1-11-migration

> Migrate from openspec 1.4 → 1.11 + adopt corrected OPSX framing +
> `.openspec.yaml` per-change convention.
> In-progress (4/8).

## 1. CLI upgrade + config (done)

- [x] **O1.1** Run `bun add -g @fission-ai/openspec@1.11.0`; verify `openspec --version` reports `1.11.0`
- [x] **O1.2** Create `openspec/config.yaml` with `schema: spec-driven`; verify `openspec doctor` reports `OpenSpec root: ok`

## 2. `.openspec.yaml` convention adoption

- [x] **O2.1** Add `.openspec.yaml` to this change (openspec-1-11-migration); verify `openspec validate openspec-1-11-migration --strict` accepts the file
- [ ] **O2.2** For the remaining 36 pending dated-ID changes, do NOT add `.openspec.yaml` (those are out of scope for this change); instead record in `openspec/plans/2026-09-02-change-batching-and-conversion-map-v1.md` that new changes adopt the convention going forward

## 3. Documentation update

- [ ] **O3.1** Rewrite `.agents/skills/openspec/SKILL.md` for openspec 1.11 with the corrected schema/profile framing, undated-kebab convention, and the verified counts (13 pending / 121 specs / 401 archived — verified post-Phase-3 consolidation)
- [ ] **O3.2** Edit `openspec/AGENTS.md` to remove the OPSX-vs-legacy framing and replace with the single-schema + profile-layer framing, and to update the quoted spec/change counts
- [ ] **O3.3** Verify the new SKILL.md by re-reading post-rewrite
- [ ] **O3.4** Verify the new AGENTS.md by re-reading post-edit

## 4. Verification

- [x] **O4.1** Run `openspec validate openspec-1-11-migration --strict`; verify it passes (verified 2026-09-12)
- [ ] **O4.2** Run `openspec status openspec-1-11-migration`; verify all 4 artifacts report done
- [ ] **O4.3** Re-run the consolidation count sweep — confirm `13 pending / 121 specs / 401 archived` (post-Phase-3 of the 2026-09-13 ops-session)
- [ ] **O4.4** Confirm no `.openspec.yaml` was added to any of the 36 dated-ID archived changes (verify the O2.2 exclusion)

## Verification

```bash
cd ~/dev/cianchosaint-laim 2>/dev/null || cd ~/dev/cianchoshlaim
openspec validate openspec-1-11-migration --strict
openspec doctor
```
