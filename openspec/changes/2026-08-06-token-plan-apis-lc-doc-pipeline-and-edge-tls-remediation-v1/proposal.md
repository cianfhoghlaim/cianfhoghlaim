# Change: Token-plan API orchestration (MiniMax + Qwen), LC document processing, and edge TLS remediation

## Why

Three problems converged on 2026-08-06:

1. **The MiniMax coding plan was blocked by an unrouted edge hostname.**
   Every opencode agent (build, plan, and all 12 subagents) is pinned to
   `minimax/MiniMax-M3`, whose provider `baseURL` pointed at
   `https://litellm.cianfhoghlaim.ie` — an endpoint that was **never actually
   live**, not one that "drifted". That edge — together with
   `langfuse.cianfhoghlaim.ie` — serves the self-signed
   `CN=TRAEFIK DEFAULT CERT` instead of a Let's Encrypt certificate
   (OpenSSL **verify return code 21** → the exact Node/Bun error
   `unable to verify the first certificate`).
   **Root cause, verified live 2026-08-07 (corrects the original diagnosis
   below):** the arm1-oci Traefik ACME resolver is healthy — the resolver
   name already matches every stack's `certResolver: letsencrypt`,
   `CLOUDFLARE_DNS_API_TOKEN` is already set, and DNS-01 is not even used
   by this resolver (it issues via HTTP-01; 4 certs are currently valid:
   `pangolin`, `auth`, `infisical`, `openchamber`). The actual cause is that
   **Traefik has no router for `litellm`/`langfuse`/`vikunja`/`n8n`/
   `glance`/`changedetection`/`paperless` at all** — none of these hostnames
   were ever registered as Pangolin resources, so requests fall through to
   the default certificate. See the corrected `infrastructure-stacks` spec
   delta for the full diagnosis, including a second, independent fault
   (private resources bound to offline sites) that produces `HTTP 000`
   rather than a certificate error on `infisical`/`openchamber`/`komodo`.

2. **Two flat-rate token plans were paid for but not wired in.** The user
   holds a **MiniMax coding plan** (MiniMax-M3: frontier coding/agentic
   model, MSA attention, 1M context, native multimodality; direct endpoints
   `https://api.minimax.io/anthropic` + `https://api.minimax.io/v1`) and a
   **Qwen Cloud token plan** (served via the DashScope API platform at
   `https://coding.dashscope.aliyuncs.com/v1` — verified live 2026-08-06,
   serving `qwen3.7-plus`, `qwen3-coder-next`, `qwen3-coder-plus`,
   `qwen3-max-2026-01-23`, plus third-party `glm-5`, `kimi-k2.5`,
   `MiniMax-M2.5` under the same plan; Anthropic-compatible path at
   `/apps/anthropic`). Neither endpoint was registered in the
   `MODEL_REGISTRY`, the `.infisical.env` template, or opencode providers,
   so none of the priority openspec backlog or the Leaving Certificate
   corpus could be processed at flat-rate token-plan economics.

3. **The Leaving Certificate corpus is staged but unprocessed.**
   `leaving_certificate/` holds 13 subjects × (EN + GA) PDFs — syllabi
   (`SCSEC09_*_syllabus_*`), guideline material, specifications
   (`SC-*-Specification-*`), and exam papers (`LC022ALP000EV.pdf`,
   `LC022GLP000EV.pdf`, …) — that must flow through the BIEP v3 5-phase
   pattern (Ingestion → Extraction → Embedding → ibis logging → Analytics)
   using the token-plan text APIs for BAML extraction.

## What changes

- **Edge TLS remediation + verification gate** (capability
  `infrastructure-stacks`): new `scripts/check-edge-tls.sh` gate that fails
  on any OpenSSL verify code ≠ 0; a runbook to repair the arm1-oci Traefik
  ACME resolver (resolver-name match + Cloudflare DNS-01 token + restart);
  wiring of the gate into `iac:health`.
- **Localhost-first fallback policy** (capability
  `infrastructure-stacks`): while the edge certificate is broken,
  `LITELLM_BASE_URL` resolves to `http://localhost:4000/v1` and
  `LANGFUSE_HOST` to `http://localhost:3000`; opencode gains a
  `litellm_local` provider. The public edge URLs are documented for
  restoration once the ACME repair lands.
- **Token-plan API registration** (capability `centralized-model-registry`):
  the MiniMax coding-plan direct endpoints and the Qwen token-plan
  (DashScope) endpoints become registered, env-var-driven routing targets
  (`MINIMAX_API_KEY` + `MINIMAX_BASE_URL`, `DASHSCOPE_API_KEY` +
  `DASHSCOPE_BASE_URL`); opencode providers consume them (the `minimax`
  provider now points at `https://api.minimax.io/anthropic`; the new `qwen`
  provider reads `{env:DASHSCOPE_BASE_URL}` so the coding-plan vs
  international-console endpoint is a one-line `.env` switch).
- **Leaving Certificate document processing via token-plan APIs**
  (capability `british-isles-education-pipeline-v3`): the 13-subject
  EN+GA corpus is processed by the 5-phase pattern with MiniMax-M3 as the
  primary BAML extraction client, `qwen3.7-plus` as the secondary, and the
  local llama-swap `qwen3-vl-8b` OCR path as the offline fallback; rows land
  in DuckLake `cianfhoghlaim.leaving_cert.*` and are introspectable via
  `schema_introspect`.
- **Opencode prompt pack** for executing this change, the priority openspec
  backlog, and the LC pipeline with the two token plans:
  `docs/plans/2026-08-06-token-plan-opencode-prompts.md`.

## Impact

- Affected specs: `infrastructure-stacks`, `centralized-model-registry`,
  `british-isles-education-pipeline-v3`.
- Affected code/config: `opencode.json` (4 providers: minimax direct, qwen,
  litellm_local, opencode_go), `.infisical.env` (token-plan section +
  LANGFUSE_HOST + LITELLM_BASE_URL), `scripts/check-edge-tls.sh` (new),
  `meaisinfhoghlaim/models/model_registry.py` (token-plan endpoint
  entries), `baml_src/clients.baml` (MINIMAX_BASE_URL hydration),
  `dlt/british_isles/ireland/education/` (LC filesystem source),
  `orchestration/defs/2_materials/` (LC assets).
- No secret values are written to disk: all keys resolve via
  `infisical://dev-baile/...` template refs hydrated by mise + Locket.

## Out of scope

- Repairing the arm1-oci Traefik certificate **from this repo** (the actual
  server-side mutation happens on arm1-oci per the runbook in tasks.md; this
  change ships the gate, the runbook, and the fallback policy).
- The `2026-08-15-meaisinfhoghlaim-to-machine-learning-rename-v1` change
  (independent; remains pending).
- Fine-tuning or Unsloth work (separate capability).

## Dependencies

Blocked by: none.
Blocks: any change that restores `https://litellm.cianfhoghlaim.ie` or
`https://langfuse.cianfhoghlaim.ie` as a consumer-facing endpoint (the edge
MUST pass `scripts/check-edge-tls.sh --strict` first).
