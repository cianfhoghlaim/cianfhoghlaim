"""a2ui_generator — the canonical ADK-side A2UI card payload generator.

Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change
(TASK-M3B-3.1 through 3.5: A2UI generator for the ADK fleet).

This module is the **Python mirror** of the canonical TypeScript
generator at
``web/apps/cianfhoghlaim/components/_shared/A2UISurfaceGenerator.tsx``.
It produces AG-UI card payloads that any of the 12 ADK agents can
return to the front-end, where the consumer at
``web/hono-api/src/routes/copilotkit/registry.ts`` (the AG-UI
event collector) ships them via the AG-UI protocol handshake.

The 8 surfaces supported (each backed by its own generator + a
Pydantic model) match the canonical 8 from the TypeScript side:

  | Surface    | Source agent              | Use case                              |
  |:-----------|:--------------------------|:--------------------------------------|
  | chart      | statistics_agent          | Real-time BIEP stats                  |
  | graph      | corpus_agent              | Knowledge graph view                  |
  | playback   | research_agent            | Time-based playback                    |
  | lineage    | curriculum_agent          | Per-page PDF.js lineage               |
  | search     | mcp_curriculum_agent      | Curriculum search                     |
  | subject_grid | root_agent              | 8 NCCA JC subjects                    |
  | dashboard  | curriculum_comparison_agent | Cross-jurisdiction comparison       |
  | translator | translation_agent         | EN ↔ GA translation                   |

Each generator returns an AG-UI ``updateComponents`` event payload
that the front-end renders via the canonical A2UI surface
generator. The payload format is the AG-UI 0.29.0 protocol spec.

Usage:

    from agents.adk.a2ui_generator import (
        A2UIGenerator,
        chart_card,
        graph_card,
        playback_card,
        lineage_card,
        search_card,
        subject_grid_card,
        dashboard_card,
        translator_card,
    )

    payload = chart_card(
        title="Leaving Cert enrolments 2018-2024",
        x_label="Year",
        y_label="Enrolments",
        series=[{"name": "Mathematics", "x": ["2018", ...], "y": [12345, ...]}],
    )

The generator is also exposed as a callable ADK tool
(``emit_a2ui_card``) so any ADK agent can return an A2UI card in
its response by calling the tool.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal, TypedDict


# ============================================================================
# AG-UI protocol payload models (typed dicts)
# ============================================================================


class ChartSeries(TypedDict):
    name: str
    x: list[str | int]
    y: list[float]


class LineageRow(TypedDict):
    row_id: str
    page_number: int
    extraction_function: str
    extraction_client: str
    extracted_at: str
    confidence: float


class SearchResultRow(TypedDict):
    title: str
    subject_slug: str
    stage_slug: str
    score: float


class SubjectCard(TypedDict):
    slug: str
    display_name: str
    icon: str
    ncca_lo_prefix: str


class DashboardCell(TypedDict):
    nation: str
    subject: str
    lo_a: str
    lo_b: str
    similarity: float


class GraphNode(TypedDict):
    id: str
    label: str
    cluster: str


class GraphEdge(TypedDict):
    source: str
    target: str
    weight: float


class PlaybackChapter(TypedDict):
    title: str
    start_seconds: float


# ============================================================================
# The canonical 8 surface dataclasses (mirrors of TS A2UIDataMap)
# ============================================================================


@dataclass(frozen=True)
class ChartSurfacePayload:
    """The chart surface data payload."""

    type: Literal["line", "bar", "pie"]
    title: str
    x_label: str
    y_label: str
    series: list[ChartSeries]


@dataclass(frozen=True)
class GraphSurfacePayload:
    """The graph surface data payload."""

    nodes: list[GraphNode]
    edges: list[GraphEdge]


@dataclass(frozen=True)
class PlaybackSurfacePayload:
    """The playback surface data payload."""

    video_url: str
    thumbnail_url: str
    duration_seconds: float
    chapters: list[PlaybackChapter]


@dataclass(frozen=True)
class LineageSurfacePayload:
    """The lineage surface data payload."""

    source_pdf: str
    rows: list[LineageRow]


@dataclass(frozen=True)
class SearchSurfacePayload:
    """The search surface data payload."""

    query: str
    results: list[SearchResultRow]


@dataclass(frozen=True)
class SubjectGridSurfacePayload:
    """The subject_grid surface data payload."""

    subjects: list[SubjectCard]


@dataclass(frozen=True)
class DashboardSurfacePayload:
    """The dashboard surface data payload."""

    nations: list[str]
    subjects: list[str]
    cells: list[DashboardCell]


@dataclass(frozen=True)
class TranslatorSurfacePayload:
    """The translator surface data payload."""

    source_text: str
    source_language: Literal["en", "ga"]
    translated_text: str
    target_language: Literal["en", "ga"]
    confidence: float


A2UISurfacePayload = (
    ChartSurfacePayload
    | GraphSurfacePayload
    | PlaybackSurfacePayload
    | LineageSurfacePayload
    | SearchSurfacePayload
    | SubjectGridSurfacePayload
    | DashboardSurfacePayload
    | TranslatorSurfacePayload
)


# ============================================================================
# The AG-UI card payload (the wire format)
# ============================================================================


@dataclass(frozen=True)
class A2UICard:
    """A single AG-UI A2UI card payload.

    Mirrors the AG-UI 0.29.0 ``updateComponents`` event schema.
    The ``surface_id`` is what the front-end keys on to dispatch
    to the right ``A2UISurfaceKind`` renderer.
    """

    surface: Literal[
        "chart", "graph", "playback", "lineage",
        "search", "subject_grid", "dashboard", "translator",
    ]
    data: A2UISurfacePayload
    surface_id: str = field(default_factory=lambda: f"a2ui-{uuid.uuid4().hex[:12]}")
    emitted_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    agent_source: str | None = None

    def to_agui_event(self) -> dict[str, Any]:
        """Serialize to the AG-UI ``updateComponents`` event payload.

        The shape follows the AG-UI 0.29.0 protocol:
        https://docs.ag-ui.com/concepts/agentic-ui-rendering
        """
        return {
            "type": "updateComponents",
            "surface_id": self.surface_id,
            "surface": self.surface,
            "data": asdict(self.data),
            "emitted_at": self.emitted_at,
            "agent_source": self.agent_source,
        }

    def to_json(self) -> str:
        """Serialize to a JSON string for AG-UI SSE delivery."""
        return json.dumps(self.to_agui_event(), ensure_ascii=False)


# ============================================================================
# The 8 surface factories (one per surface kind)
# ============================================================================


def chart_card(
    *,
    title: str,
    x_label: str,
    y_label: str,
    series: list[ChartSeries],
    chart_type: Literal["line", "bar", "pie"] = "line",
    agent_source: str | None = None,
) -> A2UICard:
    """Build a chart A2UI card payload.

    Returns:
        A2UICard with surface="chart" and a ChartSurfacePayload.
    """
    return A2UICard(
        surface="chart",
        data=ChartSurfacePayload(
            type=chart_type,
            title=title,
            x_label=x_label,
            y_label=y_label,
            series=list(series),
        ),
        agent_source=agent_source,
    )


def graph_card(
    *,
    nodes: list[GraphNode],
    edges: list[GraphEdge],
    agent_source: str | None = None,
) -> A2UICard:
    """Build a graph A2UI card payload.

    Returns:
        A2UICard with surface="graph" and a GraphSurfacePayload.
    """
    return A2UICard(
        surface="graph",
        data=GraphSurfacePayload(nodes=list(nodes), edges=list(edges)),
        agent_source=agent_source,
    )


def playback_card(
    *,
    video_url: str,
    thumbnail_url: str,
    duration_seconds: float,
    chapters: list[PlaybackChapter],
    agent_source: str | None = None,
) -> A2UICard:
    """Build a playback A2UI card payload.

    Returns:
        A2UICard with surface="playback" and a PlaybackSurfacePayload.
    """
    return A2UICard(
        surface="playback",
        data=PlaybackSurfacePayload(
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            duration_seconds=duration_seconds,
            chapters=list(chapters),
        ),
        agent_source=agent_source,
    )


def lineage_card(
    *,
    source_pdf: str,
    rows: list[LineageRow],
    agent_source: str | None = None,
) -> A2UICard:
    """Build a lineage A2UI card payload.

    Returns:
        A2UICard with surface="lineage" and a LineageSurfacePayload.
    """
    return A2UICard(
        surface="lineage",
        data=LineageSurfacePayload(source_pdf=source_pdf, rows=list(rows)),
        agent_source=agent_source,
    )


def search_card(
    *,
    query: str,
    results: list[SearchResultRow],
    agent_source: str | None = None,
) -> A2UICard:
    """Build a search A2UI card payload.

    Returns:
        A2UICard with surface="search" and a SearchSurfacePayload.
    """
    return A2UICard(
        surface="search",
        data=SearchSurfacePayload(query=query, results=list(results)),
        agent_source=agent_source,
    )


def subject_grid_card(
    *,
    subjects: list[SubjectCard],
    agent_source: str | None = None,
) -> A2UICard:
    """Build a subject_grid A2UI card payload.

    Returns:
        A2UICard with surface="subject_grid" and a SubjectGridSurfacePayload.
    """
    return A2UICard(
        surface="subject_grid",
        data=SubjectGridSurfacePayload(subjects=list(subjects)),
        agent_source=agent_source,
    )


def dashboard_card(
    *,
    nations: list[str],
    subjects: list[str],
    cells: list[DashboardCell],
    agent_source: str | None = None,
) -> A2UICard:
    """Build a dashboard A2UI card payload.

    Returns:
        A2UICard with surface="dashboard" and a DashboardSurfacePayload.
    """
    return A2UICard(
        surface="dashboard",
        data=DashboardSurfacePayload(
            nations=list(nations),
            subjects=list(subjects),
            cells=list(cells),
        ),
        agent_source=agent_source,
    )


def translator_card(
    *,
    source_text: str,
    source_language: Literal["en", "ga"],
    translated_text: str,
    target_language: Literal["en", "ga"],
    confidence: float,
    agent_source: str | None = None,
) -> A2UICard:
    """Build a translator A2UI card payload.

    Returns:
        A2UICard with surface="translator" and a TranslatorSurfacePayload.
    """
    return A2UICard(
        surface="translator",
        data=TranslatorSurfacePayload(
            source_text=source_text,
            source_language=source_language,
            translated_text=translated_text,
            target_language=target_language,
            confidence=confidence,
        ),
        agent_source=agent_source,
    )


# ============================================================================
# The 8 canonical surface configs (the agent → surface mapping)
# ============================================================================


A2UI_SURFACE_AGENT_MAP: dict[str, str] = {
    "chart": "statistics_agent",
    "graph": "corpus_agent",
    "playback": "research_agent",
    "lineage": "curriculum_agent",
    "search": "mcp_curriculum_agent",
    "subject_grid": "root_agent",
    "dashboard": "curriculum_comparison_agent",
    "translator": "translation_agent",
}


def emit_a2ui_card(card: A2UICard) -> dict[str, Any]:
    """ADK tool entrypoint: emit an A2UI card as an AG-UI event.

    This is the canonical entrypoint for any ADK agent that wants
    to render an A2UI surface. Returns the JSON-ready AG-UI event
    payload that the front-end ``registry.ts`` will collect + ship
    via the AG-UI SSE handshake.

    Args:
        card: A pre-built A2UICard (use the 8 ``<surface>_card``
            factories above to construct it).

    Returns:
        The AG-UI ``updateComponents`` event dict (ready for
        SSE delivery).
    """
    return card.to_agui_event()


# ============================================================================
# The canonical A2UIGenerator (the unified entry point)
# ============================================================================


class A2UIGenerator:
    """The canonical A2UI card generator for the ADK fleet.

    All 12 ADK agents can call into this generator via
    ``A2UIGenerator().<surface>(...)`` to produce an A2UI card.
    The generator handles surface_id allocation, timestamp
    stamping, and the AG-UI event serialization.

    Usage:

        generator = A2UIGenerator()
        card = generator.chart(
            title="...",
            x_label="...",
            y_label="...",
            series=[...],
        )
        # Hand off to the AG-UI runtime:
        event = generator.emit(card)
    """

    def __init__(self, default_agent_source: str | None = None) -> None:
        self.default_agent_source = default_agent_source

    def chart(
        self,
        *,
        title: str,
        x_label: str,
        y_label: str,
        series: list[ChartSeries],
        chart_type: Literal["line", "bar", "pie"] = "line",
        agent_source: str | None = None,
    ) -> A2UICard:
        return chart_card(
            title=title,
            x_label=x_label,
            y_label=y_label,
            series=series,
            chart_type=chart_type,
            agent_source=agent_source or self.default_agent_source,
        )

    def graph(
        self,
        *,
        nodes: list[GraphNode],
        edges: list[GraphEdge],
        agent_source: str | None = None,
    ) -> A2UICard:
        return graph_card(
            nodes=nodes,
            edges=edges,
            agent_source=agent_source or self.default_agent_source,
        )

    def playback(
        self,
        *,
        video_url: str,
        thumbnail_url: str,
        duration_seconds: float,
        chapters: list[PlaybackChapter],
        agent_source: str | None = None,
    ) -> A2UICard:
        return playback_card(
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            duration_seconds=duration_seconds,
            chapters=chapters,
            agent_source=agent_source or self.default_agent_source,
        )

    def lineage(
        self,
        *,
        source_pdf: str,
        rows: list[LineageRow],
        agent_source: str | None = None,
    ) -> A2UICard:
        return lineage_card(
            source_pdf=source_pdf,
            rows=rows,
            agent_source=agent_source or self.default_agent_source,
        )

    def search(
        self,
        *,
        query: str,
        results: list[SearchResultRow],
        agent_source: str | None = None,
    ) -> A2UICard:
        return search_card(
            query=query,
            results=results,
            agent_source=agent_source or self.default_agent_source,
        )

    def subject_grid(
        self,
        *,
        subjects: list[SubjectCard],
        agent_source: str | None = None,
    ) -> A2UICard:
        return subject_grid_card(
            subjects=subjects,
            agent_source=agent_source or self.default_agent_source,
        )

    def dashboard(
        self,
        *,
        nations: list[str],
        subjects: list[str],
        cells: list[DashboardCell],
        agent_source: str | None = None,
    ) -> A2UICard:
        return dashboard_card(
            nations=nations,
            subjects=subjects,
            cells=cells,
            agent_source=agent_source or self.default_agent_source,
        )

    def translator(
        self,
        *,
        source_text: str,
        source_language: Literal["en", "ga"],
        translated_text: str,
        target_language: Literal["en", "ga"],
        confidence: float,
        agent_source: str | None = None,
    ) -> A2UICard:
        return translator_card(
            source_text=source_text,
            source_language=source_language,
            translated_text=translated_text,
            target_language=target_language,
            confidence=confidence,
            agent_source=agent_source or self.default_agent_source,
        )

    def emit(self, card: A2UICard) -> dict[str, Any]:
        """Emit an A2UI card as an AG-UI event payload."""
        return emit_a2ui_card(card)


__all__ = [
    "A2UICard",
    "A2UIGenerator",
    "A2UI_SURFACE_AGENT_MAP",
    "ChartSurfacePayload",
    "GraphSurfacePayload",
    "PlaybackSurfacePayload",
    "LineageSurfacePayload",
    "SearchSurfacePayload",
    "SubjectGridSurfacePayload",
    "DashboardSurfacePayload",
    "TranslatorSurfacePayload",
    "chart_card",
    "graph_card",
    "playback_card",
    "lineage_card",
    "search_card",
    "subject_grid_card",
    "dashboard_card",
    "translator_card",
    "emit_a2ui_card",
]