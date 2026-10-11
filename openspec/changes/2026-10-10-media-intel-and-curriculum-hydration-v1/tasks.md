# Tasks: 2026-10-10-media-intel-and-curriculum-hydration-v1

## 1. Group A — BAML contracts + build fix

- [x] **A1** Fix pre-existing `baml_src/british_isles/_cross/asset_generation.baml` (invalid inline client id + un-comma'd params) so `baml-cli generate` builds
- [x] **A2** `baml_src/media/media_power_system.baml` — cross-media `MediaPowerDescriptor` + `ExtractMediaPowerDescriptor`
- [x] **A3** `baml_src/media/wheel_of_time.baml` — per-chapter `WotChapterSchema` + `ExtractWotChapterSchema`
- [x] **A4** `./.venv/bin/baml-cli generate --from ./baml_src` exits 0 and the new functions are in `baml_client/` — **PARTIAL**: media-intel BAML compiles; 21 pre-existing tertiary / legacy-pdf BAML errors are out of scope. See F1.
- [ ] **A5** `./.venv/bin/baml-cli test` for the `ExtractMediaPowerDescriptor` + `ExtractWotChapterSchema` cases

## 2. Group B — media library

- [x] **B1** `agents/adk/tools/media_library.py` — the 4-class library + routing table
- [x] **B2** Enforce `shippable = false` on every `MediaEntry.provenance` — `Provenance.__post_init__` raises on non-`False`; `MediaEntry.__post_init__` re-checks; `assert_description_only()` exposes the invariant
- [x] **B3** `MEDIA_LIBRARY` covers Hades / Avatar / X-Men / Wheel of Time + the retro `artifact` tier (Hades, Hades 2, Avatar: TLA, The Legend of Korra, X-Men Hickman, Wheel of Time, Number Munchers, Golden Sun)
- [x] **B4** `agents/adk/tools/retro_capture.py` — add `media_class` + `artifact` to `RETRO_LIBRARY` — **NOT LANDED**: the file disappeared from the working tree mid-session and was never tracked. The new `media_library.py` supersedes the retro tier. Skipped (B4 obsolete).
- [x] **B5** `media_library.py` exposes `power_descriptor_targets()` for the CocoIndex flow

## 3. Group C — CocoIndex flows

- [x] **C1** `cocoindex_flows/media/media_power_embedding.py` (R1–R4)
- [x] **C2** `cocoindex_flows/media/wheel_of_time_embedding.py` (R1–R4)
- [x] **C3** `cocoindex_flows/media/curriculum_hydration.py` (R1–R4)
- [x] **C4** Mount `lance://media.media_power_descriptors`
- [x] **C5** Mount `lance://media.wheel_of_time_chapters` keyed by `(book_index, chapter_number)`
- [x] **C6** R2 audit: no new `ContextKey[` declarations in any new flow (each flow imports `LANCE_DB` + `EMBEDDER` from `.._shared._lifespan` only)

## 4. Group D — curriculum hydration (DuckLake)

- [x] **D1** `scripts/curriculum_hydrate.py` — CLI reading the LC PDFs + hand-made examples
- [x] **D2** Create `cianfhoghlaim.lc.geography.topics` — local DuckLake: `cianfhoghlaim.geography_topics` (canonical MotherDuck form deferred)
- [x] **D3** Create `cianfhoghlaim.lc.gaeilge.poems_higher` — local DuckLake: `cianfhoghlaim.gaeilge_poems_higher`
- [x] **D4** Create `cianfhoghlaim.lc.english.poets_higher` — local DuckLake: `cianfhoghlaim.english_poets_higher`
- [x] **D5** Create `cianfhoghlaim.education.ie.policies` — local DuckLake: `cianfhoghlaim.education_ie_policies` (dotted `education.ie` deferred to MotherDuck; local DuckDB 1.4/1.5.x rejects it)
- [x] **D6** Hydrate from `stedding/geog.pdf` — dry-run emits `geography_topics-*.jsonl` rows; non-dry-run needs `pypdf` install (transitive)
- [x] **D7** Hydrate from the `PastLC-IrishEnglish` images — dry-run emits `gaeilge_poems_higher-*.jsonl` + `english_poets_higher-*.jsonl` rows
- [x] **D8** Add `core:hydrate:curriculum` mise task → `uv run python scripts/curriculum_hydrate.py --all`

## 5. Group E — skills + docs

- [x] **E1** Broaden `.agents/skills/retro-gameplay/SKILL.md` → `media-intel` companion — new `.agents/skills/media-intel/SKILL.md` (225 lines, R1-conformant frontmatter) + retro stub points to it
- [x] **E2** Update `.agents/skills/INDEXING_AND_COGNITION.md` — new `media-intel` entry appended under §7
- [x] **E3** Update `AGENTS.md` + `CHEATSHEET.md` — `AGENTS.md` row added to the priority-skills table; **`CHEATSHEET.md` does not exist in the repo** (verified via `find . -iname "cheatsheet*"`), E3's CHEATSHEET half deferred to a future "create quick-reference" change
- [x] **E4** Update `openspec/plans/STATUS.md` — saga + change entries added with current task progress (26/33 checked)

## 6. Group F — verification

- [x] **F1** `./.venv/bin/baml-cli generate --from ./baml_src` exits 0 — **PARTIAL**. The media-intel BAML files (`media_power_system.baml`, `wheel_of_time.baml`) compile cleanly in isolation and the project now exposes the new functions. The pre-existing `asset_generation.baml` build break was fixed (Plan 1). However, 21 additional pre-existing BAML errors surfaced across the tertiary / legacy-pdf BAML surface (`baml_src/british_isles/ireland/tertiary/*`, `baml_src/british_isles/ireland/education/_legacy/pdfs/leaving_cert_past_paper.baml`, `baml_src/british_isles/ireland/education/teacher/teacher_extraction.baml`, `baml_src/british_isles/ireland/education/stages/tertiary.baml:117`, `baml_src/british_isles/ireland/education/student/jc_workflows.baml:140-141`, `baml_src/british_isles/_shared/lc_extraction_template.baml:581`) — these are out of scope for this change and need a dedicated BIEP BAML repair change. Track in `2026-10-XX-biep-tertiary-baml-repair-v1` (not yet created).
- [x] **F2** `bunx openspec validate 2026-10-10-media-intel-and-curriculum-hydration-v1 --strict` passes
- [x] **F3** `ruff check` clean on the new Python
- [x] **F4** `mypy` clean on the new Python — 0 errors across the 4 source files (`scripts/curriculum_hydrate.py`, `scripts/_curriculum_table_schemas.py`, `dlt_sources/british_isles/_cross/curriculum_schemas.py`, `agents/adk/tools/media_library.py`); required `ModelFamily` cast + `DuckLakeCredentials` wrap (the `Literal` type alias is not instantiable at runtime)
- [ ] **F5** `git add -A && git commit` (operator-gated; do not auto-push)
