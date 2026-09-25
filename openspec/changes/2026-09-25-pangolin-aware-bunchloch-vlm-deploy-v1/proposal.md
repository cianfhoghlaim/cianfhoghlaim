# Change: 2026-09-25-pangolin-aware-bunchloch-vlm-deploy-v1

## Why

The bunchloch MacBook (M4 Max, 16.8 GB RAM) has 20+ vision-LLM models in `MODEL_REGISTRY`
(`meaisinfhoghlaim/models/model_registry.py`) routed through `local/unsloth/*` and
`local/vision/unsloth/*` aliases, but the `unsloth-serve` stack has never been brought up
on the bunchloch host — the 12 GGUF vision models, 2 embedders, 2 image-gen, and 2 voice
models are all unwired. Similarly, the AI Gateway surface from Pangolin (the new 2026-Q3
identity-aware AI Gateway feature per `https://pangolin.net/ai-gateway`) has not been
provisioned for any self-hosted upstream on `ai.cianfhoghlaim.ie`.

This change ships the focused slice: stand up `unsloth-serve` on bunchloch, expose it as a
Pangolin Custom provider, create 2 overlapping AI Gateway resources on `ai.cianfhoghlaim.ie`
(public + private) following the documented overlapping-FQDN pattern, wire the litellm +
MODEL_REGISTRY entries through the gateway, ship the VLM benchmark marimo notebook that
exercises the full unsloth model surface, and update `AGENTS.md` + create 3 new skills to
make the new surface discoverable for future operators.

InvokeAI + ComfyUI are deferred to sibling openspec changes (see the "What this does NOT
ship" section at the bottom).

## What Changes

### Code — new (~10 files)

**Tier 1 — bring up unsloth-serve + verify**
- `bonneagar/stacks/unsloth-serve/compose.bunchloch.yaml` already exists; bring it up
- Verify `curl :8889/v1/models` returns ≥1 GGUF

**Tier 2 — provision the AI Gateway (Pangolin UI + API)**
- 1 Custom provider (`unsloth-local`, OpenAI Chat, `http://<bunchloch-site-ip>:8889/v1`)
- 2 AI Gateway resources on shared FQDN `ai.cianfhoghlaim.ie`:
  - private (role=Member, auth=client identity, key=`none`)
  - public (auth=virtual API key, role=CI-Agent, $5/day per-role + $50/day global budget)
- Session logs → Langfuse + MLflow (already wired in the Pangolin UI)

**Tier 3 — litellm + MODEL_REGISTRY wire-up**
- 12 new `local/unsloth/*` aliases in `bonneagar/stacks/litellm/config/config.yaml`
- Update existing 20 unsloth `litellm_alias` entries in `meaisinfhoghlaim/models/model_registry.py`
- Run `pangolin configure opencode --resource ai.cianfhoghlaim.ie`
- Run `mise run ml:litellm:regenerate`

**Tier 4 — VLM benchmark marimo notebook**
- `notebooks/_shared/evaluation/vlm_registry_benchmark.py` — exercises all 12+ unsloth
  models against 3 standard prompts (NCCA syllabus PDF, LC marking scheme, OS map extract)

**Tier 5 — docs + skills**
- `AGENTS.md` — 3 new sections (Remote access, VLM surface, arm1-oci SSH)
- 3 new skills: `pangolin-cli`, `pangolin-ai-gateway`, `marimo-embed`
- `INDEXING_AND_COGNITION.md` — 4th knowledge surface row

### Specs — 3 new

- `openspec/specs/pangolin-ai-gateway-vision-bundle/spec.md` — the umbrella (overlapping
  Public+Private AI Gateway contract)
- `openspec/specs/bunchloch-unsloth-studio/spec.md` — per-server requirements
- `openspec/specs/marimo-pangolin-embed/spec.md` — auth + embed pattern

### Reference surfaces
- Pangolin docs: https://docs.pangolin.net/manage/ai/overview
- Marimo embed docs: https://docs.marimo.io/guides/publishing/embedding/
- Marimo WASM: https://docs.marimo.io/guides/exporting/webassembly_html/
- Existing `bonneagar/stacks/unsloth-serve/` (compose.yaml, compose.bunchloch.yaml, pangolin.yaml, blueprint.yaml)
- Existing `meaisinfhoghlaim/models/model_registry.py` (52 entries / 7 families)
- Existing `bonneagar/stacks/litellm/config/config.yaml`

## What this does NOT ship (deferred to follow-up openspec changes)

- **InvokeAI**: image rename `ghcr.io/invokeai/invokeai:latest` no longer resolves; needs
  pin to `v3.6.0` or replacement. → `2026-09-26-invokeai-image-fix-v1/`
- **ComfyUI stack**: new GOLD_STANDARD layout + OpenAI→ComfyUI bridge package.
  → `2026-09-26-comfyui-stack-creation-v1/`
- **VLM stacks as Custom AI Gateway providers (invokeai + comfyui)**: bundled into the
  VLM bundle change after both stacks are operational.
- **Litellm restart diagnosis**: the litellm container is in a restart loop; deferred
  to `2026-09-26-litellm-restart-diagnosis-v1/` so this change stays focused.

## Why now

- Pangolin.app is already installed and connected on bunchloch (confirmed by operator).
- SSH `oci.arm1` works from this session; the self-hosted Pangolin EE 1.21.1 + Newt 1.16.0
  are healthy on `140.238.96.148`.
- The unsloth stack already has its 6-file GOLD_STANDARD layout prepared
  (`compose.bunchloch.yaml` with CPU/MPS overrides is ready to bring up).
- The 12 GGUF models are pre-registered in `MODEL_REGISTRY` (per
  `openspec/changes/2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority-v1/`).
- Pocket ID OIDC is wired for SSO at `auth.cianfhoghlaim.ie`.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
