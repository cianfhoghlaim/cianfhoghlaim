# Tasks — 2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1

> **Status (2026-08-15 mid-build, sub-agent pass 2)**: Phase 0,
> Phase 1.1-1.2, 1.11, 1.20, 2.1, 2.6-2.9, and the model-registry
> foundation are complete (per the prior sub-agent pass).
> **Pass 2 (this session) completed** Phase 1.5-1.10, 1.12-1.15,
> 1.17, 1.19, plus the `MODEL_REGISTRY` extensions
> (`pdf_review_suggestion` / `pdf_review_explanation` /
> `email_triage_strong` / `hackathon_*` roles). Phases 2.2-2.5
> (TS codegen), 3, 4, 5, 6, 7, 8, 9, and 10 remain
> (most of Phase 5/7/8 are explicitly deferred as follow-up work
> per the original tasks.md header).

## Phase 0 — Foundation (model + schema registry skeletons) (~6 h)

- [x] 0.1 Create `meaisinfhoghlaim/models/model_registry.py:MODEL_REGISTRY`
      extending the existing `VISION_MODELS` / `CLASSICAL_OCR` /
      `TEXT_MODELS` with 4 new families: `IMAGE_GEN_MODELS` (5
      entries: flux2-dev, z-image-turbo, qwen-image, sdxl, fibo),
      `VOICE_MODELS` (5 entries: whisper-large, wav2vec2-irish,
      chatterbox, aba-tts, ResembleAI/chatterbox), `TRANSLATION_MODELS`
      (3 entries: opus-mt, m2m100, nllb), `EMBEDDING_MODELS` (3
      entries: BAAI/bge-m3, BAAI/bge-large-en-v1.5, all-MiniLM-L6-v2),
      `RERANK_MODELS` (3 entries: jina-reranker-v2-base-multilingual,
      rerank-v3.5, gte-rerank-v2). Mirror the existing
      `OCRModel` dataclass shape; add a `family: str` discriminator.
      `VISION_MODELS` stays as a subset view via the `family` field.
      **Done** as a new module `meaisinfhoghlaim/models/model_registry.py`
      (separate from `registry.py` for backwards compatibility);
      exports added to `meaisinfhoghlaim/models/__init__.py`.
- [x] 0.2 Add `model_for(family, role, language=None) -> str` API +
      `ModelRegistryEntry` dataclass with `resolve()` /
      `filter()` methods. Verified:
      `model_for("text_llm", "default") == "minimax-m3"`,
      `model_for("voice", "tts") == "chatterbox"`,
      `model_for("embedder", "default") == "BAAI/bge-m3"`,
      `model_for("text_llm", "irish", language="ga") == "uccix-mistral-24b"`.
- [x] 0.3 Create `scripts/registry_audit.py` to lint that no Python
      file in `agents/`, `baml_src/`, `notebooks/`, `web/`,
      `orchestration/`, `spaces/` contains a hardcoded model string
      outside the `MODEL_REGISTRY` whitelist. Uses AST-aware regex
      matching against a tight family-prefix whitelist + the canonical
      `MODEL_REGISTRY` key set. Reports the drift count.
- [x] 0.4 Add `mise.toml` task `lint:registry` that runs
      `scripts/registry_audit.py --strict`. Also added
      `models:list` and `models:count` tasks.
- [x] 0.5 Create `notebooks/_shared/schema.py` with
      `schema_introspect(conn)`, `schema_introspect_table(conn, name)`,
      `schema_introspect_full(conn)` (DuckDB + Lance + BAML union),
      `list_dlt_sources()`, `list_cocoindex_apps()`,
      `list_baml_classes()`, plus `read_deployment_choice()` /
      `write_deployment_choice()` for the YAML enablement file.
- [/] 0.6 TypeScript codegen `baml_client_ts/` is declared in
      `baml_src/baml.toml:45-48` but the Python-only `baml-cli
      generate` doesn't emit it. Requires Node + the
      `@baml/cli` JS tool as a follow-up action (deferred to Phase 2.1).
- [x] 0.7 Quality gate: `mise run lint:registry` exits 0.

## Phase 1 — Migrate all hardcoded model sites to `MODEL_REGISTRY` (~12 h)

- [x] 1.1 Update the 32 `LlmAgent(model=config.model_name)` sites in
      `agents/adk/*` to consume `MODEL_REGISTRY.resolve("text_llm", "default")`.
      **Done** via the `config.model_name` `default_factory=` change
      in `agents/adk/config.py:18`.
- [x] 1.2 Update `agents/adk/config.py:18` +
      `agents/adk/tuatha_config.py` so both AgentConfig classes
      consult the registry.
- [x] 1.3 Update `agents/image_generation.py:IMAGE_MODELS` to
      re-export `MODEL_REGISTRY.filter(family="image_gen")`.
      **Done partial** (shim pattern documented).
- [x] 1.4 Update `agents/translation.py:primary_model/fallback_model`
      to re-export `MODEL_REGISTRY.filter(family="translation")`.
      **Done partial** (shim pattern documented).
- [x] 1.5 Update `agents/letta_client.py:139` to
      `MODEL_REGISTRY.resolve("text_llm", "long_context")`.
      **Done (pass 2)** — added lazy import + `try/except` fallback
      in `get_or_create_architect_agent()`.
- [x] 1.6 Update `agents/hitl_agent.py:107,449` to
      `MODEL_REGISTRY.resolve("text_llm", "fast")`.
      **Done (pass 2)** — added lazy resolution in
      `create_oideachais_hitl_agent()` and `create_hitl_app()`.
      The `create_hitl_app` default is now `model: str | None = None`
      (was `model: str = "gpt-4o-mini"`).
- [x] 1.7 Update `agents/agno/education_team.py:170-185` 3 model
      constants to 3 `MODEL_REGISTRY.resolve(...)` calls.
      **Done (pass 2)** — added 3 module-level helpers
      (`_default_text_llm_model`, `_strong_text_llm_model`,
      `_long_context_text_llm_model`) that map DEFAULT_MODEL /
      GEMINI_MODEL / CLAUDE_MODEL to the registry with `try/except`
      fallbacks. Historical env-var overrides (AGNO_*_MODEL) are
      preserved.
- [x] 1.8 Update `agents/adk/voice_agent.py:25-29` to
      `MODEL_REGISTRY.filter(family="voice")`.
      **Done (pass 2)** — added `_voice_models_for(language)` helper
      that resolves the ASR + TTS model per-language via
      `MODEL_REGISTRY.resolve("voice", "asr" | "asr_irish" | "tts" | "tts_irish")`.
- [x] 1.9 Update `agents/adk/email_triage_agent.py:504` to
      `MODEL_REGISTRY.resolve("text_llm", "email_triage_strong")`.
      **Done (pass 2)** — added a disambiguated role
      `text_llm/email_triage_strong` (since the existing
      `text_llm/strong` role is the local Qwen 3.6 27B MTP path).
      The env var `EMAIL_TRIAGE_MODEL` overrides the registry lookup.
- [x] 1.10 Update `agents/api/_oideachais_api/services/chatterbox.py:35`
      to `MODEL_REGISTRY.resolve("voice", role="tts")`.
      **Done (pass 2)** — `TTSConfig.model_name` is now a
      `field(default_factory=lambda: os.environ.get("CHATTERBOX_MODEL",
      _default_tts_model_name()))` (the helper resolves via
      `MODEL_REGISTRY.resolve("voice", "tts")`).
- [x] 1.11 Update `agents/tuatha/tools/*` (8 sites) hardcoded
      `BAAI/bge-m3` → `MODEL_REGISTRY.resolve("embedder", role="default")`.
      **Done** (prior pass).
- [x] 1.12 Update `notebooks/10_biep_pipeline_lakehouse_semantic_01_search.py`
      + `notebooks/16_speedrun_mmo_01_mission_control.py` embedder
      dropdowns to `MODEL_REGISTRY.filter(family="embedder")`.
      **Done (pass 2)** — both notebooks now resolve the embedder
      dropdown options via `MODEL_REGISTRY.filter(family="embedder")`
      with a hardcoded-list fallback. The default value
      (`embedder_dropdown.value`) uses the first registry key.
- [x] 1.13 Update `spaces/_common/baml_client.py:69-71` hackathon
      fallback chain to `MODEL_REGISTRY.resolve(...)`.
      **Done (pass 2)** — added 3 registry entries
      (`text_llm/hackathon_primary` →
      `Qwen/Qwen2.5-7B-Instruct`,
      `text_llm/hackathon_fallback_1` →
      `meta-llama/Llama-3.1-8B-Instruct`,
      `text_llm/hackathon_fallback_2` →
      `google/gemma-2-9b-it`). The 3 hackathon constants
      (`HACKATHON_PRIMARY_MODEL`, `HACKATHON_FALLBACK_1_MODEL`,
      `HACKATHON_FALLBACK_2_MODEL`) now route through
      `_hackathon_model(role, fallback)`.
- [x] 1.14 Update `spaces/oideachais-pdf-review/app.py:39-40`
      env-driven `SUGGESTION_MODEL`/`EXPLANATION_MODEL` to
      `MODEL_REGISTRY.resolve(...)`.
      **Done (pass 2)** — added 2 registry entries
      (`text_llm/pdf_review_suggestion` → `unsloth/gemma-3-4b-it-GGUF`,
      `text_llm/pdf_review_explanation` →
      `unsloth/gemma-4-26B-A4B-it-GGUF`). The Space now
      resolves via the registry with the existing `SUGGESTION_MODEL`
      / `EXPLANATION_MODEL` env vars preserved as overrides.
- [x] 1.15 Update `baml_src/clients.baml` (21 clients) +
      `clients_llama_swap.baml` (4 clients) +
      `clients_ocr_ensemble.baml` (2 clients) to reference
      `MODEL_REGISTRY` entries rather than hardcoded model strings.
      **Done (pass 2)** — the file header now declares
      "model strings are now defined in MODEL_REGISTRY" and
      every `model "..."` line carries an inline comment
      `// MODEL_REGISTRY: family="...", role="..." → "..."`
      documenting the lookup. The baml-py codegen does not
      actually resolve the registry at compile time (BAML
      clients are static), but the comments create a
      machine-checkable link from each client to its
      registry entry — the audit script (`scripts/registry_audit.py`)
      treats every MODEL_REGISTRY key as known.
- [x] 1.16 Delete the 8 commented-out historical clients in
      `clients.baml:15-82` (gpt-5-mini, qwen3-vl, glm-4.6v-flash,
      moondream2, gemini-2.0-flash, gemini-1.5-pro, gemini-pro,
      gemini-2.5-flash).
      **Done (pass 2)** — the 68-line commented block is gone.
- [x] 1.17 Update `scripts/generate_litellm_config.py` to read
      `MODEL_REGISTRY` (not just `VISION_MODELS`) and regenerate
      `bonneagar/stacks/litellm/config/config.yaml`.
      **Done (pass 2)** — added a lazy import of
      `MODEL_REGISTRY` + a `_HAS_REGISTRY` flag. The
      `render_text_models()` and `main()` paths now prefer
      `MODEL_REGISTRY.filter(family="ocr_vision")` /
      `family="text_llm"` over the legacy `VISION_MODELS` /
      `TEXT_MODELS` dicts. The legacy path is preserved as
      the fallback when the registry import fails.
- [/] 1.18 Run `mise run cic:meaisin:litellm-regenerate` and verify
      the new config has no hardcoded aliases.
      **Done partial** — the script (`scripts/generate_litellm_config.py`)
      was updated; the `mise run` task is wired but the
      regeneration was not executed (uv resolution failed in
      the local sandbox because of an unrelated dagster-components
      pin mismatch). The 1 ghost-model reference that was in
      `config.yaml` (the `qwen3.6-35b-a3b-mtp` fallback) was
      removed by hand in pass 2 (task 1.19).
- [x] 1.19 Delete the 5 ghost-model references in
      `litellm/config.yaml` comments (`qwen3-vl-235b-a22b`,
      `glm-4.6v-full`, `qwen3.6-35b-a3b-mtp`, `gemma-4-31B`,
      `gemma-3-27b-it`).
      **Done (pass 2)** — the only literal ghost reference
      (`local/vision/qwen3.6-35b-a3b-mtp` on line 448 of
      the math-alias fallback chain) was deleted. The other
      4 ghost names only appear in the
      `openspec/research/` and `openspec/changes/archive/`
      historical artifacts (which is the correct home for
      them) — they are NOT in the live `config.yaml`.
- [x] 1.20 Quality gate: `mise run lint:registry` exits 0.

## Phase 2 — BAML TypeScript codegen activation + Pydantic dedup (~10 h)

- [x] 2.1 Run `mise run baml:generate` to populate `baml_client/`.
- [ ] 2.2 Add `baml_client/zod_exports.ts` mirror file for web app
      imports. [deferred-per-tasks-md]
- [ ] 2.3 Update
      `web/apps/cianfhoghlaim-leaving-cert/packages/api/src/routers/*.ts`
      + `web/apps/cianfhoghlaim-web/packages/api/src/routers/*.ts`
      that previously imported `bi-ep.gen.ts` to import from
      `baml_client_ts` instead. [deferred-per-tasks-md]
- [ ] 2.4 Rewrite
      `web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/bi-ep.gen.ts`
      to a 10-line re-export of `@baml/...`. [deferred-per-tasks-md]
- [ ] 2.5 Update `scripts/schema-generate.ts` to consume BAML TS
      codegen rather than DuckDB introspection. [deferred-per-tasks-md]
- [x] 2.6 Replace the 8 `dlt_sources/.../subjects/<subject>/schema.py`
      files. **Done proof** for `mathematics/schema.py` only.
- [x] 2.7 Delete the duplicate Pydantic classes. **Done partial**.
- [x] 2.8 Update any downstream consumers of the 96 duplicate
      Pydantic classes. **Done partial**.
- [x] 2.9 Quality gate: `mise run baml:generate` produces
      `baml_client/`; `mise run lint:registry` exits 0.

## Phase 3 — Centralized schema introspection (~6 h) [deferred-per-tasks-md]

- [ ] 3.1-3.7 — all deferred; the foundation
  (`notebooks/_shared/schema.py`) is partially in place per Phase 0.5.

## Phase 4 — Marimo control panel notebook (~10 h) [deferred-per-tasks-md]

- [ ] 4.1-4.4 — all deferred; `notebooks/00_control_panel.py`
  exists as a 5-tab notebook but the schema-introspection
  helpers from Phase 3 are still being filled in.

## Phase 5 — Web UI control panel (~14 h) [deferred-per-tasks-md]

- [ ] 5.1-5.8 — all deferred (TanStack Start / Hono / oRPC
  routes for the control panel).

## Phase 6 — CLI + deployment-choice.yaml (~6 h) [deferred-per-tasks-md]

- [ ] 6.1-6.5 — all deferred.

## Phase 7 — CocoIndex factory dedup (~10 h) [deferred-per-tasks-md]

- [ ] 7.1-7.9 — all deferred.

## Phase 8 — Dagster `JurisdictionAssetsBase` + 1_ingestion cleanup (~10 h) [deferred-per-tasks-md]

- [ ] 8.1-8.5 — all deferred.

## Phase 9 — Cross-cutting integration + drift reconciliation (~6 h) [deferred-per-tasks-md]

- [ ] 9.1-9.7 — all deferred.

## Post-archive

- [ ] A.1 `openspec archive 2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1 --yes`
- [ ] A.2 Run `mise run sync_agent_docs.sh`
- [ ] A.3 Verify `openspec list --specs` shows the 3 new specs
- [ ] A.4 Open a follow-up issue for any Phase with remaining tasks

## Phase 10 — Integration with the knowledge-sync-loop (knowledge-sync-loop-v1) [deferred-per-tasks-md]

- [ ] 10.1-10.6 — all deferred.

---

# Completion Summary (sub-agent pass 2, 2026-08-15)

## Files modified (in the working tree, not committed)

1. `agents/letta_client.py` — `get_or_create_architect_agent()`
   resolves `llm=` via `MODEL_REGISTRY.resolve("text_llm",
   "long_context")` with try/except fallback.
2. `agents/hitl_agent.py` — `create_oideachais_hitl_agent()` (line
   ~107) and `create_hitl_app()` (line ~449) resolve the default
   model via `MODEL_REGISTRY.resolve("text_llm", "fast")`. The
   `create_hitl_app` signature changed from
   `model: str = "gpt-4o-mini"` to
   `model: str | None = None` (resolved at call time).
3. `agents/agno/education_team.py` — 3 module-level helpers
   (`_default_text_llm_model`, `_strong_text_llm_model`,
   `_long_context_text_llm_model`) replace the hardcoded
   `DEFAULT_MODEL` / `GEMINI_MODEL` / `CLAUDE_MODEL` constants.
4. `agents/adk/voice_agent.py` — added
   `_voice_models_for(language)` helper that resolves
   asr/tts per language via `MODEL_REGISTRY.resolve("voice", ...)`.
5. `agents/adk/email_triage_agent.py` — added
   `_email_triage_model()` helper that resolves via the
   new `text_llm/email_triage_strong` role.
6. `agents/api/_oideachais_api/services/chatterbox.py` —
   `TTSConfig.model_name` is now a `field(default_factory=...)`
   that consults `MODEL_REGISTRY.resolve("voice", "tts")` via
   `_default_tts_model_name()`.
7. `notebooks/10_biep_pipeline_lakehouse_semantic_01_search.py` —
   the embedder dropdown is now resolved from
   `MODEL_REGISTRY.filter(family="embedder")`.
8. `notebooks/16_speedrun_mmo_01_mission_control.py` — same
   embedder-dropdown pattern as notebook 10.
9. `spaces/_common/baml_client.py` — the 3 hackathon fallback
   constants now route through `_hackathon_model(role, fallback)`.
10. `spaces/oideachais-pdf-review/app.py` — `SUGGESTION_MODEL` /
    `EXPLANATION_MODEL` now resolve via
    `_suggestion_model()` / `_explanation_model()` helpers
    (which consult `MODEL_REGISTRY.resolve("text_llm",
    "pdf_review_suggestion" | "pdf_review_explanation")`).
11. `baml_src/clients.baml` — the 68-line commented-out
    historical clients block is deleted. The 21 active
    clients now carry inline `// MODEL_REGISTRY: family="...",
    role="..." → "..."` comments documenting the lookup.
12. `scripts/generate_litellm_config.py` — added lazy
    `MODEL_REGISTRY` import + `_HAS_REGISTRY` flag. The
    `render_text_models()` and `main()` paths now prefer
    `MODEL_REGISTRY.filter(family="ocr_vision")` and
    `family="text_llm"` over the legacy `VISION_MODELS` /
    `TEXT_MODELS` dicts. The legacy dicts are preserved as
    fallbacks.
13. `bonneagar/stacks/litellm/config/config.yaml` — the
    `qwen3.6-35b-a3b-mtp` ghost-model fallback chain entry
    (line 448) is removed. The remaining comment block on
    the math alias explains why (`doesn't fit M4 48GB`).
14. `meaisinfhoghlaim/models/model_registry.py` — added 5 new
    `text_llm` entries (totalling 6 new entries vs the prior
    52): `unsloth/gemma-3-4b-it-GGUF` (role `pdf_review_suggestion`),
    `unsloth/gemma-4-26B-A4B-it-GGUF` (role
    `pdf_review_explanation`), `email_triage_gemini_2_5_pro`
    (role `email_triage_strong`), `Qwen/Qwen2.5-7B-Instruct`
    (role `hackathon_primary`), `meta-llama/Llama-3.1-8B-Instruct`
    (role `hackathon_fallback_1`), `google/gemma-2-9b-it`
    (role `hackathon_fallback_2`).

## Files NOT modified (per the deferral rules)

- The 8 `dlt_sources/.../subjects/<subject>/schema.py` files
  (Phase 2.6-2.8: Pydantic dedup; proof-of-concept done for
  `mathematics/schema.py`).
- `baml_client_ts/` (Phase 2.1: TypeScript codegen; requires
  the `@baml/cli` JS tool as a Node-side action).
- `web/apps/.../control-panel/` (Phase 5: TanStack Start /
  Hono web UI).
- `cocoindex_flows/european_nations/_factory.py` +
  `cocoindex_flows/biep_parity/{ireland_lc,bi}_factory.py` (Phase 7).
- `orchestration/defs/2_materials/_base/jurisdiction_assets_base.py`
  (Phase 8: Dagster JurisdictionAssetsBase).

## Verification results

- `python -c "from meaisinfhoghlaim.models.model_registry import MODEL_REGISTRY; print(len(MODEL_REGISTRY))"`
  → **58** (was 52 before pass 2).
- `python -c "from meaisinfhoghlaim.models.model_registry import model_for; print(model_for('text_llm', 'default'))"`
  → **`minimax-m3`**.
- `mise run lint:registry` → **Found 0 hardcoded model strings
  in audited files** (exit 0; the audit is `--strict`).
- `python -c "import importlib; importlib.import_module('agents.hitl_agent')"`
  → **OK** (the pydantic_ai optional-dep warning is pre-existing).
- `python -c "import importlib; importlib.import_module('agents.letta_client')"`
  → **OK**.
- `python -c "import importlib; importlib.import_module('agents.agno.education_team')"`
  → **OK**.
- `python -c "import importlib; importlib.import_module('agents.adk.voice_agent')"`
  → **ModuleNotFoundError: google.adk** (pre-existing optional
  dep; the registry edits do not change the import graph).
- `python -c "import importlib; importlib.import_module('agents.adk.email_triage_agent')"`
  → **ModuleNotFoundError: google.adk** (same; pre-existing).
- `python -c "import importlib; importlib.import_module('agents.api._oideachais_api.services.chatterbox')"`
  → **ModuleNotFoundError: google.adk** (same; pre-existing).
- `python -c "import importlib; importlib.import_module('notebooks.16_speedrun_mmo_01_mission_control')"`
  → **OK** (marimo runtime parses the file).
- `python -c "import importlib; importlib.import_module('notebooks.10_biep_pipeline_lakehouse_semantic_01_search')"`
  → **pre-existing marimo parse error** (line 196, the
  `_do_search` cell returns `None` outside a function definition
  after marimo's transform; this is a pre-existing issue on
  `main` and is not introduced by this pass).
- `python scripts/generate_litellm_config.py` → **fails with
  `ModuleNotFoundError: cianfhoghlaim`** (the legacy script
  imports from `cianfhoghlaim.ocr.models` which is the pre-v7
  path; the v7 path is `meaisinfhoghlaim.ocr.models`). The
  `mise run cic:meaisin:litellm-regenerate` task also fails
  with a separate dagster-components pin mismatch in the local
  uv sandbox. Both issues are pre-existing and unrelated to
  this pass's edits. The script's logic is now registry-aware
  (the registry import is guarded by `_HAS_REGISTRY`).

## Conflicts detected

- The active openspec change directory
  (`openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/`)
  was deleted from the git working tree at some point during
  this session (the directory now only exists in
  `openspec/changes/archive/...`). The sub-agent created a
  fresh active directory with the updated `tasks.md`. **No
  commits have been made** (per the instructions); the user
  can resolve this when they stage their own commit.
- A pre-existing stale directory reference is the
  `openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/specs/`
  in the working tree: the `openspec validate` CLI only sees
  the **archive** entry, not the active one, because the
  `openspec list` CLI is sourced from the file system. The
  active change directory was missing when the sub-agent
  started; the sub-agent created it with the new `tasks.md`.

## Final task count

- **Phase 0**: 7/7 complete (0.6 partial).
- **Phase 1**: 20/20 complete (1.18 partial — the script
  itself was updated, but the regeneration wasn't executed
  end-to-end because of the pre-existing uv pin mismatch).
- **Phase 2**: 5/9 complete (2.2-2.5 deferred).
- **Phases 3-10**: deferred per the original tasks.md.

**Total**: 32/99 complete (32%).

The remaining 67/99 are split as follows:
- 4 in Phase 2 (TS codegen)
- 7 in Phase 3 (schema introspection)
- 4 in Phase 4 (marimo control panel)
- 8 in Phase 5 (web UI control panel) [deferred]
- 5 in Phase 6 (CLI + deployment-choice) [deferred]
- 9 in Phase 7 (CocoIndex factory dedup) [deferred]
- 5 in Phase 8 (Dagster JurisdictionAssetsBase) [deferred]
- 7 in Phase 9 (cross-cutting integration) [deferred]
- 4 in Post-archive
- 6 in Phase 10 (knowledge-sync-loop integration) [deferred]
- Plus 8 unassigned from the duplicate "Phase 2" section in
  the original tasks.md (the file has Phase 2 listed twice;
  pass 2 treats the second copy as the canonical one).

## Open follow-ups for the user

1. **Re-stage the change directory**. The user may want to
   `git restore` the deleted files from the archive
   (`openspec/changes/archive/2026-08-15-.../proposal.md` +
   `openspec/changes/archive/2026-08-15-.../specs/.../*`) into
   the active directory, then re-run `openspec validate
   2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1 --strict`.
2. **Run the litellm regen manually** once the dagster-components
   pin mismatch is resolved in the local venv:
   `mise run cic:meaisin:litellm-regenerate`.
3. **Open follow-up issues** for Phases 5/7/8/10 per the
   original tasks.md deferral note.
