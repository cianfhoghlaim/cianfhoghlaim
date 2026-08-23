# Spec Delta: celtic-history-research

## Purpose

`celtic-history-research` is the canonical stub surface for the
9 Celtic-history research topics (Tuatha Dé Danann + Irish
mythology + Celtic mythology + Celtic law + Brehon law + the 4
Celtic-history British Isles geographies: Aran Islands + Isle of
Skye + Isle of Man + Dyfed).

The capability is **GATED** for the downstream Celtic-MMO theming
change — none of the 9 source records materialise in this change.
The user's personal clippings at
`cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`
is the canonical source for the future theming change.

The capability was created by the 2026-08-23-tuatha-media-intel-
gameplay-capture-research-v1 refactor: the 9 Wikipedia pages that
were originally committed to
`dlt_sources/media/official/ncca_sec_celt_duchas_wikipedia/scrape.py`
were MOVED here as stub sources (per the user's brief: the Class E
"official" surface should be reserved for the actual official
government / police / defence / army / Acts / treaties surface).

## ADDED Requirements

### Requirement: 9 stub Celtic-history research sources, GATED

The system SHALL provide 9 stub DLT sources for the 9 Celtic-history
research topics. Each stub source yields zero rows in v1; the
materialisation is GATED for the downstream Celtic-MMO theming
change. The user's personal clippings directory
(`cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`)
is the canonical source for the future theming change.

The 9 stub sources SHALL be:

1. `dlt_sources/media/celtic_history_research/tuatha_de_danann/` —
   the supernatural race of pre-Christian Irish mythology
2. `dlt_sources/media/celtic_history_research/irish_mythology/` —
   the body of myths native to Ireland
3. `dlt_sources/media/celtic_history_research/celtic_mythology/` —
   the body of myths of the Celtic peoples
4. `dlt_sources/media/celtic_history_research/celtic_law/` —
   the body of ancient Celtic legal traditions
5. `dlt_sources/media/celtic_history_research/brehon_law/` —
   the ancient Irish law system
6. `dlt_sources/media/celtic_history_research/aran_islands/` —
   the Irish-speaking Gaeltacht islands off the west coast of Ireland
7. `dlt_sources/media/celtic_history_research/isle_of_skye/` —
   the Scottish Gaelic-speaking island
8. `dlt_sources/media/celtic_history_research/isle_of_man/` —
   the Manx-Gaelic-speaking Crown Dependency
9. `dlt_sources/media/celtic_history_research/dyfed/` —
   the medieval Brythonic kingdom in south-west Wales

Each stub source SHALL have a `source.yaml` declaring the
`status: stub` flag + the gated `acquisition_path: []` + the gated
`baml_functions: []` + the licensed Wikipedia source URL (CC-BY-SA-4.0
attribution preserved).

Each stub source SHALL have a `scrape.py` that yields zero rows
(the `@dlt.resource` declares the primary_key but the function
body is `return; yield  # noqa: unreachable`).

#### Scenario: A stub source is queried

- **GIVEN** the 9 stub sources are committed at the paths above
- **WHEN** the DLT pipeline runs any of the 9 sources
- **THEN** the source yields zero rows
- **AND** the system SHALL log "celtic_history_research: stub — gated
  for the downstream theming change"
- **AND** the `media_descriptor_coverage` asset check SHALL NOT
  fail (the 9 Celtic-history sources are explicitly stubbed)

#### Scenario: The downstream theming change activates a stub

- **GIVEN** the downstream Celtic-MMO theming change archives
- **AND** the operator sets `status: active` on a stub's `source.yaml`
- **WHEN** the DLT pipeline re-runs the source
- **THEN** the source yields the activation's per-page records
- **AND** the activation reads from the user's clippings
  directory as the canonical source
- **AND** the activation's records carry the
  `provenance.licence = "CC-BY-SA-4.0"` field (Wikipedia
  attribution preserved)

### Requirement: Cross-class drift contract

The system SHALL prevent the 9 Celtic-history topics from being
re-introduced into the Class E (official) surface. The
`media-intel-acquisition-plan` spec's Requirement 5 (the official
surface) is the exclusive home for the 6 educational body sources
(NCCA + SEC + DfE + SQA + WJEC + DESC) + the 8 new government
sources (UK + Éire + Crown Dependencies) + the 5 new
departments sources (UK + Éire + Scotia + Wales + Northern
Ireland).

The 9 Celtic-history topics SHALL NOT appear in the official
surface — they live exclusively in the `celtic_history_research/`
sub-package.

#### Scenario: A new official source is added

- **GIVEN** a new official source is added to the
  `dlt_sources/media/official/{government,departments}/` sub-tree
- **WHEN** the openspec change is authored
- **THEN** the change SHALL NOT add any Wikipedia URL whose
  topic is in the 9 Celtic-history topics list
- **AND** the change SHALL NOT add any URL whose
  `provenance.rights_holder` is "Wikipedia Foundation" (the 9
  Celtic-history topics use "Wikipedia editors (CC-BY-SA-4.0)" as
  the rights_holder per the per-source licence whitelist)
