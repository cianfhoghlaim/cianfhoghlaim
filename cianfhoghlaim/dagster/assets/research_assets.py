"""
Research Assets for Oideachais Pipeline.

DLT filesystem ingestion for bunchloch research documents.
Loads to DuckLake SQL catalog with partitioning by subject.

Migrated from taighde.dagster_assets.ingestion_assets.

Document Counts (1,251 files, 3.4GB):
- PDFs: 843
- DOCX: 407
- Code: 42 (Java)
- Other: Keynote, text, images

Subjects:
- comp_science: CT511-CT870 (CS courses)
- gaeilge: GA101-GF107 (Irish language)
- mata: Statistics, Networks (Mathematical)
- oideachas: Presentations, lesson plans
"""

import os
from pathlib import Path
from typing import Any

from dagster import (
    DynamicPartitionsDefinition,
    MaterializeResult,
    MetadataValue,
    asset,
)

# Partitions for subjects
research_subject_partitions = DynamicPartitionsDefinition(name="research_subjects")

# Configuration
BUNCHLOCH_PATH = os.getenv(
    "BUNCHLOCH_PATH",
    str(Path(__file__).parent.parent.parent.parent.parent / "taighde" / "bunchloch"),
)
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "storage/duckdb/oideachais.duckdb")


@asset(
    group_name="research_ingestion",
    description="Ingest all bunchloch documents via DLT to DuckLake",
    compute_kind="dlt",
)
def research_bunchloch_raw(context) -> MaterializeResult:
    """
    DLT ingestion of bunchloch research documents.

    Discovers and loads:
    - PDF documents (exams, papers, presentations)
    - DOCX documents (assignments, reports)
    - Code files (Java, Python, JavaScript)

    Target: DuckLake SQL catalog partitioned by subject.
    """
    import dlt

    from cianfhoghlaim.dlt.cross.bunchloch import bunchloch_source

    # Create DLT pipeline
    pipeline = dlt.pipeline(
        pipeline_name="research_bunchloch_ingestion",
        destination="duckdb",
        dataset_name="research_bunchloch",
    )

    # Run ingestion
    source = bunchloch_source(BUNCHLOCH_PATH)
    load_info = pipeline.run(source)

    # Extract metrics
    row_counts: dict[str, int] = {}
    for load in load_info.load_packages:
        for table in load.tables:
            row_counts[table.table_name] = table.rows_count or 0

    total_documents = sum(row_counts.values())

    context.log.info(f"Loaded {total_documents} documents to DuckLake")

    return MaterializeResult(
        metadata={
            "load_id": MetadataValue.text(str(load_info.load_id)),
            "total_documents": MetadataValue.int(total_documents),
            "row_counts": MetadataValue.json(row_counts),
            "destination": MetadataValue.text("duckdb://research_bunchloch"),
        }
    )


@asset(
    group_name="research_ingestion",
    partitions_def=research_subject_partitions,
    description="Ingest documents by subject partition",
    compute_kind="dlt",
)
def research_bunchloch_by_subject(context) -> MaterializeResult:
    """
    Subject-partitioned ingestion for incremental processing.

    Subjects:
    - comp_science: CT511-CT870 (8 courses)
    - gaeilge: GA101-GF107 (Irish language)
    - mata: Statistics, Networks (Mathematical)
    - oideachas: Presentations, lesson plans
    """
    import dlt

    from cianfhoghlaim.dlt.cross.bunchloch import bunchloch_by_subject_source

    subject = context.partition_key

    pipeline = dlt.pipeline(
        pipeline_name=f"research_bunchloch_{subject}",
        destination="duckdb",
        dataset_name=f"research_bunchloch_{subject}",
    )

    source = bunchloch_by_subject_source(subject)
    load_info = pipeline.run(source)

    row_counts: dict[str, int] = {}
    for load in load_info.load_packages:
        for table in load.tables:
            row_counts[table.table_name] = table.rows_count or 0

    total_documents = sum(row_counts.values())

    context.log.info(f"Loaded {total_documents} documents for subject: {subject}")

    return MaterializeResult(
        metadata={
            "subject": MetadataValue.text(subject),
            "load_id": MetadataValue.text(str(load_info.load_id)),
            "total_documents": MetadataValue.int(total_documents),
            "row_counts": MetadataValue.json(row_counts),
        }
    )


@asset(
    group_name="research_ingestion",
    deps=["research_bunchloch_raw"],
    description="Process PDFs with document factory",
    compute_kind="python",
)
def research_pdf_extraction(context) -> MaterializeResult:
    """
    Extract text from research PDFs using the document factory.

    Uses oideachais document_factory for PDF processing:
    - Marker for complex layouts
    - DeepSeek-OCR for scanned
    - PyMuPDF4LLM for simple
    - Docling for VLM-enhanced
    """
    import duckdb
    from document_factory.pdf_converter import PDFConverterFactory

    conn = duckdb.connect(DUCKDB_PATH)
    factory = PDFConverterFactory()

    # Get PDF documents from raw ingestion
    try:
        pdf_docs = conn.execute("""
            SELECT file_hash, file_path, file_name, subject
            FROM research_bunchloch.documents
            WHERE file_type = 'pdf'
        """).fetchall()
    except Exception as e:
        context.log.warning(f"No PDF documents found: {e}")
        pdf_docs = []

    extracted = 0
    failed = 0
    extraction_results = []

    for file_hash, file_path, file_name, subject in pdf_docs:
        doc_type = _classify_document_type(file_name, subject)

        try:
            converter = factory.get_converter(doc_type)
            result = converter.convert(file_path)

            extraction_results.append({
                "file_hash": file_hash,
                "file_name": file_name,
                "subject": subject,
                "doc_type": doc_type,
                "converter": result.get("converter", "unknown"),
                "text_length": len(result.get("text", "")),
                "page_count": result.get("page_count", 0),
            })

            # Ensure table exists
            conn.execute("""
                CREATE TABLE IF NOT EXISTS research_bunchloch.pdf_extractions (
                    file_hash VARCHAR PRIMARY KEY,
                    text_content TEXT,
                    converter VARCHAR,
                    page_count INTEGER,
                    extracted_at TIMESTAMP
                )
            """)

            conn.execute("""
                INSERT OR REPLACE INTO research_bunchloch.pdf_extractions
                (file_hash, text_content, converter, page_count, extracted_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, [
                file_hash,
                result.get("text", ""),
                result.get("converter", "unknown"),
                result.get("page_count", 0),
            ])

            extracted += 1

        except Exception as e:
            context.log.warning(f"Failed to extract {file_name}: {e}")
            failed += 1

    conn.close()

    context.log.info(f"Extracted {extracted} PDFs, {failed} failed")

    return MaterializeResult(
        metadata={
            "pdfs_extracted": MetadataValue.int(extracted),
            "pdfs_failed": MetadataValue.int(failed),
            "extraction_results": MetadataValue.json(extraction_results[:20]),
        }
    )


@asset(
    group_name="research_ingestion",
    deps=["research_bunchloch_raw"],
    description="Ingest code files with language detection and chunking",
    compute_kind="python",
)
def research_code_ingestion(context) -> MaterializeResult:
    """
    Process code files with language detection and TreeSitter chunking.

    Uses shared codeolas for:
    - Language detection from extension
    - AST-based chunking (cAST algorithm)
    - Function/class extraction
    """
    import duckdb
    from códeolas import chunk_code_file, detect_language

    conn = duckdb.connect(DUCKDB_PATH)

    # Get code files
    try:
        code_files = conn.execute("""
            SELECT file_hash, file_path, file_name, subject
            FROM research_bunchloch.documents
            WHERE file_type = 'code'
        """).fetchall()
    except Exception as e:
        context.log.warning(f"No code files found: {e}")
        code_files = []

    processed = 0
    language_counts: dict[str, int] = {}
    chunk_counts: dict[str, int] = {}

    # Ensure table exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS research_bunchloch.code_files (
            file_hash VARCHAR PRIMARY KEY,
            file_name VARCHAR,
            subject VARCHAR,
            language VARCHAR,
            content TEXT,
            line_count INTEGER
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS research_bunchloch.code_chunks (
            id VARCHAR PRIMARY KEY,
            file_hash VARCHAR,
            chunk_type VARCHAR,
            name VARCHAR,
            start_line INTEGER,
            end_line INTEGER,
            text TEXT
        )
    """)

    for file_hash, file_path, file_name, subject in code_files:
        language = detect_language(file_name)
        if language:
            language_counts[language] = language_counts.get(language, 0) + 1

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Store code file
            conn.execute("""
                INSERT OR REPLACE INTO research_bunchloch.code_files
                (file_hash, file_name, subject, language, content, line_count)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [
                file_hash,
                file_name,
                subject,
                language or "unknown",
                content,
                content.count("\n") + 1,
            ])

            # Chunk the code using shared codeolas
            if language:
                chunks = chunk_code_file(content, file_name)
                chunk_counts[language] = chunk_counts.get(language, 0) + len(chunks)

                for i, chunk in enumerate(chunks):
                    chunk_id = f"{file_hash}_{i}"
                    conn.execute("""
                        INSERT OR REPLACE INTO research_bunchloch.code_chunks
                        (id, file_hash, chunk_type, name, start_line, end_line, text)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, [
                        chunk_id,
                        file_hash,
                        chunk.chunk_type.value,
                        chunk.name,
                        chunk.start_line,
                        chunk.end_line,
                        chunk.text,
                    ])

            processed += 1

        except Exception as e:
            context.log.warning(f"Failed to process {file_name}: {e}")

    conn.close()

    context.log.info(f"Processed {processed} code files")

    return MaterializeResult(
        metadata={
            "code_files_processed": MetadataValue.int(processed),
            "language_breakdown": MetadataValue.json(language_counts),
            "chunks_by_language": MetadataValue.json(chunk_counts),
        }
    )


@asset(
    group_name="research_ingestion",
    deps=["research_pdf_extraction", "research_code_ingestion"],
    description="Research ingestion statistics and validation",
    compute_kind="python",
)
def research_ingestion_stats(context) -> MaterializeResult:
    """
    Compute research ingestion statistics and validate data quality.

    Checks:
    - Document counts by type and subject
    - Extraction success rates
    - Code chunk distribution
    """
    import duckdb

    conn = duckdb.connect(DUCKDB_PATH, read_only=True)

    stats: dict[str, Any] = {}

    # Document counts by subject
    try:
        subject_counts = conn.execute("""
            SELECT subject, COUNT(*) as count
            FROM research_bunchloch.documents
            GROUP BY subject
        """).fetchdf().to_dict("records")
        stats["subject_counts"] = subject_counts
    except Exception:
        stats["subject_counts"] = []

    # Document counts by type
    try:
        type_counts = conn.execute("""
            SELECT file_type, COUNT(*) as count
            FROM research_bunchloch.documents
            GROUP BY file_type
        """).fetchdf().to_dict("records")
        stats["type_counts"] = type_counts
    except Exception:
        stats["type_counts"] = []

    # PDF extraction stats
    try:
        pdf_stats = conn.execute("""
            SELECT
                COUNT(*) as total_pdfs,
                COUNT(CASE WHEN LENGTH(text_content) > 100 THEN 1 END) as extracted,
                AVG(LENGTH(text_content)) as avg_text_length,
                AVG(page_count) as avg_pages
            FROM research_bunchloch.pdf_extractions
        """).fetchone()
        stats["pdf_extraction"] = {
            "total": pdf_stats[0] if pdf_stats else 0,
            "extracted": pdf_stats[1] if pdf_stats else 0,
            "avg_text_length": round(pdf_stats[2], 0) if pdf_stats and pdf_stats[2] else 0,
            "avg_pages": round(pdf_stats[3], 1) if pdf_stats and pdf_stats[3] else 0,
        }
    except Exception:
        stats["pdf_extraction"] = {"total": 0, "extracted": 0}

    # Code file stats
    try:
        code_stats = conn.execute("""
            SELECT
                COUNT(*) as total_files,
                SUM(line_count) as total_lines,
                COUNT(DISTINCT language) as languages
            FROM research_bunchloch.code_files
        """).fetchone()
        stats["code_files"] = {
            "total": code_stats[0] if code_stats else 0,
            "total_lines": code_stats[1] if code_stats else 0,
            "languages": code_stats[2] if code_stats else 0,
        }
    except Exception:
        stats["code_files"] = {"total": 0}

    # Code chunk stats
    try:
        chunk_stats = conn.execute("""
            SELECT chunk_type, COUNT(*) as count
            FROM research_bunchloch.code_chunks
            GROUP BY chunk_type
        """).fetchdf().to_dict("records")
        stats["code_chunks"] = chunk_stats
    except Exception:
        stats["code_chunks"] = []

    conn.close()

    context.log.info(f"Research ingestion stats computed: {stats}")

    return MaterializeResult(
        metadata={
            "subject_counts": MetadataValue.json(stats.get("subject_counts", [])),
            "type_counts": MetadataValue.json(stats.get("type_counts", [])),
            "pdf_extraction": MetadataValue.json(stats.get("pdf_extraction", {})),
            "code_files": MetadataValue.json(stats.get("code_files", {})),
            "code_chunks": MetadataValue.json(stats.get("code_chunks", [])),
        }
    )


def _classify_document_type(file_name: str, subject: str) -> str:
    """Classify document type for converter selection."""
    name_lower = file_name.lower()

    if "exam" in name_lower or "paper" in name_lower:
        return "exam"
    elif "lecture" in name_lower or "slide" in name_lower:
        return "presentation"
    elif "scan" in name_lower:
        return "scanned"
    elif subject == "gaeilge":
        return "academic"  # Complex Irish text
    else:
        return "simple"
