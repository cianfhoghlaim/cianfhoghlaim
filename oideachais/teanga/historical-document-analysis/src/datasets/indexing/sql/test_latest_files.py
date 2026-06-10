#!/usr/bin/env python3
"""
Test script for the latest JSON files.

This script tests the SQL insertion process with the latest files:
- rylands_friedberger_documents.json (with joins_data)
- f_docs_updated.json (Princeton format)
- cambridge_full_08_scrape.json (Cambridge format)
"""

import json
import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.datasets.cairo_genizah.indexing.sql_insert_genizah_documents import GenizahSQLInserter, DatabaseConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)


def create_test_config():
    """Create a test database configuration."""
    return DatabaseConfig(
        host="136.113.131.233",
        port=5432,
        database="genizah",
        user="genizah_user",
        password="pgGjMTDiWY8kJgEv"  # Update with your actual password
    )


def test_rylands_documents():
    """Test insertion with Rylands documents (with joins_data)."""
    logger.info("Testing Rylands document insertion...")
    
    db_config = create_test_config()
    inserter = GenizahSQLInserter(db_config)
    
    inserter.connect()
    
    # Test with Rylands file
    test_file = project_root / "rylands_friedberger_documents.json"

    if test_file.exists():
        logger.info(f"Testing with file: {test_file}")
        inserter.process_json_file(str(test_file), "rylands", batch_size=50)
        inserter.print_statistics()
        
        # Check for joins_data processing
        logger.info("Checking joins_data processing...")
        inserter.cursor.execute("""
            SELECT canonical_shelf_mark, joins_with, metadata->'joins_data' as joins_data
            FROM genizah_documents 
            WHERE joins_with IS NOT NULL AND array_length(joins_with, 1) > 0
            LIMIT 5
        """)
        results = inserter.cursor.fetchall()
        for result in results:
            logger.info(f"Document {result['canonical_shelf_mark']} joins with: {result['joins_with']}")
            if result['joins_data']:
                logger.info(f"Joins data: {result['joins_data']}")
    else:
        logger.warning(f"Test file not found: {test_file}")
        
    inserter.disconnect()


def test_princeton_documents():
    """Test insertion with Princeton documents."""
    logger.info("Testing Princeton document insertion...")
    
    db_config = create_test_config()
    inserter = GenizahSQLInserter(db_config)
    
    try:
        inserter.connect()
        
        # Test with Princeton file
        test_file = project_root / "tests" / "test_data" / "f_docs_updated.json"
        if test_file.exists():
            logger.info(f"Testing with file: {test_file}")
            inserter.process_json_file(str(test_file), "princeton", batch_size=50)
            inserter.print_statistics()
        else:
            logger.warning(f"Test file not found: {test_file}")
            
    except Exception as e:
        logger.error(f"Error testing Princeton documents: {e}")
        raise
    finally:
        inserter.disconnect()


def test_cambridge_documents():
    """Test insertion with Cambridge documents."""
    logger.info("Testing Cambridge document insertion...")
    
    db_config = create_test_config()
    inserter = GenizahSQLInserter(db_config)
    
    try:
        inserter.connect()
        
        # Test with Cambridge file
        test_file = project_root / "src" / "datasets" / "raw_data" / "cairo_genizah" / "cambridge_university" / "cambridge_full_08_scrape.json"
        if test_file.exists():
            logger.info(f"Testing with file: {test_file}")
            inserter.process_json_file(str(test_file), "cambridge")
            inserter.print_statistics()
        else:
            logger.warning(f"Test file not found: {test_file}")
            
    except Exception as e:
        logger.error(f"Error testing Cambridge documents: {e}")
        raise
    finally:
        inserter.disconnect()


def test_joins_data_processing():
    """Test specifically the joins_data processing."""
    logger.info("Testing joins_data processing...")
    
    # Create a test document with joins_data
    test_doc = {
        "doc_id": "A_445",
        "shelf_mark": "Manchester: A 445",
        "description": "Test document with joins",
        "transcriptions": [],
        "translations": [],
        "image_urls": ["A_445_1r.jpg"],
        "joins_data": {
            "joinedManuscripts": [
                {
                    "shelfmark": "Manchester: A 415",
                    "index": 0,
                    "source": "listOfJoins"
                }
            ],
            "mainShelfmark": "Manchester: A 445",
            "source": "Site User - Dr. Ezra Chwat",
            "metadata": {
                "pageUrl": "https://fgp.genizah.org/GeneralPages/Join/JoinDetails.aspx?InventoryId=446740",
                "extractedAt": "2025-10-12T17:31:46.360Z",
                "extractionMethod": "DOM"
            }
        }
    }
    
    # Save test document to temporary file
    test_file = project_root / "test_joins_document.json"
    with open(test_file, 'w') as f:
        json.dump(test_doc, f)
    
    try:
        db_config = create_test_config()
        inserter = GenizahSQLInserter(db_config)
        
        inserter.connect()
        inserter.process_json_file(str(test_file), "rylands")
        
        # Check the results
        inserter.cursor.execute("""
            SELECT canonical_shelf_mark, joins_with, 
                   (SELECT array_agg(variant_shelf_mark) FROM shelf_mark_variants 
                    WHERE document_uuid = genizah_documents.uuid) as variants
            FROM genizah_documents 
            WHERE canonical_shelf_mark = 'Manchester: A 445'
        """)
        result = inserter.cursor.fetchone()
        
        if result:
            logger.info(f"Document processed: {result['canonical_shelf_mark']}")
            logger.info(f"Joins with: {result['joins_with']}")
            logger.info(f"Shelf mark variants: {result['variants']}")
        else:
            logger.error("Document not found in database")
        
        inserter.print_statistics()
        
    except Exception as e:
        logger.error(f"Error testing joins_data processing: {e}")
        raise
    finally:
        inserter.disconnect()
        # Clean up test file
        if test_file.exists():
            test_file.unlink()


def main():
    """Run all tests."""
    logger.info("Starting tests for latest JSON files...")
    
    # Test 1: Joins data processing
    # test_joins_data_processing()
    
    # Test 2: Rylands documents
    # test_rylands_documents()
    
    # Test 3: Princeton documents
    test_princeton_documents()
    
    # Test 4: Cambridge documents
    # test_cambridge_documents()
    
    logger.info("All tests completed successfully!")


if __name__ == '__main__':
    main()
