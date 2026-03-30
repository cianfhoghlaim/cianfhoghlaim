"""
Test script for fetching secondary source documents (bibliography)
Run with: python src/backend/test_fetch_secondary_sources.py
"""

import asyncio
import sys
import os
import json
from pprint import pprint

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

import dotenv
# Load .env file
file_path = os.path.dirname(os.path.realpath(__file__))
dotenv.load_dotenv(file_path + '/.env')

from search_bibliography import bibliography_search_service, BibliographySearchRequest
from search_service import search_service, SecondaryDocumentMetadata
from embedding_client import embedding_client
import numpy as np

# Mock embedding client to avoid network calls
async def mock_get_embedding(text, image=None, use_cache=True):
    print(f"  [Mock] Generating dummy embedding for: '{text}'")
    return np.random.rand(128)  # Return random vector of correct dimension (128) to avoid NaN in cosine sim

embedding_client.get_embedding = mock_get_embedding

async def test_fetch_bibliography():
    print("=" * 60)
    print("Testing Bibliography Search & Metadata Extraction")
    print("=" * 60)
    
    # 1. Search for a bibliography item
    query = "Cairo" 
    print(f"\nSearching for '{query}' in bibliography index...")
    
    request = BibliographySearchRequest(
        query=query,
        num_results=5,
        include_embeddings=False
    )
    
    try:
        response = await bibliography_search_service.search(request)
        print(f"Found {response.count} results.")
        
        if response.results:
            first_result = response.results[0]
            print(f"\nFirst Result ID: {first_result.doc_id}")
            print("Metadata fields present:")
            
            # Check for new fields in the result object directly (as defined in BibliographySearchResult)
            fields_to_check = [
                'authors', 'author', 'title', 'description', 
                'shelf_marks_mentioned', 'subject_keywords',
                'extracted_page_number'
            ]
            
            for field in fields_to_check:
                val = getattr(first_result, field, None)
                print(f"  - {field}: {val is not None} ({type(val)})")
                if val:
                    print(f"    Value: {val}")

            # 2. Test fetching via main search_service.get_document_by_id
            # This verifies that the main search service can also handle these docs and extract metadata correctly
            # Note: We need to know the index name. Assuming it's the one used by bibliography service.
            index_name = response.index_name
            print(f"\nFetching document {first_result.doc_id} via main search_service from index '{index_name}'...")
            
            doc_metadata = search_service.get_document_by_id(first_result.doc_id, index_name=index_name)
            
            if doc_metadata:
                print("\nDocumentMetadata extracted successfully!")
                print(f"Type: {type(doc_metadata)}")
                
                if isinstance(doc_metadata, SecondaryDocumentMetadata):
                    print("✅ Correctly identified as SecondaryDocumentMetadata")
                else:
                    print(f"❌ Incorrect type: {type(doc_metadata)}")

                print("New fields in DocumentMetadata:")
                
                meta_fields_to_check = [
                    'authors', 'author', 'date_display', 'isbn', 
                    'page_number', 'shelf_marks_mentioned', 'subject_keywords'
                ]
                
                for field in meta_fields_to_check:
                    val = getattr(doc_metadata, field, None)
                    print(f"  - {field}: {val is not None}")
                    if val:
                        print(f"    Value: {val}")
            else:
                print("❌ Failed to fetch document via search_service")
                
        else:
            print("⚠️ No results found to test with.")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fetch_bibliography())
