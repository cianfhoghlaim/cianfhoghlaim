"""Aleyum GitHub Insights Dashboard.

Interactive Marimo notebook for exploring GitHub repository data.
Visualizes languages, commits, and project activity.

Run with: marimo run notebooks/github_insights.py
"""

import marimo

__generated_with = "0.17.2"
app = marimo.App(width="full")


@app.cell
def imports():
    """Import dependencies."""
    import marimo as mo
    import ibis
    import altair as alt
    import polars as pl
    from pathlib import Path
    from datetime import datetime

    alt.data_transformers.enable("vegafusion")

    return mo, ibis, alt, pl, Path, datetime


@app.cell
def database_connection(mo, ibis, Path):
    """Connect to the portfolio DuckDB database."""
    db_path = Path("./data/aleyum.duckdb")

    if not db_path.exists():
        mo.md("""
        ## Database Not Found

        Run the GitHub pipeline first:

        ```bash
        python -m pipelines.github.source
        ```
        """)
        conn = None
    else:
        conn = ibis.duckdb.connect(str(db_path))
        mo.md(f"**Connected to:** `{db_path}`")

    return conn, db_path


@app.cell
def repositories_overview(mo, conn, pl):
    """Overview of repositories."""
    if conn is None or "github_data_repositories" not in conn.list_tables():
        return mo.md("GitHub repositories not loaded yet")

    repos = conn.table("github_data_repositories").to_polars()

    # Calculate stats
    total_repos = len(repos)
    total_stars = repos["stargazers_count"].sum() if "stargazers_count" in repos.columns else 0
    total_forks = repos["forks_count"].sum() if "forks_count" in repos.columns else 0

    mo.md(f"""
    ## GitHub Repositories Overview

    | Metric | Value |
    |--------|-------|
    | **Total Repositories** | {total_repos} |
    | **Total Stars** | {total_stars:,} |
    | **Total Forks** | {total_forks:,} |
    """)

    return (repos,)


@app.cell
def repos_table(mo, repos, pl):
    """Interactive repositories table."""
    if repos is None or len(repos) == 0:
        return mo.md("No repositories found")

    # Select relevant columns
    display_cols = [
        "name",
        "description",
        "language",
        "stargazers_count",
        "forks_count",
        "updated_at",
    ]
    available_cols = [c for c in display_cols if c in repos.columns]

    repos_display = repos.select(available_cols).sort("stargazers_count", descending=True)

    table = mo.ui.table(
        repos_display.to_pandas(),
        selection="single",
        label="Select a repository to view details",
    )

    return (table,)


@app.cell
def language_distribution(mo, conn, alt, pl):
    """Language distribution across all repositories."""
    if conn is None or "github_data_repository_languages" not in conn.list_tables():
        # Fall back to primary language from repos
        if "repos" in dir() and repos is not None and "language" in repos.columns:
            lang_counts = repos.group_by("language").count().sort("count", descending=True)

            chart = (
                alt.Chart(lang_counts.to_pandas())
                .mark_arc(innerRadius=50)
                .encode(
                    theta=alt.Theta("count:Q"),
                    color=alt.Color("language:N", legend=alt.Legend(title="Language")),
                    tooltip=["language", "count"],
                )
                .properties(
                    title="Primary Languages by Repository Count",
                    width=400,
                    height=400,
                )
            )

            return mo.ui.altair_chart(chart)
        return mo.md("Language data not available. Run pipeline with `fetch_languages=True`")

    # Use detailed language breakdown
    languages = conn.table("github_data_repository_languages").to_polars()

    # Aggregate by language
    lang_totals = (
        languages.group_by("language")
        .agg(
            pl.col("bytes").sum().alias("total_bytes"),
            pl.col("repo_name").n_unique().alias("repo_count"),
        )
        .sort("total_bytes", descending=True)
    )

    # Convert bytes to MB for readability
    lang_totals = lang_totals.with_columns((pl.col("total_bytes") / 1_000_000).alias("megabytes"))

    chart = (
        alt.Chart(lang_totals.head(10).to_pandas())
        .mark_bar()
        .encode(
            x=alt.X("megabytes:Q", title="Total Code (MB)"),
            y=alt.Y("language:N", title="Language", sort="-x"),
            color=alt.Color("language:N", legend=None),
            tooltip=["language", alt.Tooltip("megabytes:Q", format=".2f"), "repo_count"],
        )
        .properties(
            title="Top 10 Languages by Code Volume",
            width=600,
            height=350,
        )
    )

    mo.ui.altair_chart(chart)

    return languages, chart


@app.cell
def commit_activity(mo, conn, alt, pl, datetime):
    """Commit activity over time."""
    if conn is None or "github_data_recent_commits" not in conn.list_tables():
        return mo.md("Commit data not available. Run pipeline with `fetch_commits=True`")

    commits = conn.table("github_data_recent_commits").to_polars()

    if len(commits) == 0:
        return mo.md("No commits found")

    # Parse dates and group by week
    commits = commits.with_columns(pl.col("authored_date").str.to_datetime().alias("date"))

    # Group by week
    commits_by_week = (
        commits.with_columns(pl.col("date").dt.truncate("1w").alias("week"))
        .group_by("week")
        .count()
        .sort("week")
    )

    chart = (
        alt.Chart(commits_by_week.to_pandas())
        .mark_area(
            line={"color": "#4a90d9"},
            color=alt.Gradient(
                gradient="linear",
                stops=[
                    alt.GradientStop(color="#4a90d9", offset=0),
                    alt.GradientStop(color="#4a90d920", offset=1),
                ],
                x1=1,
                x2=1,
                y1=1,
                y2=0,
            ),
        )
        .encode(
            x=alt.X("week:T", title="Week"),
            y=alt.Y("count:Q", title="Commits"),
            tooltip=["week:T", "count:Q"],
        )
        .properties(
            title="Commit Activity Over Time",
            width=700,
            height=250,
        )
    )

    mo.ui.altair_chart(chart)

    return commits, chart


@app.cell
def commits_by_repo(mo, commits, alt, pl):
    """Commits breakdown by repository."""
    if commits is None or len(commits) == 0:
        return mo.md("No commit data")

    commits_per_repo = commits.group_by("repo_name").count().sort("count", descending=True)

    chart = (
        alt.Chart(commits_per_repo.to_pandas())
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title="Commits (last 90 days)"),
            y=alt.Y("repo_name:N", title="Repository", sort="-x"),
            color=alt.Color("count:Q", scale=alt.Scale(scheme="greens"), legend=None),
            tooltip=["repo_name", "count"],
        )
        .properties(
            title="Recent Commits by Repository",
            width=600,
            height=max(200, len(commits_per_repo) * 25),
        )
    )

    mo.ui.altair_chart(chart)

    return (commits_per_repo,)


@app.cell
def readme_previews(mo, conn):
    """README content previews."""
    if conn is None or "github_data_repository_readmes" not in conn.list_tables():
        return mo.md("README data not available. Run pipeline with `fetch_readmes=True`")

    readmes = conn.table("github_data_repository_readmes").to_polars()

    if len(readmes) == 0:
        return mo.md("No READMEs found")

    # Create dropdown to select repo
    repo_options = {row["repo_name"]: row["repo_name"] for row in readmes.to_dicts()}

    selector = mo.ui.dropdown(
        options=repo_options,
        label="Select repository to view README",
    )

    return readmes, selector


@app.cell
def readme_display(mo, selector, readmes, pl):
    """Display selected README."""
    if selector.value is None:
        return mo.md("Select a repository above")

    readme = readmes.filter(pl.col("repo_name") == selector.value).to_dicts()

    if not readme:
        return mo.md("README not found")

    content = readme[0].get("readme_content", "")

    # Truncate if too long
    if len(content) > 3000:
        content = content[:3000] + "\n\n... (truncated)"

    return mo.md(f"""
    ## {selector.value} README

    ---

    {content}
    """)


@app.cell
def featured_projects(mo, repos, pl):
    """Highlight featured projects for portfolio."""
    if repos is None:
        return mo.md("No repository data")

    # Define featured repos (could be loaded from config)
    featured_names = ["Portfolio"]  # Add more as needed

    featured = repos.filter(pl.col("name").is_in(featured_names))

    if len(featured) == 0:
        # Fall back to top starred repos
        featured = repos.sort("stargazers_count", descending=True).head(5)

    mo.md("""
    ## Featured Projects

    Projects highlighted for the portfolio:
    """)

    for repo in featured.to_dicts():
        mo.md(f"""
        ### {repo.get("name", "Unknown")}

        {repo.get("description", "No description")}

        - **Language:** {repo.get("language", "N/A")}
        - **Stars:** {repo.get("stargazers_count", 0)}
        - **URL:** [{repo.get("html_url", "")}]({repo.get("html_url", "")})
        """)

    return (featured,)


@app.cell
def technology_stack(mo, languages, pl):
    """Summarize technology stack."""
    if languages is None:
        return mo.md("Language data not available")

    # Get top languages
    top_langs = (
        languages.group_by("language")
        .agg(pl.col("bytes").sum().alias("total_bytes"))
        .sort("total_bytes", descending=True)
        .head(10)
    )

    lang_list = top_langs["language"].to_list()

    mo.md(f"""
    ## Technology Stack

    Primary languages used across repositories:

    {", ".join(f"**{lang}**" for lang in lang_list)}

    This demonstrates proficiency in:
    - **Backend:** Python, JavaScript/TypeScript
    - **Data:** SQL, Python data libraries
    - **Web:** HTML, CSS, JavaScript frameworks
    """)

    return (lang_list,)


@app.cell
def export_for_portfolio(mo, repos, commits, languages):
    """Export data for portfolio website."""
    mo.md("""
    ## Export for Portfolio

    Generate JSON data for the web application:
    """)

    def generate_portfolio_json():
        import json

        output = {
            "repositories": [],
            "languages": {},
            "stats": {},
        }

        if repos is not None:
            output["repositories"] = repos.to_dicts()
            output["stats"]["total_repos"] = len(repos)
            output["stats"]["total_stars"] = (
                repos["stargazers_count"].sum() if "stargazers_count" in repos.columns else 0
            )

        if languages is not None:
            lang_totals = languages.group_by("language").agg(pl.col("bytes").sum()).to_dicts()
            output["languages"] = {l["language"]: l["bytes"] for l in lang_totals}

        if commits is not None:
            output["stats"]["recent_commits"] = len(commits)

        return json.dumps(output, indent=2, default=str)

    export_btn = mo.ui.button(
        label="Export GitHub Data",
        on_click=lambda _: mo.download(
            generate_portfolio_json().encode(), filename="github_data.json"
        ),
    )

    return (export_btn,)


if __name__ == "__main__":
    app.run()
