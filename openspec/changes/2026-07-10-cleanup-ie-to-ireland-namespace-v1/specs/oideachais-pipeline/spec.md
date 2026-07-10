## MODIFIED Requirements

### Requirement: Canonical post-v4 source namespaces for the Ireland/law quadrant

The system SHALL use the canonical post-v4 namespaces for every
Ireland/law dlt + baml + cocoindex + skills source.

All dlt + baml + cocoindex + skills sources for the Ireland/law
quadrant MUST use the canonical post-v4 namespaces:

- **DLT** — `cianfhoghlaim.dlt.british_isles.ireland.education.law.<source>`
  (replacing the legacy `cianfhoghlaim.dlt.british_isles.ie.law.<source>`)
- **BAML** — `cianfhoghlaim.baml.education.law.<schema>`
  (replacing the legacy `cianfhoghlaim.baml.ie.law.<schema>`)
- **Skills** — the `oideachais-ireland-education-law` skill (when added)
  references the canonical namespaces above

The legacy `dlt/british_isles/ie/` + `baml/ie/` trees SHALL NOT exist
on disk. There is no `oideachais.dlt.british_isles.ie.*` import path
in the active codebase.

#### Scenario: A consumer imports the canonical Ireland/law DLT sources

- **GIVEN** the 5 Ireland/law DLT source files (piab, courts,
  judgements, court_rules, legal_aid) at
  `cianfhoghlaim/dlt/british_isles/ireland/education/law/`
- **WHEN** a Dagster asset does
  `from cianfhoghlaim.dlt.british_isles.ireland.education.law import piab_source`
- **THEN** the import SHALL succeed (the canonical namespace is wired)
- **AND** `grep -rn 'dlt.british_isles.ie\|dlt/british_isles/ie' --include='*.py' cianfhoghlaim/` SHALL return 0 matches

#### Scenario: A consumer imports the canonical Ireland/law BAML schemas

- **GIVEN** the 6 Ireland/law BAML schema files (piab, courts,
  judgements, court_rules, legal_aid, shared_legal_enums) at
  `cianfhoghlaim/baml/education/law/`
- **WHEN** a Dagster asset does
  `from cianfhoghlaim.baml.education.law import shared_legal_enums`
- **THEN** the import SHALL succeed
- **AND** `grep -rn 'baml.ie\.\|baml/ie/' --include='*.{py,baml}' cianfhoghlaim/` SHALL return 0 matches

#### Scenario: The legacy `ie/` directories are removed

- **GIVEN** this openspec change is archived
- **WHEN** a developer runs
  `ls cianfhoghlaim/dlt/british_isles/ | grep -c '^ie$'`
- **THEN** the output SHALL be `0`
- **AND** `ls cianfhoghlaim/baml/ | grep -c '^ie$'` SHALL also be `0`
- **AND** `ls cianfhoghlaim/dlt/british_isles/ireland/education/law/`
  SHALL list the 5 migrated `.py` files
- **AND** `ls cianfhoghlaim/baml/education/law/`
  SHALL list the 6 migrated `.baml` files + `__init__.py`