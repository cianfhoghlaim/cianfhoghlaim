from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)
"""05 — Fediverse instance coverage (official-media-marimo spec, R3).

Renders a 3-panel view of the fediverse instance coverage for the
British Isles official-media accounts. Visualises:

- **Panel A** — the 4 Cognee edge types defined in the spec
  (``ig_profile → official_website``, ``ig_profile → fediverse_account``,
  ``ig_profile → companies_house_entity``,
  ``official_website ↔ wikipedia_article`` (bi-directional))
- **Panel B** — fediverse instance distribution (which Mastodon / Bluesky
  PDS hosts the official accounts)
- **Panel C** — edge direction pie (uni-directional vs bi-directional)

This dashboard is the marimo companion to the **Cognee dataset
``oideachais_official_media``** (R3) — the marimo view is the operator
surface for inspecting the cognify output; the Cognee UI is the
graph query surface for end-users.

Data source: the Cognee ``oideachais_official_media`` dataset
(4 edge types × N profile nodes). Falls back to the cognify stub
metadata when Cognee is unreachable.

Reference: ``openspec/specs/official-media-marimo/spec.md`` —
Requirement "OfficialMediaCogneeDataset" (R3) and the 4-edge-type
topology.
"""
from __future__ import annotations

import marimo

__generated_with = "0.14.10"
app = marimo.App(width="medium")


@app.cell
def _intro():
    import marimo as mo

    mo.md(
        r"""
        # 🌐 Official Media — Fediverse Instance Coverage (R3)

        3-panel coverage view for the **Cognee dataset
        ``oideachais_official_media``** — the graph that joins
        British Isles official-media Instagram profiles to their
        canonical official websites, fediverse accounts,
        Companies House entities, and Wikipedia articles.

        Backed by the 4 edge types from the spec:

        - ``ig_profile → official_website``
        - ``ig_profile → fediverse_account``
        - ``ig_profile → companies_house_entity``
        - ``official_website → wikipedia_article`` (bi-directional)

        ---
        """
    )
    return (mo,)


@app.cell
def _imports():
    import os

    import altair as alt
    import duckdb
    import pandas as pd

    return alt, duckdb, os, pd


@app.cell
def _cognee_metadata():
    """The 4 edge types + their canonical directions, as defined in
    the spec (R3). Source of truth: the ``official_media_cognify``
    module's ``EDGE_TYPES`` constant + the spec requirement body."""
    from cianfhoghlaim.storage.cognify.cognee_integration.official_media_cognify import (
        DATASET_NAME,
        EDGE_TYPES,
    )

    return DATASET_NAME, EDGE_TYPES


@app.cell
def _data_loading(mo, duckdb, os, allowlist_categories, DATASET_NAME, EDGE_TYPES):
    """Load the cognify edges from Cognee (or fall back to a synthetic
    edge set derived from the 4 allowlist YAML fixtures)."""
    edges_df = None
    db_label = ""
    fallback_used = False

    # Try the Cognee REST API first (when COGNEE_API_URL is configured).
    cognee_url = os.environ.get("COGNEE_API_URL", "")
    if cognee_url:
        try:
            import httpx  # local import — keeps the module importable in CI

            resp = httpx.get(
                f"{cognee_url}/v1/datasets/{DATASET_NAME}/edges",
                timeout=10.0,
            )
            resp.raise_for_status()
            payload = resp.json()
            edges_df = pd.DataFrame(payload.get("edges", []))
            db_label = f"Cognee REST ({cognee_url})"
        except Exception as exc:  # noqa: BLE001
            db_label = f"Cognee REST — query failed ({exc!s:.60s})"
            edges_df = None

    if edges_df is None:
        # Graceful fallback — synthesise edges from the 4 allowlist
        # YAML fixtures, anchored on the 4 spec-defined edge types.
        from dlt_sources.official_media.fediverse import (
            resolve_bluesky,
            resolve_mastodon,
        )

        _rows: list[dict] = []
        for cat, usernames in allowlist_categories.items():
            for uname in usernames:
                # ig_profile → official_website (1 per profile)
                _rows.append(
                    {
                        "source_node": f"ig_profile:{uname}",
                        "source_type": "ig_profile",
                        "edge_type": "ig_profile->official_website",
                        "target_node": f"url:https://www.{uname}.example",
                        "target_type": "official_website",
                        "bidirectional": False,
                    }
                )
                # ig_profile → fediverse_account (1–2 per profile)
                for _platform in ("mastodon", "bluesky"):
                    _rows.append(
                        {
                            "source_node": f"ig_profile:{uname}",
                            "source_type": "ig_profile",
                            "edge_type": "ig_profile->fediverse_account",
                            "target_node": f"fediverse:{_platform}:{uname}",
                            "target_type": "fediverse_account",
                            "bidirectional": False,
                        }
                    )
                # ig_profile → companies_house_entity (1 per profile)
                _rows.append(
                    {
                        "source_node": f"ig_profile:{uname}",
                        "source_type": "ig_profile",
                        "edge_type": "ig_profile->companies_house_entity",
                        "target_node": f"ch:{(sum(ord(c) for c in uname) % 9999999):07d}",
                        "target_type": "companies_house_entity",
                        "bidirectional": False,
                    }
                )
                # official_website → wikipedia_article (bi-directional)
                _rows.append(
                    {
                        "source_node": f"url:https://www.{uname}.example",
                        "source_type": "official_website",
                        "edge_type": "official_website->wikipedia_article",
                        "target_node": f"wiki:{uname.title()}",
                        "target_type": "wikipedia_article",
                        "bidirectional": True,
                    }
                )
        edges_df = pd.DataFrame(_rows)
        fallback_used = True
        db_label = f"synthetic (allowlist-derived, {len(EDGE_TYPES)} edge types)"

    # Aggregate by edge_type for the visualisations
    edges_by_type = (
        edges_df.groupby("edge_type", as_index=False)
        .size()
        .rename(columns={"size": "n_edges"})
    )

    summary = {
        "db_label": db_label,
        "n_edges": len(edges_df),
        "n_edge_types": int(edges_df["edge_type"].nunique()),
        "n_nodes": int(
            pd_unique_count(edges_df["source_node"]) + pd_unique_count(edges_df["target_node"])
        ),
        "fallback_used": fallback_used,
    }
    mo.md(
        f"""
        **Database**: `{summary['db_label']}`
        **Edges**: {summary['n_edges']}  |
        **Edge types**: {summary['n_edge_types']}  |
        **Unique nodes**: {summary['n_nodes']}
        **Fallback**: {summary['fallback_used']}
        """
    )
    return (
        db_label,
        edges_by_type,
        edges_df,
        fallback_used,
        resolve_bluesky,
        resolve_mastodon,
        summary,
    )


@app.cell
def _pd_unique():
    """Local helper: count unique values in a Series without requiring
    an explicit `import pandas as pd` in the calling cell (marimo
    scopes imports per-cell)."""
    def pd_unique_count(series):
        return int(series.nunique())

    return (pd_unique_count,)


@app.cell
def _viz_edge_type_counts(alt, edges_by_type, mo):
    """Panel A — the 4 Cognee edge types from the spec, ranked by edge
    count. Horizontal bar chart."""
    _chart_a = (
        alt.Chart(edges_by_type)
        .mark_bar()
        .encode(
            x=alt.X("n_edges:Q", title="Edge count"),
            y=alt.Y("edge_type:N", sort="-x", title="Edge type"),
            color=alt.Color("edge_type:N", legend=None),
            tooltip=["edge_type", "n_edges"],
        )
        .properties(
            width=620,
            height=240,
            title="Panel A — Cognee edge type counts (4 types, spec R3)",
        )
    )
    mo.ui.altair_chart(_chart_a)
    return _chart_a,


@app.cell
def _viz_fediverse_instance_distribution(alt, edges_df, mo):
    """Panel B — fediverse instance distribution (which Mastodon / Bluesky
    hosts the official accounts)."""
    fediverse = edges_df[edges_df["edge_type"] == "ig_profile->fediverse_account"].copy()
    fediverse["platform"] = fediverse["target_node"].apply(
        lambda n: n.split(":")[1] if isinstance(n, str) and ":" in n else "unknown"
    )
    by_platform = (
        fediverse.groupby("platform", as_index=False)
        .size()
        .rename(columns={"size": "n_accounts"})
    )
    _chart_b = (
        alt.Chart(by_platform)
        .mark_arc(innerRadius=60)
        .encode(
            theta=alt.Theta("n_accounts:Q", title="Accounts"),
            color=alt.Color("platform:N", title="Platform"),
            tooltip=["platform", "n_accounts"],
        )
        .properties(
            width=360,
            height=360,
            title="Panel B — Fediverse instance distribution",
        )
    )
    mo.ui.altair_chart(_chart_b)
    return _chart_b, by_platform, fediverse


@app.cell
def _viz_edge_direction(alt, edges_df, mo):
    """Panel C — edge direction pie (uni-directional vs bi-directional)."""
    by_dir = (
        edges_df.assign(
            direction=edges_df["bidirectional"].map(
                {True: "bi-directional", False: "uni-directional"}
            )
        )
        .groupby("direction", as_index=False)
        .size()
        .rename(columns={"size": "n_edges"})
    )
    _chart_c = (
        alt.Chart(by_dir)
        .mark_arc(innerRadius=50)
        .encode(
            theta=alt.Theta("n_edges:Q", title="Edges"),
            color=alt.Color("direction:N", title="Direction"),
            tooltip=["direction", "n_edges"],
        )
        .properties(
            width=360,
            height=360,
            title="Panel C — Edge direction (uni vs bi)",
        )
    )
    mo.ui.altair_chart(_chart_c)
    return _chart_c, by_dir


@app.cell
def _baml_extractor(mo):
    """BAML extractors for the cognify dataset. The R3 requirement
    doesn't directly invoke BAML, but the BAML `ClassifyOfficialMedia`
    is the upstream classifier that decides which Instagram profiles
    become Cognee nodes."""
    baml_result: dict = {"status": "skipped", "reason": "no candidate available"}
    b = None
    decision_obj = None
    try:
        from cianfhoghlaim.baml_client import b

        decision_obj = b.ClassifyOfficialMedia(
            ig_username="mi5official",
            ig_bio="The Security Service (MI5) — official UK domestic counter-intelligence and security agency.",
            ig_external_url="https://www.mi5.gov.uk",
        )
        baml_result = {
            "status": "ok",
            "ig_username": "mi5official",
            "is_official_media": decision_obj.is_official_media,
            "confidence": decision_obj.confidence,
            "category": decision_obj.category,
        }
    except Exception as exc:  # noqa: BLE001
        baml_result = {"status": "failed", "error": str(exc)[:200]}

    mo.md(
        f"""
        ## 🔬 BAML extractor sample

        ```json
        {baml_result!s}
        ```

        Each Cognee node ``ig_profile:*`` was originally classified by
        the BAML `ClassifyOfficialMedia` Stage-2 fallback — the
        cognify step (R3) only sees profiles that passed BAML.
        """
    )
    return baml_result, b, decision_obj


@app.cell
def _allowlist_categories():
    """Read the curated allowlist once (shared across cells)."""
    from dlt_sources.official_media.allowlist import allowlist_filter

    return (allowlist_filter.categories(),)


@app.cell
def _(mo):
    mo.md(
        r"""
        ---

        ## ✊ Why we built this

        The Cognee graph (R3) is the **canonical identity layer** of
        the official-media pipeline. Without it, every other consumer
        (the TanStack route, the marimo dashboards, the agent
        memory) would re-resolve Wikipedia + Companies House +
        Mastodon + Bluesky from scratch on every call. With it, the
        4 lookups happen once at materialisation time, and the rest
        of the stack just does Cypher queries against the graph.

        See ``openspec/specs/official-media-marimo/spec.md`` (R3) for
        the 4 edge types + the cognify registration contract.
        """
    )
    return


if __name__ == "__main__":
    app.run()
