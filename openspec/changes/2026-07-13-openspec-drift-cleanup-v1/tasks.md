# Tasks — Openspec drift cleanup v1

## 1. Capture baseline (15 min)

- [x] Run `grep -rn "sruth\.[a-z]" openspec/specs/ --include='*.md'` to capture
  pre-rename count (67).
- [x] Run `grep -rE "from oideachais\.|oideachais\.[a-z]+" openspec/specs/ --include='*.md'`
  to capture bare-oideachais count (142).
- [x] Run per-spec breakdown: `oideachais-pipeline` (29 sruth, 60 bare),
  `meaisinfhoghlaim-platform` (24, 21), `croilar-data-engineering` (10, 3),
  `oideachais-leabharlann` (2, 2), `indexing-and-cognition` (2, 3).

## 2. Apply `sruth.<quadrant>.` → `<quadrant>.` rename (45 min)

- [x] Run `sed -i '' 's|sruth\.oideachais\.|oideachais.|g'` across all
  `openspec/specs/*.md`.
- [x] Run `sed -i '' 's|sruth\.meaisinfhoghlaim\.|meaisinfhoghlaim.|g'`
  across all `openspec/specs/*.md`.
- [x] Run `sed -i '' 's|sruth\.croilar\.|croilar.|g'` across all
  `openspec/specs/*.md`.
- [x] Run `sed -i '' 's|sruth\.tuatha\.|tuatha.|g'` across all
  `openspec/specs/*.md` (no matches; pre-emptive).
- [x] Verify post-rename: `sruth.*` count 67 → 6 (91% reduction).
- [x] Verify the 6 remaining are: 4 `sruth.oideachas` typo refs in
  `meaisinfhoghlaim-platform` (negative-test) + 1 `sruth.oideachais` bare-import
  ref in `croilar-data-engineering` (historical packaging-fix context) + 1
  `from sruth.*` broad-regex ref in `oideachais-pipeline` line 1533.
- [x] Hand-fix line 1535 of `oideachais-pipeline/spec.md` to remove the
  duplicate `oideachais.*` listing created by the v4-rename collapse.

## 3. Apply stale-subpath renames (30 min)

- [x] `oideachais.dlt_sources.X` → `oideachais.dlt.X` (7 refs) per v4
  layout where `dlt_sources/` was renamed to `dlt/` with subdirs
  `british_isles/`, `language/`, `filesystem/`, etc.
- [x] `oideachais.dagster_defs.X` → `oideachais.orchestration.defs.X` (9 refs)
  per v4 layout where `dagster_defs/` was renamed to `orchestration/defs/`.
- [x] `oideachais.dagster_assets` → `oideachais.orchestration.defs.assets` (1 ref).
- [x] Hand-fix `meaisinfhoghlaim-platform/spec.md:111` (the lone
  `\`oideachais.dagster_defs\`` reference that wasn't caught by sed).

## 4. Verify renames + validate (15 min)

- [x] Run `grep -rn "sruth\.[a-z]" openspec/specs/ --include='*.md'` —
  count = 6 (target: <20).
- [x] Run `grep -rE "oideachais\.dlt_sources|oideachais\.dagster_defs|oideachais\.dagster_assets"`
  — count = 0 (target: 0).
- [x] Run `git diff openspec/specs/` — 5 files modified, ~66 lines changed.
- [x] Run `openspec validate oideachais-pipeline --strict` — 1 pre-existing
  error (Requirement outside main section), unchanged from HEAD.
- [x] Run `openspec validate oideachais-leabharlann --strict` — valid.
- [x] Run `openspec validate meaisinfhoghlaim-platform --strict` — 3
  pre-existing errors (Requirements outside main section), unchanged from HEAD.
- [x] Run `openspec validate croilar-data-engineering --strict` — valid.
- [x] Run `openspec validate indexing-and-cognition --strict` — valid.

## 5. Write the openspec change (30 min)

- [x] Write `proposal.md` — rename pairs table + acceptance gates + deferred
  work.
- [x] Write `tasks.md` (this file).
- [x] Write 5 MODIFIED spec deltas:
  - `specs/oideachais-pipeline/spec.md` — codifies the v4 namespace convention
  - `specs/oideachais-leabharlann/spec.md` — codifies the v4 namespace convention
  - `specs/meaisinfhoghlaim-platform/spec.md` — codifies the v4 namespace convention
  - `specs/croilar-data-engineering/spec.md` — codifies the v4 namespace convention
  - `specs/indexing-and-cognition/spec.md` — codifies the v4 namespace convention

## 6. Validate + commit + push (10 min)

- [x] Run `openspec validate 2026-07-13-openspec-drift-cleanup-v1 --strict`.
- [ ] Commit with the message template (see proposal.md).
- [ ] Push to `origin/pick-4-biep-v1` (NOT `main`).