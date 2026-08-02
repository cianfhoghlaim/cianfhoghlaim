---
name: memgraph
description: Expert assistance for graph database development with Memgraph. Use when users need Cypher queries, graph data modeling, real-time analytics, streaming data processing, knowledge graphs, or GraphRAG applications.
---

# Memgraph - High-Performance Graph Database

**Version:** 3.x | **Last Updated:** 2025-01

## Overview

Memgraph is an in-memory graph database optimized for:

- **Real-Time Analytics**: Sub-millisecond query latency
- **Streaming Processing**: Native Kafka/Pulsar/RabbitMQ connectors
- **HTAP Workloads**: Hybrid transactional/analytical processing
- **GraphRAG**: Native vector search for AI applications
- **ACID Compliance**: Full transaction support

**Performance**: 3-8x faster than Neo4j, 132x higher write throughput

**Documentation**: https://memgraph.com/docs

## When to Use This Skill

Activate when users need:

- "Write Cypher queries for graph data"
- "Model data as a graph"
- "Build a knowledge graph"
- "Implement real-time graph analytics"
- "Process streaming graph data"
- "Run graph algorithms (PageRank, community detection)"

## Core Concepts

### Labeled Property Graph Model

**Components:**
1. **Nodes**: Entities (User, Product, Document)
2. **Relationships**: Directed edges connecting nodes
3. **Properties**: Key-value pairs on nodes/relationships
4. **Labels**: Node categorizations

**Naming Conventions:**
- Node labels: `CamelCase` (User, ProductCategory)
- Relationship types: `UPPER_CASE` (KNOWS, BELONGS_TO)
- Properties: `camelCase` (userName, createdAt)

## Cypher Query Patterns

### CRUD Operations

**Create:**
```cypher
// Create node
CREATE (u:User {name: 'Alice', email: 'alice@example.com', age: 30});

// Create relationship
MATCH (a:User {name: 'Alice'}), (b:User {name: 'Bob'})
CREATE (a)-[:FOLLOWS {since: date()}]->(b);

// Upsert with MERGE
MERGE (u:User {email: 'alice@example.com'})
ON CREATE SET u.created = timestamp(), u.name = 'Alice'
ON MATCH SET u.lastSeen = timestamp()
RETURN u;
```

**Read:**
```cypher
// Simple match
MATCH (u:User {name: 'Alice'}) RETURN u;

// Pattern matching
MATCH (u:User)-[:FOLLOWS]->(followed:User)
RETURN u.name, collect(followed.name) AS following;

// Complex query
MATCH (user:User)-[r:RATED]->(movie:Movie)<-[:OF_GENRE]-(genre:Genre {name: 'Comedy'})
WHERE r.rating > 3
RETURN movie.title, r.rating
ORDER BY r.rating DESC
LIMIT 10;
```

**Update:**
```cypher
MATCH (u:User {name: 'Alice'})
SET u.age = 31, u.updated = timestamp();

// Multiple properties
MATCH (u:User {name: 'Alice'})
SET u += {location: 'NYC', verified: true};
```

**Delete:**
```cypher
// Delete node and relationships
MATCH (u:User {name: 'Alice'})
DETACH DELETE u;

// Delete only relationships
MATCH (u:User {name: 'Alice'})-[r:FOLLOWS]->()
DELETE r;
```

### Path Traversal

**Shortest Path (BFS):**
```cypher
MATCH path=(start {id: 0})-[*BFS]->(end {id: 8})
RETURN path;

// With filtering
MATCH path=(:City {name: 'London'})-[r:ROAD *BFS ..3 (r, n | r.continent = 'Europe')]->(:City)
RETURN path;
```

**All Paths (DFS):**
```cypher
MATCH path=(start {id: 0})-[*2..4]->(end {id: 8})
RETURN path;
```

**Weighted Shortest Path:**
```cypher
MATCH p = (:City {name: "Paris"})
  -[:Road *WSHORTEST (e, v | e.distance) total_weight]->
  (:City {name: "Berlin"})
RETURN nodes(p) AS cities, total_weight;
```

### Aggregations

```cypher
// Counting
MATCH (n:User) RETURN count(n);

// Statistical functions
MATCH (n:User) RETURN sum(n.age), avg(n.age), min(n.age), max(n.age);

// Collect into list
MATCH (n:User) RETURN collect(n.name) AS names;

// Group by
MATCH (u:User)-[:POSTED]->(p:Post)
RETURN u.name, count(p) AS post_count
ORDER BY post_count DESC;
```

## Indexing and Performance

### Creating Indexes

```cypher
// Label-property index
CREATE INDEX ON :User(email);

// Composite index
CREATE INDEX ON :User(name, age);

// View indexes
SHOW INDEX INFO;

// Drop index
DROP INDEX ON :User(email);
```

### ANALYZE GRAPH

**Critical for performance** - run after bulk operations:

```cypher
ANALYZE GRAPH;
```

This helps Memgraph:
- Calculate node degree statistics
- Optimize MERGE on supernodes
- Improve query planning

### Query Profiling

```cypher
// View plan without execution
EXPLAIN MATCH (n:User)-[:FOLLOWS]->(m) RETURN m;

// Execute and profile
PROFILE MATCH (n:User)-[:FOLLOWS]->(m) RETURN m;
```

## Graph Algorithms (MAGE)

### Centrality

```cypher
// PageRank
CALL pagerank.get(100, 0.85)
YIELD node, rank
RETURN node.name, rank
ORDER BY rank DESC
LIMIT 10;

// Betweenness Centrality
CALL betweenness_centrality.get()
YIELD node, betweenness
RETURN node.name, betweenness
ORDER BY betweenness DESC;
```

### Community Detection

```cypher
// Louvain method
CALL community_detection.get()
YIELD node, community_id
RETURN community_id, collect(node.name) AS members;
```

### Machine Learning

```cypher
// Node2Vec embeddings
CALL node2vec.get()
YIELD node, embedding;

// Link prediction
CALL link_prediction.predict()
YIELD node1, node2, probability
WHERE probability > 0.7
RETURN node1, node2, probability;
```

## Common Use Cases

### Social Network

```cypher
// Mutual friends
MATCH (me:User {name: 'Alice'})-[:FRIENDS_WITH]-(mutual)-[:FRIENDS_WITH]-(friend:User {name: 'Bob'})
RETURN mutual.name;

// Friend recommendations
MATCH (me:User {name: 'Alice'})-[:FRIENDS_WITH]-()-[:FRIENDS_WITH]-(recommendation)
WHERE NOT (me)-[:FRIENDS_WITH]-(recommendation) AND me <> recommendation
RETURN DISTINCT recommendation.name, count(*) AS mutual_friends
ORDER BY mutual_friends DESC
LIMIT 10;
```

### Fraud Detection

```cypher
// Suspicious transaction patterns
MATCH (account:Account)-[t:TRANSACTION]->(other:Account)
WHERE t.timestamp > timestamp() - 3600000
WITH account, count(t) AS tx_count, sum(t.amount) AS total_amount
WHERE tx_count > 50 OR total_amount > 100000
RETURN account.id, tx_count, total_amount;

// Circular money flows
MATCH path = (a:Account)-[:TRANSACTION *3..5]->(a)
WHERE all(tx IN relationships(path) WHERE tx.amount > 10000)
RETURN path;
```

### Knowledge Graph

```cypher
// Multi-hop reasoning
MATCH path = (entity:Entity {name: 'Drug A'})-[:RELATED_TO*1..3]-(related:Entity)
WHERE related.type = 'Disease'
RETURN path;

// Co-occurrence analysis
MATCH (e1:Entity)<-[:MENTIONS]-(doc:Document)-[:MENTIONS]->(e2:Entity)
WHERE e1.name = 'Einstein' AND e1 <> e2
RETURN e2.name, count(doc) AS co_occurrences
ORDER BY co_occurrences DESC;
```

### Recommendation Engine

```cypher
// Collaborative filtering
MATCH (user:User {id: $userId})-[:RATED {rating: 5}]->(item:Item)
      <-[:RATED {rating: 5}]-(similar:User)-[:RATED {rating: 5}]->(recommendation:Item)
WHERE NOT (user)-[:RATED]->(recommendation)
RETURN recommendation.title, count(*) AS score
ORDER BY score DESC
LIMIT 10;
```

## Python Integration (GQLAlchemy)

```python
from gqlalchemy import Memgraph, Node, Relationship, Field

# Connect
db = Memgraph(host='127.0.0.1', port=7687)

# Define models
class User(Node):
    email: str = Field(unique=True, exists=True, db=db)
    name: str = Field(exists=True, db=db)
    age: int = Field()

class Follows(Relationship, type="FOLLOWS"):
    since: str = Field()

# Create nodes
alice = User(email="alice@example.com", name="Alice", age=30).save(db)
bob = User(email="bob@example.com", name="Bob", age=25).save(db)

# Create relationship
follows = Follows(
    _start_node_id=alice._id,
    _end_node_id=bob._id,
    since="2024-01-15"
).save(db)

# Query
results = db.execute_and_fetch("MATCH (u:User) WHERE u.age > 25 RETURN u")
for result in results:
    print(result['u'].name)
```

## Streaming Data

```cypher
// Create Kafka stream
CREATE KAFKA STREAM user_events
TOPICS user_activity
TRANSFORM event_processor.process_event
BOOTSTRAP_SERVERS 'localhost:9092'
BATCH_INTERVAL 100;

// Manage streams
SHOW STREAMS;
START STREAM user_events;
STOP STREAM user_events;
```

## Data Modeling Best Practices

1. **Avoid Supernodes**: Nodes with 50k+ connections hurt performance
2. **Index Strategically**: Only high-cardinality, frequently queried properties
3. **Use Relationships for Shared Data**: Don't duplicate across nodes
4. **Think Graph-First**: Model for traversals, not SQL joins
5. **Run ANALYZE GRAPH**: After bulk loads and before complex queries

## Storage Modes

```cypher
// Transactional (OLTP) - default
SET DATABASE SETTING 'storage.storage_mode' TO 'IN_MEMORY_TRANSACTIONAL';

// Analytical (OLAP) - 6x faster import
SET DATABASE SETTING 'storage.storage_mode' TO 'IN_MEMORY_ANALYTICAL';
```

## Troubleshooting

### Slow Queries
1. Run `PROFILE` to find bottlenecks
2. Check indexes exist on filtered properties
3. Run `ANALYZE GRAPH`
4. Use inline filtering vs WHERE when possible

### High Memory
1. Check storage mode
2. Review indexing strategy
3. Look for data duplication

### Supernode Problems
1. Run `ANALYZE GRAPH`
2. Add filtering early in query
3. Consider denormalization

## Resources

- **Documentation**: https://memgraph.com/docs
- **Cypher Manual**: https://memgraph.com/docs/cypher-manual
- **MAGE Library**: https://memgraph.com/docs/mage
- **GitHub**: https://github.com/memgraph/memgraph
- **GQLAlchemy**: https://memgraph.github.io/gqlalchemy
