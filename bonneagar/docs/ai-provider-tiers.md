# AI provider tiers and fallback

> One OpenAI-compatible endpoint in front of local model servers and remote
> APIs, so that applications never encode which one they're using — and so
> that the same repository works on a 48 GB workstation, an 8 GB laptop, or a
> VPS with no GPU at all.

---

## 1. The idea

Everything that consumes a model — OpenChamber, Hermes, agents, notebooks —
talks to **LiteLLM** at `:4000`, never to a provider directly.

```
                        application
                             │
                             │  OpenAI-compatible
                             ▼
                    ┌─────────────────┐
                    │ LiteLLM  :4000  │   routing, fallback, keys, budgets
                    └────────┬────────┘
        ┌────────────┬───────┴────────┬─────────────┐
        ▼            ▼                ▼             ▼
  Unsloth Studio  llama-swap      mlx-omni      Cloud APIs
  :8888           :8080           :10240        MiniMax M3, Gemini,
  fine-tunes      GGUF, dynamic   MLX, Apple    GLM, OpenAI, Anthropic
                  model swapping  Silicon only
                             │
                        transformers :5000
                        PyTorch, last resort
```

The value is that **the tiers are configuration, not architecture**. Deleting
every local tier leaves a working system that routes to APIs. Deleting every
API key leaves a working system that routes locally. Applications don't change.

---

## 2. The tiers

| Tier | Endpoint | Good at | Needs |
|---|---|---|---|
| **Unsloth Studio** | `:8888` | Serving your own fine-tunes | Local GPU/NPU |
| **llama-swap** | `:8080` | GGUF quantised models, swaps model per request so one process covers a large catalogue | Any CPU/GPU; RAM is the ceiling |
| **mlx-omni** | `:10240` | MLX-format models, fastest option on Apple Silicon | Apple Silicon only |
| **transformers** | `:5000` | Anything with no GGUF/MLX conversion | Heaviest; last resort |
| **Cloud** | vendor | Frontier capability, no local compute | API key, egress, per-token cost |

Nothing requires you to run all five. Most deployments run one or two local
tiers plus one API.

---

## 3. Choosing tiers for your hardware

The honest constraint is memory bandwidth and RAM, not model count.

| Your machine | Local tiers worth running | Realistic local ceiling | Strategy |
|---|---|---|---|
| **Apple Silicon, 8–16 GB** (e.g. M1 Air) | mlx-omni | 3B–8B quantised | **API-primary.** Local for cheap, offline and privacy-sensitive calls. |
| **Apple Silicon, 32–48 GB+** (e.g. M4 Max) | mlx-omni + llama-swap + Unsloth | 30B-class quantised, 8B comfortably | **Local-primary,** API for frontier tasks and peaks. |
| **NVIDIA GPU, Linux** | llama-swap (or vLLM), Unsloth | VRAM-dependent | Local-primary. **No mlx tier** — MLX is Apple-only. |
| **CPU-only server / VPS** | llama-swap, small models only | 1B–3B, slow | **API-primary.** Keep LiteLLM for routing and budgets. |
| **No local compute** | none | — | API-only. LiteLLM still earns its place: key rotation, fallback, cost tracking. |
| **No API budget** | whatever fits | your RAM | Local-only. Document the ceiling so nobody expects frontier behaviour. |

Two rules that survive any hardware change:

- **A weaker machine changes which tier is primary, not the architecture.** An
  M1 Air runs this repository perfectly well; it simply leans on the API tier
  where the M4 Max leans on local.
- **Keep the gateway even with a single provider.** It's what makes the
  provider swappable later, and it's where retries, fallback and spend limits
  live.

---

## 4. Fallback chains

LiteLLM declares ordered fallbacks per alias. A chain typically walks from
*specific and local* to *general and remote*:

```yaml
model_list:
  - model_name: vision
    litellm_params:
      model: openai/qwen3-vl-8b
      api_base: http://llama-swap:8080/v1

router_settings:
  fallbacks:
    - vision: [gemma-4-26B-A4B, glm-4.6v-flash, gemini/gemini-2.5-pro]
```

Design them so each hop degrades along **one** axis at a time — capability, or
locality, or vendor — never all three. A chain that jumps from a local 8B
straight to a frontier API hides both a capability cliff and a cost cliff
behind one silent retry.

---

## 5. Vendor de-risking

Our MiniMax M3 configuration is the worked example of a pattern worth copying
whenever a plan-based (rather than per-token) provider sits on the critical
path.

**Problem.** A subscription plan is a single point of failure in two ways: the
account can rate-limit, and the vendor can change terms. Either takes out
every dependent workflow at once.

**Mitigations, layered:**

1. **Key round-robin.** The `minimax` alias rotates across three keys
   (`OPENCODE_GO_API_KEY_0/1/2`), so one exhausted key doesn't stop work.
2. **A local model of the same family.** `MiniMax-M2.5-GGUF` runs under
   Unsloth/llama-swap as the fallback for the M3 chokepoint — lower capability,
   but same prompting idiom, so behaviour degrades predictably.
3. **A cross-vendor last resort.** A different vendor entirely, so a
   MiniMax-wide outage isn't total.

Generalised: **plan-based provider → same-family local model → different
vendor.** The middle step is the one people skip, and it's the one that keeps
prompt behaviour stable when the primary is unavailable.

---

## 6. Exposing model servers privately

Model servers should not be public. They're expensive to run, usually
unauthenticated, and trivially abused. Expose them as **Pangolin private
resources** — same mechanism as OpenChamber:

```yaml
private-resources:
  unsloth:
    name: Unsloth Studio
    mode: http
    scheme: http
    ssl: true
    sites: [<site-niceId>]
    destination: host.docker.internal
    destination-port: 8888
    full-domain: unsloth.example.com
    users: [you@example.com]
    roles: []
    machines: []
```

See [deploy-private-resource-from-scratch.md](deploy-private-resource-from-scratch.md).

Inside a host, containers should reach each other by container name on a shared
Docker network — don't route internal traffic through the tunnel.

---

## 7. Where the config lives

| Thing | Path |
|---|---|
| LiteLLM stack | [`../stacks/litellm/`](../stacks/litellm/) |
| Live routing config | `litellm:/app/config/config.yaml` |
| llama-swap | [`../stacks/llama-swap/`](../stacks/llama-swap/) |
| Unsloth | [`../stacks/unsloth/`](../stacks/unsloth/), [`../stacks/unsloth-serve/`](../stacks/unsloth-serve/) |
| API keys | See [../SECRETS-MANAGEMENT.md](../SECRETS-MANAGEMENT.md) |

The LiteLLM config is generated rather than hand-written
(`python scripts/generate_litellm_config.py`) — edit the generator, not the
output, or the next regeneration discards your changes.
