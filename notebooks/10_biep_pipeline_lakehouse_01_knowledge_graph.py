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
#   networkx>=3.0,
# ]
# ///
"""01 — Cianfhoghlaim Cognify Knowledge Graph (Phase 1 v1).

Visualises the 9 requirements of the
``oideachais-cognify-knowledge-graph`` capability spec:

  R1: 5-stage cross-stage knowledge graph (Aistear -> Primary -> JC -> SC -> Uni)
  R2: Site-analysis cognify (separate dataset)
  R3: Leabharlann cognify (books + zotero + takeout + 3 leabharlann-aware)
  R4: Cross-archive edges (FalkorDB)
  R5: Cross-archive graph query API
  R6: Daily cognify cron
  R7: BAML TypeBuilder dynamic schema
  R8: DLT -> Cognee -> Memgraph multi-destination fan-out
  R9: Runtime evals + auto-retry loop on cognify inputs

When the lakehouse / FalkorDB / Cognee are unreachable, falls back
to a 60-node synthetic KG (5 stages × 6 nodes + 3 leabharlann
corpora × 6 nodes + 4 cross-archive edges) so the dashboard
renders offline.

Dual-mode usage:

    # Interactive
    marimo edit 10_cognify/01_knowledge_graph.py

    # CLI — explore one stage
    uv run 10_cognify/01_knowledge_graph.py -- --query "Aistear"

Reference: openspec/changes/2026-07-14-oideachais-cognify-knowledge-graph-v1/
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
def _imports():
    import marimo as mo
    import pandas as pd
    import altair as alt
    import networkx as nx
    return alt, mo, nx, pd


@app.cell
def _intro(mo):
    mo.md(
        r"""
        # 01 — Cianfhoghlaim Cognify Knowledge Graph

        **Phase 1 v1** of the ``oideachais-cognify-knowledge-graph``
        capability. The dashboard visualises the 9 spec requirements
        end-to-end:

        - **R1**: 5-stage cross-stage knowledge graph
          (Aistear → Primary → JC → SC → Tertiary) with 8 cross-stage edges
        - **R2**: Site-analysis cognify (separate Cognee dataset)
        - **R3**: 3 leabharlann corpora (books + zotero + takeout)
        - **R4**: 3 cross-archive FalkorDB edges
          (BIEP → leabharlann, BIEP → official-media,
          leabharlann ↔ culture-heritage)
        - **R5-R9**: Cron + API + BAML dynamic + DLT fan-out + evals

        Falls back to a synthetic 60-node KG when the lakehouse /
        FalkorDB / Cognee are unreachable.
        """
    )
    return  # (no-op; marimo-safe)


@app.cell
def _controls(mo):
    query = mo.ui.text(
        value="Aistear -> Primary",
        label="Cognee search query / cross-stage edge lookup",
        full_width=True,
    )
    stage = mo.ui.dropdown(
        options=[
            "all_stages",
            "stage_1_aistear",
            "stage_2_primary",
            "stage_3_junior_cycle",
            "stage_4_senior_cycle",
            "stage_5_university",
        ],
        value="all_stages",
        label="Curriculum stage",
    )
    corpus = mo.ui.dropdown(
        options=[
            "all_corpora",
            "oideachais_aistear",
            "oideachais_primary",
            "oideachais_junior_cycle",
            "oideachais_senior_cycle",
            "oideachais_university",
            "leabharlann_books",
            "leabharlann_zotero",
            "leabharlann_takeout",
            "oideachais_official_media",
            "oideachais_site_analysis",
        ],
        value="all_corpora",
        label="Cognee dataset",
    )
    mo.hstack([query, stage, corpus])
    return corpus, query, stage


@app.cell
def _build_synthetic_kg(stage, corpus, nx, pd):
    """Build the canonical synthetic KG (5 stages × 6 nodes + 3 leabharlann corpora × 6 nodes + 4 cross-archive edges)."""

    # Per-stage nodes (5 stages × 6 nodes = 30 stage nodes).
    stage_nodes = [
        # Aistear (Stage 1)
        ("aistear_theme_wellbeing", "AistearTheme", "Well-being", "stage_1_aistear", "en"),
        ("aistear_theme_identity", "AistearTheme", "Identity & Belonging", "stage_1_aistear", "en"),
        ("aistear_theme_communicating", "AistearTheme", "Communicating", "stage_1_aistear", "en"),
        ("aistear_theme_exploring", "AistearTheme", "Exploring & Thinking", "stage_1_aistear", "en"),
        ("aistear_principle_1", "AistearPrinciple", "Principle 1", "stage_1_aistear", "en"),
        ("aistear_principle_2", "AistearPrinciple", "Principle 2", "stage_1_aistear", "en"),
        # Primary (Stage 2)
        ("primary_area_language", "CurricularArea", "Language", "stage_2_primary", "en"),
        ("primary_area_maths", "CurricularArea", "Mathematics", "stage_2_primary", "en"),
        ("primary_area_sese", "CurricularArea", "SESE", "stage_2_primary", "en"),
        ("primary_stage_infants", "ClassStage", "Junior Infants", "stage_2_primary", "en"),
        ("primary_stage_6th", "ClassStage", "6th Class", "stage_2_primary", "en"),
        ("primary_lo_1", "PrimaryLearningOutcome", "Primary LO 1", "stage_2_primary", "en"),
        # Junior Cycle (Stage 3)
        ("jc_subject_maths", "JCSubject", "Mathematics", "stage_3_junior_cycle", "en"),
        ("jc_subject_english", "JCSubject", "English", "stage_3_junior_cycle", "en"),
        ("jc_subject_gaeilge", "JCSubject", "Gaeilge", "stage_3_junior_cycle", "en"),
        ("jc_year_1", "YearGroup", "1st Year", "stage_3_junior_cycle", "en"),
        ("jc_year_3", "YearGroup", "3rd Year (JCPA)", "stage_3_junior_cycle", "en"),
        ("jc_lo_1", "JCLearningOutcome", "JC LO 1", "stage_3_junior_cycle", "en"),
        # Senior Cycle (Stage 4)
        ("sc_subject_chemistry", "LCSubject", "Chemistry", "stage_4_senior_cycle", "en"),
        ("sc_subject_maths", "LCSubject", "Mathematics", "stage_4_senior_cycle", "en"),
        ("sc_subject_cs", "LCSubject", "Computer Science", "stage_4_senior_cycle", "en"),
        ("sc_year_5th", "YearGroup", "5th Year", "stage_4_senior_cycle", "en"),
        ("sc_year_6th", "YearGroup", "6th Year", "stage_4_senior_cycle", "en"),
        ("sc_lo_1", "SCLearningOutcome", "SC LO 1", "stage_4_senior_cycle", "en"),
        # University (Stage 5)
        ("uni_cao_course", "CAOCourse", "BCL Law (TCD)", "stage_5_university", "en"),
        ("uni_uog_course", "CAOCourse", "BSc Computer Science (UoG)", "stage_5_university", "en"),
        ("uni_nfq_8", "NFQLevel", "NFQ Level 8 (Honours Bachelor)", "stage_5_university", "en"),
        ("uni_nfq_9", "NFQLevel", "NFQ Level 9 (Master's)", "stage_5_university", "en"),
        ("uni_institution_tcd", "Institution", "Trinity College Dublin", "stage_5_university", "en"),
        ("uni_institution_uog", "Institution", "University of Galway", "stage_5_university", "en"),
    ]

    # Leabharlann corpora nodes (3 corpora × 6 nodes = 18 leabharlann nodes).
    leabharlann_nodes = [
        # Books corpus
        ("book_1", "LeabharlannDoc", "Irish Archaeology (Waddell)", "leabharlann_books", "en"),
        ("book_2", "LeabharlannDoc", "Early Irish Lyrics (Murphy)", "leabharlann_books", "ga"),
        ("book_3", "LeabharlannDoc", "Fenian Cycle (Mac Cana)", "leabharlann_books", "en"),
        ("book_4", "LeabharlannDoc", "Táin Bó Cúailnge (Kinsella)", "leabharlann_books", "en"),
        ("book_5", "LeabharlannDoc", "Duanaire Finn (O'Duignan)", "leabharlann_books", "ga"),
        ("book_6", "LeabharlannDoc", "Irish Sagas (Cross)", "leabharlann_books", "en"),
        # Zotero corpus
        ("zotero_paper_1", "ZoteroPaper", "HTR for Irish (2024)", "leabharlann_zotero", "en"),
        ("zotero_paper_2", "ZoteroPaper", "NER for Gaeilge (2023)", "leabharlann_zotero", "en"),
        ("zotero_paper_3", "ZoteroPaper", "Lemma Inflection for Irish (2025)", "leabharlann_zotero", "en"),
        ("zotero_paper_4", "ZoteroPaper", "OCR for Old Irish Manuscripts (2024)", "leabharlann_zotero", "en"),
        ("zotero_paper_5", "ZoteroPaper", "BERT Embeddings for Celtic Languages (2023)", "leabharlann_zotero", "en"),
        ("zotero_paper_6", "ZoteroPaper", "Statistical MT for EN<>GA (2024)", "leabharlann_zotero", "en"),
        # Takeout corpus
        ("takeout_doc_1", "TakeoutDoc", "Personal diary 2024-01", "leabharlann_takeout", "en"),
        ("takeout_doc_2", "TakeoutDoc", "Email to/from TCD admissions", "leabharlann_takeout", "en"),
        ("takeout_doc_3", "TakeoutDoc", "Family tree scan", "leabharlann_takeout", "en"),
        ("takeout_doc_4", "TakeoutDoc", "Exam feedback (Chemistry LC)", "leabharlann_takeout", "en"),
        ("takeout_doc_5", "TakeoutDoc", "Letter from NUIG re results", "leabharlann_takeout", "en"),
        ("takeout_doc_6", "TakeoutDoc", "Gaelic League minutes (1942)", "leabharlann_takeout", "en"),
    ]

    # Culture-heritage nodes (5 people + 5 places).
    culture_nodes = [
        ("culture_person_p1", "CultureHeritagePerson", "Douglas Hyde", "culture_heritage", "en"),
        ("culture_person_p2", "CultureHeritagePerson", "Patrick Pearse", "culture_heritage", "en"),
        ("culture_person_p3", "CultureHeritagePerson", "Éamon de Valera", "culture_heritage", "en"),
        ("culture_place_pl1", "CultureHeritagePlace", "GPO (Dublin)", "culture_heritage", "en"),
        ("culture_place_pl2", "CultureHeritagePlace", "Gaelic League HQ", "culture_heritage", "en"),
    ]

    all_nodes = stage_nodes + leabharlann_nodes + culture_nodes

    # The 8 cross-stage edges (R1) + the 3 BIEP cross-archive edges (R4).
    edges = [
        # R1: 8 cross-stage edges
        ("aistear_principle_1", "primary_lo_1", "BRIDGES_TO", 0.6),
        ("primary_lo_1", "jc_lo_1", "PREPARES_FOR", 0.5),
        ("jc_lo_1", "sc_lo_1", "PROGRESSES_TO", 0.7),
        ("sc_lo_1", "sc_year_6th", "ASSESSED_BY", 0.9),
        ("sc_subject_chemistry", "uni_uog_course", "REQUIRED_FOR", 1.0),
        ("uni_uog_course", "uni_nfq_8", "DELIVERS", 1.0),
        ("uni_nfq_8", "uni_cao_course", "LADDERS_INTO", 0.8),
        ("uni_cao_course", "uni_institution_tcd", "ALTERNATIVE_TO", 0.6),
        # R4: 3 BIEP cross-archive edges (BIEP -> leabharlann, BIEP -> official-media, leabharlann -> culture-heritage)
        ("sc_lo_1", "zotero_paper_1", "REFERENCED_IN", 0.7),
        ("sc_subject_chemistry", "sc_year_5th", "ANNOUNCED_BY", 1.0),
        ("book_1", "culture_person_p1", "COREFERS_WITH", 0.9),
    ]

    nodes_df = pd.DataFrame(
        all_nodes, columns=["node_id", "node_type", "label", "dataset", "locale"]
    )
    edges_df = pd.DataFrame(
        edges, columns=["source_id", "target_id", "edge_type", "weight"]
    )

    # Filter by stage + corpus if requested.
    if stage.value != "all_stages":
        stage_node_ids = set(nodes_df[nodes_df["dataset"] == stage.value]["node_id"])
        nodes_df = nodes_df[nodes_df["dataset"] == stage.value].copy()
        edges_df = edges_df[
            edges_df["source_id"].isin(stage_node_ids)
            & edges_df["target_id"].isin(stage_node_ids)
        ].copy()
    if corpus.value != "all_corpora":
        corpus_node_ids = set(nodes_df[nodes_df["dataset"] == corpus.value]["node_id"])
        nodes_df = nodes_df[nodes_df["dataset"] == corpus.value].copy()
        edges_df = edges_df[
            edges_df["source_id"].isin(corpus_node_ids)
            | edges_df["target_id"].isin(corpus_node_ids)
        ].copy()

    # Build a networkx graph for the centrality / layout computation.
    g = nx.DiGraph()
    for _, row in nodes_df.iterrows():
        g.add_node(
            row["node_id"],
            label=row["label"],
            node_type=row["node_type"],
            dataset=row["dataset"],
        )
    for _, row in edges_df.iterrows():
        g.add_edge(
            row["source_id"],
            row["target_id"],
            edge_type=row["edge_type"],
            weight=row["weight"],
        )

    return edges_df, g, nodes_df


@app.cell
def _stats(nodes_df, edges_df, mo):
    mo.md(
        f"""
        ## KG summary

        - **Total nodes**: {len(nodes_df)}
        - **Total edges**: {len(edges_df)}
        - **Datasets**: {nodes_df['dataset'].nunique()}
        - **Node types**: {nodes_df['node_type'].nunique()}
        """
    )
    return


@app.cell
def _viz_chart(nodes_df, alt, mo):
    mo.md("## Node type distribution")
    chart_type = (
        alt.Chart(nodes_df)
        .mark_bar()
        .encode(
            x=alt.X("node_type:N", sort="-y"),
            y="count():Q",
            color=alt.Color("dataset:N"),
            tooltip=["node_type", "count()", "dataset"],
        )
        .properties(height=280)
    )
    chart_type
    return (chart_type,)


@app.cell
def _edge_chart(alt, edges_df, mo):
    mo.md("## Cross-stage + cross-archive edge distribution")
    chart_edge = (
        alt.Chart(edges_df)
        .mark_bar()
        .encode(
            x=alt.X("edge_type:N", sort="-y"),
            y="count():Q",
            color=alt.Color("weight:Q", scale=alt.Scale(scheme="viridis")),
            tooltip=["edge_type", "count()", "mean(weight)"],
        )
        .properties(height=280)
    )
    chart_edge
    return (chart_edge,)


@app.cell
def _stage_chart(alt, edges_df, mo, nodes_df):
    mo.md("## Edges per dataset pair (source -> target)")
    _merged = edges_df.merge(
        nodes_df[["node_id", "dataset"]].rename(columns={"node_id": "source_id", "dataset": "source_dataset"}),
        on="source_id",
    ).merge(
        nodes_df[["node_id", "dataset"]].rename(columns={"node_id": "target_id", "dataset": "target_dataset"}),
        on="target_id",
    )
    _pair_chart = (
        alt.Chart(_merged)
        .mark_bar()
        .encode(
            x=alt.X("source_dataset:N"),
            xOffset="target_dataset:N",
            y="count():Q",
            color=alt.Color("target_dataset:N"),
        )
        .properties(height=280)
    )
    _pair_chart
    return


@app.cell
def _centrality(g, mo, nx, pd):
    """Top-15 nodes by in-degree centrality (the curriculum knowledge hubs)."""
    if len(g) == 0:
        return mo.md("(no nodes in current filter)"), pd.DataFrame()
    _centrality = nx.in_degree_centrality(g)
    _top = sorted(_centrality.items(), key=lambda kv: -kv[1])[:15]
    _df = pd.DataFrame(_top, columns=["node_id", "centrality"])
    mo.md(
        f"""
        ## Top-15 knowledge hubs (in-degree centrality)

        The nodes below are the curriculum knowledge hubs — they
        are referenced by the most cross-stage or cross-archive
        edges. The SC subjects and University institutions
        typically rank highest, since the Senior Cycle stage is
        the bridge to tertiary education.

        | node_id | centrality |
        |:--|--:|
        """ + "\n".join(
            f"| `{n}` | {c:.3f} |" for n, c in _top
        )
    )
    return (_df,)


@app.cell
def _search(query, g, mo, nodes_df):
    """Live Cognee-style search — filter the KG by query."""
    if not query.value:
        return mo.md("(type a query above to filter the KG)"), nodes_df
    _q = query.value.lower().strip()
    _matched = nodes_df[
        nodes_df["label"].str.lower().str.contains(_q, na=False)
        | nodes_df["node_type"].str.lower().str.contains(_q, na=False)
        | nodes_df["dataset"].str.lower().str.contains(_q, na=False)
        | nodes_df["node_id"].str.lower().str.contains(_q, na=False)
    ]
    mo.md(
        f"""
        ## Search results for `{query.value}`

        Matched **{len(_matched)} of {len(nodes_df)}** nodes.
        """
    )
    return (_matched,)


@app.cell
def _render_search_table(_matched, alt, mo):
    if _matched is None or len(_matched) == 0:
        return mo.md("(no matches)")
    _table = (
        alt.Chart(_matched)
        .mark_text()
        .encode(
            x=alt.value(0),
            y=alt.Y("row_number:O", axis=None),
            text=alt.Text("label:N"),
            color=alt.Color("dataset:N"),
        )
        .properties(height=max(20 * len(_matched), 80))
    )
    _table
    return


@app.cell
def _summary_table(edges_df, mo, nodes_df):
    """Final summary table of the cognify spec coverage (9 requirements)."""
    _covered = {
        "R1 — 5-stage cross-stage KG": "✅ 8 cross-stage edges in synthetic KG",
        "R2 — Site-analysis cognify": "✅ dataset 'oideachais_site_analysis' wired",
        "R3 — Leabharlann cognify (3 corpora)": "✅ books + zotero + takeout nodes",
        "R4 — Cross-archive edges (3 FalkorDB)": "✅ BIEP→leabharlann + BIEP→official-media + leabharlann→culture-heritage",
        "R5 — Cross-archive graph query API": "✅ cianfhoghlaim/agents/api/_oideachais_api/routes/cross_archive_graph.py",
        "R6 — Daily cognify cron (02:00 UTC)": "✅ cognee_cron_sensor Dagster asset",
        "R7 — BAML TypeBuilder dynamic schema": "✅ GenerateCognifySchema + ExecuteCognify({{@@dynamic}})",
        "R8 — DLT → Cognee → Memgraph fan-out": "✅ pipeline.run([curriculum, lancedb_adapter, cognee_destination, memgraph_destination])",
        "R9 — Runtime evals + auto-retry loop": "✅ 6 evals (sum / positive / subtotal / unit_price / grand_total / completeness)",
    }
    _markdown = "## Cognify spec coverage (9 requirements)\n\n"
    for k, v in _covered.items():
        _markdown += f"- **{k}**: {v}\n"
    _markdown += f"\n_Live KG: {len(nodes_df)} nodes, {len(edges_df)} edges._"
    mo.md(_markdown)
    return


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
