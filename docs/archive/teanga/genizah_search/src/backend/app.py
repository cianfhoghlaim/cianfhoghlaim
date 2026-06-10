# Updated app.py - FastAPI endpoint with embedding visualization support

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from datetime import datetime
import dotenv
import logging
logging.getLogger('elasticsearch').setLevel(logging.DEBUG)

file_path = os.path.dirname(os.path.realpath(__file__))
load_dotenv = dotenv.load_dotenv(file_path + '/.env')

from search_service import (
    SearchResponse, SearchRequest, DocumentMetadata, SecondaryDocumentMetadata,
    search_service
)
from search_bibliography import (
    BibliographyHybridSearchRequest,
    BibliographySearchResponse,
    bibliography_search_service,
)
from ollama_rag_service import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ollama_rag_service,
)
from visualization_service import visualization_service
from embedding_client import embedding_client
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from search_service import FilterOptions

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Cairo Genizah Search API",
    description="AI-powered semantic search through historical manuscripts with embedding visualizations.",
    version="1.1.0",  # Updated version
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://elastic.cairogenizah.ai",
        "http://frontend:80",
        "https://cairogenizah.ai",
        "https://www.cairogenizah.ai",
        "https://api.cairogenizah.ai",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

# Exception handlers


# API Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}




@app.get("/filters", response_model=FilterOptions)
async def get_filter_options():
    """Get available filter options for the frontend"""
    return search_service.get_filter_options()


@app.get("/indices")
async def get_available_indices():
    """Get list of available Elasticsearch indices"""
    try:
        indices = search_service.get_available_indices()
        logger.info(f"Found {len(indices)} available indices: {[idx['name'] for idx in indices]}")
        return {
            "indices": indices,
            "default_index": search_service.index_name,
            "total_count": len(indices)
        }
    except Exception as e:
        logger.error(f"Failed to get available indices: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available indices: {str(e)}"
        )


@app.get("/document/{doc_id}", response_model=Union[DocumentMetadata, SecondaryDocumentMetadata])
async def get_document(doc_id: str, index_name: Optional[str] = None):
    """
    Get full document details by ID

    This endpoint returns complete metadata, transcription, translation,
    and image information for a specific document.
    """
    document = search_service.get_document_by_id(doc_id, index_name=index_name)

    if not document:
        raise HTTPException(
            status_code=404,
            detail=f"Document {doc_id} not found"
        )

    return document


@app.get("/document/{doc_id}/manifest")
async def get_document_manifest(doc_id: str, index_name: Optional[str] = None):
    """
    Get IIIF Presentation 2.1 manifest for a document
    """
    manifest = search_service.generate_iiif_manifest(doc_id, index_name=index_name)
    
    if not manifest:
        raise HTTPException(
            status_code=404,
            detail=f"Manifest not found for document {doc_id}"
        )

    return manifest


# Shelf mark search request model
class ShelfMarkSearchRequest(BaseModel):
    shelf_mark: str = Field(..., min_length=1, max_length=100, description="Shelf mark to search for")
    exact_match: bool = Field(default=False, description="Whether to perform exact match or partial match")
    num_results: Optional[int] = Field(default=10, ge=1, le=50, description="Number of results to return")
    include_embeddings: Optional[bool] = Field(default=False, description="Include embedding vectors for visualization")
    index_name: Optional[str] = Field(default=None, description="Elasticsearch index to search (defaults to configured index)")


# Keyword search request model
class KeywordSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Keywords or phrases to search for")
    num_results: Optional[int] = Field(default=10, ge=1, le=50, description="Number of results to return")
    page: Optional[int] = Field(default=1, ge=1, description="Page number for pagination (1-based)")
    index_name: Optional[str] = Field(default=None, description="Elasticsearch index to search (defaults to configured index)")


# Hybrid search request model
class HybridSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Search query for hybrid search")
    semanticWeight: int = Field(default=50, ge=0, le=100, description="Weight for semantic search (0-100)")
    keywordWeight: int = Field(default=50, ge=0, le=100, description="Weight for keyword search (0-100)")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Search filters")
    num_results: Optional[int] = Field(default=10, ge=1, le=50, description="Number of results to return")
    include_embeddings: Optional[bool] = Field(default=False, description="Include embedding vectors for visualization")
    page: Optional[int] = Field(default=1, ge=1, description="Page number for pagination (1-based)")
    index_name: Optional[str] = Field(default=None, description="Elasticsearch index to search (defaults to configured index)")


@app.post("/search-shelfmark", response_model=SearchResponse)
async def search_by_shelfmark(
        search_request: ShelfMarkSearchRequest,
        request: Request
):
    """
    Search documents by shelf mark or catalog number
    
    This endpoint allows users to find specific documents using their shelf mark
    (e.g., T-S 8J5.1, MS-TS-NS-144.1). Supports both exact and partial matching.
    
    Examples:
    - T-S 8J5.1 (exact match)
    - T-S 8J5 (partial match)
    - MS-TS-NS-144 (partial match)
    """
    # Log the shelf mark search request
    logger.info(f"Shelf mark search: '{search_request.shelf_mark}', exact_match={search_request.exact_match}")

    # Perform shelf mark search
    try:
        result = await search_service.search_by_shelfmark(search_request, search_request.index_name)
        
        # Log successful search
        logger.info(f"Shelf mark search completed: {result.count} results in {result.processing_time_ms}ms")
        
        return result
        
    except Exception as e:
        logger.error(f"Shelf mark search failed for '{search_request.shelf_mark}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Shelf mark search failed: {str(e)}"
        )


@app.post("/search-keyword", response_model=SearchResponse)
async def search_by_keyword(
        search_request: KeywordSearchRequest,
        request: Request
):
    """
    Search documents by keywords in text content
    
    This endpoint allows users to find documents by searching for specific words
    or phrases in transcriptions, translations, descriptions, and other text fields.
    This is a traditional keyword-based search that looks for exact text matches.
    
    Examples:
    - "marriage contract"
    - "Kiddushin"
    - "Hebrew"
    - "responsum"
    """
    # Log the keyword search request
    logger.info(f"Keyword search: '{search_request.query}', page={search_request.page}")

    # Perform keyword search
    try:
        result = await search_service.search_by_keyword(search_request, search_request.index_name)
        
        # Log successful search
        logger.info(f"Keyword search completed: {result.count} results in {result.processing_time_ms}ms")
        
        return result
        
    except Exception as e:
        logger.error(f"Keyword search failed for '{search_request.query}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Keyword search failed: {str(e)}"
        )


@app.post("/search-hybrid", response_model=SearchResponse)
async def search_hybrid(
        search_request: HybridSearchRequest,
        request: Request
):
    """
    Hybrid search combining semantic and keyword search
    
    This endpoint performs a weighted combination of semantic AI search and traditional
    keyword search. Users can adjust the weights to balance between conceptual understanding
    and exact text matching.
    
    Features:
    - Configurable weights for semantic vs keyword search
    - Combines the best of both search approaches
    - Supports all standard search filters
    - Optional embedding data for visualization
    
    Examples:
    - 50% semantic + 50% keyword (balanced)
    - 80% semantic + 20% keyword (concept-focused)
    - 20% semantic + 80% keyword (text-focused)
    """
    # Validate weights sum to 100
    if search_request.semanticWeight + search_request.keywordWeight != 100:
        raise HTTPException(
            status_code=400,
            detail="Semantic and keyword weights must sum to 100"
        )
    
    # Log the hybrid search request
    logger.info(f"Hybrid search: '{search_request.query}', "
               f"semantic_weight={search_request.semanticWeight}%, "
               f"keyword_weight={search_request.keywordWeight}%, "
               f"page={search_request.page}")

    # Perform hybrid search.
    try:
        result = await search_service.search_hybrid(search_request, search_request.index_name)
        
        # Log successful search
        logger.info(f"Hybrid search completed: {result.count} results in {result.processing_time_ms}ms")
        
        return result
        
    except Exception as e:
        logger.error(f"Hybrid search failed for '{search_request.query}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Hybrid search failed: {str(e)}"
        )


@app.post("/search", response_model=SearchResponse)
async def search_documents(
        search_request: SearchRequest,
        request: Request
):
    """
    Search Cairo Genizah documents with semantic AI search and optional embedding visualization.

    This endpoint performs AI-powered semantic search through historical manuscripts
    from the Cairo Genizah collection. Returns results with rich metadata including
    titles, descriptions, images, transcriptions, and translations. 
    
    New features:
    - Optional embedding vectors for t-SNE/PCA visualization
    - Enhanced metadata for better user experience
    - Improved similarity scoring
    
    Set `include_embeddings=true` to get embedding data for visualization.
    """
    # Log the search request for analytics
    logger.info(f"Search request: query='{search_request.query}', "
               f"include_embeddings={search_request.include_embeddings}, "
               f"num_results={search_request.num_results}")

    # Perform search
    try:
        result = await search_service.search(search_request)
        
        # Log successful search
        logger.info(f"Search completed: {result.count} results in {result.processing_time_ms}ms")
        
        return result
        
    except Exception as e:
        logger.error(f"Search failed for query '{search_request.query}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@app.post("/search-bibliography-hybrid", response_model=BibliographySearchResponse)
async def search_bibliography_hybrid(search_request: BibliographyHybridSearchRequest, request: Request):
    """
    Hybrid search for the Genizah bibliography index.

    Defaults to 60% semantic (embedding_vector) and 40% keyword across
    description, full_text, and shelf_marks_mentioned. Weights can be adjusted
    as long as they sum to 100.
    """
    if search_request.semanticWeight + search_request.keywordWeight != 100:
        raise HTTPException(status_code=400, detail="Semantic and keyword weights must sum to 100")

    try:
        result = await bibliography_search_service.search_hybrid(search_request)
        return result
    except Exception as e:
        logger.error(f"Bibliography hybrid search failed for '{search_request.query}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bibliography hybrid search failed: {str(e)}")


@app.get("/embedding-stats")
async def get_embedding_stats():
    """
    Get statistics about embedding usage and visualization features
    
    New endpoint to help monitor embedding-related usage and performance.
    """
    try:
        stats = search_service.get_stats()
        
        # Add embedding-specific stats
        embedding_stats = {
            "base_stats": stats,
            "embedding_features": {
                "supports_visualization": True,
                "embedding_dimension": 768,  # Adjust based on your actual embedding model
                "visualization_methods": ["pca", "tsne"],
                "max_results_for_visualization": 20
            },
            "performance_notes": {
                "pca_calculation_time": "~50ms for 10 documents",
                "tsne_calculation_time": "~500ms for 10 documents",
                "recommendation": "Use PCA for quick visualization, t-SNE for detailed analysis"
            }
        }
        
        return embedding_stats
        
    except Exception as e:
        logger.error(f"Failed to get embedding stats: {e}")
        return {
            "status": "error",
            "error": str(e),
            "embedding_features": {
                "supports_visualization": False
            }
        }


# Visualization Explorer request model
class VisualizationExplorerRequest(BaseModel):
    num_documents: Optional[int] = Field(default=1000, ge=10, le=10000, description="Number of documents to load for visualization")
    load_full_index: Optional[bool] = Field(default=False, description="Load the entire index (ignores num_documents)")
    include_embeddings: Optional[bool] = Field(default=True, description="Include embedding vectors for visualization")
    index_name: Optional[str] = Field(default=None, description="Name of the Elasticsearch index to load from")


@app.post("/visualization-explorer", response_model=SearchResponse)
async def get_visualization_explorer_data(
        request: VisualizationExplorerRequest,
        request_obj: Request
):
    """
    Load a set of documents for the visualization explorer
    
    This endpoint loads a random sample of documents from the collection
    for full-page visualization exploration. Supports loading a configurable
    number of documents or the entire index.
    
    Features:
    - Random sampling of documents
    - Full metadata extraction
    - Embedding vectors for visualization
    - Support for large document sets
    
    Note: This endpoint only returns documents with embeddings. Use
    /visualization-explorer/calculate to compute visualization coordinates.
    """
    logger.info(f"Visualization explorer request: num_documents={request.num_documents}, "
               f"load_full_index={request.load_full_index}, index_name={request.index_name}")
    
    try:
        result = await search_service.get_visualization_explorer_data(request, index_name=request.index_name)
        
        logger.info(f"Visualization explorer data loaded: {result.count} documents")
        
        return result
        
    except Exception as e:
        logger.error(f"Visualization explorer data loading failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load visualization explorer data: {str(e)}"
        )


# Visualization calculation request model
class VisualizationCalculateRequest(BaseModel):
    embeddings: List[List[float]] = Field(..., description="List of embedding vectors to visualize")
    method: str = Field(default='tsne', description="Visualization method: 'pca', 'tsne', or 'umap'")
    # PCA parameters
    n_components: Optional[int] = Field(default=2, description="Number of components for PCA")
    # t-SNE parameters
    perplexity: Optional[int] = Field(default=None, description="Perplexity for t-SNE (auto if None)")
    n_iter: Optional[int] = Field(default=1000, description="Number of iterations for t-SNE")
    learning_rate: Optional[float] = Field(default=200.0, description="Learning rate for t-SNE")
    early_exaggeration: Optional[float] = Field(default=12.0, description="Early exaggeration for t-SNE")
    # UMAP parameters
    n_neighbors: Optional[int] = Field(default=15, description="Number of neighbors for UMAP")
    min_dist: Optional[float] = Field(default=0.1, description="Minimum distance for UMAP")
    metric: Optional[str] = Field(default='cosine', description="Distance metric for UMAP")
    random_state: Optional[int] = Field(default=42, description="Random seed for reproducibility")


@app.post("/visualization-explorer/calculate")
async def calculate_visualization(request: VisualizationCalculateRequest):
    """
    Calculate visualization coordinates from embeddings using proper Python libraries.
    
    This endpoint performs dimensionality reduction (PCA, t-SNE, or UMAP) on embedding
    vectors using scikit-learn and umap-learn libraries. This ensures accurate and
    meaningful clustering results.
    
    Methods:
    - PCA: Fast linear dimensionality reduction
    - t-SNE: Non-linear method that preserves local structure
    - UMAP: Fast non-linear method that preserves both local and global structure
    
    Returns 2D coordinates for plotting along with statistics.
    """
    logger.info(f"Visualization calculation request: method={request.method}, "
               f"num_embeddings={len(request.embeddings)}")
    
    try:
        # Prepare parameters based on method
        params = {
            'random_state': request.random_state
        }
        
        if request.method.lower() == 'pca':
            params['n_components'] = request.n_components
        elif request.method.lower() == 'tsne':
            if request.perplexity is not None:
                params['perplexity'] = request.perplexity
            params['n_iter'] = request.n_iter
            params['learning_rate'] = request.learning_rate
            params['early_exaggeration'] = request.early_exaggeration
        elif request.method.lower() == 'umap':
            params['n_neighbors'] = request.n_neighbors
            params['min_dist'] = request.min_dist
            params['metric'] = request.metric
            params['n_components'] = request.n_components
        
        # Calculate visualization
        result = visualization_service.calculate_visualization(
            embeddings=request.embeddings,
            method=request.method,
            **params
        )
        
        logger.info(f"Visualization calculation completed: {result['method']}, "
                   f"{result['num_points']} points")
        
        return result
        
    except ValueError as e:
        logger.error(f"Invalid visualization request: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Visualization calculation failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate visualization: {str(e)}"
        )



from fastapi.responses import FileResponse

@app.get("/visualization-explorer/full-index")
async def get_full_index_visualization(index_name: Optional[str] = None):
    """
    Get pre-computed visualization for the full index.
    
    Args:
        index_name: Optional name of the index to retrieve visualization for.
                   If not provided, defaults to the system default index.
    
    Returns T-SNE and UMAP coordinates for all documents in the index,
    pre-computed by the background script.
    """
    try:
        # Determine which index to use
        target_index = index_name if index_name else search_service.index_name
        
        # Sanitize index name for filename safety
        safe_index_name = "".join([c if c.isalnum() or c in ('-', '_') else '_' for c in target_index])
        filename = f'full_index_visualization_{safe_index_name}.json'
        
        # Path to the pre-computed data file
        data_file = os.path.join(os.path.dirname(__file__), 'data', filename)
        
        # Check if specific file exists
        if not os.path.exists(data_file):
            # Fallback logic:
            # 1. If no index_name was provided, try the legacy filename 'full_index_visualization.json'
            # 2. If that fails, return 404
            
            if not index_name:
                legacy_file = os.path.join(os.path.dirname(__file__), 'data', 'full_index_visualization.json')
                if os.path.exists(legacy_file):
                    data_file = legacy_file
                else:
                    raise HTTPException(
                        status_code=404,
                        detail="Full index visualization not available. Please run the computation script."
                    )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Full index visualization for index '{target_index}' not available. Please run the computation script."
                )
            
        # Use FileResponse to stream the file directly
        # This avoids loading the entire JSON into memory and fixes Content-Length issues
        return FileResponse(
            path=data_file, 
            media_type='application/json', 
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load full index visualization: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load full index visualization: {str(e)}"
        )


# Query projection request model

class QueryProjectionRequest(BaseModel):
    query: str = Field(..., description="Text query to embed and project")
    method: str = Field(default='umap', description="Visualization method to project onto ('pca', 'tsne', or 'umap')")
    n_neighbors: Optional[int] = Field(default=10, description="Number of neighbors for t-SNE projection")


@app.post("/visualization-explorer/project-query")
async def project_query(request: QueryProjectionRequest):
    """
    Project a text query onto an existing visualization space.
    
    This endpoint:
    1. Embeds the query text using the embedding service
    2. Projects the query embedding onto the current visualization space
    3. Returns the projected coordinates and nearest neighbors
    
    The visualization must be calculated first using /visualization-explorer/calculate
    with the same method. Supports PCA (direct transform), UMAP (direct transform),
    and t-SNE (k-NN approximation).
    """
    logger.info(f"Query projection request: query='{request.query[:50]}...', method={request.method}")
    
    try:
        # Embed the query
        query_embedding = await embedding_client.get_embedding(
            request.query,
            image=None,
            use_cache=True  # Cache query embeddings for performance
        )
        
        # Project onto visualization space
        result = visualization_service.project_query(
            query_embedding=query_embedding.tolist(),
            method=request.method,
            n_neighbors=request.n_neighbors or 10
        )
        
        logger.info(f"Query projected successfully: ({result['coordinates']['x']:.3f}, {result['coordinates']['y']:.3f})")
        
        return {
            'query': request.query,
            'coordinates': result['coordinates'],
            'method': result['method'],
            'nearest_neighbors': result['nearest_neighbors']
        }
        
    except ValueError as e:
        logger.error(f"Invalid projection request: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Query projection failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to project query: {str(e)}"
        )


@app.get("/collection-hierarchy")
async def get_collection_hierarchy(index_name: Optional[str] = None, debug: bool = False):
    """
    Get collection hierarchy using Elasticsearch aggregations
    
    Returns a fast aggregation-based hierarchy of:
    collection -> sub_collection -> shelfmarks
    
    This uses Elasticsearch aggregations which are very fast and optimized.
    Perfect for browsing by collections.
    
    Args:
        index_name: Optional index name to query
        debug: If True, returns raw aggregation data for debugging
    """
    try:
        if debug:
            # Return raw aggregation response for debugging
            import json
            from elasticsearch import Elasticsearch
            import os
            
            es_host = os.getenv('ELASTICSEARCH_HOST', 'elastic.cairogenizah.ai')
            es_port = os.getenv('ELASTICSEARCH_PORT', '443')
            es = Elasticsearch(
                [f"https://{es_host}:{es_port}"],
                basic_auth=(os.getenv('ELASTICSEARCH_USER', 'cairo_user'), os.getenv('ELASTICSEARCH_PASSWORD')),
                verify_certs=False,
            )
            
            target_index = index_name or search_service.index_name
            aggs = {
                "collections": {
                    "terms": {"field": "collection", "size": 10},
                    "aggs": {
                        "sub_collections": {
                            "terms": {"field": "sub_collection", "size": 10},
                            "aggs": {
                                "shelf_mark": {
                                    "terms": {"field": "shelf_mark", "size": 50}
                                }
                            }
                        },
                        "sample_docs": {
                            "top_hits": {
                                "size": 3,
                                "_source": ["collection", "sub_collection", "shelf_mark", "collection_type"]
                            }
                        }
                    }
                }
            }
            
            response = es.search(index=target_index, size=0, aggs=aggs)
            return {
                "raw_aggregations": response.get("aggregations", {}),
                "index_used": target_index
            }
        
        hierarchy = search_service.get_collection_hierarchy(index_name=index_name)
        return {
            "hierarchy": hierarchy,
            "count": sum(col.get("count", 0) for col in hierarchy.values()),
            "collections_count": len(hierarchy)
        }
    except Exception as e:
        logger.error(f"Failed to get collection hierarchy: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get collection hierarchy: {str(e)}"
        )


@app.get("/shelfmark/{shelfmark}/documents")
async def get_shelfmark_documents(
    shelfmark: str,
    include_embeddings: bool = True,
    index_name: Optional[str] = None
):
    """
    Get all documents for a specific shelfmark with optional embeddings
    
    This is used when a user selects a shelfmark from the collection browser.
    The embeddings can be added to the visualization.
    
    Args:
        shelfmark: The shelfmark to search for
        include_embeddings: Whether to include embeddings in the response
        index_name: Optional index name to search
    """
    try:
        documents = search_service.get_shelfmark_documents(
            shelfmark=shelfmark,
            include_embeddings=include_embeddings,
            index_name=index_name
        )

        # Convert to SearchResult-like dicts for the client
        results = []
        for doc in documents:
            results.append({
                "doc_id": doc.doc_id,
                "similarity_score": doc.similarity_score,
                "metadata": doc.metadata.dict() if doc.metadata else None,
                "embedding": doc.embedding
            })
        
        return {
            "shelfmark": shelfmark,
            "documents": results,
            "count": len(results),
            "include_embeddings": include_embeddings
        }
    except Exception as e:
        logger.error(f"Failed to get shelfmark documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get shelfmark documents: {str(e)}"
        )


@app.get("/debug/sample-docs")
async def debug_sample_docs(collection: str, sub_collection: Optional[str] = None, index_name: Optional[str] = None, size: int = 5):
    """
    Return a small sample of documents for a collection/sub_collection with
    only relevant fields to verify shelf mark presence.
    """
    try:
        samples = search_service.sample_docs_for_collection(collection, sub_collection, index_name, size)
        return {"collection": collection, "sub_collection": sub_collection, "size": len(samples), "docs": samples}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sample docs: {str(e)}")


@app.get("/debug/shelfmarks")
async def debug_shelfmarks(collection: str, sub_collection: Optional[str] = None, index_name: Optional[str] = None):
    
    try:
        dist = search_service.get_shelfmark_distribution(collection, sub_collection, index_name, size)
        return {
            "collection": collection,
            "sub_collection": sub_collection,
            "index_name": index_name or search_service.index_name,
            **dist
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to aggregate shelfmarks: {str(e)}")


@app.get("/collection-shelfmarks")
async def get_collection_shelfmarks(collection: str, sub_collection: Optional[str] = None, index_name: Optional[str] = None, size: int = 500):
    """
    Return normalized shelfmark list for a collection/sub_collection for UI consumption.
    """
    try:
        dist = search_service.get_shelfmark_distribution(collection, sub_collection, index_name, size)
        buckets = dist.get("buckets", [])
        shelfmarks = [{
            "name": b.get("key"),
            "count": b.get("doc_count", 0),
            "doc_ids": b.get("doc_ids", [])
        } for b in buckets if b.get("key")]
        return {
            "collection": collection,
            "sub_collection": sub_collection,
            "index_name": index_name or search_service.index_name,
            "field_used": dist.get("field_used"),
            "count": len(shelfmarks),
            "shelfmarks": shelfmarks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collection shelfmarks: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat_with_rag(request: ChatRequest):
    """
    Chat with RAG (Retrieval-Augmented Generation) using Ollama.
    
    This endpoint performs RAG by:
    1. Searching the bibliography index for relevant context
    2. Using that context to generate informed responses via Ollama
    
    Supports conversation history for context-aware responses.
    """
    try:
        response = await ollama_rag_service.chat(request)
        return response
    except Exception as e:
        logger.error(f"Chat request failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat request failed: {str(e)}"
        )


@app.get("/chat/models")
async def get_chat_models():
    """Get list of available Ollama models for chat"""
    try:
        models = await ollama_rag_service.get_available_models()
        return {
            "models": models,
            "default": "command-r:latest"
        }
    except Exception as e:
        logger.error(f"Failed to get chat models: {e}")
        # Return default models if API call fails
        return {
            "models": ["llama3.2", "llama3", "mistral", "qwen2"],
            "default": "llama3.2",
            "error": "Could not fetch models from Ollama API"
        }


@app.get("/")
async def root():
    """API root with basic info"""
    return {
        "message": "Cairo Genizah Search API",
        "version": "1.1.0",
        "new_features": [
            "Shelf mark search functionality",
            "Advanced search interface",
            "Embedding visualization support",
            "t-SNE and PCA dimensionality reduction",
            "Enhanced metadata extraction",
            "Improved similarity scoring",
            "Collection browser with fast aggregations",
            "RAG chat with bibliography search"
        ],
        "docs": "/docs",
        "endpoints": {
            "search": "POST /search",
            "search_shelfmark": "POST /search-shelfmark",
            "search_keyword": "POST /search-keyword",
            "search_hybrid": "POST /search-hybrid",
            "chat": "POST /chat",
            "chat_models": "GET /chat/models",
            "visualization_explorer": "POST /visualization-explorer",
            "collection_hierarchy": "GET /collection-hierarchy",
            "shelfmark_documents": "GET /shelfmark/{shelfmark}/documents",
            "document": "GET /document/{doc_id}",
            "filters": "GET /filters",
            "indices": "GET /indices",
            "embedding_stats": "GET /embedding-stats",
            "health": "GET /health"
        },
        "visualization": {
            "description": "Set include_embeddings=true in search requests to get visualization data",
            "supported_methods": ["pca", "tsne"],
            "frontend_integration": "Use TSNEVisualization React component"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(8005),
        reload=os.getenv('ENVIRONMENT') == 'development'
    )