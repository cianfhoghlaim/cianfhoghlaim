# Kings' College Galway || Coláiste na Déisigh

> *A unified Celtic education platform, infrastructure mesh, and AI research laboratory by Cian Mac an Déisigh Uí Liatháin.*

[![Polyglot](https://img.shields.io/badge/polyglot-bun_%2B_uv_%2B_turbo-blue)](#)
[![Dagster](https://img.shields.io/badge/dagster-228_assets-4B8BBE)](oideachais/)
[![AI Spend](https://img.shields.io/badge/AI_spend-%3C$25%2Fmonth-brightgreen)](#budget-ai-tooling)
[![License](https://img.shields.io/badge/license-BSL_1.1-green)](LICENSE.md)

---

## What This Is

A polyglot monorepo (`bun + uv + turbo`) that ingests the curriculums and exam papers of the British Isles, makes them interactive and bilingual through self-hosted AI, and serves as the personal research-and-deployment platform of Cian Mac an Déisigh Uí Liatháin. Eight cooperating streams:

| Stream | What it does | Stack | Status (2026-06-16) |
|:--|:--|:--|:--|
| [`oideachais/`](oideachais/) | Curriculum, exam, marking-scheme extraction; the VLM PDF pipeline; asset generation | Dagster + DLT + DuckLake + LanceDB + BAML + LiteLLM | **228 / 228** Dagster assets, **81 / 81** tests pass |
| [`meaisinfhoghlaim/`](meaisinfhoghlaim/) | Model lifecycle — HF cache, GGUF conversion, llama-swap dynamic model swapper; 12 specialised agents, 10 OCR models, 6 Celtic languages | llama-swap + llama.cpp + MLX + Bria FIBO | **4 / 4** heartbeat assets; 8-component skeleton |
| [`croilar/`](croilar/) | Multi-persona portfolio & reference implementation; DevTools Hub | Convex + Hono + TanStack + BetterAuth + Dagster + DLT | **25** assets wired; packaging fixed (#17); 5 stacks |
| [`tuatha/`](tuatha/) | Celtic Educational MMO + crypto platform; codeolas code-intelligence; crypteolas DeFi research | Babylon.js + Dagster + BAML + DLT + SpacetimeDB + x402 | **23** assets wired; sruth shim fix (#18) |
| [`cian_mac_an_déisigh_uí_liatháin/`](cian_mac_an_déisigh_uí_liatháin/) | Personal identity & credential vault: achievement, identity, teaching | PDFs + scanned records | TC registration, degrees, citizenship, disability evidence |
| [`leabharlann/`](leabharlann/) | Digital library: Zotero, Google Takeout, CocoIndex v1; Irish-language corpus | CocoIndex v1 + Zotero | CocoIndex v1 built with books/zotero/takeout sources |
| [`infrastructure/`](infrastructure/) | Multi-cloud zero-trust mesh; LLM gateway; ~50 stacks; team-workflow (n8n+Vikunja+cal-diy) | Pulumi + Komodo + Pangolin + Locket + Infisical + LiteLLM | 35 containers on bunchloch, ~10 on arm1-oci |
| [`docs/`](docs/) | Canonical reference corpus — skills, architecture, data-platform, AI/ML, Celtic, infra, web | markdown + notebooks | 15+ cross-dir duplicates removed; master routing table |

The **3-way interaction** that makes the engine work:

```
┌─────────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐
│  oideachais/        │    │  meaisinfhoghlaim/    │    │  infrastructure/     │
│  Dagster assets     │───>│  llama-swap :8080     │<───│  LiteLLM gateway     │
│  BAML extraction    │    │  mlx-omni :10240      │    │   :4000              │
│  Asset generation   │    │  invokeai :9090       │    │  Locket sidecar      │
│                     │    │  HF cache (124 GB)    │    │  Infisical vault     │
│                     │<───│  hub/ gguf/ mlx/      │───>│  Pangolin + PocketID │
└─────────────────────┘    └──────────────────────┘    └──────────────────────┘
```

- `oideachais/` **calls** LiteLLM gateway at `http://litellm:4000/v1` through `LiteLLMResource` (Dagster) and `client LiteLLM` (BAML).
- The gateway **routes** to `llama-swap` (GGUF), `mlx-omni` (MLX), `invokeai` (image), or cloud providers (Gemini, GLM, OpenAI, OpenCode Go).
- `meaisinfhoghlaim/` **feeds** backends with converted GGUF models and runs `llama-swap` on M4 Max 48GB with dynamic profiles (text/vision/image).
- `infrastructure/` **secures** connections with PocketID SSO + Pangolin; **observes** with Langfuse + MLflow + Prometheus; **injects** secrets via Locket.

---

## Quickstart

```bash
# 1. Install toolchain + hydrate secrets
bun run setup         # mise + bun + uv + infisical bootstrap

# 2. Bring up lakehouse + LLM gateway + backends
cd infrastructure/stacks/lakehouse && docker compose up -d
cd ../engineering/litellm    && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../../meaisinfhoghlaim     && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../../engineering/mlx-omni && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../../engineering/invokeai && docker compose -f compose.yaml -f sidecar.yaml up -d

# 3. Materialise model conversion (HF -> GGUF) once
cd oideachais && uv run dagster dev -m data_platform.dagster_defs.definitions
# -> http://localhost:3000 -> Jobs -> model_conversion -> Materialize

# 4. Run VLM PDF pipeline
USE_LOCAL_SCRAPES=true uv run python -c "
from oideachais.data_platform.agents.baml_integration import EnhancedBAMLExtractionPipeline
p = EnhancedBAMLExtractionPipeline(subject='mathematics', cycle='senior_cycle')
spec = p.extract_curriculum_specification(document_text=open('sample.txt').read())
print(spec.model_dump_json(indent=2))
"

# 5. Open marimo ops dashboard
uv run marimo edit notebooks/mission_control.py
```

The first model conversion takes hours (124 GB HF safetensors + ~30 GB GGUF output). Subsequent runs are incremental.

---

## Recommended Developer Environment

The full stack that powers day-to-day development across this monorepo is opinionated and tightly integrated. Every choice is made to (a) minimise the cost of a context switch between TypeScript, Python, infrastructure-as-code, and AI-agentic work, (b) keep monthly spend under $25, and (c) keep the developer one `cd` away from a fully hydrated, fully indexed, fully reproducible working copy.

### Pillar-by-pillar rationale

| Pillar | Role | Why we chose it |
|:--|:--|:--|
| **Visual Studio Code** | Primary editor | First-class TS + Python, native `tasks.json` / `.vscode/launch.json`, integrates natively with `mise`, `bun`, `uv`, the OpenCode companion, and the LiteLLM gateway. Single UI for editing code, running Dagster assets in the integrated terminal, browsing marimo notebooks, and chatting with the OpenCode subagents. |
| **bun** | TS runtime, package manager, script runner | One tool replaces `node` + `npm` + `yarn` + `pnpm` + `npx` + `tsx`. Powers workspace orchestration, secret sync, OpenSpec, the `ccc` index, the dagster / komodo / pangolin glue, and every BAML codegen step. `bun run setup` is the canonical onboarding entry point. |
| **uv** | Python package manager + workspace manager | Replaces `pip` + `poetry` + `pyenv` + `virtualenv`. Native PEP 723, lockfile, and uv-workspace member resolution. Drives the five `members` of the `pyproject.toml` workspace (`oideachais`, `tuath`, `códeolas`, `sruth-browser`, `mcpo`) and every `uv run …` entry point. |
| **mise** | Polyglot toolchain + task runner | Pins `python 3.13`, `uv`, `bun`, `dagger`, `pulumi`, `duckdb`, `sops`, `opencode`, and friends in a single `mise.toml`. Directory hooks auto-export `.env` and the workspace `PYTHONPATH` on every `cd`, so the shell is always the same shape as the editor. |
| **HuggingFace GGUF** | Local model format | Q4_K_M quantised GGUFs are small (≈ 4-6 GB per 7 B model) and run on the M4 Max 48 GB via `llama-swap`. Cache lives at `stedding/huggingface/{hub,gguf,mlx}/`; 28 models, 124 GB safetensors + 30 GB GGUF + 15 GB MLX. |
| **LiteLLM** | OpenAI-compatible LLM gateway | One URL (`http://litellm:4000/v1`) routes to local GGUF (`llama-swap`), local MLX (`mlx-omni`), local image (`invokeai`), and cloud providers (Gemini, GLM, OpenAI, OpenCode Go). Every BAML function, every Dagster asset, every marimo cell, every n8n workflow calls an *alias* — never a provider id. |
| **OpenCode** | AI coding agent / IDE companion | Speaks the same OpenAI-compatible protocol as LiteLLM. Runs as a VS Code companion or a standalone CLI. Dispatches to five specialised subagents (`explorer`, `data-engineer`, `ai-engineer`, `frontend-dev`, `devops-architect`) defined in `opencode.json`. |
| **OpenChamber** | Rich GUI / web / PWA front-end for OpenCode | [OpenChamber](https://github.com/openchamber/openchamber) (⭐ 5.4 k, 1.7 k+ commits, 111 releases — current `v1.13.1`) wraps the OpenCode CLI in a polished UI available as a [VS Code extension (`FedaykinDev.openchamber`)](https://marketplace.visualstudio.com/items?itemName=FedaykinDev.openchamber) (13 k+ installs), a macOS / Windows desktop app, and a self-hostable Web / PWA reachable over LAN, Tailscale, or a Cloudflare tunnel. It is the recommended way to *use* the OpenCode row above when the developer prefers GUI workflows: branchable chat timeline with `/undo` and `/redo`, smart tool UIs for diffs / file ops / permissions, voice mode, multi-agent parallel runs in isolated worktrees, GitHub-native flows (start sessions from issues and PRs), inline comment drafts on diffs, integrated terminal, 18+ built-in themes, and a Skills catalog. The OpenChamber VS Code extension adds editor-native niceties — Agent Manager for parallel multi-model runs, right-click *Add to Context / Explain / Improve*, click-to-open file paths, theme-aware panels — without replacing the OpenCode companion itself, so the five subagents in `opencode.json` remain dispatchable from inside the editor. Installation: `code --install-extension FedaykinDev.openchamber`, or download the desktop app from the [OpenChamber releases page](https://github.com/openchamber/openchamber/releases). |
| **OpenCode Go** | Cloud LLM backbone behind OpenCode | One flat-rate API exposes the full model lineup (`deepseek-v4-pro`, `deepseek-v4-flash`, `kimi-k2.6`, `glm-5.1`, `minimax-m2.5`, `qwen-3.7-max`) at a single base URL. The whole n8n LLM backbone uses it via `$OPENAI_BASE_URL/chat/completions`. |
| **MiniMax M3 coding plan** | Subscription that unlocks frontier M3 reasoning | The newest member of the model lineup. Used for the hardest, multi-step, long-context coding tasks — 20-file refactors, dependency-graph reasoning over a Dagster code-location, full-repo PR review, anything where the planner needs a million-token window. |
| **DeepSeek V4 Pro API key** | Direct provider access | Bypasses the OpenCode Go rate limit when a subagent needs sustained high throughput (e.g. BAML `extract` fanning out to 800+ SEC exam papers in a single run). The key is hydrated through Infisical and exposed as `DEEPSEEK_API_KEY` in the container env. |

### How they fit together

```
┌────────────────────────────┐    ┌──────────────────────────────┐    ┌──────────────────────────────┐
│  Visual Studio Code        │    │  OpenCode (agent)            │    │  OpenCode Go API             │
│  ── editor + tasks         │───>│  ── sub-agent dispatcher     │───>│  ── 6-model lineup           │
│  ── integrated terminal    │    │  ── explorer / data / ai /   │    │  ── minimax m3 coding plan   │
│  ── debug + MCP clients    │    │     frontend / devops        │    │  ── deepseek-v4-pro direct   │
└──────────────┬─────────────┘    └──────────────┬───────────────┘    └──────────────┬───────────────┘
               │                                │                                 │
               │ mise → bun / uv                │ chat/completions                │
               ▼                                ▼                                 ▼
┌────────────────────────────┐    ┌──────────────────────────────┐    ┌──────────────────────────────┐
│  mise.toml toolchain       │    │  LiteLLM gateway :4000       │    │  HuggingFace GGUF cache      │
│  python 3.13, bun, uv,     │    │  ── llama-swap :8080 (GGUF)  │◀───│  stedding/huggingface/       │
│  dagger, pulumi, opencode  │    │  ── mlx-omni :10240 (MLX)    │    │  hub/  gguf/  mlx/           │
│  ── dir hooks + tasks      │    │  ── OpenCode Go passthrough  │    │  28 models, ~124 GB safetensors│
└────────────────────────────┘    └──────────────────────────────┘    └──────────────────────────────┘
```

### One-time setup

```bash
# 1. Install the toolchain (mise pins every version)
mise install

# 2. Install TS + Python dependencies
bun install
uv sync

# 3. Hydrate secrets from Infisical
#    (.env is written here; mise directory hooks keep it in sync on every cd)
bun run secrets:env
bun run secrets:init

# 4. Start the local LLM gateway + HF GGUF swapper
cd infrastructure/stacks/litellm    && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../meaisinfhoghlaim                          && docker compose -f compose.yaml -f sidecar.yaml up -d

# 5. Materialise model conversion (HF safetensors -> Q4_K_M GGUF) once
cd oideachais && uv run dagster dev -m data_platform.dagster_defs.definitions
# -> http://localhost:3000 -> Jobs -> model_conversion -> Materialize
```

### The VS Code experience

- **`.vscode/`** holds `settings.json`, `tasks.json`, and `launch.json` that point at the *mise-managed* binaries (`bun`, `uv`, `python 3.13`, `opencode`) — the editor and the terminal therefore always resolve to the same interpreter and runtime, eliminating the "works in the editor, fails in CI" class of bugs.
- **MCP clients** (Browserbase, Firecrawl, MotherDuck, Cocoindex-Code, Cognee, Graphiti, Langfuse) are wired through `opencode.json` and are equally usable inside VS Code via the OpenCode companion — so `mcp__motherduck__execute_query` works the same way whether you call it from a chat, a notebook, or a BAML prompt.
- **Tasks** for `bun run setup`, `mise turbo dev`, `mise dagster:oideachais`, `mise ccc:index`, `mise spec:validate …` are exposed as one-click VS Code tasks. The Turborepo graph (`build`, `dev`, `typecheck`, `lint`, `format`, `test`) is reachable through `mise turbo <task>`.
- **Debugging** uses Python `debugpy` for Dagster assets, Bun `--inspect` for root scripts, and `tsx` for the BAML client; all three are configured in `launch.json` with launch profiles per workspace.

### Why a single gateway

Every BAML function, every Dagster asset, every marimo cell, every n8n workflow, and every OpenCode subagent call the same URL: `http://litellm:4000/v1`. The gateway decides whether a request hits a local GGUF (free, private, low latency) or a cloud model (paid, frontier). The application code never knows — it just asks for an *alias* like `extract`, `vision`, `irish`, `general`, and LiteLLM resolves the `primary -> fallback` chain.

This is what makes the **MiniMax M3 coding plan** and the **DeepSeek V4 Pro key** interchangeable from the application's point of view: both are exposed as aliases, both fail over gracefully, and both are rate-limit aware via Langfuse. If the M3 plan is exhausted, the alias falls through to DeepSeek V4 Pro; if DeepSeek is rate-limited, the alias falls through to GLM 5.1; if every cloud is down, it falls through to the local GGUF. The same code path serves all four cases.

### Why bun + uv + mise

The three tools each own a clean horizontal slice and they do not overlap:

- **mise** owns *which versions* of every binary are on `PATH` (including binaries it does not manage, via `[env]` blocks). It also owns the *task* surface — `mise turbo dev`, `mise ccc:search …`, `mise dagster:oideachais`, `mise spec:validate …`, `mise secrets:init`, etc.
- **bun** owns the *TypeScript graph* — the root orchestration scripts, the three `workspaces` (`oideachais-web`, `oideachais-mcp-filesystem`, `tuatha-ui`), secret sync, OpenSpec, `ccc`, the dagster / komodo / pangolin glue, and every `bunx` invocation of the MCP servers.
- **uv** owns the *Python graph* — the five uv-workspace members, the lockfile, the venvs, the `uv run …` entry points, and PEP 723 inline scripts. A developer never has to activate a venv manually: `uv run` resolves to the workspace venv, and mise injects `PYTHONPATH` and `VIRTUAL_ENV` so that `python` in a terminal lands in the same interpreter VS Code uses.

### Why HuggingFace GGUF specifically

- **Privacy.** OCR, vision, Irish generation, and curriculum embeddings run locally; raw PDFs and student work never leave the laptop. The HF safetensors are checksum-pinned in `meaisínfhoghlaim/`, the GGUF conversions are reproducible Dagster assets, and the swap profiles are deterministic.
- **Cost.** Once a Q4_K_M GGUF is in `stedding/huggingface/gguf/`, every subsequent request is free, and we can serve thousands of pages per day for under $0.001 in electricity. The only recurring AI spend is for the *cloud* aliases that GGUF cannot cover (frontier reasoning, the M3 coding plan, the DeepSeek V4 Pro key).
- **Latency.** On M4 Max 48 GB the Qwen2.5-VL-7B vision model returns in ≈ 250 ms per page — faster than a network round-trip to any cloud VLM. The `text`, `vision`, and `image` profiles in `llama-swap` keep one model resident at a time and hot-swap when the alias changes.
- **Quantisation flexibility.** Q4_K_M, Q5_K_M, Q8_0, and f16 variants sit side by side; `llama-swap` picks the right one for the alias and the request.
- **No vendor lock-in.** GGUFs are an open format, the conversion code is open-source, and the entire HF -> GGUF pipeline is a Dagster asset (`hf_models_downloaded -> gguf_*`), so a fresh machine can reproduce the full cache in hours.

### Why a coding plan matters

A **coding plan** is a flat-rate subscription that gives the developer a guaranteed monthly token budget against a specific frontier model. We pair two:

- **MiniMax M3 coding plan** — long-context (1 M+ tokens), deep multi-step reasoning, the model used when an OpenCode subagent has to plan a 20-file refactor, trace a graph-of-thought through a Dagster dependency graph, or hold an entire PR review in context. M3 is the planner-of-last-resort; when an alias asks for `general` and the chain is exhausted, M3 takes over.
- **DeepSeek V4 Pro API key** — direct provider access, used when the subagent throughput spikes (BAML `extract` fanning out to 800+ SEC exam papers in a single run) and we need to bypass the OpenCode Go rate limit. The key is hydrated through Infisical and exposed as `DEEPSEEK_API_KEY` in the container env, so any container, any Dagster asset, any subagent can pick it up without code changes.

Both are referenced from `opencode.json` and from the LiteLLM aliases so the same alias (`extract`, `general`, `ai-engineer`) can fall back from one to the other without code changes — and the LiteLLM gateway, the OpenCode dispatcher, and the BAML client all converge on the same URL.

### Closed-source models — our position

For workloads that require a *closed-source* provider — frontier reasoning, multimodal safety pipelines, regulated British Isles data flows, classroom and child-facing surfaces — our internal research in [`leabharlann/gemini_deep_research/technology/`](leabharlann/gemini_deep_research/technology/) concludes that the **British DeepMind** lineage and the associated **Gemini** family are **by far the most secure and feature-rich option in the closed-source ecosystem** — especially for developers, schools, public-sector teams, and families in the British Isles who care about **data privacy, child safety, and alignment with UK / EU regulatory frameworks**. The local HF GGUF stack is still the *first* line of defence (privacy by architecture, not by policy), but when a closed-source model is unavoidable, our policy is **Gemini-first**.

The position is documented across six deep-research reports that the developer is expected to read before changing the closed-source default:

| Report | What it underwrites |
|:--|:--|
| [`gemini_pro_for_public_safety.pdf`](leabharlann/gemini_deep_research/technology/gemini_pro_for_public_safety.pdf) | The Gemini Pro deployment profile we default to for **child-facing** and **public-safety** surfaces (schools, classroom tutors, junior-cycle, primary, KS1-KS4), including the content-filter and refusal-tuning posture. |
| [`gemini_s_safety_privacy_and_origins.pdf`](leabharlann/gemini_deep_research/technology/gemini_s_safety_privacy_and_origins.pdf) | Safety and privacy architecture of Gemini, with explicit attention to **DeepMind's British provenance** and the safety-research lineage that pre-dates the Google acquisition. |
| [`google_s_ai_regulation_and_competitors.pdf`](leabharlann/gemini_deep_research/technology/google_s_ai_regulation_and_competitors.pdf) | Comparative regulatory analysis: how Gemini's UK / EU regulatory engagement compares against US-only and PRC-origin closed-source competitors. |
| [`ai_company_analysis_financial_technical_corporate.pdf`](leabharlann/gemini_deep_research/technology/ai_company_analysis_financial_technical_corporate.pdf) | Financial, technical, and corporate analysis of the major AI labs — the evidence base for the "by far the most secure and feature-rich" assessment. |
| [`regulating_big_tech_in_british_isles.pdf`](leabharlann/gemini_deep_research/technology/regulating_big_tech_in_british_isles.pdf) | UK / Ireland regulatory landscape; explains why a British-origin lab with strong UK regulatory engagement is the lower-friction choice for British Isles deployments. |
| [`us_tech_infiltration_and_uk_ireland_defense.pdf`](leabharlann/gemini_deep_research/technology/us_tech_infiltration_and_uk_ireland_defense.pdf) | Defensive posture: threat-modelling US-only and PRC-origin closed-source providers, and the case for routing regulated British Isles data through a British-origin lab wherever possible. |

In practice this translates into four concrete dev-environment rules:

1. **Default ordering.** When the LiteLLM aliases `extract`, `vision`, `document`, and `general` resolve to a closed-source model, the primary in the chain is a **Gemini** model (e.g. `gemini-2.5-pro`, `gemini-2.5-flash`). OpenCode Go and DeepSeek V4 Pro are fallbacks; MiniMax M3 / `minimax-m2.5` are fallbacks; the local Q4_K_M GGUF is the always-on last resort. Gemini-first is policy, not coincidence.
2. **Child-facing surfaces.** Any deployment that touches a **child-facing** surface — school, classroom, junior-cycle, primary, KS1-KS4, tutor chatbots, formative-assessment flows, the CopilotKit tutor on `oideachais-web` — routes through the **Gemini Pro public-safety profile** documented in `gemini_pro_for_public_safety.pdf`, with the content filters and refusal-tuning that report specifies.
3. **Regulated British Isles data.** Any deployment that touches **regulated British Isles data** — NHS, DEIS schools, Teaching Council of Ireland, courts, citizens information, primary-source exam papers from SEC / NCCA / CCEA / SQA / WJEC — prefers Gemini over US-only or PRC-origin competitors for the reasons outlined in `regulating_big_tech_in_british_isles.pdf` and `us_tech_infiltration_and_uk_ireland_defense.pdf`.
4. **Local-first never goes away.** The local HF GGUF stack remains the *first* line of defence (privacy by architecture, not by policy). The OpenCode Go + MiniMax M3 coding plan + DeepSeek V4 Pro key is the *coding* backbone. **Gemini is the closed-source default, not a replacement** for either layer.

This is the stack that ships: VS Code + `mise` + `bun` + `uv` + OpenCode + OpenCode Go + the MiniMax M3 coding plan + the DeepSeek V4 Pro API key + the local HF GGUF cache behind LiteLLM, **with Gemini as the closed-source default** for the workloads that the open-source local stack cannot cover and where British Isles privacy and child safety are non-negotiable.

### Daily loop

```bash
# Pull the latest, run quality gates
git pull --rebase
mise turbo dev              # boots lakehouse + litellm + llama-swap + mlx-omni
uv run pytest -q
bun run lint

# Pick a ticket
gh issue view 142
mise turbo task ai-engineer # or open the issue in VS Code and let OpenCode triage

# Open a PR
git checkout -b feat/issue-142
# ... edit ...
mise turbo test && mise turbo lint
gh pr create --fill
```

The first time a developer runs this loop, the M4 Max fans up as `llama-swap` loads a Q4_K_M GGUF, the LiteLLM gateway warms its alias cache, the OpenCode Go API auths the M3 coding plan, and OpenCode is already talking to `deepseek-v4-pro` for the `explorer` subagent and to `minimax-m2.5` (or `m3` on the M3 coding plan) for the hardest planner. By the second run, everything is in cache and the cold-start is under five seconds.

---

## Monorepo Topology (v2 — Polyglot)

Two language graphs orchestrated by `turbo.json` and a single `mise.toml`.

### TypeScript (bun workspaces)

| Workspace | Path | Purpose |
|:--|:--|:--|
| `oideachais-web` | `oideachais/web/` | TanStack Start + React front-end |
| `oideachais-mcp-filesystem` | `oideachais/mcp/filesystem/` | Filesystem MCP server |
| `tuatha-ui` | `tuatha/ui/` | Tuatha educational MMO front-end |

### Python (uv workspaces)

| Member | Path | Purpose |
|:--|:--|:--|
| `oideachais` | `oideachais/` | Celtic education data platform (Dagster, DLT, LanceDB) |
| `tuath` | `tuatha/` | Educational MMO + crypto (Babylon.js, SIWE, x402) |
| `codeolas` | `codeolas/` | Code intelligence library (publishable) |
| `meaisinfhoghlaim` | `meaisinfhoghlaim/` | AI/ML model lifecycle & Celtic NLP |
| `croilar` | `croilar/` | Multi-persona portfolio & DevTools Hub |
| `sruth-browser` | `infrastructure/browser/` | Browser automation (Stagehand, MCP) |
| `mcpo` | `oideachais/mcp/mcpo/` | MCPO bridge |

### One command to onboard

```bash
bun run setup  # mise install && bun install && uv sync && bun run secrets:env && bun run secrets:init
```

---

## LLM Gateway — the Heart of the System

Every LLM call flows through one URL: `http://litellm:4000/v1`. The gateway exposes 16 alias routes:

| Alias | Primary -> Fallback | Used by |
|:--|:--|:--|
| `extract` | gemini-2.5-pro -> glm-4.6 -> gemini-2.5-flash | BAML extraction (10 functions) |
| `vision` | local qwen25-vl GGUF -> gemma3-vision -> gemini-2.5-flash | VLM PDF processing |
| `document` | local granite-docling MLX -> qwen25-vl | PDF -> DocTags XML |
| `ocr` | local olmocr MLX -> deepseek-ocr GGUF -> gemini-2.5-flash | SEC exam paper OCR |
| `math` | local qwen25-math GGUF -> glm-4.6 | Math reasoning |
| `irish` | local UCCIX 13B -> qwen25-math -> gemini-2.5-flash | Irish text generation |
| `image` | local z-image-turbo GGUF -> qwen-image -> flux2 -> sdxl | Study asset image gen |
| `image-fibo` | local Bria FIBO MLX -> z-image-turbo | Deterministic JSON image gen |
| `embedding-curriculum` | celtic bge-m3 HF passthrough | Curriculum vector search |
| `general` | opencode-go deepseek-v4-flash -> glm-4.6 -> gpt-4o-mini | Cheap generic tasks |
| `whisper-irish` | celtic whisper-large HF passthrough | ASR |
| `translation` | celtic nllb HF passthrough | 200-language translation |

Full registry: `infrastructure/stacks/litellm/config/config.yaml`.

### Why a gateway

- **One OpenAI-compatible URL** — every consumer writes identical code.
- **No direct provider SDKs** — all BAML uses `client LiteLLM`.
- **Fallback chains** — UCCIX 13B before Gemini Flash for Irish.
- **Local-first by default** — OCR/vision start on local MLX/GGUF.
- **Langfuse + MLflow** — full lineage without per-callsite instrumentation.
- **PocketID SSO + Pangolin** — exposed only to authenticated Member roles.

---

## Oideachais — the Lakehouse Engine

228 Dagster assets across 4 layer groups:

| Group | Assets | Example |
|:--|:--|:--|
| **Ingestion** | curriculum/{cycle}, uk_education, multi_nation | DLT -> DuckDB / DuckLake |
| **Materials** | exam_materials/{cycle}, pdf_assets | SEC scraper -> Garage S3 -> ColPali OCR |
| **Model lifecycle** | hf_models_downloaded, gguf_* (10) | HF -> GGUF for llama-swap |
| **Asset generation** | image_prompts -> fibo_configs -> rendered -> published | BAML -> gateway -> Garage S3 |

### Recent milestones

| Milestone | What shipped |
|:--|:--|
| SourceFactory Phase 5 | 3 runtime constructors wired (source, dlt_asset, dagster_asset), closes #20 |
| Lateralise Phase 3.3 | 6 UK medicine + 4 UK law DLT sources as Dagster assets |
| Lateralise Phase 3.4 | 3 marimo dashboards |
| Lateralise Phase 3.5 | domain x nation x table reader |
| Lateralise Phase 3.6 | Crown-dependency DLT sources + assets (IOM/JEY/GGY) |
| Per-area READMEs | STATUS + REFACTORING + per-area READMEs + stack overview |

Full details: [`oideachais/README.md`](oideachais/README.md) — data contracts, asset topology, DLT patterns.

---

## Meaisinfhoghlaim — the AI/ML Quadrant

Eight integrated components feeding models and agents into the lakehouse:

| Component | Purpose | Status |
|:--|:--|:--|
| **AI Agents** | 12 specialised agents (curriculum, translation, corpus, research, geospatial, voice) | Functional |
| **OCR / HTR** | 10 OCR models across 6 backends with Irish-specific metrics | Functional |
| **Celtic Language Data** | DLT sources for Duchas, Canuint, Tearma, Gaois + 6-language cognate DB | Functional |
| **ML Pipelines** | Irish document scanner, dialect classifier, transcript aligner, LLM router | Functional |
| **Text Alignment** | Sentence-level Irish<->English aligner, ColPali visual aligner, G2P | Functional |
| **RAG Evaluation** | RAGAS: baseline 65.2% -> agentic 87.9% (+22.7pp) | Functional |
| **Content Quality** | Curriculum quality + completeness + audio validation | Functional |
| **Model & Data Catalog** | 13 models + 16 data sources + 3 training mixes | Functional |

### Local model lifecycle

```
stedding/huggingface/
├── hub/   # HF safetensors, 28 models ~124 GB
├── gguf/  # Converted Q4_K_M GGUFs ~30 GB
└── mlx/   # Converted MLX ~15 GB
```

Three swap profiles (one model resident at a time on M4 Max 48GB):

| Profile | Models |
|:--|:--|
| `text` | Qwen2.5-Math-7B, UCCIX Llama2-13B, Gemma-2-9B |
| `vision` | Qwen2.5-VL-7B + mmproj f16, Gemma-3-Vision, DeepSeek-OCR |
| `image` | Z-Image-Turbo, Qwen-Image, Qwen-Image-Edit-2511, FLUX.2-dev |

Full details: [`meaisinfhoghlaim/README.md`](meaisinfhoghlaim/README.md).

---

## Croilar — Multi-Persona Portfolio & DevTools Hub

The canonical reference implementation. Combines public-facing persona-aware portfolio with self-hosted developer platform and typed end-to-end pipelines.

| Surface | Stack | Status |
|:--|:--|:--|
| Public persona sites | TanStack Start + BetterAuth + Tailwind | N personas, EN+GA, per-persona themes |
| Data pipelines | DLT + DuckLake + BAML | 12 DLT pipelines (artwork, cv, github, spotify, …) |
| Admin portal | TanStack + Marimo + MotherDuck | Live dashboards + agent runtime |
| DevTools Hub | Convex + Hono + TanStack | Reference implementation |

Packaging fixed (#17 closed), 25 assets wired, 5 user-named stacks. Full details: [`croilar/README.md`](croilar/README.md).

---

## Tuatha — Celtic Educational MMO + Crypto Platform

Four cooperating streams under `tuath` uv workspace:

| Stream | What it does | Stack |
|:--|:--|:--|
| **Celtic Educational MMO** | Curriculum + mythology + Babylon.js + Rust+SpacetimeDB backend | Babylon.js + Dagster + BAML + DLT + SpacetimeDB + x402 |
| **codeolas** | Code-analysis library: semantic search, AST KG, MCP server | LanceDB + tree-sitter + BGE-M3 + Dagster + MCP |
| **crypteolas** | GitHub ingestion, DeFi research, KG construction, AgentOS | DLT + CocoIndex + Cognee + Graphiti + Memgraph + FalkorDB |
| **crypteolas_demo** | TanStack Start frontend, Agno agents, Gradio FIBO, Foundry | TanStack + Bun + Agno + Gradio + BAML + Foundry |

Sruth shim fix (#18 closed), 23 assets wired, 7+ DLT sources. Full details: [`tuatha/README.md`](tuatha/README.md).

---

## Cian Mac an Deisigh Ui Liathain — Personal Vault

The author's identity and credential archive:

| Directory | Contents |
|:--|:--|
| [`achievement/`](cian_mac_an_déisigh_uí_liatháin/achievement/) | Academic transcripts, parchments, Apple award, cybersecurity reference, Irish results |
| [`identity/`](cian_mac_an_déisigh_uí_liatháin/identity/) | Birth certs, dual-citizenship (ROI/UK), passports, family memorials, disability evidence (CPTSD) |
| [`teaching/`](cian_mac_an_déisigh_uí_liatháin/teaching/) | TC registration (roll 241571), placement references, Junior/Leaving Cert, BCS PGCE Scholarship |

Teaching Council registration: Mathematics & Applied Mathematics, Route 2 Post-Primary, Droichead conditions. See [Personal Foundation](#personal-foundation).

---

## Leabharlann — Digital Library

| Subdirectory | Contents |
|:--|:--|
| `aigne/` | Cognitive science & AI research |
| `gaeilge/` | Irish-language corpus: literature, folklore, linguistic resources |
| `gemini_deep_research/` | Deep research outputs (legal, regulatory, academic) |
| `ollscoil_na_gaillimhe/` | University of Galway coursework |
| `zotero/` | Zotero reference database |

CocoIndex v1 built with books, Zotero, and Google Takeout sources.

---

## Infrastructure Mesh

### Server fleet

| Server | Hardware | Role |
|:--|:--|:--|
| `arm1-oci` | Oracle Ampere A1, 4 OCPU, 24 GB | Control plane — Pangolin, Komodo, Garage S3 |
| `cax41-hetzner` | Hetzner CAX41 ARM, 16 vCPU, 32 GB | Workloads — Memgraph, FalkorDB, MLflow, Langfuse |
| `bunchloch` | MacBook M4 Max, 14c, 48 GB | Dev + analytics — llama-swap, mlx-omni, Bria FIBO |

### Gold-Standard stack (5 files per stack)

```
compose.yaml    # App services
sidecar.yaml    # Locket sidecar
secrets.env     # infisical:// URIs
pangolin.yaml   # Traefik + PocketID
blueprint.yaml  # Pangolin resource
```

### Key stacks

| Stack | Port | Purpose |
|:--|:-:|:--|
| `litellm` | 4000 | LLM gateway |
| `llama-swap` | 8080 | GGUF model swapper (M4) |
| `mlx-omni` | 10240 | MLX OpenAI server (M4) |
| `invokeai` | 9090 | SDXL image gen |
| `langfuse` | 3000 | LLM tracing |
| `mlflow` | 5000 | ML experiment tracking |
| `lakehouse` | 3900-3904 | Garage S3 + Lakekeeper + Lance |
| `cognee` | 8000 | AI memory (Neo4j, Memgraph) |
| `graphiti` | 8080 | Temporal knowledge graph |

### Team workflow stack

| Service | Domain | What it does |
|:--|:--|:--|
| n8n | `n8n.cianfhoghlaim.ie` | Visual workflow + LLM pipelines |
| Vikunja | `vikunja.cianfhoghlaim.ie` | Kanban + Gantt + team sharing |
| cal-diy | `calcom.cianfhoghlaim.ie` | Team + per-member booking |

6 seeded n8n workflows: daily-briefing, email-triage, booking-to-vikunja, followup-drafter, weekly-summary, stale-task-nudger.

### Secret flow

```
Infisical vault "dev-baile"   <- source of truth
       |  mise hook
Root .env (gitignored)        <- hydrated at runtime
       |  init-vault.ts
.infisical.env (committed)    <- infisical:// URIs
       |  Locket sidecar
/run/secrets/locket/secrets.env (tmpfs)
       |
Container env (read-only)
```

---

## Documentation Corpus

The [`docs/`](docs/) tree has 7 numbered domain directories with master routing at [`docs/00_index.md`](docs/00_index.md). Recent refactoring deduplicated 15+ cross-directory duplicates.

| Domain | Directory |
|:--|:--|
| Core, Deploy Plans, Package Ecosystem | `00-core/`, `00-deploy-plans/`, `00-package-ecosystem/` |
| Cognee, Patterns, Platform Architecture | `01-cognee/`, `01-patterns/`, `01-platform-architecture/` |
| Architecture, Audit, Data Platform | `02-architecture/`, `02-audit/`, `02-data-platform/` |
| Agents, Pipelines | `03-agents/`, `03-pipelines/` |
| AI/ML | `04-ai-ml/` |
| Celtic Language, Web | `05-celtic-language/`, `05-web/` |
| Infrastructure, Product | `06-infrastructure/`, `06-product/` |
| Skills, Standards | `07-skills/`, `07-standards/` |
| Examples | `08-examples/` |

---

## Multi-Agent Configuration

`opencode.json` defines 5 sub-agents:

| Agent | Model | Focus |
|:--|:--|:--|
| `explorer` | DeepSeek V4 Flash | Codebase search, context mapping |
| `data-engineer` | Qwen 3.7 Max | Dagster, DLT, DuckDB, MotherDuck, LanceDB |
| `ai-engineer` | DeepSeek V4 Pro | BAML, LiteLLM, OCR, Graphiti, Celtic AI |
| `frontend-dev` | Kimi K2.6 | TanStack Start, Convex, Marimo, canvas design |
| `devops-architect` | GLM 5.1 | Docker Compose, Komodo, Pangolin, Pulumi |

The `.agents/skills/` library holds 70+ skill definitions.

---

## Budget AI Tooling — $0-25/month

Architected for free and near-free infrastructure.

### OpenCode Go — 6 models, one flat rate

| Model | Used by | Profile |
|:--|:--|:--|
| `deepseek-v4-pro` | ai-engineer, extract alias | Frontier reasoning, BAML, Celtic NLP |
| `deepseek-v4-flash` | explorer, general alias | High-volume cheap tasks |
| `kimi-k2.6` | frontend-dev | React/TanStack/Marimo UI |
| `glm-5.1` | devops-architect | Docker, Komodo, Pulumi |
| `minimax-m2.5` | general fallback | 1M-token context window |
| `qwen-3.7-max` | data-engineer | Dagster, DLT, DuckDB/SQL |

### Cost tiers

| Tier | What you get | ~Monthly spend |
|:--|:--|:--|
| **Free** | Copilot Pro (student), Vertex AI $300 trial, DeepSeek free credits | $0 |
| **$5-10** | OpenCode Go flat rate, local models on M4 | ~$5-10 |
| **$20-25** | Above + DeepSeek Pro API pay-as-you-go | ~$20-25 |

Total: **under $25/month** for 50+ stacks, 28 HF models, 5 subagents, 3 local AI servers. Compare to direct OpenAI/Anthropic: $200-500+/month.

### Fork this project

Two config files control everything:
- `opencode.json` — which model each subagent uses
- `infrastructure/stacks/litellm/config/config.yaml` — which model each alias routes to

Every BAML function, Dagster asset, and marimo notebook calls aliases (e.g. `model="extract"`), not hardcoded provider IDs.

---

## HuggingFace Model Registry

Cache: `stedding/huggingface/hub/`. 28 models, 124 GB.

| Model | Size | Use |
|:--|:-:|:--|
| Qwen2.5-VL-7B | 15 GB | VLM -> Q4_K_M GGUF |
| Qwen2.5-Math-7B | 14 GB | Math -> Q4_K_M GGUF |
| deepseek-ocr | 6.2 GB | OCR -> Q4_K_M + mmproj |
| glm-4v-9b | 26 GB | VLM alt -> Q4_K_M GGUF |
| UCCIX-Llama2-13B | stub | Irish generation |
| bge-m3 | 4.3 GB | Curriculum embeddings |
| colpali-v1.3 | 108 MB | Visual retrieval |
| wav2vec2-xlsr-irish | 2.4 GB | Irish ASR |
| nllb-200-600M | 2.3 GB | Translation |
| bert-base-irish-cased | 483 MB | Irish NER/POS |
| whisper-large-v3 | 23 GB | ASR |
| opus-mt en-ga/ga-en/en-cy/cy-en | ~566 MB | Celtic translation |
| chatterbox | 9.7 GB | TTS |

---

## Technology Stack

| Layer | Technology |
|:--|:--|
| **Infrastructure** | Pulumi + Komodo + Pangolin + PocketID + Locket + Infisical + Garage S3 + Lakekeeper + Lance |
| **Storage** | DuckDB + DuckLake + LanceDB + Memgraph + FalkorDB + Neo4j + MotherDuck + R2 |
| **Orchestration** | Dagster v1.13+ + DLT v1.4+ + SQLMesh + CocoIndex |
| **LLM Gateway** | LiteLLM + llama-swap + mlx-omni + InvokeAI + docling-serve |
| **AI Frameworks** | BAML + Google ADK + Agno + Pydantic AI + Langfuse + MLflow + Ragas |
| **Memory / KG** | Graphiti + Cognee + temporal KGs |
| **Fine-tuning** | Unsloth + TRL + LoRA/QLoRA + Modal |
| **Embedding** | BGE-M3 + GaBERT + ColPali |
| **Translation** | NLLB-200 + Helsinki OPUS-MT + M2M-100 |
| **Speech** | Whisper-large-v3 + wav2vec2-XLSR-Irish + Chatterbox |
| **Frontend** | TanStack Start + CopilotKit + Convex + Hono + Marimo + AG-UI |
| **Browser** | Stagehand + Crawl4AI + Skyvern + Patchright + Browserbase + Firecrawl |
| **Observability** | Langfuse + MLflow + Logfire + Prometheus + Ragas |
| **Languages** | Python 3.12 + TypeScript (Bun) + Rust + TOML + BAML |

---

## Personal Foundation

Built by Cian Mac an Deisigh Ui Liathain — qualified Mathematics & Applied Mathematics teacher (Teaching Council of Ireland), NUI Galway HDip graduate in Applied Statistics, Software Development, and Irish Language Studies.

### Academic-to-architecture mapping

- **MA311 Applied Statistics I** -> RAGAS eval, grade distributions, DLT validation
- **MA378 Numerical Analysis II** -> numerical ops in DuckDB, geospatial interpolation
- **MP307 Modelling II** -> BAML IdentifyPrerequisiteChain
- **CS4423 Networks** -> KG topology for Memgraph/FalkorDB + Graphiti
- **CS402 Cryptography** -> zero-trust Pangolin/WireGuard
- **CT511 Databases** -> DuckDB/DuckLake schema design
- **CT545 Enterprise Java** -> FastAPI service-layer pattern
- **CT853 Algorithmics** -> deduplication hashing, HNSW indexing
- **CT870 Internet Programming** -> TanStack Start, MCP/AG-UI/SSE
- **ED116/ED305/ED411** -> pedagogical strategy for curriculum agents
- **GA101/GF101/GA81010** -> bilingual curriculum, Irish G2P, canuint TTS

### Professional standing

- **Teaching Council of Ireland** — Roll 241571, Route 2 Post-Primary, Maths & Applied Maths, Droichead conditions. [Verify](https://registration.teachingcouncil.ie).
- **BCS PGCE Computing Scholarship** — awarded for CS teacher training (UK KS2-KS4); PGCE not completed.
- **DEIS placement** — two full school years in DEIS schools.
- **Bilingual practice** — Irish-medium meanscoil; Spanish-language accommodation.
- **Action research** — three published mini-studies (Plickers, creative coding, critical incident).

### Education — Detailed Module Mapping

Pedagogical frameworks (constructivism, social identity, self-efficacy, differentiation, formative assessment, inclusion) are the engineering rationale for every curriculum agent and BAML schema.

| Module | Key Content | Project Impact |
|:--|:--|:--|
| **ED116** | Hedge-schools, 1831 Stanley letter, 1922/1998 constitutions | Pipeline taxonomy; agent system prompt references Irish education lineage |
| **ED303** | Piaget, Vygotsky ZPD, scaffolding, problem-based learning | Every curriculum agent designed for active knowledge construction |
| **ED305 Auto.** | Social capital, meritocracy, "shortcoming of the teacher not student" | Agent empathy/tone-mirroring for students who don't see themselves as "maths people" |
| **ED305 Psych.** | Bandura self-efficacy, Tajfel & Turner SIT, Dweck incremental theory, Tomlinson differentiation | Accessibility: every outcome tagged with difficulty, language_register, inclusion_notes |
| **ED411** | Plickers, creative-coding (Minecraft/Scratch/Python), critical incident | FormativeCheck tool, BehaviorSignal schema, CreativeCodingActivity assets |
| **3BME1 Placement** | Complex numbers, trig, stats, EAL/Spanish bilingual key | Lesson-plan reference; bilingual key seeds language alignment |
| **BCS PGCE CS** | NCCE Guides, AQA 8525, Scratch Y7, Python Y8 | Blueprint for Riomheolaiocht/CS strand |
| **Taster Days** | Outreach to BME students | "Why study this" hook for CopilotKit tutor |

**Regulatory context — MGO dispute:** The BCS PGCE Scholarship provides methodology for adding CS to registration. The project's open-source Riomheolaiocht strand resolves the methodology gap — same PGCE content packaged for Irish-medium schools without re-taking a Master's.

---

## Deployment

```bash
bun run setup
cd infrastructure/stacks/lakehouse && docker compose up -d
cd ../machine_learning/langfuse && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../../storage/mlflow && docker compose up -d
cd ../machine_learning/cognee && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../graphiti && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../../engineering/litellm && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../../meaisinfhoghlaim && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../../engineering/mlx-omni && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../../engineering/invokeai && docker compose -f compose.yaml -f sidecar.yaml up -d
cd oideachais && uv run dagster dev -m data_platform.dagster_defs.definitions
```

---

## Licensing

Business Source License 1.1 — non-commercial, cultural preservation, and academic research use permitted within Ireland, UK, EU, Commonwealth, and aligned jurisdictions. Transitions to AGPL v3.0 after 4 years. See [`LICENSE.md`](LICENSE.md).

---

*Built by Cian Mac an Deisigh Ui Liathain — qualified Mathematics & Applied Mathematics teacher (TCI), NUI Galway graduate (Applied Statistics, Software Development, Irish Language Studies), dual Irish-British citizen.*
