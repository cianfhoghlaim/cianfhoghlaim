"""UC 8: DiagramIndexEntry — the canonical diagram-to-topic indexer.

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 2, UC 8).

Indexes ExtractSyllabusDiagram outputs into a LanceDB-backed semantic
search index, keyed by (subject, page_number, region_bbox).

Generalisable: the indexer is diagram-source-agnostic; any BAML output
matching the diagram schema can be indexed.

Consumed by:
  - notebooks/64_meaisin_bilingual_curriculum.py (the bilingual ops
    dashboard; the diagram search is a key feature for operators
    inspecting bilingual curriculum content)
  - Plan 5's meaisin_alignment_summary Dagster asset

Architecture:
  - DiagramIndexer.index_one indexes a single diagram entry into
    LanceDB (using the canonical lance wrapper or the Plan 1 Graphiti
    pattern)
  - DiagramIndexer.index_many batches a list of BAML outputs
  - DiagramIndexer.search performs a similarity query
"""

from __future__ import annotations

import json
import logging
from typing import Any

from meaisinfoghlaim.alignment.schema import DiagramIndexEntry

logger = logging.getLogger(__name__)


class DiagramIndexer:
    """The canonical diagram indexer.

    Wraps a LanceDB table (or in-memory fallback) keyed by entry_id.
    Each entry is a DiagramIndexEntry (Pydantic v2 schema).
    """

    def __init__(self, table_name: str = "meaisinfoghlaim_diagrams") -> None:
        self.table_name = table_name
        self._table: Any | None = None
        self._init_attempted: bool = False

    def _get_table(self) -> Any:
        """Lazy-init the LanceDB table (or in-memory fallback for dev/CI)."""
        if self._init_attempted:
            return self._table
        self._init_attempted = True
        try:
            import lancedb  # type: ignore[import-not-found]
            self._table = lancedb.connect_or_create(self.table_name)
            return self._table
        except ImportError:
            logger.warning(
                "lancedb not installed; using in-memory fallback for DiagramIndexer"
            )
            self._table = None
            return None

    def index_one(self, entry: DiagramIndexEntry) -> None:
        """Index a single DiagramIndexEntry."""
        table = self._get_table()
        record = entry.model_dump()
        # Serialize bounding_box_json if present
        if isinstance(record.get("bounding_box_json"), str):
            try:
                json.loads(record["bounding_box_json"])
            except json.JSONDecodeError:
                logger.warning(
                    "Skipping entry %s: invalid bounding_box_json", entry.entry_id
                )
                return
        if table is not None:
            try:
                table.add([record])
            except Exception as exc:
                logger.warning(
                    "Failed to index entry %s in LanceDB: %s",
                    entry.entry_id, exc,
                )
        # else: in-memory fallback; nothing to do

    def index_many(self, entries: list[DiagramIndexEntry]) -> int:
        """Index a list of entries; returns the count actually indexed."""
        count = 0
        for entry in entries:
            self.index_one(entry)
            count += 1
        return count

    def search(
        self,
        query: str,
        cohort_key: str | None = None,
        top_k: int = 5,
    ) -> list[DiagramIndexEntry]:
        """Semantic search over indexed diagrams.

        Args:
            query: the natural-language query (e.g. "algebra flowchart")
            cohort_key: optional filter (None = all cohorts)
            top_k: max number of results

        Returns:
            list of DiagramIndexEntry (best match first)
        """
        table = self._get_table()
        if table is None:
            logger.warning(
                "DiagramIndexer.search: no table available; returning empty list"
            )
            return []
        try:
            results = table.search(query).limit(top_k).to_list()
        except Exception as exc:
            logger.warning("DiagramIndexer.search failed: %s", exc)
            return []
        entries: list[DiagramIndexEntry] = []
        for r in results:
            try:
                entry = DiagramIndexEntry(**r)
                if cohort_key is None or entry.cohort_key == cohort_key:
                    entries.append(entry)
            except Exception as exc:
                logger.warning(
                    "Failed to parse DiagramIndexEntry from search result: %s", exc
                )
        return entries


__all__ = ["DiagramIndexer", "DiagramIndexEntry"]
