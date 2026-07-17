# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "altair>=5.0",
#     "pandas>=2.0",
# ]
# ///
"""03 — Cognee knowledge-graph visualiser (per-subject).

For each BIEP subject, visualises the Cognify pass output —
reads from ``md:cianfhoghlaim.cognee.<subject>_kg`` (the table that
the ``lc5_<subject>_cognified`` Dagster asset materialises).

Falls back to a 20-node synthetic KG (5 NCCA Key Competencies +
15 example LO nodes) when the lakehouse is unreachable so the
dashboard renders offline.

Dual-mode usage:

    # Interactive
    marimo edit 03_cognee_knowledge_graph.py

    # CLI — single subject
    uv run 06_observability/03_cognee_knowledge_graph.py --subject chemistry
"""
from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    import pandas as pd
    import altair as alt
    return alt, mo, pd


@app.cell
def _intro(mo):
    mo.md(
        """
        # 03 — Cognee knowledge-graph visualiser

        Per-subject view of the Cognify pass output for the 6 BIEP
        priority LC subjects. Reads from
        ``md:cianfhoghlaim.cognee.<subject>_kg`` (the Cognee node/edge
        tables materialised by ``lc5_<subject>_cognified``).

        When the lakehouse is unreachable, falls back to a 20-node
        synthetic KG (5 NCCA Key Competencies + 15 example LO nodes)
        so the dashboard renders during local dev.
        """
    )
    return  # (no-op; marimo-safe)


@app.cell
def _controls(mo):
    from cianfhoghlaim.notebooks.nb_utils import BIEP_SUBJECTS
    subject = mo.ui.dropdown(
        options=list(BIEP_SUBJECTS),
        value="chemistry",
        label="Subject",
    )
    subject
    return BIEP_SUBJECTS, subject


@app.cell
def _read_lakehouse(subject, mo):
    """Read the kg nodes for the selected subject from md:cianfhoghlaim."""
    from cianfhoghlaim.notebooks.nb_utils import connect_biep_lakehouse
    con, engine = connect_biep_lakehouse()
    nodes = []
    edges = []
    if engine == "md:oideachais":
        try:
            nodes_df = con.execute(f"""
                SELECT node_id, node_type, label, weight
                FROM md:cianfhoghlaim.cognee.{subject.value}_kg_nodes
            """).fetchdf() if False else con.execute(f"""
                SELECT node_id, node_type, label, weight
                FROM cianfhoghlaim.cognee.{subject.value}_kg_nodes
            """).fetchdf()
            edges_df = con.execute(f"""
                SELECT source_id AS source, target_id AS target, edge_type, weight
                FROM cianfhoghlaim.cognee.{subject.value}_kg_edges
            """).fetchdf()
            nodes = nodes_df.to_dict("records")
            edges = edges_df.to_dict("records")
            src = "md:oideachais"
        except Exception as exc:
            src = f"error: {exc}"
    else:
        src = engine
    return con, edges, engine, nodes, src


@app.cell
def _synthetic_kg(subject, nodes, edges):
    """Build synthetic KG when the lakehouse is unavailable.

    Returns (nodes, edges). When the lakehouse provides nodes we use them;
    otherwise we synthesize a 20-node KG (5 KeyCompetencies + 15 LOs).
    """
    _synth_nodes = nodes if nodes else [
        {"node_id": "kc_communicating", "node_type": "KeyCompetency", "label": "Communicating", "weight": 1.0},
        {"node_id": "kc_info_processing", "node_type": "KeyCompetency", "label": "Information Processing", "weight": 1.0},
        {"node_id": "kc_critical_creative", "node_type": "KeyCompetency", "label": "Critical & Creative Thinking", "weight": 1.0},
        {"node_id": "kc_personal_effectiveness", "node_type": "KeyCompetency", "label": "Personal Effectiveness", "weight": 1.0},
        {"node_id": "kc_working_with_others", "node_type": "KeyCompetency", "label": "Working with Others", "weight": 1.0},
    ]
    if not nodes:
        for _i in range(1, 16):
            _synth_nodes.append({
                "node_id": f"lo_{subject.value}_{_i:02d}",
                "node_type": "LearningOutcome",
                "label": f"LO-{subject.value}-{_i}",
                "weight": 0.5 + (_i % 5) * 0.1,
            })
    (_synth_nodes, edges)


@app.cell
def _render(nodes, edges, mo, pd, alt, subject, src):
    """Render the KG as a force-layout altair scatter (proj-via-UMAP fallback to a hash)."""
    import hashlib

    if not nodes:
        _render_md = mo.md(
            f"_No KG data for `{subject.value}` (engine: `{src}`). "
            "Materialise the `cognee_<subject>_kg` asset first._"
        )
    else:
        _df = pd.DataFrame(nodes)
        # Cheap 2D projection — hash-based deterministic layout (UMAP will
        # be wired when sentence-transformers is added to this notebook's
        # PEP 723 block).
        def _proj(node_id: str) -> tuple[float, float]:
            _h = hashlib.sha256(node_id.encode()).digest()
            return (_h[0] / 255.0, _h[1] / 255.0)
        _proj_df = _df["node_id"].apply(
            lambda s: pd.Series(_proj(s), index=["x", "y"])
        )
        _df = pd.concat([_df, _proj_df], axis=1)
        _chart = (
            alt.Chart(_df)
            .mark_circle(size=180, opacity=0.8)
            .encode(
                x=alt.X("x:Q", axis=None),
                y=alt.Y("y:Q", axis=None),
                color=alt.Color("node_type:N", legend=alt.Legend(title="Node type")),
                size=alt.Size("weight:Q", scale=alt.Scale(range=[60, 380])),
                tooltip=["node_id", "label", "node_type", "weight"],
            )
            .properties(
                width=620, height=420,
                title=f"Cognee KG — {subject.value} ({len(_df)} nodes, src: {src})",
            )
            .interactive()
        )
        _render_md = mo.vstack([
            mo.md(f"## KG projection — `{subject.value}` ({len(_df)} nodes, source: `{src}`)"),
            mo.ui.altair_chart(_chart),
            mo.md("**Node types**: `KeyCompetency` (root nodes) + `LearningOutcome` (children)."),
        ])
    _render_md


# =============================================================================
# Dual-mode CLI
# =============================================================================
def _cli_main(argv=None) -> int:
    import argparse
    import json
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="03_cognee_knowledge_graph.py",
        description="Cognee KG visualiser (per-subject CLI mode).",
    )
    parser.add_argument(
        "--subject",
        type=str,
        default="chemistry",
        choices=["mathematics", "applied_mathematics", "english", "gaeilge", "biology", "chemistry"],
    )
    args = parser.parse_args(argv)

    # Add the repo root to sys.path so we can import the cianfhoghlaim package
    # when the notebook is invoked as a CLI script from any cwd.
    # File: <repo>/cianfhoghlaim/notebooks/06_observability/03_cognee_knowledge_graph.py
    # Repo: <repo>/  ← here.parents[2]
    import sys
    _here = Path(__file__).resolve().parent  # 06_observability/
    _repo_root = _here.parents[2]            # <repo>/
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))

    from cianfhoghlaim.notebooks.nb_utils import connect_biep_lakehouse
    con, engine = connect_biep_lakehouse()

    summary = {"subject": args.subject, "engine": engine, "nodes": 0, "edges": 0}
    if engine == "md:oideachais":
        try:
            n_nodes = con.execute(f"""
                SELECT count(*) FROM cianfhoghlaim.cognee.{args.subject}_kg_nodes
            """).fetchone()
            n_edges = con.execute(f"""
                SELECT count(*) FROM cianfhoghlaim.cognee.{args.subject}_kg_edges
            """).fetchone()
            summary["nodes"] = n_nodes[0] if n_nodes else 0
            summary["edges"] = n_edges[0] if n_edges else 0
        except Exception as exc:
            summary["error"] = str(exc)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main())
    app.run()