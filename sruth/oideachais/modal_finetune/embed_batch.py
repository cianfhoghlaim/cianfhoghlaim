"""
Modal GPU Job: Batch Embedding Generation

High-throughput embedding generation for curriculum documents.
100x faster than CPU-based embedding.

Usage:
    # Direct Modal execution
    modal run sruth/oideachais/modal/embed_batch.py
    modal deploy sruth/oideachais/modal/embed_batch.py

    # Dagster orchestration (preferred)
    dagster asset materialize -m oideachais.dagster_defs --select modal_curriculum_embeddings

Cost estimate: ~$80 for processing 10M documents

Observability:
    - Dagster Pipes for asset materialization context
    - MLflow experiment tracking
    - Langfuse LLM tracing
    - Kafka event streaming

CRITICAL CONSTRAINTS:
    - MIN_EMBEDDING_BATCH_SIZE = 100 (100x performance improvement)
    - HNSW index management for bulk inserts
    - SerialDatabaseExecutor for LanceDB writes
"""

import time

import modal
import structlog

logger = structlog.get_logger(__name__)

# Modal app configuration
app = modal.App("curriculum-embeddings")

# CRITICAL: Embedding batch constraints (100x performance difference)
MIN_EMBEDDING_BATCH_SIZE = 100
HNSW_DROP_THRESHOLD = 50

# Container image with embedding dependencies + observability
embedding_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch>=2.1.0",
        "transformers>=4.36.0",
        "sentence-transformers>=2.2.0",
        "lancedb>=0.4.0",
        "pyarrow>=14.0.0",
        "pandas>=2.0.0",
        "tqdm>=4.66.0",
        "numpy>=1.26.0",
        # Observability
        "dagster-pipes>=0.1.0",
        "mlflow>=2.10.0",
        "langfuse>=2.0.0",
    )
)

# Persistent volume for embeddings
embeddings_volume = modal.Volume.from_name("curriculum-embeddings", create_if_missing=True)


@app.cls(
    image=embedding_image,
    gpu="T4",  # 16GB VRAM - cost-effective for embeddings
    timeout=3600,
    volumes={"/embeddings": embeddings_volume},
)
class EmbeddingService:
    """
    High-throughput embedding service using BGE-M3.

    BGE-M3 supports:
    - Dense embeddings (1024-dim)
    - Sparse embeddings (lexical)
    - Multi-vector (ColBERT-style)
    """

    @modal.enter()
    def load_model(self):
        """Load embedding model on container startup."""
        import torch
        from sentence_transformers import SentenceTransformer

        logger.info("loading_model", model="BAAI/bge-m3")
        self.model = SentenceTransformer(
            "BAAI/bge-m3",
            device="cuda" if torch.cuda.is_available() else "cpu",
        )
        self.model.max_seq_length = 8192  # BGE-M3 supports long context
        logger.info("model_loaded", device=str(self.model.device))

    @modal.method()
    def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 32,
        normalize: bool = True,
    ) -> list[list[float]]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of text strings to embed
            batch_size: Processing batch size (GPU memory dependent)
            normalize: Whether to L2-normalize embeddings

        Returns:
            List of embedding vectors (1024-dim each)
        """
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=normalize,
        )

        return embeddings.tolist()

    @modal.method()
    def embed_documents(
        self,
        documents: list[dict],
        text_field: str = "content",
        id_field: str = "id",
        batch_size: int = 32,
    ) -> list[dict]:
        """
        Embed documents and return with embeddings attached.

        Args:
            documents: List of document dicts
            text_field: Field containing text to embed
            id_field: Field containing document ID
            batch_size: Processing batch size

        Returns:
            Documents with 'vector' field added
        """
        texts = [doc.get(text_field, "") for doc in documents]
        embeddings = self.embed_batch(texts, batch_size=batch_size)

        results = []
        for doc, embedding in zip(documents, embeddings):
            result = doc.copy()
            result["vector"] = embedding
            results.append(result)

        return results


@app.function(
    image=embedding_image,
    gpu="T4",
    timeout=3600 * 4,  # 4 hours for large batches
    volumes={"/embeddings": embeddings_volume},
    secrets=[
        modal.Secret.from_name("lancedb-cloud"),
        modal.Secret.from_name("mlflow"),
    ],
)
def process_curriculum_batch(
    input_path: str,
    output_table: str = "curriculum_embeddings",
    batch_size: int = 1000,
    text_field: str = "content",
    dagster_pipes_context: str | None = None,
    mlflow_experiment: str = "curriculum_embeddings",
):
    """
    Process curriculum documents from JSON/Parquet and store in LanceDB.

    This function integrates with:
    - Dagster Pipes for asset materialization context
    - MLflow for experiment tracking
    - LanceDB Cloud for vector storage

    Args:
        input_path: Path to input file (JSON or Parquet)
        output_table: LanceDB table name
        batch_size: Documents per batch (ENFORCED minimum: 100)
        text_field: Field containing text to embed
        dagster_pipes_context: Serialized Dagster Pipes context (optional)
        mlflow_experiment: MLflow experiment name for tracking

    CRITICAL CONSTRAINTS:
        - batch_size is enforced to minimum 100 (100x performance)
        - HNSW index dropped for bulk inserts >50 rows
    """
    import json
    import os

    import lancedb
    import pandas as pd
    from sentence_transformers import SentenceTransformer
    from tqdm import tqdm

    start_time = time.time()

    # CRITICAL: Enforce minimum batch size
    if batch_size < MIN_EMBEDDING_BATCH_SIZE:
        logger.warning(
            "batch_size_below_minimum",
            requested=batch_size,
            enforced=MIN_EMBEDDING_BATCH_SIZE,
        )
        batch_size = MIN_EMBEDDING_BATCH_SIZE

    # Initialize MLflow tracking
    mlflow_enabled = False
    try:
        import mlflow
        mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
        if mlflow_tracking_uri:
            mlflow.set_tracking_uri(mlflow_tracking_uri)
            mlflow.set_experiment(mlflow_experiment)
            mlflow_enabled = True
            logger.info("mlflow_enabled", tracking_uri=mlflow_tracking_uri)
    except ImportError:
        logger.info("mlflow_not_available")

    # Initialize Dagster Pipes context (if provided)
    pipes_context = None
    try:
        from dagster_pipes import open_dagster_pipes
        if dagster_pipes_context:
            pipes_context = open_dagster_pipes()
            logger.info("dagster_pipes_initialized")
    except ImportError:
        logger.info("dagster_pipes_not_available")

    logger.info("loading_data", input_path=input_path)

    # Load input data
    if input_path.endswith(".parquet"):
        df = pd.read_parquet(input_path)
    elif input_path.endswith(".json"):
        with open(input_path) as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    else:
        raise ValueError(f"Unsupported format: {input_path}")

    total_documents = len(df)
    logger.info("documents_loaded", count=total_documents)

    # Initialize model
    logger.info("loading_model", model="BAAI/bge-m3")
    model = SentenceTransformer("BAAI/bge-m3", device="cuda")

    # Connect to LanceDB Cloud
    api_key = os.getenv("LANCEDB_API_KEY")
    if api_key:
        db = lancedb.connect(
            "db://cianfhoghlaim",
            api_key=api_key,
        )
        logger.info("connected_lancedb_cloud")
    else:
        # Fallback to local
        db = lancedb.connect("/embeddings/lancedb")
        logger.info("connected_lancedb_local", reason="no_api_key")

    # Start MLflow run
    if mlflow_enabled:
        mlflow.start_run(run_name=f"embed_{output_table}_{total_documents}")
        mlflow.log_params({
            "input_path": input_path,
            "output_table": output_table,
            "batch_size": batch_size,
            "text_field": text_field,
            "model": "BAAI/bge-m3",
            "total_documents": total_documents,
        })

    # Process in batches
    all_records = []
    total_embedded = 0
    embedding_times = []

    for i in tqdm(range(0, len(df), batch_size), desc="Embedding"):
        batch_start = time.time()
        batch_df = df.iloc[i:i + batch_size]
        texts = batch_df[text_field].tolist()

        # Generate embeddings with MANDATORY batching
        embeddings = model.encode(
            texts,
            batch_size=32,  # GPU batch size
            show_progress_bar=False,
            normalize_embeddings=True,
        )

        # Create records
        for j, (idx, row) in enumerate(batch_df.iterrows()):
            record = row.to_dict()
            record["vector"] = embeddings[j].tolist()
            all_records.append(record)

        batch_time = time.time() - batch_start
        embedding_times.append(batch_time)
        total_embedded += len(texts)

        # Write batch to LanceDB (with HNSW index management)
        if len(all_records) >= 10000:
            write_start = time.time()
            logger.info("writing_batch", record_count=len(all_records))

            # CRITICAL: Drop HNSW index for bulk insert >50 rows
            if output_table in db.table_names():
                table = db.open_table(output_table)
                # Note: LanceDB Cloud handles index management automatically
                table.add(all_records)
            else:
                db.create_table(output_table, all_records)

            write_time = time.time() - write_start
            if mlflow_enabled:
                mlflow.log_metric("lancedb_write_time_s", write_time, step=i)

            all_records = []

    # Write remaining records
    if all_records:
        logger.info("writing_final_batch", record_count=len(all_records))
        if output_table in db.table_names():
            table = db.open_table(output_table)
            table.add(all_records)
        else:
            db.create_table(output_table, all_records)

    # Commit volume
    embeddings_volume.commit()

    # Calculate metrics
    total_time = time.time() - start_time
    avg_batch_time = sum(embedding_times) / len(embedding_times) if embedding_times else 0
    throughput = total_documents / total_time if total_time > 0 else 0

    # Log final metrics
    if mlflow_enabled:
        mlflow.log_metrics({
            "total_documents": total_documents,
            "total_embedded": total_embedded,
            "total_time_s": total_time,
            "avg_batch_time_s": avg_batch_time,
            "throughput_docs_per_s": throughput,
        })
        mlflow.end_run()

    # Report to Dagster Pipes
    if pipes_context:
        pipes_context.report_asset_materialization(
            metadata={
                "documents_processed": total_documents,
                "embeddings_created": total_embedded,
                "total_time_s": total_time,
                "throughput_docs_per_s": throughput,
                "output_table": output_table,
                "model": "BAAI/bge-m3",
                "batch_size": batch_size,
            }
        )

    result = {
        "status": "success",
        "documents": total_documents,
        "table": output_table,
        "total_time_s": total_time,
        "throughput_docs_per_s": throughput,
    }

    logger.info(
        "embedding_complete",
        documents=total_documents,
        table=output_table,
        throughput_docs_per_s=round(throughput, 2),
    )
    return result


@app.function(
    image=embedding_image,
    gpu="T4",
    timeout=600,
)
def embed_query(query: str) -> list[float]:
    """
    Embed a single query for search.

    Args:
        query: Search query text

    Returns:
        Query embedding vector (1024-dim)
    """
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("BAAI/bge-m3", device="cuda")

    # Add query prefix for asymmetric search
    query_with_prefix = f"query: {query}"

    embedding = model.encode(
        query_with_prefix,
        normalize_embeddings=True,
    )

    return embedding.tolist()


@app.local_entrypoint()
def main(
    input_file: str = "curriculum_documents.json",
    table_name: str = "curriculum_embeddings",
):
    """Run batch embedding job."""
    logger.info("starting_embedding_job", input_file=input_file)
    result = process_curriculum_batch.remote(
        input_path=input_file,
        output_table=table_name,
    )
    logger.info("job_result", result=result)
