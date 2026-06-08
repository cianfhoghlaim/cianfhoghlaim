# Tasks: croilar-hf-build-small-2026-demo

## Phase 0: Pre-build (Day 0 — pre-Sun, during plan mode → build mode transition)

- [x] Write `doc/hackathons/build-small-2026-docs-catalogue.md` (consolidated catalogue)
- [x] Write `doc/hackathons/croilar-demo-quadrant-indexes.md` (per-quadrant asset indexes)
- [x] Write `doc/hackathons/build-small-2026-model-fallback.md` (LiteLLM fallback chains)
- [x] Write `openspec/changes/croilar-hf-build-small-2026-demo/{proposal,tasks,spec}.md`
- [x] Patch `doc/hackathons/build-small-2026-plan.md` (re-themes section + 5-element story)
- [ ] `openspec validate croilar-hf-build-small-2026-demo --strict`
- [ ] `git add -A && git commit -m "hackathon: croilar-hf-build-small-2026-demo — catalogue + indexes + model fallback + OpenSpec change"`
- [ ] `git push`

## Phase 1: `spaces/_common/` shared bundle (Day 1)

- [ ] Create `spaces/_common/` directory at repo root
- [ ] `spaces/_common/theme.py` — Celtic theme tokens (deep green + amber + stone gray + Celtic teal + 5-element colours), Hades Shadow-First palette
- [ ] `spaces/_common/anam_bonneagar_footer.py` — small per-Space footer showing Pobal HP decile + 32B model alias + linter score
- [ ] `spaces/_common/soulbound_svg.py` — deterministic Celtic-knot SVG generator (from `tuatha/apps/crypteolas_demo/anam-contracts/src/CuchulainnNFT.sol:173-203`)
- [ ] `spaces/_common/social_card.py` — 4 social card generator (Hugging Face logo + project name + tagline + HF Space URL)
- [ ] `spaces/_common/demo_recorder.py` — 30-second screen recorder (Gradio + moviepy or ffmpeg)
- [ ] `spaces/_common/i18n.py` — bilingual EN/GA toggle (using `croilar/packages/i18n/` pattern)
- [ ] `spaces/_common/README.md` — usage docs for the bundle

## Phase 2: BAML re-pointing to HF Inference (Day 1)

- [ ] Fork `tuatha/baml_src/tuatha_clients.baml` → `tuatha/baml_src/clients_hackathon.baml`
- [ ] Re-point to HF Inference per `doc/hackathons/build-small-2026-model-fallback.md`:
  - `BAML_HACKATHON_PRIMARY` → `Qwen/Qwen2.5-7B-Instruct` on `https://api-inference.huggingface.co/v1`
  - `BAML_HACKATHON_FALLBACK_1` → `meta-llama/Llama-3.1-8B-Instruct`
  - `BAML_HACKATHON_FALLBACK_2` → `google/gemma-2-9b-it`
- [ ] Add `HF_TOKEN` to HF Space secrets
- [ ] Run `baml-cli generate` from `tuatha/baml_src/` to rebuild the BAML client
- [ ] Smoke test: invoke `ExtractCurriculumSyllabus` against the new client

## Phase 3: New BAML schemas (Day 1–2)

### For Space 1
- [ ] `oideachais/data_platform/baml_src/extract_circular_meta.baml` — `ExtractCircularMeta()` (~30 lines) — from `docs/03-agents/baml-extraction.md:508-524`
- [ ] `oideachais/data_platform/baml_src/exit_card.baml` — `GenerateExitCardQuestions()` + `ScoreExitCardResponse()` (~60 lines)
- [ ] `oideachais/data_platform/baml_src/marking_scheme_diff.baml` — `ComposeMarkingSchemeDiff()` (~40 lines)
- [ ] `oideachais/data_platform/baml_src/primary_framework.baml` — `ExtractPrimaryFramework()` for Junior Infants → 6th Class (~50 lines)

### For Space 2
- [ ] `meaisínfhoghlaim/baml_src/terminologue.baml` — `ExtractTerminologueEntry()` (~30 lines)
- [ ] `meaisínfhoghlaim/baml_src/bardic_grade.baml` — `MapToBardicGrade()` (~40 lines)
- [ ] `tuatha/baml_src/cross_border_alignment.baml` — `CrossBorderAlignment` class + `AlignCrossBorder()` (~50 lines)
- [ ] `meaisínfhoghlaim/baml_src/school_geography.baml` — `SchoolGeography` class (~30 lines)

### For Space 3
- [ ] `tuatha/baml_src/extract_wikipedia_article.baml` — `ExtractWikipediaArticle()` (~60 lines, extended from `MythologicalCharacter`)
- [ ] `tuatha/baml_src/evaluate_riddle_response.baml` — `EvaluateRiddleResponse()` (~50 lines, modelled on `MarkingPoint`)

### For Space 4
- [ ] `meaisínfhoghlaim/baml_src/formative_question.baml` — `FormativeQuestion` class (~40 lines)
- [ ] `meaisínfhoghlaim/baml_src/chemistry_visual.baml` — `ChemistryVisual` class + Fibo JSON (~40 lines)

- [ ] Run `baml-cli generate` for all BAML clients
- [ ] Smoke test each new function against the 3-tier fallback chain

## Phase 4: Space 1 "An Scrúdú" (Day 3)

- [ ] Create `spaces/an-scrudai/` directory
- [ ] `spaces/an-scrudai/app.py` — Gradio Blocks with 8 tabs:
  1. NCCA syllabus heatmap (33 subjects × 17 years)
  2. Marking-scheme diff viewer (side-by-side year-on-year)
  3. Past-paper topic graph (force-directed)
  4. PCLM-PDF marking-scheme pack (export)
  5. Dúchas Manuscript Explorer (NEW, browse by county)
  6. Policy Circular Timeline (NEW, CircularStatus)
  7. DPRE Live "New Papers Detected" Feed (NEW, dynamic partitions sensor)
  8. Cross-Strand Prerequisite Heatmap + Pobal HP Context Overlay (NEW)
- [ ] `spaces/an-scrudai/data.py` — DuckDB queries against `oideachais/data_platform/` (or static CSVs for the demo)
- [ ] `requirements.txt` — `gradio`, `baml`, `pandas`, `plotly`
- [ ] `README.md` — Space metadata, how to run locally
- [ ] HF Space config: `app.py` + `requirements.txt` + `README.md` + small Yaml frontmatter
- [ ] Test locally: `gradio app.py`
- [ ] Record demo video #2 (An Scrúdú, 60–90 sec)
- [ ] Deploy to HF Space `build-small-hackathon/an-scrudai`

## Phase 5: Space 2 "Meaisín Cliste" (Day 4)

- [ ] Create `spaces/meaisin-cliste/` directory
- [ ] `spaces/meaisin-cliste/app.py` — Gradio Blocks with 3-theme tab layout (Foclóir / Scoil ar an Léarscáil / Curaclam Trasteorann)
- [ ] `spaces/meaisin-cliste/focloir.py` — 5 features:
  1. Type English word → 6-nation cognate table
  2. Live Terminology Cross-Reference (GaDOIS Tearma)
  3. Bardic Grade Quiz (Ollamh → Fochlocon)
  4. Etymology card
  5. In-context sentence generation
- [ ] `spaces/meaisin-cliste/scoil.py` — 5 features:
  1. Leaflet map of 7 nations + every Celtic-medium school pinned
  2. Click pin → school curriculum side-by-side
  3. Pobal HP filter
  4. Manx Bunscoill Ghaelgagh data story
  5. Scottish Gaelic Árainneachd H3 hex grid
- [ ] `spaces/meaisin-cliste/curaclam.py` — 5 features:
  1. 12-agent Q&A in EN/GA
  2. Agent provenance
  3. SQA↔NCCA↔WJEC↔CCEA↔IoM↔Cornwall alignment matrix
  4. Cornish & Breton "Forgotten Nations" panel
  5. Cross-border credit transfer
- [ ] `requirements.txt` — `gradio`, `baml`, `pandas`, `plotly`, `folium`, `h3`
- [ ] `README.md`
- [ ] Test locally
- [ ] Record demo video #3 (Meaisín Cliste, 90 sec)
- [ ] Deploy to HF Space `build-small-hackathon/meaisin-cliste`

## Phase 6: Space 3 "Cianfhoghlaim" (Day 2 — moved to first for risk reduction)

- [ ] Create `spaces/cianfhoghlaim/` directory
- [ ] `spaces/cianfhoghlaim/app.py` — Gradio Blocks with iframe of Babylon.js WebGPU scene + 6 NPC side panel
- [ ] `spaces/cianfhoghlaim/scene.html` — Babylon.js WebGPU scene with 4 diegetic zones, 6 NPCs, WGSL Celtic-knot shader
- [ ] `spaces/cianfhoghlaim/npcs.py` — 6 NPCs loaded from cached Wikipedia sources:
  1. Uí Liatháin lord (Loughcrew)
  2. Brec/Óengus (Rathmore)
  3. Manannán mac Lir (Isle of Man)
  4. Rhiannon (Prysgwyddion, Dyfed)
  5. Dian Cécht (Leinster Healing Well)
  6. Cian (Loughcrew)
- [ ] `spaces/cianfhoghlaim/quests.py` — 5 NEW quest types:
  1. Uí Liatháin Exile Chain
  2. Déisi Living Epic
  3. Manannán Ferryman's Trial (3 riddles)
  4. Rhiannon Justice Mechanic
  5. Cian Sun-Gem Quest (shape-shifting)
- [ ] `spaces/cianfhoghlaim/anvil_sidecar/` — Anvil container for CuchulainnNFT.sol
- [ ] `spaces/cianfhoghlaim/landscape_scraper.py` — gov.ie / gov.uk landscape image scraper
- [ ] `requirements.txt` — `gradio`, `baml`, `httpx`, `beautifulsoup4`, `Pillow`, `solcx` (for Anvil)
- [ ] `Dockerfile` (multi-stage: Gradio + Anvil sidecar)
- [ ] `README.md`
- [ ] Cache the 6 Wikipedia sources to `doc/hackathons/wikipedia-sources/`
- [ ] Test locally
- [ ] Record demo video #1 (Cianfhoghlaim, 90 sec)
- [ ] Deploy to HF Space `build-small-hackathon/cianfhoghlaim`

## Phase 7: Space 4 "Anam: Tuatha na nGaelscoil" (Day 5)

- [ ] Create `spaces/anam-tuatha-na-ngaelscoil/` directory
- [ ] `spaces/anam-tuatha-na-ngaelscoil/app.py` — Gradio Blocks with 5-element tab layout (Tine / Uisce / Talamh / Aer / Anam + Mac Léinn + Fiosraigh)
- [ ] `spaces/anam-tuatha-na-ngaelscoil/tine.py` — OCR-Powered Exam Paper Transformer (Feature 1)
- [ ] `spaces/anam-tuatha-na-ngaelscoil/uisce.py` — Chemistry/Biology Visual Asset Factory (Feature 2)
- [ ] `spaces/anam-tuatha-na-ngaelscoil/talamh.py` — Interactive British Isles Education Map (Feature 3)
- [ ] `spaces/anam-tuatha-na-ngaelscoil/aer.py` — Celtic Languages Curriculum Bridge (Feature 4)
- [ ] `spaces/anam-tuatha-na-ngaelscoil/anam.py` — Soulbound Credential & NFT Minting (Feature 5, uses CuchulainnNFT.sol on Anvil sidecar)
- [ ] `spaces/anam-tuatha-na-ngaelscoil/mac_leinn.py` — Formative Assessment from Real Exam Papers (Feature 6)
- [ ] `spaces/anam-tuatha-na-ngaelscoil/fiosraigh.py` — Classroom-to-MMO Bridge (Feature 7)
- [ ] `requirements.txt` — `gradio`, `baml`, `httpx`, `solcx`, `Pillow`
- [ ] `Dockerfile` (multi-stage: Gradio + Anvil)
- [ ] `README.md` — explain the 5-element connective-tissue story
- [ ] Test locally
- [ ] Record demo video #4 (Anam: Tuatha na nGaelscoil, 120 sec)
- [ ] Deploy to HF Space `build-small-hackathon/anam-tuatha-na-ngaelscoil`

## Phase 8: Polish + accessibility (Day 6)

- [ ] Bilingual EN/GA verification for every Space (i18n strings)
- [ ] Accessibility audit using `chrome_lighthouse_audit` against each Space
- [ ] Mobile-responsive check
- [ ] Anam Bonneagar footer added to all 4 Spaces
- [ ] Social cards auto-rendered for all 4 Spaces
- [ ] Bilingual blog post published (EN + GA)

## Phase 9: Submission + OpenSpec archive (Day 7)

- [ ] All 4 HF Space URLs live and working
- [ ] All 4 demo videos uploaded to YouTube and embedded in the blog post
- [ ] `openspec validate croilar-hf-build-small-2026-demo --strict` passes
- [ ] OpenSpec change marked ready for review
- [ ] OpenSpec `spec:archive croilar-hf-build-small-2026-demo --yes` after approval
- [ ] Twitter / Mastodon thread with 4 social cards
- [ ] Final commit + push to remote
