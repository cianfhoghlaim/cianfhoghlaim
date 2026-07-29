## ADDED Requirements

### Requirement: British Isles per-subject completeness

The system MUST ensure that every British Isles nation (Scotland /
Wales / England / Northern Ireland + the Crown Dependencies) ships
the full 6-subject per-subject depth for the BIEP pattern. The 6
required subjects are:

1. mathematics
2. chemistry
3. biology
4. physics
5. language (native-language + literature)
6. computing_science

#### Scenario: Wales ships physics + biology

- **WHEN** the upgrade change is materialised
- **THEN** `dlt/british_isles/wls/education/subjects/physics/physics.py`
  MUST exist with its corresponding L1 def
- **AND** `dlt/british_isles/wls/education/subjects/biology/biology.py`
  MUST exist with its corresponding L1 def
- **AND** the BIEP language partition for Wales is `("en", "cy")`
  (English primary + Welsh secondary)
