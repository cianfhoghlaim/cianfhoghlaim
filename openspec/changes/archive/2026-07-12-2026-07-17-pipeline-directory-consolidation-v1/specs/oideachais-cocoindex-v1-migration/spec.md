# oideachais-cocoindex-v1-migration

## ADDED Requirements

### Requirement: CocoIndex v1 apps SHALL be organised in jurisdiction subdirectories

CocoIndex v1 Apps SHALL live under
`cocoindex/{european_nations,commonwealth,british_isles,american_nations}/<full>/<topic>_embedding.py`. Cross-jurisdiction apps
SHALL live under
`cocoindex/{european_nations,commonwealth,british_isles}_cross/`.

#### Scenario: cocoindex/european_nations/germany has the per-country app

- **WHEN** the directory consolidation change is materialised
- **THEN** `cocoindex/european_nations/germany/education_embedding.py`
  SHALL exist
- **AND** `cocoindex/european_nations_cross/law_embedding.py`
  SHALL exist
- **AND** `cocoindex/european_nations_deu_education_embedding.py`
  SHALL NOT exist
- **AND** `cocoindex/european_nations_law_embedding.py` SHALL NOT
  exist at the root

### Requirement: CocoIndex subdirectories by purpose SHALL exist

CocoIndex purpose-based subdirectories SHALL exist at the root of
`cocoindex/`. The required subdirectories are `_shared/`
(cross-cutting helpers), `subjects/` (per-subject
cross-jurisdiction apps), `media/` (image, audio, OCR, apple
photos), `portfolio/` (croílár heritage + CV),
`knowledge_graph/` (Cognify, multi-hop search, YouTube KG),
`infrastructure/` (codebase indexing, API indexing, filesystem
indexing, agent registry), `corpus/` (multi-source corpora:
leabharlann, root PDFs, government circulars, Dúchas, unified),
and `celtic/` (Celtic-language embeddings).

#### Scenario: All required subdirectories exist

- **WHEN** the directory consolidation change is materialised
- **THEN** all of `cocoindex/{_shared,american_nations,british_isles,european_nations,european_nations_cross,commonwealth,commonwealth_cross,celtic,subjects,media,portfolio,knowledge_graph,infrastructure,corpus,biep_parity}/`
  SHALL exist
- **AND** `cocoindex/subjects/mathematics_embedding.py` SHALL exist
- **AND** `cocoindex/corpus/leabharlann_flow.py` SHALL exist
- **AND** `cocoindex/infrastructure/codebase_indexing.py` SHALL
  exist
- **AND** `cocoindex/knowledge_graph/cognify.py` SHALL exist