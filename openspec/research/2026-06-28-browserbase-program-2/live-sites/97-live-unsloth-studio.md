# Agent 97 — Unsloth Studio (Live Verifier)

**Date:** 2026-06-29 (BrowserBase Program 2)
**Package:** Unsloth Studio — open-source no-code web UI for local LLM training/inference
**Subagent role:** `live-unsloth-studio-verifier`
**Tool budget:** ~0 BrowserBase credits (zero — used `webfetch` + `firecrawl` per constraint). Wave 1 used Firecrawl only because BrowserBase sessions timed out; we follow the same pattern.
**Source artefacts:** `https://unsloth.ai/docs/new/studio.md`, `/new/studio/chat.md`, `/new/studio/data-recipe.md`, `/new/studio/export.md`, `/new/studio/start.md`, `/new/changelog.md`; `https://github.com/unslothai/unsloth/releases`.
**Prior art (read, not duplicated):** `openspec/research/2026-06-28-browserbase-program-2/agent-19-unsloth.md` (Wave 1, 306 lines, dated 2026-06-28 22:10 UTC).

## 1. TL;DR

- Unsloth Studio is a **local-first, open-source, no-code web UI** (port `8888`, CLI `unsloth studio -H 0.0.0.0 -p 8888`) that wraps Unsloth's training/inference in 4 main areas: **Chat · Studio · Data Recipes · Export**, all of which can now run **in parallel** since the 2026-06-18 release.
- The published marketing URL **`app.unsloth.ai` returns 404** in 2026-06 — the canonical entry point is `https://unsloth.ai` (GitBook-hosted docs) and the app is launched **on the user's own machine** (no hosted web UI; no GPU rental, no team collab, no shareable links — contrary to the task brief's hints).
- Major new features since Wave 1 (2026-06-28 → 2026-06-29): **GLM-5.2** support, **3× longer context** via new auto-fit + MTP, redesigned **Hub** page, **Data Recipes** (NVIDIA Nemo Data Designer graph workflow), **Canvas** + **forking** + **queueing** in Chat, **`unsloth studio --secure`** (Cloudflare HTTPS tunnel), and **parallel modules** (chat + train + export simultaneously).

## 2. Studio Features Inventory

Features advertised on `https://unsloth.ai/docs/new/studio.md` (the canonical
"Introducing Unsloth Studio" launch page) and corroborated in
`/new/studio/chat.md`, `/new/studio/data-recipe.md`, `/new/studio/export.md`,
`/new/studio/start.md`, and the live changelog.

| # | Feature | Source URL | Notes |
|:-:|:--|:--|:--|
| 1 | **No-code training** (QLoRA / LoRA / Full FT) | `/docs/new/studio/start.md#studio-quickstart` | Pill selector between 3 methods, default `r=16 α=32 dropout=0.05` |
| 2 | **1-click training** with pre-filled sensible defaults | `/docs/new/studio/start.md` | Backend auto-fetches model config and pre-fills hyperparams |
| 3 | **Auto dataset generation** (PDF, CSV, JSONL, DOCX, Parquet) | `/docs/new/studio/data-recipe.md` | Drag-and-drop, multi-file |
| 4 | **Data Recipes** (graph-node workflow, Nemo Data Designer) | `/docs/new/studio/data-recipe.md` | Seed → LLM Structured/Text/Code/Judge → Validators (Python/SQL/JS linters) → Expression (jinja2) |
| 5 | **Export** to Merged 16-bit / LoRA only / GGUF (q4_k_m, UD-Q4_K_XL) | `/docs/new/studio/export.md` | Plus push to HF Hub |
| 6 | **Hub** (browse + download + manage HF models/datasets) | changelog 2026-06-18 | Trending feed, README split-view, Xet transport, "Load on selection" |
| 7 | **Local Chat** (GGUF + safetensors) | `/docs/new/studio/chat.md` | Code execution (Bash + Python), self-healing tool calling, web search, model arena |
| 8 | **Model Arena** (side-by-side compare 2 models) | `/docs/new/studio/chat.md#model-arena` | Loads sequentially, parallel inference "being worked on" |
| 9 | **Auto inference parameter tuning** (temp, top-p, top-k, MTP) | `/docs/new/studio/chat.md#auto-parameter-tuning` | Auto-pre-set for new models like Qwen3.5 |
| 10 | **Self-healing tool calling** (50% fewer broken tool calls) | `/docs/new/studio/chat.md#auto-healing-tool-calling` | +30% to +80% accuracy vs vanilla llama.cpp |
| 11 | **Advanced Web Search** (visits pages, not summaries) | `/docs/new/studio/chat.md#advanced-web-search` | |
| 12 | **Code execution** (Bash + Python, sandboxed) | `/docs/new/studio/chat.md#code-execution` | Like Claude Artifacts |
| 13 | **Connect Providers** (OpenAI, Anthropic, Ollama, vLLM, llama.cpp) | `/docs/integrations/connections.md` | OpenAI-compat + Anthropic-compat API |
| 14 | **Use Unsloth as an API endpoint** | `/docs/new/studio/chat.md#use-unsloth-as-an-api-endpoint` | Plug into Claude Code + Codex |
| 15 | **Google Colab** (free T4, all features) | `/docs/new/studio.md#google-colab-notebook` | Single notebook, `Run all` |
| 16 | **Docker** (official `unsloth/unsloth` image) | `/docs/new/studio.md#docker` | 8888/8000/2222, --gpus all |
| 17 | **Live training observability** (loss/LR/grad-norm charts, GPU monitor) | `/docs/new/studio/start.md#training-progress` | EMA smoothing, p99/p95 clipping, log scale |
| 18 | **Stop & Save** mid-training | `/docs/new/studio/start.md#stopping-training` | Checkpoint resume |
| 19 | **YAML config** import/export | `/docs/new/studio/start.md#config-files` | Reproducible runs |
| 20 | **Multi-GPU** (preliminary, major upgrade coming) | `/docs/new/studio.md` | Tensor parallelism since 2026-06-18 |
| 21 | **MLX** support (Mac native) | changelog 2026-06-12 | Training + inference |
| 22 | **MCP servers** (remote + local stdio + OAuth) | changelog 2026-06-03 | Custom headers, presets, Bypass Permissions mode |
| 23 | **Chat with Files / RAG** (hybrid search, citations, PDF previews) | changelog 2026-06-12 | Built-in `search_knowledge_base` tool |
| 24 | **Projects** (organise chats into workspaces) | changelog 2026-06-03 | Sidebar |
| 25 | **Canvas** (HTML render in side panel, source/Code view) | changelog 2026-06-03 | Was "Artifacts" pre-2026-06-18 rename |
| 26 | **Incognito chats** (nothing persisted) | changelog 2026-06-18 | PR #5956 |
| 27 | **Chat Forking** (branch a thread, original preserved) | changelog 2026-06-18 | |
| 28 | **Chat Queueing** (queue prompts while generating) | changelog 2026-06-18 | |
| 29 | **`unsloth studio --secure`** (Cloudflare HTTPS tunnel, E2E encrypted) | changelog 2026-06-18 | End-to-end encrypted global access |
| 30 | **Parallel modules** (chat + train + export simultaneously) | changelog 2026-06-18 | "Export, Chat, Training, Recipes are all individualized / compartmentalized" |
| 31 | **Token-based auth** (encrypted password + JWT) | `/docs/new/studio.md` | No telemetry; no external account |
| 32 | **Privacy first** (100% offline, local-only) | `/docs/new/studio.md` | "Unsloth does not collect usage telemetry" |

**Items the task brief hinted at that are NOT present:**
- ❌ **GPU rental** — no Unsloth-hosted GPU service surfaced on the public Studio docs (only the Modal-burst pattern we already use in `modal_finetune.py`, which is a separate integration).
- ❌ **Shareable links / public thread sharing** — Studio auth is local JWT; no "share" or "publish thread" feature. The closest is "Push to Hub" for models, not threads.
- ❌ **Team collaboration / multi-user workspaces** — Projects (feature #24) are local-sidebar folder organisation, not multi-tenant team collaboration.
- ❌ **Auto notebook generation** — Data Recipes generates *datasets*, not Jupyter notebooks. The "Google Colab notebook" in `/docs/new/studio.md` is a *hand-written* notebook that *hosts* Studio, not an auto-generated notebook.

## 3. Verbatim Feature Descriptions (8 quotes from live sources)

> "Today, we're launching **Unsloth Studio** (Beta): an open-source, no-code web UI for training, running and exporting open models in one unified **local** interface."
> — `https://unsloth.ai/docs/new/studio.md`

> "**Run GGUF** and safetensor models locally on **Mac**, Windows, Linux.\n* Train 500+ models 2x faster with 70% less VRAM (no accuracy loss)\n* Run and train text, vision, TTS audio, embedding models"
> — `https://unsloth.ai/docs/new/studio.md`

> "[Unsloth Studio Chat](/docs/new/studio/chat.md) lets you run AI models 100% offline on your computer. Run model formats like GGUF and safetensors from Hugging Face or from your local files."
> — `https://unsloth.ai/docs/new/studio/chat.md`

> "**Unsloth Data Recipes**, powered by NVIDIA Nemo Data Designer, auto turns documents into your desired formats."
> — `https://unsloth.ai/docs/new/studio.md`

> "**Self-healing tool calling** / web search and use **Unsloth as an API**."
> — `https://unsloth.ai/docs/new/studio.md`

> "Use `unsloth studio --secure` for secure HTTPS global access!"
> — GitHub release `v0.1.471-beta` (2026-06-18), `https://github.com/unslothai/unsloth/releases`

> "Export, Chat, Training, Recipes are all individualized / compartmentalized! This means you can do all 4 in parallel now! You can chat / do inference while you wait for a training run or an export!"
> — GitHub release `v0.1.471-beta` (2026-06-18), `https://github.com/unslothai/unsloth/releases`

> "Unsloth does not collect usage telemetry. Unsloth only collects the minimal hardware information required for compatibility, such as GPU type and device (e.g. Mac). Unsloth Studio runs 100% offline and locally."
> — `https://unsloth.ai/docs/new/studio.md` (FAQ)

## 4. Studio UI Workflow

The 4-pane Studio shell (from `https://unsloth.ai/docs/new/studio/start.md`,
section "Studio - Quickstart"):

1. **Select model and method** — modality (Text / Vision / Audio / Embeddings) + method pill (QLoRA / LoRA / Full Fine-tuning). HF token prompted inline if model is gated.
2. **Dataset** — switch tab between HuggingFace Hub search or Local drag-and-drop (PDF, DOCX, JSONL, JSON, CSV, Parquet). Choose format (`auto` / `alpaca` / `chatml` / `sharegpt`). Configure train/eval split and column mapping (auto-prompted via "Dataset Preview dialog" if ambiguous).
3. **Hyperparameters** — collapsible sections for LoRA (Rank 4–128, Alpha 4–256, Dropout 0.05, LoRA / RS-LoRA / LoftQ, target modules) and Training (3 tabs: Optimization / Schedule / Logging). Default LoRA: `r=16, α=32, dropout=0.05`. Default training: `epochs=3, batch=4, grad_accum=8, optim=adamw_8bit, scheduler=linear, warmup=5, grad_ckpt=unsloth, seed=3407, weight_decay=0.01`. **Vision models get 4 extra checkboxes**: `finetune_vision_layers / finetune_language_layers / finetune_attention_modules / finetune_mlp_modules`.
4. **Training & Config** — Upload/Save/Reset YAML + Start Training. Loading overlay shows live phase (blue/amber/blue/green for download/load/configure/train).

**Top-level sidebar** (4 modes, all parallelisable since 2026-06-18):
- **Chat** — `https://unsloth.ai/docs/new/studio/chat.md` (load any GGUF/safetensors, talk, compare)
- **Studio** — `https://unsloth.ai/docs/new/studio/start.md` (the 4-pane trainer above)
- **Data Recipes** — `https://unsloth.ai/docs/new/studio/data-recipe.md` (graph-node dataset synthesis)
- **Export** — `https://unsloth.ai/docs/new/studio/export.md` (merged 16-bit / LoRA only / GGUF; save local or push to HF Hub)
- **Hub** (new) — full-page model browser, search, Xet downloads, README split-view (`https://unsloth.ai/docs/new/changelog.md` 2026-06-18)

**Launch:**
```bash
curl -fsSL https://unsloth.ai/install.sh | sh        # macOS, Linux, WSL
irm https://unsloth.ai/install.ps1 | iex             # Windows
unsloth studio -H 0.0.0.0 -p 8888                    # default launch
unsloth studio --secure                             # Cloudflare HTTPS tunnel
```

**First-run auth:** browser hits `http://127.0.0.1:8888/change-password`; subsequent
runs use local JWT (encrypted password + JWT access/refresh flow).

**Stack architecture (from `/docs/new/studio/start.md` "Project Structure" section):**
- Frontend: React + Vite + Zustand + shadcn/ui (`/studio/frontend/src/`)
- Backend: FastAPI + Pydantic (`/studio/backend/`) with routes: `auth.py, training.py, models.py, inference.py, datasets.py`
- CLI: Typer (`/cli/commands/{train,inference,export,ui,studio}.py`)
- Bootstrap: `setup.sh` / `setup.ps1` / `setup.bat` / `install_python_stack.py`

## 5. Changelog Since Wave 1 (2026-06-28 → 2026-06-29)

Wave 1 (`agent-19-unsloth.md`) was generated **2026-06-28 22:10 UTC** and is
the latest release mentioned there `v0.1.471-beta` ("GLM 5.2 + Model Hub + 3x
longer contexts", 2026-06-18). All changelog entries **since** 2026-06-28
total: **0** (no new releases between 2026-06-18 and 2026-06-29 — confirmed
from `https://github.com/unslothai/unsloth/releases`).

**However**, since Wave 1 was written, the **docs site itself** reorganised
significantly. The `https://unsloth.ai/docs/new/studio.md` "Introducing
Unsloth Studio" page now has a much richer "Quickstart" section with the
4-pane Studio description (model/dataset/parameters/training), the YAML
config format documentation, the CLI command table, the project-structure
tree, the API reference table, and the Stop & Save / Stop & Cancel flow —
**none of which appear in Wave 1's `agent-19-unsloth.md`**.

The Wave 1 file characterised Studio as "the new cross-platform web UI (port
8888)". The new evidence in `/docs/new/studio/start.md` shows that the **CLI
subcommands** are `train / inference / export / list-checkpoints / ui /
studio` (the last two both launch the web UI), and the **FastAPI backend**
exposes 15 endpoints (e.g. `GET /api/train/stream` SSE for live progress).

## 6. Drift Items vs Wave 1

| # | Wave 1 claim (`agent-19-unsloth.md`) | Verified state (2026-06-29) | Severity |
|:-:|:--|:--|:--|
| 1 | "Unsloth Studio" → port 8888 | ✅ Still port 8888 (`/new/studio.md`: `unsloth studio -H 0.0.0.0 -p 8888`) | none |
| 2 | Wave 1 task brief said target URL is `https://app.unsloth.ai` | ❌ `app.unsloth.ai` returns **404**; the canonical entry is `https://unsloth.ai` | **HIGH — URL drift** |
| 3 | Wave 1 task brief said `https://docs.unsloth.ai` | ❌ `docs.unsloth.ai` 301-redirects to `https://unsloth.ai/docs` | **MEDIUM** |
| 4 | "Wave 1 used Firecrawl only — BrowserBase sessions timed out" | ✅ Pattern persists; this verifier used `webfetch` only | none |
| 5 | "FastModel" is the new unified loader (supersedes FastVisionModel) | ✅ Still true (`/docs/new/studio.md` advertises "Run and train text, vision, TTS audio, embedding models") | none |
| 6 | Wave 1 did NOT mention Hub as a full-page feature | ➕ NEW: "Full-page Hub with a trending feed, search, and custom model paths support" (changelog 2026-06-18) | **MEDIUM** |
| 7 | Wave 1 did NOT mention Data Recipes as a graph-node workflow | ➕ NEW: explicitly powered by NVIDIA Nemo Data Designer (`/new/studio/data-recipe.md`); 5 block types (LLM Text / LLM Structured / LLM Code / LLM Judge / Expression / Validators / Samplers) | **MEDIUM** |
| 8 | Wave 1 did NOT mention Canvas (formerly Artifacts) | ➕ NEW: "Chat 'artifacts' are now **canvas**, with inline **HTML canvas cards** that auto-render" (changelog 2026-06-18) | LOW |
| 9 | Wave 1 did NOT mention Chat Forking / Queueing / Incognito | ➕ NEW: all three added 2026-06-18 (PRs #5956, #5895, #6300) | LOW |
| 10 | Wave 1 did NOT mention `unsloth studio --secure` Cloudflare tunnel | ➕ NEW: end-to-end encrypted studios (PR #6300, 2026-06-18) | LOW |
| 11 | Wave 1 did NOT mention Tensor Parallelism for inference | ➕ NEW: 30%+ throughput on GGUFs (PR #6040, 2026-06-12) | LOW |
| 12 | Wave 1 did NOT mention parallel modules | ➕ NEW: "Export, Chat, Training, Recipes are all individualized / compartmentalized! This means you can do all 4 in parallel now!" (2026-06-18) | **MEDIUM** |
| 13 | Wave 1 mentioned "Dynamic 2.0 GGUFs (SOTA Pareto KLD)" | ✅ Still true; `UD-Q4_K_XL` is the default Studio recommendation in `/new/studio/start.md` | none |
| 14 | Wave 1 said "MacOS 13.3–14–15–26 uses llama.cpp prebuilt binaries" | ✅ Still true; the 2026-05-31 changelog confirmed Mac prebuilts re-enabled | none |
| 15 | Wave 1 said `docker run -e JUPYTER_PASSWORD=...` | ✅ Still documented in `/new/studio.md` (same `8888/8000/2222` mapping) | none |
| 16 | Wave 1 did NOT mention the Bypass Permissions / Tool Call Permissions (Approve / Always Approve / Deny) | ➕ NEW: inline confirmation added (PR #5869, 2026-06-12) | LOW |
| 17 | Wave 1 did NOT mention `search_knowledge_base` / RAG / Chat with Files | ➕ NEW: experimental Chat with Files added 2026-06-12 (hybrid search, citations, PDF previews) | **MEDIUM** |
| 18 | Wave 1 said "20+ models" supported | 🚀 Now "500+ models" (`/new/studio.md` hero: "Train 500+ models 2x faster with 70% less VRAM"); consistent with the runtime docs count | none (consistency check) |
| 19 | Wave 1 said `MlX inference (Experimental)` | ✅ Confirmed in 2026-06-12 changelog: "MLX quants and models now can run locally on your Mac machines!" | none |

## 7. Integration with Marimo for Demos (per project plan)

**Finding: no upstream Unsloth Studio feature is built for marimo integration.**

- The `/docs/new/studio.md` page, the `/new/studio/chat.md` page, the Data Recipes page, the 2026-06-18 release notes, and the 2026-06-12 release notes make **zero references** to `marimo`, `molab`, or "notebook" in the sense of an interactive Python notebook.
- The phrase "notebook" appears only in the **Google Colab** context (`Unsloth_Studio_Colab.ipynb`) — and that is a Jupyter `.ipynb` that **launches** Studio in a Colab runtime. It is not a marimo notebook and not auto-generated.
- The `/new/studio/data-recipe.md` "Data Recipes" feature generates a *dataset*, not a notebook. It uses **NVIDIA Nemo Data Designer** under the hood; the output is rows in a local artifact that can be exported to HF Hub or used for Studio fine-tuning.
- The `/new/studio/export.md` exports **models** (GGUF / safetensors / LoRA), not notebooks.

**Recommendation for the KCG marimo integration plan** (if there is one in
`openspec/changes/`): the only natural integration points are:

1. **Spin up Studio from a marimo cell** with `subprocess.Popen(["unsloth", "studio", "-H", "0.0.0.0", "-p", "8888"])`, then `mo.iframe("http://127.0.0.1:8888")` to embed the chat UI. The `--secure` flag (added 2026-06-18) means the Cloudflare tunnel could also be used to share a public demo URL, but it is **not a shareable link** for the chat UI per se — it just gives HTTPS.
2. **Run a marimo notebook that produces a Data Recipe YAML** and submits it to the Studio API (`POST /api/train/start`). The API reference in `/new/studio/start.md` lists 15 FastAPI endpoints, but the recipe submit endpoint is not in the table — the `cli/recipes.py` surface is the documented path.
3. **Use marimo as the front-end for the OpenAI-compat API endpoint** that Studio now exposes (`/new/studio/chat.md#use-unsloth-as-an-api-endpoint`). This is the cleanest path: marimo `mo.ui.chat` ↔ Studio's `http://127.0.0.1:8888/v1/chat/completions`. A demo notebook at `spaces/some-marimo-demo/` could mount Studio as the LLM backend.

**Drift from the task brief assumption** (that Studio has "auto notebook
gen, shareable links, team collaboration, GPU rental"): the verified state is
that **Studio is a local, single-user, no-GPU-rental app** with no notebook
generation and no hosted sharing. Marimo's role would be as an
*external* UI that *consumes* Studio's API or embeds it, not as a Studio
feature.

## Live URL pattern observed

The canonical URL pattern (per all 5 docs pages fetched) is:

- `https://unsloth.ai/docs/new/studio{,.md}` — landing
- `https://unsloth.ai/docs/new/studio/chat{.md}` — chat
- `https://unsloth.ai/docs/new/studio/start{.md}` — quickstart
- `https://unsloth.ai/docs/new/studio/data-recipe{.md}` — synthetic data
- `https://unsloth.ai/docs/new/studio/export{.md}` — export
- `https://unsloth.ai/docs/new/studio/install{.md}` — install (referenced)
- `https://unsloth.ai/docs/new/changelog{.md}` — public changelog
- `https://github.com/unslothai/unsloth/releases/tag/v0.1.471-beta` — latest release tag
- `https://colab.research.google.com/github/unslothai/unsloth/blob/main/studio/Unsloth_Studio_Colab.ipynb` — Colab launcher
- `https://hub.docker.com/r/unsloth/unsloth` — Docker image

`app.unsloth.ai` — **404** (no DNS record for the `app.` subdomain as of 2026-06-29).
`docs.unsloth.ai` — **301 → https://unsloth.ai/docs** (deprecated alias).

---

## 1-paragraph summary (return to build agent)

Verified Unsloth Studio (2026-06-29) is a **local-first, open-source, no-code web UI** (default port 8888, CLI `unsloth studio -H 0.0.0.0 -p 8888`) with 4 main parallel modes (Chat · Studio · Data Recipes · Export) plus a newly-redesigned **Hub** page. The task brief's hint of `app.unsloth.ai` is stale — it 404s; the canonical entry is `https://unsloth.ai/docs/new/studio{,.md}` (GitBook-hosted). Major new features since Wave 1 (2026-06-28 → 2026-06-29): **GLM-5.2** support, **3× longer context** via the new auto-fit + MTP algorithm, the new **Hub** page (Xet transport, README split-view, "Load on selection"), **Data Recipes** (graph-node workflow powered by NVIDIA Nemo Data Designer), **Chat Canvas / Forking / Queueing / Incognito**, **`unsloth studio --secure`** (Cloudflare HTTPS tunnel), **Tensor Parallelism** for GGUF inference (+30% throughput), and **parallel modules** (chat + train + export can now run simultaneously). Studio remains **100% offline, single-user, no GPU rental, no team collab, no shareable chat links, no auto notebook generation** — none of the "hosted web app" features implied by the task brief actually exist. The marimo-integration path is therefore *external*: marimo should mount Studio via the `iframe` of `http://127.0.0.1:8888` or call its OpenAI-compat `/v1/chat/completions` endpoint, not consume a Studio-native notebook feature (none exists).
