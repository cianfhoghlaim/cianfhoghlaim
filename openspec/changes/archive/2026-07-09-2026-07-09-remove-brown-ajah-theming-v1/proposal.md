# Change: 2026-07-09-remove-brown-ajah-theming-v1

## Why

`openspec/specs/cianfhoghlaim-leaving-cert-portal/spec.md`, `openspec/specs/agentic-frontend-frameworks/spec.md`, and `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` all reference the **Brown Ajah Wheel of Time theming** — Aes Sedai / Amyrlin Seat / Dragon Reborn / Dragon Banner / Tuatha'an + the "Aes Sedai — servants of all" tagline.

The user no longer wants this theming. Per their preference:

> "we will be using mythology historical sources only long after full and proper official professional british isles educational pipelines"

The mythology/historical-sources layer will be added **long after the full BIEP v1 lands**. For now, the openspec just describes a professional minimal theming without the Brown Ajah / WoT lens.

R10 (Cian Mac an Déisigh Uí Liatháin personal bio) is **kept but rephrased** — the operator's triple-crown lineage is independent of the WoT mapping and doesn't belong in this cleanup.

## What changes

**A. `openspec/specs/cianfhoghlaim-leaving-cert-portal/spec.md` — REMOVE R7 + strip WoT body.** Replace the WoT theming paragraph with a minimal professional placeholder. Drop the "8 Brown Ajah members" / "Amyrlin Seat" / "Dragon Reborn" / "Tuatha'an" mappings. The 8 NCCA subject specialists stay referenced as the 8 subject agents.

**B. `openspec/specs/agentic-frontend-frameworks/spec.md` — REMOVE R6 + strip the Theming/Tagline rows.** Drop the "Aes Sedai" / "Brown Ajah" / "Khan mastery → Brown Ajah éraic" references.

**C. `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` — KEEP R10 but REPHASE.** Drop the "Aes Sedai + Amyrlin Seat + Dragon Reborn + Dragon Banner + Tuatha'an" framing, the "Brown Ajah only" public-theming line, and the "Aes Sedai — servants of all" tagline scenario. The operator's personal lore (Cian Mac an Déisigh Uí Liatháin + triple-crown lineage) stays as operator-only content.

**D. `openspec/project.md` — Update Plan 1.5.** Replace the "Themed as the Brown Ajah of the Wheel of Time" line with a deferral note: "(mythology/historical-sources theming deferred to BIEP-v2)".

## What does NOT change

- 50+ archived openspec changes under `openspec/changes/archive/*` (point-in-time artifacts per the `openspec/AGENTS.md` rule)
- 12 component code files in `cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/` (out of scope; owned by the 6th `frontend-apps` subagent engagement)
- `docs/BROWN_AJAH_THEMING.md` + `docs/CIANFHLOGHLAIM_LORE.md` (both referenced but never created on disk)
- `openspec/specs/tuatha-platform/spec.md` (already a deprecated alias per the cianfhoghlaim-educational-mmo spec)
- `cianfhoghlaim/tests/test_subject_router.py` (asserts "Brown Ajah ↔ Tuatha Dé mapping"; out of scope for openspec)
- `cianfhoghlaim/tuatha/asset_generation/fibo/education_fibo.py` (comments reference Brown Ajah theming; out of scope for openspec)
- `bonneagar/stacks/changedetection/README.md` (lists "The Wheel of Time" as a watch item; can change in a follow-up)
- The 4 openspec changes I just shipped (5-tangent-modernization, BIEP-v1, dlthub-platform-integration, end-to-end-llm-zoomcamp-style-tutorial) — all clean

## Files (4 edited)

- `openspec/specs/cianfhoghlaim-leaving-cert-portal/spec.md` (R7 REMOVED + body text edited)
- `openspec/specs/agentic-frontend-frameworks/spec.md` (R6 REMOVED + Theming/Tagline rows removed)
- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` (R10 REPHASED, tagline scenario removed)
- `openspec/project.md` (Plan 1.5 line updated)

## New openspec change files (5 created)

- `openspec/changes/2026-07-09-remove-brown-ajah-theming-v1/proposal.md` (this file)
- `openspec/changes/2026-07-09-remove-brown-ajah-theming-v1/tasks.md`
- `openspec/changes/2026-07-09-remove-brown-ajah-theming-v1/specs/cianfhoghlaim-leaving-cert-portal/spec.md`
- `openspec/changes/2026-07-09-remove-brown-ajah-theming-v1/specs/agentic-frontend-frameworks/spec.md`
- `openspec/changes/2026-07-09-remove-brown-ajah-theming-v1/specs/cianfhoghlaim-educational-mmo/spec.md`

## Acceptance

- `openspec validate 2026-07-09-remove-brown-ajah-theming-v1 --strict` passes
- `ccc search "Brown Ajah"` in `openspec/specs/` (active only, excluding `openspec/changes/archive/`) returns 0 matches in the 3 cleaned specs
- `ccc search "Wheel of Time"` in the 3 cleaned specs returns 0 matches
- `ccc search "Aes Sedai" "Amyrlin Seat" "Dragon Reborn" "Dragon Banner" "Tuatha'an"` in the 3 cleaned specs returns 0 matches
- The 3 cleaned specs still validate as canonical (each retains ≥5 requirements after the R6/R7 REMOVED + R10 REPHASED)
- `mise run lint:skills` still passes

## Cross-references

- This is a **cleanup change** — no new capability spec, no spec delta requirements ADDED
- The mythology/historical-sources theming is owned by a future post-BIEP-v1 change (per the user's preference)
- The 6th `frontend-apps` subagent engagement (Tangent 6 from the 5-tangent plan) will clean up the component code