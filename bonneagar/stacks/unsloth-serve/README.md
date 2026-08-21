# Unsloth Serve

The Unsloth Studio headless inference server. Hosts the 3-product Unsloth
stack (Desktop + Studio + Core) as a Docker container, exposing both the
Studio UI on `:8888` and the OpenAI/Anthropic-compatible API on `:8889`.

## Why two compose override files (arm1-oci + bunchloch)?

Unsloth has different runtime requirements per host:

| Host | Image | GPU | Memory | Public? | Use case |
|:--|:--|:--|:--|:--|:--|
| **`arm1-oci`** | `unsloth/unsloth:cuda-latest` | `-ngl 99` (full GPU offload) | 12 GB | Yes (Pangolin) | Production serving for hermes/openclaw/webchat |
| **`bunchloch`** | `unsloth/unsloth:latest` | `-ngl 0` (CPU/MPS) | 8 GB | No (`127.0.0.1` only) | Dev mode + the marimo 10-way comparison notebook + the Studio UI |

The base `compose.yaml` is shared. The two override files differ only in
`image`, `LLAMA_ARG_NGL`, `deploy.resources.limits.memory`, and the
Pangolin `expose` block.

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

```bash
# Production (arm1-oci, GPU)
docker compose -f compose.yaml -f compose.arm1-oci.yaml -f sidecar.yaml up -d

# Dev mode (bunchloch, CPU/MPS)
docker compose -f compose.yaml -f compose.bunchloch.yaml -f sidecar.yaml up -d

# Verify the API is serving models
curl -s http://localhost:8889/v1/models \
  -H "Authorization: Bearer $UNSLOTH_API_KEY" | jq

# Confirm the loaded model
curl -s http://localhost:8889/v1/models \
  -H "Authorization: Bearer $UNSLOTH_API_KEY" | jq '.data[0].id'
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

## Cost

- **Compute:** 0 (runs on existing bunchloch M4 Max + arm1-oci GPU)
- **API tokens:** Saves up to ~80% of M3 plan spend during heavy agent sessions
- **Storage:** ~50 GB on the GGUF cache for 5 commonly-used quants
- **Infisical:** 1 new secret scope (`unsloth/`); 0 new projects
