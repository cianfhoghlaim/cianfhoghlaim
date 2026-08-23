# Tasks — Tuatha Media-Intel + Gameplay-Capture Research v1

Each task is sized for ≤1 day of focused work. Every task is gated
by `openspec validate <id> --strict` at the spec-delta level + the
standard mise gates (`lint`, `py:typecheck`, `turbo typecheck`,
`openspec:validate-all`, `lint:drift-docs`, `lint:registry`,
`devops:validate-stacks`) at the implementation level.

## Phase 1 — Reference-corpus spine + the 4 NEW stacks (~10 days)

- [x] **T1.1** Verify the change artifact set is valid: `proposal.md`,
  `tasks.md`, `design.md`, `PHASING.md`, `cross-repo-sync.md` are
  written; the 3 NEW spec dirs (`media-intel-corpus`,
  `media-intel-acquisition-plan`, `celtic-history-research`) each
  have `spec.md` + `AGENTS.md`; the 5 MODIFIED spec dirs have
  their delta `spec.md` files (carried over from the prior
  turn).

- [x] **T1.2** Author the 5 BAML files under `baml_src/media/`:
  - `comic_descriptor.baml` (Class A — Hickman FF + Avengers +
    Secret Wars + Krakoan X-Men; `ExtractComicDescriptor` →
    `qwen3-vl-8b` default via MODEL_REGISTRY)
  - `prose_descriptor.baml` (Class B — Wheel of Time; the
    saidar/saidin/Tel'aran'rhiod/One Power contract;
    `ExtractProseDescriptor` → `qwen3.6-27b-mtp` default via
    MODEL_REGISTRY)
  - `animation_descriptor.baml` (Class C — ATLA + Korra + Aang
    film; air/water/fire/earth/spirit; `ExtractAnimationDescriptor`
    → `molmo2-8b` default via MODEL_REGISTRY)
  - `gameplay_descriptor.baml` (Class D — Hades boon system +
    Golden Sun Djinn/Psynergy + Pokémon type chart + WoW role
    design; `ExtractGameplayDescriptor` → `qwen3-vl-8b` default
    for image + structured session_log)
  - `official_document_descriptor.baml` (Class E — NCCA + SEC +
    DfE + SQA + WJEC + DESC + Met Éireann + OSi + Met Office +
    Wikipedia + CELT + Dúchas; `ExtractOfficialDocumentDescriptor`
    → `olmocr-2-7b` default via MODEL_REGISTRY)
  Each function emits the 7-axis `MediaDescriptor` (power_event,
  visual_grammar, palette, vfx_vocabulary, narrative_beat,
  transferability, provenance) with `shippable: false` enforced.
  Each function routes through `MODEL_REGISTRY.resolve(family=
  "ocr_vision", role="media_descriptor")` only — no hardcoded
  model strings.

- [x] **T1.3** Author the 5 v1 DLT sources under
  `dlt_sources/media/<class>/<work>/`:
  - `comics/hickman_marvel/` — `source.yaml` (Firecrawl plan
    A, VLM `qwen3-vl-8b`, BAML `ExtractComicDescriptor`,
    LanceDB `media_descriptors`, DuckLake
    `cianfhoghlaim.media`) + `scrape.py`
    (`@dlt.resource(marvel_hickman_panel_descriptors, write_disposition=
    "merge", primary_key=("work", "source_url", "source_timestamp"))`)
  - `prose/wheel_of_time/` — `source.yaml` (plan A, VLM
    `qwen3.6-27b-mtp`, BAML `ExtractProseDescriptor`) +
    `scrape.py` (Wikisource + Wikipedia summary pull)
  - `animation/atla_korra_aang_film/` — `source.yaml` (plan A,
    VLM `molmo2-8b`, BAML `ExtractAnimationDescriptor`) +
    `scrape.py` (Wikipedia + Avatar wiki concept-art thumb pulls)
  - `games/hades_wow_golden_sun_pokemon/` — `source.yaml`
    (n/a Firecrawl — local capture via `sunshine` for
    Hades/WoW + `libretro-retroarch` for Golden Sun/Pokémon; VLM
    `qwen3-vl-8b`; BAML `ExtractGameplayDescriptor`) +
    `capture.py` (orchestrates the 3 macro scripts and emits
    screenshots + session_log to `stedding/ingest_queue/retro/`)
  - `official/ncca_sec_celt_duchas_wikipedia/` — `source.yaml`
    (plan A, VLM `olmocr-2-7b`, BAML
    `ExtractOfficialDocumentDescriptor`) + `scrape.py`
    (the 2 NCCA research PDFs + the 12 NCCA LC syllabus PDFs)
  Each source declares `shippable_default: false`.

- [x] **T1.4** Stand up the 4 NEW Docker Compose stacks as
  6-file GOLD_STANDARD artifacts (per the `infrastructure-stacks`
  spec):
  - `bonneagar/stacks/comfyui/{compose.yaml, sidecar.yaml,
    secrets.env, pangolin.yaml, blueprint.yaml, .env.example}`
    (ComfyUI node-graph image gen wired to `unsloth-serve` + HF
    models from the *same providers* as the OCR_VISION-24 family;
    exposes :8188 to avoid collision with the lakehouse :8181)
  - `bonneagar/stacks/libretro-retroarch/{...6 files...}`
    (headless libretro + 6 cores: Mesen, snes9x, gambatte,
    mgba, genesis_plus_gx, pcsx_rearmed; deterministic macro
    execution via the libretro netcommand interface)
  - `bonneagar/stacks/sam3-server/{...6 files...}` (Facebook
    SAM3 image segmentation, Apache 2.0)
  - `bonneagar/stacks/sam3d-objects-server/{...6 files...}`
    (Facebook SAM-3D-Objects sprite-to-3D, Apache 2.0)
  Add Komodo procedures at
  `bonneagar/komodo/procedures/deploy-<name>-{bunchloch,arm-oci}.toml`.
  Add Infisical secret entries via
  `bun run scripts/init-vault.ts`.
  Run `mise run devops:validate-stacks` — must pass.

- [x] **T1.5** Author the 2 CocoIndex v1 Apps:
  - `cocoindex_flows/media_intel/media_descriptors.py` (mounts
    `media_descriptors_lance` table)
  - `cocoindex_flows/media_intel/cross_medium_compare.py`
    (mounts `media_descriptors_cross_medium_lance` table; the
    multihop search that surfaces the *consistent visual
    grammar* across ATLA + WoT prose + Hickman)
  Both R1–R4 conformant per `dagster-5-layer-component-architecture`.
  Shared embedder: `BAAI/bge-m3` 1024-d (per
  `cocoindex_flows/_lifespan.py:107`).
  Run `bun run ccc:index`.

- [x] **T1.6** Add the 1 new entry to
  `agents/agent_registry.py:AGENT_REGISTRY` (fleet 13 → 14):
  - `media_descriptor_agent` (ADK; the 10-tool media-intel
    extractor; routes through
    `MODEL_REGISTRY.resolve(family="ocr_vision", role="media_descriptor")`)
  Each tool wraps one of the 5 BAML functions + 5 corpus
  introspection tools.
  Register with the Cognee dataset
  `oideachais_media_descriptors` and the Langfuse trace
  `agent.media_descriptor.extract`.

- [x] **T1.7** Add the 5-layer Dagster asset group at
  `orchestration/defs/media_intel.py`:
  - L1 Ingestion: 5 DLT source assets (one per media class)
  - L2 Materials: 5 BAML extraction assets
  - L3 Model Lifecycle: 2 CocoIndex Apps
  - L4 Asset Generation: 2 marimo notebooks
  - L5 Agent Ops: 1 ADK `media_descriptor_agent` execution
    asset
  + the `media_descriptor_coverage` asset check (Dagster
  sensor; fails the run if any of the 5 source classes has 0
  rows in `media_descriptors_lance`).

- [x] **T1.8** Author the 2 marimo notebooks:
  - `notebooks/media_intel_explorer_per_medium.py` — per-medium
    coverage table (Row count per class, sample descriptors,
    per-axis field histograms, top 5 most-cited source URLs)
  - `notebooks/media_intel_explorer_cross_medium.py` — the
    cross-medium comparator the question "which element's
    visual grammar is most consistent across WoT prose + ATLA
    animation + Hickman comics" answers. The cell-level SQL
    runs DuckDB over the LanceDB tables joined with the
    BAML-typed records.

- [x] **T1.9** Refresh `notebooks/00_control_panel.py` with a
  "Media Intel Coverage" tab showing the 5-class descriptor
  counter, the asset check status, the most-recently-ingested
  source URL, the per-class row count.

- [x] **T1.10** Run the 6 quality gates (must all pass before
  commit):
  - `openspec validate 2026-08-23-tuatha-media-intel-gameplay-capture-research-v1 --strict`
  - `mise run openspec:validate-all`
  - `mise run lint:drift-docs`
  - `mise run lint:registry` (must remain 0)
  - `mise run devops:validate-stacks` (after the 4 new
    stacks)
  - `mise run lint`
  - `mise run py:typecheck`
  - `mise run turbo typecheck`
  - `bun run ccc:index` (refresh the index)

## Phase 2 — Mid-flight refactor: the Class E drift fix (2026-08-23)

The change was refactored mid-execution to address the user's
drift correction: the prior draft of Class E committed 12
Wikipedia pages (Tuatha Dé Danann, Irish mythology, etc.) as
official sources. The brief corrected this — the Celtic-history
Wikipedia pages were MOVED to a stubbed class for the downstream
theming change, and the Class E official surface was REPLACED
with 3 government sub-buckets + 5 departments sub-buckets (36
official records total).

- [x] **T2.1** Refactor `dlt_sources/media/official/
  ncca_sec_celt_duchas_wikipedia/scrape.py` — keep the 2 NCCA
  research PDFs + 12 NCCA LC syllabus PDFs (the educational
  body sub-bucket), DELETE the Wikipedia resource. Update
  `source.yaml` to remove the 12 Wikipedia entries from
  `input_sources`.

- [x] **T2.2** Create 9 stub Celtic-history research sources at
  `dlt_sources/media/celtic_history_research/{tuatha_de_danann,
  irish_mythology, celtic_mythology, celtic_law, brehon_law,
  aran_islands, isle_of_skye, isle_of_man, dyfed}/` (9 ×
  `source.yaml` + 9 × no-op `scrape.py` = 18 files). All gated
  for the downstream theming change.

- [x] **T2.3** Create 3 government DLT sources:
  - `dlt_sources/media/official/government/uk/` — UK police
    (Met + BTP + PSNI) + UK defence (MoD + British Army + Royal
    Navy + RAF) + UK Home Office + FCDO + MoJ + DoH + 7 UK Acts
    + Treaties = 18 records
  - `dlt_sources/media/official/government/ie/` — Garda + Irish
    Defence Forces + Naval + Air Corps + DoD + DoJ + DFA +
    Oireachtas + Office of the President + 6 Acts + Treaties =
    15 records
  - `dlt_sources/media/official/government/crown_dependencies/`
    — IoM Government + IoM Constabulary + Tynwald + IoM Courts
    + States of Jersey + States of Guernsey = 8 records

- [x] **T2.4** Create 5 departments DLT sources:
  - `dlt_sources/media/official/departments/uk/` — NHS England
    + DWP + Transport + Education + DEFRA
  - `dlt_sources/media/official/departments/ie/` — DoH (IE) +
    DoEdu (IE) + HSE
  - `dlt_sources/media/official/departments/sct/` — NHS Scotland
    + Education Scotland + Scottish Government
  - `dlt_sources/media/official/departments/wls/` — NHS Wales
    + HEIW + Welsh Government
  - `dlt_sources/media/official/departments/ni/` — DoH (NI) +
    DE (NI) + DfE (NI) + nidirect

- [x] **T2.5** Refactor
  `agents/meaisinfhoghlaim/media_intel/media_descriptor_agent.py` +
  `__init__.py` to match the `academic_history_agent.py` shape:
  - @dataclass Tool registry (10 tools: 5 per-medium extractors
    + 5 corpus introspection)
  - `_BAML_AVAILABLE` + `_FIRECRAWL_AVAILABLE` +
    `_MEMORY_BACKEND_AVAILABLE` graceful degradation
  - `_build_wire()` factory → `media_descriptor_agent_wire`
    singleton
  - bilingual EN/GA summary surface (matches the
    `bilingual_extraction` invariant)
  - `run_tool(name, **kwargs)` dispatcher
  - `list_tools()` + `TOOL_NAMES` set

- [x] **T2.6** Create the new `celtic-history-research` spec at
  `openspec/changes/.../specs/celtic-history-research/{spec.md,
  AGENTS.md}` — the canonical surface for the 9 stub sources
  (gated for the downstream theming change).

- [x] **T2.7** Rewrite `media-intel-acquisition-plan/spec.md` +
  `AGENTS.md` — drop the 12 Wikipedia entries, add the new
  government + departments sources (36 official records),
  per-source `rights_holder` / `licence` / `category`
  decomposition.

- [x] **T2.8** Update `orchestration/defs/media_intel.py` to
  register the 8 new DLT source assets (15 → 23 total assets:
  5 L1 media-class + 8 L1 official sub-bucket + 5 L2 BAML + 2
  L3 CocoIndex + 2 L4 marimo + 1 L5 ADK agent). The 8 new L1
  assets: `ncca_sec_dfe_sqa_wjec_desc_l1`, `uk_government_l1`,
  `ie_government_l1`, `crown_dependencies_government_l1`,
  `uk_departments_l1`, `ie_departments_l1`, `sct_departments_l1`,
  `wls_departments_l1`, `ni_departments_l1`.

- [x] **T2.9** Update `mise.toml` — replace the single
  `data:media-intel:official-pdfs` task with 8 per-jurisdiction
  tasks + 1 educational-bodies task (9 tasks total in the
  `data:media-intel:*` namespace).

## Phase 3 — Mid-flight documentation sync (2026-08-23)

The 5 root files (`proposal.md` / `tasks.md` / `design.md` /
`PHASING.md` / `cross-repo-sync.md`) were written in the
initial build BEFORE the Phase 2 refactor. They describe the
original 12-Wikipedia-entries version of Class E. The Phase 3
documentation sync rewrites them to reflect the post-refactor
implementation (the 36 official records + the 9 Celtic-history
stubs + the 10-tool agent + the 23 Dagster assets + the 8
per-jurisdiction mise tasks).

- [x] **T3.1** Update `proposal.md` — rewrite the "Why" +
  "What changes" + "Impact" sections to reflect the refactored
  Class E (36 official records across 3 sub-buckets) + the 9
  Celtic-history stub sources + the 10-tool agent.
- [x] **T3.2** Update `tasks.md` — rewrite to reflect T1-T13
  (the actual task list) + the new spec deltas (the 3 NEW
  spec delta dirs).
- [x] **T3.3** Update `design.md` — drop the Celtic-Elemental
  world canon sections (those went away with the trimmed
  scope); add the Class E refactor section + the
  celtic-history-research stub class section + the drift fix
  section.
- [x] **T3.4** Update `PHASING.md` — rewrite to reflect the
  3 phases (Phase 1 = reference-corpus spine + 4 NEW stacks;
  Phase 2 = the Class E refactor; Phase 3 = the documentation
  sync).
- [x] **T3.5** Verify `cross-repo-sync.md` — single-repo, no
  edit needed.

## Phase 4 — Agentic gameplay capture at scale (deferred to v2)

- [ ] **T4.1** Stand up `sunshine` + `moonlight` + `ludusavi` on
  `bunchloch` (host machine that owns Hades 1/2 + WoW). Wire
  the libretro-headless capture loop for Golden Sun via the
  new `libretro-retroarch` stack on `arm-oci`. Confirm
  `bun run preflight:arm-oci` passes before any IaC
  bootstrap.

- [ ] **T4.2** Author the 3 deterministic macro scripts:
  - `golden_sun_title_to_venus_lighthouse.py` (head from the
    start to the first Djinn fight; capture the overworld,
    the menu, the party screen, the Djinn-equip screen, the
    first battle)
  - `hades_1_first_boon_roll.py` (capture the first 10
    boon-grant UI states, the boon-rarity-orb icon variants,
    the Mirror/Arcana meta-progression menus)
  - `wow_first_quest_chain.py` (capture the first level-1
    quest's HUD + the power-usage frames during the first
    combat)
  Store outputs in `stedding/ingest_queue/retro/{gba/
  golden_sun, hades_1, world_of_warcraft}/` per the
  `retro-game-design-catalogue` spec.

- [ ] **T4.3** Wire `sam3-server` to segment the Djinn
  sprites from Golden Sun + the boon-orb icons from Hades.
  Store the segments + the sprite masks in the
  `retro_sprite_masks` Convex table (per the
  `retro-game-design-catalogue` spec).

- [ ] **T4.4** Run the cross-medium explorer. Verify a
  sensible answer to "which element's visual grammar is
  most consistent across WoT prose + ATLA animation + Hickman
  comics" — i.e. the 7-axis similarity score for the
  `palette + vfx_vocabulary` subset is well-defined across
  the 3 sources.

- [ ] **T4.5** Re-run `mise run sync:all` + the 6 quality
  gates. Re-validate the change. All must pass.

## Phase 5 — Stubbed comics + British Isles parity (deferred to v2)

- [ ] **T5.1** Add 5 stubbed comic-class sources with
  `source.yaml` but no materialisation: Morrison `Batman
  Incorporated`, Tomasi `Super Sons`, Johns `Green Lantern`,
  Valiant `Harbinger`, Gillen `The Power Fantasy`. The
  plugin-style registry handles the no-op.

- [ ] **T5.2** Add British Isles parity sources: SQA CfE
  (Scotland), WJEC CfW (Wales), DESC (Isle of Man), Gaelic
  Council sources. Each as a stub `source.yaml` under
  `dlt_sources/media/celtic_history_research/` (Celtic
  history future) + the BIEP v3 educational body surface.

- [ ] **T5.3** Final `mise run sync:all` + the archive gate.

## Out of scope tasks (deferred to the downstream Celtic-MMO design change)

- The 4+1 element world canon
- The Cymru-Wales+England / Aran Islands / Isle of Skye /
  Isle of Man / Dyfed sub-nation binding
- The anam currency + earn/spend/decay rule system
- The Hades-style boon-for-homework loop
- The anamcara NFT familiar mechanic
- The 2D particle renderer choice
- The iOS delivery vehicle decision
- The 60-subject agent surface per `per-subject-agents` spec
- The full Parnell-3 + Cromien-7 marimo dashboards

## Cross-cutting invariants (apply to every task)

- **MODEL_REGISTRY only**: no hardcoded model strings anywhere
- **BAML as source of truth**: Pydantic + Zod + Convex + DuckLake
  DDL are all codegen
- **Use `mcp_apps_builder` for any MCP server work** (per the
  `mcp-apps-builder` skill)
- **Concurrent-write safety**: every file edit uses the
  `git status/diff` → edit → `git status/diff` → `git add <path>`
  protocol
- **Read `agents/WEB_INTEGRATION.md` before touching any web app**
- **Never hand-edit `.env`**: use `mise run secrets:init`
- **Never bypass the Hono API gateway**: every backend call goes
  through `web/hono-api/`
- **Never create a per-app `convex/`**: all apps share
  `apps/oideachais-dashboard/convex/`
- **Description-only invariant**: every `MediaDescriptor` has
  `shippable: false`; shippable art is a downstream concern
  derived from the descriptor (and never via a re-render of
  copyrighted source material)
- **Per-source `rights_holder` correctness**: the issuing body
  (e.g., "An Garda Síochána", "Metropolitan Police Service",
  "Ministry of Defence", "Crown copyright"), NEVER "Wikipedia
  Foundation" (Wikipedia Foundation is the Wikipedia host, not
  the original publisher)
- **Per-source `licence` correctness**: CC-BY-SA-4.0 for the 9
  Celtic-history stubs (Wikipedia attribution preserved); OGL-3.0
  for UK gov + Crown copyright Acts; PSI for Éire gov + Crown
  copyright Acts; fair-use-description for the NCCA educational
  body PDFs
