# Tasks: Sister-repo gemini_hackathon Lesson Transfer v1

> 6 phases, ~30 tasks. All tasks MUST pass before `openspec archive`.

## Phase A — OpenSpec scaffolding (5 min)

- [ ] **A.1** Author `proposal.md` + `tasks.md`
- [ ] **A.2** `openspec validate 2026-08-31-sister-repo-gemini-lesson-transfer-v1 --strict`

## Phase B — bonneagar IaC promotion (30 min)

- [ ] **B.1** Promote the 6 GCP mirror stacks from Phase 3 to canonical location
- [ ] **B.2** Update `bonneagar/AGENTS.md` with GCP-first pattern references
- [ ] **B.3** Add Stackdriver AI Agent ADK instrumentation docs

## Phase C — tuatha (60 min — biggest transfer)

- [ ] **C.1** Add Primary + UnslothGemma4 + VertexGemini35Flash BAML clients to `~/dev/tuatha/tuatha/baml/`
- [ ] **C.2** Add Document AI for character data (replaces qwen3-vl-8b)
- [ ] **C.3** Add AG-UI/A2UI/CopilotKit per-persona dashboards
- [ ] **C.4** Add ADK 2-stage coordinators (per-subject quest-pack pattern)

## Phase D — ciancheiltis (45 min)

- [ ] **D.1** Add the 6 Celtic-language BAML extraction path lifted to gemma-4-26b-a4b
- [ ] **D.2** BGE-M3 embedder swap (the canonical cianfhoghlaim embedder)
- [ ] **D.3** Add Document AI for manuscript OCR

## Phase E — ciandlithe (45 min)

- [ ] **E.1** Add Document AI OCR-ensemble path-1 for the legal-doc pipeline
- [ ] **E.2** Add the OSINT legal-doc DLT source (BAILII + ICLR + CaseMine + ...)
- [ ] **E.3** Add the dossier-generator CopilotKit UI per the gemini_hackathon Stitch pattern

## Phase F — cianchosaint (45 min)

- [ ] **F.1** Add the OSINT defence DLT source (CSO Ireland + data.police.uk + ...)
- [ ] **F.2** Add Cloud Run ADK 2-stage coordinators
- [ ] **F.3** Add AG-UI per-persona dashboards

## Phase G — Reciprocal mirrors (15 min)

- [ ] **G.1** Author `openspec/changes/2026-08-31-bonneagar-sister-mirror-v1/`
- [ ] **G.2** Author `openspec/changes/2026-08-31-tuatha-sister-mirror-v1/`
- [ ] **G.3** Author `openspec/changes/2026-08-31-ciancheiltis-sister-mirror-v1/`
- [ ] **G.4** Author `openspec/changes/2026-08-31-ciandlithe-sister-mirror-v1/`
- [ ] **G.5** Author `openspec/changes/2026-08-31-cianchosaint-sister-mirror-v1/`

## Phase H — Validation (10 min)

- [ ] **H.1** `mise run openspec:validate 2026-08-31-sister-repo-gemini-lesson-transfer-v1 --strict`
- [ ] **H.2** `mise run lint:registry` — 0 drift
- [ ] **H.3** `mise run lint:skills` — 66 skills pass

---

*Last updated by build subagent at 2026-08-31.*