# Tasks: sync-skills-from-docs-round-8

## 1. OpenSpec change scaffolding
- [x] Create change directory.
- [x] Write `MERGE_MAP.md` (Phase 0 reconnaissance).
- [x] Write `proposal.md`.
- [x] Write `tasks.md` (this file).
- [x] Write 2 spec deltas (tuatha-platform, new
      celtic-asset-generation).
- [x] Validate `--strict`.

## 2. Phase 1: New skills (4)
- [x] `.agents/skills/celtic-asset-generation/SKILL.md`
      (298 lines) — Celtic asset generation pipeline.
- [x] `.agents/skills/tuatha-mmo/SKILL.md` (316 lines) —
      Tuatha MMO architecture + cosmology + agents.
- [x] `.agents/skills/irish-llm-on-device/SKILL.md` (255
      lines) — Apple Silicon + MLX + on-device OCR/HTR.
- [x] `.agents/skills/upstream-mirrors/SKILL.md` (147
      lines) — 11 KCG-mirrored upstream repos.

## 3. Phase 2: Move 119 KEEP-NEW files into references/
- [x] 41 moves → `celtic-asset-generation/references/`
      (incl. 2 PDFs to `references/papers/`, 8 to
      `references/clippings/`)
- [x] 44 moves → `tuatha-mmo/references/` (incl. 6 to
      `references/clippings/`)
- [x] 15 moves → `irish-llm-on-device/references/` (incl. 4
      to `references/clippings/`)
- [x] 19 moves → `upstream-mirrors/references/` (incl. 3
      to `references/clippings/`)

## 4. Phase 3: Expand 8 existing skills (+1,492 lines)
- [x] `baml` (+160) — Polyglot IDL section.
- [x] `celtic-language-ai` (+237) — KCG Celtic LLMs +
      Diffusion NMT + English-pivoted CoT.
- [x] `cross-domain-registry` (+112) — 2024-25 census +
      fiscal context.
- [x] `kcg-leabharlann-pipeline` (+200) — Ingestion layer.
- [x] `kcg-ml-models` (+241) — EuroLLM 22B + Inference
      backends.
- [x] `motherduck` (+138) — MCP server.
- [x] `oideachas-pipeline` (+126) — EU sources catalogue.
- [x] `tuatha-platform` (+278) — Sovereign game state +
      Dagster assets for MMO.

## 5. Phase 4: Dedup + delete
- [x] 5 from `docs/sruth/tuatha/` (INDEX, ANALYSIS, README,
      GRAPHICS_INDEX, Agentic Web Scraping Pipeline.md
      duplicate).
- [x] 5 from `docs/teanga/` (INDEX, README,
      notebooklm_1, Gaelic ÈIST, DSPydantic).
- [x] 10 dedup duplicates from `references/`.
- [x] `rm -rf docs/teanga/`.

## 6. Verify
- [ ] Re-validate `--strict`.
- [ ] `git status --short | wc -l` is reasonable
      (~150-180 staged).

## 7. Archive
- [ ] `openspec archive sync-skills-from-docs-round-8
      --yes`.

## 8. Land the plane
- [ ] `git add` only my changes (avoid the pre-existing
      .gitignore, .infisical.env, stirling-pdf,
      cocoindex_flows, untracked top-level docs, etc.).
- [ ] `git commit -m "..."`.
- [ ] `git push`.
