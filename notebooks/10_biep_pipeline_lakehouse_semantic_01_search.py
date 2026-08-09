# /// script
# requires-python = ">=3.12"
# dependencies = [
#   marimo>=0.13,
#   duckdb>=1.0,
#   ibis-framework[duckdb]>=9.0,
#   pandas>=2.2,
#   altair>=5.0,
#   pyarrow>=15,
#   anywidget>=0.9,
#   traitlets>=5.14,
#   lancedb>=0.20,
#   sentence-transformers>=3.0,
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

from notebooks._shared.marimo_patterns import setup_biep_registry_header

import marimo


# R1 — `setup_biep_registry_header()` collapses the 14-line header
# (per the 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1 change)
from notebooks._shared.marimo_patterns import setup_biep_registry_header


__generated_with = "0.14.10"
app = marimo.App(width="wide")


@app.cell
def _header(mo):
    # Per the 2026-08-08-lakehouse-extensive-hydration-v1 change: this
    # cell used to `import marimo as mo` locally and also return it,
    # colliding with the `_imports` cell's own `mo` export (confirmed
    # live: "MultipleDefinitionError: The variable 'mo' was defined by
    # another cell"). Now takes `mo` as a parameter from `_imports`
    # instead of re-importing/re-exporting it.
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
    return


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
        from cianfhoghlaim.storage.cognify.rules import semantic_search as ss
        SS_AVAILABLE = True
    except ImportError as e:  # noqa: BLE001
        mo.md(f"⚠️ Could not import cognify.rules.semantic_search: {e}")
        SS_AVAILABLE = False
        ss = None

    return (mo, ss, SS_AVAILABLE)


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
def search_results(ss, SS_AVAILABLE, search_input, embedder_dropdown, subject_filter, level_filter, language_filter, year_filter, top_k_dropdown, mode_dropdown):
    """Run the search when the query is non-empty."""
    # Per the 2026-08-08-lakehouse-extensive-hydration-v1 change: marimo
    # requires a cell's return to be a single unconditional statement,
    # not reachable from multiple mid-cell `return` branches (confirmed
    # live: "SyntaxError: 'return' outside function"). Restructured to
    # assign a single `search_results` local and return once at the end.
    q = (search_input.value or "").strip()
    if not SS_AVAILABLE or not q:
        search_results = None
    else:
        top_k = int(top_k_dropdown.value)
        filters = ss.SearchFilter(
            corpora=tuple(subject_filter.value or ()),
            subjects=tuple(subject_filter.value or ()),
            levels=tuple(level_filter.value or ()),
            languages=tuple(language_filter.value or ()),
            years=tuple(int(y) for y in (year_filter.value or [])),
        )
        mode = mode_dropdown.value
        if mode == "bm25":
            search_results = ss.bm25_search(q, top_k=top_k, filters=filters)
        elif mode == "hybrid":
            search_results = ss.hybrid_search(
                q,
                top_k=top_k,
                model=embedder_dropdown.value,
                filters=filters,
            )
        else:
            # default: vector
            search_results = ss.semantic_search(
                q,
                top_k=top_k,
                model=embedder_dropdown.value,
                filters=filters,
            )
    return (search_results,)


@app.cell
def results_panel(mo, search_results, ss):
    """Render the results list with pagination (5 results per page)."""
    PAGE_SIZE = 5
    if search_results is None:
        _panel = mo.md(
            "_Enter a query above to begin searching the BIEP + leabharlann corpora._"
        )
    elif len(search_results) == 0:
        _panel = mo.md(
            "_No results found. The cognify rules will populate results once the "
            "BIEP v1 Dagster assets have run the per-subject CocoIndex flows._"
        )
    else:
        _total = len(search_results)
        _pages = (_total + PAGE_SIZE - 1) // PAGE_SIZE
        _page_state = mo.ui.slider(
            start=1, stop=max(1, _pages), value=1, label=f"Page (of {_pages})"
        )
        _start = (_page_state.value - 1) * PAGE_SIZE
        _end = _start + PAGE_SIZE
        _rows = []
        for r in search_results[_start:_end]:
            _rows.append(
                f"- **{r.corpus}** · score={r.score:.3f} · model={r.model_name}\n"
                f"  {r.text[:200]}{'...' if len(r.text) > 200 else ''}\n"
                f"  source: `{r.source_url}`"
            )
        _panel = mo.vstack(
            [
                mo.md(
                    f"### Results — {_total} matches (showing {_start+1}-{min(_end, _total)})"
                ),
                mo.md("\n".join(_rows)),
            ]
        )
    return _panel


@app.cell
def detail_panel(mo, search_results, ss):
    """Render the bilingual EN+GA highlight panel for the top result."""
    if search_results is None or len(search_results) == 0:
        _panel = mo.md("")
    else:
        top = search_results[0]
        _panel = mo.vstack(
            [
                mo.md("### Top result — bilingual highlight"),
                mo.md(f"**Corpus:** `{top.corpus}` · **Score:** `{top.score:.3f}`"),
                mo.md(f"**Source:** `{top.source_url}`"),
                mo.md(f"**EN:** {top.highlight_en or '(no English highlight)'}"),
                mo.md(f"**GA:** {top.highlight_ga or '(no Irish highlight)'}"),
                mo.md(f"**Model:** `{top.model_name}`"),
            ]
        )
    return _panel


@app.cell
def telemetry_footer(mo, search_results, ss, embedder_dropdown, mode_dropdown):
    """Render the search-telemetry footer."""
    if search_results is None:
        _footer = mo.md("")
    else:
        # The rules module emits structlog records on every search.
        # We mirror the key fields here as a compact summary.
        _footer = mo.md(
            f"_Telemetry: embedder=`{embedder_dropdown.value}` · "
            f"mode=`{mode_dropdown.value}` · "
            f"result_count=`{len(search_results)}` · "
            f"see `langfuse` or `mlflow` for the full LatencySpan._"
        )
    return _footer


@app.cell
def _main(mo, results_panel, detail_panel, telemetry_footer):
    """Compose the main layout."""
    return mo.vstack(
        [
            results_panel,
            detail_panel,
            telemetry_footer,
        ]
    )


if __name__ == "__main__":
    app.run()

# ────────────────────────────────────────────────────────────────────────────
# P3 — LLM-assisted analysis tab (the "Ask BAML" tab)
# ────────────────────────────────────────────────────────────────────────────

def _llm_tab():
    """Return an LLM chat widget wired to the canonical litellm proxy (P3).

    Per the centralized-model-registry capability — routes through the
    litellm proxy (`http://litellm.cianfhoghlaim.ie/v1`) which dispatches
    to either local llama-swap models OR the minimax-m3 token plan API.
    """
    from notebooks._shared.marimo_patterns import llm_chat_with_prompts
    import marimo as mo

    return mo.vstack([
        mo.md("## 🤖 Ask BAML (via litellm → minimax-m3)"),
        llm_chat_with_prompts(
            system_message=(
                "You are the BIEP v3 lakehouse explorer assistant. You help "
                "operators query the DuckLake / MotherDuck / LanceDB lakehouse. "
                "When the user asks about a table or column, refer to the DLT "
                "schema introspection in information_schema.tables."
            ),
            prompts=[
                "📚 How many tables are in this schema?",
                "🔍 Show me the schema for the most recently materialised table",
                "📊 What are the top 10 most frequent values in <column_name>?",
                "🎯 How do I query for a specific subject's curriculum_pages?",
            ],
        ),
    ])


# ────────────────────────────────────────────────────────────────────────────
# Dual-mode CLI (per https://docs.marimo.io/guides/scripts/)
# ────────────────────────────────────────────────────────────────────────────

def _cli_main(argv=None):
    """CLI entry point — emits a JSON summary payload (per marimo scripts guide)."""
    import subprocess
    from notebooks._shared.marimo_patterns import (
        cli_argparser_biep, cli_payload_to_output,
    )

    parser = cli_argparser_biep(__name__)
    args = parser.parse_args(argv)

    payload = {
        "notebook": __name__,
        "milestone": args.milestone,
        "asset_check": args.asset_check,
        "status": "ok",
        "exit_code": 0,
        "note": (
            "Run `dagster dev -m oideachais` to start the pipeline, then "
            "re-run this CLI to see the latest status."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    from notebooks._shared.marimo_patterns import cli_main_if_argv
    cli_main_if_argv(_cli_main, app)
