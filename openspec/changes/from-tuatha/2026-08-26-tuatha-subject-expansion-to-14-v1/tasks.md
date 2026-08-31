# Tasks — Tuatha Subject Expansion 8 → 14 v1

## Phase A — Subject + tool + BAML + routing expansion (parallel)

### A.1 — DLT stubs (30 NEW files)

- [x] T1.1: Commit the 30 untracked DLT stubs for
  `{accounting,biology,business,french,irish,physics}` ×
  `{syllabus,past_paper,marking_scheme,formative_item,response_score}`
  (commit `14fbe16`)

### A.2 — Subject agents (6 NEW files)

- [x] T2.1: Author `tuatha/subjects/{accounting,biology,business,french,irish,physics}.py`
  (each is a 1:1 mirror of `tuatha/subjects/applied_mathematics.py`)

### A.3 — Per-subject tools (30 NEW files)

- [x] T3.1: Author `tuatha/tools/<subject>_<tool>.py` for the 6 new subjects
  (each tool wraps the corresponding BAML function per the
  `qpack_<subject>.baml` contract)

### A.4 — BAML contracts (6 NEW files)

- [x] T4.1: Author `tuatha/baml/qpack_{accounting,biology,business,french,irish,physics}.baml`
  (each is a 1:1 mirror of `qpack_applied_mathematics.baml`)

### A.5 — routing.py extension (1 MODIFIED file)

- [x] T5.1: Add 6 new `SUBJECT_WIRING_REGISTRY` entries to
  `tuatha/routing.py`
- [x] T5.2: Add 6 new `ROUTING_KEYWORDS` buckets to
  `tuatha/routing.py`

### A.2-A.5 mega-commit (commit `8864b87`)

- [x] All 6 subject agents + 30 tools + 6 BAML + routing.py
  bundled into 1 atomic commit

## Phase A — PixiJS realm routes + sprite banks (parallel)

### A.6 — PixiJS realm routes (6 NEW + 2 MODIFIED files)

- [x] T6.1: Author the 6 new `routes/realm/<subject>.tsx` files
- [x] T6.2: Extend `tuatha/web/apps/tuatha-ui/src/router.tsx`
- [x] T6.3: Extend `tuatha/web/packages/realm-canvas/src/types.ts`

### A.7 — Sprite banks (6 NEW files)

- [x] T7.1: Author the 6 new `realm-canvas/src/subjects/<subject>.ts`
  files (one per new subject; bilingual title + tagline +
  7-colour palette + sprite bank + tiltRadians per the
  realm-canvas spec)

### A.6 commit (commit `a1ac9c6`)
### A.7 commit (commit `96956e6`)

## Phase B — OpenSpec specs (parallel)

### B.1 — Populate openspec/specs/ (4 NEW files)

- [x] T8.1: Copy `cianfhoghlaim-educational-mmo/spec.md` from the
  canonical main repo
- [x] T8.2: Copy `celtic-asset-generation/spec.md` from main repo
- [x] T8.3: Copy `learn-to-earn-token-credential/spec.md` from main repo
- [x] T8.4: Author `tuatha-british-isles-mmo/spec.md` (the standalone
  British Isles MMO spec)

### B.2 — Author the change (this commit)

- [x] T9.1: Author `proposal.md` + `tasks.md`
- [x] T9.2: Author `specs/cianfhoghlaim-educational-mmo/spec.md` delta
  (extend the 8-subject requirement to 14)
- [x] T9.3: Author `specs/tuatha-british-isles-mmo/spec.md` delta
  (the new standalone spec)

### B.1 commit (commit `c002bff`)

## Phase C — Sources + subapp_manifest (parallel)

### C.1 — sources/ commit

- [ ] T10.1: Commit `sources/ireland_fetcher.py` + `sources/duckdb/`
  (the rung-1 fetcher)

### C.2 — subapp_manifest commit

- [ ] T11.1: Commit `subapp_manifest.yaml` (the TIER 3 subapp
  declaration)

## Phase D — Quality gates

- [ ] G1: `openspec validate 2026-08-26-tuatha-subject-expansion-to-14-v1 --strict` PASS
- [ ] G2: `openspec archive 2026-08-26-tuatha-subject-expansion-to-14-v1 --yes` after deploy

## Final

- [ ] Final: push to `origin main`
