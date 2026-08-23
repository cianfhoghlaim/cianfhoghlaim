# Design — Tuatha Media-Intel + Gameplay-Capture Research v1

This document captures the design decisions that don't fit in the
spec-delta format. It is the canonical reference for the 7-axis
medium-agnostic `MediaDescriptor` schema, the source-type
plugin contract, the Firecrawl 3-plan ladder, the legal capture
boundary, the post-refactor Class E official surface (the
36 official records across 3 sub-buckets), and the 9 stub
Celtic-history research sources (gated for the downstream
theming change).

It does **not** describe the Celtic MMO design itself. The
Celtic-MMO design is a downstream change gated on this corpus
being populated.

## 1. The 7-axis `MediaDescriptor` schema

The descriptor is the canonical record type emitted by every
per-medium BAML extractor function. It is the substrate on
which the future Celtic-MMO design will be built.

### 1.1 Why medium-agnostic

The Wheel of Time prose has *zero* pixels but a deeply
developed magic system. ATLA's animation has pixels + motion +
colour. A Hades boon has UI + particle + text. A Hickman
comic has panel layout + colour + typography. An NCCA
syllabus has text + table + figure.

The 7 descriptor axes are the *common substrate* that lets
all 5 media classes be ingested into a single database. The
schema is **BAML-as-source-of-truth** with codegen to
Pydantic + Zod + Convex + DuckLake DDL per
`centralized-schema-registry`.

### 1.2 The 7 axes

```python
class MediaDescriptor(BaseModel):
    """The 7-axis medium-agnostic descriptor."""
    work: str                          # e.g. "Wheel of Time", "ATLA S1E3", "FF #570"
    medium: Literal["comic","prose","animation","game","official"]
    language: str                      # ISO 639-1, default "en"
    source_url: HttpUrl
    source_timestamp: datetime

    # Axis 1 — power_event
    actor: str | None
    element: Literal["earth","air","water","fire","spirit","none"]
    power_source: str | None
    trigger: str | None
    scale_tier: Literal["personal","local","regional","continental","planetary","cosmic"]
    cost: str | None
    consequence: str | None
    counter: str | None

    # Axis 2 — visual_grammar
    composition: str | None
    panel_or_shot_type: str | None
    motion_lines: str | None
    camera: str | None
    silhouette: str | None
    focal_hierarchy: str | None

    # Axis 3 — palette
    dominant_hex: list[str]
    accent_hex: list[str]
    emissive_hex: list[str]
    per_element_palette: dict[str, list[str]]
    contrast_strategy: str | None

    # Axis 4 — vfx_vocabulary
    particle_class: Literal["dust","ember","mist","spark","lattice","ash","ink","glyph","none"]
    density: Literal["sparse","moderate","dense","overwhelming"]
    trail_behavior: str | None
    dissipation: str | None
    light_interaction: str | None

    # Axis 5 — narrative_beat
    arc_position: str | None
    beat_significance: str | None

    # Axis 6 — transferability
    in_game_mechanic: str | None           # e.g. "boon_rare_tier_earth_channelling"
    anam_cost: int | None                 # 0 if not a power
    palette_token: str | None              # the @theme/* token name in tuatha-ui (future)
    particle_effect: str | None            # the @particles/* archetype in tuatha-ui (future)

    # Axis 7 — provenance
    rights_holder: str
    licence: str                           # e.g. "fair-use-description", "CC-BY-SA-4.0", "OGL-3.0", "PSI"
    derivation_class: Literal["description_only","derivative","fair_use_quote"]
    shippable: Literal[False]              # ALWAYS False at this stage; see §5
    shippable_art_path: str | None         # set later by the asset-gen pipeline
```

### 1.3 The medium-specific extractor

Each BAML function in `baml_src/media/` populates the 7 axes
from its medium:

- `comic_descriptor.baml::ExtractComicDescriptor` reads a
  panel image + caption text via `qwen3-vl-8b` and emits the
  full descriptor with the panel's panel-locked coordinates
  as `source_timestamp`.
- `prose_descriptor.baml::ExtractProseDescriptor` reads a
  text passage via `qwen3.6-27b-mtp` (the prose-specialist
  model per `multimodal-code-and-media-intel`) and emits the
  same 7 axes (the `vfx_vocabulary.particle_class` is set to
  `ink` for prose-as-medium and the
  `visual_grammar.composition` becomes a paragraph of text
  rather than a panel coordinate).
- `animation_descriptor.baml::ExtractAnimationDescriptor`
  reads a frame + audio + subtitle via `molmo2-8b` (the
  diagram-pointing specialist) and emits the full
  descriptor.
- `gameplay_descriptor.baml::ExtractGameplayDescriptor`
  reads a screenshot + a session log (input events, current
  game state) via the same VLM and emits the descriptor.
- `official_document_descriptor.baml::ExtractOfficialDocumentDescriptor`
  reads a PDF page + a metadata block (issuer, date, version)
  via `olmocr-2-7b` (the OCR specialist) and emits the
  descriptor.

### 1.4 The "no graphics-from-graphics" invariant

Every `MediaDescriptor` record has `shippable: false` enforced
by the type system. To produce a *shippable* asset, the
asset-gen pipeline must:

1. Take the descriptor's `palette`, `vfx_vocabulary`, and
   `visual_grammar` (the *transferable descriptors*).
2. Combine with the ogham-stone public-domain art records
   (from `2026-09-08-ogham-celtic-stones-pipeline-v1`).
3. Combine with the public-domain NCCA/Wikipedia/CC-BY-SA
   Celtic motif sources.
4. Generate the asset via ComfyUI + a model from the *same
   providers* as the OCR_VISION-24 family (Flux /
   Z-Image-Turbo / Qwen-Image / FIBO).
5. Set the new record's `shippable_art_path` and the new
   `derivation_class` = `"derivative"`.

The original comic panel / animation frame / game screenshot
is **never** committed, hashed, or stored in the shippable
asset output. This invariant is enforced by the
`celtic-asset-generation` spec's `exporters/` pipeline.

## 2. The source-type plugin contract

### 2.1 Why a plugin registry

The 5 v1 sources are: Hickman comics, WoT prose, ATLA
animation, Hades+WoW+Golden Sun games, NCCA+SEC+DfE+SQA+WJEC+DESC
official (educational body subset) + the 3 government sub-buckets
+ the 5 departments sub-buckets (the 36 official records).

The 5 v2 stubbed sources are: Morrison `Batman Incorporated`,
Tomasi `Super Sons`, Johns `Green Lantern`, Valiant
`Harbinger`, Gillen `The Power Fantasy`.

The 3 v3 future sources are: Crown Dependencies education,
Cornish / Kernow curriculum, full Alba CfE coverage.

The 9 Celtic-history research topics (Tuatha Dé Danann, Irish
mythology, Celtic mythology, Celtic law, Brehon law, Aran
Islands, Isle of Skye, Isle of Man, Dyfed) are stubbed in
`dlt_sources/media/celtic_history_research/` — GATED for the
downstream theming change.

A *plugin contract* means adding a new source is *config, not
code*. The contract:

```yaml
# dlt_sources/media/<class>/<work>/source.yaml
source:
  id: marvel_hickman_ff
  medium: comic
  work: Fantastic Four 570-611
  firecrawl_plan: plan_a_keyless       # v1 default
  vlm_primary: qwen3-vl-8b             # via MODEL_REGISTRY
  vlm_secondary: gemma-4-12b           # via MODEL_REGISTRY
  baml_functions:
    - ExtractComicDescriptor
  lance_table: media_descriptors
  ducklake_schema: cianfhoghlaim.media
  licence_summary: fair-use-description
  shippable_default: false
  legal_notes: "Panels are analysed but never committed. Only the textual descriptor is stored."
```

### 2.2 What the contract enforces

- Every source declares its Firecrawl plan (Plan A/B/C). The
  DLT resource refuses to materialise if the declared plan is
  unavailable (e.g. Plan B not provisioned).
- Every source declares its VLM routing through
  `MODEL_REGISTRY` family+role (no hardcoded model strings).
- Every source declares its BAML function set (a list of
  functions from `baml_src/media/<medium>_descriptor.baml`).
- Every source declares its LanceDB target table
  (`media_descriptors`).
- Every source declares its DuckLake schema
  (`cianfhoghlaim.media`).
- Every source declares its licence summary and `legal_notes`.
- The system refuses to materialise if `shippable_default: true`
  and `licence_summary` is not in the approved list
  (`CC-BY-SA-4.0`, `CC0`, `OFL-1.1`, `fair-use-description`,
  `OGL-3.0`, `PSI`).

## 3. The Firecrawl 3-plan ladder

### 3.1 Plan A — keyless (v1 default)

Tools used: `firecrawl_search`, `firecrawl_scrape`,
`firecrawl_parse`. Substitution for `firecrawl_map` and
`firecrawl_crawl`: sitemap inspection + `USE_LOCAL_SCRAPES`
cache.

Hard caps: ≤2 concurrent calls, exponential backoff, full
`firecrawl_meta.scrapes` logging per
`firecrawl-corpus-and-portals` invariant #1.

Class D (games) leans entirely on local `romm` + libretro +
`hermes` + `openclaw` capture. No Firecrawl involvement.

### 3.2 Plan B — paid basic (v2)

Adds `firecrawl_map`, `firecrawl_crawl`,
`firecrawl_batch_scrape`, `firecrawl_monitor_create`,
`firecrawl_monitor_check`.

Gated by the `firecrawl_budget_asset` (already exists per
`firecrawl-corpus-and-portals` invariant #6). Per-domain daily
credit budget; an `asset_check` fails the run before overspend.

### 3.3 Plan C — full (v3)

Adds `firecrawl_agent`, `firecrawl_interact`,
`firecrawl_research_search_papers`,
`firecrawl_research_inspect_paper`,
`firecrawl_developer_search`, `firecrawl_ask`.

Per-source cost attribution surfaced in the marimo control
panel.

## 4. The legal capture boundary

### 4.1 Auto-allowed (v1)

- **Hades 1 + Hades 2** (owned, installed locally) — boon
  descriptors only, never captured screenshots
- **World of Warcraft** (owned, installed locally) —
  class/role/zone descriptors, never captured frames
- **Golden Sun** (owned ROM) — Djinn/Psynergy class
  descriptors via libretro `mgba` core, screenshots are
  `libretro_screenshots` rows in
  `stedding/ingest_queue/retro/gba/golden_sun/` per the
  `retro-game-design-catalogue` spec and are NOT shippable
- **Pokémon** (owned ROM) — type chart interaction matrix is
  public-domain mechanics; no per-game asset reused
- **DragonBox** (owned iOS) — mechanic descriptor only
- **Duolingo** (owned iOS) — economy / lesson-tree
  descriptor only, no captured frames
- **Bejeweled** (owned iOS) — juice / palette descriptor only

### 4.2 Requires per-title ownership audit (v2)

- All other ROMs in the `romm` library
- All other Game Boy Advance / NES / SNES / Genesis / PS1
  titles
- iOS games not in the auto-allowed list
- All Steam / Epic / GOG titles beyond Hades + WoW

### 4.3 What is NEVER captured

- Copyrighted comic panel images (only the textual descriptor
  is stored)
- Animation frame stills from Netflix / Paramount / Disney
  (only the textual descriptor)
- Game screenshots beyond the libretro headless output
  (and those are stored in `stedding/ingest_queue/retro/`
  per the `retro-game-design-catalogue` spec, NEVER in the
  shippable asset output)
- Any derived asset that re-renders, upscales, or img2img's
  a copyrighted source (the `derivation_class` invariant
  enforces this)

## 5. The post-refactor Class E official surface

The 2026-08-23 refactor replaced the 12 Wikipedia entries
(formerly committed to Class E) with 36 official records
across 3 government sub-buckets + 5 departments sub-buckets
(per the user's brief: "replace the Celtic-history Wikipedia
sources with the official wiki pages of the British Isles
subnational police, defence, army, governmental departments
and relevant historic type things acts and treaties").

### 5.1 Class E educational body sub-bucket (14 records)

The 2 NCCA research PDFs at the root of `leaving_certificate/`
+ the 12 NCCA Leaving Certificate syllabus PDFs (en + ga
parity) + the 6 educational body Wikipedia pages (NCCA + SEC
+ DfE + SQA + WJEC + DESC) live in
`dlt_sources/media/official/ncca_sec_celt_duchas_wikipedia/`.

Acquisition: `firecrawl_parse` (PDFs). VLM: `olmocr-2-7b`. BAML:
`ExtractOfficialDocumentDescriptor`. Rights holders: NCCA + SEC
+ DfE + SQA + WJEC + DESC. Licences: `fair-use-description` for
the syllabus PDFs (the canonical curriculum spec surface).

### 5.2 Class E government sub-buckets (41 records total)

The government sub-bucket contains police + defence + army +
Home Office + FCDO + MoJ + DoH + Oireachtas + Office of the
President + Crown Dependencies + Acts + Treaties.

#### 5.2.1 UK government (`dlt_sources/media/official/government/uk/`) — 18 records

- **Police (3)**: Metropolitan Police Service + British
  Transport Police + Police Service of Northern Ireland
- **Defence (4)**: Ministry of Defence + British Army + Royal
  Navy + Royal Air Force
- **Departments (4)**: Home Office + FCDO + MoJ + Department
  of Health and Social Care
- **Acts + Treaties (7)**: Acts of Union 1707 + Acts of
  Union 1800 + Anglo-Irish Treaty 1921 + Good Friday
  Agreement 1998 + Windsor Framework 2023 + UK Internal
  Market Act 2020 + UK Withdrawal (Continuity) Act 2020

Rights holders: the actual issuing body (e.g., "Metropolitan
Police Service", "Ministry of Defence", "Crown copyright").
Licences: `OGL-3.0` (Open Government Licence v3.0) for
departmental pages, `OGL-3.0` (Crown copyright) for the
Acts + Treaties.

#### 5.2.2 Éire government (`dlt_sources/media/official/government/ie/`) — 15 records

- **Police + Defence (4)**: An Garda Síochána + Irish
  Defence Forces + Naval Service + Air Corps
- **Departments (5)**: Department of Defence (IE) +
  Department of Justice (IE) + Department of Foreign Affairs
  (IE) + Houses of the Oireachtas + Office of the President
- **Acts + Treaties (6)**: Government of Ireland Act 1920 +
  Statute of Westminster 1931 + Treaty of Limerick 1691 +
  Bunreacht na hÉireann 1937 + Anglo-Irish Treaty 1921 +
  Good Friday Agreement 1998 (IE)

Rights holders: the actual issuing body (e.g., "An Garda
Síochána", "Department of Defence (Ireland)", "Government of
Ireland"). Licences: `PSI` (Public Sector Information
Licence) for departmental pages, `OGL-3.0` (Crown copyright)
for the Acts + Treaties.

#### 5.2.3 Crown Dependencies government (`dlt_sources/media/official/government/crown_dependencies/`) — 8 records

- **Isle of Man (4)**: Isle of Man Government + IoM
  Constabulary + Tynwald + IoM Courts of Justice
- **Jersey (2)**: States of Jersey + States of Jersey Police
- **Guernsey (2)**: States of Guernsey + Bailiwick of
  Guernsey Police

The 3 British Crown Dependencies (IoM + Jersey + Guernsey) are
self-governing Crown Dependencies of the UK Crown — NOT part
of the UK. They have their own legislative assemblies + police
forces + courts.

Rights holders: the actual issuing body. Licences: `OGL-3.0`.

### 5.3 Class E departments sub-buckets (18 records total)

The departments sub-bucket contains the non-police /
non-defence departmental surface per jurisdiction.

- **UK (5)**: NHS England + DWP + Transport + Education +
  DEFRA
- **Éire (3)**: DoH (IE) + DoEdu (IE) + HSE
- **Scotland (3)**: NHS Scotland + Education Scotland +
  Scottish Government
- **Wales (3)**: NHS Wales + HEIW + Welsh Government
- **Northern Ireland (4)**: DoH (NI) + DE (NI) + DfE (NI) +
  nidirect

Rights holders: the actual issuing body. Licences: `OGL-3.0`
(or `PSI` for Éire) per the per-source licence whitelist.

## 6. The 9 stub Celtic-history research sources

The 9 Celtic-history Wikipedia topics (Tuatha Dé Danann, Irish
mythology, Celtic mythology, Celtic law, Brehon law, Aran
Islands, Isle of Skye, Isle of Man, Dyfed) were MOVED to
`dlt_sources/media/celtic_history_research/` per the
2026-08-23 refactor. They are stubbed (`scrape.py` yields
zero rows) for the downstream theming change.

The canonical source for these topics is the user's personal
clippings directory
`cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`.

### 6.1 Per-source `licence`

All 9 Celtic-history topics use `licence: "CC-BY-SA-4.0"`
(Wikipedia attribution preserved). The `rights_holder` is
`"Wikipedia editors (CC-BY-SA-4.0)"` (NOT "Wikipedia
Foundation" — that's the Wikipedia host, not the original
publisher).

### 6.2 Activation

To activate a stub, the downstream Celtic-MMO theming change
flips the `status: stub` to `status: active` in the
per-source `source.yaml` AND materialises the scrape.py with
the per-page ingestion logic.

## 7. The 4 NEW docker stacks

| Stack | Purpose | License | Network |
|:--|:--|:--|:--|
| `comfyui/` | Node-graph image gen wired to `unsloth-serve` + HF models from the *same providers* as the OCR_VISION-24 family | Apache 2.0 (ComfyUI) | Outbound to HF Hub |
| `libretro-retroarch/` | Headless libretro + 6 cores: Mesen (NES), snes9x (SNES), gambatte (GB), mgba (GBA), genesis_plus_gx (Genesis), pcsx_rearmed (PS1) | GPL (libretro cores) + BSD (libretro API) | n/a (local only) |
| `sam3-server/` | Facebook SAM3 image segmentation | Apache 2.0 | n/a (local only) |
| `sam3d-objects-server/` | Facebook SAM-3D-Objects sprite-to-3D | Apache 2.0 | n/a (local only) |

All 4 land as 6-file GOLD_STANDARD artifacts per
`infrastructure-stacks` spec.

## 8. The drift fix (2026-08-23 mid-flight)

The 2026-08-23 refactor corrected 6 specific drifts from the
prior draft:

| Drift | Before | After |
|:--|:--|:--|
| `rights_holder: "Wikipedia Foundation"` for 9 Celtic-history topics | in Class E (official) | MOVED to `celtic_history_research/` stubs with `rights_holder: "Wikipedia editors (CC-BY-SA-4.0)"` per licence |
| `rights_holder: "Wikipedia Foundation"` for 3 NCCA/SEC/SQA/WJEC etc. pages | already-correct for education bodies | kept (now proper sub-bucket) |
| Single task `data:media-intel:official-pdfs` mixed NCCA + Wikipedia | 1 task | 8 per-jurisdiction tasks + 1 educational-bodies task |
| `media_descriptor_agent` 5 tools | 5 | **10** (the academic_history_agent.py shape) |
| Wikipedia + Celtic-history drift in Class E | YES | **NO** — Class E is the official government surface exclusively |
| 0 official Acts / Treaties in the corpus | none | 13 Acts + Treaties (7 UK + 6 Éire) |
| 0 police / defence / army in the corpus | none | 7 sources (3 Met + BTP + PSNI; 4 MoD + Army + Navy + RAF; 4 Irish Defence Forces) |
| Celtic-history sub-package for downstream theming | absent | created + gated |

## 9. The future theming change (out of scope)

The Celtic MMO design itself is **out of scope** for this
change. The 9 Celtic-history research sources (gated) +
the 36 official records (the government / police / defence /
Acts / Treaties spine) + the 4 games sources (Hades + WoW +
Golden Sun + Pokémon) + the 5 v1 media-class sources
(comics / prose / animation / games / official) form the
**empirical input** for the downstream theming change.

The downstream theming change will:

1. Activate the 9 Celtic-history stubs
2. Cross-reference the 4 game-captured elements + the 4
   animation-captured elements + the 1 prose-captured
   element + the 5 official-recorded elements
3. Decide the 4+1 element binding (or conclude "no binding")
4. Decide the sub-nation mapping (or conclude "no mapping")
5. Decide the 2D particle renderer
6. Decide the iOS delivery vehicle
7. Decide the boons / anam / anamcara / x402 mechanic

None of these decisions are in this change. The 7-axis
`MediaDescriptor` schema is what feeds that future design.
Until the corpus is populated, the design has no factual
basis.

## 10. Creative (unsourced) decisions for operator override

There are **zero** creative decisions in this change. Every
choice in this change is dictated by an on-disk source
(existing scaffolding + the 5 media classes + the 36 official
records + the 9 stub sources). The future theming change
will have its own unsourced-decisions list; this change does
not.
