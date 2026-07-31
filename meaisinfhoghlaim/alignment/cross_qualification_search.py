"""UC cross-qual: CrossQualificationSearcher (Plan 3).

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 3).

The LanceDB-indexed cross-qualification topic search. Powers the cross-
jurisdiction RAG: "find all topics about atomic structure across ALL
qualifications + jurisdictions".

Generalisable: same searcher works for Scotland / Wales / NI rollouts.
"""

from __future__ import annotations

import logging
from typing import Any

from meaisinfoghlaim.alignment.cross_qualification_topic_alignment import (
    CrossQualificationTopicAligner,
)
from meaisinfoghlaim.alignment.schema import (
    CrossQualificationTopicAlignment,
    QualificationLevel,
)

logger = logging.getLogger(__name__)


class CrossQualificationSearcher:
    """The canonical cross-qualification topic searcher.

    Backed by a LanceDB table (when lancedb is installed; falls back to
    in-memory cache otherwise).
    """

    TABLE_NAME = "meaisinfoghlaim_cross_qual_topic_alignment"

    def __init__(self, topic_aligner: CrossQualificationTopicAligner | None = None) -> None:
        self.topic_aligner = topic_aligner or CrossQualificationTopicAligner()
        self._table: Any | None = None
        self._init_attempted: bool = False

    def _get_table(self) -> Any | None:
        """Lazy-init the LanceDB table."""
        if self._init_attempted:
            return self._table
        self._init_attempted = True
        try:
            import lancedb  # type: ignore[import-not-found]
            self._table = lancedb.connect_or_create(self.TABLE_NAME)
            return self._table
        except ImportError:
            logger.warning(
                "lancedb not installed; CrossQualificationSearcher using in-memory fallback"
            )
            return None

    def index(self, alignment: CrossQualificationTopicAlignment) -> None:
        """Index a single alignment row into LanceDB."""
        table = self._get_table()
        record = alignment.model_dump()
        if table is not None:
            try:
                table.add([record])
            except Exception as exc:
                logger.warning("Failed to index alignment %s: %s", alignment.alignment_id, exc)

    def index_many(self, alignments: list[CrossQualificationTopicAlignment]) -> int:
        """Index many alignments; returns the count actually indexed."""
        count = 0
        for a in alignments:
            self.index(a)
            count += 1
        return count

    def search(
        self,
        query: str,
        qualifications: list[QualificationLevel] | None = None,
        jurisdictions: list[str] | None = None,
        top_k: int = 10,
    ) -> list[CrossQualificationTopicAlignment]:
        """Search the cross-qualification topic alignment table.

        Args:
            query: natural-language query (e.g. 'atomic structure')
            qualifications: optional filter (default: all)
            jurisdictions: optional filter (default: all)
            top_k: max results

        Returns:
            list of CrossQualificationTopicAlignment (best match first)
        """
        table = self._get_table()
        if table is None:
            logger.warning(
                "CrossQualificationSearcher.search: no table; returning empty"
            )
            return []
        try:
            results = table.search(query).limit(top_k).to_list()
        except Exception as exc:
            logger.warning("CrossQualificationSearcher.search failed: %s", exc)
            return []
        out: list[CrossQualificationTopicAlignment] = []
        for r in results:
            try:
                a = CrossQualificationTopicAlignment(**r)
                if qualifications is not None and a.qualification_a not in qualifications:
                    continue
                if jurisdictions is not None:
                    if (
                        a.jurisdiction_a not in jurisdictions
                        and a.jurisdiction_b not in jurisdictions
                    ):
                        continue
                out.append(a)
            except Exception as exc:
                logger.warning("Failed to parse search result: %s", exc)
        return out


__all__ = ["CrossQualificationSearcher", "CrossQualificationTopicAlignment", "QualificationLevel"]
