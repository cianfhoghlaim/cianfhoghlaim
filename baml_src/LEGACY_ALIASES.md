# LEGACY_ALIASES — baml_src/

Per the
[`2026-07-17-pipeline-directory-consolidation-v1`](../../changes/2026-07-17-pipeline-directory-consolidation-v1/proposal.md)
openspec change. **All old paths remain importable via deprecation
shims for at least one release cycle.**

## European nations — ISO 3-letter → full snake_case

| Old | New |
|:--|:--|
| `baml_src/european_nations/alb/` | `baml_src/european_nations/albania/` |
| `baml_src/european_nations/aut/` | `baml_src/european_nations/austria/` |
| `baml_src/european_nations/bel/` | `baml_src/european_nations/belgium/` |
| `baml_src/european_nations/bgr/` | `baml_src/european_nations/bulgaria/` |
| `baml_src/european_nations/bih/` | `baml_src/european_nations/bosnia_and_herzegovina/` |
| `baml_src/european_nations/che/` | `baml_src/european_nations/switzerland/` |
| `baml_src/european_nations/cyp/` | `baml_src/european_nations/cyprus/` |
| `baml_src/european_nations/cze/` | `baml_src/european_nations/czechia/` |
| `baml_src/european_nations/deu/` | `baml_src/european_nations/germany/` |
| `baml_src/european_nations/dnk/` | `baml_src/european_nations/denmark/` |
| `baml_src/european_nations/esp/` | `baml_src/european_nations/spain/` |
| `baml_src/european_nations/est/` | `baml_src/european_nations/estonia/` |
| `baml_src/european_nations/fin/` | `baml_src/european_nations/finland/` |
| `baml_src/european_nations/fra/` | `baml_src/european_nations/france/` |
| `baml_src/european_nations/geo/` | `baml_src/european_nations/georgia/` |
| `baml_src/european_nations/grc/` | `baml_src/european_nations/greece/` |
| `baml_src/european_nations/hrv/` | `baml_src/european_nations/croatia/` |
| `baml_src/european_nations/hun/` | `baml_src/european_nations/hungary/` |
| `baml_src/european_nations/isl/` | `baml_src/european_nations/iceland/` |
| `baml_src/european_nations/ita/` | `baml_src/european_nations/italy/` |
| `baml_src/european_nations/lie/` | `baml_src/european_nations/liechtenstein/` |
| `baml_src/european_nations/ltu/` | `baml_src/european_nations/lithuania/` |
| `baml_src/european_nations/lux/` | `baml_src/european_nations/luxembourg/` |
| `baml_src/european_nations/lva/` | `baml_src/european_nations/latvia/` |
| `baml_src/european_nations/mda/` | `baml_src/european_nations/moldova/` |
| `baml_src/european_nations/mkd/` | `baml_src/european_nations/north_macedonia/` |
| `baml_src/european_nations/mlt/` | `baml_src/european_nations/malta/` |
| `baml_src/european_nations/mne/` | `baml_src/european_nations/montenegro/` |
| `baml_src/european_nations/nld/` | `baml_src/european_nations/netherlands/` |
| `baml_src/european_nations/nor/` | `baml_src/european_nations/norway/` |
| `baml_src/european_nations/pol/` | `baml_src/european_nations/poland/` |
| `baml_src/european_nations/prt/` | `baml_src/european_nations/portugal/` |
| `baml_src/european_nations/rou/` | `baml_src/european_nations/romania/` |
| `baml_src/european_nations/srb/` | `baml_src/european_nations/serbia/` |
| `baml_src/european_nations/svk/` | `baml_src/european_nations/slovakia/` |
| `baml_src/european_nations/svn/` | `baml_src/european_nations/slovenia/` |
| `baml_src/european_nations/swe/` | `baml_src/european_nations/sweden/` |
| `baml_src/european_nations/tur/` | `baml_src/european_nations/turkey/` |
| `baml_src/european_nations/ukr/` | `baml_src/european_nations/ukraine/` |
| `baml_src/european_nations/xkx/` | `baml_src/european_nations/kosovo/` |

## Commonwealth — ISO 3-letter → full snake_case

| Old | New |
|:--|:--|
| `baml_src/commonwealth/aus/` | `baml_src/commonwealth/australia/` |
| `baml_src/commonwealth/can/` | `baml_src/commonwealth/canada/` |
| `baml_src/commonwealth/ind/` | `baml_src/commonwealth/india/` |
| `baml_src/commonwealth/nga/` | `baml_src/commonwealth/nigeria/` |
| `baml_src/commonwealth/nzl/` | `baml_src/commonwealth/new_zealand/` |
| `baml_src/commonwealth/zaf/` | `baml_src/commonwealth/south_africa/` |

## Canada — provinces

| Old | New |
|:--|:--|
| `baml_src/commonwealth/can/ab/` | `baml_src/commonwealth/canada/provinces/alberta/` |
| `baml_src/commonwealth/can/bc/` | `baml_src/commonwealth/canada/provinces/british_columbia/` |
| `baml_src/commonwealth/can/mb/` | `baml_src/commonwealth/canada/provinces/manitoba/` |
| `baml_src/commonwealth/can/nb/` | `baml_src/commonwealth/canada/provinces/new_brunswick/` |
| `baml_src/commonwealth/can/nl/` | `baml_src/commonwealth/canada/provinces/newfoundland_and_labrador/` |
| `baml_src/commonwealth/can/ns/` | `baml_src/commonwealth/canada/provinces/nova_scotia/` |
| `baml_src/commonwealth/can/nt/` | `baml_src/commonwealth/canada/provinces/northwest_territories/` |
| `baml_src/commonwealth/can/nu/` | `baml_src/commonwealth/canada/provinces/nunavut/` |
| `baml_src/commonwealth/can/on/` | `baml_src/commonwealth/canada/provinces/ontario/` |
| `baml_src/commonwealth/can/pe/` | `baml_src/commonwealth/canada/provinces/prince_edward_island/` |
| `baml_src/commonwealth/can/qc/` | `baml_src/commonwealth/canada/provinces/quebec/` |
| `baml_src/commonwealth/can/sk/` | `baml_src/commonwealth/canada/provinces/saskatchewan/` |
| `baml_src/commonwealth/can/yt/` | `baml_src/commonwealth/canada/provinces/yukon/` |

## British Isles — collapse dual naming

| Old | New |
|:--|:--|
| `baml_src/education/en/` | `baml_src/british_isles/england/` |
| `baml_src/education/england/` | `baml_src/british_isles/england/` |
| `baml_src/education/ni/` | `baml_src/british_isles/northern_ireland/` |
| `baml_src/education/northern_ireland/` | `baml_src/british_isles/northern_ireland/` |
| `baml_src/education/sct/` | `baml_src/british_isles/scotland/` |
| `baml_src/education/scotland/` | `baml_src/british_isles/scotland/` |
| `baml_src/education/wls/` | `baml_src/british_isles/wales/` |
| `baml_src/education/wales/` | `baml_src/british_isles/wales/` |
| `baml_src/education/ggy/` | `baml_src/british_isles/guernsey/` |
| `baml_src/education/guernsey/` | `baml_src/british_isles/guernsey/` |
| `baml_src/education/iom/` | `baml_src/british_isles/isle_of_man/` |
| `baml_src/education/isle_of_man/` | `baml_src/british_isles/isle_of_man/` |
| `baml_src/education/jey/` | `baml_src/british_isles/jersey/` |
| `baml_src/education/jersey/` | `baml_src/british_isles/jersey/` |

### British Isles sub-domain move (Ireland)

`baml_src/education/<topic>/` → `baml_src/british_isles/ireland/education/<topic>/` for: `lc_extraction`, `stages`, `subjects`, `grading`, `marking`, `web`, `pdfs`, `primary`, `junior_cycle`, `university`, `statistics`, `law`, `_shared`.

### British Isles cross-nation

`baml_src/education/cross_nation/` → `baml_src/british_isles/_cross/`.

## Americas — `americas/` → `american_nations/`

| Old | New |
|:--|:--|
| `baml_src/americas/bra/` | `baml_src/american_nations/brazil/` |
| `baml_src/americas/mex/` | `baml_src/american_nations/mexico/` |
| `baml_src/americas/ven/` | `baml_src/american_nations/venezuela/` |
| `baml_src/americas/us_us_ca/` | `baml_src/american_nations/united_states/` |