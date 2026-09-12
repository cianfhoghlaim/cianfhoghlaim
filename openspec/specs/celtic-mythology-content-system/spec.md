# Celtic Mythology Content System Capability

## Purpose

`celtic-mythology-content-system` is the BAML SSOT for the 6 Celtic
pantheons + Irish dynastic history + Welsh Mabinogi + Scottish Ulster
Cycle + Manx + Cornish mythic cycles. It emits structured extractions
for every mythology source document so the Tuatha educational MMO
can render NPC dialogue + quest backstories + lore cards that cite
their source.

This capability is referenced by:
- `openspec/changes/2026-09-01-celtic-mythology-content-system-v1`

## Requirements

### Requirement: 6 Celtic pantheon extraction

The BAML extraction SHALL cover 6 pantheons: Tuatha Dé Danann
(Irish), Fianna (Irish warrior band), Mabinogi (Welsh incl.
Gwydion), Ulster Cycle (NI), Manannán mac Lir (IoM), Scottish
myth (SQA).

#### Scenario: Pantheon extraction

- **WHEN** a mythology corpus row is ingested with `corpus_id`,
  `text`, `language`, `pantheon`
- **THEN** the BAML extraction SHALL emit a `MythologyLore`
  dataclass with `pantheon`, `characters`, `locations`,
  `evidence_spans`, `confidence` populated

### Requirement: Bilingual invariant

Every extraction SHALL preserve the source's bilingual invariant
(Cornish-English, Irish-English, Welsh-English, Scottish Gaelic-
English) and emit both languages as separate fields.

#### Scenario: Bilingual extraction

- **WHEN** a bilingual source row is ingested
- **THEN** the extraction SHALL populate both `text_primary` and
  `text_secondary` fields and emit the canonical LO numbering

### Requirement: Difficulty 1-5 rubric

Every extraction SHALL emit a `difficulty` score (1-5) reflecting
the source's curriculum level (primary → advanced higher).

### Requirement: Evidence PDF citations

Every extraction SHALL cite the source PDF (`evidence_pdfs`) with
page + bbox so the Evidence Ladder rungs 1-3 are preserved.
