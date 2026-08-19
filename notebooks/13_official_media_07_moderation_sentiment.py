from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)
"""07 — Content moderation + sentiment over time
(official-media-marimo spec, R5).

Renders a 4-panel content-moderation + sentiment dashboard for the
British Isles official-media accounts. Visualises:

- **Panel A** — sentiment over time (line chart, smoothed)
- **Panel B** — moderation flags (bar chart, by flag type)
- **Panel C** — sentiment distribution per category (stacked bar)
- **Panel D** — multi-column tab layout demo (R5 — the Streamlit-
  compatible ``mo.ui.tabs({...})`` layout)

This dashboard is the marimo companion to the **multi-column
``mo.ui.tabs({...})`` layout** requirement (R5). The marimo view
demonstrates the layout; the spec's R5 requirement is that the
layout works on both narrow and wide viewports.

Data source: ``md:cianfhoghlaim_official_media.sentiment_scores`` +
``md:cianfhoghlaim_official_media.moderation_flags``. Falls back to a
synthetic dataset derived from the 4 allowlist YAML fixtures when the
lakehouse is unreachable.

Reference: ``openspec/specs/official-media-marimo/spec.md`` —
Requirement "Streamlit-compatible layout in marimo" (R5) and the
content-moderation + sentiment sub-requirement.
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
        # 🛡️ Official Media — Content Moderation + Sentiment (R5)

        4-panel content-moderation + sentiment dashboard for the
        British Isles official-media accounts.

        Also demonstrates the **multi-column ``mo.ui.tabs({...})``
        layout** (R5) — the Streamlit-compatible layout that the
        spec requires for both narrow and wide viewports.

        ---
        """
    )
    return (mo,)


@app.cell
def _imports():
    import os
    from datetime import UTC, datetime, timedelta

    import altair as alt
    import duckdb
    import pandas as pd

    return UTC, alt, datetime, duckdb, os, pd, timedelta


@app.cell
def _allowlist_categories():
    """Read the curated allowlist once (shared across cells)."""
    from dlt_sources.official_media.allowlist import allowlist_filter

    return (allowlist_filter.categories(),)


@app.cell
def _data_loading(mo, duckdb, os, pd, allowlist_categories):
    """Load the sentiment + moderation data from the lakehouse (or
    fall back to a synthetic dataset derived from the 4 allowlist
    YAML fixtures)."""
    sentiment_df = None
    db_label = ""
    fallback_used = False

    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    use_md = os.environ.get("MOTHERDUCK_ENABLED", "false").lower() == "true"

    if use_md and token:
        try:
            duckdb.sql(f"SET motherduck_token='{token}'")
            con = ibis.duckdb.connect("md:cianfhoghlaim")
            sentiment_df = con.execute(
                """
                SELECT ig_username, category, posted_at, sentiment_score,
                       moderation_flag, engagement_likes
                FROM cianfhoghlaim.official_media.sentiment_scores
                ORDER BY posted_at DESC
                LIMIT 5000
                """
            ).fetchdf()
            con.close()
            db_label = "md:cianfhoghlaim (live MotherDuck + DuckLake)"
        except Exception as exc:  # noqa: BLE001
            db_label = f"md:cianfhoghlaim — query failed ({exc!s:.60s})"
            sentiment_df = None

    if sentiment_df is None:
        # Per-category sentiment bias (hand-tuned for realism)
        cat_bias = {
            "intelligence": 0.10,
            "university": 0.45,
            "party": -0.20,
            "jurisdiction": 0.15,
            "agency": 0.05,
            "emergency_service": -0.05,
            "military": 0.00,
            "government": 0.05,
        }
        _flag_types = (
            "verified_only",
            "engagement_bait",
            "advocacy",
            "polarising_topic",
            "breaking_news",
        )
        _rows: list[dict] = []
        _rng_seed = 0
        _now = datetime.now(UTC)
        for cat, usernames in allowlist_categories.items():
            _bias = cat_bias.get(cat, 0.0)
            for uname in usernames:
                # 8–18 posts per profile over the last 30 days
                _n_posts = 8 + (sum(ord(c) for c in uname) % 11)
                for _ in range(_n_posts):
                    _rng_seed = (_rng_seed + 1) % 997
                    _ts = _now - timedelta(
                        days=(_rng_seed % 30),
                        hours=(_rng_seed * 7) % 24,
                        minutes=(_rng_seed * 13) % 60,
                    )
                    _sentiment = max(
                        -1.0,
                        min(1.0, _bias + ((_rng_seed * 17) % 200 - 100) / 200.0),
                    )
                    _flag = _flag_types[_rng_seed % len(_flag_types)] if _rng_seed % 4 == 0 else None
                    _rows.append(
                        {
                            "ig_username": uname,
                            "category": cat,
                            "posted_at": _ts,
                            "sentiment_score": round(_sentiment, 3),
                            "moderation_flag": _flag,
                            "engagement_likes": 50 + (_rng_seed * 37) % 5000,
                        }
                    )
        sentiment_df = pd.DataFrame(_rows).sort_values("posted_at", ascending=False)
        fallback_used = True
        db_label = "synthetic (allowlist-derived sentiment + flags)"

    summary = {
        "db_label": db_label,
        "n_rows": len(sentiment_df),
        "mean_sentiment": round(float(sentiment_df["sentiment_score"].mean()), 3),
        "n_flagged": int(sentiment_df["moderation_flag"].notna().sum()),
        "fallback_used": fallback_used,
    }
    mo.md(
        f"""
        **Database**: `{summary['db_label']}`
        **Rows**: {summary['n_rows']}  |  **Mean sentiment**: {summary['mean_sentiment']}
        **Flagged posts**: {summary['n_flagged']}
        **Fallback**: {summary['fallback_used']}
        """
    )
    return db_label, fallback_used, sentiment_df, summary


@app.cell
def _tab_layout(mo, sentiment_df, alt, pd):
    """R5 — Multi-column tab layout. The spec requires that
    ``mo.ui.tabs({...})`` renders correctly on both narrow and wide
    viewports. The four tabs each contain one of the four panels."""

    # --- Tab 1: Sentiment over time --------------------------------------
    _sentiment_df = sentiment_df.copy()
    _sentiment_df["date"] = pd.to_datetime(_sentiment_df["posted_at"]).dt.date
    daily = (
        _sentiment_df.groupby("date", as_index=False)["sentiment_score"]
        .mean()
        .rename(columns={"sentiment_score": "mean_sentiment"})
    )
    tab1_chart = (
        alt.Chart(daily)
        .mark_line(strokeWidth=2)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y(
                "mean_sentiment:Q",
                title="Mean sentiment (−1 negative, +1 positive)",
                scale=alt.Scale(domain=[-1, 1]),
            ),
            tooltip=["date:T", "mean_sentiment:Q"],
        )
        .properties(
            width=620,
            height=320,
            title="Panel A — Sentiment over time (smoothed mean)",
        )
    )
    tab1 = mo.vstack(
        [
            mo.md("### Sentiment over time"),
            mo.ui.altair_chart(tab1_chart),
        ]
    )

    # --- Tab 2: Moderation flags ----------------------------------------
    flagged = (
        _sentiment_df[_sentiment_df["moderation_flag"].notna()]
        .groupby("moderation_flag", as_index=False)
        .size()
        .rename(columns={"size": "n_posts"})
        .sort_values("n_posts", ascending=False)
    )
    tab2_chart = (
        alt.Chart(flagged)
        .mark_bar()
        .encode(
            x=alt.X("n_posts:Q", title="Flagged posts"),
            y=alt.Y("moderation_flag:N", sort="-x", title="Flag type"),
            color=alt.Color("moderation_flag:N", legend=None),
            tooltip=["moderation_flag", "n_posts"],
        )
        .properties(
            width=620,
            height=320,
            title="Panel B — Moderation flag distribution",
        )
    )
    tab2 = mo.vstack(
        [
            mo.md("### Moderation flags"),
            mo.ui.altair_chart(tab2_chart),
        ]
    )

    # --- Tab 3: Sentiment by category -----------------------------------
    by_cat = (
        _sentiment_df.assign(
            bucket=lambda d: pd.cut(
                d["sentiment_score"],
                bins=[-1.0, -0.3, 0.3, 1.0],
                labels=["negative", "neutral", "positive"],
            )
        )
        .groupby(["category", "bucket"], as_index=False)
        .size()
        .rename(columns={"size": "n_posts"})
    )
    tab3_chart = (
        alt.Chart(by_cat)
        .mark_bar()
        .encode(
            x=alt.X("n_posts:Q", title="Posts", stack="normalize"),
            y=alt.Y("category:N", title="Official-media category"),
            color=alt.Color("bucket:N", title="Sentiment bucket"),
            tooltip=["category", "bucket", "n_posts"],
        )
        .properties(
            width=620,
            height=320,
            title="Panel C — Sentiment distribution per category",
        )
    )
    tab3 = mo.vstack(
        [
            mo.md("### Sentiment by category"),
            mo.ui.altair_chart(tab3_chart),
        ]
    )

    # --- Tab 4: BAML extractor -----------------------------------------
    baml_result: dict = {"status": "skipped", "reason": "no candidate available"}
    decision_obj = None
    target_username = None
    try:
        from cianfhoghlaim.baml_client import b

        if len(_sentiment_df) > 0:
            target_username = (
                _sentiment_df.sort_values("engagement_likes", ascending=True)
                .iloc[0]["ig_username"]
            )
            decision_obj = b.ClassifyOfficialMedia(
                ig_username=target_username,
                ig_bio=(
                    f"Synthetic bio for {target_username} — flagged "
                    "for engagement-bait content."
                ),
                ig_external_url="https://www.gov.uk",
            )
            baml_result = {
                "status": "ok",
                "ig_username": target_username,
                "is_official_media": decision_obj.is_official_media,
                "confidence": decision_obj.confidence,
                "category": decision_obj.category,
                "reason": decision_obj.reason,
            }
    except Exception as exc:  # noqa: BLE001
        baml_result = {"status": "failed", "error": str(exc)[:200]}
    tab4 = mo.vstack(
        [
            mo.md("### BAML extractor sample"),
            mo.md(f"```json\n{baml_result!s}\n```"),
        ]
    )

    # The R5 multi-column tab layout (Streamlit-compatible)
    tabs = mo.ui.tabs(
        {
            "Sentiment over time": tab1,
            "Moderation flags": tab2,
            "Sentiment by category": tab3,
            "BAML extractor": tab4,
        }
    )
    tabs
    return (
        baml_result,
        by_cat,
        daily,
        decision_obj,
        flagged,
        tab1,
        tab1_chart,
        tab2,
        tab2_chart,
        tab3,
        tab3_chart,
        tab4,
        tabs,
    )


@app.cell
def _(mo):
    mo.md(
        r"""
        ---

        ## ✊ Why we built this

        The content-moderation + sentiment view is the *normative*
        half of the official-media mission control. R1–R4 are
        **descriptive** (who, what, where, when) — R5 is
        **normative** (is this content within the British Isles
        regulatory lineage: UK GDPR, the Online Safety Act, the
        Irish Broadcasting Act 2009, the EU Digital Services Act).

        The ``mo.ui.tabs({...})`` layout is required by R5 — it
        must render correctly on both narrow (mobile) and wide
        (desktop) viewports. The 4 tabs map to the 4 panels:
        sentiment over time, moderation flags, sentiment by
        category, and the BAML extractor.

        See ``openspec/specs/official-media-marimo/spec.md`` (R5) for
        the Streamlit-compatible layout contract and
        ``openspec/changes/archive/2026-06-18-official-media-pipeline/proposal.md``
        for the regulatory-lineage rationale.
        """
    )
    return


if __name__ == "__main__":
    app.run()
