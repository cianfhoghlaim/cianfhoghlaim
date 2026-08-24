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
