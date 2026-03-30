"""
Example Assets demonstrating LakeKeeper resource usage in Dagster.

This file shows how to use the LakeKeeper resource to register and track
LanceDB tables in Dagster assets.

These are example assets for reference. To use them, uncomment the asset
definitions and add them to your Dagster definitions.
"""

import os
from pathlib import Path

from dagster import (
    AssetExecutionContext,
    AssetKey,
    MetadataValue,
    asset,
)

from sruth.shared.dagster import LakeKeeperResource


# ============================================================================
# Example 1: Register a simple LanceDB table
# ============================================================================

# @asset(
#     group_name="lakekeeper_examples",
#     description="Register a simple table in LakeKeeper",
# )
# def simple_table_registration(lakekeeper: LakeKeeperResource) -> dict:
#     """
#     Example: Register a simple table with LakeKeeper.
#
#     This demonstrates basic table registration with custom properties.
#     """
#     # Ensure namespace exists
#     lakekeeper.create_namespace_if_not_exists("examples")
#
#     # Register the table
#     table_info = lakekeeper.register_table(
#         table_name="my_data",
#         location="s3://my-bucket/lance/my_data.lance",
#         namespace="examples",
#         properties={
#             "source": "csv_ingestion",
#             "row_count": "1000",
#             "created_by": "ingestion_pipeline",
#         },
#     )
#
#     return {
#         "table": f"{table_info.namespace}.{table_info.name}",
#         "location": table_info.location,
#         "uuid": table_info.table_uuid,
#     }


# ============================================================================
# Example 2: Register an embedding table with metadata
# ============================================================================

# @asset(
#     group_name="lakekeeper_examples",
#     description="Register an embedding table with model metadata",
# )
# def embedding_table_registration(lakekeeper: LakeKeeperResource) -> dict:
#     """
#     Example: Register an embedding table with model-specific metadata.
#
#     This shows how to register embedding tables with model information
#     for tracking and discovery.
#     """
#     lakekeeper.create_namespace_if_not_exists("embeddings")
#
#     table_info = lakekeeper.register_embedding_table(
#         table_name="document_embeddings",
#         lance_uri="s3://my-bucket/lance/document_embeddings.lance",
#         model="BAAI/bge-m3",
#         dimension=1024,
#         source_type="documents",
#         namespace="embeddings",
#     )
#
#     return {
#         "table": table_info.name,
#         "model": table_info.properties.get("embedding-model"),
#         "dimension": table_info.properties.get("embedding-dimension"),
#     }


# ============================================================================
# Example 3: Materialize with Dagster metadata
# ============================================================================

# @asset(
#     group_name="lakekeeper_examples",
#     description="Create LanceDB table and register with materialization",
# )
# def create_and_register_table(
#     context: AssetExecutionContext,
#     lakekeeper: LakeKeeperResource,
# ) -> dict:
#     """
#     Example: Create a LanceDB table and register it with materialization metadata.
#
#     This demonstrates the full workflow of creating data, storing it in
#     LanceDB, and registering it with LakeKeeper while tracking metadata.
#     """
#     import lancedb
#     import pandas as pd
#
#     # Create sample data
#     data = pd.DataFrame({
#         "id": range(100),
#         "text": [f"Sample text {i}" for i in range(100)],
#         "category": ["A", "B", "C"] * 33 + ["A"],
#     })
#
#     # Store in LanceDB
#     lance_uri = os.getenv("LANCEDB_URI", "storage/lance")
#     db = lancedb.connect(lance_uri)
#
#     table_name = "sample_data"
#     try:
#         table = db.open_table(table_name)
#         table.add(data.to_dict(orient="records"))
#     except FileNotFoundError:
#         db.create_table(table_name, data)
#         table = db.open_table(table_name)
#
#     # Get table path
#     table_path = f"{lance_uri}/{table_name}.lance"
#
#     # Register with LakeKeeper and add materialization metadata
#     lakekeeper.create_namespace_if_not_exists("examples")
#
#     table_info = lakekeeper.materialize_table_asset(
#         context=context,
#         table_name=table_name,
#         location=table_path,
#         namespace="examples",
#         properties={
#             "row_count": str(len(data)),
#             "columns": str(list(data.columns)),
#             "source": "example_asset",
#         },
#     )
#
#     context.add_output_metadata(
#         metadata={
#             "row_count": len(data),
#             "columns": MetadataValue.json(list(data.columns)),
#             "table_path": table_path,
#         }
#     )
#
#     return {
#         "table": table_name,
#         "rows": len(data),
#         "location": table_path,
#     }


# ============================================================================
# Example 4: Conditional table creation
# ============================================================================

# @asset(
#     group_name="lakekeeper_examples",
#     description="Register table only if it doesn't exist",
# )
# def conditional_table_registration(lakekeeper: LakeKeeperResource) -> dict:
#     """
#     Example: Conditionally register a table only if it doesn't exist.
#
#     This pattern is useful for idempotent asset runs.
#     """
#     lakekeeper.create_namespace_if_not_exists("examples")
#
#     table_name = "conditional_table"
#
#     if not lakekeeper.table_exists(table_name, namespace="examples"):
#         table_info = lakekeeper.register_table(
#             table_name=table_name,
#             location="s3://my-bucket/lance/conditional_table.lance",
#             namespace="examples",
#             properties={"created": "2024-01-01"},
#         )
#         return {"status": "created", "table": table_name}
#     else:
#         return {"status": "exists", "table": table_name}


# ============================================================================
# Example 5: Batch table registration
# ============================================================================

# @asset(
#     group_name="lakekeeper_examples",
#     description="Register multiple tables in batch",
# )
# def batch_table_registration(lakekeeper: LakeKeeperResource) -> dict:
#     """
#     Example: Register multiple tables in a single asset.
#
#     This shows how to handle multiple related tables efficiently.
#     """
#     lakekeeper.create_namespace_if_not_exists("batch_examples")
#
#     tables_to_register = [
#         {
#             "name": "table_1",
#             "location": "s3://bucket/lance/table1.lance",
#             "properties": {"type": "metrics"},
#         },
#         {
#             "name": "table_2",
#             "location": "s3://bucket/lance/table2.lance",
#             "properties": {"type": "logs"},
#         },
#         {
#             "name": "table_3",
#             "location": "s3://bucket/lance/table3.lance",
#             "properties": {"type": "events"},
#         },
#     ]
#
#     registered = []
#     for table_spec in tables_to_register:
#         if not lakekeeper.table_exists(table_spec["name"], namespace="batch_examples"):
#             table_info = lakekeeper.register_table(
#                 table_name=table_spec["name"],
#                 location=table_spec["location"],
#                 namespace="batch_examples",
#                 properties=table_spec["properties"],
#             )
#             registered.append(table_info.name)
#
#     return {
#         "registered_count": len(registered),
#         "tables": registered,
#     }


# ============================================================================
# Example 6: Embedding table with materialization metadata
# ============================================================================

# @asset(
#     group_name="lakekeeper_examples",
#     description="Create embedding table with full metadata tracking",
# )
# def create_embedding_table_with_metadata(
#     context: AssetExecutionContext,
#     lakekeeper: LakeKeeperResource,
# ) -> dict:
#     """
#     Example: Create an embedding table and register with full materialization.
#
#     This demonstrates the recommended pattern for embedding tables with
#     comprehensive metadata tracking.
#     """
#     import lancedb
#     import numpy as np
#     import pandas as pd
#
#     # Create sample embeddings
#     num_embeddings = 100
#     dimension = 768
#
#     data = pd.DataFrame({
#         "id": [f"doc_{i}" for i in range(num_embeddings)],
#         "text": [f"Sample document text {i}" for i in range(num_embeddings)],
#         "vector": [np.random.rand(dimension).tolist() for _ in range(num_embeddings)],
#     })
#
#     # Store in LanceDB
#     lance_uri = os.getenv("LANCEDB_URI", "storage/lance")
#     db = lancedb.connect(lance_uri)
#
#     table_name = "example_embeddings"
#     try:
#         table = db.open_table(table_name)
#         table.add(data.to_dict(orient="records"))
#     except FileNotFoundError:
#         db.create_table(table_name, data)
#         table = db.open_table(table_name)
#
#     table_path = f"{lance_uri}/{table_name}.lance"
#
#     # Register with LakeKeeper using embedding-specific helper
#     lakekeeper.create_namespace_if_not_exists("embeddings")
#
#     table_info = lakekeeper.materialize_embedding_asset(
#         context=context,
#         table_name=table_name,
#         lance_uri=table_path,
#         model="sentence-transformers/all-MiniLM-L6-v2",
#         dimension=dimension,
#         source_type="examples",
#         row_count=num_embeddings,
#         namespace="embeddings",
#     )
#
#     return {
#         "table": table_name,
#         "model": "sentence-transformers/all-MiniLM-L6-v2",
#         "dimension": dimension,
#         "rows": num_embeddings,
#     }


# ============================================================================
# Example 7: Integration with existing embedding_assets.py
# ============================================================================

"""
To integrate LakeKeeper with the existing embedding_assets.py, modify the
code_embeddings and document_embeddings assets to register tables:

```python
# In embedding_assets.py, after adding data to LanceDB:

@asset(
    partitions_def=repo_partitions,
    group_name="embeddings",
    deps=["github_code_content"],
    description="Code embeddings using CodeBERT via CocoIndex",
)
def code_embeddings(
    context: AssetExecutionContext,
    lakekeeper: LakeKeeperResource,  # Add resource parameter
) -> dict:
    # ... existing embedding generation code ...

    if embeddings_data:
        try:
            table = lance_db.open_table("code_embeddings")
            table.add(embeddings_data)
        except Exception:
            lance_db.create_table("code_embeddings", embeddings_data)
            table = lance_db.open_table("code_embeddings")

        # Register with LakeKeeper
        lakekeeper.create_namespace_if_not_exists("crypteolas")
        lakekeeper.materialize_embedding_asset(
            context=context,
            table_name="code_embeddings",
            lance_uri=f"{lance_uri}/code_embeddings.lance",
            model="microsoft/codebert-base",
            dimension=768,
            source_type="code",
            row_count=len(embeddings_data),
            namespace="crypteolas",
        )

    context.add_output_metadata({
        "repo": repo_full_name,
        "chunks_embedded": len(embeddings_data),
    })

    return {
        "repo": repo_full_name,
        "status": "success",
        "chunks": len(embeddings_data),
    }
```
"""
