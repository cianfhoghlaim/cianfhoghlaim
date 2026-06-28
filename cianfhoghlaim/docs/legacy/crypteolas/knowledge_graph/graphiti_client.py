"""
Compatibility shim for the legacy `crypteolas.knowledge_graph.graphiti_client` import.

The real implementation lives at `graphiti.temporal_graph`. This module
re-exports the relevant functions so that test files and any other
caller that still uses the old `graphiti_client` import path can find them.

When updating the test suite, prefer importing from
`tuatha.crypteolas.knowledge_graph.graphiti.temporal_graph` directly.
"""

from __future__ import annotations

from sruth.tuatha.crypteolas.knowledge_graph.graphiti.temporal_graph import (
    add_governance_proposal,
    add_protocol_episode,
    add_protocol_upgrade,
    add_security_incident,
    add_tvl_milestone,
    find_related_protocols,
    get_graphiti_client,
    get_protocol_facts,
    query_protocol_timeline,
)

# Aliases for the legacy test API.
add_episode = add_protocol_episode
temporal_search = query_protocol_timeline
get_entity_history = get_protocol_facts


async def create_temporal_entity(*args, **kwargs):
    """Legacy alias: route to ``add_protocol_episode``."""
    return await add_protocol_episode(*args, **kwargs)


__all__ = [
    "get_graphiti_client",
    "add_episode",
    "add_governance_proposal",
    "add_protocol_episode",
    "add_protocol_upgrade",
    "add_security_incident",
    "add_tvl_milestone",
    "create_temporal_entity",
    "find_related_protocols",
    "get_entity_history",
    "get_protocol_facts",
    "query_protocol_timeline",
    "temporal_search",
]
