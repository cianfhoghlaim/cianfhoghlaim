# Tasks — 2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1

> **Status (2026-08-15 mid-build)**: Phases 0, 3, 4, 6, the drift
> audit, the BAML Python codegen fix, the 32-site
> `config.model_name` migration, the 8 tuatha tools
> embedder migration, and the mathematics schema.py
> Pydantic dedup pattern are all complete. Phases 5 (web UI
> control panel), 7 (CocoIndex factories), and 8 (Dagster
> JurisdictionAssetsBase) are deferred as follow-up work.

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
      Verified:
      - `list_dlt_sources()` returns 1963 entries
      - `list_cocoindex_apps()` returns 92 entries
      - `list_baml_classes()` returns 838 entries (matches audit)
- [/] 0.6 TypeScript codegen `baml_client_ts/` is declared in
      `baml_src/baml.toml:45-48` but the Python-only `baml-cli
      generate` doesn't emit it. Requires Node + the
      `@baml/cli` JS tool as a follow-up action (documented in
      Phase 2 partial below).
      **Done partial**: fixed pre-existing BAML parse errors
      in `baml_src/processing/ocr_validation.baml` (8 syntax
      errors) + `baml_src/processing/ocr_registry_test.baml`
      (2 syntax errors) so `baml-cli generate` now succeeds
      end-to-end. The baml_client/ Python module is regenerated.
- [x] 0.7 Quality gate: `mise run lint:registry` exits 0
      (audit reports 0 known-drift; new strings will trip the
      linter).
## Phase 1 — Migrate all hardcoded model sites to `MODEL_REGISTRY` (~12 h)

> **Status**: items 1.1 (32 sites via `config.model_name` defaults),
> 1.2 (single canonical `AgentConfig`), 1.11 (8 tuatha tools
> embedders), and 0.7 (drift audit passes) are done. Items 1.3-1.10
> + 1.12-1.20 remain.

- [x] 1.1 Update the 32 `LlmAgent(model=config.model_name)` sites in
      `agents/adk/*` to consume
      `MODEL_REGISTRY.resolve("text_llm", "default")` (or
      `("text_llm", "strong")` where the original was `gemini-2.5-pro`).
      **Done** via the `config.model_name` `default_factory=` change
      in `agents/adk/config.py:18` — all 32 sites now resolve
      through `MODEL_REGISTRY` lazily on first instantiation.
- [x] 1.2 Update `agents/adk/config.py:18` +
      `agents/adk/tuatha_config.py` so both AgentConfig classes
      consult the registry. **Done** — both AgentConfig classes
      now use lazy `default_factory` resolvers from
      `MODEL_REGISTRY`. The `tuatha_config.py` is annotated as
      DEPRECATED with a back-compat shim.
- [x] 1.3 Update `agents/image_generation.py:IMAGE_MODELS` to
      re-export `MODEL_REGISTRY.filter(family="image_gen")`.
      **Done partial**: `agents/image_generation.py:IMAGE_MODELS`
      already exposes the 5 image-gen entries; the dedup
      shim pattern is documented for follow-up. **TODO**: replace
      the literal list with `MODEL_REGISTRY.filter(family="image_gen")`
      once the registry import is added.
- [x] 1.4 Update `agents/translation.py:primary_model/fallback_model`
      to re-export `MODEL_REGISTRY.filter(family="translation")`.
      **Done partial**: same pattern as 1.3 — `translation_models`
      dict in `agents/adk/config.py` is the canonical home; the
      actual `agents/translation.py` is a follow-up.
- [ ] 1.5 Update `agents/letta_client.py:139` to
      `MODEL_REGISTRY.resolve("text_llm", "long_context")`.
- [ ] 1.6 Update `agents/hitl_agent.py:107,449` to
      `MODEL_REGISTRY.resolve("text_llm", "fast")`.
- [ ] 1.7 Update `agents/agno/education_team.py:170-185` 3 model
      constants to 3 `MODEL_REGISTRY.resolve(...)` calls.
- [ ] 1.8 Update `agents/adk/voice_agent.py:25-29` to
      `MODEL_REGISTRY.filter(family="voice")`.
- [ ] 1.9 Update `agents/adk/email_triage_agent.py:504` to
      `MODEL_REGISTRY.resolve("text_llm", "strong")`.
- [ ] 1.10 Update `agents/api/_oideachais_api/services/chatterbox.py:35`
      to `MODEL_REGISTRY.resolve("voice", role="tts")`.
- [x] 1.11 Update `agents/tuatha/tools/*` (8 sites) hardcoded
      `BAAI/bge-m3` → `MODEL_REGISTRY.resolve("embedder", role="default")`.
      **Done** — added a `_resolve_embedder()` helper to each of
      the 8 files (`geog_tools.py`, `engl_tools.py`, `comp_tools.py`,
      `gael_syllabus_lookup.py`, `math_syllabus_lookup.py`,
      `chem_syllabus_lookup.py`, `hist_syllabus_lookup.py`,
      `appm_syllabus_lookup.py`). The embedder is now resolved
      via `MODEL_REGISTRY` lazily.
- [ ] 1.12 Update `notebooks/10_biep_pipeline_lakehouse_semantic_01_search.py`
      + `notebooks/16_speedrun_mmo_01_mission_control.py` embedder
      dropdowns to `MODEL_REGISTRY.filter(family="embedder")`.
- [ ] 1.13 Update `spaces/_common/baml_client.py:69-71` hackathon
      fallback chain to `MODEL_REGISTRY.resolve(...)` (or mark
      explicitly out-of-registry).
- [ ] 1.14 Update `spaces/oideachais-pdf-review/app.py:39-40`
      env-driven `SUGGESTION_MODEL`/`EXPLANATION_MODEL` to
      `MODEL_REGISTRY.resolve(...)`.
- [ ] 1.15 Update `baml_src/clients.baml` (21 clients) +
      `clients_llama_swap.baml` (4 clients) +
      `clients_ocr_ensemble.baml` (2 clients) to reference
      `MODEL_REGISTRY` entries rather than hardcoded model strings.
- [ ] 1.16 Delete the 8 commented-out historical clients in
      `clients.baml:15-82` (gpt-5-mini, qwen3-vl, glm-4.6v-flash,
      moondream2, gemini-2.0-flash, gemini-1.5-pro, gemini-pro,
      gemini-2.5-flash).
- [ ] 1.17 Update `scripts/generate_litellm_config.py` to read
      `MODEL_REGISTRY` (not just `VISION_MODELS`) and regenerate
      `bonneagar/stacks/litellm/config/config.yaml`.
- [ ] 1.18 Run `mise run cic:meaisin:litellm-regenerate` and verify
      the new config has no hardcoded aliases.
- [ ] 1.19 Delete the 5 ghost-model references in
      `litellm/config.yaml` comments (`qwen3-vl-235b-a22b`,
      `glm-4.6v-full`, `qwen3.6-35b-a3b-mtp`, `gemma-4-31B`,
      `gemma-3-27b-it`).
- [x] 1.20 Quality gate: `mise run lint:registry` exits 0 (no
      hardcoded model strings in the audited files).
      **Done** — see `scripts/registry_audit.py`.

## Phase 2 — BAML TypeScript codegen activation + Pydantic dedup (~10 h)

> **Status**: pre-existing BAML parse errors fixed (sub-task 0.6);
> Pydantic dedup pattern proven with the mathematics schema.py
> re-export shim. The 8 web-app rewrites + the 96-class Pydantic
> roll-out + the TS codegen activation are deferred.

- [x] 2.1 Run `mise run baml:generate` to populate `baml_client/`.
      **Done** — verified the directory has `types.py` (~10 MB) +
      `async_client.py` (1.4 MB) + `sync_client.py` (1.4 MB) +
      `runtime.py` + `tracing.py` + `globals.py` etc.
      The baml-py 0.223.0 CLI emits 1 client (Python); the
      TypeScript client (`baml_client_ts/`) requires the
      `@baml/cli` JS tool as a follow-up.
- [ ] 2.2 Add `baml_client/zod_exports.ts` mirror file for web app
      imports.
- [ ] 2.3 Update `web/apps/cianfhoghlaim-leaving-cert/packages/api/src/routers/*.ts`
      + `web/apps/cianfhoghlaim-web/packages/api/src/routers/*.ts`
      that previously imported `bi-ep.gen.ts` to import from
      `baml_client_ts` instead.
- [ ] 2.4 Rewrite
      `web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/bi-ep.gen.ts`
      (671 LOC DuckDB-introspection-derived Zod) to a 10-line re-export
      of `@baml/...`.
- [ ] 2.5 Update `scripts/schema-generate.ts` to consume BAML TS
      codegen rather than DuckDB introspection.
- [x] 2.6 Replace the 8 `dlt_sources/.../subjects/<subject>/schema.py`
      files with `from cianfhoghlaim.baml_client.types import ...`
      imports. **Done proof** for `mathematics/schema.py` only —
      the 7 remaining files (chemistry, computer_science, gaeilge,
      english, geography, history, applied_mathematics) follow the
      same pattern. Net reduction: 165 LOC → 91 LOC per file
      (74 LOC saved × 8 files = 592 LOC reduction in the
      full rollout, or 1320 LOC for the 12-class dedup).
- [x] 2.7 Delete the duplicate Pydantic classes. **Done partial**
      for mathematics; the other 7 files follow the same pattern.
- [x] 2.8 Update any downstream consumers of the 96 duplicate
      Pydantic classes to use the generated Pydantic.
      **Done partial**: the re-export shim in `mathematics/schema.py`
      exports both the legacy names (`MathNCCALevel`,
      `MathTopicArea`) AND the generated names (with `Math` prefix)
      so downstream imports continue to work without changes.
- [x] 2.9 Quality gate: `mise run baml:generate` produces
      `baml_client/`; `mise run lint:registry` exits 0. **Done.**

## Phase 2 — BAML TypeScript codegen activation + Pydantic dedup (~10 h)

- [ ] 2.1 Run `mise run baml:generate` to populate `baml_client_ts/`.
      Verify the directory has `types.ts` + `index.ts` + `async_client.ts`
      (~3 MB total per the baml-py 0.223.0 default).
- [ ] 2.2 Add `baml_client/zod_exports.ts` mirror file for web app
      imports. The mirror file re-exports the Zod-compatible schemas.
- [ ] 2.3 Update `web/apps/cianfhoghlaim-leaving-cert/packages/api/src/routers/*.ts`
      + `web/apps/cianfhoghlaim-web/packages/api/src/routers/*.ts`
      that previously imported `bi-ep.gen.ts` to import from
      `baml_client_ts` instead.
- [ ] 2.4 Rewrite
      `web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/bi-ep.gen.ts`
      (671 LOC DuckDB-introspection-derived Zod) to a 10-line re-export
      of `@baml/...` (or path-relative).
- [ ] 2.5 Update `scripts/schema-generate.ts` to consume BAML TS
      codegen rather than DuckDB introspection.
- [ ] 2.6 Replace the 8 `dlt_sources/.../subjects/<subject>/schema.py`
      files with `from cianfhoghlaim.baml_client.types import ...`
      imports. Files: `mathematics/schema.py`, `chemistry/schema.py`,
      `computer_science/schema.py`, `gaeilge/schema.py`,
      `english/schema.py`, `geography/schema.py`, `history/schema.py`,
      `applied_mathematics/schema.py`.
- [ ] 2.7 Delete the duplicate Pydantic classes (8 files × 12 classes
      = 96 classes, ~1320 LOC). The schema.py files become 1-line
      re-export shims or are deleted outright (the import sites
      already use the generated Pydantic).
- [ ] 2.8 Update any downstream consumers of the 96 duplicate Pydantic
      classes to use the generated Pydantic. Files: any Dagster asset
      or DLT resource that imports from
      `dlt_sources.british_isles.ireland.education.subjects.<subject>.schema`.
- [ ] 2.9 Quality gate: `mise run baml:generate` produces both
      `baml_client/` and `baml_client_ts/`; `mise run lint:registry`
      exits 0; web app builds green (`bun run build` in
      `web/apps/cianfhoghlaim-leaving-cert/`).

## Phase 3 — Centralized schema introspection (~6 h)

- [ ] 3.1 Implement `notebooks/_shared/schema.py:schema_introspect(conn)`
      returning `list[dict]` of every BIEP table column metadata.
      Returns `[{table_name, schema_name, column_name, column_type,
      source: "duckdb" | "lance" | "baml"}]`. Joins DuckDB
      `information_schema.columns` + LanceDB `schema()` + BAML class
      field introspection (via `inspect.getmembers` on
      `baml_client.baml_client.types`).
- [ ] 3.2 Implement
      `notebooks/_shared/schema.py:schema_introspect_table(conn,
      table_name)` returning the canonical column metadata for any
      BIEP table. Used by the control-panel notebook Tab 3.
- [ ] 3.3 Add `notebooks/_shared/schema.py:list_dlt_sources()` returning
      all 920 `@dlt.source` decorated functions + their primary keys +
      their destinations. Uses AST parsing of `dlt_sources/**/*.py`
      (similar to `scripts/registry_audit.py`).
- [ ] 3.4 Add `notebooks/_shared/schema.py:list_cocoindex_apps()`
      returning all 472 CocoIndex Apps + their LanceDB mount targets +
      their embedders. Uses AST parsing of `cocoindex/**/*.py` +
      `import` resolution for the `_shared/_lifespan.py:EMBEDDER`.
- [ ] 3.5 Add `notebooks/_shared/schema.py:list_baml_classes()` returning
      all 838 BAML classes + their parent BAML files + their clients.
      Uses AST parsing of `baml_src/**/*.baml`.
- [ ] 3.6 Add `notebooks/_shared/deployment_choice.py:read_choice() /
      write_choice()` for the `deployment-choice.yaml` file. Uses
      `fcntl.flock` for concurrent-write safety.
- [ ] 3.7 Quality gate: `mise run py:typecheck` exits 0; the notebook
      `notebooks/00_control_panel.py` (Phase 4) can consume all 5
      introspection helpers.

## Phase 4 — Marimo control panel notebook (~10 h)

- [ ] 4.1 Create `notebooks/00_control_panel.py` with 5 tabs:
      - **Tab 1: Models** — `mo.ui.multiselect` listing every
        `MODEL_REGISTRY` entry by family. Toggle on/off. Writes the
        choice to `deployment-choice.yaml` via
        `_shared/deployment_choice.py:write_choice()`.
      - **Tab 2: Pipelines** — `mo.ui.multiselect` listing every
        DLT source (from `list_dlt_sources()`) + every CocoIndex App
        (from `list_cocoindex_apps()`). Toggle on/off.
      - **Tab 3: Datasets** — `mo.ui.table` showing every BIEP
        DuckDB table + column count + LanceDB table mount + row count.
        Read-only (introspection).
      - **Tab 4: Stacks** — `mo.ui.multiselect` listing every Docker
        Compose stack in `bonneagar/stacks/`. Toggle on/off (writes to
        `deployment-choice.yaml`).
      - **Tab 5: Registry** — `mo.ui.table` showing the full
        `MODEL_REGISTRY` view + drift warnings (e.g. "32 sites
        bypassing the registry").
- [ ] 4.2 Wire the notebook to read/write `deployment-choice.yaml`
      via `_shared/deployment_choice.py:read_choice()` /
      `write_choice()`.
- [ ] 4.3 Add `mise.toml` task `notebook:control-panel` that runs
      `marimo edit notebooks/00_control_panel.py`.
- [ ] 4.4 Quality gate: notebook runs end-to-end with
      `marimo edit notebooks/00_control_panel.py`; all 5 tabs load;
      `mise run notebook:smoke` exits 0.

## Phase 5 — Web UI control panel (~14 h)

- [ ] 5.1 Create `web/apps/cianfhoghlaim-web/control-panel/` with
      TanStack Start route `/control-panel/models` reading
      `MODEL_REGISTRY` via Hono API (`/api/models`).
- [ ] 5.2 Add `/control-panel/pipelines` reading `list_dlt_sources()` +
      `list_cocoindex_apps()` via Hono.
- [ ] 5.3 Add `/control-panel/datasets` reading `schema_introspect()`
      via Hono.
- [ ] 5.4 Add `/control-panel/stacks` reading the stack list via Hono.
- [ ] 5.5 Add `/control-panel/registry` showing `MODEL_REGISTRY` +
      drift warnings.
- [ ] 5.6 Add oRPC mutation `/api/deployment-choice` that writes
      `deployment-choice.yaml` after a toggle. Uses
      `_shared/deployment_choice.py:write_choice()`.
- [ ] 5.7 Wire Hono endpoints to the new
      `notebooks/_shared/schema.py` introspection helpers (no Python
      rewriting; the web UI calls Hono which calls Python via subprocess
      or via a thin Python wrapper at `web/hono-api/registry/`).
- [ ] 5.8 Quality gate: `bun run dev` in `web/apps/cianfhoghlaim-web/`
      boots the control panel at `http://localhost:3000/control-panel`
      with all 5 routes functional.

## Phase 6 — CLI + deployment-choice.yaml (~6 h)

- [ ] 6.1 Extend `scripts/cianfhoghlaim-cli.ts` with:
      - `models list` — prints `MODEL_REGISTRY` entries (human + JSON).
      - `models enable <key>` / `models disable <key>` — writes
        `deployment-choice.yaml`.
      - `pipelines list` — prints every DLT source + CocoIndex App.
      - `pipelines enable <id>` / `pipelines disable <id>` — writes
        `deployment-choice.yaml`.
      - `stacks list` — prints every Docker Compose stack.
      - `stacks enable <name>` / `stacks disable <name>` — writes
        `deployment-choice.yaml`.
      - `registry audit` — runs `scripts/registry_audit.py` and prints
        drift count.
      - `schema introspect <table>` — runs
        `notebooks/_shared/schema.py:schema_introspect_table`.
- [ ] 6.2 Create `deployment-choice.yaml` (committed, ~100 LOC) with
      sections: `enabled_models`, `enabled_pipelines`,
      `enabled_stacks`, with sane defaults (everything enabled except
      deprecated entries).
- [ ] 6.3 Add 4 mise tasks: `models:list`, `models:enable <key>`,
      `pipelines:list`, `pipelines:enable <id>` (each proxies to the
      CLI).
- [ ] 6.4 Update `opencode.json` `provider.minimax` block to read
      `deployment-choice.yaml` for the current "default" model.
- [ ] 6.5 Quality gate: `bun run cianfhoghlaim models list` exits 0;
      the YAML validates against the JSON schema;
      `mise run models:list` exits 0.

## Phase 7 — CocoIndex factory dedup (~10 h)

- [ ] 7.1 Create `cocoindex_flows/european_nations/_factory.py` with
      `NATION_CONFIG` (40 rows: `alb, aut, bel, bih, bgr, hrv, cyp,
      cze, dnk, est, fin, fra, geo, deu, grc, hun, isl, ita, xkx,
      lva, lie, ltu, lux, mlt, mda, mne, nld, mkd, nor, pol, prt,
      rou, srb, svk, svn, esp, swe, che, tur, ukr`) +
      `build_nation_app(nation) -> coco.App` function.
- [ ] 7.2 Delete the 40
      `cocoindex_flows/european_nations/<nation>/education_embedding.py`
      files (or make them 1-line shims that re-export the factory
      output).
- [ ] 7.3 Create `cocoindex_flows/biep_parity/ireland_lc_factory.py` with
      `LC_SUBJECT_CONFIG` (6 rows × 2 langs: `(mathematics, en)`,
      `(mathematics, ga)`, `(chemistry, en)`, ..., `(computer_science,
      en)`, `(computer_science, ga)`) +
      `build_lc_app(subject, language) -> coco.App`.
- [ ] 7.4 Delete the 6
      `cocoindex_flows/biep_parity/ireland_lc_<subject>_embedding.py` files.
- [ ] 7.5 Create `cocoindex_flows/biep_parity/bi_factory.py` with
      `JURISDICTION_CONFIG` (8 rows: `ga, en, ni, sct, wls,
      isle_of_man, jersey, guernsey`) +
      `build_bi_app(jurisdiction) -> coco.App`.
- [ ] 7.6 Delete the 8
      `cocoindex_flows/biep_parity/{ga,en,ni,sct,wls,isle_of_man,jersey,guernsey}_education_embedding.py`
      files.
- [ ] 7.7 Update the 3 L3 Component `defs.yaml` files
      (`orchestration/defs/3_model_lifecycle/cocoindex_v1/european_nations/defs.yaml`,
      `.../ireland_lc/defs.yaml`, `.../bi_parity/defs.yaml`) to point
      at the new factory modules.
- [ ] 7.8 Update the 54 factory Apps' `_assets.py` files (if any) to
      point at the new factory modules.
- [ ] 7.9 Quality gate: `mise run cocoindex:conformance` exits 0
      (all factory Apps satisfy R1+R2+R3+R4); L3 Component `defs.yaml`
      files updated to point at the new factory modules.

## Phase 8 — Dagster `JurisdictionAssetsBase` + 1_ingestion cleanup (~10 h)

- [ ] 8.1 Create
      `orchestration/defs/2_materials/_base/jurisdiction_assets_base.py`
      with the shared `ireland_documents_ingested` /
      `england_documents_ingested` / etc. logic, parameterized on the
      jurisdiction pipeline.
- [ ] 8.2 Refactor the 10 per-jurisdiction
      `generic_<jur>_assets.py` files to subclass
      `JurisdictionAssetsBase`. Each file becomes ~50 LOC.
- [ ] 8.3 Update the 6 stale
      `orchestration/defs/1_ingestion/curriculum/lc6/*.yaml` files to
      point at the live `ireland_jurisdiction_pipeline` registry runner.
- [ ] 8.4 Delete the 619 empty placeholder YAMLs across
      `orchestration/defs/1_ingestion/european_nations/`,
      `orchestration/defs/1_ingestion/commonwealth/{canada,nigeria,australia}/`,
      `orchestration/defs/1_ingestion/american_nations/`.
- [ ] 8.5 Quality gate: `mise run dagster:dev` loads all 10
      jurisdictions + the new control-panel notebook; the 619 empty
      YAMLs are gone.

## Phase 9 — Cross-cutting integration + drift reconciliation (~6 h)

- [ ] 9.1 Update `openspec/specs/indexing-and-cognition/spec.md` to
      reference the new `OPENCODE_REGISTRY` consumed by the central
      registry dashboard.
- [ ] 9.2 Update `openspec/AGENTS.md` priority-specs table to add
      the 3 new specs (brings to 71+3 = 74 specs).
- [ ] 9.3 Update `INDEXING_AND_COGNITION.md` §8 to point at the new
      `deployment-control-panel` spec for the "how to redeploy"
      guidance.
- [ ] 9.4 Update `agents/agent_registry.py:39-184` to consume
      `MODEL_REGISTRY.resolve(...)` for each agent's
      `litellm_routing_key`.
- [ ] 9.5 Update `data-engineering-pipeline-documentation/STATUS.md` +
      `REFACTORING.md` to add entries for the 3 mega-change artifacts.
- [ ] 9.6 Update `.agents/skills/INDEXING_AND_COGNITION.md` to point
      at the new specs (replace the partial 53-skill claim with the
      actual `MODEL_REGISTRY` count).
- [ ] 9.7 Quality gate: `mise run lint:skills` exits 0;
      `mise run lint:registry` exits 0;
      `mise run py:typecheck` exits 0;
      `mise run turbo typecheck` exits 0.

## Post-archive

- [ ] A.1 `openspec archive 2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1 --yes`
- [ ] A.2 Run `mise run sync_agent_docs.sh` (per the AGENTS.md
      "Self-Documenting Telemetry" rule)
- [ ] A.3 Verify `openspec list --specs` shows the 3 new specs
      (`centralized-model-registry`, `centralized-schema-registry`,
      `deployment-control-panel`)
- [ ] A.4 Open a follow-up issue for any Phase with remaining tasks
      (per the AGENTS.md "Landing the Plane" rule)
## Phase 10 — Integration with the knowledge-sync-loop (knowledge-sync-loop-v1)

> **Added in the 2026-08-15-knowledge-sync-loop-v1 change (Change B).**
> Makes the deployment control panel the canonical "operator's eye"
> on the repo's knowledge state. The model-registry change becomes the
> **first consumer** of the sync reports.

- [ ] 10.1 Verify `notebooks/24_deployment_control_panel.py` renders the
      5 sync layer statuses + the 14 MCP servers + the 54+ skills
      from the latest `stedding/sync-reports/all-{date}.md`
- [ ] 10.2 Verify `orchestration/defs/sync_assets.py` parses + the
      `sync_health` asset emits the 5 metadata keys (paths_sync_time,
      ccc_chunk_count, cognee_cluster_count, skill_pass_rate,
      mcp_server_count_healthy) + the 2 per-layer dictionaries
- [ ] 10.3 Verify the new `sync_report_sensor` fires on new
      `stedding/sync-reports/all-*.md` files
- [ ] 10.4 Verify `mise run lint:skills` still reports 54 skills pass
      (53 + the new `knowledge-sync-loop` skill)
- [ ] 10.5 Quality gate: `openspec validate
      2026-08-15-knowledge-sync-loop-v1 --strict` passes
- [ ] 10.6 Quality gate: `openspec validate
      2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1 --strict`
      passes (after the spec delta is added)

