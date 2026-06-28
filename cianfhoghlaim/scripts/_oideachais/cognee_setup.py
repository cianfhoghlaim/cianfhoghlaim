#!/usr/bin/env python3
"""Cognee v1.0.1 setup — run once before document ingestion.
Uses OpenAI API directly via $OPENAI_API_KEY from Infisical/mise."""

import os

import cognee


def setup():
    # LLM: OpenAI directly (native Cognee provider, no compat issues)
    cognee.config.set_llm_provider("openai")
    cognee.config.set_llm_model("gpt-4o-mini")  # cost-effective for entity extraction

    # Embedding: OpenAI
    cognee.config.set_embedding_provider("openai")
    cognee.config.set_embedding_model("text-embedding-3-small")

    # Graph: Neo4j via graphiti stack
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "devpassword")
    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")

    cognee.config.set_graph_database_provider("neo4j")
    cognee.config.set_graph_db_config({
        "graph_database_url": neo4j_uri,
        "graph_database_username": neo4j_user,
        "graph_database_password": neo4j_password,
    })

    # Vector: LanceDB (local)
    cognee.config.set_vector_db_provider("lancedb")
    cognee.config.set_vector_db_url("./cognee_lancedb")

    print("Cognee v1.0.1 configured:")
    print("  LLM: gpt-4o-mini @ OpenAI")
    print(f"  Graph: Neo4j @ {neo4j_uri}")
    print("  Vector: LanceDB (local)")
    print("  Embedding: text-embedding-3-small")


if __name__ == "__main__":
    setup()
