"""badges.graph — FalkorDB writer for cross-realm mastery edges.

Each SkillTreeBadge becomes a node in the FalkorDB knowledge graph
with edges to:
- The player's profile node (`(:Player {student_id: ...})`)
- The LO node (`(:NCCALearningOutcome {lo_code: ...})`)
- The agent node (`(:Agent {name: ...})`)

This enables:
- `fetch_student_mastery(student_id)` — cross-8-subject mastery rollup
- Cross-subject synthesis queries (e.g. "show all LO nodes a student
  has mastered across all 8 subjects at HL level")
"""
from __future__ import annotations

from typing import Any

from .schema import SkillTreeBadge


async def upsert_badge_node(badge: SkillTreeBadge) -> None:
    """Insert or update the FalkorDB nodes + edges for one badge."""
    try:
        import falkordb
    except ImportError:
        return

    client = falkordb.FalkorDB(
        host=__import__("os").environ.get("FALKORDB_HOST", "localhost"),
        port=int(__import__("os").environ.get("FALKORDB_PORT", "6379")),
    )
    graph = client.select_graph("cianfhoghlaim_badges")
    query = """
    MERGE (p:Player {student_id: $student_id})
    MERGE (lo:NCCALearningOutcome {lo_code: $lo_code})
    MERGE (a:Agent {name: $agent_issuer})
    CREATE (b:SkillTreeBadge {
        id: $id,
        framework: $framework,
        level: $level,
        subject: $subject,
        competency_code: $competency_code,
        date_earned: $date_earned,
        evidence_hash: $evidence_hash
    })
    MERGE (p)-[:EARNED]->(b)
    MERGE (b)-[:DEMONSTRATES]->(lo)
    MERGE (a)-[:ISSUED]->(b)
    RETURN b.id
    """
    graph.query(
        query,
        params={
            "id": badge.id,
            "student_id": badge.student_id,
            "lo_code": badge.competency_code,
            "agent_issuer": badge.agent_issuer,
            "framework": badge.framework,
            "level": badge.level,
            "subject": badge.subject,
            "competency_code": badge.competency_code,
            "date_earned": badge.date_earned.isoformat(),
            "evidence_hash": badge.evidence_hash,
        },
    )


async def fetch_student_mastery(student_id: str) -> dict[str, Any]:
    """Return a per-subject mastery rollup across the 8 NCCA subjects.

    Shape:
        {
            "mathematics": {"hl": 12, "ol": 8, "fl": 0},
            "gaeilge":     {"hl": 5, "ol": 7, "fl": 3},
            ...
        }
    """
    try:
        import falkordb
    except ImportError:
        return {}

    client = falkordb.FalkorDB(
        host=__import__("os").environ.get("FALKORDB_HOST", "localhost"),
        port=int(__import__("os").environ.get("FALKORDB_PORT", "6379")),
    )
    graph = client.select_graph("cianfhoghlaim_badges")
    rows = graph.query(
        """
        MATCH (p:Player {student_id: $student_id})-[:EARNED]->(b:SkillTreeBadge)
        RETURN b.subject AS subject, b.level AS level, count(b) AS badges
        ORDER BY subject, level
        """,
        params={"student_id": student_id},
    )
    out: dict[str, dict[str, int]] = {}
    for row in rows:
        out.setdefault(row[0], {})[row[1]] = int(row[2])
    return out