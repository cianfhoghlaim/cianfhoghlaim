import os
import json
import logging
import asyncio
import argparse
import sys
import pickle
import warnings
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

# Suppress insecure request warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

from search_service import search_service
from visualization_service import visualization_service

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

async def fetch_all_embeddings(index_name, force_refresh=False):
    """
    Fetch all documents with embeddings from Elasticsearch for a specific index.
    Uses local cache if available and force_refresh is False.
    """
    # Sanitize index name for filename safety
    safe_index_name = "".join([c if c.isalnum() or c in ('-', '_') else '_' for c in index_name])
    cache_file = os.path.join(DATA_DIR, f'embeddings_cache_{safe_index_name}.pkl')
    
    # Check cache first
    if not force_refresh and os.path.exists(cache_file):
        try:
            logger.info(f"Loading embeddings from cache for index '{index_name}'...")
            with open(cache_file, 'rb') as f:
                documents = pickle.load(f)
            logger.info(f"Loaded {len(documents)} documents from cache.")
            return documents
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}. Will fetch from Elasticsearch.")
    
    logger.info(f"Fetching all documents with embeddings from index '{index_name}'...")
    
    # Let's use the underlying ES client from search_service
    es = search_service.es
    
    query = {
        "bool": {
            "must": [
                {"exists": {"field": "embedding_vector"}}
            ]
        }
    }
    
    # Use scroll to fetch all results
    documents = []
    
    try:
        # Initial search
        resp = es.search(
            index=index_name,
            query=query,
            scroll='2m',
            size=1000,
            _source=["doc_id", "embedding_vector", "collection", "document_type", "language", "main_language", "period", "title", "description"]
        )
        
        old_scroll_id = resp['_scroll_id']
        hits = resp['hits']['hits']
        
        while len(hits):
            for hit in hits:
                source = hit['_source']
                if 'embedding_vector' in source and source['embedding_vector']:
                    # Extract minimal metadata needed for visualization
                    metadata = {
                        'doc_id': source.get('doc_id', hit['_id']),
                        'collection': source.get('collection', 'Unknown'),
                        'document_type': source.get('document_type', 'Unknown'),
                        'language': source.get('language') or source.get('main_language') or 'Unknown',
                        'period': source.get('period', 'Unknown'),
                        'title': source.get('title', f"Document {source.get('doc_id', hit['_id'])}")
                    }
                    
                    documents.append({
                        'doc_id': source.get('doc_id', hit['_id']),
                        'embedding': source['embedding_vector'],
                        'metadata': metadata
                    })
            
            logger.info(f"Fetched {len(documents)} documents so far from '{index_name}'...")
            
            # Scroll to next page
            try:
                resp = es.scroll(
                    scroll_id=old_scroll_id,
                    scroll='2m'
                )
                old_scroll_id = resp['_scroll_id']
                hits = resp['hits']['hits']
            except Exception as e:
                logger.error(f"Error during scroll: {e}")
                break
                
        logger.info(f"Total documents fetched from '{index_name}': {len(documents)}")
        
        # Save to cache
        if documents:
            try:
                os.makedirs(DATA_DIR, exist_ok=True)
                with open(cache_file, 'wb') as f:
                    pickle.dump(documents, f)
                logger.info(f"Saved embeddings cache to {cache_file}")
            except Exception as e:
                logger.error(f"Failed to save cache: {e}")
                
        return documents
        
    except Exception as e:
        logger.error(f"Failed to fetch documents from index '{index_name}': {e}")
        return []

def compute_visualizations(documents):
    """Compute T-SNE and UMAP coordinates"""
    if not documents:
        return None
        
    embeddings = [doc['embedding'] for doc in documents]
    
    results = {
        'generated_at': datetime.now().isoformat(),
        'count': len(documents),
        'documents': []
    }
    
    # Compute T-SNE
    logger.info("Computing T-SNE...")
    tsne_coords, _ = visualization_service.perform_tsne(
        embeddings, 
        perplexity=min(30, len(embeddings) // 10),
        n_iter=1000,
        store_model=False
    )
    
    # Compute UMAP
    logger.info("Computing UMAP...")
    umap_coords, _ = visualization_service.perform_umap(
        embeddings,
        n_neighbors=15,
        min_dist=0.1,
        store_model=False
    )
    
    # Combine results
    for i, doc in enumerate(documents):
        doc_entry = {
            'doc_id': doc['doc_id'],
            'metadata': doc['metadata'],
            'tsne': tsne_coords[i],
            'umap': umap_coords[i]
        }
        results['documents'].append(doc_entry)
        
    return results

def save_results(results, index_name):
    """Save results to JSON file specific to the index"""
    if not results:
        return
        
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Create filename based on index name
    # Sanitize index name to be safe for filenames
    safe_index_name = "".join([c if c.isalnum() or c in ('-', '_') else '_' for c in index_name])
    filename = f'full_index_visualization_{safe_index_name}.json'
    output_file = os.path.join(DATA_DIR, filename)
    
    with open(output_file, 'w') as f:
        json.dump(results, f)
        
    logger.info(f"Saved visualization data for '{index_name}' to {output_file}")

async def process_index(index_name, force_refresh=False):
    """Process a single index"""
    logger.info(f"Starting processing for index: {index_name}")
    documents = await fetch_all_embeddings(index_name, force_refresh)
    
    if not documents:
        logger.warning(f"No documents found with embeddings in index '{index_name}'. Skipping.")
        return
        
    results = compute_visualizations(documents)
    save_results(results, index_name)
    logger.info(f"Completed processing for index: {index_name}")

async def main():
    parser = argparse.ArgumentParser(description='Compute full index visualization for Genizah Search')
    parser.add_argument('--index', type=str, help='Specific index name to process')
    parser.add_argument('--all', action='store_true', help='Process all available indices')
    parser.add_argument('--refresh', action='store_true', help='Force refresh from Elasticsearch (ignore cache)')
    
    args = parser.parse_args()
    
    if args.all:
        # Fetch all available indices
        logger.info("Fetching list of available indices...")
        indices = search_service.get_available_indices()
        
        if not indices:
            logger.error("No indices found.")
            return
            
        logger.info(f"Found {len(indices)} indices: {[idx['name'] for idx in indices]}")
        
        for idx in indices:
            await process_index(idx['name'], args.refresh)
            
    elif args.index:
        # Process specific index
        await process_index(args.index, args.refresh)
        
    else:
        # Default behavior: process the default configured index
        default_index = search_service.index_name
        logger.info(f"No arguments provided. Processing default index: {default_index}")
        await process_index(default_index, args.refresh)

if __name__ == "__main__":
    asyncio.run(main())
