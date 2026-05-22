"""
Temporal Knowledge Graph using Graphiti for Crypteolas.

Tracks protocol evolution over time:
- TVL changes and trends
- Protocol updates and migrations
- Team changes
- Security incidents
- Governance proposals

Uses FalkorDB as the graph database backend.
"""

import os
from datetime import datetime, timezone
from typing import Any

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType


def get_graphiti_client() -> Graphiti:
    """Get configured Graphiti client."""
    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "password")

    return Graphiti(
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
    )


# Entity types for crypto domain
CRYPTO_ENTITY_TYPES = [
    "Protocol",
    "Token",
    "Chain",
    "Team",
    "Developer",
    "Investor",
    "Auditor",
    "Governance",
    "Proposal",
    "Vulnerability",
    "Integration",
]

# Relation types
CRYPTO_RELATION_TYPES = [
    "DEPLOYED_ON",  # Protocol -> Chain
    "HAS_TOKEN",  # Protocol -> Token
    "FOUNDED_BY",  # Protocol -> Team/Developer
    "INVESTED_IN",  # Investor -> Protocol
    "AUDITED_BY",  # Protocol -> Auditor
    "INTEGRATED_WITH",  # Protocol -> Protocol
    "FORKED_FROM",  # Protocol -> Protocol
    "EXPLOITED",  # Vulnerability -> Protocol
    "PROPOSED",  # Governance -> Proposal
    "MIGRATED_TO",  # Protocol -> Protocol (v1 -> v2)
]


async def add_protocol_episode(
    client: Graphiti,
    protocol_name: str,
    event_type: str,
    description: str,
    metadata: dict[str, Any] | None = None,
    source_url: str | None = None,
) -> str:
    """
    Add a temporal episode for a protocol.

    Episodes track changes over time:
    - TVL milestones
    - Version upgrades
    - Security incidents
    - Team announcements
    - Governance votes
    """
    timestamp = datetime.now(timezone.utc)

    episode_content = f"""
    Protocol: {protocol_name}
    Event: {event_type}
    Description: {description}
    Timestamp: {timestamp.isoformat()}
    """

    if metadata:
        episode_content += f"\nMetadata: {metadata}"

    episode = await client.add_episode(
        name=f"{protocol_name}_{event_type}_{timestamp.strftime('%Y%m%d')}",
        episode_body=episode_content,
        source_description=source_url or "Crypteolas Data Pipeline",
        reference_time=timestamp,
        episode_type=EpisodeType.json,  # Use JSON for structured data
    )

    return episode.uuid


async def add_tvl_milestone(
    client: Graphiti,
    protocol_name: str,
    tvl_value: float,
    chain: str | None = None,
    previous_tvl: float | None = None,
) -> str:
    """Record a TVL milestone for a protocol."""
    change_pct = None
    if previous_tvl and previous_tvl > 0:
        change_pct = ((tvl_value - previous_tvl) / previous_tvl) * 100

    metadata = {
        "tvl_usd": tvl_value,
        "chain": chain,
        "previous_tvl": previous_tvl,
        "change_percent": change_pct,
    }

    if tvl_value >= 1_000_000_000:
        event_type = "TVL_BILLION"
    elif tvl_value >= 100_000_000:
        event_type = "TVL_100M"
    elif tvl_value >= 10_000_000:
        event_type = "TVL_10M"
    else:
        event_type = "TVL_UPDATE"

    description = f"TVL reached ${tvl_value:,.2f}"
    if change_pct:
        description += f" ({change_pct:+.1f}% change)"

    return await add_protocol_episode(
        client,
        protocol_name,
        event_type,
        description,
        metadata,
    )


async def add_security_incident(
    client: Graphiti,
    protocol_name: str,
    incident_type: str,  # exploit, hack, rug_pull, vulnerability
    description: str,
    loss_usd: float | None = None,
    source_url: str | None = None,
) -> str:
    """Record a security incident for a protocol."""
    metadata = {
        "incident_type": incident_type,
        "loss_usd": loss_usd,
    }

    return await add_protocol_episode(
        client,
        protocol_name,
        f"SECURITY_{incident_type.upper()}",
        description,
        metadata,
        source_url,
    )


async def add_protocol_upgrade(
    client: Graphiti,
    protocol_name: str,
    from_version: str,
    to_version: str,
    description: str,
    breaking_changes: bool = False,
) -> str:
    """Record a protocol version upgrade."""
    metadata = {
        "from_version": from_version,
        "to_version": to_version,
        "breaking_changes": breaking_changes,
    }

    return await add_protocol_episode(
        client,
        protocol_name,
        "VERSION_UPGRADE",
        description,
        metadata,
    )


async def add_governance_proposal(
    client: Graphiti,
    protocol_name: str,
    proposal_id: str,
    title: str,
    status: str,  # pending, passed, rejected, executed
    votes_for: float | None = None,
    votes_against: float | None = None,
) -> str:
    """Record a governance proposal."""
    metadata = {
        "proposal_id": proposal_id,
        "status": status,
        "votes_for": votes_for,
        "votes_against": votes_against,
    }

    return await add_protocol_episode(
        client,
        protocol_name,
        f"GOVERNANCE_{status.upper()}",
        f"Proposal: {title}",
        metadata,
    )


async def query_protocol_timeline(
    client: Graphiti,
    protocol_name: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    event_types: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Query the temporal history of a protocol.

    Returns chronological list of events/episodes.
    """
    # Build Cypher query
    query = """
    MATCH (e:Episode)-[:MENTIONS]->(p:Entity {name: $protocol_name})
    WHERE e.valid_at IS NOT NULL
    """

    params: dict[str, Any] = {"protocol_name": protocol_name}

    if start_date:
        query += " AND e.valid_at >= $start_date"
        params["start_date"] = start_date.isoformat()

    if end_date:
        query += " AND e.valid_at <= $end_date"
        params["end_date"] = end_date.isoformat()

    query += """
    RETURN e.name as event_name,
           e.content as content,
           e.valid_at as timestamp,
           e.source_description as source
    ORDER BY e.valid_at DESC
    """

    # Execute query through Graphiti
    results = await client.search(
        query=f"timeline for {protocol_name}",
        num_results=100,
    )

    return [
        {
            "event": r.fact,
            "timestamp": r.valid_at,
            "source": r.episode_uuid,
        }
        for r in results
    ]


async def find_related_protocols(
    client: Graphiti,
    protocol_name: str,
    relation_type: str | None = None,
) -> list[dict[str, Any]]:
    """
    Find protocols related to the given protocol.

    Relations include: forks, integrations, shared teams, etc.
    """
    results = await client.search(
        query=f"protocols related to {protocol_name}",
        num_results=20,
    )

    return [
        {
            "protocol": r.fact,
            "relation": relation_type,
            "confidence": r.score if hasattr(r, "score") else None,
        }
        for r in results
    ]


async def get_protocol_facts(
    client: Graphiti,
    protocol_name: str,
) -> list[dict[str, Any]]:
    """
    Get all known facts about a protocol.

    Returns accumulated knowledge from all episodes.
    """
    results = await client.search(
        query=f"all facts about {protocol_name}",
        num_results=50,
    )

    return [
        {
            "fact": r.fact,
            "valid_from": r.valid_at,
            "invalid_from": r.invalid_at if hasattr(r, "invalid_at") else None,
            "source": r.episode_uuid,
        }
        for r in results
    ]
