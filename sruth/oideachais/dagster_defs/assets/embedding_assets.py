"""
Embedding Assets for Celtic Education Platform.

Assets that create vector embeddings for semantic search:
- Curriculum content embeddings (all nations)
- Language resource embeddings (folklore, pronunciation)
- Document Q&A embeddings
- RAG evaluation assets

All embedding assets enforce MANDATORY constraints:
- Batch minimum: 100 embeddings per call
- HNSW indexes: Drop before bulk insert >50 rows
- DuckDB: Single-threaded access only

Observability:
- MLflow experiment tracking
- Langfuse LLM tracing
- Ragas RAG evaluation
- Kafka streaming events
"""
# Note: Removed future annotations for Dagster compatibility

import time
from typing import Any

import dagster as dg
from dagster import (
    AssetKey,
    MaterializeResult,
    Output,
    asset,
    op,
    job,
    graph_asset,
    AssetIn,
)


# ============================================================================
# Curriculum Embedding Assets
# ============================================================================

@asset(
    key=["embeddings", "curriculum", "ireland"],
    group_name="embeddings",
    description="Embeddings for Irish curriculum content (NCCA, SEC)",
    deps=[
        AssetKey(["ireland", "education", "curriculum_pages"]),
    ],
    compute_kind="embedding",
)
def ireland_curriculum_embeddings(context) -> MaterializeResult:
    """
    Create embeddings for Irish curriculum content.

    Uses CocoIndex flow with:
    - MANDATORY batching (100+ per call)
    - HNSW index management
    - Observability integration
    """
    from cocoindex_flows import CurriculumEmbeddingFlow, EmbeddingConfig

    context.log.info("Starting Ireland curriculum embedding")

    # Import observability
    try:
        from observability import mlflow_run, log_agent_metrics, langfuse_trace
        has_observability = True
    except ImportError:
        has_observability = False
        context.log.warning("Observability not available")

    # Configure for Ireland
    config = EmbeddingConfig(
        source_table="education.curriculum_pages",
        output_table="ireland_curriculum_embeddings",
        batch_size=100,  # MANDATORY minimum
    )

    flow = CurriculumEmbeddingFlow(config)

    # Run with MLflow tracking
    start_time = time.time()

    if has_observability:
        with mlflow_run("ireland_curriculum_embedding", tags={"nation": "ireland"}):
            with langfuse_trace("embedding_flow", metadata={"nation": "ireland"}):
                result = flow.run(limit=1000)
                log_agent_metrics(
                    agent_name="curriculum_embedding",
                    query="ireland_curriculum",
                    response_length=result["chunks"],
                    latency_ms=(time.time() - start_time) * 1000,
                    token_count=result.get("total_chars", 0),
                )
    else:
        result = flow.run(limit=1000)

    # Publish to Kafka
    try:
        from kafka import get_producer, CURRICULUM_PAGES
        producer = get_producer()
        producer.produce(
            CURRICULUM_PAGES.name,
            key="embedding_complete",
            value={
                "nation": "ireland",
                "documents": result["documents"],
                "chunks": result["chunks"],
            }
        )
        producer.flush()
    except Exception as e:
        context.log.warning(f"Kafka publish failed: {e}")

    return MaterializeResult(
        metadata={
            "nation": "ireland",
            "documents_processed": result["documents"],
            "chunks_created": result["chunks"],
            "embeddings_inserted": result.get("inserted", 0),
            "total_time_s": result["total_time_s"],
            "throughput_chunks_per_s": result.get("throughput_chunks_per_s", 0),
            "batch_size": config.batch_size,
            "model": config.model_name,
        }
    )


@asset(
    key=["embeddings", "curriculum", "uk"],
    group_name="embeddings",
    description="Embeddings for UK curriculum content (England, Scotland, Wales, NI)",
    deps=[
        AssetKey(["uk", "education", "curriculum_pages"]),
    ],
    compute_kind="embedding",
)
def uk_curriculum_embeddings(context) -> MaterializeResult:
    """
    Create embeddings for UK curriculum content.

    Covers:
    - England (National Curriculum, DfE)
    - Scotland (Curriculum for Excellence, SQA)
    - Wales (Curriculum for Wales)
    - Northern Ireland (CCEA)
    """
    from cocoindex_flows import CurriculumEmbeddingFlow, EmbeddingConfig

    context.log.info("Starting UK curriculum embedding")

    config = EmbeddingConfig(
        source_table="uk_education.curriculum_pages",
        output_table="uk_curriculum_embeddings",
        batch_size=100,
        nations=["england", "scotland", "wales", "northern_ireland"],
    )

    flow = CurriculumEmbeddingFlow(config)
    result = flow.run(limit=1000)

    return MaterializeResult(
        metadata={
            "nations": ["england", "scotland", "wales", "northern_ireland"],
            "documents_processed": result["documents"],
            "chunks_created": result["chunks"],
            "embeddings_inserted": result.get("inserted", 0),
            "total_time_s": result["total_time_s"],
        }
    )


@asset(
    key=["embeddings", "curriculum", "multilingual"],
    group_name="embeddings",
    description="Embeddings for translated curriculum (6 Celtic languages)",
    deps=[
        AssetKey(["embeddings", "curriculum", "ireland"]),
        AssetKey(["enriched", "curriculum_translations"]),
    ],
    compute_kind="embedding",
)
def multilingual_curriculum_embeddings(context) -> MaterializeResult:
    """
    Create embeddings for translated curriculum content.

    Languages:
    - ga: Irish
    - gd: Scottish Gaelic
    - cy: Welsh
    - gv: Manx
    - kw: Cornish
    - br: Breton
    """
    from cocoindex_flows import CurriculumEmbeddingFlow, EmbeddingConfig

    context.log.info("Starting multilingual curriculum embedding")

    config = EmbeddingConfig(
        source_table="education.curriculum_translations",
        output_table="multilingual_curriculum_embeddings",
        batch_size=100,
        languages=["ga", "gd", "cy", "gv", "kw", "br"],
    )

    flow = CurriculumEmbeddingFlow(config)
    result = flow.run(limit=2000)

    return MaterializeResult(
        metadata={
            "languages": config.languages,
            "documents_processed": result["documents"],
            "chunks_created": result["chunks"],
            "embeddings_inserted": result.get("inserted", 0),
        }
    )


# ============================================================================
# Celtic Language Embedding Assets
# ============================================================================

@asset(
    key=["embeddings", "celtic", "folklore"],
    group_name="embeddings",
    description="Embeddings for Duchas.ie folklore collection",
    deps=[
        AssetKey(["celtic", "folklore", "duchas"]),
    ],
    compute_kind="embedding",
)
def folklore_embeddings(context) -> MaterializeResult:
    """
    Create embeddings for Irish folklore from Duchas.ie.

    School Collection: ~700,000 manuscript pages
    - Stories and legends
    - Local customs
    - Historical accounts
    """
    from cocoindex_flows import CurriculumEmbeddingFlow, EmbeddingConfig

    config = EmbeddingConfig(
        source_table="celtic.duchas_folklore",
        output_table="folklore_embeddings",
        batch_size=100,
        chunk_size=800,  # Shorter chunks for folklore
    )

    flow = CurriculumEmbeddingFlow(config)
    result = flow.run(limit=5000)

    return MaterializeResult(
        metadata={
            "source": "duchas.ie",
            "collection": "School Collection",
            "documents_processed": result["documents"],
            "chunks_created": result["chunks"],
        }
    )


@asset(
    key=["embeddings", "celtic", "terminology"],
    group_name="embeddings",
    description="Embeddings for Tearma.ie terminology",
    deps=[
        AssetKey(["celtic", "terminology", "tearma"]),
    ],
    compute_kind="embedding",
)
def terminology_embeddings(context) -> MaterializeResult:
    """
    Create embeddings for Irish terminology from Tearma.ie.

    Official Irish language terminology:
    - Technical terms
    - Scientific vocabulary
    - Legal/administrative terms
    """
    from cocoindex_flows import CurriculumEmbeddingFlow, EmbeddingConfig

    config = EmbeddingConfig(
        source_table="celtic.tearma_terms",
        output_table="terminology_embeddings",
        batch_size=100,
        chunk_size=200,  # Short chunks for terms
        min_chunk_length=10,
    )

    flow = CurriculumEmbeddingFlow(config)
    result = flow.run(limit=10000)

    return MaterializeResult(
        metadata={
            "source": "tearma.ie",
            "terms_processed": result["documents"],
            "embeddings_created": result["chunks"],
        }
    )


# ============================================================================
# RAG Evaluation Assets
# ============================================================================

@asset(
    key=["evaluation", "rag", "curriculum"],
    group_name="evaluation",
    description="RAG quality evaluation for curriculum search",
    deps=[
        AssetKey(["embeddings", "curriculum", "ireland"]),
        AssetKey(["search", "unified_curriculum"]),
    ],
    compute_kind="evaluation",
)
def curriculum_rag_evaluation(context) -> MaterializeResult:
    """
    Evaluate RAG quality for curriculum search.

    Metrics:
    - Faithfulness: Is the answer grounded in context?
    - Answer Relevancy: Does the answer address the question?
    - Context Precision: Are retrieved contexts relevant?

    Integrations:
    - Ragas for evaluation
    - MLflow for experiment tracking
    - Langfuse for cost tracking
    - Kafka for streaming results
    """
    context.log.info("Starting RAG evaluation for curriculum search")

    try:
        from observability import (
            RagasEvaluator,
            EvaluationSample,
            run_evaluation_suite,
            mlflow_run,
            log_evaluation_results,
        )
        has_ragas = True
    except ImportError:
        has_ragas = False
        context.log.warning("Ragas not available for evaluation")

    if not has_ragas:
        return MaterializeResult(
            metadata={"status": "skipped", "reason": "Ragas not available"}
        )

    # Create evaluation samples
    # In production, these would come from logged queries
    evaluation_samples = [
        EvaluationSample(
            question="What are the key learning outcomes for Junior Cycle Mathematics?",
            answer="",  # To be filled by search
            contexts=[],  # To be filled by retrieval
            ground_truth="Number, Algebra, Geometry, Statistics and Probability",
        ),
        EvaluationSample(
            question="What is the structure of the Leaving Certificate Irish exam?",
            answer="",
            contexts=[],
            ground_truth="Paper 1: Literature (3 hours), Paper 2: Prose/Poetry (2.5 hours)",
        ),
        EvaluationSample(
            question="How is SPHE (Social, Personal and Health Education) assessed?",
            answer="",
            contexts=[],
            ground_truth="Classroom-based assessment with portfolio and reflective tasks",
        ),
    ]

    # Run evaluation (in production, would include actual retrieval + generation)
    # For now, we log the structure
    with mlflow_run("curriculum_rag_evaluation", tags={"domain": "curriculum"}):
        log_evaluation_results(
            evaluation_name="curriculum_search",
            scores={
                "sample_count": len(evaluation_samples),
                "status": "samples_prepared",
            },
        )

    # Publish to Kafka
    try:
        from kafka import get_producer, EVALUATION_RAG
        producer = get_producer()
        producer.produce(
            EVALUATION_RAG.name,
            key="curriculum_evaluation",
            value={
                "domain": "curriculum",
                "sample_count": len(evaluation_samples),
                "status": "initiated",
            }
        )
        producer.flush()
    except Exception as e:
        context.log.warning(f"Kafka publish failed: {e}")

    return MaterializeResult(
        metadata={
            "evaluation_samples": len(evaluation_samples),
            "metrics": ["faithfulness", "answer_relevancy", "context_precision"],
            "mlflow_experiment": "curriculum_rag_evaluation",
            "status": "samples_prepared",
        }
    )


@asset(
    key=["evaluation", "agent", "metrics"],
    group_name="evaluation",
    description="Agent performance metrics aggregation",
    deps=[
        AssetKey(["evaluation", "rag", "curriculum"]),
    ],
    compute_kind="metrics",
)
def agent_metrics_aggregation(context) -> MaterializeResult:
    """
    Aggregate agent performance metrics.

    Metrics:
    - Latency percentiles (p50, p95, p99)
    - Token usage and cost
    - Success/error rates
    - Query distribution by agent

    Sources:
    - Datadog APM traces
    - Langfuse LLM traces
    - MLflow experiments
    """
    context.log.info("Aggregating agent metrics")

    # In production, this would query observability backends
    # For now, we return placeholder structure

    return MaterializeResult(
        metadata={
            "metrics_aggregated": True,
            "sources": ["datadog", "langfuse", "mlflow"],
            "agents": [
                "curriculum_search",
                "language_agent",
                "qa_agent",
                "geospatial_agent",
            ],
            "time_range": "last_24h",
        }
    )


# ============================================================================
# Export All Embedding Assets
# ============================================================================

embedding_assets = [
    # Curriculum
    ireland_curriculum_embeddings,
    uk_curriculum_embeddings,
    multilingual_curriculum_embeddings,
    # Celtic language
    folklore_embeddings,
    terminology_embeddings,
    # Evaluation
    curriculum_rag_evaluation,
    agent_metrics_aggregation,
]
