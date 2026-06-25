# spaces-bundle-decomposition-v1

## Why

The `spaces/` directory houses the 4 active HuggingFace
Spaces (the Celtic AI demo suite) + the 4 new demo Spaces
(2026-06-24 batch) + 1 archived Space + 1 non-gradio
Space (the canonical exception) + the shared `_common/`
bundle. The directory has grown to 8 active Spaces + the
bundle + the docs.

Round 12 of the multi-quadrant refactor plan documents the
Spaces inventory, the bundle decomposition, the canonical
exceptions, and the add-a-new-Space workflow via:

1. **2 new skills** —
   `.agents/skills/hf-spaces-deploy/SKILL.md` (the 4 + 4 + 1
   Spaces inventory + the 4-file Space structure + the
   reusable workflow at `.github/workflows/spaces-sync.yml` +
   the 4 per-Space sync.yml wrappers + the LiteLLM gateway
   pattern) +
   `.agents/skills/gradio-ensemble-pattern/SKILL.md` (the
   `build_ensemble_interface()` helper + the
   `push_model_to_hub()` HF Hub push helper + the 3
   canonical Space structures + the 4 component patterns +
   the add-a-new-Space-theme workflow)
2. **Bundle decomposition documentation** — the
   `spaces/_common/` bundle has 12 files (theme + baml_client
   + i18n + anam_bonneagar + soulbound_svg + social_card +
   demo_recorder + hf_hub_push + cicd.md + README.md +
   AGENTS.md + __init__.py). The 2 new skills document the
   12-file bundle as the canonical Spaces foundation.
3. **OpenSpec spec delta** — 2 ADDED Requirements on
   `spaces-cicd-pipeline` (4 active Spaces + 4 new demo
   Spaces inventory; data-engineering quarantine as the
   canonical exception).

The change is the 12th round of the multi-quadrant refactor
plan (rounds 7-13). Rounds 7-11 have already landed
(infrastructure, meaisinfhoghlaim, oideachais, tuatha,
croilar).

## What changes

- `.agents/skills/hf-spaces-deploy/SKILL.md` (new)
- `.agents/skills/gradio-ensemble-pattern/SKILL.md` (new)
- `spaces/AGENTS.md` (priority skills 5 of 108 → 7 of 120
  + 2 new skill rows in the related skills section)
- `openspec/specs/spaces-cicd-pipeline/spec.md` (2 ADDED
  requirements)

## Impact

- **Spaces inventory** — the 4 + 4 + 1 + 1 Spaces are
  documented in the canonical skill + the canonical spec.
- **Bundle decomposition** — the 12-file `_common/`
  bundle is documented in the 2 new skills (the LiteLLM
  gateway + the 5-element palette + the i18n toggle + the
  Anam Bonneagar footer + the deterministic SVG + the
  social card + the HF Hub push + the demo recorder).
- **Data-engineering exception** — the canonical exception
  is documented (the only non-gradio Space; it consumes
  `sruth/oideachais/agents/adk/` + `sruth/oideachais/baml_src/`
  directly, not the LiteLLM gateway).
- **Add-a-new-Space workflow** — the 2 new skills document
  the canonical 4-step workflow (create the 4 files + wire
  the LiteLLM gateway + create the per-Space sync.yml
  wrapper + add to `spaces/AGENTS.md`).
