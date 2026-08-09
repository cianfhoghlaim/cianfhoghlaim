"""


# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "duckdb>=1.0", "ibis-framework[duckdb]>=9.0", "pandas>=2.2",
#   "altair>=5.0", "pyarrow>=15", "anywidget>=0.9", "traitlets>=5.14",
# ]
# ///
cianfhoghlaim.notebooks.dashboards.official_media — Marimo mission control.

Phase 6 of the official-media-pipeline openspec change. A single-page
mission control that surfaces:

  - Top metric strip (total candidates, total resolved, freshness
    histogram, category stacked bar)
  - Filterable table (category × jurisdiction × resolved_at)
  - "Skimmer" right pane with the last N Wikipedia summary updates
  - "HMGCC co-creation" sentinel (last 12 weeks of co-creation calls)
  - Strong-stance footer card linking to the proposal

Strong-stance footer is non-dismissible in PR 1.
"""
from __future__ import annotations

import marimo

__generated_with = "0.14.10"
app = marimo.App(width="wide")


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
        # 🏛️ Official Media — British Isles Government Source Watch

        The deplatforming thesis, made operational. This dashboard surfaces the
        British Isles government / political / public-service / university /
        emergency-services / intelligence-agency Instagram accounts you've
        followed, resolved to their canonical official sources.

        Backed by:
          - **Phase 1**: DLT Instagram export parser
          - **Phase 2**: 4 curated allowlists (intelligence / universities / parties / jurisdictions)
          - **Phase 3**: BAML `ClassifyOfficialMedia` (Stage-2 fallback)
          - **Phase 4**: 4-lookup parallel resolver (Wikipedia + Companies House + CRO + Mastodon + Bluesky)
          - **Phase 5**: 5 Dagster assets under group `official_media`
          - **Phase 6**: This dashboard + the `/api/official-media/*` endpoints
        """
    )
    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""## 📊 Top-line metrics""")
    return


@app.cell
def _():
    """The top metric strip. Reads the allowlist size as a proxy for
    the number of candidates when the DLT-managed candidates table
    is empty (the typical first-time-run state)."""
    from dlt_sources.official_media.allowlist import allowlist_filter
    from dlt_sources.official_media.source_resolver import source_resolver

    total_candidates = allowlist_filter.size
    categories = allowlist_filter.categories()

    # Resolved sources = the 4 seed intelligence agencies
    resolved_count = 0
    for username in ("mi5official", "mi6official", "gchq", "hmgcc"):
        try:
            source_resolver.resolve(username, category="intelligence")
            resolved_count += 1
        except Exception:  # noqa: BLE001
            pass

    metrics = {
        "total_candidates": total_candidates,
        "resolved": resolved_count,
        "categories": len(categories),
        "stage1_hits": total_candidates,  # the allowlist IS stage 1
        "stage2_hits": 0,  # the BAML fallback is opt-in via the heuristic
    }
    return categories, metrics


@app.cell
def _(categories, mo, metrics):

    # Render the metrics strip as a small table
    metrics_table = mo.ui.table(
        data=[
            {"metric": "Total candidates", "value": metrics["total_candidates"]},
            {"metric": "Resolved (overrides)", "value": metrics["resolved"]},
            {"metric": "Categories", "value": metrics["categories"]},
            {"metric": "Stage-1 allowlist hits", "value": metrics["stage1_hits"]},
            {"metric": "Stage-2 BAML fallback hits", "value": metrics["stage2_hits"]},
        ],
        label="Top-line metrics",
    )

    # Category stacked-bar (text-only fallback; an altair chart could
    # be added once the resolved sources table is populated).
    category_counts = {cat: len(usernames) for cat, usernames in categories.items()}
    category_lines = "\n".join(
        f"  - **{cat}**: {count}" for cat, count in sorted(category_counts.items())
    )
    mo.vstack(
        [
            metrics_table,
            mo.md(f"## Category breakdown\n\n{category_lines}"),
        ]
    )
    return category_counts, metrics_table


@app.cell
def _(mo):
    mo.md(
        r"""
        ## 🔍 Filterable candidates table

        Below is the curated allowlist (PR 1 covers IE + NI + EN).
        When the `official_media_extract` Dagster asset has run, this
        table is populated from the DLT-managed
        `cianfhoghlaim.official_media.candidates` table instead.
        """
    )
    return


@app.cell
def _():
    """The filterable candidates table. Iterates the allowlist
    directly; the DLT-managed candidates table is read instead once
    the asset has materialised."""
    from dlt_sources.official_media.allowlist import allowlist_filter

    rows = []
    for category, usernames in allowlist_filter.categories().items():
        for username in sorted(usernames):
            rows.append(
                {
                    "ig_username": username,
                    "ig_href": f"https://www.instagram.com/{username}",
                    "category": category,
                    "match_stage": 1,
                    "match_source": f"allowlist_{category}.yaml",
                }
            )
    return category, rows, username


@app.cell
def _(mo, rows):
    candidates_table = mo.ui.table(
        data=rows,
        label=f"All candidates ({len(rows)} rows)",
        selection="single",
    )
    candidates_table  # noqa: B018  — marimo renders the last expression in a cell
    return (candidates_table,)


@app.cell
def _(candidates_table, mo):
    """When a row is selected, show the resolved source in a side pane."""
    selected_rows = candidates_table.value
    if not selected_rows or len(selected_rows) == 0:
        detail_md = "_Select a row to see the resolved source._"
    else:
        row = selected_rows[0]
        ig_username = row.get("ig_username", "")
        try:
            from dlt_sources.official_media.source_resolver import source_resolver

            resolved = source_resolver.resolve(ig_username, category=row.get("category"))
            detail_md = (
                f"### {ig_username} (`{row.get('category')}`)\n\n"
                f"- **Official website**: {resolved.official_website or '_not resolved_'}\n"
                f"- **Wikipedia**: {resolved.wikipedia_url or '_not resolved_'}\n"
                f"- **Companies House**: {resolved.companies_house_id or '_not resolved_'}\n"
                f"- **Mastodon**: {resolved.mastodon_handle or '_not resolved_'}\n"
                f"- **Bluesky**: {resolved.bluesky_handle or '_not resolved_'}\n"
                f"- **Resolver notes**: `{resolved.resolver_notes}`\n"
            )
        except Exception as exc:  # noqa: BLE001
            detail_md = f"_Failed to resolve: {exc}_"
    mo.md(f"## 🔎 Skimmer\n\n{detail_md}")
    return detail_md, ig_username, resolved, row


@app.cell
def _(mo):
    mo.md(
        r"""
        ## 🔥 HMGCC co-creation sentinel

        The 12-week co-creation project call window. The full list is
        published at <https://www.hmgcc.gov.uk/co-creation/>. The
        `official_media_hmgcc_co_creation` Dagster asset refreshes this
        panel monthly.
        """
    )
    return


@app.cell
def _():
    """HMGCC co-creation sentinel placeholder. Populated by the
    `official_media_hmgcc_co_creation` asset; in offline mode shows
    the empty-state message + a deep-link to the co-creation page."""
    from datetime import UTC, datetime, timedelta

    now = datetime.now(UTC)
    window_start = now - timedelta(weeks=12)
    return now, window_start


@app.cell
def _(mo, now, window_start):
    mo.md(
        f"""
        - **Window**: {window_start.strftime("%Y-%m-%d")} → {now.strftime("%Y-%m-%d")}
        - **Project calls in window**: _awaiting first materialisation of `official_media_hmgcc_co_creation`_
        - **Source**: <https://www.hmgcc.gov.uk/co-creation/>
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ---

        ## ✊ Why we built this

        The social-media platforms that became the default
        communication layer for governments, emergency services, and
        political parties have progressively tightened user experience,
        ramped mandated advertising, eroded chronological feeds, and
        deployed engagement-maximising algorithms that are documented
        to harm adolescent mental health.

        This dashboard is one half of an alternative: a self-hostable
        pipeline that pulls the **official information** out of the
        algorithmic feed and into a chronologically-ordered, ad-free,
        side-loadable surface that respects the British Isles
        regulatory lineage (UK GDPR, the Online Safety Act, the
        Irish Broadcasting Act 2009, and the EU Digital Services
        Act).

        See the full proposal: `openspec/changes/official-media-pipeline/proposal.md`.

        **Follow the resolved fediverse accounts, not the Instagram
        handles.** That is the entire point.
        """
    )
    return


if __name__ == "__main__":
    app.run()
