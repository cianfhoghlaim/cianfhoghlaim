# Semantic Search Capability

## Purpose

`semantic-search` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

## Background
Vector-based semantic search for curriculum content, exam questions, and learning materials.
## Requirements
### Requirement: Curriculum Content Search
The system SHALL enable semantic search across curriculum content.

#### Scenario: Concept Search
- **GIVEN** a natural language query "how to solve quadratic equations"
- **WHEN** searched against curriculum content
- **THEN** relevant topics and learning outcomes are returned

#### Scenario: Bilingual Search
- **GIVEN** an Irish query "conas a réitíonn tú cothromóidí"
- **WHEN** searched
- **THEN** relevant content in both languages is returned

### Requirement: Exam Question Search
The system SHALL enable semantic search across exam papers.

#### Scenario: Similar Question Finding
- **GIVEN** a specific exam question
- **WHEN** searched for similar questions
- **THEN** questions testing similar concepts from other years are returned

#### Scenario: Topic-Based Question Retrieval
- **GIVEN** a topic "Integration by Parts"
- **WHEN** searched
- **THEN** all exam questions on that topic are returned

### Requirement: Multi-Modal Search
The system SHALL support search across text and visual content.

#### Scenario: Diagram Search
- **GIVEN** a description "triangle with inscribed circle"
- **WHEN** searched with ColPali
- **THEN** exam questions with matching diagrams are returned

#### Scenario: Table Search
- **GIVEN** a query about statistical data presentation
- **WHEN** searched
- **THEN** questions with relevant tables are returned

### Requirement: Filtered Search
The system SHALL support filtering search results.

#### Scenario: Subject Filter
- **GIVEN** a search query
- **WHEN** filtered by subject "Mathematics"
- **THEN** only mathematics content is returned

#### Scenario: Level Filter
- **GIVEN** a search query
- **WHEN** filtered by level "Higher"
- **THEN** only Higher Level content is returned

### Requirement: Leabharlann Query Handlers
The system SHALL expose three new query handlers for semantic search across the leabharlann archives.

#### Scenario: Books search
- **GIVEN** the user invokes `await search_leabharlann_books(query="Celtic placenames of Belfast", subject="gaeilge", limit=10)`
- **WHEN** the handler runs
- **THEN** the top 10 most similar chunks from `leabharlann_books` SHALL be returned
- **AND** each result SHALL include `filename`, `subject`, `chunk_text`, and `score`

#### Scenario: Zotero search with metadata filter
- **GIVEN** the user invokes `await search_leabharlann_zotero(query="handwritten essay recognition", htr_relevant=True, limit=5)`
- **WHEN** the handler runs
- **THEN** the top 5 most similar `ZoteroPaper` rows SHALL be returned
- **AND** only rows with `htr_relevant=true` SHALL be considered
- **AND** each result SHALL include `title`, `authors`, `year`, `venue`, `chunk_text`, and `score`

#### Scenario: Takeout search
- **GIVEN** the user invokes `await search_leabharlann_takeout(query="disability allowance", account="stedding_takeout", limit=10)`
- **WHEN** the handler runs
- **THEN** the top 10 most similar chunks from `leabharlann_takeout` SHALL be returned
- **AND** only rows with `account="stedding_takeout"` SHALL be considered

## Embedding Configuration

| Content Type | Model | Dimensions |
|--------------|-------|------------|
| Text content | text-embedding-3-large | 3072 |
| Irish text | GaBERT | 768 |
| Visual content | ColPali | 128 per patch |

## Batch Constraints

**MANDATORY:** All embedding operations must follow `.claude/CONSTRAINTS.md`:

```python
# CORRECT: Batch embeddings
embeddings = embed_batch(texts, batch_size=100)

# WRONG: Single-item embedding
# for text in texts:
#     embedding = embed([text])  # 100x slower!
```

## Search API

```python
# Semantic search
results = search(
    query="differentiation rules",
    collection="curriculum",
    filter={"subject": "mathematics", "level": "higher"},
    top_k=10
)

# Multi-vector search (ColPali)
results = search_visual(
    query="graph of sine function",
    collection="colpali_visual",
    top_k=5
)
```
