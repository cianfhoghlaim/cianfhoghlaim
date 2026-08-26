# meaisinfhoghlaim + Unsloth Studio + Agent Fleet Integration v1

## Why

Three strategic pillars converge in this change:

**Pillar 1: Unsloth Studio replaces llama-swap for Unsloth GGUFs.**
The prior architecture had 4 OCR backends (llama-swap + mlx-omni + transformers + unsloth-serve) for the meaisinfhoghlaim 24-entry VISION_MODELS registry. The unsloth-serve container could not start in practice (per the prior session's `9fbd9820f` commit). With Unsloth Studio now running directly on the bunchloch host at `localhost:8888`, accessible from Docker via `host.docker.internal:8888`, the 4-backend surface simplifies to 3 (Unsloth Studio + llama-swap + transformers). The 22 litellm routes verified in this session prove the integration works.

**Pillar 2: Hermes + OpenClaw + OpenChamber as the agentic surface.**
The meaisinfhoghlaim v3 operator surface (per the existing `meaisin-v3-operator-surface` spec + the new `meaisin-24-ocr-models` spec) has 24 OCR/VLM models + 7 document converters + 12 agents. None of these are wired to Hermes/OpenClaw/OpenChamber today. This change adds 8 canonical tools (4 OCR + 1 HTR fine-tune + 1 alignment + 1 schema extract + 1 form fill / bash execute / eval orchestrator) + 5 agents (OCR-Router + HTR-FineTuner + Schema-Extractor + Eval-Orchestrator + Alignment-Worker) that use these tools.

**Pillar 3: CIANLEILTIS for HTR + the bilingual EN/GA syllabus map.**
The ciancheiltis sister repo (Phase 4 of the multi-repo scaffold, deferred past 12-month horizon per user Q4) owns the HTR + alignment pipeline. The user's prior ask was "for example fill out forms online or test or use local software selections" + "now that we have Unsloth Studio and Hermes and OpenClaw and this openchamber I believe that we can simplify prioritising the use of those much of the intended fand implemented features of meaisinfhoghlaim htr ocr pdf file processing improve ciancheiltis /Users/cianmacandeisigh/dev/ciancheiltis processing the duchas.ie htr and subtitle alignment and european union irish language and english language alignment to create a dataset alongside bilingual documentation processing in cianfhoghlaim, ciandlithe and cianchosaint sources to help create alignment datasets and train / finetune via unsloth best tactics gemma and associated model registry relevant models and previous plans of ocr and htr and homework scanning in line with the schemas and syllabus processing to improve our game allowing for pagr scan in blilingual irish and english cursive and normal writing as part of the user experience rpogressing through maps of syllabus"

## What changes

### Tools (8 new)

| Tool | Backed by | Use case |
|:--|:--|:--|
| `ocr_qwen3_vl_8b` | Unsloth Studio (host.docker.internal:8888) | OCR baseline via Qwen3-VL-8B-Instruct |
| `ocr_gemma4_26b` | llama-swap (legacy) | OCR fallback via Gemma 4 26B-A4B |
| `ocr_unstract` | Unstract (http://unstract:8002) | Schema-driven extraction |
| `ocr_docling` | Docling (http://docling-serve:5001) | Layout-aware extraction |
| `htr_finetune_unsloth_local` | Unsloth + Modal H100 | Local HTR fine-tune |
| `bilingual_align` | fast_align + eflomal | EU IR-EN + NCCA alignment |
| `web_form_fill` | Playwright MCP | Auto-fill forms online |
| `bash_execute` | local_sandbox | Local shell execution |

### Agents (5 new)

| Agent | Tools used | Dispatched via |
|:--|:--|:--|
| `OCR-Router` | ocr_qwen3_vl_8b, ocr_gemma4_26b, ocr_unstract, ocr_docling | Hermes |
| `HTR-FineTuner` | htr_finetune_unsloth_local | OpenClaw |
| `Schema-Extractor` | ocr_qwen3_vl_8b + BAML | Hermes |
| `Eval-Orchestrator` | all OCR tools + RAGAS | OpenChamber |
| `Alignment-Worker` | bilingual_align | OpenClaw |

### Spec deltas (7)

- `meaisinfhoghlaim-ocr-htr` (REMODIFIED) — Unsloth Studio as primary backend
- `meaisin-24-ocr-models` (REMODIFIED) — adds UNSLOTH_STUDIO backend to the 4-backend schema
- `agent-platform-cluster` (REMODIFIED) — Unsloth fallback chain for the 3 agent vertices
- `agentic-frontend-frameworks` (REMODIFIED) — 4 web surfaces consume Unsloth via litellm
- `bonneagar-tuatha-iac-stack` (REMODIFIED) — 6 new tutorial tasks + verify-unsloth-serve.sh
- `ciancheiltis-htr-pipeline` (NEW) — Dúchas IIIF + EUR-Lex + fine-tune surface
- `meaisinfhoghlaim-bilingual-alignment` (NEW) — EUR-Lex + NCCA bilingual aligner

### Tutorial notebooks (5 new)

- `notebooks/31_onboarding_01_env_check.py` (3 min)
- `notebooks/32_onboarding_02_first_unsloth_chat.py` (5 min)
- `notebooks/33_onboarding_03_4_stack_walkthrough.py` (10 min)
- `notebooks/34_onboarding_04_biep_ocr_eval.py` (15 min)
- `notebooks/35_onboarding_05_duchas_htr.py` (20 min)

Total walkthrough: ~50 min for a fresh user.

### mise.toml additions (6 new tasks)

```toml
[tasks."tutorial:01-env"]             run = "uv run notebooks/31_onboarding_01_env_check.py"
[tasks."tutorial:02-first-chat"]      run = "uv run notebooks/32_onboarding_02_first_unsloth_chat.py"
[tasks."tutorial:03-walkthrough"]     run = "uv run notebooks/33_onboarding_03_4_stack_walkthrough.py"
[tasks."tutorial:04-biep-ocr"]        run = "uv run notebooks/34_onboarding_04_biep_ocr_eval.py"
[tasks."tutorial:05-duchas-htr"]      run = "uv run notebooks/35_onboarding_05_duchas_htr.py"
[tasks."tutorial:all"]                run = "mise run tutorial:01-env && mise run tutorial:02-first-chat && mise run tutorial:03-walkthrough && mise run tutorial:04-biep-ocr && mise run tutorial:05-duchas-htr"
[tasks."tutorial:verify"]             run = "mise run sync:all && bash scripts/verify-unsloth-serve.sh"
```

### `scripts/verify-unsloth-serve.sh`

The 7-step verification protocol from the prior session, packaged as a reusable CI script.

## Impact

### Affected specs (7)
- `meaisinfhoghlaim-ocr-htr` — MODIFIED
- `meaisin-24-ocr-models` — MODIFIED
- `agent-platform-cluster` — MODIFIED
- `agentic-frontend-frameworks` — MODIFIED
- `bonneagar-tuatha-iac-stack` — MODIFIED
- `ciancheiltis-htr-pipeline` — NEW
- `meaisinfhoghlaim-bilingual-alignment` — NEW

### Affected repos (3)
- `cianfhoghlaim` (this repo) — openspec change + 5 tutorial notebooks + verify script + mise additions
- `meaisínfhoghlaim` — 8 tools + 5 agents + the openspec specs live here
- `ciancheiltis` — HTR pipeline + bilingual alignment + Gemma fine-tune
- `tuatha` — bilingual cursive + syllabus map UX

## Dependencies

`Blocked by: none` (Unsloth Studio is already running per the prior `9fbd9820f` commit)

`Blocked by (soft): 2026-08-21-unsloth-v5-architecture-refinement-v1` (already archived; this change builds on its Unsloth Studio deployment)

`Affected repos: cianfhoghlaim + meaisinfhoghlaim + ciancheiltis + tuatha` (4 repos)

## Cost

- **Compute:** 0 — Unsloth Studio runs on the existing bunchloch M4 Max
- **Storage:** ~50 GB for the 4 new GGUF models (Gemma 4 4B + Qwen3-VL-8B) when downloaded
- **Fine-tuning:** Modal H100 for 2 fine-tunes (Gemma 4 + Qwen3-VL-8B) — ~$30-60 each
- **Infisical:** 1 new secret scope `ciancheiltis/duchas_api_key` for Dúchas IIIF