# pangolin-ai-gateway-vision-bundle Specification

## Purpose
TBD - created by archiving change 2026-09-25-pangolin-aware-bunchloch-vlm-deploy-v1. Update Purpose after archive.
## Requirements
### Requirement: Overlapping Public+Private AI Gateway on shared FQDN
The system SHALL provide 2 overlapping AI Gateway resources on the shared FQDN
`ai.cianfhoghlaim.ie`:

- **Resource A (private)** — reachable only via the Pangolin client tunnel
  (Pangolin.app on macOS / Pangolin CLI on Linux). Auth = client identity. Placeholder
  API key = literal string `none`. Roles granted = `Member`.
- **Resource B (public)** — reachable from anywhere on the public internet. Auth =
  virtual API key per call. Roles granted = `CI-Agent`. Each call requires a virtual API
  key scoped to this resource.

Both resources SHALL attach the same Custom providers (initially `unsloth-local`; later
`invokeai-local` and `comfyui-local` per the deferred openspec changes).

#### Scenario: Human client reaches the private resource over the Pangolin.app tunnel
- **GIVEN** the user has Pangolin.app installed and connected on their MacBook
- **WHEN** the user runs `curl -H "Authorization: Bearer none" https://ai.cianfhoghlaim.ie/v1/models`
- **THEN** the request resolves over the WireGuard tunnel to the private resource
- **AND** Pangolin forwards the call to the `unsloth-local` provider
- **AND** the response contains the 12 unsloth GGUF models

#### Scenario: CI agent reaches the public resource with a virtual API key
- **GIVEN** a CI runner has minted a virtual API key scoped to the public resource
- **WHEN** the runner runs `curl -H "Authorization: Bearer vk_<key>" https://ai.cianfhoghlaim.ie/v1/models`
- **THEN** the request resolves via the public route
- **AND** the call is attributed to the role `CI-Agent` in session logs
- **AND** the response contains the 12 unsloth GGUF models

#### Scenario: Internet call without a key fails
- **WHEN** an unauthenticated caller runs `curl https://ai.cianfhoghlaim.ie/v1/models`
- **THEN** the response is `401 Unauthorized` (the public resource rejects the call)

### Requirement: Custom provider registration
The system SHALL register each self-hosted VLM upstream as a Pangolin Custom provider with
the appropriate native API capability:

| Provider slug | api_base | Capability |
|:--|:--|:--|
| `unsloth-local` | `http://<bunchloch-site-ip>:8889/v1` | OpenAI Chat Completions |
| `invokeai-local` (deferred) | `http://<bunchloch-site-ip>:9090/v1` | OpenAI Chat Completions |
| `comfyui-local` (deferred) | `http://<bunchloch-site-ip>:9000/v1` | OpenAI Chat Completions |

#### Scenario: Provider health check
- **WHEN** the Pangolin dashboard polls each provider's `api_base/v1/models`
- **THEN** each provider returns a non-empty `data` array
- **AND** the dashboard marks the provider as `healthy`

### Requirement: Per-role + global budget caps
The public AI Gateway resource SHALL enforce per-role and global budgets:

- **Per-role budget**: `$5/day` for the `CI-Agent` role (per the dev cost envelope).
- **Global budget**: `$50/day` across all roles on the public resource.
- The private resource SHALL NOT enforce budgets (humans are trusted operators).

#### Scenario: Per-role budget exhausts mid-call
- **GIVEN** the `CI-Agent` role has already spent $5 today
- **WHEN** a new request is made with a virtual API key for that role
- **THEN** the response is `429 Too Many Requests` with a `Retry-After` header

#### Scenario: Global budget exhausts
- **GIVEN** the public resource has already spent $50 today
- **WHEN** any new request arrives
- **THEN** the response is `429 Too Many Requests`

### Requirement: Session log capture to Langfuse + MLflow
The system SHALL forward every AI Gateway call's prompt + response + metadata to:

- **Langfuse** (`:3001` internally, `langfuse-web:3000` from inside docker) — for trace-level
  prompt/response inspection
- **MLflow** (`:5050`) — for token/cost aggregation per model

Both sinks SHALL receive: `{timestamp, caller_identity, model, prompt_tokens, completion_tokens,
estimated_cost_usd, latency_ms, role, resource}`.

#### Scenario: Trace appears in Langfuse after a call
- **WHEN** a call completes against `ai.cianfhoghlaim.ie`
- **THEN** within 5 seconds the trace appears in `http://localhost:3001` under the
  `cliste-default` project with the caller identity + model + tokens populated

#### Scenario: Cost appears in MLflow within 60 seconds
- **WHEN** a call completes against `ai.cianfhoghlaim.ie`
- **THEN** within 60 seconds the cost record appears in MLflow under the
  `cliste-default` experiment with `model_name` set to the called model alias

### Requirement: Backed by a Self-Hosted Pangolin Enterprise Edition
The system SHALL be backed by the self-hosted Pangolin EE instance at
`https://pangolin.cianfhoghlaim.ie` (running `fosrl/pangolin:ee-1.21.1` on arm1-oci), with
`fosrl/newt:1.16.0` as the client connector on the bunchloch site. Both versions satisfy
the AI Gateway + browser-SSH requirements (pangolin ≥ 1.19, newt ≥ 1.13).

#### Scenario: Version check
- **WHEN** an operator runs `ssh oci.arm1 'docker exec pangolin -- pangolin --version'`
- **THEN** the response includes `1.21.x` (Enterprise Edition)
- **AND** `docker exec newt-bunchloch -- newt --version` returns `1.16.x`
- **AND** the browser-SSH feature is enabled (pangolin ≥ 1.19 + newt ≥ 1.13)

