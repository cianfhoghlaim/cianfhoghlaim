"""
Multi-Nation Curriculum Assets.

Pipeline for cross-nation curriculum ingestion, alignment, and comparison:
- Ireland: NCCA curriculum, SEC exams, Oide CPD
- England: National Curriculum, AQA/Edexcel/OCR exam boards
- Scotland: Curriculum for Excellence, SQA qualifications
- Wales: Curriculum for Wales, WJEC/CBAC
- Northern Ireland: NI Curriculum, CCEA

Asset Hierarchy:
    curriculum.{nation}.pages        - Raw crawled pages
    curriculum.{nation}.structured   - BAML-extracted structured data
    curriculum.unified.outcomes      - Normalized learning outcomes
    curriculum.unified.embeddings    - Vector embeddings for semantic search
    curriculum.unified.alignments    - Cross-nation outcome alignments

Critical Constraints:
    - DuckDB: Single-threaded only via SerialDatabaseExecutor
    - Embeddings: Batched (min 100) for performance
    - BAML: Schema validation required for extractions
"""

# Note: Removed future annotations for Dagster compatibility

from datetime import UTC, datetime

from dagster import (
    AssetKey,
    MaterializeResult,
    asset,
)
from dagster_dlt import DagsterDltResource

# ============================================================================
# Ireland Curriculum Assets
# ============================================================================


@asset(
    key=["curriculum", "ireland", "ncca_pages"],
    group_name="multi_nation_curriculum",
    description="NCCA curriculum specifications (Ireland)",
    compute_kind="firecrawl",
)
def ireland_ncca_curriculum(
    context,
    dlt: DagsterDltResource,
) -> MaterializeResult:
    """
    Crawl NCCA curriculum content from curriculumonline.ie and ncca.ie.

    Includes:
    - Primary curriculum
    - Junior Cycle specifications
    - Senior Cycle specifications
    - Irish (Gaeilge) medium content
    """
    context.log.info("Crawling NCCA curriculum content")

    from oideachais.data_platform.dlt_sources.ireland.ncca import ncca_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="ireland_ncca",
        destination="duckdb",
        dataset_name="curriculum",
    )

    # Crawl both English and Irish content
    for language in ["en", "ga"]:
        source = ncca_source(language=language)
        pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "ireland",
            "source": "ncca",
            "languages": ["en", "ga"],
            "pages_crawled": sum(row_counts.values()),
        }
    )


@asset(
    key=["curriculum", "ireland", "oide_pages"],
    group_name="multi_nation_curriculum",
    description="Oide CPD resources (Ireland)",
    compute_kind="firecrawl",
)
def ireland_oide_cpd(
    context,
    dlt: DagsterDltResource,
) -> MaterializeResult:
    """
    Crawl Oide.ie CPD (Continuing Professional Development) resources.

    Includes:
    - Primary subject resources
    - Post-primary Junior Cycle resources
    - Post-primary Senior Cycle resources
    - Irish medium teaching resources
    """
    context.log.info("Crawling Oide CPD resources")

    from oideachais.data_platform.dlt_sources.ireland.oide import oide_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="ireland_oide",
        destination="duckdb",
        dataset_name="curriculum",
    )

    source = oide_source(include_resources=True)
    pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "ireland",
            "source": "oide",
            "sections": ["primary", "post_primary", "stem", "languages"],
            "pages_crawled": sum(row_counts.values()),
        }
    )


# ============================================================================
# England Curriculum Assets
# ============================================================================


@asset(
    key=["curriculum", "england", "national_curriculum_pages"],
    group_name="multi_nation_curriculum",
    description="gov.uk National Curriculum (England)",
    compute_kind="firecrawl",
)
def england_national_curriculum(
    context,
    dlt: DagsterDltResource,
) -> MaterializeResult:
    """
    Crawl National Curriculum from gov.uk.

    Includes:
    - Key Stage 1-4 curriculum
    - GCSE subject content
    - A-Level subject content
    """
    context.log.info("Crawling England National Curriculum")

    from oideachais.data_platform.dlt_sources.uk.england.national_curriculum import national_curriculum_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="england_national_curriculum",
        destination="duckdb",
        dataset_name="curriculum",
    )

    source = national_curriculum_source()
    pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "england",
            "source": "gov_uk",
            "key_stages": ["ks1", "ks2", "ks3", "ks4", "ks5"],
            "pages_crawled": sum(row_counts.values()),
        }
    )


@asset(
    key=["curriculum", "england", "exam_boards_pages"],
    group_name="multi_nation_curriculum",
    description="AQA, Edexcel, OCR specifications (England)",
    compute_kind="firecrawl",
)
def england_exam_boards(
    context,
    dlt: DagsterDltResource,
) -> MaterializeResult:
    """
    Crawl exam board specifications from AQA, Edexcel, and OCR.

    Includes:
    - GCSE specifications
    - A-Level specifications
    - PDF specification links
    """
    context.log.info("Crawling England exam board specifications")

    from oideachais.data_platform.dlt_sources.uk.england.national_curriculum import all_exam_boards_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="england_exam_boards",
        destination="duckdb",
        dataset_name="curriculum",
    )

    source = all_exam_boards_source(include_pdf_links=True)
    pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "england",
            "source": "exam_boards",
            "boards": ["aqa", "edexcel", "ocr"],
            "pages_crawled": sum(row_counts.values()),
        }
    )


# ============================================================================
# Scotland Curriculum Assets
# ============================================================================


@asset(
    key=["curriculum", "scotland", "cfe_pages"],
    group_name="multi_nation_curriculum",
    description="Curriculum for Excellence (Scotland)",
    compute_kind="firecrawl",
)
def scotland_cfe(
    context,
    dlt: DagsterDltResource,
) -> MaterializeResult:
    """
    Crawl Curriculum for Excellence from Education Scotland.

    Includes:
    - CfE Benchmarks
    - Experiences and Outcomes
    - Gaelic Medium Education resources
    """
    context.log.info("Crawling Curriculum for Excellence")

    from oideachais.data_platform.dlt_sources.uk.scotland.curriculum_for_excellence import curriculum_for_excellence_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="scotland_cfe",
        destination="duckdb",
        dataset_name="curriculum",
    )

    source = curriculum_for_excellence_source(include_gaelic=True)
    pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "scotland",
            "source": "education_gov_scot",
            "framework": "curriculum_for_excellence",
            "languages": ["en", "gd"],
            "pages_crawled": sum(row_counts.values()),
        }
    )


@asset(
    key=["curriculum", "scotland", "sqa_pages"],
    group_name="multi_nation_curriculum",
    description="SQA National Qualifications (Scotland)",
    compute_kind="firecrawl",
)
def scotland_sqa(
    context,
    dlt: DagsterDltResource,
) -> MaterializeResult:
    """
    Crawl SQA qualification specifications.

    Includes:
    - National 5 specifications
    - Higher specifications
    - Advanced Higher specifications
    - Gaelic subject specifications
    """
    context.log.info("Crawling SQA qualifications")

    from oideachais.data_platform.dlt_sources.uk.scotland.curriculum_for_excellence import sqa_qualifications_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="scotland_sqa",
        destination="duckdb",
        dataset_name="curriculum",
    )

    source = sqa_qualifications_source(include_pdf_links=True)
    pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "scotland",
            "source": "sqa",
            "qualification_levels": ["national_5", "higher", "advanced_higher"],
            "pages_crawled": sum(row_counts.values()),
        }
    )


# ============================================================================
# Wales Curriculum Assets
# ============================================================================


@asset(
    key=["curriculum", "wales", "hwb_pages"],
    group_name="multi_nation_curriculum",
    description="Curriculum for Wales from Hwb (bilingual)",
    compute_kind="firecrawl",
)
def wales_curriculum(
    context,
    dlt: DagsterDltResource,
) -> MaterializeResult:
    """
    Crawl Curriculum for Wales from Hwb (hwb.gov.wales).

    Includes:
    - Areas of Learning and Experience (AoLE)
    - What Matters statements
    - Bilingual content (English and Welsh)
    """
    context.log.info("Crawling Curriculum for Wales")

    from oideachais.data_platform.dlt_sources.uk.wales.curriculum_for_wales import curriculum_for_wales_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="wales_curriculum",
        destination="duckdb",
        dataset_name="curriculum",
    )

    source = curriculum_for_wales_source(languages=["en", "cy"])
    pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "wales",
            "source": "hwb",
            "framework": "curriculum_for_wales",
            "languages": ["en", "cy"],
            "pages_crawled": sum(row_counts.values()),
        }
    )


@asset(
    key=["curriculum", "wales", "wjec_pages"],
    group_name="multi_nation_curriculum",
    description="WJEC/CBAC specifications (bilingual)",
    compute_kind="firecrawl",
)
def wales_wjec(
    context,
    dlt: DagsterDltResource,
) -> MaterializeResult:
    """
    Crawl WJEC/CBAC qualification specifications.

    Includes:
    - GCSE specifications (English and Welsh)
    - A-Level specifications
    - Welsh Baccalaureate
    """
    context.log.info("Crawling WJEC/CBAC qualifications")

    from oideachais.data_platform.dlt_sources.uk.wales.curriculum_for_wales import wjec_qualifications_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="wales_wjec",
        destination="duckdb",
        dataset_name="curriculum",
    )

    source = wjec_qualifications_source(languages=["en", "cy"], include_pdf_links=True)
    pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "wales",
            "source": "wjec",
            "languages": ["en", "cy"],
            "pages_crawled": sum(row_counts.values()),
        }
    )


# ============================================================================
# Northern Ireland Curriculum Assets
# ============================================================================


@asset(
    key=["curriculum", "northern_ireland", "ni_curriculum_pages"],
    group_name="multi_nation_curriculum",
    description="Northern Ireland Curriculum (CCEA)",
    compute_kind="firecrawl",
)
def northern_ireland_curriculum(
    context,
    dlt: DagsterDltResource,
) -> MaterializeResult:
    """
    Crawl Northern Ireland Curriculum from CCEA.

    Includes:
    - Foundation Stage to Key Stage 4
    - Irish-medium education resources
    """
    context.log.info("Crawling Northern Ireland Curriculum")

    from oideachais.data_platform.dlt_sources.uk.northern_ireland.ccea_curriculum import ni_curriculum_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="ni_curriculum",
        destination="duckdb",
        dataset_name="curriculum",
    )

    source = ni_curriculum_source(include_irish_medium=True)
    pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "northern_ireland",
            "source": "ccea",
            "framework": "ni_curriculum",
            "languages": ["en", "ga"],
            "pages_crawled": sum(row_counts.values()),
        }
    )


@asset(
    key=["curriculum", "northern_ireland", "ccea_qualifications_pages"],
    group_name="multi_nation_curriculum",
    description="CCEA GCSE/A-Level specifications",
    compute_kind="firecrawl",
)
def northern_ireland_ccea_quals(
    context,
    dlt: DagsterDltResource,
) -> MaterializeResult:
    """
    Crawl CCEA qualification specifications.

    Includes:
    - GCSE specifications
    - AS/A-Level specifications
    - Irish language specifications
    """
    context.log.info("Crawling CCEA qualifications")

    from oideachais.data_platform.dlt_sources.uk.northern_ireland.ccea_curriculum import ccea_qualifications_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="ni_ccea_quals",
        destination="duckdb",
        dataset_name="curriculum",
    )

    source = ccea_qualifications_source(include_pdf_links=True)
    pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "nation": "northern_ireland",
            "source": "ccea",
            "qualification_levels": ["gcse", "as_level", "a_level"],
            "pages_crawled": sum(row_counts.values()),
        }
    )


# ============================================================================
# Unified Processing Assets
# ============================================================================


@asset(
    key=["curriculum", "unified", "structured_extraction"],
    group_name="multi_nation_curriculum",
    description="BAML-extracted structured curriculum data",
    deps=[
        AssetKey(["curriculum", "ireland", "ncca_pages"]),
        AssetKey(["curriculum", "england", "national_curriculum_pages"]),
        AssetKey(["curriculum", "scotland", "cfe_pages"]),
        AssetKey(["curriculum", "wales", "hwb_pages"]),
        AssetKey(["curriculum", "northern_ireland", "ni_curriculum_pages"]),
    ],
    compute_kind="baml",
)
def curriculum_structured_extraction(
    context,
) -> MaterializeResult:
    """
    Extract structured curriculum data using BAML schemas.

    Uses multi_nation_curriculum.baml to extract:
    - CrossNationCurriculumSpec for each nation
    - CrossNationLearningOutcome for each outcome
    """
    context.log.info("Extracting structured curriculum data with BAML")

    # BAML extraction would be implemented here
    # For now, return placeholder
    extracted_count = 0

    return MaterializeResult(
        metadata={
            "nations_processed": ["ireland", "england", "scotland", "wales", "northern_ireland"],
            "specs_extracted": extracted_count,
            "baml_schema": "multi_nation_curriculum.baml",
        }
    )


@asset(
    key=["curriculum", "unified", "embeddings"],
    group_name="multi_nation_curriculum",
    description="Vector embeddings for cross-curriculum search",
    deps=[
        AssetKey(["curriculum", "unified", "structured_extraction"]),
    ],
    compute_kind="embedding",
)
def curriculum_unified_embeddings(
    context,
) -> MaterializeResult:
    """
    Generate vector embeddings for all curriculum content.

    Uses BGE-M3 for multilingual embeddings (1024 dimensions).
    Stores in LanceDB: oileain.multi_nation_curriculum

    Critical: Batch size >= 100 for performance.
    """
    context.log.info("Generating unified curriculum embeddings")

    # Embedding generation would be implemented here
    # Following CRITICAL_CONSTRAINTS: batch_size >= 100
    embedded_count = 0

    return MaterializeResult(
        metadata={
            "table": "oileain.multi_nation_curriculum",
            "embedding_model": "BAAI/bge-m3",
            "dimensions": 1024,
            "total_embedded": embedded_count,
        }
    )


@asset(
    key=["curriculum", "unified", "outcome_alignments"],
    group_name="multi_nation_curriculum",
    description="Cross-nation learning outcome alignments",
    deps=[
        AssetKey(["curriculum", "unified", "embeddings"]),
    ],
    compute_kind="alignment",
)
def curriculum_outcome_alignments(
    context,
) -> MaterializeResult:
    """
    Compute semantic alignments between learning outcomes across nations.

    Uses vector similarity + LLM reasoning to identify:
    - Equivalent outcomes
    - Partial overlaps
    - Prerequisite relationships
    - Complementary content
    """
    context.log.info("Computing cross-nation outcome alignments")

    # Alignment computation would be implemented here
    alignment_count = 0

    return MaterializeResult(
        metadata={
            "nations_aligned": ["ireland", "england", "scotland", "wales", "northern_ireland"],
            "alignments_computed": alignment_count,
            "methods": ["semantic", "llm_reasoning"],
        }
    )


@asset(
    key=["curriculum", "unified", "comparison_report"],
    group_name="multi_nation_curriculum",
    description="Cross-nation curriculum comparison report",
    deps=[
        AssetKey(["curriculum", "unified", "outcome_alignments"]),
    ],
    compute_kind="analysis",
)
def curriculum_comparison_report(
    context,
) -> MaterializeResult:
    """
    Generate comprehensive cross-nation curriculum comparison.

    Produces:
    - Coverage matrices per subject
    - Key similarities and differences
    - Resource sharing recommendations
    - Translation requirements for Celtic languages
    """
    context.log.info("Generating curriculum comparison report")

    # Report generation would be implemented here
    timestamp = datetime.now(UTC).isoformat()

    return MaterializeResult(
        metadata={
            "report_generated_at": timestamp,
            "nations_compared": 5,
            "subjects_analyzed": 0,
            "recommendations_generated": 0,
        }
    )


# ============================================================================
# Export All Assets
# ============================================================================

multi_nation_curriculum_assets = [
    # Ireland
    ireland_ncca_curriculum,
    ireland_oide_cpd,
    # England
    england_national_curriculum,
    england_exam_boards,
    # Scotland
    scotland_cfe,
    scotland_sqa,
    # Wales
    wales_curriculum,
    wales_wjec,
    # Northern Ireland
    northern_ireland_curriculum,
    northern_ireland_ccea_quals,
    # Unified processing
    curriculum_structured_extraction,
    curriculum_unified_embeddings,
    curriculum_outcome_alignments,
    curriculum_comparison_report,
]
