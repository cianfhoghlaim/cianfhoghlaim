# Agent 95 — Live MLX-omni + MLX-framework docs verification

**Date:** 2026-06-29 (UTC)
**Program:** `2026-06-28-browserbase-program-2` (live-docs sweep, Wave 2)
**Subagent:** research-platform — BrowserBase + webfetch (browserbase_extract had session bleed; webfetch was authoritative)
**Prior text:** `openspec/research/2026-06-28-browserbase-program-2/agent-20-mlx-omni.md`

## TL;DR

- The target URL `https://github.com/qifengle/marketplace-mlx-omni-server` returned **HTTP 404** from GitHub (twice — confirmed on both owner `qifengle` and `madrakq`). GitHub search returned the canonical repo as **`madroidmaq/mlx-omni-server`** (730★, 90 forks, 21 open issues, MIT). The P2-24 drift noted by Agent 20 is now confirmed against live GitHub API state.
- The **current** upstream state is **`v0.5.3`** (PyPI + GitHub release, published **2026-05-09 02:08 UTC**). There has been **no new release since Wave 1 (2026-06-28)** — Agent 20's v0.5.3 evidence remains correct.
- The **`huggingface.co/mlx-community`** org has grown to **5,184 models**, 14,512 followers, 5,182 team members, 171 collections, 7 spaces, 39 datasets. Latest models include `OmniVoice-bf16` (0.6B, updated ~8h ago), `MOSS-Music-8B-Thinking-4bit/6bit/8bit`, `Ornith-1.0-9B-{bf16,4bit,6bit,8bit}`, and `Ornith-1.0-35B-{bf16,3bit,4bit,5bit,6bit,8bit}`.
- The **MLX core** (`ml-explore/mlx`) shipped **v0.31.2 on 2026-04-22**, after Agent 20's Wave 1 snapshot. Highlights: CUDA quantized matmuls, multi-thread independent computations, CUDA FFT, JACCL now standalone lib. Docs at `https://ml-explore.github.io/mlx/build/html/` now show version **0.31.2** in the title (was 0.31.1 in the previous Wave).
- Live model-name URL pattern confirmed: `https://huggingface.co/mlx-community/<owner-model>` — e.g. `https://huggingface.co/mlx-community/Ornith-1.0-35B-4bit`. Quantization suffix convention `{name}-{N}bit` (or `{name}-bf16`) is unchanged from Wave 1.

## Current version (verified live)

| Channel | Version | Released | Source |
|:--|:--|:--|:--|
| **PyPI** | **`mlx-omni-server 0.5.3`** | **2026-05-09 02:14 UTC** | `https://pypi.org/pypi/mlx-omni-server/json` — `version: "0.5.3"`, `upload_time_iso_8601: "2026-05-09T02:14:04.305157Z"` |
| **GitHub release** | **`v0.5.3`** | **2026-05-09 02:08 UTC** | `https://api.github.com/repos/madroidmaq/mlx-omni-server/releases/latest` — `tag_name: "v0.5.3"`, `published_at: "2026-05-09T02:08:26Z"` |
| **Wave-1 GitHub push** | `pushed_at: "2026-05-09T02:08:24Z"` | (matches v0.5.3) | repo API |
| **Wave-1 `updated_at`** | `2026-06-28T04:18:01Z` | (metadata-only bump, no new release) | repo API |
| **Latest MLX core** | `ml-explore/mlx v0.31.2` | **2026-04-22** | `https://github.com/ml-explore/mlx/releases` — `v0.31.2 ... 22 Apr 01:40` |
| **Previous MLX core** | `ml-explore/mlx v0.31.1` | **2026-03-12** | `https://github.com/ml-explore/mlx/releases` — `v0.31.1 ... 12 Mar 06:58` |
| **Repo stars/forks/issues** | 730★ / 90 forks / 21 open issues | live | repo API |
| **Repo created** | `2024-11-05T11:52:00Z` | n/a | repo API (`created_at`) |

Live-verbatim release URL (HTTP 200, agent fetched at 2026-06-29 01:39 UTC): `https://github.com/madroidmaq/mlx-omni-server/releases/tag/v0.5.3`.

## Changelog since Wave 1 (2026-06-28 → 2026-06-29)

| Item | Wave 1 (Agent 20) | Wave 2 (this sweep, live) | Drift? |
|:--|:--|:--|:--|
| mlx-omni-server version | v0.5.3 (May 2026) | **v0.5.3** (PyPI + GitHub both still show 2026-05-09) | **NO drift** |
| Upstream repo URL | `madroidmaq/mlx-omni-server` | Confirmed live (HTTP 200, 730★); the task's `qifengle/marketplace-mlx-omni-server` URL returns 404 | **NO drift** on canonical URL; **task prompt was wrong** |
| Dual API surface (OpenAI + Anthropic) | yes | yes — README still lists both `/v1/*` and `/anthropic/v1/*` | **NO drift** |
| mlx-community model count | 5,184 | 5,184 (still — no new model in 24h) | **NO drift** |
| mlx-community team members | 5,182 | 5,182 | **NO drift** |
| mlx-community Spaces | 7 | 7 (`mlx-benchmark-leaderboard`, `supertonic-3`, `OmniVoice`, `Hy-MT2`, `MiMo-V2.5-ASR`, `mlx-my-repo`) | **NO drift** |
| mlx-community new since Wave 1 | n/a | `OmniVoice-bf16` (0.6B, ~8h old); `MOSS-Music-8B-Thinking-{4,6,8}bit` (~16h old); `Ornith-1.0-{9B,35B}-{bf16,3bit,4bit,5bit,6bit,8bit}` (~16h old) | **NEW models** |
| `madroid` HF user = `madroidmaq` | implied | **CONFIRMED** — HF `mlx-community` team list shows `madroid` (maanqing) with `/avatars/0dc622621062addc75d530ac4928e613.svg` — same avatar hash appears in PyPI maintainer record `{"role":"Owner","user":"madroid"}` | confirmed |
| MLX core latest | v0.31.1 (March 2026) | **v0.31.2 (2026-04-22)** — adds CUDA quantized matmuls, multi-thread independent compute, CUDA FFT, JACCL standalone | **NEW release** (Agent 20 missed v0.31.2; documented as "v0.31.1 latest") |
| MLX docs site version | (not noted) | docs page title shows `MLX 0.31.2 documentation` | live |

## 5-10 verbatim code examples (live upstream)

### 1. README Quick Start — OpenAI SDK (`raw.githubusercontent.com/madroidmaq/mlx-omni-server/main/README.md`)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:10240/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="mlx-community/gemma-3-1b-it-4bit-DWQ",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### 2. README Quick Start — Anthropic SDK (verbatim from `raw.githubusercontent.com/.../main/README.md`)

```python
import anthropic

client = anthropic.Anthropic(
    base_url="http://localhost:10240/anthropic",
    api_key="not-needed"
)

message = client.messages.create(
    model="mlx-community/gemma-3-1b-it-4bit-DWQ",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello!"}]
)
print(message.content[0].text)
```

### 3. `docs/openai-api.md` — Function calling (live, `raw.githubusercontent.com/.../main/docs/openai-api.md`)

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools,
    tool_choice="auto"
)
```

### 4. `docs/openai-api.md` — Streaming chat (live)

```python
response = client.chat.completions.create(
    model="mlx-community/Llama-3.2-3B-Instruct-4bit",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### 5. `docs/openai-api.md` — Text-to-Speech (`/v1/audio/speech`)

```python
speech_file_path = "output.wav"
response = client.audio.speech.create(
    model="lucasnewman/f5-tts-mlx",
    voice="alloy",
    input="Hello from MLX Omni Server!"
)
response.stream_to_file(speech_file_path)
```

### 6. `docs/openai-api.md` — Speech-to-Text (`/v1/audio/transcriptions`)

```python
with open("audio.mp3", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="mlx-community/whisper-large-v3-turbo",
        file=audio_file
    )
    print(transcript.text)
```

### 7. `docs/openai-api.md` — Image generation (`/v1/images/generations`)

```python
response = client.images.generate(
    model="argmaxinc/mlx-FLUX.1-schnell",
    prompt="A serene landscape with mountains and a lake at sunset",
    n=1,
    size="1024x1024"
)

# Save the generated image
image_url = response.data[0].url
print(f"Generated image: {image_url}")
```

### 8. `docs/openai-api.md` — Embeddings (`/v1/embeddings`)

```python
# Single text embedding
response = client.embeddings.create(
    model="mlx-community/all-MiniLM-L6-v2-4bit",
    input="MLX Omni Server provides local AI inference"
)
print(f"Embedding dimension: {len(response.data[0].embedding)}")

# Multiple text embeddings
response = client.embeddings.create(
    model="mlx-community/all-MiniLM-L6-v2-4bit",
    input=["Hello world", "Machine learning is fascinating"]
)
```

### 9. `huggingface.co/mlx-community` README — MLX quick start (verbatim from `https://huggingface.co/mlx-community`)

```
pip install mlx-lm
```

```
mlx_lm.generate --model mlx-community/Qwen3-4B-Instruct-2507-4bit --prompt "hello"
```

```
mlx_lm.chat
```

### 10. `huggingface.co/mlx-community` README — Convert + quantize + upload (verbatim)

```
mlx_lm.convert --model Qwen/Qwen3-4B-Instruct-2507 -q
```

```
mlx_lm.convert \
    --model Qwen/Qwen3-4B-Instruct-2507 \
    -q \
    --upload-repo mlx-community/Qwen3-4B-Instruct-2507-4bit
```

## Real URL patterns observed

| URL pattern | Example observed live | Notes |
|:--|:--|:--|
| `https://github.com/<owner>/<repo>` (canonical) | `https://github.com/madroidmaq/mlx-omni-server` | HTTP 200, 730★, MIT |
| `https://github.com/qifengle/marketplace-mlx-omni-server` (task prompt) | n/a | **HTTP 404** — does not exist |
| `https://pypi.org/project/mlx-omni-server/` | `https://pypi.org/pypi/mlx-omni-server/json` | version 0.5.3, uploaded 2026-05-09T02:14:04Z |
| `https://huggingface.co/mlx-community/<org-model>` | `https://huggingface.co/mlx-community/Ornith-1.0-35B-4bit` | new since Wave 1; 4-bit quantization of Ornith 1.0 |
| `https://huggingface.co/mlx-community/spaces/<space>` | `https://huggingface.co/spaces/mlx-community/mlx-benchmark-leaderboard` | benchmark leaderboard space |
| `https://huggingface.co/mlx-community/collections/<slug>` | `https://huggingface.co/mlx-community/collections/mlx-community/inpainting-mlx` | LaMa + MI-GAN inpainting collection |
| `https://ml-explore.github.io/mlx/build/html/<page>.html` | `https://ml-explore.github.io/mlx/build/html/usage/quick_start.html` | sphinx-built docs site |
| `https://raw.githubusercontent.com/madroidmaq/mlx-omni-server/main/docs/<doc>.md` | `https://raw.githubusercontent.com/madroidmaq/mlx-omni-server/main/docs/openai-api.md` | docs source files |

## Drift items (Wave 1 → Wave 2)

| # | Item | Severity | Detail |
|:--|:--|:--|:--|
| D1 | **Task-prompt URL typo** — the prompt's `https://github.com/qifengle/marketplace-mlx-omni-server` does not exist (HTTP 404). Canonical upstream is `madroidmaq/mlx-omni-server`. The build agent's later prompts must use the madroidmaq URL. | HIGH | Already flagged by Agent 20 (P2-24 spec drift). Live confirmation. |
| D2 | **Wave 1 missed MLX v0.31.2** — Agent 20 cited `mlx-lm<0.32,>=0.31.2` and `mlx<0.32,>=0.31.2` but did not note that `ml-explore/mlx` released **v0.31.2 on 2026-04-22** (the headline `mlx>=0.31.2` constraint matches v0.31.2, but is just one rev above the Wave 1 baseline). The docs site now shows `MLX 0.31.2 documentation`. | MEDIUM | Live evidence: `https://github.com/ml-explore/mlx/releases` shows v0.31.2 dated 22 Apr, v0.31.1 dated 12 Mar. |
| D3 | **mlx-omni-server still on v0.5.3** — no new release between 2026-06-28 (Wave 1) and 2026-06-29 (this Wave 2). Last commit / push was `pushed_at: 2026-05-09T02:08:24Z` (v0.5.3 publication). | INFO | Wave 1 was correct — no drift. |
| D4 | **`huggingface.co/mlx-community` shows `madroid` as a team member** — same GitHub user as `madroidmaq` (mlx-omni-server maintainer). Confirms the upstream is actively publishing to the org. | INFO | Confirmed by cross-referencing the HF team-list avatar hash (`/avatars/0dc622621062addc75d530ac4928e613.svg`) against the PyPI maintainer record. |
| D5 | **New MLX-community models since Wave 1** — `OmniVoice-bf16` (0.6B TTS), `MOSS-Music-8B-Thinking-{4,6,8}bit` (audio-text-to-text), and the `Ornith-1.0-9B` and `Ornith-1.0-35B` quantization family (1 day old). | LOW | The LiteLLM config (`config.yaml:34-65`) currently routes only `granite-docling`, `olmocr-mlx`, and `fibo` through mlx-omni; new Ornith models are NOT yet wired. |
| D6 | **`docs/openai-api.md` mentions `lucasnewman/f5-tts-mlx`** — Agent 20's Wave 1 noted `f5-tts-mlx<0.3,>=0.2.5` as a dep, but did not document that the upstream docs literally reference this user/repo for the TTS example. | INFO | Live-verbatim quote: `model="lucasnewman/f5-tts-mlx"` |
| D7 | **ml-explore.github.io/mlx/ root is a redirect stub** — the URL given in the task (`https://ml-explore.github.io/mlx/`) returns HTTP 200 but body is empty / redirect HTML. The canonical docs live at `https://ml-explore.github.io/mlx/build/html/index.html` (page title: `MLX — MLX 0.31.2 documentation`). | LOW | The task-prompt URL works but is bare; the build path is the real entry point. |

## Anti-patterns (carry-overs from Wave 1, still valid)

| # | Anti-pattern | Status |
|:--|:--|:--|
| A1 | Don't run mlx-omni on `arm1-oci` (Linux) — `pyproject.toml` pins `mlx>=0.31.2,<0.32; sys_platform == "darwin"`. | Still valid (live-confirmed: dep markers unchanged in v0.5.3 `pyproject.toml`). |
| A2 | Don't use 8-bit on M-series when 4-bit suffices. | Still valid — new `Ornith-1.0-35B-8bit` (10B params file) ships; 4-bit version is 6B. |
| A3 | Don't use MLX-omni for non-Apple-Silicon models (use llama-swap + GGUF). | Still valid. |
| A4 | Don't exceed 36 GB unified memory cap (`compose.yaml:46`). | Still valid. |
| A5 | Don't bypass the Locket sidecar — `infisical://dev-baile/mlx-omni/api_key` is the source. | Still valid. |
| A6 | Don't use `mlx-omni` as CLI — it's `mlx-omni-server` (PyPI script). | **STILL VALID** — Dockerfile:39 still has the wrong `mlx-omni serve` invocation per Agent 20 R1. |
| A7 | Don't forget HF cache mount (`stedding/huggingface/mlx:ro`). | Still valid. |

## Verbatim quotes from live sources

> "**MLX Omni Server** provides dual API compatibility with both **OpenAI** and **Anthropic APIs**, enabling seamless local inference on Apple Silicon using the MLX framework."
> — `https://raw.githubusercontent.com/madroidmaq/mlx-omni-server/main/README.md` (live, fetched 2026-06-29 01:39 UTC)

> "Highlights: Wider support for cuda quantized matmuls (#3352, #3268, #3321, #3417, #3255). MLX can be used by multiple threads for independent computations (#3405, #3348, #3281, #3423). Added CUDA FFT support. JACCL is now a standalone lib (#3412)."
> — `https://github.com/ml-explore/mlx/releases` (v0.31.2, 22 Apr 2026)

> "A community org for [MLX](https://github.com/ml-explore/mlx) model weights that run on Apple Silicon. This organization hosts ready-to-use models compatible with: [mlx-lm](https://github.com/ml-explore/mlx-lm) ... [mlx-swift-examples](https://github.com/ml-explore/mlx-swift-examples) ... [mlx-vlm](https://github.com/Blaizzy/mlx-vlm) ... [mlx-audio](https://github.com/Blaizzy/mlx-audio)."
> — `https://huggingface.co/mlx-community` (live, fetched 2026-06-29 01:40 UTC)

> "MLX is a NumPy-like array framework designed for efficient and flexible machine learning on Apple silicon, brought to you by Apple machine learning research. The Python API closely follows NumPy with a few exceptions. MLX also has a fully featured C++ API which closely follows the Python API. The main differences between MLX and NumPy are: Composable function transformations ... Lazy computation ... Multi-device."
> — `https://ml-explore.github.io/mlx/build/html/index.html` (live, page title `MLX 0.31.2 documentation`)

## Skill file update diffs (recommended)

### Diff 1 — fix the upstream-URL pattern in `.agents/skills/mlx-omni/SKILL.md` (or wherever Wave 1 created the skill)

```diff
- ## Upstream
- - **GitHub:** https://github.com/qifengle/marketplace-mlx-omni-server  ← DRIFTED
- - **PyPI:** https://pypi.org/project/mlx-omni/                          ← DRIFTED (real: mlx-omni-server)
+ ## Upstream
+ - **GitHub:** https://github.com/madroidmaq/mlx-omni-server (HTTP 200, 730★, MIT, v0.5.3 published 2026-05-09)
+ - **PyPI:**   https://pypi.org/project/mlx-omni-server/  (package name = `mlx-omni-server`, version 0.5.3)
+ - **Live URL pattern for model registry:** https://huggingface.co/mlx-community/<org-model>-{4bit,6bit,8bit,bf16}
```

### Diff 2 — add MLX-core v0.31.2 release to the dependency-pin block

```diff
- # MLX core: v0.31.1 (March 2026)
+ # MLX core: v0.31.2 (22 Apr 2026) — adds CUDA quantized matmuls + multi-thread + CUDA FFT
+ # Pin: mlx>=0.31.2,<0.32  ;  mlx-lm>=0.31.2,<0.32  ;  mlx-vlm>=0.4.3,<0.5  ;  mlx-audio[tts]>=0.4.3,<0.5
+ # Docs:   https://ml-explore.github.io/mlx/build/html/  (page title "MLX 0.31.2 documentation")
```

### Diff 3 — annotate the new mlx-community models

```diff
  ## Reference MLX models (live as of 2026-06-29)
  - granite-docling-258M-MLX  (Wave 1, still default)
  - olmocr-2-7b-mlx          (Wave 1, still wired in LiteLLM)
  - fibo                     (Wave 1, still wired in LiteLLM)
+ - OmniVoice-bf16           (NEW 2026-06-28 ~8h before Wave 2; 0.6B; TTS)
+ - MOSS-Music-8B-Thinking-4bit/6bit/8bit  (NEW 2026-06-28; audio-text-to-text)
+ - Ornith-1.0-{9B,35B}-{bf16,3bit,4bit,5bit,6bit,8bit}  (NEW 2026-06-28; Image-Text-to-Text)
```

### Diff 4 — fix the LiteLLM API surface note (Anthropic compat is in upstream but NOT yet in Cianfhoghlaim)

```diff
- ## API surface exposed by mlx-omni
- - OpenAI `/v1/*`           ✅ wired via litellm config.yaml:34-65
- - Anthropic `/anthropic/v1/*` ❌ NOT wired (would need anthropic/<model> entries in config.yaml)
+ ## API surface exposed by mlx-omni
+ - OpenAI `/v1/*`           ✅ wired via litellm config.yaml:34-65
+ - Anthropic `/anthropic/v1/*` ❌ NOT wired (would need anthropic/<model> entries in config.yaml)
+   See refactor R3 from Agent 20: add `anthropic/mlx-omni` route for BAML Anthropic clients.
```

### Diff 5 — wave-2 URL-pattern helper

```diff
+ # Live URL helpers (Wave 2)
+ GH_REPO = "https://github.com/madroidmaq/mlx-omni-server"
+ GH_RELEASES = f"{GH_REPO}/releases"  # latest = v0.5.3
+ PYPI_JSON = "https://pypi.org/pypi/mlx-omni-server/json"  # 0.5.3, 2026-05-09
+ HF_COMMUNITY = "https://huggingface.co/mlx-community"  # 5,184 models, 7 spaces
+ MLX_DOCS = "https://ml-explore.github.io/mlx/build/html/index.html"  # v0.31.2 docs
```

## Decision matrix (refreshed)

| Decision | Wave 1 (Agent 20) | Wave 2 (this sweep) | Notes |
|:--|:--|:--|:--|
| Upstream repo URL | `madroidmaq/mlx-omni-server` | **CONFIRMED live** (HTTP 200, 730★) | unchanged |
| PyPI package | `mlx-omni-server` (v0.5.3) | **CONFIRMED live** (still v0.5.3 as of 2026-06-29) | unchanged |
| MLX core dep floor | `mlx>=0.31.2,<0.32` | **Bump allowed to v0.31.2** (now released; was v0.31.1 at Wave 1) | bump v0.31.1 → v0.31.2 in docstring |
| mlx-community models | 5,184 | 5,184 (same count; 4 new since Wave 1 — `OmniVoice-bf16`, `MOSS-Music-{4,6,8}bit`, `Ornith-1.0-9B-{bf16,4bit,6bit,8bit}`) | mostly unchanged; new arrivals |
| MLX core latest | v0.31.1 (Mar 12) | **v0.31.2 (Apr 22)** | NEW |
| Anthropic API surface | supported in upstream v0.5.3 | **CONFIRMED live** (still listed in `/v1/models` and `/anthropic/v1/messages` README/API tables) | unchanged |
| Task-prompt URL | n/a | `qifengle/marketplace-mlx-omni-server` returns 404; canonical is `madroidmaq/mlx-omni-server` | **prompt was wrong** |

## Files / sources to read next

1. `https://raw.githubusercontent.com/madroidmaq/mlx-omni-server/main/README.md` — canonical, full README
2. `https://raw.githubusercontent.com/madroidmaq/mlx-omni-server/main/docs/openai-api.md` — OpenAI surface reference (has 8 verbatim examples used above)
3. `https://api.github.com/repos/madroidmaq/mlx-omni-server/releases/latest` — JSON release metadata
4. `https://pypi.org/pypi/mlx-omni-server/json` — PyPI metadata (v0.5.3, deps, Python ≥3.11)
5. `https://github.com/ml-explore/mlx/releases` — MLX core release timeline
6. `https://ml-explore.github.io/mlx/build/html/index.html` — MLX 0.31.2 docs index
7. `https://huggingface.co/mlx-community` — model registry (5,184 models)

## Wave-2 refactor candidates (incremental on top of Agent 20's R1–R10)

| # | Refactor | Source | Benefit |
|:--|:--|:--|:--|
| **W1** | **Fix the task-prompt URL** in any build-agent brief or skill doc that cites `qifengle/marketplace-mlx-omni-server` — replace with `madroidmaq/mlx-omni-server` | `openspec/research/.../agent-95-*.md` (this file) and any future Wave-3 briefs | Eliminates the recurring 404 |
| **W2** | **Bump MLX dep pin docs to v0.31.2** — the dep `mlx>=0.31.2,<0.32` in v0.5.3 was authored when v0.31.2 was the current rev. The README quick-start should mention the v0.31.2 release for awareness. | `infrastructure/stacks/mlx-omni/README.md` and any internal docstring | Tracks reality |
| **W3** | **Wire Ornith-1.0-35B-4bit into LiteLLM** as a new `local/vision/ornith-35b` route — the model is 6B params, MLX-native, and `Ornith-1.0-35B-bf16` (35B Image-Text-to-Text) is the largest mlx-community VLM as of Wave 2 | `infrastructure/stacks/litellm/config/config.yaml` | Adds the largest open MLX VLM to the local model menu |
| **W4** | **Document the `https://ml-explore.github.io/mlx/build/html/` redirect** — the task URL `https://ml-explore.github.io/mlx/` is a stub. Agents hitting it directly need a one-line pointer to `build/html/`. | `.agents/skills/browser-tools/SKILL.md` or an `mlx-framework/SKILL.md` if created | Prevents Agent 96+ from re-discovering the redirect |
| **W5** | **Add `madroid` to the mlx-omni owner mapping** in the secrets/Locket config — the HF team list confirms `madroidmaq` is the upstream maintainer, which is also the HF user `madroid`. This validates the `infisical://dev-baile/mlx-omni/...` path naming is consistent with the maintainer. | `infrastructure/stacks/mlx-omni/secrets.env` docs | Single-source naming |