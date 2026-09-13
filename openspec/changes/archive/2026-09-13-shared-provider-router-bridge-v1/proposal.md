# Change: Bridge the shared provider_router into cianfhoghlaim

## Why

Per `openspec/changes/cianchosaint-handoff-v1/proposal.md` §4
(drift #1), `baml_src/_shared/provider_router.py` exists in
`cianchosaint` (the sister fork) but is **missing** from
`cianfhoghlaim`. This violates the Shared-1 contract codified
by `cianchosaint-handoff-v1` — every sister repo MUST carry
the 4-tier ModelProviderRouter module.

Without it, `cianfhoghlaim`'s `baml_src/clients.baml` falls
back to ad-hoc client wiring (no per-call routing, no fallback
chain, no emergency tier). Carrying the wholesale copy from
`cianchosaint/baml_src/_shared/provider_router.py` closes the
drift and brings cianfhoghlaim into spec compliance.

## What changes

- New file: `baml_src/_shared/provider_router.py` — wholesale
  copy of `cianchosaint/baml_src/_shared/provider_router.py`
  with the cianfhoghlaim `Provider` enum extended to cover
  the cianfhoghlaim-specific backends (the 6 hackathon HF
  Inference fallbacks + the centralised model-registry
  M3 chokepoint aliases).
- New `baml_src/_shared/provider_router_config.yaml` —
  cianfhoghlaim-local fallback configuration.

## Impact

- **Affected code**: `baml_src/_shared/` (new files only — no
  existing code modified)
- **Affected specs**: `sister-shared` (Shared-1 requirement now
  satisfied by cianfhoghlaim)

## Pre-flight checklist

- [ ] `diff /Users/cianmacandeisigh/dev/cianfhoghlaim/baml_src/_shared/provider_router.py /Users/cianmacandeisigh/dev/cianchosaint/baml_src/_shared/provider_router.py | wc -l` returns a small number (wholesale copy + local extensions only).
- [ ] `openspec validate 2026-09-13-shared-provider-router-bridge-v1 --strict` exits 0.

## Out of scope

- No new BAML client changes (existing `clients.baml` is left
  as-is — the provider_router is a routing helper, not a
  BAML client).
- No sister-repo changes (cianchosaint already has it;
  gemini_hackathon's standalone model_registry.py is the
  gemini_hackathon-specific equivalent, addressed by the
  sister-umbrella codification).
