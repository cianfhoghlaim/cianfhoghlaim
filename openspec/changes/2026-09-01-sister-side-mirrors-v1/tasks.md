# Tasks — Sister-Side Mirrors v1

> 4 sections, 9 tasks. All tasks MUST pass before
> `openspec archive 2026-09-01-sister-side-mirrors-v1 --yes`.

## Phase A — OpenSpec scaffolding (5 min)

- [x] **A.1** Author `proposal.md` + `tasks.md` + spec delta
- [x] **A.2** `uv run openspec validate 2026-09-01-sister-side-mirrors-v1 --strict` exits 0

## Phase B — Activate the 6 sister-side umbrella-mirror changes (§1, 6 tasks)

- [x] **B.1** Activate `2026-09-01-bonneagar-sister-umbrella-mirror-v1/`
- [x] **B.2** Activate `2026-09-01-tuatha-sister-umbrella-mirror-v1/`
- [x] **B.3** Activate `2026-09-01-ciancheiltis-sister-umbrella-mirror-v1/`
- [x] **B.4** Activate `2026-09-01-ciandlithe-sister-umbrella-mirror-v1/`
- [x] **B.5** Activate `2026-09-01-cianchosaint-sister-umbrella-mirror-v1/`
- [x] **B.6** Activate `2026-09-01-gemini-hackathon-sister-umbrella-mirror-v1/`

## Phase C — Per-sister customisation summary (§2, 1 task)

- [x] **C.1** Authored the per-sister customisation table in proposal.md §2

## Phase D — Drop the soft-cut feature flags from Phase 5 (§3, 1 task)

- [x] **D.1** Remove the Phase 1 stub fallback paths from
  `agents/adk/subjects/lc/<subject>.py` and
  `orchestration/defs/2_materials/lc_extraction/quest_pack_assets.py`
  (the sister repos now consume the canonical BAML functions)

## Phase E — Spec delta (§4, 1 task)

- [x] **E.1** `openspec/changes/2026-09-01-sister-side-mirrors-v1/specs/infrastructure-stacks/spec.md` (2 ADDED Requirements)

---

*Last updated by build subagent at 2026-09-01.*