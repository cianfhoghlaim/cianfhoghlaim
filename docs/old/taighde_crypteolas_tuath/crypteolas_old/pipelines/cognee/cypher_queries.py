"""Cypher Query Templates for Memgraph.

Common Cypher queries for exploring and analyzing the knowledge graph.
Compatible with Neo4j and Memgraph.
"""

# Graph exploration queries
EXPLORE_ALL = """
MATCH p=()-[]-()
RETURN p
LIMIT 100
"""

EXPLORE_ENTITIES = """
MATCH (e:Entity)
RETURN e.value as entity
ORDER BY e.value
LIMIT $limit
"""

EXPLORE_DOCUMENTS = """
MATCH (d:Document)
RETURN d.filename as filename, d.title as title, d.summary as summary
ORDER BY d.filename
LIMIT $limit
"""

# Entity queries
FIND_ENTITY = """
MATCH (e:Entity)
WHERE toLower(e.value) CONTAINS toLower($query)
RETURN e.value as entity
LIMIT $limit
"""

ENTITY_RELATIONSHIPS = """
MATCH (e:Entity {value: $entity})-[r]-(related)
RETURN type(r) as relationship_type,
       r.predicate as predicate,
       CASE WHEN startNode(r) = e THEN 'outgoing' ELSE 'incoming' END as direction,
       related.value as related_entity
"""

ENTITY_DOCUMENTS = """
MATCH (d:Document)-[:MENTIONS]->(e:Entity {value: $entity})
RETURN d.filename as filename, d.title as title
"""

# Relationship queries
RELATIONSHIP_PATTERN = """
MATCH (s:Entity)-[r:RELATIONSHIP]->(o:Entity)
WHERE r.predicate = $predicate
RETURN s.value as subject, r.predicate as predicate, o.value as object
LIMIT $limit
"""

ALL_PREDICATES = """
MATCH ()-[r:RELATIONSHIP]->()
RETURN DISTINCT r.predicate as predicate, count(r) as count
ORDER BY count DESC
"""

# Path queries
SHORTEST_PATH = """
MATCH p=shortestPath((s:Entity {value: $source})-[*]-(t:Entity {value: $target}))
RETURN p
"""

ALL_PATHS = """
MATCH p=(s:Entity {value: $source})-[*1..3]-(t:Entity {value: $target})
RETURN p
LIMIT $limit
"""

# Analytics queries
MOST_CONNECTED = """
MATCH (e:Entity)-[r]-()
RETURN e.value as entity, count(r) as connections
ORDER BY connections DESC
LIMIT $limit
"""

CENTRALITY = """
MATCH (e:Entity)
WITH e, size((e)-[]-()) as degree
RETURN e.value as entity, degree
ORDER BY degree DESC
LIMIT $limit
"""

DOCUMENT_ENTITY_MATRIX = """
MATCH (d:Document)-[:MENTIONS]->(e:Entity)
RETURN d.filename as document, collect(e.value) as entities
"""

# Subgraph queries
TECHNOLOGY_SUBGRAPH = """
MATCH (t:Entity)-[r:RELATIONSHIP]->(related:Entity)
WHERE t.value IN $technologies
RETURN t.value as technology, r.predicate as relationship, related.value as related
"""

TOPIC_CLUSTER = """
MATCH (e:Entity)-[r]-(related:Entity)
WHERE e.value = $topic
WITH related
MATCH (related)-[r2]-(second_degree:Entity)
RETURN DISTINCT related.value as first_degree,
       collect(DISTINCT second_degree.value) as second_degree
"""

# Search queries
SEMANTIC_SEARCH = """
MATCH (e:Entity)
WHERE toLower(e.value) CONTAINS toLower($query)
WITH e
MATCH p=(e)-[r*0..2]-(related)
RETURN e.value as entity,
       [rel in relationships(p) | type(rel)] as path_types,
       [node in nodes(p) | node.value] as path_nodes
LIMIT $limit
"""

FULL_TEXT_SEARCH = """
MATCH (d:Document)
WHERE toLower(d.title) CONTAINS toLower($query)
   OR toLower(d.summary) CONTAINS toLower($query)
RETURN d.filename as filename, d.title as title, d.summary as summary
LIMIT $limit
"""

# Data quality queries
ORPHAN_ENTITIES = """
MATCH (e:Entity)
WHERE NOT (e)-[]-()
RETURN e.value as orphan_entity
"""

DUPLICATE_CHECK = """
MATCH (e1:Entity), (e2:Entity)
WHERE e1.value < e2.value
  AND toLower(e1.value) = toLower(e2.value)
RETURN e1.value as entity1, e2.value as entity2
"""

# Statistics
GRAPH_STATS = """
MATCH (n)
WITH labels(n)[0] as label, count(n) as count
RETURN label, count
ORDER BY count DESC
"""

EDGE_STATS = """
MATCH ()-[r]->()
WITH type(r) as type, count(r) as count
RETURN type, count
ORDER BY count DESC
"""


class CypherQueryRunner:
    """Helper class to run Cypher queries."""

    def __init__(self, driver):
        self.driver = driver

    def run(self, query: str, params: dict | None = None) -> list[dict]:
        """Execute a Cypher query."""
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [dict(record) for record in result]

    def explore(self, limit: int = 100):
        """Explore entities in the graph."""
        return self.run(EXPLORE_ENTITIES, {"limit": limit})

    def find_entity(self, query: str, limit: int = 10):
        """Search for entities matching query."""
        return self.run(FIND_ENTITY, {"query": query, "limit": limit})

    def entity_relationships(self, entity: str):
        """Get relationships for an entity."""
        return self.run(ENTITY_RELATIONSHIPS, {"entity": entity})

    def most_connected(self, limit: int = 10):
        """Get most connected entities."""
        return self.run(MOST_CONNECTED, {"limit": limit})

    def shortest_path(self, source: str, target: str):
        """Find shortest path between entities."""
        return self.run(SHORTEST_PATH, {"source": source, "target": target})

    def semantic_search(self, query: str, limit: int = 10):
        """Perform semantic search."""
        return self.run(SEMANTIC_SEARCH, {"query": query, "limit": limit})

    def stats(self) -> dict:
        """Get graph statistics."""
        nodes = self.run(GRAPH_STATS)
        edges = self.run(EDGE_STATS)
        return {"nodes": nodes, "edges": edges}
