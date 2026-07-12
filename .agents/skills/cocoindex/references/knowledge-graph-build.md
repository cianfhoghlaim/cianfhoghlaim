# Knowledge-Graph Build in CocoIndex v1

CocoIndex v1 supports building knowledge graphs in Neo4j and FalkorDB
via `mount_table_target` for nodes + `mount_relation_target` for
edges. The canonical KCG pattern is `meeting_notes_graph_neo4j` /
`meeting_notes_graph_falkordb` (a 3-phase pipeline: extract →
resolve entities → declare relations).

## Three-phase pattern

```python
import cocoindex as coco
from cocoindex.connectors import neo4j, falkordb

KG_DB = coco.ContextKey[neo4j.ConnectionFactory]("kg_db", detect_change=False)

# Phase 1: Extract entities from each source document
@coco.fn(memo=True)
async def extract_entities(file, entity_table: neo4j.TableTarget[Entity]) -> None:
    text = await file.read_text()
    entities = b.ExtractEntities(text)  # BAML function returning Entity[]
    for e in entities:
        entity_table.declare_record(
            record=Entity(id=e.id, name=e.name, type=e.type, …)
        )

# Phase 2: Resolve duplicate entities (e.g. "Patrick" == "Pat")
@coco.fn
async def resolve_entities(entity_table, resolved_table) -> None:
    async for entity in entity_table.iter():
        canonical_id = await resolve_to_canonical(entity)
        resolved_table.declare_record(
            record=ResolvedEntity(canonical_id=canonical_id, name=entity.name)
        )

# Phase 3: Declare relations between resolved entities
@coco.fn
async def declare_relations(rel_table: neo4j.TableTarget[Relation]) -> None:
    async for rel in relation_source.iter():
        rel_table.declare_relation(
            from_id=rel.from_id,
            to_id=rel.to_id,
            record=Relation(kind=rel.kind, weight=rel.weight),
        )
```

## Neo4j (mount_table_target for nodes + relations)

```python
await neo4j.mount_table_target(
    KG_DB, label="Person",
    table_schema=await neo4j.TableSchema.from_class(Person, primary_key="id"),
)
await neo4j.mount_relation_target(
    KG_DB, rel_type="KNOWS",
    from_table=person_table, to_table=person_table,
)
```

The relation target auto-derives the edge key from `(from_id, to_id)`.

## FalkorDB (similar API)

```python
from cocoindex.connectors import falkordb

await falkordb.mount_table_target(
    KG_DB, "Person",
    await falkordb.TableSchema.from_class(Person, primary_key="id"),
    primary_key="id",
)
```

## In-repo examples (canonical v1)

- `cocoindex/learning_outcome_graph.py` — the
  KCG in-repo knowledge-graph flow (5-stage cross-stage + 3
  leabharlann cognify adapters)
- `cocoindex/docs_skills_consolidation.py` —
  3-phase FalkorDB graph: DocSkill, Concept, ConsolidationGroup with
  TAGGED / CONSOLIDATED_INTO / RELATES_TO edges
- `cocoindex/cognee_integration/` — Cognee-driven cognify (5
  stages)

The external examples `meeting_notes_graph_neo4j/` and
`meeting_notes_graph_falkordb/` (now in the upstream cocoindex
repo) are the canonical references for the 3-phase pattern.
