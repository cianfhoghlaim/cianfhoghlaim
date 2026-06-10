#!/usr/bin/env python3
"""
Bulk SQL insertion script for all Genizah documents.

This script processes all available JSON files containing Genizah document data
and inserts them into PostgreSQL tables. It handles both Cambridge and Princeton
format documents with proper deduplication and source tracking.

Usage:
    python bulk_insert_all_documents.py --config db_config.json
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict
import argparse

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.datasets.cairo_genizah.indexing.sql_insert_genizah_documents import GenizahSQLInserter, DatabaseConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)


def load_database_config(config_file: str) -> DatabaseConfig:
    """Load database configuration from JSON file."""
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    return DatabaseConfig(
        host=config['host'],
        port=config['port'],
        database=config['database'],
        user=config['user'],
        password=config['password']
    )


def get_document_files() -> List[Dict[str, str]]:
    """Get all available document files with their source information."""
    files = []
    
    # Latest files (priority)
    latest_files = [
        ("rylands_friedberger_documents.json", "rylands"),
        ("tests/test_data/f_docs_updated.json", "princeton"),
        ("src/datasets/raw_data/cairo_genizah/cambridge_university/cambridge_full_08_scrape.json", "cambridge"),
    ]
    
    # Cambridge documents
    cambridge_files = [
        ("talmud_full_cambridge_documents.json", "cambridge"),
        ("piyyut_full_cambridge_documents.json", "cambridge"),
        ("piyyut_lit2_cambridge_documents.json", "cambridge"),
    ]
    
    # Princeton documents from test data
    princeton_files = [
        ("tests/test_data/transcribed_docs_updated.json", "princeton"),
        ("tests/test_data/letter_docs.json", "princeton"),
        ("tests/test_data/k_legal_documents.json", "princeton"),
    ]
    
    # Archive files
    archive_files = [
        ("json_archive/cambridge_genizah_documents.json", "cambridge"),
        ("json_archive/piyyut_cambridge_documents.json", "cambridge"),
        ("json_archive/tal_cambridge_documents.json", "cambridge"),
        ("json_archive/cambridge_piyyut_documents_1.json", "cambridge"),
        ("json_archive/piyyut_lit2_cambridge_docs_final.json", "cambridge"),
    ]
    
    all_files = latest_files + cambridge_files + princeton_files + archive_files
    
    # Check which files exist
    for filename, source in all_files:
        file_path = project_root / filename
        if file_path.exists():
            files.append({
                'path': str(file_path),
                'source': source,
                'name': filename
            })
            logger.info(f"Found file: {filename} ({source})")
        else:
            logger.warning(f"File not found: {filename}")
    
    return files


def process_all_documents(config_file: str, test_mode: bool = False, batch_size: int = 100, resume_from: int = 0):
    """Process all available document files."""
    logger.info("Starting bulk document insertion...")
    
    # Load database configuration
    db_config = load_database_config(config_file)
    
    # Get all document files
    files = get_document_files()
    
    if not files:
        logger.error("No document files found!")
        return
    
    logger.info(f"Found {len(files)} files to process")
    logger.info(f"Batch size: {batch_size}")
    if resume_from > 0:
        logger.info(f"Resuming from document {resume_from + 1}")
    
    # Initialize inserter
    inserter = GenizahSQLInserter(db_config)
    
    # Connect to database
    inserter.connect()
    
    # Process each file
    for file_info in files:
        logger.info(f"Processing {file_info['name']} ({file_info['source']})")
        
        inserter.process_json_file(file_info['path'], file_info['source'], batch_size, resume_from)
        
        if test_mode and inserter.stats['documents_processed'] >= 50:
            logger.info("Test mode: stopping after 50 documents")
            break
    
    # Print final statistics
    logger.info("=== Final Statistics ===")
    inserter.print_statistics()
    
    # Print summary
    total_docs = inserter.stats['documents_inserted']
    total_sources = inserter.stats['source_records_inserted']
    total_variants = inserter.stats['shelf_mark_variants_inserted']
    total_images = inserter.stats['images_inserted']
    
    logger.info(f"Successfully processed {total_docs} documents")
    logger.info(f"Created {total_sources} source records")
    logger.info(f"Created {total_variants} shelf mark variants")
    logger.info(f"Created {total_images} image records")
    
    inserter.disconnect()


def main():
    """Main function."""
    
    parser = argparse.ArgumentParser(description='Bulk insert all Genizah documents into PostgreSQL')
    parser.add_argument('--config', required=True, help='Database configuration JSON file')
    parser.add_argument('--test-mode', action='store_true', help='Process only first 50 documents for testing')
    parser.add_argument('--batch-size', type=int, default=100, help='Number of documents to process per batch (default: 100)')
    parser.add_argument('--resume-from', type=int, default=0, help='Resume processing from this document number (0-based, default: 0)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.config):
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
    
    process_all_documents(args.config, args.test_mode, args.batch_size, args.resume_from)
    logger.info("Bulk insertion completed successfully!")


if __name__ == '__main__':
    main()
