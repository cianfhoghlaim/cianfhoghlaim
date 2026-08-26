# Tasks — meaisinfhoghlaim + Unsloth Studio + Agent Fleet Integration v1

Total: 47 tasks across 4 phases. Estimated effort: **~2 weeks** (10 working days).

## Phase 1 — The 5-agent meaisínfhoghlaim surface (5 days)

- [ ] **1.1** Write `agents/meaisinfhoghlaim/tools/__init__.py` with the 8-tool `TOOL_REGISTRY` (per the proposal §Tools)
- [ ] **1.2** Implement `agents/meaisinfhoghlaim/tools/ocr_qwen3_vl_8b.py` — OpenAI-compatible HTTP client to `host.docker.internal:8888/v1/chat/completions` with `model=unsloth/Qwen3-VL-8B-Instruct-GGUF`
- [ ] **1.3** Implement `agents/meaisinfhoghlaim/tools/ocr_gemma4_26b.py` — OpenAI-compatible HTTP client to `http://llama-swap:8080/v1/chat/completions` with `model=local/vision/gemma-4-26B-A4B`
- [ ] **1.4** Implement `agents/meaisinfhoghlaim/tools/ocr_unstract.py` — Unstract prompt-driven extraction
- [ ] **1.5** Implement `agents/meaisinfhoghlaim/tools/ocr_docling.py` — Docling DocTags XML output
- [ ] **1.6** Implement `agents/meaisinfhoghlaim/tools/htr_finetune_unsloth_local.py` — Python subprocess wrapper around `finetune_unsloth_local.py` for Modal H100 / M4 Max
- [ ] **1.7** Implement `agents/meaisinfhoghlaim/tools/bilingual_align.py` — fast_align + eflomal subprocess wrapper
- [ ] **1.8** Implement `agents/meaisinfhoghlaim/tools/web_form_fill.py` — Playwright MCP client
- [ ] **1.9** Implement `agents/meaisinfhoghlaim/tools/bash_execute.py` — subprocess.run with cwd=/tmp/agent-sandbox/
- [ ] **1.10** Implement `agents/meaisinfhoghlaim/tools/eval_orchestrator.py` — RAGAS evaluator
- [ ] **1.11** Implement `agents/meaisinfhoghlaim/educational/ocr_router.py` — uses all 4 OCR tools to pick the best per PDF
- [ ] **1.12** Implement `agents/meaisinfhoghlaim/educational/htr_fine_tuner.py` — uses htr_finetune_unsloth_local
- [ ] **1.13** Implement `agents/meaisinfhoghlaim/educational/schema_extractor.py` — uses ocr_qwen3_vl_8b + BAML
- [ ] **1.14** Implement `agents/meaisinfhoghlaim/educational/eval_orchestrator.py` — uses eval_orchestrator tool
- [ ] **1.15** Implement `agents/meaisinfhoghlaim/educational/alignment_worker.py` — uses bilingual_align

## Phase 2 — Bonneagar + ciancheiltis + HTR/alignment/Gemma (5 days)

- [ ] **2.1** Update `openspec/changes/2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1/specs/meaisinfhoghlaim-ocr-htr/spec.md` (REMODIFIED)
- [ ] **2.2** Update `openspec/changes/2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1/specs/meaisin-24-ocr-models/spec.md` (REMODIFIED)
- [ ] **2.3** Update `openspec/changes/2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1/specs/agent-platform-cluster/spec.md` (REMODIFIED)
- [ ] **2.4** Update `openspec/changes/2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1/specs/agentic-frontend-frameworks/spec.md` (REMODIFIED)
- [ ] **2.5** Update `openspec/changes/2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1/specs/bonneagar-tuatha-iac-stack/spec.md` (REMODIFIED)
- [ ] **2.6** Write `openspec/changes/2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1/specs/ciancheiltis-htr-pipeline/spec.md` (NEW)
- [ ] **2.7** Write `openspec/changes/2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1/specs/meaisinfhoghlaim-bilingual-alignment/spec.md` (NEW)
- [ ] **2.8** Wire `agents/meaisinfhoghlaim/tools/` to Hermes via the `tool_use` schema (BAML `Generate*` functions)
- [ ] **2.9** Wire the same tools to OpenClaw via the `fallback_chain` config (OpenClaw dispatches tools on M3 plan quota exhaustion)
- [ ] **2.10** Write `dlt_sources/cultural_heritage/duchas_images_htr.py` (the HTR-specific duchas loader)
- [ ] **2.11** Write `dlt_sources/cultural_heritage/_htr_helpers.py` (IIIF + page-level transcription helpers)
- [ ] **2.12** Write `dlt_sources/language/bilingual_alignment.py` (EUR-Lex + NCCA bilingual aligner)
- [ ] **2.13** Write `dlt_sources/language/_alignment_helpers.py` (fast_align + eflomal helpers)
- [ ] **2.14** Write `dlt_sources/language/ndcc_syllabus.py` (the NCCA LC syllabus loader, bilingual EN + GA)
- [ ] **2.15** Write `dlt_sources/language/eur_lex.py` (the EUR-Lex Irish-English parallel corpus loader)
- [ ] **2.16** Fine-tune Gemma 4 4B on NCCA LC Gaeilge syllabus (LoRA r=16, 3 epochs, Modal H100). Output: `gemma-4-e4b-ncca-gaeilge-v1` adapter
- [ ] **2.17** Fine-tune Qwen3-VL-8B on Dúchas cbes (QLoRA r=8, 3 epochs, Modal H100). Output: `qwen3-vl-8b-gaeilge-htr-v1` adapter
- [ ] **2.18** Add `mise.toml` entries for the ciancheiltis HTR pipeline (`ciancheiltis:htr-test`, `ciancheiltis:align-test`, `ciancheiltis:finetune-gemma`)
- [ ] **2.19** Run `openspec validate 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 --strict` (MUST exit 0)
- [ ] **2.20** Run `openspec validate --all` to verify no regressions
- [ ] **2.21** Run `mise run lint:registry` (verifies no hardcoded model strings)
- [ ] **2.22** Run the end-to-end agent chain test (the 5 agents in concert on a sample LC Gaeilge paper)
- [ ] **2.23** Wire `web_form_fill` tool via Playwright MCP into Hermes + OpenClaw. OpenClaw TUI exposes `web_form_fill`
- [ ] **2.24** Wire `bash_execute` tool with sandbox at `/tmp/agent-sandbox/`. OpenClaw can run tests in isolation
- [ ] **2.25** Wire `eval_orchestrator` tool into OpenChamber. RAGAS scores visible in chat

## Phase 3 — Full web stack enablement (4 days)

- [ ] **3.1** Upgrade `tuatha-ui` to `@copilotkit/react-core/v2` (per `react-core` + `a2ui-renderer` skills)
- [ ] **3.2** Add the 8 new tools to the `tool_use` schema in `baml_src/clients.baml`
- [ ] **3.3** Wire the BAML `tool_use` to AG-UI event bridge in `tuatha-ui`
- [ ] **3.4** Wire Convex reactive state for the per-tool result streaming
- [ ] **3.5** Wire TanStack Start routes for the 6 user-facing features (per the prior plan §7)
- [ ] **3.6** Add Langfuse + MLflow instrumentation to the CopilotKit chat surface
- [ ] **3.7** Wire OpenChamber with the same tools + AG-UI bridge + TanStack Start routes (the operator surface)
- [ ] **3.8** Author `ciandlithe-web` + `cianchosaint-web` TanStack Start scaffolds (per Wave 5)

## Phase 4 — Tutorial notebooks + verify script + mise tasks (1 day)

- [ ] **4.1** Write `notebooks/31_onboarding_01_env_check.py` (3 min walkthrough)
- [ ] **4.2** Write `notebooks/32_onboarding_02_first_unsloth_chat.py` (5 min walkthrough)
- [ ] **4.3** Write `notebooks/33_onboarding_03_4_stack_walkthrough.py` (10 min walkthrough)
- [ ] **4.4** Write `notebooks/34_onboarding_04_biep_ocr_eval.py` (15 min walkthrough)
- [ ] **4.5** Write `notebooks/35_onboarding_05_duchas_htr.py` (20 min walkthrough)
- [ ] **4.6** Write `scripts/verify-unsloth-serve.sh` (the 7-step verification protocol)
- [ ] **4.7** Add the 7 `mise.toml` tasks (`tutorial:01-env` ... `tutorial:05-duchas-htr` + `tutorial:all` + `tutorial:verify`)
- [ ] **4.8** Run `mise run tutorial:all` to verify the 50-min walkthrough works end-to-end
- [ ] **4.9** Run `mise run tutorial:verify` (the 7-step verification protocol) — MUST exit 0
- [ ] **4.10** Commit + push

## Done-when criteria

- [ ] All 47 tasks `[x]`
- [ ] `openspec validate --all --strict` returns 160+ passed, 0 failed
- [ ] `mise run lint:registry` exits 0 (no hardcoded model strings)
- [ ] `mise run tutorial:all` works end-to-end
- [ ] `mise run tutorial:verify` exits 0
- [ ] 2 new fine-tuned adapters (`gemma-4-e4b-ncca-gaeilge-v1`, `qwen3-vl-8b-gaeilge-htr-v1`) pushed to HuggingFace Hub

## Out of scope (follow-up changes)

- Carve out `bonneagar/` + `meaisinfhoghlaim/` + `ciancheiltis/` to their own repos (per the v2 plan, deferred past 12-month horizon)
- Full BIEP Ireland + England coverage (~3 weeks of work)
- 5 other sister jurisdictions (Scotland + Wales + NI + Jersey + Guernsey + IoM)
- Wave 4 DuckLake hardening (`metadata_schema` per quadrant + `SORTED BY` + nightly maintenance)
- Wave 6 frontend modernisation (CopilotKit v2 across all 4 web surfaces)
