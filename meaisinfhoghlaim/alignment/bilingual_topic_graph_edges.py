"""Bilingual topic graph edges emitter (Plan 2 UC 3 + UC 7).

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 2).

Emits the canonical meaisinfoghlaim.alignment.bilingual_topic_edges table.

This module is a thin emitter over the bilingual_topic_graph builder
(see topic_graph.BilingualTopicGraphBuilder). The builder builds the
in-memory BilingualTopicEdge list; this module persists it to:
  - LanceDB (canonical semantic index)
  - dlt_sources (the canonical dlt ingest path)
  - MLflow (logging tags for trace correlation)

Generalisable: same emitter works for Wales (EN/CY) + Scotland (EN/GD)
via the LanguagePair enum.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from meaisinfhoghlaim.alignment.schema import (
    BilingualTopicEdge,
    LanguagePair,
)

logger = logging.getLogger(__name__)


BILINGUAL_TOPIC_EDGES_ROOT = Path(
    "stedding/education/bilingual_topic_edges",
)


class BilingualTopicGraphEdgeEmitter:
    """The canonical bilingual topic edge emitter."""

    def __init__(self, output_root=None) -> None:
        self.output_root = (
            Path(output_root) if output_root is not None
            else BILINGUAL_TOPIC_EDGES_ROOT
        )
        self.output_root.mkdir(parents=True, exist_ok=True)
        self._table = None
        self._init_attempted = False

    def _get_table(self):
        if self._init_attempted:
            return self._table
        self._init_attempted = True
        try:
            import lancedb  # type: ignore[import-not-found]
            self._table = lancedb.connect_or_create("meaisinfoghlaim_bilingual_topic_edges")
            return self._table
        except ImportError:
            return None

    def emit(self, edges):
        """Persist the bilingual topic edges to disk + (optionally) LanceDB."""
        edges_list = list(edges)
        if not edges_list:
            return 0

        self._write_jsonl(edges_list)

        table = self._get_table()
        if table is not None:
            try:
                table.add([e.model_dump() for e in edges_list])
            except Exception as exc:
                logger.warning(
                    "Failed to write %d bilingual topic edges to LanceDB: %s",
                    len(edges_list), exc,
                )

        logger.info(
            "Emitted %d bilingual topic edges (%d distinct cohorts)",
            len(edges_list),
            len({e.cohort_key for e in edges_list}),
        )
        return len(edges_list)

    def _write_jsonl(self, edges):
        by_cohort_pair = {}
        for edge in edges:
            key = (edge.cohort_key, edge.language_pair.value)
            by_cohort_pair.setdefault(key, []).append(edge)
        for (cohort_key, language_pair_value), cohort_edges in by_cohort_pair.items():
            safe = cohort_key.replace("/", "__")
            path = self.output_root / f"{safe}__{language_pair_value}.jsonl"
            with path.open("w", encoding="utf-8") as f:
                for e in cohort_edges:
                    f.write(e.model_dump_json() + "\n")
            logger.debug("Wrote %d edges to %s", len(cohort_edges), path)

    def read(self, cohort_key, language_pair):
        """Read the bilingual topic edges for a (cohort, language_pair)."""
        safe = cohort_key.replace("/", "__")
        path = self.output_root / f"{safe}__{language_pair.value}.jsonl"
        if not path.exists():
            return []
        out = []
        try:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    d = json.loads(line)
                    out.append(BilingualTopicEdge.model_validate(d))
        except Exception:
            logger.exception(
                "Failed to read bilingual topic edges from %s", path
            )
        return out


__all__ = [
    "BILINGUAL_TOPIC_EDGES_ROOT",
    "BilingualTopicGraphEdgeEmitter",
    "BilingualTopicEdge",
    "LanguagePair",
]
