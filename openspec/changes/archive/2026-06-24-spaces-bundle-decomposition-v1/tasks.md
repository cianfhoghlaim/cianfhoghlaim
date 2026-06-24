# Tasks for spaces-bundle-decomposition-v1

## 1. Two new skills

- [x] 1.1 Create `.agents/skills/hf-spaces-deploy/SKILL.md`
  (the 4 + 4 + 1 + 1 Spaces inventory + the 4-file Space
  structure + the reusable workflow at
  `.github/workflows/spaces-sync.yml` + the 4 per-Space
  sync.yml wrappers + the LiteLLM gateway pattern)
- [x] 1.2 Create `.agents/skills/gradio-ensemble-pattern/SKILL.md`
  (the `build_ensemble_interface()` helper + the
  `push_model_to_hub()` HF Hub push helper + the 3
  canonical Space structures + the 4 component patterns +
  the add-a-new-Space-theme workflow)

## 2. Spaces AGENTS.md update

- [x] 2.1 Update `spaces/AGENTS.md` (priority skills 5 of
  108 → 7 of 120 + 2 new skill rows in the related skills
  section)

## 3. Spec delta

- [x] 3.1 ADDED Requirement "8 active Spaces + 1 archived
  Space + 1 canonical exception" (the full inventory)
- [x] 3.2 ADDED Requirement "data-engineering quarantine"
  (the canonical exception — the only non-gradio Space;
  it consumes oideachais/agents/adk/ + oideachais/baml_src/
  directly, not the LiteLLM gateway)

## 4. Validation + commit + push + archive

- [ ] 4.1 Run `openspec validate spaces-bundle-decomposition-v1 --strict`
- [ ] 4.2 Run `mise run lint:skills` to verify the 2 new skills
- [ ] 4.3 Commit + push
- [ ] 4.4 Run `openspec archive spaces-bundle-decomposition-v1 --yes`
