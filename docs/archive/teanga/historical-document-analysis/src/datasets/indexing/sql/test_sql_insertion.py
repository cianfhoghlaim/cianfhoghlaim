#!/usr/bin/env python3
"""
Test script for SQL insertion of Genizah documents.

This script tests the SQL insertion process with a small subset of documents
to ensure everything works correctly before processing large datasets.
"""

import json
import logging
import os
import sys
from pathlib import Path

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


def create_test_config():
    """Create a test database configuration."""
    return DatabaseConfig(
        host="localhost",
        port=5432,
        database="genizah_test_db",
        user="postgres",
        password="password"  # Update with your actual password
    )


def test_cambridge_documents():
    """Test insertion with Cambridge documents."""
    logger.info("Testing Cambridge document insertion...")
    
    db_config = create_test_config()
    inserter = GenizahSQLInserter(db_config)
    
    try:
        inserter.connect()
        
        # Test with a small Cambridge file
        test_file = project_root / "talmud_full_cambridge_documents.json"
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


def test_princeton_documents():
    """Test insertion with Princeton documents."""
    logger.info("Testing Princeton document insertion...")
    
    db_config = create_test_config()
    inserter = GenizahSQLInserter(db_config)
    
    try:
        inserter.connect()
        
        # Test with a Princeton file
        test_file = project_root / "tests" / "test_data" / "f_docs_updated.json"
        if test_file.exists():
            logger.info(f"Testing with file: {test_file}")
            inserter.process_json_file(str(test_file), "princeton")
            inserter.print_statistics()
        else:
            logger.warning(f"Test file not found: {test_file}")
            
    except Exception as e:
        logger.error(f"Error testing Princeton documents: {e}")
        raise
    finally:
        inserter.disconnect()


def test_small_sample():
    """Test with a very small sample to verify the process works."""
    logger.info("Testing with small sample...")
    
    # Create a small test document
    test_doc = {
        "doc_id": "MS-TS-TEST-00001",
        "shelf_mark": "MS-TS-TEST-00001",
        "description": "Test document for SQL insertion",
        "transcriptions": [
            {
                "name": "Editor: Test Editor",
                "lines": {"1": "Test line 1", "2": "Test line 2"}
            }
        ],
        "translations": ["Test translation"],
        "image_urls": ["https://example.com/test-image.jpg"],
        "original_url": "https://cudl.lib.cam.ac.uk/view/MS-TS-TEST-00001",
        "full_metadata_info": {
            "{http://www.tei-c.org/ns/1.0}idno": "MS-TS-TEST-00001",
            "{http://www.tei-c.org/ns/1.0}title": "Test Document"
        }
    }
    
    # Save test document to temporary file
    test_file = project_root / "test_document.json"
    with open(test_file, 'w') as f:
        json.dump(test_doc, f)
    
    try:
        db_config = create_test_config()
        inserter = GenizahSQLInserter(db_config)
        
        inserter.connect()
        inserter.process_json_file(str(test_file), "test")
        inserter.print_statistics()
        
    except Exception as e:
        logger.error(f"Error testing small sample: {e}")
        raise
    finally:
        inserter.disconnect()
        # Clean up test file
        if test_file.exists():
            test_file.unlink()


def main():
    """Run all tests."""
    logger.info("Starting SQL insertion tests...")
    
    try:
        # Test 1: Small sample
        test_small_sample()
        
        # Test 2: Cambridge documents (if available)
        # test_cambridge_documents()
        
        # Test 3: Princeton documents (if available)
        # test_princeton_documents()
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Tests failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

