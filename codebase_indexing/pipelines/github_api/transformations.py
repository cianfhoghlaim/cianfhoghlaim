"""GitHub API Data Transformations.

Uses dlthub transformations with ibis for data quality and metrics.
Follows patterns from small-data-sf-2025 elvis.ipynb example.

Requires: dlt license issue dlthub.transformation
"""

import typing

import dlt

# Note: These imports require the dlthub package with a valid license
# Run: dlt license issue dlthub.transformation
try:
    import ibis
    import ibis.expr.types as ir
    from dlthub import hub
    HAS_DLTHUB = True
except ImportError:
    HAS_DLTHUB = False
    ir = None


if HAS_DLTHUB:
    @dlt.hub.transformation
    def issue_stats_by_month(dataset: dlt.Dataset) -> typing.Iterator[ir.Table]:
        """Aggregate issue statistics by month.

        Creates monthly counts of issues created, closed, and average time to close.
        """
        issues = dataset.table("issues").to_ibis()

        # Extract year/month from created_at
        result = issues.mutate(
            year=issues.created_at.year(),
            month=issues.created_at.month(),
        ).group_by("year", "month").aggregate(
            total_issues=issues.id.count(),
            open_issues=issues.state.case().when("open", 1).else_(0).end().sum(),
            closed_issues=issues.state.case().when("closed", 1).else_(0).end().sum(),
        ).order_by(["year", "month"])

        yield result

    @dlt.hub.transformation
    def pr_review_metrics(dataset: dlt.Dataset) -> typing.Iterator[ir.Table]:
        """Calculate pull request review metrics.

        Analyzes PR lifecycle: time to first review, merge time, etc.
        """
        prs = dataset.table("pull_requests").to_ibis()

        # Monthly PR metrics
        result = prs.mutate(
            year=prs.created_at.year(),
            month=prs.created_at.month(),
        ).group_by("year", "month").aggregate(
            total_prs=prs.id.count(),
            merged_prs=prs.merged_at.notnull().sum(),
            avg_comments=prs.comments.mean(),
            avg_review_comments=prs.review_comments.mean(),
        ).order_by(["year", "month"])

        yield result

    @dlt.hub.transformation
    def commit_activity(dataset: dlt.Dataset) -> typing.Iterator[ir.Table]:
        """Analyze commit activity patterns.

        Groups commits by author and time period.
        """
        commits = dataset.table("commits").to_ibis()

        # Get author login from nested commit.author structure
        # Note: dlt normalizes nested objects, so we access the flattened column
        result = commits.group_by(
            author_login=commits.author__login,
        ).aggregate(
            total_commits=commits.sha.count(),
        ).order_by(ibis.desc("total_commits"))

        yield result

    @dlt.hub.transformation
    def workflow_success_rate(dataset: dlt.Dataset) -> typing.Iterator[ir.Table]:
        """Calculate CI/CD workflow success rates.

        Tracks success, failure, and cancellation rates by workflow.
        """
        runs = dataset.table("workflow_runs").to_ibis()

        result = runs.group_by("name").aggregate(
            total_runs=runs.id.count(),
            successful=runs.conclusion.case().when("success", 1).else_(0).end().sum(),
            failed=runs.conclusion.case().when("failure", 1).else_(0).end().sum(),
            cancelled=runs.conclusion.case().when("cancelled", 1).else_(0).end().sum(),
        ).mutate(
            success_rate=lambda t: t.successful / t.total_runs * 100,
        )

        yield result

    @dlt.hub.transformation
    def enrich_issues_with_labels(dataset: dlt.Dataset) -> typing.Iterator[ir.Table]:
        """Enrich issues with label information.

        Flattens the labels array and creates a searchable format.
        """
        issues = dataset.table("issues").to_ibis()

        # Select key fields for enriched issues table
        result = issues.select(
            "id",
            "number",
            "title",
            "state",
            "created_at",
            "updated_at",
            "user__login",
            "comments",
            # Body truncated for embedding
            body_preview=issues.body.substr(0, 500) if hasattr(issues, 'body') else None,
        )

        yield result


def create_analytics_source(dataset: dlt.Dataset) -> list:
    """Create a collection of analytics transformations.

    Args:
        dataset: DLT dataset to transform

    Returns:
        List of transformation resources
    """
    if not HAS_DLTHUB:
        raise RuntimeError(
            "dlthub package not available. "
            "Install with: pip install dlthub "
            "Then run: dlt license issue dlthub.transformation"
        )

    return [
        issue_stats_by_month(dataset),
        pr_review_metrics(dataset),
        commit_activity(dataset),
        workflow_success_rate(dataset),
    ]


def run_transformations(
    source_pipeline_name: str,
    destination: str = "duckdb",
    dataset_name: str = "github_analytics",
) -> typing.Any:
    """Run analytics transformations on existing GitHub data.

    Args:
        source_pipeline_name: Name of the pipeline containing raw GitHub data
        destination: DLT destination for analytics
        dataset_name: Name for the analytics dataset

    Returns:
        LoadInfo from transformation pipeline
    """
    if not HAS_DLTHUB:
        raise RuntimeError("dlthub package required for transformations")

    # Get the source dataset
    source_pipeline = dlt.pipeline(pipeline_name=source_pipeline_name)
    dataset = source_pipeline.dataset()

    # Create transformation pipeline
    transform_pipeline = dlt.pipeline(
        pipeline_name=f"{source_pipeline_name}_analytics",
        destination=destination,
        dataset_name=dataset_name,
    )

    # Run transformations
    analytics = create_analytics_source(dataset)
    load_info = transform_pipeline.run(analytics)

    print(load_info)
    return load_info
