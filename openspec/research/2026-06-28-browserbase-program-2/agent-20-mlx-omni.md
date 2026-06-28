# Agent 20 — MLX-omni (Apple-Silicon-native OpenAI-compatible server)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages) — Agent 20 of 25
**BrowserBase budget used:** ~6 navigations (~30 credits)
**CCC queries:** 3

## TL;DR

MLX-omni (`madroidmaq/mlx-omni-server`, PyPI: `mlx-omni-server` v0.5.3, May 2026) is the canonical Apple-Silicon MLX-format inference server for Cianfhoghlaim. It exposes **dual API compatibility** (OpenAI `/v1/*` AND Anthropic `/anthropic/v1/*`), not just OpenAI as P2-24 claims. The actual upstream repo is `madroidmaq/mlx-omni-server` (730 stars, 296 commits), **not** `qifengle/marketplace-mlx-omni-server` as P2-24:1 states. Three Cianfhoghlaim models route through it via LiteLLM: `local/document/granite-docling` (258M, MLX), `local/ocr/olmocr-mlx` (2-7B MLX 4-bit), `local/image/fibo` (Bria FIBO JSON-driven). Memory cap is 36 GB (M-series unified memory headroom), well under the 48 GB anti-pattern ceiling.

The package stack is built **from source** via `infrastructure/stacks/mlx-omni/Dockerfile` (clones `madroidmaq/mlx-omni-server`, installs `.[server]` extras) — not pulled from PyPI. The pyproject.toml shows it depends on **seven MLX-family packages**: `mlx-lm` (text), `mlx-vlm` (vision), `mlx-audio[tts]` (TTS), `mlx-whisper` (STT), `mlx-embeddings`, `mflux` (image gen via FLUX), and `f5-tts-mlx` (TTS). Quantization support spans **3-bit / 4-bit / 5-bit / 6-bit / 8-bit / bf16 / fp16** — the mlx-community registry has 5,184 models following the `{name}-{quant}` convention (e.g. `Qwen3-4B-Instruct-2507-4bit` = 0.6B params, 2.26 GB).

## Code

| Path | Purpose |
|:--|:--|
| `infrastructure/stacks/mlx-omni/compose.yaml` | MLX-omni service (port 10240, 36 GB mem cap) |
| `infrastructure/stacks/mlx-omni/Dockerfile` | Build-from-source `madroidmaq/mlx-omni-server` (Python 3.12-slim) |
| `infrastructure/stacks/mlx-omni/secrets.env` | Locket template → `infisical://dev-baile/mlx-omni/api_key` + HF token aliases |
| `infrastructure/stacks/mlx-omni/sidecar.yaml` | Locket sidecar (Infisical + tmpfs at mode 700) |
| `infrastructure/stacks/mlx-omni/blueprint.yaml` | Pangolin blueprint → `mlxomni.cianfhoghlaim.ie` (Member role) |
| `infrastructure/stacks/litellm/config/config.yaml:34-65` | 3 local MLX model_list entries (granite-docling, olmocr-mlx, fibo) |
| `infrastructure/stacks/litellm/config/config.yaml:564-664` | 4 alias routes that prefer mlx-omni (`ocr`, `document`, `image-fibo`, `document/granite-docling`) |

**Canonical MLX-omni CLI** (per upstream `pyproject.toml`):

```toml
# pyproject.toml — actual CLI entry point
[project.scripts]
mlx-omni-server = "mlx_omni_server.main:start"
```

**Canonical install + serve** (per upstream README):

```bash
pip install mlx-omni-server          # PyPI package name is mlx-omni-server, NOT mlx-omni
mlx-omni-server                       # Default port 10240, listens 0.0.0.0
mlx-omni-server --port 8000          # Custom port
MLX_OMNI_LOG_LEVEL=debug mlx-omni-server
```

**OpenAI-compatible call** (per upstream README quick-start):

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:10240/v1", api_key="not-needed")
response = client.chat.completions.create(
    model="mlx-community/gemma-3-1b-it-4bit-DWQ",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**Anthropic-compatible call** (also supported):

```python
import anthropic
client = anthropic.Anthropic(base_url="http://localhost:10240/anthropic", api_key="not-needed")
message = client.messages.create(
    model="mlx-community/gemma-3-1b-it-4bit-DWQ",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**LiteLLM integration** (`stacks/litellm/config/config.yaml:34-65`):

```yaml
- model_name: local/document/granite-docling
  litellm_params:
    model: openai/granite-docling
    api_base: http://mlx-omni:10240/v1
    api_key: not-needed
    timeout: 600   # Docling can be slow on dense PDFs

- model_name: local/ocr/olmocr-mlx
  litellm_params:
    model: openai/olmocr-2-7b-mlx
    api_base: http://mlx-omni:10240/v1
    api_key: not-needed
    timeout: 600

- model_name: local/image/fibo
  litellm_params:
    model: openai/fibo
    api_base: http://mlx-omni:10240/v1
    api_key: not-needed
    timeout: 600
```

**Alias route that exposes mlx-omni to clients** (`config.yaml:590-601`):

```yaml
- model_name: document
  litellm_params:
    model: openai/granite-docling
    api_base: http://mlx-omni:10240/v1
    api_key: not-needed
    timeout: 600
  model_info:
    description: "Alias: document → Granite Docling (MLX) for DocTags XML structure"
    fallback_chain: ["local/document/granite-docling", "local/vision/qwen25-vl"]
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `MLX_OMNI_API_KEY` | `not-needed` (dev) / `infisical://dev-baile/mlx-omni/api_key` (prod) | compose env + secrets.env |
| `MLX_OMNI_HOST` | `0.0.0.0` | compose env |
| `MLX_OMNI_PORT` | `10240` | compose env |
| `MLX_OMNI_DEFAULT_MODEL` | `mlx-community/granite-docling-258M-MLX` | compose env |
| `MLX_OMNI_LOG_LEVEL` | (unset by default; `debug` for troubleshooting) | runtime env |
| `HF_TOKEN` / `HUGGINGFACE_HUB_TOKEN` / `HUGGINGFACE_TOKEN` | `infisical://dev-baile/huggingface/token` (all three aliases accepted) | secrets.env |
| `HF_HOME` | `/stedding/huggingface` | compose env |
| `HF_HUB_CACHE` | `/stedding/huggingface/hub` | compose env |
| `HF_HUB_DOWNLOAD_TIMEOUT` | `600` | compose env |

## CCC anchors

| Anchor | Why |
|:--|:--|
| `infrastructure/stacks/mlx-omni/README.md` | Stack overview — port 10240, dual API, 36 GB mem |
| `infrastructure/stacks/mlx-omni/Dockerfile` | Build-from-source via `git clone madroidmaq/mlx-omni-server` |
| `infrastructure/stacks/mlx-omni/compose.yaml` | Service definition + 36G mem limit + read-only HF cache mounts |
| `infrastructure/stacks/litellm/config/config.yaml:34-65` | Three `http://mlx-omni:10240/v1` model_list entries |
| `infrastructure/stacks/litellm/config/config.yaml:564-664` | Alias routes (`ocr`, `document`, `image-fibo`) that prefer MLX |
| `infrastructure/stacks/mlx-omni/blueprint.yaml` | Pangolin blueprint → `mlxomni.cianfhoghlaim.ie` |
| `infrastructure/stacks/mlx-omni/sidecar.yaml:11-21` | Locket Infisical provider + tmpfs 700 mode |
| `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-24-mlx-omni.md` | Spec file — **DRIFTED**: wrong repo URL, wrong package name |

Search terms: `"mlx-omni"`, `"mlx-community"`, `"http://mlx-omni:10240/v1"`, `"MLX Omni"`, `"apple silicon"`, `"mlx-lm"`.

CCC search results (top hits):
1. `infrastructure/stacks/mlx-omni/README.md:1-4` (score 0.747) — confirms stack exists at expected path
2. `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-24-mlx-omni.md:1-12` (score 0.677) — the drifted spec
3. `infrastructure/stacks/mlx-omni/README.md:6-14` (score 0.658) — same content re-ranked

## Drift log

| Date | Event | Source |
|:--|:--|:--|
| **2026-06-28** | **CRITICAL: P2-24 spec drift** — declares upstream as `qifengle/marketplace-mlx-omni-server`; actual canonical repo used by `Dockerfile:19` and `README.md:55` is `madroidmaq/mlx-omni-server` | `infrastructure/stacks/mlx-omni/Dockerfile:19`, README.md:55 |
| **2026-06-28** | **CRITICAL: P2-24 package-name drift** — declares `pip install mlx-omni`; actual PyPI name (per `pyproject.toml:2`) is `mlx-omni-server` | `pyproject.toml:2` |
| **2026-06-28** | **CRITICAL: P2-24 API-surface drift** — declares "OpenAI-compatible server"; actual upstream supports **dual API** (OpenAI `/v1/*` AND Anthropic `/anthropic/v1/*`) | upstream README API Support table |
| **2026-06-28** | **CRITICAL: P2-24 CLI drift** — declares `mlx-omni serve --model …`; actual CLI is `mlx-omni-server` with no `serve` subcommand (auto-discovers models from HF cache), accepts only `--port` flag per upstream README | upstream README, pyproject.toml scripts entry |
| **2026-06-28** | **CRITICAL: P2-24 Dockerfile CMD drift** — Dockerfile:39 runs `mlx-omni serve --host 0.0.0.0 --port 10240`; correct invocation per upstream is `mlx-omni-server` (no `serve` verb) | `Dockerfile:39` vs upstream README Quick Start |
| **2026-06-28** | **MEDIUM: P2-24 model-list drift** — declares "Qwen3.6, Gemma 4"; these don't exist yet (Qwen3 max is `Qwen3-4B-Instruct-2507`; Gemma 4 not in mlx-community). Actual stack model is `mlx-community/granite-docling-258M-MLX` (per compose.yaml:34) | `compose.yaml:34` |
| 2026-01 | Initial MLX-omni deploy (Qwen2.5 only) | P2-24 |
| 2026-04 | Added Gemma 3 + OLMoE support | P2-24 |
| 2026-05 | **Confirmed v0.5.3 release** — adds Anthropic API surface, TTS (mlx-audio), image gen (mflux) | upstream releases |
| 2026-06-28 | mlx-community registry = **5,184 models**, 7 spaces, 39 datasets, 171 collections | huggingface.co/mlx-community |
| 2026-06-28 | Latest popular quantizations on mlx-community: 3-bit, 4-bit, 5-bit, 6-bit, 8-bit, bf16, fp16 (full MLX-native spectrum) | huggingface.co/mlx-community |

## Anti-patterns

1. **Don't run MLX-omni on `arm1-oci`** — `pyproject.toml:21` pins `mlx>=0.31.2,<0.32; sys_platform == 'darwin'` — dependency only resolves on macOS. The Dockerfile:28-29 explicitly warns `WARNING: mlx not available — this image will not start on non-Apple hosts`. The Dockerfile even has the comment "this Dockerfile will only run on macOS hosts".
2. **Don't use 8-bit on M-series** — 4-bit is the native sweet spot; the upstream README Quick Start uses `mlx-community/gemma-3-1b-it-4bit-DWQ` as the canonical example. 8-bit MLX weights exist (`Ornith-1.0-35B-8bit`) but double the memory for marginal quality gain.
3. **Don't use MLX-omni for non-Apple-Silicon models** — use llama-swap (GGUF) for cross-arch. MLX weights are darwin-only.
4. **Don't exceed 48 GB unified memory** — `compose.yaml:46` caps at 36G. The M4 Max has 36-128 GB unified memory. 4-bit quantization: ~3.5 GB per 7B params → can fit two 7B models concurrently at 36G.
5. **Don't bypass the Locket sidecar** — `secrets.env` uses `infisical://dev-baile/mlx-omni/api_key` references; never hand-edit `.env`. The 3 HF token aliases (`HF_TOKEN`, `HUGGINGFACE_HUB_TOKEN`, `HUGGINGFACE_TOKEN`) are intentional for cross-tool compat (transformers, mlx-lm, huggingface-cli).
6. **Don't use `mlx-omni` as the CLI command** — it's `mlx-omni-server` (the PyPI script entry per `pyproject.toml:38`). The `Dockerfile:39` invocation `mlx-omni serve ...` is **incorrect** — there is no `serve` subcommand in v0.5.3.
7. **Don't forget that HF cache must be mounted** — `compose.yaml:24` mounts `../../stedding/huggingface/mlx:/models:ro` and `../../stedding/huggingface:/stedding/huggingface:ro`. Without these, every model would re-download on container restart.

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Upstream repo | `madroidmaq/mlx-omni-server` | Canonical, 730★, v0.5.3 (May 2026), used by `infrastructure/stacks/mlx-omni/Dockerfile:19`. **Overrides P2-24** which incorrectly cites `qifengle/marketplace-mlx-omni-server`. |
| PyPI package | `mlx-omni-server` | The actual `name = "mlx-omni-server"` in `pyproject.toml:2`. `pip install mlx-omni-server`. **Overrides P2-24** which says `pip install mlx-omni`. |
| Build strategy | Build from source via local Dockerfile | `Dockerfile:19` does `git clone https://github.com/madroidmaq/mlx-omni-server.git`. Avoids PyPI binary compatibility issues on Apple Silicon. |
| Hosting | MacBook M4 Max only (bunchloch) | Apple Silicon native; MLX dep is darwin-only. |
| Default port | 10240 | Matches upstream default and `compose.yaml:32`. |
| Quantization (recommended) | 4-bit | Native MLX hardware path. The README Quick Start uses `mlx-community/gemma-3-1b-it-4bit-DWQ`. |
| Quantization (alternative) | 8-bit, bf16, fp16 | Available but uses more memory; only needed when quality dominates latency. |
| API surface | Dual: OpenAI `/v1/*` + Anthropic `/anthropic/v1/*` | v0.5.3 added Anthropic. Cianfhoghlaim uses OpenAI surface via LiteLLM. |
| Server invoker | `mlx-omni-server` (no `serve` subcommand) | The CLI entry in `pyproject.toml:38`. **Dockerfile:39 needs fix.** |
| Memory cap | 36 GB | M4 Max unified memory headroom; P2-24 anti-pattern says "Don't exceed 48 GB". |
| Fallback tier | 3rd in LiteLLM chain (after llama-swap GGUF, before invokeai/docling-serve) | `config.yaml:11-15` documents route topology. **Overrides P2-24** which says "6th in minimax chain". |
| Model registry | 3 reference MLX models in litellm config (granite-docling 258M, olmocr-2-7b-mlx, fibo) | `config.yaml:34-65`. P2-24 says "11 vision + 4 text" — that's aspirational, not currently wired. |
| HF cache mount | `stedding/huggingface/mlx` (read-only) + parent | `compose.yaml:24-25`. Same shared cache used by other stacks. |

## Files to read next

- `infrastructure/stacks/mlx-omni/Dockerfile` — currently has wrong CMD; needs fix to `["mlx-omni-server"]`
- `infrastructure/stacks/litellm/config/config.yaml:564-664` — verify all 4 alias routes that prefer mlx-omni
- `openspec/specs/infrastructure-stacks/spec.md` — confirm 36G memory limit matches M-series tier spec
- `infrastructure/stacks/mlx-omni/README.md:55-57` — upstream-tracking links (currently say `madroidmaq/mlx-omni-server`)
- Upstream README quick-start + `docs/openai-api.md` — for Anthropic endpoint migration

## §8 Refactor opportunities

| # | Refactor | File:line | Benefit |
|:--|:--|:--|:--|
| **R1** | **Fix Dockerfile CMD** — replace `["mlx-omni", "serve", "--host", "0.0.0.0", "--port", "10240"]` with `["mlx-omni-server"]` (per upstream `pyproject.toml:38`); env vars `MLX_OMNI_HOST` / `MLX_OMNI_PORT` already cover the host/port | `infrastructure/stacks/mlx-omni/Dockerfile:39` | Fixes broken invocation; aligns with v0.5.3 |
| **R2** | **Fix P2-24 spec drift** — update `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-24-mlx-omni.md:1,8,22-34,40-42,88-90` to use `madroidmaq/mlx-omni-server` + `pip install mlx-omni-server` + dual API surface | `P2-24-mlx-omni.md` | Eliminates research/real-code divergence |
| **R3** | **Add Anthropic API support to litellm config** — `mlx-omni` v0.5.3 supports `/anthropic/v1/messages`; could add `anthropic/mlx-omni` route for the BAML `litellm` client's Anthropic surface | `config.yaml` (new entries near line 65) | Unlocks Anthropic-flavored BAML extractions on-device |
| **R4** | **Pin `mlx` family versions together** — `pyproject.toml:21-25` uses `>=0.31.2,<0.32` for `mlx`, `mlx-lm`, `>=0.4.3,<0.5` for `mlx-vlm` and `mlx-audio[tts]`; add a `[tool.uv]` constraints block to prevent partial upgrades | upstream `pyproject.toml:21-25` | Stability for `uv pip install -e ".[server]"` builds |
| **R5** | **Expose `/anthropic/v1/*` through Pangolin** — `blueprint.yaml:8` only declares `mlxomni.cianfhoghlaim.ie`; Anthropic clients would need a separate domain (`anthropic-mlxomni.cianfhoghlaim.ie`) or path-rewrite in Traefik | `blueprint.yaml:3-13` | Single-domain multi-API surface |
| **R6** | **Wire mlx-community model registry into mlx-omni auto-discovery** — the README says "Auto-discovery of MLX models in HuggingFace cache" but the cache is mounted read-only at `/models:ro` (compose.yaml:24); consider adding a `--models-dir` CLI flag to upstream PR | upstream + `compose.yaml:24` | Use the curated `stedding/huggingface/mlx` collection without per-model config |
| **R7** | **Add mlx-omni healthcheck probe path** — `compose.yaml:36` probes `/v1/models`; consider `/v1/models` returning 200 + non-empty list as a stronger liveness signal | `compose.yaml:35-40` | Catch misconfigured cache mount at startup |
| **R8** | **Document the Anthropic compatibility surface** — Cianfhoghlaim hasn't yet added `litellm`'s `anthropic/` prefix for mlx-omni; create a small `docs/stacks/mlx-omni-anthropic.md` showing `anthropic.messages.create(...)` usage | new doc | Migration guide for BAML Anthropic clients |
| **R9** | **Bump healthcheck `start_period`** — `compose.yaml:40` uses 60s; cold-start loading a 7B 4-bit model from `/stedding/huggingface/mlx` into unified memory can take 90-120s on M4 Max | `compose.yaml:40` | Fewer false-negative healthchecks |
| **R10** | **Update `infrastructure/stacks/mlx-omni/README.md:55-57`** — the upstream repo already tracks `madroidmaq/mlx-omni-server`; the spec note says "tracks the upstream repository" which is correct, but should add the PyPI link `https://pypi.org/project/mlx-omni-server/` | `README.md:55-57` | Single source of truth |
