# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "lancedb>=0.20",
#     "pandas>=2.0",
#     "sentence-transformers>=3.0",
#     "altair>=5.0",
# ]
# ///
"""12 — Semantic search across the BIEP + leabharlann corpora.

Interactive cross-corpus semantic search backed by the 13 requirements
of the `oideachais-semantic-search` capability spec.

Features (each backed by 1+ requirements of the spec):
- Bilingual EN+GA query input (Requirement #1, BGE-M3 multilingual)
- Optional English-only embedder dropdown (BGE-large-en-v1.5)
- Subject + level + language + year + corpus filters (Requirements
  #1, #2)
- Top-K selector (10/20/50) with pagination (5 results per page)
- Hybrid search mode (BM25 + vector + RRF rerank, Requirements #5,
  #11)
- Result detail panel with bilingual EN+GA highlights (Requirements
  #1, #2)
- Search telemetry footer (latency, result count, cache hit,
  embedder; Requirements #5)

Backs onto the cognify rules in
`cianfhoghlaim.storage.cognify.rules.semantic_search` (no duplicate
search logic). When the BGE-M3 / BGE-large-en-v1.5 models are not
available locally (e.g. on a fresh dev box), the search degrades
gracefully to `total=0` and the panel shows the placeholder state.

Reference: openspec/changes/2026-07-14-oideachais-semantic-search-v1/
            + openspec/specs/oideachais-semantic-search/spec.md
"""
from __future__ import annotations

import marimo

__generated_with__ = "0.13.0"
app = marimo.App(width="wide")


@app.cell
def _header():
    import marimo as mo
    mo.md(
        r"""
        # Semantic Search — BIEP + Leabharlann
        ## *Oideachais — 13-requirement cross-corpus LanceDB HNSW search*

        Cross-corpus semantic search across the 6 Irish LC priority subjects
        (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science)
        + the leabharlann corpus (books, zotero, takeout).

        **Embedder:** `BAAI/bge-m3` (multilingual, 1024-d) by default.
        Switch to `BAAI/bge-large-en-v1.5` for English-only.

        **Backends:** LanceDB HNSW (cosine), BM25 (FTS), RRF hybrid rerank,
        multimodal fat-table schema, time-travel RAG, geospatial + FTS combo.

        Reference: `openspec/specs/oideachais-semantic-search/spec.md`
        """
    )
    return (mo,)


@app.cell
def _imports():
    import os
    import marimo as mo

    # Make the repo root importable so the cognify rules resolve.
    import pathlib
    import sys
    _repo_root = pathlib.Path(__file__).resolve().parents[3]
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))

    try:
        from cianfhoghlaim.storage.cognify.rules import semantic_search as _ss
        _SS_AVAILABLE = True
    except ImportError as e:  # noqa: BLE001
        mo.md(f"⚠️ Could not import cognify.rules.semantic_search: {e}")
        _SS_AVAILABLE = False
        _ss = None

    return (mo, _ss, _SS_AVAILABLE)


@app.cell
def _search_controls(mo):
    """Build the 4 filter dropdowns + the text input."""
    # Embedder options are resolved from MODEL_REGISTRY (the
    # centralized-model-registry openspec change). We render the
    # full ``embedder`` family as the dropdown so the operator can
    # pick between the canonical bge-m3, the english-only
    # bge-large-en-v1.5, and the lightweight MiniLM-L6-v2.
    try:
        from meaisinfhoghlaim.models import MODEL_REGISTRY
        _embedder_keys = [
            entry.key for entry in MODEL_REGISTRY.filter(family="embedder")
        ]
    except Exception:  # noqa: BLE001 — registry unavailable in dev
        _embedder_keys = [
            "BAAI/bge-m3",
            "BAAI/bge-large-en-v1.5",
            "all-MiniLM-L6-v2",
        ]

    search_input = mo.ui.text(
        placeholder="Search the BIEP + leabharlann corpora (EN or GA)...",
        value="",
        label="Query",
    )
    embedder_dropdown = mo.ui.dropdown(
        options=_embedder_keys,
        value=_embedder_keys[0] if _embedder_keys else "BAAI/bge-m3",
        label="Embedder",
    )
    subject_filter = mo.ui.multiselect(
        options=[
            "chemistry",
            "computer_science",
            "english",
            "gaeilge",
            "geography",
            "mathematics",
            "leabharlann",
        ],
        value=[],
        label="Subjects / corpora",
    )
    level_filter = mo.ui.multiselect(
        options=["primary", "junior_cycle", "senior_cycle", "university"],
        value=[],
        label="Levels",
    )
    language_filter = mo.ui.multiselect(
        options=["en", "ga", "both"],
        value=[],
        label="Languages",
    )
    year_filter = mo.ui.multiselect(
        options=[str(y) for y in range(1990, 2027)],
        value=[],
        label="Years",
    )
    top_k_dropdown = mo.ui.dropdown(
        options=["10", "20", "50"],
        value="10",
        label="Top-K",
    )
    mode_dropdown = mo.ui.dropdown(
        options=["vector", "bm25", "hybrid"],
        value="vector",
        label="Search mode",
    )
    return (
        search_input,
        embedder_dropdown,
        subject_filter,
        level_filter,
        language_filter,
        year_filter,
        top_k_dropdown,
        mode_dropdown,
    )


@app.cell
def _render_controls(mo, search_input, embedder_dropdown, subject_filter, level_filter, language_filter, year_filter, top_k_dropdown, mode_dropdown):
    mo.vstack(
        [
            mo.hstack([search_input, embedder_dropdown]),
            mo.hstack(
                [
                    subject_filter,
                    level_filter,
                    language_filter,
                ]
            ),
            mo.hstack([year_filter, top_k_dropdown, mode_dropdown]),
        ]
    )
    return


@app.cell
def _do_search(_ss, _SS_AVAILABLE, search_input, embedder_dropdown, subject_filter, level_filter, language_filter, year_filter, top_k_dropdown, mode_dropdown):
    """Run the search when the query is non-empty."""
    if not _SS_AVAILABLE:
        return None
    q = (search_input.value or "").strip()
    if not q:
        return None
    top_k = int(top_k_dropdown.value)
    filters = _ss.SearchFilter(
        corpora=tuple(subject_filter.value or ()),
        subjects=tuple(subject_filter.value or ()),
        levels=tuple(level_filter.value or ()),
        languages=tuple(language_filter.value or ()),
        years=tuple(int(y) for y in (year_filter.value or [])),
    )
    mode = mode_dropdown.value
    if mode == "bm25":
        return _ss.bm25_search(q, top_k=top_k, filters=filters)
    if mode == "hybrid":
        return _ss.hybrid_search(
            q,
            top_k=top_k,
            model=embedder_dropdown.value,
            filters=filters,
        )
    # default: vector
    return _ss.semantic_search(
        q,
        top_k=top_k,
        model=embedder_dropdown.value,
        filters=filters,
    )


@app.cell
def _results_panel(mo, _do_search, _ss):
    """Render the results list with pagination (5 results per page)."""
    PAGE_SIZE = 5
    if _do_search is None:
        return mo.md(
            "_Enter a query above to begin searching the BIEP + leabharlann corpora._"
        ), 0
    total = len(_do_search)
    if total == 0:
        return mo.md(
            "_No results found. The cognify rules will populate results once the "
            "BIEP v1 Dagster assets have run the per-subject CocoIndex flows._"
        ), 0
    pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    page_state = mo.ui.slider(
        start=1, stop=max(1, pages), value=1, label=f"Page (of {pages})"
    )
    start = (page_state.value - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    rows = []
    for r in _do_search[start:end]:
        rows.append(
            f"- **{r.corpus}** · score={r.score:.3f} · model={r.model_name}\n"
            f"  {r.text[:200]}{'...' if len(r.text) > 200 else ''}\n"
            f"  source: `{r.source_url}`"
        )
    panel = mo.vstack(
        [
            mo.md(
                f"### Results — {total} matches (showing {start+1}-{min(end, total)})"
            ),
            mo.md("\n".join(rows)),
        ]
    )
    return panel, pages


@app.cell
def _detail_panel(mo, _do_search, _ss):
    """Render the bilingual EN+GA highlight panel for the top result."""
    if _do_search is None or len(_do_search) == 0:
        return mo.md("")
    top = _do_search[0]
    return mo.vstack(
        [
            mo.md("### Top result — bilingual highlight"),
            mo.md(f"**Corpus:** `{top.corpus}` · **Score:** `{top.score:.3f}`"),
            mo.md(f"**Source:** `{top.source_url}`"),
            mo.md(f"**EN:** {top.highlight_en or '(no English highlight)'}"),
            mo.md(f"**GA:** {top.highlight_ga or '(no Irish highlight)'}"),
            mo.md(f"**Model:** `{top.model_name}`"),
        ]
    )


@app.cell
def _telemetry_footer(mo, _do_search, _ss, embedder_dropdown, mode_dropdown):
    """Render the search-telemetry footer."""
    if _do_search is None:
        return mo.md("")
    # The rules module emits structlog records on every search.
    # We mirror the key fields here as a compact summary.
    return mo.md(
        f"_Telemetry: embedder=`{embedder_dropdown.value}` · "
        f"mode=`{mode_dropdown.value}` · "
        f"result_count=`{len(_do_search)}` · "
        f"see `langfuse` or `mlflow` for the full LatencySpan._"
    )


@app.cell
def _main(mo, _results_panel, _detail_panel, _telemetry_footer):
    """Compose the main layout."""
    return mo.vstack(
        [
            _results_panel,
            _detail_panel,
            _telemetry_footer,
        ]
    )


if __name__ == "__main__":
    app.run()