"""Local documents by subject MotherDuck Dive.

Added 2026-07-17. Reads from `oideachais.celtic.local_documents.*` via
the local DuckDB destination.
"""

from __future__ import annotations


def build_local_documents_dive() -> str:
    """Return the SQL DDL for the local documents Dive."""
    return """
    CREATE OR REPLACE VIEW md:oideachais.dives.local_documents AS
    SELECT
        subject,
        file_name,
        file_path,
        rel_path,
        size_bytes,
        extension,
        modified_at
    FROM (
        SELECT 'comp_science' AS subject, * FROM md:oideachais.celtic.local_documents.comp_science_documents
        UNION ALL SELECT 'gaeilge', * FROM md:oideachais.celtic.local_documents.gaeilge_documents
        UNION ALL SELECT 'mata', * FROM md:oideachais.celtic.local_documents.mata_documents
        UNION ALL SELECT 'oideachas', * FROM md:oideachais.celtic.local_documents.oideachas_documents
    );
    """


LOCAL_DOCUMENTS_KPI_QUERIES = {
    "per_subject_count": """
        SELECT subject, COUNT(*) AS n_documents, SUM(size_bytes) AS total_bytes
        FROM md:oideachais.dives.local_documents
        GROUP BY subject
        ORDER BY n_documents DESC;
    """,
    "extension_breakdown": """
        SELECT extension, COUNT(*) AS n_files
        FROM md:oideachais.dives.local_documents
        WHERE extension IS NOT NULL
        GROUP BY extension
        ORDER BY n_files DESC;
    """,
    "recent_additions": """
        SELECT file_name, subject, size_bytes, modified_at
        FROM md:oideachais.dives.local_documents
        WHERE modified_at IS NOT NULL
        ORDER BY modified_at DESC
        LIMIT 30;
    """,
    "size_distribution": """
        SELECT
            subject,
            CASE
                WHEN size_bytes < 1024 THEN '< 1 KB'
                WHEN size_bytes < 1024 * 1024 THEN '1 KB - 1 Manitoba'
                WHEN size_bytes < 10 * 1024 * 1024 THEN '1 Manitoba - 10 Manitoba'
                ELSE '> 10 Manitoba'
            END AS size_bucket,
            COUNT(*) AS n_files
        FROM md:oideachais.dives.local_documents
        GROUP BY subject, size_bucket
        ORDER BY subject, n_files DESC;
    """,
}


__all__ = [
    "build_local_documents_dive",
    "LOCAL_DOCUMENTS_KPI_QUERIES",
]