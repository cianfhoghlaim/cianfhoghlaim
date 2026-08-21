# Unsloth Serve

The Unsloth Studio headless inference server. Hosts the 3-product Unsloth
stack (Desktop + Studio + Core) as a Docker container, exposing both the
Studio UI on `:8888` and the OpenAI/Anthropic-compatible API on `:8889`.

## Why two compose override files (arm1-oci + M4 Max)?

Unsloth has different runtime requirements per host (per the 2026-08-21
hotfix commit — bunchloch is the M4 Max GPU host via Apple Silicon
Metal/MLX, arm1-oci is the CPU-only host):

| Host | Image | GPU | Memory | Public? | Use case |
|:--|:--|:--|:--|:--|:--|
| **`arm1-oci`** | `unsloth/unsloth:latest` | `-ngl 0` (CPU-only, Oracle Cloud arm64) | 10 GB | Yes (Pangolin) | Production serving for hermes/openclaw/webchat |
| **`bunchloch`** | `unsloth/unsloth:latest` | `-ngl 99` (Metal/MLX, M4 Max 48 GB unified memory) | 16 GB | No (`127.0.0.1` only) | Dev mode + the marimo 10-way comparison notebook + the Studio UI |

The base `compose.yaml` is shared. The two override files differ only in
`image`, `LLAMA_ARG_NGL`, `LLAMA_ARG_THREADS`, `UNSLOTH_PLATFORM`,
`deploy.resources.limits.memory`, and the bind host.

## Deployed model

The default `unsloth run` command loads `unsloth/Qwen3.8-27B-GGUF:UD-Q4_K_XL`
(the new flagship — 5.1M downloads in 5 days post-launch). This is the
fallback for the M3 token-plan chokepoint (Kimi-K2.6 / GLM-5.1 / MiniMax-M2.5).

To serve a different model, override via env:
```bash
UNSLOTH_MODEL_ID=unsloth/DeepSeek-V4-Pro-0813-GGUF docker compose -f compose.yaml -f sidecar.yaml up -d
```

## Endpoints

| Endpoint | Port | Compatible with |
|:--|:--|:--|
| `/v1/chat/completions` | 8889 | OpenAI SDK, opencode, Cursor, Continue, Cline, Open WebUI, curl |
| `/v1/messages` | 8889 | Claude Code, Anthropic SDK, OpenClaw, hermes-agent |
| `/v1/models` | 8889 | OpenAI models list |
| Studio UI | 8888 | Any browser (Pangolin-protected) |

Both APIs support streaming, tool calling (OpenAI `tools` / Anthropic
`tools`), and vision inputs. Services: web search, code execution
(server-side), and self-healing tool calls (per Unsloth's 2026-08 API).

## 5 integrations wired in via the umbrella OpenSpec change

The 5 agent runtimes consume this server via the `unsloth start <agent>`
meta-command pattern:

| Agent | `unsloth start <agent>` |
|:--|:--|
| Claude Code | `unsloth start claude` |
| OpenAI Codex | `unsloth start codex` |
| Hermes Agent | `unsloth start hermes` |
| OpenClaw | `unsloth start openclaw` |
| OpenCode | `unsloth start opencode` |

Plus `unsloth start pi` for Pi Coding Agent.

## Usage

### Production (arm1-oci, CPU-only, public via Pangolin)

```bash
docker compose \
  -f compose.yaml \
  -f compose.arm1-oci.yaml \
  -f sidecar.yaml \
  --env-file ../../.env \
  up -d
```

The sidecar pulls `UNSLOTH_API_KEY` from Infisical via Locket.

### Dev mode (bunchloch, M4 Max MLX, local)

**Option A: With Locket sidecar (when Infisical is healthy)**

```bash
docker compose \
  -f compose.yaml \
  -f compose.m4-max.yaml \
  -f sidecar.yaml \
  --env-file ../../.env \
  up -d
```

**Option B: Without Infisical (local-dev fallback, no Locket)**

```bash
cd bonneagar/stacks/unsloth-serve/
cp .env.example .env
# edit .env to set UNSLOTH_API_KEY
docker compose \
  -f compose.yaml \
  -f compose.m4-max.yaml \
  -f compose.local-dev.yaml \
  --env-file .env \
  up -d
```

The `compose.local-dev.yaml` overlay REMOVES the Locket sidecar
dependency. The container reads `UNSLOTH_API_KEY` directly from
the mounted `.env` file.

### Verify

```bash
# Verify the API is serving models (any mode)
curl -s http://localhost:8889/v1/models \
  -H "Authorization: Bearer $UNSLOTH_API_KEY" | jq

# Confirm the loaded model
curl -s http://localhost:8889/v1/models \
  -H "Authorization: Bearer $UNSLOTH_API_KEY" | jq '.data[0].id'

# Trigger a chat completion (first load takes ~81s on M4 Max CPU)
curl -s http://localhost:8889/v1/chat/completions \
  -H "Authorization: Bearer $UNSLOTH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"unsloth/Qwen3.8-27B-GGUF","messages":[{"role":"user","content":"ping"}],"max_tokens":5}' | jq
```

## Network

The unsloth-serve container joins both `cianfhoghlaim` (the agent fleet)
and `lakehouse` (the model cache + observability). The volume mount
`../../../stedding/huggingface/unsloth:/models/unsloth:ro` is shared
with `llama-swap` — both serve the same GGUF cache.

## Secrets

A single shared secret scope:
- `infisical://dev-baile/unsloth/api_key` (the long-running daemon key)
- `infisical://dev-baile/unsloth/model_id` (the default model ID)
- `infisical://dev-baile/unsloth/otel_exporter_otlp_endpoint`

The 5 agent stacks (hermes, openclaw, openchamber, cianfhoghlaim,
openclaw-arm1-oci) all read the same key via Locket.

**Local-dev fallback:** `compose.local-dev.yaml` reads from a mounted
`.env` file at `/etc/unsloth/.env` (the entrypoint checks Locket first,
falls back to `.env` if Locket is empty).

## Cost

- **Compute:** 0 (runs on existing bunchloch M4 Max + arm1-oci)
- **API tokens:** Saves up to ~80% of M3 plan spend during heavy agent sessions
- **Storage:** ~50 GB on the GGUF cache for 5 commonly-used quants
- **Infisical:** 1 new secret scope (`unsloth/`); 0 new projects
