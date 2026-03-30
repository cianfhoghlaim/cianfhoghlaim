
import asyncio
import sys
import os
from pprint import pprint

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

import dotenv
# Load .env file
file_path = os.path.dirname(os.path.realpath(__file__))
dotenv.load_dotenv(file_path + '/.env')

from ollama_rag_service import ollama_rag_service

async def test_fetch_primary_sources():
    print("=" * 60)
    print("Testing Primary Source Fetching")
    print("=" * 60)
    
    # Test shelf marks that are likely to exist
    shelf_marks = ["T-S 10J16.12", "T-S 13J22.25", "Or. 1080 J1"]
    print(f"\nFetching primary sources for: {shelf_marks}")
    
    try:
        primary_sources = await ollama_rag_service._fetch_primary_sources(shelf_marks)
        print(f"\nFound {len(primary_sources)} primary sources.")
        
        for source in primary_sources:
            print(f"\nShelf Mark: {source.get('shelf_mark')}")
            print(f"Matched Shelf Mark: {source.get('matched_shelf_mark')}")
            print(f"Doc ID: {source.get('doc_id')}")
            print(f"Similarity Score: {source.get('similarity_score')}")
            
            if source.get('doc_id'):
                print("✅ doc_id present")
            else:
                print("❌ doc_id MISSING")
                
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fetch_primary_sources())
