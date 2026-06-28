"""
Embedding Assets for Crypteolas.

Generates vector embeddings for code and documents using CocoIndex.
"""

import os
from pathlib import Path

from dagster import (
    AssetExecutionContext,
    MetadataValue,
    asset,
)

# Import shared partitions from other assets
from dagster_assets.defi_assets import protocol_partitions
from dagster_assets.github_assets import repo_partitions


@asset(
    partitions_def=repo_partitions,
    group_name="embeddings",
    deps=["github_code_content"],
    description="Code embeddings using CodeBERT via CocoIndex",
)
def code_embeddings(context: AssetExecutionContext) -> dict:
    """Generate embeddings for repository code."""
    import duckdb
    import lancedb
    from sentence_transformers import SentenceTransformer

    repo_full_name = context.partition_key
    db_path = os.environ.get("DUCKDB_PATH", "storage/duckdb/crypteolas.duckdb")
    lance_uri = os.environ.get("LANCEDB_URI", "storage/lance")

    conn = duckdb.connect(db_path, read_only=True)
    lance_db = lancedb.connect(lance_uri)

    model = SentenceTransformer("microsoft/codebert-base")

    try:
        code_files = conn.execute(
            """
            SELECT file_path, content, language
            FROM github.code_files
            WHERE repo = ?
            """,
            [repo_full_name],
        ).fetchall()

        if not code_files:
            context.log.info(f"No code files found for {repo_full_name}")
            return {"repo": repo_full_name, "status": "skipped", "chunks": 0}

        embeddings_data = []
        for file_path, content, language in code_files:
            chunks = chunk_code(content, language)

            for i, chunk in enumerate(chunks):
                embedding = model.encode(chunk["code"]).tolist()
                embeddings_data.append({
                    "id": f"{repo_full_name}:{file_path}:{i}",
                    "repo": repo_full_name,
                    "file_path": file_path,
                    "language": language,
                    "chunk_type": chunk.get("type", "code"),
                    "function_name": chunk.get("function_name", ""),
                    "code": chunk["code"],
                    "line_start": chunk.get("line_start", 0),
                    "line_end": chunk.get("line_end", 0),
                    "code_embedding": embedding,
                })

        if embeddings_data:
            try:
                table = lance_db.open_table("code_embeddings")
                table.add(embeddings_data)
            except Exception:
                lance_db.create_table("code_embeddings", embeddings_data)

        context.add_output_metadata({
            "repo": repo_full_name,
            "chunks_embedded": len(embeddings_data),
        })

        return {
            "repo": repo_full_name,
            "status": "success",
            "chunks": len(embeddings_data),
        }

    finally:
        conn.close()


@asset(
    partitions_def=protocol_partitions,
    group_name="embeddings",
    description="Document embeddings for whitepapers and audits",
)
def document_embeddings(context: AssetExecutionContext) -> dict:
    """Generate embeddings for protocol documentation."""
    import lancedb
    from sentence_transformers import SentenceTransformer

    protocol = context.partition_key
    lance_uri = os.environ.get("LANCEDB_URI", "storage/lance")

    lance_db = lancedb.connect(lance_uri)
    model = SentenceTransformer("BAAI/bge-m3")

    try:
        from cocoindex_flows.document_embedding import (
            fetch_protocol_documents,
            chunk_documents,
        )

        documents = fetch_protocol_documents(protocol)

        if not documents:
            context.log.info(f"No documents found for {protocol}")
            return {"protocol": protocol, "status": "skipped", "chunks": 0}

        embeddings_data = []
        for doc in documents:
            chunks = chunk_documents(doc["content"], doc["type"])

            for i, chunk in enumerate(chunks):
                embedding = model.encode(chunk["text"]).tolist()
                embeddings_data.append({
                    "id": f"{protocol}:{doc['id']}:{i}",
                    "protocol": protocol,
                    "doc_type": doc["type"],
                    "text": chunk["text"],
                    "section": chunk.get("section", ""),
                    "page": chunk.get("page"),
                    "url": doc.get("url", ""),
                    "auditor": doc.get("auditor"),
                    "severity": chunk.get("severity"),
                    "text_embedding": embedding,
                })

        if embeddings_data:
            try:
                table = lance_db.open_table("document_embeddings")
                table.add(embeddings_data)
            except Exception:
                lance_db.create_table("document_embeddings", embeddings_data)

        context.add_output_metadata({
            "protocol": protocol,
            "documents_processed": len(documents),
            "chunks_embedded": len(embeddings_data),
        })

        return {
            "protocol": protocol,
            "status": "success",
            "chunks": len(embeddings_data),
        }

    except ImportError:
        context.log.warning("CocoIndex flows not available, skipping document embeddings")
        return {"protocol": protocol, "status": "skipped", "reason": "cocoindex not available"}


@asset(
    group_name="embeddings",
    deps=["code_embeddings", "document_embeddings"],
    description="Embedding statistics and index health",
)
def embedding_stats(context: AssetExecutionContext) -> dict:
    """Compute embedding statistics and verify index health."""
    import lancedb

    lance_uri = os.environ.get("LANCEDB_URI", "storage/lance")
    lance_db = lancedb.connect(lance_uri)

    stats = {
        "code_embeddings": {"count": 0, "repos": 0},
        "document_embeddings": {"count": 0, "protocols": 0},
    }

    try:
        code_table = lance_db.open_table("code_embeddings")
        code_df = code_table.to_pandas()
        stats["code_embeddings"]["count"] = len(code_df)
        stats["code_embeddings"]["repos"] = code_df["repo"].nunique()
        stats["code_embeddings"]["languages"] = code_df["language"].unique().tolist()
    except Exception:
        pass

    try:
        doc_table = lance_db.open_table("document_embeddings")
        doc_df = doc_table.to_pandas()
        stats["document_embeddings"]["count"] = len(doc_df)
        stats["document_embeddings"]["protocols"] = doc_df["protocol"].nunique()
        stats["document_embeddings"]["doc_types"] = doc_df["doc_type"].unique().tolist()
    except Exception:
        pass

    context.add_output_metadata({
        "code_chunks": stats["code_embeddings"]["count"],
        "code_repos": stats["code_embeddings"]["repos"],
        "doc_chunks": stats["document_embeddings"]["count"],
        "doc_protocols": stats["document_embeddings"]["protocols"],
    })

    return stats


def chunk_code(content: str, language: str, max_chunk_size: int = 2000) -> list[dict]:
    """Chunk code into semantic units using tree-sitter when available."""
    try:
        from cocoindex_flows.transforms.code_chunking import semantic_chunk

        return semantic_chunk(content, language, max_chunk_size)
    except ImportError:
        lines = content.split("\n")
        chunks = []
        current_chunk = []
        current_size = 0

        for i, line in enumerate(lines):
            current_chunk.append(line)
            current_size += len(line) + 1

            if current_size >= max_chunk_size:
                chunks.append({
                    "code": "\n".join(current_chunk),
                    "type": "code",
                    "line_start": i - len(current_chunk) + 1,
                    "line_end": i,
                })
                current_chunk = []
                current_size = 0

        if current_chunk:
            chunks.append({
                "code": "\n".join(current_chunk),
                "type": "code",
                "line_start": len(lines) - len(current_chunk),
                "line_end": len(lines) - 1,
            })

        return chunks
