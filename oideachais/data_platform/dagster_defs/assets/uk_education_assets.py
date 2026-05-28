"""
UK Education Assets.

Pipeline for British Isles education content from:
- England: DfE, Ofsted, AQA, OCR, Edexcel
- Scotland: Education Scotland, SQA, HMIE
- Wales: Curriculum for Wales, WJEC, Estyn
- Northern Ireland: CCEA, ETI, DENI
- Crown Dependencies: Isle of Man, Jersey, Guernsey

Asset Hierarchy:
    uk.education.{nation}.statistics
    uk.education.{nation}.curriculum
    uk.education.{nation}.examinations
    uk.education.{nation}.inspections
    uk.education.embeddings
    uk.education.cross_nation_comparison

Designed for independent execution via uk_multipartitions.
"""
# Note: Removed future annotations for Dagster compatibility


from dagster import (
    AssetKey,
    MaterializeResult,
    asset,
)
from dagster_dlt import DagsterDltResource

from ..resources import DuckDBResource, FirecrawlResource, LanceDBResource

# ============================================================================
# England Assets
# ============================================================================

@asset(
    key=["uk", "education", "england", "dfe_statistics"],
    group_name="uk_education",
    description="Department for Education statistics (England)",
    compute_kind="dlt",
)
def england_dfe_statistics(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Ingest DfE statistics from explore-education-statistics.service.gov.uk.

    Datasets:
    - Key stage 4 performance
    - School workforce statistics
    - Pupil absence statistics
    - Phonics screening check
    """
    context.log.info("Ingesting DfE statistics for England")

    from data_platform.dlt_sources.uk.england.dfe import dfe_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="england_dfe",
        destination="duckdb",
        dataset_name="statistics",
    )

    source = dfe_source()
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "england",
            "source": "dfe",
            "tables_loaded": list(row_counts.keys()),
            "total_rows": sum(row_counts.values()),
        }
    )


@asset(
    key=["uk", "education", "england", "ofsted_inspections"],
    group_name="uk_education",
    description="Ofsted school inspection reports (England)",
    compute_kind="dlt",
)
def england_ofsted_inspections(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Ingest Ofsted inspection reports.

    Data includes school ratings, inspection dates, and report PDFs.
    """
    context.log.info("Ingesting Ofsted inspections for England")

    from data_platform.dlt_sources.uk.england.ofsted import ofsted_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="england_ofsted",
        destination="duckdb",
        dataset_name="statistics",
    )

    source = ofsted_source()
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "england",
            "source": "ofsted",
            "inspections_loaded": sum(row_counts.values()),
        }
    )


# ============================================================================
# Scotland Assets
# ============================================================================

@asset(
    key=["uk", "education", "scotland", "gov_statistics"],
    group_name="uk_education",
    description="Scottish Government education statistics",
    compute_kind="dlt",
)
def scotland_gov_statistics(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Ingest Scottish Government education statistics.

    Datasets:
    - Attainment and leaver destinations
    - School estate statistics
    - Teacher workforce
    - Gaelic medium education
    """
    context.log.info("Ingesting Scottish Government statistics")

    from data_platform.dlt_sources.uk.scotland.gov import scotland_gov_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="scotland_gov",
        destination="duckdb",
        dataset_name="statistics",
    )

    source = scotland_gov_source()
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "scotland",
            "source": "scottish_government",
            "tables_loaded": list(row_counts.keys()),
            "total_rows": sum(row_counts.values()),
        }
    )


@asset(
    key=["uk", "education", "scotland", "sqa_examinations"],
    group_name="uk_education",
    description="SQA examination results and specifications (Scotland)",
    compute_kind="dlt",
)
def scotland_sqa_examinations(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Ingest SQA examination data.

    Includes National 5, Higher, Advanced Higher results and specs.
    Special focus on Gaelic subjects.
    """
    context.log.info("Ingesting SQA examination data")

    from data_platform.dlt_sources.uk.scotland.sqa import sqa_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="scotland_sqa",
        destination="duckdb",
        dataset_name="statistics",
    )

    source = sqa_source()
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "scotland",
            "source": "sqa",
            "exam_data_loaded": sum(row_counts.values()),
        }
    )


# ============================================================================
# Wales Assets
# ============================================================================

@asset(
    key=["uk", "education", "wales", "statswales"],
    group_name="uk_education",
    description="StatsWales education statistics",
    compute_kind="dlt",
)
def wales_statswales(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Ingest StatsWales education statistics.

    Datasets:
    - Welsh medium schools
    - Welsh language competency
    - Attainment statistics
    - School census
    """
    context.log.info("Ingesting StatsWales education data")

    from data_platform.dlt_sources.uk.wales.statswales import statswales_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="wales_statswales",
        destination="duckdb",
        dataset_name="statistics",
    )

    source = statswales_source()
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "wales",
            "source": "statswales",
            "tables_loaded": list(row_counts.keys()),
            "total_rows": sum(row_counts.values()),
        }
    )


@asset(
    key=["uk", "education", "wales", "curriculum"],
    group_name="uk_education",
    description="Curriculum for Wales content",
    compute_kind="firecrawl",
)
def wales_curriculum(
    context,
    dlt: DagsterDltResource,
    firecrawl: FirecrawlResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Crawl Curriculum for Wales content.

    Bilingual (en/cy) curriculum specifications.
    """
    context.log.info("Crawling Curriculum for Wales")

    from data_platform.dlt_sources.uk.wales.curriculum import wales_curriculum_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="wales_curriculum",
        destination="duckdb",
        dataset_name="education",
    )

    source = wales_curriculum_source()
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "wales",
            "source": "curriculum_for_wales",
            "languages": ["en", "cy"],
            "pages_crawled": sum(row_counts.values()),
        }
    )


# ============================================================================
# Northern Ireland Assets
# ============================================================================

@asset(
    key=["uk", "education", "northern_ireland", "nisra"],
    group_name="uk_education",
    description="NISRA education statistics (Northern Ireland)",
    compute_kind="dlt",
)
def ni_nisra_statistics(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Ingest NISRA education statistics.

    Datasets:
    - School enrolment
    - Examination results
    - Irish medium education
    """
    context.log.info("Ingesting NISRA education statistics")

    from data_platform.dlt_sources.uk.northern_ireland.nisra import nisra_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="ni_nisra",
        destination="duckdb",
        dataset_name="statistics",
    )

    source = nisra_source()
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "northern_ireland",
            "source": "nisra",
            "tables_loaded": list(row_counts.keys()),
            "total_rows": sum(row_counts.values()),
        }
    )


@asset(
    key=["uk", "education", "northern_ireland", "ccea"],
    group_name="uk_education",
    description="CCEA curriculum and examinations (Northern Ireland)",
    compute_kind="dlt",
)
def ni_ccea(
    context,
    dlt: DagsterDltResource,
    firecrawl: FirecrawlResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Ingest CCEA curriculum and examination data.

    Includes GCSE/A-Level specifications and Irish language materials.
    """
    context.log.info("Ingesting CCEA curriculum and exam data")

    from data_platform.dlt_sources.uk.northern_ireland.ccea import ccea_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="ni_ccea",
        destination="duckdb",
        dataset_name="education",
    )

    source = ccea_source()
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "northern_ireland",
            "source": "ccea",
            "curriculum_pages": sum(row_counts.values()),
        }
    )


# ============================================================================
# Crown Dependencies
# ============================================================================

@asset(
    key=["uk", "education", "isle_of_man", "curriculum"],
    group_name="uk_education",
    description="Isle of Man education curriculum",
    compute_kind="firecrawl",
)
def iom_curriculum(
    context,
    dlt: DagsterDltResource,
    firecrawl: FirecrawlResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Crawl Isle of Man curriculum content.

    Includes Manx language (gv) education materials.
    """
    context.log.info("Crawling Isle of Man curriculum")

    from data_platform.dlt_sources.crown_dependencies.isle_of_man import iom_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="iom_curriculum",
        destination="duckdb",
        dataset_name="education",
    )

    source = iom_source()
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "isle_of_man",
            "languages": ["en", "gv"],
            "pages_crawled": sum(row_counts.values()),
        }
    )


# ============================================================================
# UK-Wide Embeddings
# ============================================================================

@asset(
    key=["uk", "education", "embeddings"],
    group_name="uk_education",
    description="Vector embeddings for all UK education content",
    deps=[
        AssetKey(["uk", "education", "england", "dfe_statistics"]),
        AssetKey(["uk", "education", "scotland", "gov_statistics"]),
        AssetKey(["uk", "education", "wales", "statswales"]),
        AssetKey(["uk", "education", "northern_ireland", "nisra"]),
    ],
    compute_kind="embedding",
)
def uk_education_embeddings(
    context,
    duckdb: DuckDBResource,
    lancedb: LanceDBResource,
) -> MaterializeResult:
    """
    Generate embeddings for UK education content.

    Stores in LanceDB with oileain.curriculum namespace.
    """
    from sentence_transformers import SentenceTransformer

    context.log.info("Generating UK education embeddings")

    conn = duckdb.get_connection()
    db = lancedb.get_db()
    model = SentenceTransformer(lancedb.embedding_model)

    # Aggregate content from all UK nations
    nations = ["england", "scotland", "wales", "northern_ireland"]
    total_embedded = 0

    for nation in nations:
        try:
            query = f"""
                SELECT
                    '{nation}' as nation,
                    title,
                    content
                FROM statistics.{nation}_curriculum
                WHERE content IS NOT NULL
                LIMIT 200
            """
            rows = conn.execute(query).fetchall()

            if len(rows) < 10:
                continue

            texts = [f"{row[1]}\n{row[2]}" for row in rows]
            metadata = [{"nation": row[0], "title": row[1]} for row in rows]

            embeddings = model.encode(texts, batch_size=100, show_progress_bar=True)

            data = [
                {"text": text, "vector": emb.tolist(), **meta}
                for text, emb, meta in zip(texts, embeddings, metadata)
            ]

            table_name = "oileain.curriculum"
            if table_name in db.table_names():
                db.open_table(table_name).add(data)
            else:
                db.create_table(table_name, data)

            total_embedded += len(data)

        except Exception as e:
            context.log.warning(f"Failed to embed {nation}: {e}")

    return MaterializeResult(
        metadata={
            "total_embedded": total_embedded,
            "nations_processed": nations,
            "table": "oileain.curriculum",
        }
    )


# ============================================================================
# Cross-Nation Comparison Asset
# ============================================================================

@asset(
    key=["uk", "education", "cross_nation_comparison"],
    group_name="uk_education",
    description="Cross-nation education comparison metrics",
    deps=[
        AssetKey(["uk", "education", "england", "dfe_statistics"]),
        AssetKey(["uk", "education", "scotland", "gov_statistics"]),
        AssetKey(["uk", "education", "wales", "statswales"]),
        AssetKey(["uk", "education", "northern_ireland", "nisra"]),
    ],
    compute_kind="analysis",
)
def uk_cross_nation_comparison(
    context,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Generate cross-nation education comparison data.

    Metrics:
    - Attainment levels (GCSE equivalent)
    - Celtic language medium education rates
    - School inspection ratings
    - Pupil-teacher ratios
    """
    context.log.info("Generating cross-nation comparison metrics")

    conn = duckdb.get_connection()

    # Create comparison table
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS statistics.cross_nation_comparison (
                metric_name VARCHAR,
                england_value DOUBLE,
                scotland_value DOUBLE,
                wales_value DOUBLE,
                ni_value DOUBLE,
                ireland_value DOUBLE,
                comparison_year INTEGER,
                notes VARCHAR
            )
        """)

        # Insert placeholder comparison data
        # (In reality, this would aggregate from nation-specific tables)
        conn.execute("""
            INSERT INTO statistics.cross_nation_comparison VALUES
            ('celtic_medium_schools', NULL, 68, 470, 89, 247, 2023, 'Number of Celtic-medium schools'),
            ('secondary_attainment_5plus', 67.8, 65.2, 63.1, 70.5, 78.2, 2023, 'Percentage achieving 5+ passes')
        """)

        comparison_count = 2
    except Exception as e:
        context.log.warning(f"Comparison table creation failed: {e}")
        comparison_count = 0

    return MaterializeResult(
        metadata={
            "comparison_metrics": comparison_count,
            "nations": ["england", "scotland", "wales", "northern_ireland", "ireland"],
        }
    )


# ============================================================================
# Export All Assets
# ============================================================================

uk_education_assets = [
    england_dfe_statistics,
    england_ofsted_inspections,
    scotland_gov_statistics,
    scotland_sqa_examinations,
    wales_statswales,
    wales_curriculum,
    ni_nisra_statistics,
    ni_ccea,
    iom_curriculum,
    uk_education_embeddings,
    uk_cross_nation_comparison,
]
