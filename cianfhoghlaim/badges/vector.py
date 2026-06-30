"""badges.vector — LanceDB writer for SkillTreeBadge embeddings.

Each badge is embedded with BGE-M3 (1024-dim) over the concatenated
text: `competency_text_en + competency_text_ga + subject + competency_code`.

Stored in the LanceDB table `oideachais.badges.embeddings`.

Used by the public `/student/<id>/badges` page and the
`semantic_search_badges` helper.
"""
from __future__ import annotations

import os
from typing import Any

from .schema import SkillTreeBadge


async def index_badge_embedding(badge: SkillTreeBadge) -> None:
    """Embed the badge and upsert it into LanceDB."""
    try:
        import lancedb
        import pyarrow as pa
    except ImportError:
        return

    # 1. Build the text to embed
    text = " ".join(
        filter(
            None,
            [
                badge.competency_text.text_en,
                badge.competency_text.text_ga or "",
                badge.subject,
                badge.competency_code,
            ],
        )
    )

    # 2. Compute the embedding (BGE-M3 1024-dim)
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("BAAI/bge-m3", cache_folder=os.environ.get("HF_HOME"))
        vector = model.encode(text).tolist()
    except ImportError:
        return

    # 3. Upsert into LanceDB
    db = lancedb.connect(os.environ.get("CIANFHOGHLAIM_LANCEDB_URI", "./data/lancedb"))
    table_name = "oideachais.badges.embeddings"
    if table_name in db.table_names():
        table = db.open_table(table_name)
        table.delete(f"id = '{badge.id}'")
        table.add(
            pa.table(
                {
                    "id": [badge.id],
                    "vector": [vector],
                    "text": [text],
                    "subject": [badge.subject],
                    "competency_code": [badge.competency_code],
                    "level": [badge.level],
                    "framework": [badge.framework],
                    "date_earned": [badge.date_earned.isoformat()],
                }
            )
        )
    else:
        db.create_table(
            table_name,
            pa.table(
                {
                    "id": [badge.id],
                    "vector": [vector],
                    "text": [text],
                    "subject": [badge.subject],
                    "competency_code": [badge.competency_code],
                    "level": [badge.level],
                    "framework": [badge.framework],
                    "date_earned": [badge.date_earned.isoformat()],
                }
            ),
        )


async def semantic_search_badges(
    query: str,
    top_k: int = 5,
    subject: str | None = None,
) -> list[dict[str, Any]]:
    """Semantic search over the badge corpus.

    Args:
        query: Free-text query (BGE-M3 embeddings).
        top_k: Number of results to return.
        subject: Optional subject filter (e.g. "mathematics").
    """
    try:
        import lancedb
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return []

    db = lancedb.connect(os.environ.get("CIANFHOGHLAIM_LANCEDB_URI", "./data/lancedb"))
    table_name = "oideachais.badges.embeddings"
    if table_name not in db.table_names():
        return []
    table = db.open_table(table_name)

    model = SentenceTransformer("BAAI/bge-m3", cache_folder=os.environ.get("HF_HOME"))
    query_vec = model.encode(query).tolist()

    filter_str = f"subject = '{subject}'" if subject else None
    results = table.search(query_vec).limit(top_k).where(filter_str).to_list()
    return results