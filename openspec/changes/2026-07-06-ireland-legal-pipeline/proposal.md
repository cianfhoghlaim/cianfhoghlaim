# Change: 2026-07-06-ireland-legal-pipeline

## Why

The Cianfhoghlaim Ireland/law quadrant currently contains only 3 statutory-law
sources (`irish_statute_book`, `doj`, `lawreform`). The user's request
adds the 5 highest-value **operational-law** sources:

1. **injuries.ie** (Personal Injuries Assessment Board — PIAB) — the
   front-door for every personal injury claim in Ireland, including the
   "permission to seek judicial review" process that gates ~90% of High
   Court personal-injury litigation.
2. **courts.ie** (Courts Service) — the catalogue of all court forms
   (District / Circuit / High / Supreme / Court of Appeal), the published
   Judgements.ie database (~30,000 decisions), the Court Rules library
   (PDF), and the Court Fees schedules.
3. **workplacerelations.ie** (Workplace Relations Commission) — the
   ~6,000 published adjudication decisions per year covering unfair
   dismissal, employment equality, payment of wages, working time, and
   the dispute-resolution procedures (mediation → investigation →
   adjudication → appeal to Labour Court).
4. **citizensinformation.ie** (Citizens Information Board) — the
   plain-English rights/entitlements/appeals articles that the public
   uses to navigate the legal system.
5. **gov.ie/en/** (Irish Government) — the umbrella surface covering
   ~16 ministerial departments (DoJ, DoH, DES, DBEI, DECC, …). The
   existing `doj.py` covers only the DoJ sub-tree; this change expands
   to the full government directory.

The user explicitly named two use cases that today are impossible to
answer without manual searching:

- *"Indexing High Court forms for personal injury claims"* — currently
  requires manual visits to courts.ie/forms and cross-referencing
  injuries.ie/permission-to-sue.
- *"Finding the most relevant info on citizensinformation / gov.ie /
  irishtatutebook for a WRC complaint"* — currently requires
  manually cross-correlating ~5 sites.

The proposed change delivers both as BAML-structured tables +
BGE-M3-embedded LanceDB rows + marimo notebooks + a unified semantic
search.

## What changes

### L.1 Five new DLT sources under `cianfhoghlaim/dlt/british_isles/ireland/law/`

For each of the 5 sources, a new DLT source module + a registration
in `__init__.py`. Each follows the canonical pattern from
`irish_statute_book.py` and `doj.py`:

| File | Source | Routes | BAML fn (L2) |
|---|---|---|---|
| `injuries_ie.py` | `https://www.injuries.ie/eng/` (process + forms sub-trees) | process / forms / news / about | `b.ExtractPIABPage` |
| `courts_ie.py` | `https://www.courts.ie/` (forms + judgements + fees + rules) | forms / judgements / fees / rules / court-lists | `b.ExtractCourtForm`, `b.ExtractJudgement`, `b.ExtractCourtFee`, `b.ExtractCourtRule` |
| `workplace_relations.py` | `https://workplacerelations.ie/en/` (decisions + procedures) | decisions / procedures / forms / news | `b.ExtractWRCDecision`, `b.ExtractWRCProcedure` |
| `citizensinformation.py` | `https://www.citizensinformation.ie/en/` (articles) | justice / employment / social-welfare / housing / health / consumer / money-and-tax | `b.ExtractCitizensInfoArticle` |
| `gov_ie_law.py` | `https://www.gov.ie/en/` (all departments) | department / publication / news / organisation | `b.ExtractGovIEPressRelease` |

Each source:
- Honours `USE_LOCAL_SCRAPES=true` falling back to
  `stedding/ingest_queue/<source>/`.
- Uses the shared `_crawl_source` from
  `cianfhoghlaim/dlt/british_isles/ireland/education/curriculum_source.py`
  (the canonical crawler — already used by `doj.py` and `lawreform.py`).
- Emits `nation="ie"`, `domain="law"`, `entity=<source_slug>` on every
  row (per the oideachais-pipeline `Asset Key Convention` requirement).
- Uses `write_disposition="merge"` + `primary_key=["url"]` so re-crawls
  are idempotent.

### L.2 New BAML file: `cianfhoghlaim/baml_src/processing/ireland_legal_extraction.baml`

9 new BAML functions, all using `litellm/gemini-2.5-flash` as the
default client (matches `circular_extraction.baml` precedent):

| Function | Input | Output class | Use case |
|---|---|---|---|
| `ExtractPIABPage` | url + html | `PIABPage` | Crawled pages → process steps, forms, fees, time limits |
| `ExtractCourtForm` | url + pdf_path | `CourtForm` | courts.ie forms → form number, court level, parties, fee, fillable fields |
| `ExtractJudgement` | url + pdf_path | `Judgement` | Judgements.ie → neutral citation, parties, judge, statutes cited, catchwords, holding |
| `ExtractCourtFee` | url + html | `CourtFee` | Court fees → fee code, amount, court level, effective date |
| `ExtractCourtRule` | url + pdf_path | `CourtRule` | Rules of Court → rule number, order, court, subject |
| `ExtractWRCDecision` | url + html | `WRCDecision` | WRC decisions → case ref, decision date, complaint type, outcome, award, statutes cited, claimant/respondent |
| `ExtractWRCProcedure` | url + html | `WRCProcedure` | WRC procedure pages → complaint type, time limits, hearing steps, ADR options |
| `ExtractCitizensInfoArticle` | url + html | `CitizensInfoArticle` | CIB articles → topic, category, eligibility, entitlements, steps, agencies, appeals, statutory refs |
| `ExtractGovIEPressRelease` | url + html | `GovIEPressRelease` | gov.ie press → dept, headline, summary, key actions, related agencies, statutory refs |

Reuses the existing `CaseCategory`, `Jurisdiction`, `TimelineEvent`,
`StatuteReference` enums/classes from `legal_case_profile.baml` so we
do not duplicate the schema.

The class shape for `Judgement` is the canonical hook for the user's
"find the relevant info" use case — its `statutes_cited: StatuteReference[]`
field is the join key against `irish_statute_book.acts`.

### L.3 New CocoIndex v1 flow: `cianfhoghlaim/cocoindex/ireland_legal_embedding.py`

R1–R4-conformant (per the `oideachais-cocoindex-v1` skill):
- R1: `from ._lifespan import shared_lifespan`
- R2: uses canonical `ContextKeys` from `._lifespan`
- R3: `coco.App(...)` at module scope
- R4: ≥1 `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`

5 BGE-M3 1024-dim embedding targets (one per source), all in the same
LanceDB namespace `oideachais.law.ie.<entity>`:

```python
@dataclass
class IrelandLegalChunk:
    chunk_id: str
    source: str            # "piab" | "courts" | "wrc" | "citizensinfo" | "gov_ie"
    entity_type: str       # "page" | "form" | "judgement" | "decision" | "article" | "press"
    url: str
    title: str
    text: str
    extra: dict[str, Any]  # type-specific (form_number, citation, etc.)
    embedding: coco.Vector[Literal[1024]]
```

Source: `oideachais.law.ie.<entity>` DuckLake tables (read via the
canonical `duckdb` → `mo.sql(engine="md:oideachais")` pattern).

### L.4 Five L1 Dagster defs (one per source)

Following the BIEP v1 pattern:

```
cianfhoghlaim/orchestration/defs/1_ingestion/law/
├── ie_irish_statute_book/        # existing
├── ie_doj/                        # existing (gov.ie DoJ sub-tree — kept)
├── ie_lawreform/                  # existing
├── ie_injuries_board/             # NEW
├── ie_courts_service/             # NEW
├── ie_workplace_relations/        # NEW
├── ie_citizensinformation/        # NEW
└── ie_gov_ie/                     # NEW (supersedes ie_doj scope)
```

Each `defs.yaml` instantiates the `CelticIngestionComponent`
(`layer1_ingestion.py`) with the canonical group_name
`1_ingestion/law/<slug>` and a daily `0 5 * * *` cron.

### L.5 One L2 Dagster defs

```
cianfhoghlaim/orchestration/defs/2_materials/legal_research/
└── ireland_legal_extraction/
    ├── defs.yaml                   # CelticMaterialsComponent
    └── ireland_legal_assets.py     # 9 BAML extraction assets (1 per BAML fn)
```

### L.6 One L3 Dagster defs (CocoIndex v1)

```
cianfhoghlaim/orchestration/defs/3_model_lifecycle/cocoindex_v1/
└── ireland_legal/
    └── defs.yaml                   # CelticModelLifecycleComponent
```

### L.7 Five L4 Dagster defs (marimo dashboards)

```
cianfhoghlaim/orchestration/defs/4_asset_generation/marimo_dashboards/
├── ireland_legal_personal_injury/
├── ireland_legal_courts/
├── ireland_legal_wrc/
├── ireland_legal_citizensinfo/
└── ireland_legal_gov_ie/
```

Each instantiates `CelticAssetGenerationComponent` with
`dashboard_kind: marimo` and the corresponding notebook path.

### L.8 Six marimo notebooks

```
cianfhoghlaim/notebooks/12_ireland_law/
├── 01_personal_injury_journey.py    # PIAB → High Court flow chart
├── 02_courts_index.py                # forms + judgements + fees + rules catalogue
├── 03_wrc_decision_search.py         # WRC decisions semantic search + citation lookup
├── 04_citizensinfo_rights.py         # rights/entitlements/appeals explorer
├── 05_gov_ie_law_corpus.py           # gov.ie ALL sub-departments archive
└── 06_unified_cross_source_query.py  # one box across all 6 sources (incl. ISB)
```

All 6 notebooks:
- Have PEP 723 inline deps (`marimo>=0.13`, `duckdb>=1.0`, `ibis-framework[duckdb]>=9.0`,
  `altair>=5.0`, `polars>=0.20`).
- Read from `md:oideachais.law.ie.*` via `duckdb.connect("md:oideachais")`.
- Use DuckDB + Ibis (no pandas-only analytics).
- Use the shared `nb_utils.connect_md_oideachais()` helper for graceful
  local-DuckDB fallback.

### L.9 Spec delta: `openspec/specs/ireland-legal-pipeline/spec.md`

A new capability spec with 9 ADDED Requirements (see the full content
in `specs/ireland-legal-pipeline/spec.md`).

## What does NOT change

- The 3 existing ireland/law DLT sources (`irish_statute_book`, `doj`,
  `lawreform`) keep working unchanged. The new spec references them as
  the cross-source substrate for `06_unified_cross_source_query.py`.
- The 5-layer architecture (Layer1…5 Components) — no new Component
  types; only new `defs.yaml` instantiations.
- The BAML client defaults (`litellm/gemini-2.5-flash` / `litellm/anthropic/claude-sonnet-4`)
  — reused from existing patterns.
- The CocoIndex v1 R1–R4 conformance contract — enforced by the
  `CelticModelLifecycleComponent`.

## Files (NEW + modified)

### New Python files

- `cianfhoghlaim/dlt/british_isles/ireland/law/injuries_ie.py`
- `cianfhoghlaim/dlt/british_isles/ireland/law/courts_ie.py`
- `cianfhoghlaim/dlt/british_isles/ireland/law/workplace_relations.py`
- `cianfhoghlaim/dlt/british_isles/ireland/law/citizensinformation.py`
- `cianfhoghlaim/dlt/british_isles/ireland/law/gov_ie_law.py`
- `cianfhoghlaim/baml_src/processing/ireland_legal_extraction.baml` (9 fns)
- `cianfhoghlaim/cocoindex/ireland_legal_embedding.py` (v1-conformant)
- `cianfhoghlaim/orchestration/defs/2_materials/legal_research/ireland_legal_extraction/ireland_legal_assets.py`
- `cianfhoghlaim/orchestration/defs/1_ingestion/law/{ie_injuries_board,ie_courts_service,ie_workplace_relations,ie_citizensinformation,ie_gov_ie}/defs.yaml` (×5)
- `cianfhoghlaim/orchestration/defs/2_materials/legal_research/ireland_legal_extraction/defs.yaml`
- `cianfhoghlaim/orchestration/defs/3_model_lifecycle/cocoindex_v1/ireland_legal/defs.yaml`
- `cianfhoghlaim/orchestration/defs/4_asset_generation/marimo_dashboards/{ireland_legal_personal_injury,ireland_legal_courts,ireland_legal_wrc,ireland_legal_citizensinfo,ireland_legal_gov_ie}/defs.yaml` (×5)
- `cianfhoghlaim/notebooks/12_ireland_law/{01,02,03,04,05,06}_*.py` (×6)

### Modified Python files

- `cianfhoghlaim/dlt/british_isles/ireland/law/__init__.py` — register
  the 5 new sources.
- `cianfhoghlaim/baml_src/processing/__init__.py` — register the new BAML
  module.

### New openspec

- `openspec/changes/2026-07-06-ireland-legal-pipeline/`
  (this change)
- `openspec/specs/ireland-legal-pipeline/spec.md` (the new spec)

## Acceptance

- `openspec validate 2026-07-06-ireland-legal-pipeline --strict` passes.
- `dagster asset materialize --select '*ireland_legal*'` succeeds; the
  5 L1 + 9 L2 + 1 L3 (CocoIndex v1) assets produce rows in
  `oideachais.law.ie.*` DuckLake tables for all 5 sources.
- `dagster asset materialize --select '*injuries_board*'` succeeds;
  the `piab_pages` and `piab_forms` tables are populated.
- `dagster asset materialize --select '*courts_service*'` succeeds; the
  `courts_forms`, `judgements`, `court_fees`, `court_rules` tables are
  populated.
- `marimo run cianfhoghlaim/notebooks/12_ireland_law/01_personal_injury_journey.py`
  renders the PIAB→High Court flow chart against live lakehouse data.
- `marimo run cianfhoghlaim/notebooks/12_ireland_law/03_wrc_decision_search.py`
  returns a relevant WRC decision + linked Citizens Information article
  + Irish Statute Book section for a query like "unfair dismissal
  redundancy payment".
- The CocoIndex v1 embedding App passes R1–R4 conformance
  (`mise run upstream:conformance`).
- `ccc search "ireland legal pipeline"` finds the new spec + the
  5 per-source DLT modules.