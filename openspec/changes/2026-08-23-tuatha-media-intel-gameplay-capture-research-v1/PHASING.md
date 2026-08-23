# Phasing — Tuatha Media-Intel + Gameplay-Capture Research v1

## Phase 1 — Reference-corpus spine + the 4 NEW stacks (~10 days) — DONE

**Goal**: ship the 5-class source registry + the 7-axis
medium-agnostic `MediaDescriptor` schema + the 5 v1 BAML
extractors + the 5 v1 DLT sources + the 4 NEW docker
stacks + the 2 CocoIndex v1 Apps + the `media_descriptor_agent`
ADK agent + the 2 marimo notebooks.

**Scope** (all done):

- 5 BAML files (`baml_src/media/comic_descriptor.baml` +
  `prose_descriptor.baml` + `animation_descriptor.baml` +
  `gameplay_descriptor.baml` +
  `official_document_descriptor.baml`)
- 5 DLT sources under `dlt_sources/media/<class>/<work>/` (5
  `source.yaml` + 5 `.py` DLT resources; Plan A keyless for
  classes A/B/C/E; n/a for class D which is local-capture)
- 2 CocoIndex v1 Apps (`media_descriptors` +
  `cross_medium_compare`)
- 4 new Docker Compose stacks (`comfyui/`,
  `libretro-retroarch/`, `sam3-server/`,
  `sam3d-objects-server/`) — 6-file GOLD_STANDARD each
- 1 ADK `media_descriptor_agent` registered in
  `AGENT_REGISTRY` (fleet 13 → 14)
- 5-layer Dagster asset group + the
  `media_descriptor_coverage` asset check
- 2 marimo notebooks (`media_intel_explorer_per_medium.py` +
  `media_intel_explorer_cross_medium.py`)
- 2 NEW specs (`media-intel-corpus` +
  `media-intel-acquisition-plan`)
- 5 MODIFIED specs (`retro-game-design-catalogue` +
  `celtic-asset-generation` + `multimodal-code-and-media-intel`
  + `firecrawl-corpus-and-portals` + `infrastructure-stacks`)
- 1 new entry in `agents/agent_registry.py`
- 1 new section in `deployment-choice.yaml`
- 5 new `data:media-intel:*` tasks in `mise.toml`

**Dependency**: blocked by 2026-09-01, 2026-09-08, 2026-09-22,
2026-09-29, 2026-10-06. Soft-blocked by 2026-08-21 and
2026-08-15.

**Done when**:

- ✅ All 6 quality gates pass (`openspec validate --strict` +
  `mise run openspec:validate-all` + `mise run lint:drift-docs`
  + `mise run lint:registry` + `mise run devops:validate-stacks`
  + `mise run lint` + `mise run py:typecheck` + `mise run
  turbo typecheck`)
- ✅ 5 v1 sources materialise successfully
- ✅ The 4 NEW stacks pass `devops:validate-stacks`
- ✅ The `media_descriptors_lance` table has at least 1 row per
  class (the asset check passes)

## Phase 2 — Mid-flight refactor: the Class E drift fix (2026-08-23) — DONE

**Goal**: address the drift the user flagged — the prior
draft of Class E committed 12 Wikipedia pages (Tuatha Dé
Danann, Irish mythology, etc.) as official sources. The brief
corrected this: the 9 Celtic-history Wikipedia pages were
MOVED to a stubbed class for the downstream theming change,
and the Class E official surface was REPLACED with 3
government sub-buckets + 5 departments sub-buckets (36
official records total).

**Scope** (all done):

- Refactor `dlt_sources/media/official/ncca_sec_celt_duchas_wikipedia/`
  to drop the Wikipedia resource (keep the 14 educational body
  records)
- Create 9 stub Celtic-history research sources at
  `dlt_sources/media/celtic_history_research/` (gated for
  the downstream theming change)
- Create 3 government DLT sources (UK + Éire + Crown
  Dependencies — 41 records total)
- Create 5 departments DLT sources (18 records total)
- Refactor `agents/meaisinfhoghlaim/media_intel/` to match the
  `academic_history_agent.py` shape (10 tools + graceful
  degradation + _build_wire factory)
- Create the new `celtic-history-research` spec
- Rewrite `media-intel-acquisition-plan/spec.md` to drop the
  12 Wikipedia entries + add the 36 official records
- Update `orchestration/defs/media_intel.py` to register the
  8 new DLT source assets (15 → 23 total)
- Update `mise.toml` to 8 per-jurisdiction tasks

**Done when**:

- ✅ All 7 quality gates pass (`openspec validate --strict` +
  `mise run lint:registry` + ruff check + ast.parse +
  yaml.safe_load + agent import)
- ✅ Class E is the official government surface exclusively
- ✅ The 9 Celtic-history topics are stubbed
- ✅ The 4 unsourced-creative-decisions list is empty (every
  choice in this change is dictated by an on-disk source)

## Phase 3 — Mid-flight documentation sync (2026-08-23) — DONE

**Goal**: the 5 root files (`proposal.md` / `tasks.md` /
`design.md` / `PHASING.md` / `cross-repo-sync.md`) were
written in the initial build BEFORE the Phase 2 refactor.
They described the original 12-Wikipedia-entries version of
Class E. Phase 3 rewrites them to reflect the post-refactor
implementation.

**Scope** (all done):

- Update `proposal.md` — rewrite the "Why" + "What changes" +
  "Impact" sections to reflect the refactored Class E (36
  official records across 3 sub-buckets) + the 9 Celtic-
  history stub sources + the 10-tool agent
- Update `tasks.md` — rewrite to reflect T1-T13 (the actual
  task list) + the new spec deltas (the 3 NEW spec delta
  dirs)
- Update `design.md` — drop the Celtic-Elemental world canon
  sections; add the Class E refactor section + the
  celtic-history-research stub class section + the drift fix
  section
- Update `PHASING.md` — rewrite to reflect the 3 phases
- Verify `cross-repo-sync.md` — single-repo, no edit needed

**Done when**:

- ✅ All 7 quality gates pass (re-validate after the rewrite)

## Phase 4 — Agentic gameplay capture at scale (deferred to v2)

**Goal**: stand up the deterministic macro capture for Class D
games + the SAM3 sprite segmentation pipeline + the
cross-medium explorer verification.

**Scope** (deferred):

- T4.1: Stand up `sunshine` + `moonlight` + `ludusavi` on
  `bunchloch`. Wire the libretro-headless capture loop for
  Golden Sun via the new `libretro-retroarch` stack on
  `arm-oci`. Confirm `bun run preflight:arm-oci` passes
  before any IaC bootstrap.
- T4.2: Author the 3 deterministic macro scripts:
  - `golden_sun_title_to_venus_lighthouse.py`
  - `hades_1_first_boon_roll.py`
  - `wow_first_quest_chain.py`
- T4.3: Wire `sam3-server` to segment the Djinn sprites from
  Golden Sun + the boon-orb icons from Hades
- T4.4: Run the cross-medium explorer. Verify a sensible
  answer to "which element's visual grammar is most
  consistent across WoT prose + ATLA animation + Hickman
  comics"
- T4.5: Re-run `mise run sync:all` + the 6 quality gates.
  Re-validate the change. All must pass.

**Dependency**: v1 must archive first; 5 parent pending
changes must archive first.

**Done when**:

- The 3 macros complete successfully
- The 5-class descriptor counter in the marimo explorer shows
  ≥100 rows per class
- The cross-medium explorer returns a sensible answer
- All 6 quality gates pass

## Phase 5 — Stubbed comics + British Isles parity (deferred to v2)

**Goal**: add 5 stubbed comic-class sources (Morrison /
Tomasi / Johns / Valiant / Gillen) + British Isles parity
sources (SQA / WJEC / DESC / Gaelic Council).

**Scope** (deferred):

- T5.1: Add 5 NEW DLT sources under
  `dlt_sources/media/comics/stubbed/` (5 `source.yaml` files
  with `shippable_default: false` + a no-op `.py` DLT
  resource — the plugin registry handles the no-op)
- T5.2: Add British Isles parity sources: SQA CfE (Scotland),
  WJEC CfW (Wales), DESC (Isle of Man), Gaelic Council
  sources. Each as a stub `source.yaml` under
  `dlt_sources/media/celtic_history_research/` (Celtic
  history future) + the BIEP v3 educational body surface
- T5.3: Final `mise run sync:all` + the archive gate

**Dependency**: v1 + v2 must archive first; 5 parent pending
changes must archive first.

**Done when**:

- The 9 stubbed `source.yaml` files all parse
- The 5-class descriptor counter is updated to reflect the
  stubbed sources
- All 6 quality gates pass

## Out of scope (deferred to downstream Celtic-MMO design change)

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

These are the design choices that *this* change's corpus
enables but does *not* itself decide.
