# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""03 — Instagram + Mastodon post trends (official-media-marimo spec, R1).

Renders a 3-panel timeline of the official-media posts harvested from the
British Isles government / political / public-service / university /
emergency-services / intelligence-agency handles in the curated allowlist.

Three visualisations of the official-media post trends:

- **Panel A** — posts per day (line chart, stacked by platform)
- **Panel B** — posts per platform (bar chart, Instagram vs Mastodon vs Bluesky)
- **Panel C** — engagement heatmap by day-of-week × hour

Data source: ``md:cianfhoghlaim_official_media`` (MotherDuck + DuckLake lakehouse
table produced by the ``official_media_extract`` DLT pipeline). Falls back to
a synthetic dataset derived from the 4 allowlist YAML fixtures when the
lakehouse is unreachable — the same graceful-degradation pattern the
existing ``01_official_media.py`` notebook uses.

Reference: ``openspec/specs/official-media-marimo/spec.md`` — Requirement
"OfficialMediaMissionControl" + the temporal sub-requirement (the 3-panel
timeline section of the mission control).
"""
from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _intro():
    import marimo as mo

    mo.md(
        r"""
        # 📈 Official Media — Post Trends (R1, Mission Control timeline)

        3-panel trend visualisation for the British Isles government
        / political / public-service / university / emergency-services /
        intelligence-agency handles in the curated allowlist.

        Reads from ``md:cianfhoghlaim_official_media`` (the official-media
        DLT pipeline's MotherDuck + DuckLake landing zone). Falls back
        to a synthetic dataset when the lakehouse is unreachable.

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
    from pandas.api.types import CategoricalDtype

    return (
        UTC,
        CategoricalDtype,
        alt,
        datetime,
        duckdb,
        os,
        pd,
        timedelta,
    )


@app.cell
def _data_loading(mo, duckdb, os, pd, allowlist_categories):
    """Load the official-media posts from the lakehouse (or fall back to
    a synthetic dataset built from the 4 allowlist YAML fixtures)."""
    posts_df = None
    db_label = ""
    fallback_used = False

    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    use_md = os.environ.get("MOTHERDUCK_ENABLED", "false").lower() == "true"

    if use_md and token:
        try:
            duckdb.sql(f"SET motherduck_token='{token}'")
            con = ibis.duckdb.connect("md:cianfhoghlaim")
            posts_df = con.execute(
                """
                SELECT ig_username, category, platform, posted_at,
                       engagement_likes, engagement_shares, engagement_comments
                FROM cianfhoghlaim.official_media.posts
                ORDER BY posted_at DESC
                LIMIT 5000
                """
            ).fetchdf()
            con.close()
            db_label = "md:cianfhoghlaim (live MotherDuck + DuckLake)"
        except Exception as exc:  # noqa: BLE001
            db_label = f"md:cianfhoghlaim — query failed ({exc!s:.60s})"
            posts_df = None

    if posts_df is None:
        # Graceful fallback — synthesise a 30-day window of posts from
        # the 4 curated allowlist YAML fixtures. Deterministic seed so
        # the numbers are stable between runs.
        _rows: list[dict] = []
        _rng_seed = 0
        _now = datetime.now(UTC)
        _platforms = ("instagram", "mastodon", "bluesky")
        for cat, usernames in allowlist_categories.items():
            for uname in usernames:
                # 4–12 posts per profile over the last 30 days
                _n_posts = 4 + (sum(ord(c) for c in uname) % 9)
                for i in range(_n_posts):
                    _rng_seed = (_rng_seed + 1) % 997
                    ts = _now - timedelta(
                        days=(_rng_seed % 30),
                        hours=(_rng_seed * 7) % 24,
                        minutes=(_rng_seed * 13) % 60,
                    )
                    _rows.append(
                        {
                            "ig_username": uname,
                            "category": cat,
                            "platform": _platforms[_rng_seed % 3],
                            "posted_at": ts,
                            "engagement_likes": 50 + (_rng_seed * 37) % 5000,
                            "engagement_shares": 5 + (_rng_seed * 11) % 500,
                            "engagement_comments": 1 + (_rng_seed * 5) % 200,
                        }
                    )
        posts_df = pd.DataFrame(_rows).sort_values("posted_at", ascending=False)
        fallback_used = True
        db_label = "synthetic (allowlist-derived, 30-day window)"

    summary = {
        "db_label": db_label,
        "n_rows": len(posts_df),
        "n_platforms": int(posts_df["platform"].nunique()),
        "n_categories": int(posts_df["category"].nunique()),
        "fallback_used": fallback_used,
    }
    mo.md(
        f"""
        **Database**: `{summary['db_label']}`
        **Rows**: {summary['n_rows']}  |  **Platforms**: {summary['n_platforms']}
        **Categories**: {summary['n_categories']}  |  **Fallback**: {summary['fallback_used']}
        """
    )
    return db_label, fallback_used, posts_df, summary


@app.cell
def _allowlist_categories():
    """Read the curated allowlist once (shared across cells)."""
    from dlt_sources.official_media.allowlist import allowlist_filter

    return (allowlist_filter.categories(),)


@app.cell
def _viz_posts_per_day(alt, mo, posts_df):
    """Panel A — posts per day, stacked by platform."""
    daily = (
        posts_df.assign(date=posts_df["posted_at"].dt.date)
        .groupby(["date", "platform"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )

    _chart_a = (
        alt.Chart(daily)
        .mark_area(opacity=0.65)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("count:Q", title="Posts / day", stack=True),
            color=alt.Color("platform:N", title="Platform"),
            tooltip=["date:T", "platform:N", "count:Q"],
        )
        .properties(
            width=620,
            height=280,
            title="Panel A — Posts per day (stacked by platform)",
        )
        .interactive()
    )
    mo.ui.altair_chart(_chart_a)
    return _chart_a, daily


@app.cell
def _viz_posts_per_platform(alt, mo, posts_df):
    """Panel B — posts per platform (bar chart, Instagram vs Mastodon vs other)."""
    by_platform = (
        posts_df.groupby("platform", as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )

    _chart_b = (
        alt.Chart(by_platform)
        .mark_bar()
        .encode(
            x=alt.X("platform:N", title="Platform", sort="-y"),
            y=alt.Y("count:Q", title="Total posts (30-day window)"),
            color=alt.Color("platform:N", legend=None),
            tooltip=["platform:N", "count:Q"],
        )
        .properties(
            width=620,
            height=240,
            title="Panel B — Total posts by platform",
        )
    )
    mo.ui.altair_chart(_chart_b)
    return _chart_b, by_platform


@app.cell
def _viz_engagement_heatmap(alt, mo, posts_df, pd, CategoricalDtype):
    """Panel C — engagement heatmap by day-of-week × hour-of-day."""
    heat = posts_df.assign(
        dow=posts_df["posted_at"].dt.day_name(),
        hour=posts_df["posted_at"].dt.hour,
    )
    dow_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    heat["dow"] = heat["dow"].astype(
        CategoricalDtype(categories=dow_order, ordered=True)
    )
    pivot = (
        heat.groupby(["dow", "hour"], as_index=False)["engagement_likes"]
        .sum()
        .rename(columns={"engagement_likes": "likes"})
    )

    _chart_c = (
        alt.Chart(pivot)
        .mark_rect()
        .encode(
            x=alt.X("hour:O", title="Hour of day (UTC)"),
            y=alt.Y("dow:O", title="Day of week", sort=dow_order),
            color=alt.Color(
                "likes:Q",
                scale=alt.Scale(scheme="tealblues"),
                title="Total likes",
            ),
            tooltip=["dow", "hour", "likes"],
        )
        .properties(
            width=620,
            height=240,
            title="Panel C — Engagement heatmap (day-of-week × hour)",
        )
    )
    mo.ui.altair_chart(_chart_c)
    return _chart_c, heat, pivot


@app.cell
def _baml_extractor(mo, posts_df):
    """Invoke the BAML `ClassifyOfficialMedia` fallback on a sampled
    profile. Demonstrates the BAML wiring required by the spec (R1's
    "verified via BAML ClassifyOfficialMedia extraction" clause)."""
    baml_result: dict = {"status": "skipped", "reason": "no candidate available"}
    decision_obj = None
    target_username = None

    try:
        from cianfhoghlaim.baml_client import b

        if len(posts_df) > 0:
            # Pick the lowest-engagement profile (most likely to be
            # ambiguous) and run it through the BAML classifier.
            target_username = (
                posts_df.groupby("ig_username", as_index=False)["engagement_likes"]
                .sum()
                .sort_values("engagement_likes")
                .iloc[0]["ig_username"]
            )
            decision_obj = b.ClassifyOfficialMedia(
                ig_username=target_username,
                ig_bio=(
                    f"Synthetic bio for {target_username} — official "
                    "government / university handle."
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

    mo.md(
        f"""
        ## 🔬 BAML extractor sample

        ```json
        {baml_result!s}
        ```

        The BAML `ClassifyOfficialMedia` function is the Stage-2
        fallback classifier — invoked when an Instagram handle is not
        in the curated 4-allowlist set but its bio + external URL
        "look official" (verified badge, ``.gov``/``.ie``/``.uk``/``.ac``
        in the URL, or keywords like "official", "department",
        "ministry", "police" in the bio).
        """
    )
    return baml_result, decision_obj, target_username


@app.cell
def _(mo):
    mo.md(
        r"""
        ---

        ## ✊ Why we built this

        The 3-panel timeline is the "what" half of the official-media
        mission control. The 4-panel mission control at
        ``09_official_media/01_official_media.py`` is the "how" — top
        metric strip + filterable table + skimmer + HMGCC sentinel.

        Together they answer: **which British-Isles government
        accounts are still posting on the deplatforming platforms,
        and how often?**

        See ``openspec/specs/official-media-marimo/spec.md`` (R1) and
        ``openspec/changes/archive/2026-06-18-official-media-pipeline/proposal.md``
        for the full design rationale.
        """
    )
    return


if __name__ == "__main__":
    app.run()
