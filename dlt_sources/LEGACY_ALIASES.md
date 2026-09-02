# LEGACY_ALIASES — dlt_sources/

This file documents the legacy path aliases that are still importable via
re-export shims. Each wave of the 2026-08-24 master refactor plan adds
new mappings here.

## Wave 1 — 2026-08-24-dlt-sources-domain-restructure-v1 (THIS FILE)

Per the
[`2026-08-24-wave-1-dlt-sources-domain-restructure-v1`](../../changes/2026-08-24-wave-1-dlt-sources-domain-restructure-v1/proposal.md)
openspec change. **All old paths remain importable via deprecation
shims for at least one release cycle.**

### Domain-first law/ split — 59 directories

| Old | New |
|:--|:--|
| `dlt_sources/<geography>/<jurisdiction>/law/` | `dlt_sources/law/<jurisdiction>/<geography>/` |

Geographies in scope: `american_nations`, `british_isles`, `commonwealth`,
`european_nations`, `european_union`.

Examples:
- `dlt_sources/commonwealth/nigeria/law/nass.py` → `dlt_sources/law/nigeria/commonwealth/nass.py`
- `dlt_sources/british_isles/england/law/legislation.py` → `dlt_sources/law/england/british_isles/legislation.py`
- `dlt_sources/european_nations/poland/law/sejm.py` → `dlt_sources/law/poland/european_nations/sejm.py`

### Domain-first medicine/ split — 59 directories

| Old | New |
|:--|:--|
| `dlt_sources/<geography>/<jurisdiction>/medicine/` | `dlt_sources/medicine/<jurisdiction>/<geography>/` |

Examples:
- `dlt_sources/commonwealth/australia/medicine/tga.py` → `dlt_sources/medicine/australia/commonwealth/tga.py`
- `dlt_sources/commonwealth/nigeria/medicine/ncdc.py` → `dlt_sources/medicine/nigeria/commonwealth/ncdc.py`
- `dlt_sources/british_isles/ireland/medicine/<...>.py` → `dlt_sources/medicine/ireland/british_isles/<...>.py`

### Domain-first education/ split — 61 directories (K-12 / secondary)

| Old | New |
|:--|:--|
| `dlt_sources/<geography>/<jurisdiction>/education/` | `dlt_sources/education/<jurisdiction>/<geography>/` |

Examples:
- `dlt_sources/british_isles/ireland/education/<...>.py` → `dlt_sources/education/ireland/british_isles/<...>.py`
- `dlt_sources/commonwealth/canada/education/<...>.py` → `dlt_sources/education/canada/commonwealth/<...>.py`
- `dlt_sources/american_nations/united_states/california_education.py` → `dlt_sources/education/united_states/american_nations/california_education.py`

### Tertiary (3rd-level / university) — NEW

| Old (UOG flat files at orchestration layer) | New |
|:--|:--|
| `orchestration/defs/uog_exam.py` | `dlt_sources/education/tertiary/uog/exam_papers/` |
| `orchestration/defs/uog_official_docs.py` | `dlt_sources/education/tertiary/uog/official_docs/` |
| `orchestration/defs/uog_personal_archive.py` | `dlt_sources/education/tertiary/uog/personal_archive/` |
| `orchestration/defs/uog_personal_archive_figures.py` | `dlt_sources/education/tertiary/uog/personal_archive/figures/` |
| `orchestration/defs/uog_students_union.py` | `dlt_sources/education/tertiary/uog/students_union/` |
| `orchestration/defs/nui_federation.py` | `dlt_sources/education/tertiary/nui_federation/` |
| `orchestration/defs/british_isles_tertiary.py` | `dlt_sources/education/tertiary/british_isles/` |

### Themed package restructure

| Old | New |
|:--|:--|
| `dlt_sources/language/{ainm,canuint*,logainm,tearma*,universal_dependencies,_canuint_helpers,_tearma_helpers,_gaois_helpers}.py` | `dlt_sources/lexicographic/` |
| `dlt_sources/language/{celtic_mythology,duchas*,gaois*,heritage,hidden_heritages,_duchas_images_helpers}.py` | `dlt_sources/cultural_heritage/` |
| `dlt_sources/language/{local_documents_by_subject,local_education_documents,_local_documents_helpers}.py` | `dlt_sources/local_archive/` |
| `dlt_sources/media/{official,prose,celtic_history_research,animation}/` | `dlt_sources/media_text/` |
| `dlt_sources/media/comics/` | `dlt_sources/media_comics/` |
| `dlt_sources/media/games/` | `dlt_sources/media_games/` |
| `dlt_sources/api_sources/defi/` (merged with `crypteolas/defi/`) | `dlt_sources/crypteolas_defi/` |
| `dlt_sources/api_sources/documentation/` (if it exists) | `dlt_sources/api_documentation/` |
| `dlt_sources/api_sources/github/` (if it exists) | `dlt_sources/api_github/` |
| `dlt_sources/api_sources/local/` (if it exists) | `dlt_sources/api_local/` |
| `dlt_sources/crypteolas/{local,github}/` | `dlt_sources/crypteolas_chain/` |
| `dlt_sources/crypteolas/documentation/` | `dlt_sources/crypteolas_docs/` |
| `dlt_sources/apple_photos/` | `dlt_sources/media_personal/` |
| `dlt_sources/filesystem/` | `dlt_sources/raw_files/` |
| `dlt_sources/portfolio/{cv,artwork,labels}/` | `dlt_sources/{cv,artwork,labels}/` (split) |
| `dlt_sources/jobs/` | `dlt_sources/_jobs/` (rename — CLI dispatcher) |

### Layer-grouped destinations — DEFERRED to Wave 4

The destinations consolidation (`destinations_*.py` → `destinations/{ducklake,motherduck,filesystem,iceberg}.py`)
is part of the Wave 4 DuckLake v1.0 hardening cascade and is NOT
addressed by Wave 1.

---

## Wave 1 — themed packages (2026-08-24) — APPENDED 2026-08-24 (KEEP-ENGLISH + themed packages + layer-grouped destinations)

Per the master plan
[`2026-08-24-master-refactor-plan`](../../../openspec/plans/2026-08-24-master-refactor-plan.md)
§3.2 (target layout) + §7.1 (naming map), the Wave 1 rename waves
actually executed by this file are:

### Themed sub-tree split — `language/` → 3 themed sub-trees (master plan §3.2, §7.1)

| Old | New |
|:--|:--|
| `dlt_sources/language/` | **DEPRECATED** (split into 3 themed sub-trees, kept as a re-export shim for 1 release cycle) |
| `dlt_sources/language/ainm.py` | `dlt_sources/lexicographic/ainm.py` |
| `dlt_sources/language/canuint.py` | `dlt_sources/lexicographic/canuint.py` |
| `dlt_sources/language/canuint_audio.py` | `dlt_sources/lexicographic/canuint_audio.py` |
| `dlt_sources/language/canuint_dialect_summary.py` | `dlt_sources/lexicographic/canuint_dialect_summary.py` |
| `dlt_sources/language/canuint_search.py` | `dlt_sources/lexicographic/canuint_search.py` |
| `dlt_sources/language/canuint_word_alignment.py` | `dlt_sources/lexicographic/canuint_word_alignment.py` |
| `dlt_sources/language/duchas.py` (the lexicon) | `dlt_sources/lexicographic/duchas.py` (source name `duchas_folklore`) |
| `dlt_sources/language/duchas_images.py` (the folklore corpus) | `dlt_sources/cultural_heritage/duchas_corpus.py` (source name `duchas_images_source`) |
| `dlt_sources/language/gaois.py` | `dlt_sources/lexicographic/gaois.py` |
| `dlt_sources/language/gaois_combined.py` | `dlt_sources/lexicographic/gaois_combined.py` |
| `dlt_sources/language/logainm.py` | `dlt_sources/lexicographic/logainm.py` |
| `dlt_sources/language/tearma.py` | `dlt_sources/lexicographic/tearma.py` |
| `dlt_sources/language/tearma_search.py` | `dlt_sources/lexicographic/tearma_search.py` |
| `dlt_sources/language/celtic_mythology.py` | `dlt_sources/cultural_heritage/celtic_mythology.py` |
| `dlt_sources/language/heritage.py` | `dlt_sources/cultural_heritage/heritage.py` |
| `dlt_sources/language/hidden_heritages.py` | `dlt_sources/cultural_heritage/hidden_heritages.py` |
| `dlt_sources/language/local_documents_by_subject.py` | `dlt_sources/cultural_heritage/local_documents_by_subject.py` |
| `dlt_sources/language/local_education_documents.py` | `dlt_sources/cultural_heritage/local_education_documents.py` |
| `dlt_sources/language/universal_dependencies.py` | `dlt_sources/language_models/universal_dependencies.py` |
| `dlt_sources/language/_canuint_helpers.py` | `dlt_sources/lexicographic/_canuint_helpers.py` |
| `dlt_sources/language/_duchas_images_helpers.py` | `dlt_sources/cultural_heritage/_duchas_corpus_helpers.py` |
| `dlt_sources/language/_gaois_helpers.py` | `dlt_sources/lexicographic/_gaois_helpers.py` |
| `dlt_sources/language/_local_documents_helpers.py` | `dlt_sources/cultural_heritage/_local_documents_helpers.py` |
| `dlt_sources/language/_tearma_helpers.py` | `dlt_sources/lexicographic/_tearma_helpers.py` |

### Layer-grouped destinations — `destinations/*.py` at TOP LEVEL (master plan §3.2)

| Old | New |
|:--|:--|
| `dlt_sources/common/destinations_cianfhoghlaim.py` | `dlt_sources/destinations/__init__.py` (top-level canonical) + re-export shim at the legacy path |
| `dlt_sources/common/named_destinations.py` | `dlt_sources/destinations/__init__.py:named_destinations()` + re-export shim at the legacy path |
| `dlt_sources/_lakehouse/destinations.py` (renamed `lakehouse/`) | `dlt_sources/destinations/ducklake.py` (the dlt-side bridge) — kept at `lakehouse/destinations.py` (renamed from `_lakehouse/destinations.py`) |
| `dlt_sources/_lakehouse/personal_archive_destinations.py` | `dlt_sources/lakehouse/personal_archive_destinations.py` (rename only; no content change) |
| `dlt_sources/common/ducklake_options.py` | `dlt_sources/lakehouse/options.py` (rename — not part of dlt destinations) |
| `dlt_sources/common/ducklake_pool.py` | `dlt_sources/lakehouse/pool.py` (rename — not part of dlt destinations) |

### Single DuckLake namespace — `ducklake_cianfhoghlaim` (master plan §1.1)

| Old namespace | New namespace |
|:--|:--|
| `ducklake_oideachais` | `ducklake_cianfhoghlaim` |
| `ducklake_educational` | `ducklake_cianfhoghlaim` |
| `ducklake_crypteolas` | `ducklake_cianfhoghlaim` |
| `ducklake_tertiary` | `ducklake_cianfhoghlaim` |
| `ducklake_uog` | `ducklake_cianfhoghlaim` |
| `ducklake_cie` | `ducklake_cianfhoghlaim` |
| `ducklake_tuath` | `ducklake_cianfhoghlaim` |
| `ducklake_meaisinfhoghlaim` | `ducklake_cianfhoghlaim` |
| `ducklake_aleyum` | `ducklake_cianfhoghlaim` |
| `ducklake_croilar` | `ducklake_cianfhoghlaim` |
| `ducklake_oideachais_quadrant` | (NEW — per-quadrant Postgres metadata schema) |
| `ducklake_tuatha_quadrant` | (NEW) |
| `ducklake_croilar_quadrant` | (NEW) |
| `ducklake_agents_quadrant` | (NEW) |
| `ducklake_media_quadrant` | (NEW) |

### Themed sub-tree split — `official_media/` → 4 sub-dirs (master plan §7.1)

| Old | New |
|:--|:--|
| `dlt_sources/official_media/sct/` | `dlt_sources/official_media/british_crown/sct/` |
| `dlt_sources/official_media/wls/` | `dlt_sources/official_media/british_crown/wls/` |
| `dlt_sources/official_media/ggy/` | `dlt_sources/official_media/channel_islands/ggy/` |
| `dlt_sources/official_media/iom/` | `dlt_sources/official_media/channel_islands/iom/` |
| `dlt_sources/official_media/jsy/` | `dlt_sources/official_media/channel_islands/jsy/` |
| `dlt_sources/official_media/companies_house/` | `dlt_sources/official_media/companies/companies_house/` |
| `dlt_sources/official_media/fediverse.py` | `dlt_sources/official_media/fediverse/` |

### Validation gate — `mise run lint:dlt-paths` (master plan §1.10)

The `lint:dlt-paths` mise task (added per master plan §1.10) fails
the CI build if any source `.py` file exists in the deprecated
`dlt_sources/language/` directory (other than the `__init__.py`
shim that re-exports from the 3 themed sub-trees).

### Sister-repo carve (master plan INVARIANT 1)

The UD corpora (`universal_dependencies.py`) are owned by the
`ciancheiltis` sister repo. Pinned cross-repo reference:
`ciar://ciancheiltis/datasets/ud_<lang>@v<N>` (per master plan
INVARIANT 1 — bilingual carve rule).


---

## Pre-Wave-1 legacy aliases (still in effect)

### European nations — ISO 3-letter → full snake_case

| Old | New |
|:--|:--|
| `dlt/european_nations/{alb,aut,bel,bgr,bih,che,cyp,cze,deu,dnk,esp,est,fin,fra,geo,grc,hrv,hun,isl,ita,lie,ltu,lux,lva,mda,mkd,mlt,mne,nld,nor,pol,prt,rou,srb,svk,svn,swe,tur,ukr,xkx}/` | `dlt/european_nations/{albania,austria,belgium,bulgaria,bosnia_and_herzegovina,switzerland,cyprus,czechia,germany,denmark,spain,estonia,finland,france,georgia,greece,croatia,hungary,iceland,italy,liechtenstein,lithuania,luxembourg,latvia,moldova,north_macedonia,malta,montenegro,netherlands,norway,poland,portugal,romania,serbia,slovakia,slovenia,sweden,turkey,ukraine,kosovo}/` |

### Commonwealth — ISO 3-letter → full snake_case

| Old | New |
|:--|:--|
| `dlt/commonwealth/{aus,can,ind,nga,nzl,zaf}/` | `dlt/commonwealth/{australia,canada,india,nigeria,new_zealand,south_africa}/` |

### Canada — provinces

| Old | New |
|:--|:--|
| `dlt/commonwealth/can/{ab,bc,mb,nb,nl,ns,nt,nu,on,pe,qc,sk,yt}/` | `dlt/commonwealth/canada/provinces/{alberta,british_columbia,manitoba,new_brunswick,newfoundland_and_labrador,nova_scotia,northwest_territories,nunavut,ontario,prince_edward_island,quebec,saskatchewan,yukon}/` |

### Nigeria — states

| Old | New |
|:--|:--|
| `dlt/commonwealth/nigeria/states/nga_{abi,ada,aki,ana,bau,bay,ben,bor,crs,del,ebi,edo,eki,enu,fct,gom,imo,jig,kad,kan,kat,keb,kog,kwa,los,nas,ngr,ogn,ond,osn,oyo,plt,riv,sok,tar,yob,zam}/` | `dlt/commonwealth/nigeria/states/{abia,adamawa,akwa_ibom,anambra,bauchi,bayelsa,benue,borno,cross_river,delta,ebonyi,edo,ekiti,enugu,federal_capital_territory,gombe,imo,jigawa,kaduna,kano,katsina,kebbi,kogi,kwara,lagos,nasarawa,niger,ogun,ondo,osun,oyo,plateau,rivers,sokoto,taraba,yobe,zamfara}/` |

### British Isles — collapse dual naming

| Old | New |
|:--|:--|
| `dlt/british_isles/en/` | `dlt/british_isles/england/` |
| `dlt/british_isles/ni/` | `dlt/british_isles/northern_ireland/` |
| `dlt/british_isles/sct/` | `dlt/british_isles/scotland/` |
| `dlt/british_isles/wls/` | `dlt/british_isles/wales/` |
| `dlt/british_isles/iom/` | `dlt/british_isles/isle_of_man/` |
| `dlt/british_isles/jey/` | `dlt/british_isles/jersey/` |
| `dlt/british_isles/ggy/` | `dlt/british_isles/guernsey/` |

### Americas — `americas/` → `american_nations/`

| Old | New |
|:--|:--|
| `dlt/americas/{bra,mex,us,ven}/` | `dlt/american_nations/{brazil,mexico,united_states,venezuela}/` |
