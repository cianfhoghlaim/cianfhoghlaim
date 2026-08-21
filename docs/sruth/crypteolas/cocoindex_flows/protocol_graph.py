"""
Protocol Relationship Graph for Crypteolas.

Builds temporal knowledge graph of protocol relationships:
- Protocol dependencies (Aave uses Chainlink oracles)
- Integration patterns (UniswapV3 -> Curve -> Aave)
- Temporal evolution (protocol versions over time)
- Risk relationships (common vulnerabilities, shared dependencies)

Uses bi-temporal model:
- valid_time: When relationship is true in reality
- transaction_time: When we learned about it

Based on Graphiti temporal knowledge graph pattern.
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_MEMGRAPH_URI = os.getenv("MEMGRAPH_URI", "bolt://localhost:7687")


class ProtocolEntityType(str, Enum):
    """Types of entities in the protocol graph."""

    PROTOCOL = "Protocol"
    CONTRACT = "Contract"
    TOKEN = "Token"
    ORACLE = "Oracle"
    GOVERNANCE = "Governance"
    AUDIT = "Audit"
    VERSION = "Version"
    CHAIN = "Chain"
    RISK = "Risk"


class ProtocolRelationType(str, Enum):
    """Types of relationships between protocol entities."""

    # Dependency relationships
    USES = "USES"
    DEPENDS_ON = "DEPENDS_ON"
    INTEGRATES_WITH = "INTEGRATES_WITH"
    PROVIDES_ORACLE = "PROVIDES_ORACLE"

    # Governance relationships
    GOVERNS = "GOVERNS"
    VOTES_ON = "VOTES_ON"

    # Evolution relationships
    UPGRADES_TO = "UPGRADES_TO"
    FORKS_FROM = "FORKS_FROM"
    SUPERSEDES = "SUPERSEDES"

    # Security relationships
    AUDITED_BY = "AUDITED_BY"
    SHARES_VULNERABILITY = "SHARES_VULNERABILITY"
    SHARES_DEPENDENCY = "SHARES_DEPENDENCY"

    # Deployment relationships
    DEPLOYED_ON = "DEPLOYED_ON"
    BRIDGES_TO = "BRIDGES_TO"


@dataclass
class ProtocolEntity:
    """A protocol entity in the knowledge graph."""

    id: str
    entity_type: ProtocolEntityType
    name: str
    description: str | None = None

    # Bi-temporal fields
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    transaction_time: datetime = field(default_factory=datetime.utcnow)

    # Metadata
    chain: str | None = None
    version: str | None = None
    tvl_usd: float | None = None
    address: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProtocolRelationship:
    """A relationship between protocol entities."""

    source_id: str
    target_id: str
    relationship_type: ProtocolRelationType

    # Bi-temporal fields
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    transaction_time: datetime = field(default_factory=datetime.utcnow)

    # Relationship metadata
    confidence: float = 1.0
    evidence: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)


class ProtocolGraphClient:
    """
    Client for the protocol knowledge graph.

    Provides bi-temporal queries for protocol relationships.
    """

    def __init__(self, uri: str | None = None):
        self.uri = uri or DEFAULT_MEMGRAPH_URI
        self._driver = None

    def _get_driver(self):
        """Get or create Memgraph driver."""
        if self._driver is not None:
            return self._driver

        try:
            from neo4j import GraphDatabase
        except ImportError:
            raise ImportError("neo4j driver not installed. Run: pip install neo4j")

        self._driver = GraphDatabase.driver(self.uri)
        logger.info(f"Connected to Memgraph: {self.uri}")
        return self._driver

    @property
    def driver(self):
        """Get the database driver."""
        return self._get_driver()

    def close(self):
        """Close the driver."""
        if self._driver:
            self._driver.close()
            self._driver = None

    # =========================================================================
    # Schema Setup
    # =========================================================================

    def setup_schema(self):
        """Create indexes and constraints for protocol graph."""
        queries = [
            # Entity indexes
            "CREATE INDEX ON :Protocol(id)",
            "CREATE INDEX ON :Protocol(name)",
            "CREATE INDEX ON :Contract(address)",
            "CREATE INDEX ON :Token(symbol)",
            "CREATE INDEX ON :Chain(id)",
            "CREATE INDEX ON :Audit(id)",
            # Temporal indexes
            "CREATE INDEX ON :Protocol(valid_from)",
            "CREATE INDEX ON :Protocol(valid_to)",
            # Constraints
            "CREATE CONSTRAINT ON (p:Protocol) ASSERT p.id IS UNIQUE",
            "CREATE CONSTRAINT ON (c:Contract) ASSERT c.id IS UNIQUE",
        ]

        with self.driver.session() as session:
            for query in queries:
                try:
                    session.run(query)
                except Exception as e:
                    logger.debug(f"Schema query skipped: {e}")

        logger.info("Protocol graph schema initialized")

    # =========================================================================
    # Entity Operations
    # =========================================================================

    def add_entity(self, entity: ProtocolEntity) -> str:
        """Add a protocol entity to the graph."""
        query = f"""
        MERGE (e:{entity.entity_type.value} {{id: $id}})
        SET e.name = $name,
            e.description = $description,
            e.valid_from = $valid_from,
            e.valid_to = $valid_to,
            e.transaction_time = $transaction_time,
            e.chain = $chain,
            e.version = $version,
            e.tvl_usd = $tvl_usd,
            e.address = $address
        RETURN e.id
        """

        with self.driver.session() as session:
            result = session.run(
                query,
                id=entity.id,
                name=entity.name,
                description=entity.description,
                valid_from=entity.valid_from.isoformat() if entity.valid_from else None,
                valid_to=entity.valid_to.isoformat() if entity.valid_to else None,
                transaction_time=entity.transaction_time.isoformat(),
                chain=entity.chain,
                version=entity.version,
                tvl_usd=entity.tvl_usd,
                address=entity.address,
            )
            record = result.single()
            return record["e.id"] if record else entity.id

    def add_entities_batch(self, entities: list[ProtocolEntity]) -> int:
        """Add multiple entities in batch."""
        if not entities:
            return 0

        # Group by entity type
        by_type: dict[ProtocolEntityType, list[ProtocolEntity]] = {}
        for entity in entities:
            by_type.setdefault(entity.entity_type, []).append(entity)

        total = 0
        with self.driver.session() as session:
            for entity_type, type_entities in by_type.items():
                query = f"""
                UNWIND $entities AS e
                MERGE (n:{entity_type.value} {{id: e.id}})
                SET n.name = e.name,
                    n.description = e.description,
                    n.valid_from = e.valid_from,
                    n.valid_to = e.valid_to,
                    n.transaction_time = e.transaction_time,
                    n.chain = e.chain,
                    n.version = e.version
                """

                params = [
                    {
                        "id": e.id,
                        "name": e.name,
                        "description": e.description,
                        "valid_from": e.valid_from.isoformat() if e.valid_from else None,
                        "valid_to": e.valid_to.isoformat() if e.valid_to else None,
                        "transaction_time": e.transaction_time.isoformat(),
                        "chain": e.chain,
                        "version": e.version,
                    }
                    for e in type_entities
                ]

                session.run(query, entities=params)
                total += len(type_entities)

        logger.info(f"Added {total} entities")
        return total

    # =========================================================================
    # Relationship Operations
    # =========================================================================

    def add_relationship(self, rel: ProtocolRelationship) -> bool:
        """Add a relationship between entities."""
        query = f"""
        MATCH (source {{id: $source_id}})
        MATCH (target {{id: $target_id}})
        MERGE (source)-[r:{rel.relationship_type.value}]->(target)
        SET r.valid_from = $valid_from,
            r.valid_to = $valid_to,
            r.transaction_time = $transaction_time,
            r.confidence = $confidence,
            r.evidence = $evidence
        RETURN r
        """

        with self.driver.session() as session:
            result = session.run(
                query,
                source_id=rel.source_id,
                target_id=rel.target_id,
                valid_from=rel.valid_from.isoformat() if rel.valid_from else None,
                valid_to=rel.valid_to.isoformat() if rel.valid_to else None,
                transaction_time=rel.transaction_time.isoformat(),
                confidence=rel.confidence,
                evidence=rel.evidence,
            )
            return result.single() is not None

    def add_relationships_batch(self, rels: list[ProtocolRelationship]) -> int:
        """Add multiple relationships in batch."""
        if not rels:
            return 0

        # Group by relationship type
        by_type: dict[ProtocolRelationType, list[ProtocolRelationship]] = {}
        for rel in rels:
            by_type.setdefault(rel.relationship_type, []).append(rel)

        total = 0
        with self.driver.session() as session:
            for rel_type, type_rels in by_type.items():
                query = f"""
                UNWIND $rels AS r
                MATCH (source {{id: r.source_id}})
                MATCH (target {{id: r.target_id}})
                MERGE (source)-[rel:{rel_type.value}]->(target)
                SET rel.valid_from = r.valid_from,
                    rel.valid_to = r.valid_to,
                    rel.confidence = r.confidence
                """

                params = [
                    {
                        "source_id": r.source_id,
                        "target_id": r.target_id,
                        "valid_from": r.valid_from.isoformat() if r.valid_from else None,
                        "valid_to": r.valid_to.isoformat() if r.valid_to else None,
                        "confidence": r.confidence,
                    }
                    for r in type_rels
                ]

                session.run(query, rels=params)
                total += len(type_rels)

        logger.info(f"Added {total} relationships")
        return total

    # =========================================================================
    # Temporal Queries
    # =========================================================================

    def get_protocol_at_time(
        self,
        protocol_id: str,
        point_in_time: datetime,
    ) -> dict[str, Any] | None:
        """
        Get protocol state at a specific point in time.

        Uses valid_time for point-in-time queries.
        """
        query = """
        MATCH (p:Protocol {id: $id})
        WHERE (p.valid_from IS NULL OR p.valid_from <= $time)
          AND (p.valid_to IS NULL OR p.valid_to > $time)
        RETURN p
        """

        with self.driver.session() as session:
            result = session.run(
                query,
                id=protocol_id,
                time=point_in_time.isoformat(),
            )
            record = result.single()
            return dict(record["p"]) if record else None

    def get_dependencies_at_time(
        self,
        protocol_id: str,
        point_in_time: datetime,
    ) -> list[dict[str, Any]]:
        """
        Get protocol dependencies at a specific point in time.

        Returns all protocols that the given protocol depends on.
        """
        query = """
        MATCH (p:Protocol {id: $id})-[r:DEPENDS_ON|USES|INTEGRATES_WITH]->(dep)
        WHERE (r.valid_from IS NULL OR r.valid_from <= $time)
          AND (r.valid_to IS NULL OR r.valid_to > $time)
        RETURN dep.id as id, dep.name as name, type(r) as relationship,
               r.valid_from as valid_from, r.confidence as confidence
        """

        with self.driver.session() as session:
            result = session.run(
                query,
                id=protocol_id,
                time=point_in_time.isoformat(),
            )
            return [dict(record) for record in result]

    def get_integration_history(
        self,
        protocol_id: str,
    ) -> list[dict[str, Any]]:
        """
        Get full integration history for a protocol.

        Returns all integrations with temporal validity.
        """
        query = """
        MATCH (p:Protocol {id: $id})-[r:INTEGRATES_WITH]->(other)
        RETURN other.id as id, other.name as name,
               r.valid_from as started, r.valid_to as ended,
               r.transaction_time as recorded_at
        ORDER BY r.valid_from DESC
        """

        with self.driver.session() as session:
            result = session.run(query, id=protocol_id)
            return [dict(record) for record in result]

    def get_version_evolution(
        self,
        protocol_name: str,
    ) -> list[dict[str, Any]]:
        """
        Get version evolution of a protocol.

        Traces UPGRADES_TO relationships.
        """
        query = """
        MATCH path = (v1:Version)-[:UPGRADES_TO*]->(v2:Version)
        WHERE v1.protocol = $name OR v2.protocol = $name
        RETURN [n in nodes(path) | {
            version: n.version,
            valid_from: n.valid_from,
            changes: n.changes
        }] as versions
        ORDER BY length(path) DESC
        LIMIT 1
        """

        with self.driver.session() as session:
            result = session.run(query, name=protocol_name)
            record = result.single()
            return record["versions"] if record else []

    # =========================================================================
    # Risk Queries
    # =========================================================================

    def find_shared_dependencies(
        self,
        protocol_ids: list[str],
    ) -> list[dict[str, Any]]:
        """
        Find dependencies shared by multiple protocols.

        Useful for identifying systemic risk.
        """
        query = """
        UNWIND $protocols as pid
        MATCH (p:Protocol {id: pid})-[:DEPENDS_ON]->(dep)
        WITH dep, collect(p.id) as dependent_protocols
        WHERE size(dependent_protocols) > 1
        RETURN dep.id as dependency_id, dep.name as dependency_name,
               dependent_protocols, size(dependent_protocols) as num_dependents
        ORDER BY num_dependents DESC
        """

        with self.driver.session() as session:
            result = session.run(query, protocols=protocol_ids)
            return [dict(record) for record in result]

    def find_audit_overlap(
        self,
        protocol_id: str,
    ) -> list[dict[str, Any]]:
        """
        Find protocols audited by the same firms.

        Useful for understanding audit coverage.
        """
        query = """
        MATCH (p:Protocol {id: $id})-[:AUDITED_BY]->(a:Audit)
        MATCH (other:Protocol)-[:AUDITED_BY]->(a)
        WHERE other.id <> $id
        RETURN a.name as auditor, collect(DISTINCT other.id) as shared_protocols
        """

        with self.driver.session() as session:
            result = session.run(query, id=protocol_id)
            return [dict(record) for record in result]

    def find_vulnerability_exposure(
        self,
        vulnerability_type: str,
    ) -> list[dict[str, Any]]:
        """
        Find protocols potentially exposed to a vulnerability type.

        Searches SHARES_VULNERABILITY and SHARES_DEPENDENCY.
        """
        query = """
        MATCH (r:Risk {type: $vuln_type})<-[:SHARES_VULNERABILITY]-(p:Protocol)
        OPTIONAL MATCH (p)-[:DEPENDS_ON]->(dep)
        RETURN p.id as protocol, p.name as name,
               p.tvl_usd as tvl, collect(DISTINCT dep.id) as dependencies
        ORDER BY p.tvl_usd DESC
        """

        with self.driver.session() as session:
            result = session.run(query, vuln_type=vulnerability_type)
            return [dict(record) for record in result]

    # =========================================================================
    # Graph Statistics
    # =========================================================================

    def get_stats(self) -> dict[str, Any]:
        """Get graph statistics."""
        queries = {
            "protocols": "MATCH (n:Protocol) RETURN count(n) AS count",
            "contracts": "MATCH (n:Contract) RETURN count(n) AS count",
            "tokens": "MATCH (n:Token) RETURN count(n) AS count",
            "integrations": "MATCH ()-[r:INTEGRATES_WITH]->() RETURN count(r) AS count",
            "dependencies": "MATCH ()-[r:DEPENDS_ON]->() RETURN count(r) AS count",
            "audits": "MATCH ()-[r:AUDITED_BY]->() RETURN count(r) AS count",
        }

        stats = {}
        with self.driver.session() as session:
            for key, query in queries.items():
                result = session.run(query)
                record = result.single()
                stats[key] = record["count"] if record else 0

        return stats


# =============================================================================
# Pre-configured Protocol Data
# =============================================================================


def get_initial_protocol_entities() -> list[ProtocolEntity]:
    """Get initial protocol entities for bootstrapping."""
    return [
        ProtocolEntity(
            id="uniswap",
            entity_type=ProtocolEntityType.PROTOCOL,
            name="Uniswap",
            description="Decentralized exchange protocol",
            chain="ethereum",
            valid_from=datetime(2018, 11, 2),
        ),
        ProtocolEntity(
            id="aave",
            entity_type=ProtocolEntityType.PROTOCOL,
            name="Aave",
            description="Decentralized lending protocol",
            chain="ethereum",
            valid_from=datetime(2020, 1, 8),
        ),
        ProtocolEntity(
            id="chainlink",
            entity_type=ProtocolEntityType.PROTOCOL,
            name="Chainlink",
            description="Decentralized oracle network",
            chain="ethereum",
            valid_from=datetime(2019, 5, 30),
        ),
        ProtocolEntity(
            id="compound",
            entity_type=ProtocolEntityType.PROTOCOL,
            name="Compound",
            description="Algorithmic money market protocol",
            chain="ethereum",
            valid_from=datetime(2018, 9, 27),
        ),
        ProtocolEntity(
            id="makerdao",
            entity_type=ProtocolEntityType.PROTOCOL,
            name="MakerDAO",
            description="Decentralized stablecoin protocol",
            chain="ethereum",
            valid_from=datetime(2017, 12, 18),
        ),
        ProtocolEntity(
            id="curve",
            entity_type=ProtocolEntityType.PROTOCOL,
            name="Curve Finance",
            description="Stablecoin exchange protocol",
            chain="ethereum",
            valid_from=datetime(2020, 1, 21),
        ),
    ]


def get_initial_relationships() -> list[ProtocolRelationship]:
    """Get initial protocol relationships."""
    return [
        # Aave uses Chainlink oracles
        ProtocolRelationship(
            source_id="aave",
            target_id="chainlink",
            relationship_type=ProtocolRelationType.USES,
            valid_from=datetime(2020, 1, 8),
            evidence="Aave uses Chainlink price feeds for collateral valuation",
        ),
        # Compound uses Chainlink
        ProtocolRelationship(
            source_id="compound",
            target_id="chainlink",
            relationship_type=ProtocolRelationType.USES,
            valid_from=datetime(2020, 8, 27),
            evidence="Compound V2 integrates Chainlink price feeds",
        ),
        # MakerDAO provides oracle data
        ProtocolRelationship(
            source_id="makerdao",
            target_id="chainlink",
            relationship_type=ProtocolRelationType.INTEGRATES_WITH,
            valid_from=datetime(2021, 4, 1),
        ),
        # Curve integrates with Aave
        ProtocolRelationship(
            source_id="curve",
            target_id="aave",
            relationship_type=ProtocolRelationType.INTEGRATES_WITH,
            valid_from=datetime(2021, 1, 15),
        ),
    ]


async def initialize_protocol_graph(uri: str | None = None) -> dict[str, int]:
    """
    Initialize protocol graph with base entities and relationships.

    Args:
        uri: Memgraph connection URI

    Returns:
        Statistics about initialized data
    """
    client = ProtocolGraphClient(uri)

    try:
        client.setup_schema()

        entities = get_initial_protocol_entities()
        entity_count = client.add_entities_batch(entities)

        relationships = get_initial_relationships()
        rel_count = client.add_relationships_batch(relationships)

        return {
            "entities": entity_count,
            "relationships": rel_count,
        }
    finally:
        client.close()


# Singleton client
_protocol_graph: ProtocolGraphClient | None = None


def get_protocol_graph(uri: str | None = None) -> ProtocolGraphClient:
    """Get protocol graph client singleton."""
    global _protocol_graph
    if _protocol_graph is None:
        _protocol_graph = ProtocolGraphClient(uri)
    return _protocol_graph


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description="Protocol knowledge graph")
    parser.add_argument("--init", action="store_true", help="Initialize graph")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--memgraph", default=DEFAULT_MEMGRAPH_URI)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.init:
        result = asyncio.run(initialize_protocol_graph(args.memgraph))
        print(f"Initialized: {result}")
    elif args.stats:
        client = ProtocolGraphClient(args.memgraph)
        stats = client.get_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
        client.close()
