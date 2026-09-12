## 1. CLI upgrade + config

- [x] 1.1 Run `bun add -g @fission-ai/openspec@1.11.0`; verify `openspec --version` reports `1.11.0`
- [x] 1.2 Create `openspec/config.yaml` with `schema: spec-driven`; verify `openspec doctor` reports `OpenSpec root: ok`

## 2. `.openspec.yaml` convention adoption

- [x] 2.1 Add `.openspec.yaml` to this change (openspec-1-11-migration); verify `openspec validate openspec-1-11-migration --strict` accepts the file
- [ ] 2.2 For the remaining 36 pending dated-ID changes, do NOT add `.openspec.yaml` (those are out of scope for this change); instead record in `openspec/plans/2026-09-02-change-batching-and-conversion-map-v1.md` that new changes adopt the convention going forward

## 3. Documentation update

- [ ] 3.1 Rewrite `.agents/skills/openspec/SKILL.md` for openspec 1.11 with the corrected schema/profile framing, undated-kebab convention, and the verified counts (36 pending / 102 specs / 344 archived) — do not re-archive/cite 78/97/96; verify by re-reading the file post-rewrite
- [ ] 3.2 Edit `openspec/AGENTS.md` to remove the OPSX-vs-legacy framing and replace with the single-schema + profile-layer framing, and to update the quoted spec/change counts; verify by re-reading the file post-edit

## 4. Verification

- [x] 4.1 Run `openspec validate openspec-1-11-migration --strict`; verify it passes (verified 2026-09-12)
- [ ] 4.2 Run `openspec status openspec-1-11-migration`; verify all 4 artifacts report done