# Enhanced search_service.py with additional metadata fields

import os
import re
import numpy as np
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from google.cloud import aiplatform
import logging
import time
import json
from fastapi import HTTPException, Request, status
from embedding_client import embedding_client
from elasticsearch import Elasticsearch
from models.pydantic_core import FilterOptions

logger = logging.getLogger(__name__)

# Enhanced Pydantic models for API with additional metadata
class DocumentMetadata(BaseModel):
    """Rich document metadata matching new ES structure"""
    doc_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    period: Optional[str] = None
    date_info: Optional[Dict[str, Any]] = None
    location: Optional[str] = None
    material: Optional[str] = None
    dimensions: Optional[str] = None
    institution: Optional[str] = None
    library: Optional[str] = None
    collection: Optional[str] = None
    collection_type: Optional[str] = None
    shelfmark: Optional[str] = None
    shelf_mark: Optional[str] = None  # Added for compatibility
    document_types: Optional[List[str]] = None
    document_type: Optional[str] = None
    content_type: Optional[str] = None
    transcription_full_text: Optional[str] = None
    translation_full_text: Optional[str] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    actual_image_url: Optional[str] = None  # Added actual image URL
    tags: Optional[List[str]] = None
    has_images: Optional[bool] = None
    has_description: Optional[bool] = None
    has_transcriptions: Optional[bool] = None
    has_translations: Optional[bool] = None
    has_date: Optional[bool] = None
    has_bib: Optional[bool] = None  # Added bibliography flag
    has_joins: Optional[bool] = None  # Added joins flag
    joins_data: Optional[Dict[str, Any]] = None  # Joins data from index
    transcription_completeness: Optional[str] = None
    transcription_count: Optional[int] = None
    total_transcription_lines: Optional[int] = None
    translation_count: Optional[int] = None
    donation_year: Optional[str] = None
    donor_surnames: Optional[List[str]] = None
    source_institution: Optional[str] = None
    physical_location: Optional[str] = None
    classmark: Optional[str] = None
    provenance: Optional[str] = None
    original_url: Optional[str] = None  # Added original URL
    sub_collection: Optional[str] = None
    indexed_at: Optional[str] = None
    
    # New fields from schema
    source_collection: Optional[str] = None
    date_certainty: Optional[str] = None
    main_language: Optional[str] = None
    other_languages: Optional[List[str]] = None
    script_type: Optional[str] = None
    height: Optional[float] = None
    width: Optional[float] = None
    condition: Optional[str] = None
    extent: Optional[str] = None
    repository: Optional[str] = None
    named_entities: Optional[Dict[str, Any]] = None
    transcriptions: Optional[List[Dict[str, Any]]] = None  # Changed from List[str]
    translations: Optional[List[Dict[str, Any]]] = None   # Changed from List[str] 
    bibliography: Optional[List[Any]] = None
    image_urls: Optional[List[str]] = None
    completeness_score: Optional[float] = None
    content_quality: Optional[str] = None
    miscellaneous_info: Optional[str] = None
    index_name: Optional[str] = None


class SecondaryDocumentMetadata(BaseModel):
    """
    Metadata model for secondary source / bibliography documents
    """
    doc_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    authors: Optional[List[str]] = None
    author: Optional[str] = None
    date_display: Optional[str] = None
    date_start: Optional[str] = None
    date_end: Optional[str] = None
    extracted_page_number: Optional[Union[str, int]] = None
    footnotes: Optional[Union[Dict[str, Any], List[Any]]] = None
    isbn: Optional[str] = None
    page_number: Optional[int] = None
    primary_image_index: Optional[int] = None
    shelf_marks_mentioned: Optional[List[str]] = None
    subject_keywords: Optional[List[str]] = None
    image_urls: Optional[List[str]] = None
    actual_image_url: Optional[str] = None
    full_text_content: Optional[str] = None
    document_type: Optional[str] = None
    index_name: Optional[str] = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Search filters")
    num_results: Optional[int] = Field(default=10, ge=1, le=20, description="Number of results")
    include_embeddings: Optional[bool] = Field(default=False, description="Include embedding vectors for visualization")
    page: Optional[int] = Field(default=1, ge=1, description="Page number for pagination (1-based)")
    index_name: Optional[str] = Field(default=None, description="Elasticsearch index to search (defaults to configured index)")


class SearchResult(BaseModel):
    doc_id: str
    similarity_score: float
    distance: Optional[float] = None
    metadata: Optional[Union[DocumentMetadata, SecondaryDocumentMetadata]] = None
    embedding: Optional[List[float]] = None  # Added for t-SNE visualization


class EmbeddingData(BaseModel):
    """Embedding data for t-SNE visualization"""
    query_embedding: Optional[List[float]] = None
    result_embeddings: List[List[float]]
    dimension: int


class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: Optional[str] = None
    count: int  # count of results returned in this page
    filters_applied: Optional[Dict[str, Any]] = None
    processing_time_ms: float
    embedding_data: Optional[EmbeddingData] = None
    # Pagination metadata
    total: Optional[int] = None  # total matching documents across all pages
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_pages: Optional[int] = None
    has_more: Optional[bool] = None
    # Index information
    index_name: Optional[str] = None  # Name of the index that was searched


class ElasticsearchService:
    """Updated Elasticsearch service with enhanced metadata extraction"""

    def __init__(self):
        self.es_host = os.getenv('ELASTICSEARCH_HOST', 'elastic.cairogenizah.ai')
        self.es_port = os.getenv('ELASTICSEARCH_PORT', '443')
        self.index_name = os.getenv('ELASTICSEARCH_INDEX', 'cairo_genizah_text_only_v1.0.1')
        self.es = None
        self._initialize_elasticsearch()
    
    def _initialize_elasticsearch(self):
        """Initialize Elasticsearch connection for ES 8.x"""
        # ES 8.x connection
        self.es = Elasticsearch(
            [f"https://{self.es_host}:{self.es_port}"],
            basic_auth=(os.getenv('ELASTICSEARCH_USER', 'cairo_user'), os.getenv('ELASTICSEARCH_PASSWORD')),
            verify_certs=False,
        )

    def _build_filters(self, filters: Optional[Dict[str, Any]]) -> List[Dict]:
        """Convert search filters to Elasticsearch query clauses for new structure"""
        if not filters:
            return []

        filter_clauses = []

        # Updated field mappings for new ES structure
        filter_mappings = {
            'language': 'language',
            'main_language': 'main_language',
            'institution': 'institution',
            'library': 'library',
            'repository': 'repository',
            'collection': 'collection',
            'sub_collection': 'sub_collection',
            'collection_type': 'collection_type',
            'content_type': 'content_type',
            'document_type': 'document_type',
            'has_transcriptions': 'has_transcriptions',
            'has_bib': 'has_bib',
            'has_translations': 'has_translations',
            'has_images': 'has_images',
            'has_description': 'has_description',
            'has_date': 'has_date',
            # Note: has_joins is handled specially below to check both has_joins boolean and joins_data existence
            'transcription_completeness': 'transcription_completeness',
            'donation_year': 'donation_year',
            'source_institution': 'source_institution',
            'period': 'period',
            'physical_location': 'physical_location',
            'material': 'material',
            'script_type': 'script_type',
            'date_certainty': 'date_certainty'
        }

        for filter_key, es_field in filter_mappings.items():
            if filter_key in filters and filters[filter_key] is not None:
                value = filters[filter_key]

                # For text fields that might have .keyword variants, try both
                # This handles cases where the field might be text or keyword
                text_fields_that_need_keyword_fallback = [
                    'language', 'main_language', 'institution', 'library', 'repository',
                    'collection', 'sub_collection', 'collection_type', 'content_type',
                    'document_type', 'material', 'script_type'
                ]
                
                # Handle array fields
                if filter_key in ['document_types', 'donor_surnames', 'other_languages']:
                    if isinstance(value, list):
                        if filter_key in text_fields_that_need_keyword_fallback:
                            # Try both .keyword and regular field
                            filter_clauses.append({
                                "bool": {
                                    "should": [
                                        {"terms": {es_field: value}},
                                        {"terms": {f"{es_field}.keyword": value}}
                                    ],
                                    "minimum_should_match": 1
                                }
                            })
                        else:
                            filter_clauses.append({"terms": {es_field: value}})
                    else:
                        if filter_key in text_fields_that_need_keyword_fallback:
                            # Try both .keyword and regular field
                            filter_clauses.append({
                                "bool": {
                                    "should": [
                                        {"term": {es_field: value}},
                                        {"term": {f"{es_field}.keyword": value}}
                                    ],
                                    "minimum_should_match": 1
                                }
                            })
                        else:
                            filter_clauses.append({"term": {es_field: value}})
                # Handle other array or single values
                elif isinstance(value, list):
                    if filter_key in text_fields_that_need_keyword_fallback:
                        # Try both .keyword and regular field
                        filter_clauses.append({
                            "bool": {
                                "should": [
                                    {"terms": {es_field: value}},
                                    {"terms": {f"{es_field}.keyword": value}}
                                ],
                                "minimum_should_match": 1
                            }
                        })
                    else:
                        filter_clauses.append({"terms": {es_field: value}})
                else:
                    if filter_key in text_fields_that_need_keyword_fallback:
                        # Try both .keyword and regular field
                        filter_clauses.append({
                            "bool": {
                                "should": [
                                    {"term": {es_field: value}},
                                    {"term": {f"{es_field}.keyword": value}}
                                ],
                                "minimum_should_match": 1
                            }
                        })
                    else:
                        filter_clauses.append({"term": {es_field: value}})

        # Special handling for has_joins - check for existence of joins_data field if has_joins boolean not available
        if 'has_joins' in filters and filters['has_joins'] is not None:
            if filters['has_joins']:
                # Filter for documents that have joins data
                filter_clauses.append({
                    "bool": {
                        "should": [
                            {"term": {"has_joins": True}},
                            {"exists": {"field": "joins_data"}}
                        ],
                        "minimum_should_match": 1
                    }
                })
            # If has_joins is False, we don't add a filter (show all documents including those without joins)

        # Date range filtering
        if 'date_range' in filters:
            date_filter = filters['date_range']
            if 'start' in date_filter or 'end' in date_filter:
                range_query = {"range": {"indexed_at": {}}}
                if 'start' in date_filter:
                    range_query["range"]["indexed_at"]["gte"] = date_filter['start']
                if 'end' in date_filter:
                    range_query["range"]["indexed_at"]["lte"] = date_filter['end']
                filter_clauses.append(range_query)

        return filter_clauses

    def _format_dimensions(self, height: Optional[float], width: Optional[float]) -> Optional[str]:
        """Format dimensions for display"""
        if height is not None and width is not None:
            return f"{height} × {width} cm"
        elif height is not None:
            return f"H: {height} cm"
        elif width is not None:
            return f"W: {width} cm"
        return None

    def _generate_title(self, doc_id: str, metadata: Dict[str, Any]) -> str:
        """Generate a meaningful title from document ID and metadata"""
        # Clean up document ID for display
        clean_id = doc_id.replace("MS-TS-", "T-S ").replace("-", ".").replace("/", " Fragment ")

        # Use description if available
        if metadata.get('description'):
            # Extract first sentence of description for title
            desc = metadata['description']
            first_sentence = desc.split('.')[0]
            if len(first_sentence) < 100:
                return f"{clean_id}: {first_sentence}"

        # Fallback to language and document type
        language = metadata.get('language', metadata.get('main_language', ''))
        doc_type = metadata.get('document_type', '')

        title_parts = [clean_id]

        if doc_type:
            title_parts.append(doc_type.title())

        if language:
            if ';' in language:
                languages = [lang.strip() for lang in language.split(';')]
                lang_display = ' & '.join(languages)
            else:
                lang_display = language
            title_parts.append(f"({lang_display})")

        return " - ".join(title_parts) if len(title_parts) > 1 else title_parts[0]

    def _generate_description(self, metadata: Dict[str, Any]) -> str:
        """Use existing description or generate from metadata"""
        # Use existing description if available
        if metadata.get('description'):
            return metadata['description']

        # Fallback generation
        parts = []

        doc_type = metadata.get('document_type', 'document')
        language = metadata.get('language', metadata.get('main_language', ''))

        if language:
            if ';' in language:
                languages = [lang.strip() for lang in language.split(';')]
                lang_display = ' and '.join(languages)
            else:
                lang_display = language
            parts.append(f"A {doc_type} in {lang_display}")
        else:
            parts.append(f"A historical {doc_type}")

        parts.append("from the Cairo Genizah collection")

        institution = metadata.get('institution', metadata.get('repository', ''))
        if institution:
            institution_display = institution.replace('_', ' ').title()
            parts.append(f"housed at {institution_display}")

        return " ".join(parts) + "."

    # Removed _generate_image_urls - we now use raw URLs from Elasticsearch

    def _extract_tags(self, metadata: Dict[str, Any]) -> List[str]:
        """Extract tags from metadata"""
        tags = []

        # Add language tags
        if metadata.get('language'):
            languages = metadata['language'].split(';') if ';' in metadata['language'] else [metadata['language']]
            for lang in languages:
                tags.append(lang.strip().lower().replace(' ', '-'))

        if metadata.get('main_language'):
            tags.append(metadata['main_language'].lower())

        # Add other languages
        if metadata.get('other_languages'):
            for lang in metadata['other_languages']:
                tags.append(lang.lower().replace(' ', '-'))

        # Add document type tags
        if metadata.get('document_types'):
            tags.extend(metadata['document_types'])

        if metadata.get('document_type'):
            tags.append(metadata['document_type'])

        # Add collection tags
        if metadata.get('collection'):
            tags.append(metadata['collection'])
        if metadata.get('sub_collection'):
            tags.append(metadata['sub_collection'])
        if metadata.get('collection_type'):
            tags.append(metadata['collection_type'])
        if metadata.get('content_type'):
            tags.append(metadata['content_type'])

        # Add feature tags
        if metadata.get('has_images'):
            tags.append('illustrated')
        if metadata.get('has_transcriptions'):
            tags.append('transcribed')
        if metadata.get('has_translations'):
            tags.append('translated')
        if metadata.get('has_description'):
            tags.append('described')
        if metadata.get('has_bib'):
            tags.append('bibliography')

        # Add institutional tags
        if metadata.get('institution'):
            tags.append(metadata['institution'])
        if metadata.get('repository'):
            tags.append(metadata['repository'])
        if metadata.get('source_institution'):
            tags.append(metadata['source_institution'])

        # Add script type
        if metadata.get('script_type'):
            tags.append(metadata['script_type'])

        # Add material
        if metadata.get('material'):
            tags.append(metadata['material'].lower())

        # Add transcription completeness
        if metadata.get('transcription_completeness'):
            tags.append(f"transcription-{metadata['transcription_completeness']}")

        return list(set(tags))  # Remove duplicates
    
    @staticmethod
    def extract_text_field(field_value):
        """Handle fields that are now JSON arrays but used to be strings"""
        if field_value is None:
            return None
        if isinstance(field_value, list):
            # Join multiple transcriptions/translations with newlines
            return '\n\n'.join(str(item) for item in field_value if item) if field_value else None
        return str(field_value)  # Handle case where it's still a string
    


    def _extract_metadata(self, source: Dict[str, Any], index_name: Optional[str] = None) -> DocumentMetadata:
        """Extract metadata from ES source document"""
        # Handle bibliography field which can be a list of objects or strings
        bibliography_list = []
        bibliography_raw = source.get('bibliography', [])
        if bibliography_raw and isinstance(bibliography_raw, list):
            for bib in bibliography_raw:
                if isinstance(bib, dict):
                    # Try to construct a meaningful citation string
                    citation = (bib.get('citation') or 
                              bib.get('reference') or 
                              bib.get('text') or 
                              str(bib))
                    bibliography_list.append(citation)
                else:
                    bibliography_list.append(str(bib))

        # Handle dimensions which might be a string or object
        dimensions = source.get('dimensions')
        if isinstance(dimensions, dict):
            # If it's a dict (e.g. {"height": ..., "width": ...}), convert to string representation
            parts = []
            if dimensions.get('height'): parts.append(f"H: {dimensions['height']}")
            if dimensions.get('width'): parts.append(f"W: {dimensions['width']}")
            dimensions = ", ".join(parts) if parts else None

        # Handle description which might be a list
        description = source.get('description')
        if isinstance(description, list):
            description = " ".join([str(d) for d in description if d])

        # Handle transcription text
        transcription_text = source.get('transcription_full_text')
        transcriptions_raw = source.get('transcriptions') or source.get('transcription')
        
        if not transcription_text and transcriptions_raw:
            if isinstance(transcriptions_raw, list):
                texts = []
                for trans in transcriptions_raw:
                    if isinstance(trans, dict):
                        # Extract text from transcription objects
                        text = (trans.get('text') or 
                            trans.get('content') or 
                            trans.get('transcription') or 
                            trans.get('value') or 
                            str(trans))
                        texts.append(text)
                    else:
                        texts.append(str(trans))
                transcription_text = '\n\n'.join(texts) if texts else None
            else:
                transcription_text = str(transcriptions_raw)
            
        # Handle translation text
        translation_text = source.get('translation_full_text')
        translations_raw = source.get('translations') or source.get('translation')
        
        if not translation_text and translations_raw:
            if isinstance(translations_raw, list):
                texts = []
                for trans in translations_raw:
                    if isinstance(trans, dict):
                        # Extract text from translation objects
                        text = (trans.get('text') or 
                            trans.get('content') or 
                            trans.get('translation') or
                            trans.get('value') or
                            str(trans))
                        texts.append(text)
                    else:
                        texts.append(str(trans))
                translation_text = '\n\n'.join(texts) if texts else None
            else:
                translation_text = str(translations_raw)

        # Handle image URLs
        # Logic to extract the best image URL
        image_url = source.get('image_url')
        thumbnail_url = source.get('thumbnail_url')
        
        # Process tags - ensure it's a list of strings
        tags = source.get('tags', [])
        if tags and isinstance(tags, str):
            tags = [tags]
            
        # Process transcriptions/translations raw data
        transcriptions_raw = source.get('transcriptions')
        translations_raw = source.get('translations')
        
        doc_id = source.get('doc_id', 'Unknown')

        # Ensure image_urls is populated for primary sources
        image_urls = source.get('image_urls')
        if not image_urls:
            # Fallback to single image fields
            single_image = source.get('actual_image_url') or source.get('image_url')
            if single_image:
                image_urls = [single_image]

        return DocumentMetadata(
            doc_id=doc_id,
            title=source.get('title'),
            description=description,
            language=source.get('language'),
            main_language=source.get('main_language'),
            other_languages=source.get('other_languages'),
            period=source.get('period'),
            date_info=source.get('date_info'),
            location=source.get('physical_location'),
            material=source.get('material'),
            dimensions=dimensions,
            height=source.get('height'),
            width=source.get('width'),
            condition=source.get('condition'),
            extent=source.get('extent'),
            institution=source.get('institution'),
            repository=source.get('repository'),
            library=source.get('library'),
            collection=source.get('collection'),
            source_collection=source.get('source_collection'),
            collection_type=source.get('collection_type'),
            shelfmark=source.get('classmark', source.get('shelf_mark', doc_id)),
            shelf_mark=source.get('shelf_mark', source.get('classmark', doc_id)),
            document_types=source.get('document_types'),
            sub_collection=source.get('sub_collection'),
            bibliography=bibliography_list,
            transcription_full_text=transcription_text,
            translation_full_text=translation_text,
            miscellaneous_info=source.get('miscellaneous_info'),
            index_name=index_name,
            image_urls=image_urls,
            actual_image_url=source.get('actual_image_url') or source.get('image_url'),
            has_joins=source.get('has_joins'),
            joins_data=source.get('joins_data')
        )

    def _extract_secondary_metadata(self, source: Dict[str, Any], index_name: str) -> SecondaryDocumentMetadata:
        """Extract metadata for secondary source documents"""
        return SecondaryDocumentMetadata(
            doc_id=source.get('doc_id'),
            title=source.get('title'),
            description=source.get('description'),
            authors=source.get('authors'),
            author=source.get('author'),
            date_display=source.get('date_display'),
            date_end=source.get('date_end'),
            date_start=source.get('date_start'),
            extracted_page_number=source.get('extracted_page_number'),
            footnotes=source.get('footnotes'),
            isbn=source.get('isbn'),
            page_number=source.get('page_number'),
            primary_image_index=source.get('primary_image_index'),
            shelf_marks_mentioned=source.get('shelf_marks_mentioned'),
            subject_keywords=source.get('subject_keywords'),
            image_urls=source.get('image_urls'),
            actual_image_url=source.get('actual_image_url'),
            full_text_content=source.get('full_text_content'),
            document_type=source.get('document_type'),
            index_name=index_name
        )

    def generate_iiif_manifest(self, doc_id: str, index_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Generate a IIIF Presentation 2.1 manifest for a document"""
        document = self.get_document_by_id(doc_id, index_name)
        if not document:
            return None

        # Base URL for the API (should be configured properly in production)
        api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')

        # Get images
        images = []

        # Prioritize the list of all images
        if document.image_urls:
            # Clean URLs similar to frontend logic
            for url in document.image_urls:
                if url and isinstance(url, str):
                    cleaned = url.split()[0]
                    if cleaned and not cleaned.endswith('w'):
                        images.append(cleaned)

        if not images and document.image_url:
            images.append(document.image_url)

        if not images:
            # Fallback placeholder if really needed, or return empty manifest
            return None

        manifest_id = f"{api_base_url}/document/{doc_id}/manifest"

        canvases = []
        for i, img_url in enumerate(images):
            canvas_id = f"{manifest_id}/canvas/{i}"

            # Simple canvas generation without deep zoom tiles for now
            # In a real IIIF setup, we'd have an image server (IIIF Image API)
            # Here we are just pointing to static images (Level 0 compliance-ish)

            canvas = {
                "@id": canvas_id,
                "@type": "sc:Canvas",
                "label": f"Page {i + 1}",
                "height": 1000,  # Placeholder dimensions as we might not know them
                "width": 1000,
                "images": [
                    {
                        "@type": "oa:Annotation",
                        "motivation": "sc:painting",
                        "on": canvas_id,
                        "resource": {
                            "@id": img_url,
                            "@type": "dctypes:Image",
                            "format": "image/jpeg",
                            "height": 1000,
                            "width": 1000
                        }
                    }
                ]
            }
            canvases.append(canvas)

        manifest = {
            "@context": "http://iiif.io/api/presentation/2/context.json",
            "@id": manifest_id,
            "@type": "sc:Manifest",
            "label": document.title or f"Document {doc_id}",
            "description": document.description or "",
            "metadata": [
                {"label": "Shelfmark", "value": document.shelfmark or doc_id},
                {"label": "Collection", "value": document.collection or "Unknown"},
                {"label": "Language", "value": document.language or "Unknown"}
            ],
            "sequences": [
                {
                    "@id": f"{manifest_id}/sequence/normal",
                    "@type": "sc:Sequence",
                    "label": "Current Page Order",
                    "canvases": canvases
                }
            ]
        }

        return manifest

    def _get_document_embeddings(self, hits: List[Dict]) -> List[List[float]]:
        """Extract embedding vectors from Elasticsearch hits"""
        embeddings = []
        for hit in hits:
            # Get the embedding from the document source
            embedding = hit["_source"].get("embedding_vector", [])
            if embedding:
                embeddings.append(embedding)
            else:
                # If no embedding found, create a zero vector or skip
                logger.warning(f"No embedding found for document {hit['_source'].get('doc_id', 'unknown')}")
                # You might want to generate an embedding on the fly or use a default
                embeddings.append([0.0] * 768)  # Assuming 768-dimensional embeddings
        return embeddings

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Perform vector similarity search with optional embedding data for visualization"""
        start_time = time.time()

        try:
            # Generate query embedding using embedding service
            query_embedding = await embedding_client.get_embedding(
                request.query, image=None, use_cache=False
            )

            # Build filter clauses
            filter_clauses = self._build_filters(request.filters)

            # Build Elasticsearch query using script_score for vector similarity
            if filter_clauses:
                base_query = {"bool": {"filter": filter_clauses}}
            else:
                base_query = {"match_all": {}}

            # ES 8.x query structure
            query = {
                "script_score": {
                    "query": base_query,
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0",
                        "params": {"query_vector": query_embedding.flatten().tolist()}
                    }
                }
            }

            # Calculate pagination
            page_number = request.page or 1
            page_size = request.num_results or 10
            from_offset = (page_number - 1) * page_size

            # Use provided index or default to configured index
            search_index = request.index_name or self.index_name
            
            # Execute search using ES 8.x syntax
            response = self.es.search(
                index=search_index,
                query=query,
                size=page_size,
                from_=from_offset,
                _source=True  # Ensure we get the full source including embeddings
            )

            # Extract embeddings if requested
            embedding_data = None
            if request.include_embeddings and response['hits']['hits']:
                result_embeddings = self._get_document_embeddings(response['hits']['hits'])
                embedding_data = EmbeddingData(
                    query_embedding=query_embedding.flatten().tolist(),
                    result_embeddings=result_embeddings,
                    dimension=len(query_embedding.flatten())
                )

            # Format results with rich metadata
            results = []
            for hit in response['hits']['hits']:
                source = hit["_source"]
                metadata = self._extract_metadata(source)

                # Debug logging for image URLs
                logger.info(f"[SEARCH] Document {source.get('doc_id', hit['_id'])}:")
                logger.info(f"  - Has actual_image_url: {bool(source.get('actual_image_url'))}")
                logger.info(f"  - Has image_urls: {bool(source.get('image_urls'))}")
                logger.info(f"  - image_urls type: {type(source.get('image_urls'))}")
                logger.info(f"  - image_urls length: {len(source.get('image_urls', [])) if isinstance(source.get('image_urls'), list) else 'N/A'}")
                if source.get('image_urls'):
                    logger.info(f"  - image_urls value: {source.get('image_urls')}")

                # Include embedding in result if requested
                embedding = None
                if request.include_embeddings:
                    embedding = source.get("embedding_vector", [])

                doc_id = source.get("doc_id") or hit["_id"]

                results.append(SearchResult(
                    doc_id=doc_id,
                    similarity_score=round(hit["_score"] - 1.0, 4),
                    distance=round(2.0 - hit["_score"], 4),
                    metadata=metadata,
                    embedding=embedding
                ))

            processing_time = (time.time() - start_time) * 1000

            # Total hits for pagination
            total_hits_value = 0
            try:
                total_info = response.get('hits', {}).get('total')
                if isinstance(total_info, dict):
                    total_hits_value = int(total_info.get('value', 0))
                elif isinstance(total_info, int):
                    total_hits_value = int(total_info)
            except Exception:
                total_hits_value = 0

            total_pages = max(1, int(np.ceil(total_hits_value / page_size))) if page_size else 1
            has_more = (page_number * page_size) < total_hits_value

            return SearchResponse(
                results=results,
                query=request.query,
                count=len(results),
                filters_applied=request.filters,
                processing_time_ms=round(processing_time, 2),
                embedding_data=embedding_data,
                total=total_hits_value,
                page=page_number,
                page_size=page_size,
                total_pages=total_pages,
                has_more=has_more,
                index_name=search_index
            )

        except Exception as e:
            logger.error(f"Elasticsearch search failed: {e}")
            logger.error(f"Full ES error type: {type(e).__name__}")
            logger.error(f"Full ES error message: {str(e)}")
            
            if hasattr(e, 'info'):
                logger.error(f"ES error info: {json.dumps(e.info, indent=2)}")
            if hasattr(e, 'body'):
                logger.error(f"ES error body: {e.body}")
            if hasattr(e, 'status_code'):
                logger.error(f"ES status code: {e.status_code}")
                
                raise HTTPException(
                    status_code=500,
                    detail=f"Search failed: {str(e)}"
                )

    def get_document_by_id(self, doc_id: str, index_name: Optional[str] = None) -> Optional[Union[DocumentMetadata, SecondaryDocumentMetadata]]:
        """Get full document details by ID"""
        try:
            target_index = index_name or self.index_name
            
            # First: exact doc_id (keyword or text)
            response = self.es.search(
                index=target_index,
                query={
                    "bool": {
                        "should": [
                            {"term": {"doc_id": doc_id}},
                            {"term": {"doc_id.keyword": doc_id}}
                        ],
                        "minimum_should_match": 1
                    }
                },
                size=1
            )
            
            if response['hits']['total']['value'] > 0:
                source = response['hits']['hits'][0]['_source']
                
                # Check if this is a bibliography/secondary source index
                if 'bibliography' in target_index:
                    return self._extract_secondary_metadata(source, target_index)
                else:
                    return self._extract_metadata(source, target_index)
            # Second: try shelf/class marks and also ES _id
            response = self.es.search(
                index=target_index,
                query={
                    "bool": {
                        "should": [
                            {"ids": {"values": [doc_id]}},
                            {"term": {"shelf_mark.keyword": doc_id}},
                            {"term": {"shelf_mark": doc_id}},
                            {"term": {"shelfmark.keyword": doc_id}},
                            {"term": {"shelfmark": doc_id}},
                            {"term": {"classmark.keyword": doc_id}},
                            {"term": {"classmark": doc_id}},
                            {"match_phrase": {"shelf_mark": doc_id}},
                            {"match_phrase": {"shelfmark": doc_id}},
                            {"match_phrase": {"classmark": doc_id}}
                        ],
                        "minimum_should_match": 1
                    }
                },
                size=1
            )

            if response['hits']['total']['value'] > 0:
                source = response['hits']['hits'][0]['_source']
                return self._extract_metadata(source, target_index)

            return None

        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return None

    def get_filter_options(self) -> FilterOptions:
        """Get available filter options from the updated index"""
        try:
            # Simple aggregations - language is keyword, collection.keyword works
            aggs = {
                "languages": {"terms": {"field": "language", "size": 100}},
                "document_types": {"terms": {"field": "document_type.keyword", "size": 100}},
                "collections": {
                    "terms": {"field": "collection.keyword", "size": 100},
                    "aggs": {
                        "sub_collections": {
                            "terms": {"field": "sub_collection.keyword", "size": 100}
                        }
                    }
                }
            }

            response = self.es.search(
                index=self.index_name,
                size=0,
                aggs=aggs
            )

            aggregations = response.get("aggregations", {})
            
            # Extract languages (filter out empty/Unknown)
            languages = [
                bucket["key"] for bucket in aggregations.get("languages", {}).get("buckets", [])
                if bucket.get("key") and bucket["key"] != "Unknown" and str(bucket["key"]).strip()
            ]
            
            # Extract document types (filter out empty/Unknown)
            document_types = [
                bucket["key"] for bucket in aggregations.get("document_types", {}).get("buckets", [])
                if bucket.get("key") and bucket["key"] != "Unknown" and str(bucket["key"]).strip()
            ]
            
            # Extract collections (filter out empty/Unknown)
            collections = [
                bucket["key"] for bucket in aggregations.get("collections", {}).get("buckets", [])
                if bucket.get("key") and bucket["key"] != "Unknown" and str(bucket["key"]).strip()
            ]
            
            # Extract sub_collections grouped by collection
            sub_collections_dict = {}
            for coll_bucket in aggregations.get("collections", {}).get("buckets", []):
                collection_name = coll_bucket.get("key")
                if collection_name and collection_name != "Unknown" and str(collection_name).strip():
                    sub_collection_buckets = coll_bucket.get("sub_collections", {}).get("buckets", [])
                    if sub_collection_buckets:
                        sub_collections_dict[collection_name] = [
                            sub_bucket["key"] for sub_bucket in sub_collection_buckets
                            if sub_bucket.get("key") and sub_bucket["key"] != "Unknown" and str(sub_bucket["key"]).strip()
                        ]

            return FilterOptions(
                languages=languages,
                periods=['early_medieval', 'late_medieval', 'early_modern'],
                document_types=document_types,
                institutions=[],  # Removed - redundant with collection
                collections=collections,
                sub_collections=sub_collections_dict if sub_collections_dict else None
            )
        except Exception as e:
            logger.error(f"Could not get filter options from Elasticsearch: {e}", exc_info=True)
            return FilterOptions(
                languages=[],
                periods=['early_medieval', 'late_medieval', 'early_modern'],
                document_types=[],
                institutions=[],
                collections=[],
                sub_collections=None
            )

    @staticmethod
    def normalize_shelfmark(shelfmark: str) -> str:
        """
        Normalize shelf mark input for consistent searching.
        
        Collection-specific normalization rules:
        - "TS" -> "T-S" (for Cambridge/Taylor-Schechter collection)
        - "Rylands Genizah Fragment X" -> "Manchester: Rylands Genizah Fragment X" (for Manchester collection)
        - No universal rules - only specific collection mappings
        
        Args:
            shelfmark: Raw shelf mark string from user input
            
        Returns:
            Normalized shelf mark string
        """
        if not shelfmark:
            return shelfmark
        
        normalized = shelfmark.strip()
        original = normalized
        
        # Collection-specific normalization rules
        
        # 1. TS -> T-S normalization (for Cambridge/Taylor-Schechter)
        # Only apply if it looks like a TS shelf mark (starts with TS or T-S)
        if re.match(r'^T[-\s]?S\b', normalized, re.IGNORECASE):
            normalized = re.sub(r'\bTS\b', 'T-S', normalized, flags=re.IGNORECASE)
            normalized = re.sub(r'\bT-S\s+', 'T-S ', normalized, flags=re.IGNORECASE)
        
        # 2. Manchester/Rylands: Add "Manchester: " prefix if missing
        # Pattern: "Rylands Genizah Fragment X" or "Rylands Genizah fragment X"
        if re.match(r'^Rylands\s+Genizah\s+[Ff]ragment', normalized, re.IGNORECASE):
            if not re.match(r'^Manchester', normalized, re.IGNORECASE):
                normalized = f"Manchester: {normalized}"
        
        # 3. Other Manchester patterns (add more specific rules as needed)
        # Pattern: "Rylands" at start but not already prefixed with Manchester
        if re.match(r'^Rylands\s+', normalized, re.IGNORECASE):
            if not re.match(r'^Manchester', normalized, re.IGNORECASE):
                # Check if it's a known Rylands pattern
                if 'Genizah' in normalized or 'Fragment' in normalized:
                    normalized = f"Manchester: {normalized}"
        
        return normalized
    
    @staticmethod
    def get_search_variants(shelfmark: str) -> List[str]:
        """
        Get search variants for a shelf mark to help with liberal matching.
        
        Returns both the normalized version and variants that might match
        documents in the corpus. For example:
        - "Rylands Genizah Fragment 1" -> ["Manchester: Rylands Genizah Fragment 1", "Rylands Genizah Fragment 1"]
        - "T-S AS 1" -> ["T-S AS 1", "TS AS 1"]
        
        Args:
            shelfmark: Shelf mark string
            
        Returns:
            List of search variants to try
        """
        if not shelfmark:
            return [shelfmark]
        
        variants = set()
        normalized = shelfmark.strip()
        
        # Add normalized version
        normalized_version = ElasticsearchService.normalize_shelfmark(normalized)
        variants.add(normalized_version)
        variants.add(normalized)  # Also try original
        
        # Collection-specific variants
        
        # Manchester: If normalized added "Manchester: " prefix, also try without
        if normalized_version.startswith("Manchester: "):
            core = normalized_version[len("Manchester: "):].strip()
            variants.add(core)
            variants.add(f"Manchester {core}")  # Without colon
        
        # TS: Try both T-S and TS variants
        if re.search(r'\bT-S\b', normalized_version, re.IGNORECASE):
            variants.add(re.sub(r'\bT-S\b', 'TS', normalized_version, flags=re.IGNORECASE))
        if re.search(r'\bTS\b', normalized_version, re.IGNORECASE):
            variants.add(re.sub(r'\bTS\b', 'T-S', normalized_version, flags=re.IGNORECASE))
        
        return list(variants)

    async def search_by_shelfmark(self, request, index_name: Optional[str] = None) -> SearchResponse:
        """Search documents by shelf mark with exact or partial matching"""
        start_time = time.time()

        try:
            # Normalize the input shelf mark
            normalized_shelfmark = self.normalize_shelfmark(request.shelf_mark)
            logger.info(f"Normalized shelf mark: '{request.shelf_mark}' -> '{normalized_shelfmark}'")
            
            # For partial matching, get search variants to try
            search_variants = []
            if not request.exact_match:
                search_variants = self.get_search_variants(request.shelf_mark)
                # Remove duplicates and the normalized version (we'll add it separately)
                search_variants = [v for v in search_variants if v != normalized_shelfmark]
                if search_variants:
                    logger.info(f"Search variants for '{request.shelf_mark}': {search_variants}")
            
            # Build query based on exact_match preference
            # All queries are case-insensitive using match queries
            if request.exact_match:
                # Exact match query - use match queries for case-insensitive matching
                query = {
                    "bool": {
                        "should": [
                            {"match": {"shelf_mark": {"query": normalized_shelfmark, "operator": "and"}}},
                            {"match": {"shelfmark": {"query": normalized_shelfmark, "operator": "and"}}},
                            {"match": {"classmark": {"query": normalized_shelfmark, "operator": "and"}}},
                            {"match": {"doc_id": {"query": normalized_shelfmark, "operator": "and"}}},
                            # Also try term queries for exact keyword matches (case-sensitive fallback)
                            {"term": {"shelf_mark.keyword": normalized_shelfmark}},
                            {"term": {"shelfmark.keyword": normalized_shelfmark}},
                            {"term": {"classmark.keyword": normalized_shelfmark}},
                            {"term": {"doc_id": normalized_shelfmark}}
                        ],
                        "minimum_should_match": 1
                    }
                }
            else:
                # Partial match query - use case-insensitive match queries
                # Include the normalized shelfmark and all search variants for liberal matching
                should_clauses = []
                
                # Add case-insensitive match queries for the normalized shelfmark
                for field in ["shelf_mark", "shelfmark", "classmark", "doc_id"]:
                    # Use match query for case-insensitive partial matching
                    should_clauses.append({
                        "match": {
                            field: {
                                "query": normalized_shelfmark,
                                "operator": "or",
                                "fuzziness": "AUTO"
                            }
                        }
                    })
                    # Also try match_phrase for phrase matching (case-insensitive)
                    should_clauses.append({"match_phrase": {field: normalized_shelfmark}})
                    # Try wildcard with case-insensitive pattern (lowercase the pattern)
                    should_clauses.append({
                        "wildcard": {
                            field: {
                                "value": f"*{normalized_shelfmark.lower()}*",
                                "case_insensitive": True
                            }
                        }
                    })
                
                # Add queries for all search variants
                for variant in search_variants:
                    if variant and variant != normalized_shelfmark:
                        for field in ["shelf_mark", "shelfmark", "classmark", "doc_id"]:
                            should_clauses.append({
                                "match": {
                                    field: {
                                        "query": variant,
                                        "operator": "or",
                                        "fuzziness": "AUTO"
                                    }
                                }
                            })
                            should_clauses.append({"match_phrase": {field: variant}})
                            should_clauses.append({
                                "wildcard": {
                                    field: {
                                        "value": f"*{variant.lower()}*",
                                        "case_insensitive": True
                                    }
                                }
                            })
                
                query = {
                    "bool": {
                        "should": should_clauses,
                        "minimum_should_match": 1
                    }
                }

            # Use provided index or default to configured index
            search_index = index_name or self.index_name
            
            # Execute search
            response = self.es.search(
                index=search_index,
                query=query,
                size=request.num_results or 10,
                _source=True  # Ensure we get the full source including embeddings
            )

            # Extract embeddings if requested
            embedding_data = None
            include_embeddings = getattr(request, 'include_embeddings', False)
            if include_embeddings and response['hits']['hits']:
                result_embeddings = self._get_document_embeddings(response['hits']['hits'])
                # Note: No query embedding for shelf mark search
                if result_embeddings:
                    embedding_data = EmbeddingData(
                        query_embedding=None,
                        result_embeddings=result_embeddings,
                        dimension=len(result_embeddings[0]) if result_embeddings else 768
                    )

            # Format results
            results = []
            for hit in response['hits']['hits']:
                source = hit["_source"]
                metadata = self._extract_metadata(source)

                # Debug logging for image URLs
                logger.info(f"[SHELFMARK] Document {source.get('doc_id', hit['_id'])}:")
                logger.info(f"  - Has actual_image_url: {bool(source.get('actual_image_url'))}")
                logger.info(f"  - Has image_urls: {bool(source.get('image_urls'))}")
                logger.info(f"  - image_urls type: {type(source.get('image_urls'))}")
                logger.info(f"  - image_urls length: {len(source.get('image_urls', [])) if isinstance(source.get('image_urls'), list) else 'N/A'}")
                if source.get('image_urls'):
                    logger.info(f"  - image_urls value: {source.get('image_urls')}")

                doc_id = source.get("doc_id") or hit["_id"]

                # Calculate relevance score based on field match (use normalized shelfmark and variants)
                relevance_score = self._calculate_shelfmark_relevance(
                    source, normalized_shelfmark, request.exact_match, search_variants
                )

                # Include embedding in result if requested
                embedding = None
                if include_embeddings:
                    embedding = source.get("embedding_vector", [])

                results.append(SearchResult(
                    doc_id=doc_id,
                    similarity_score=relevance_score,
                    distance=1.0 - relevance_score,  # Convert to distance
                    metadata=metadata,
                    embedding=embedding
                ))

            processing_time = (time.time() - start_time) * 1000

            # Total hits for pagination
            total_hits_value = 0
            try:
                total_info = response.get('hits', {}).get('total')
                if isinstance(total_info, dict):
                    total_hits_value = int(total_info.get('value', 0))
                elif isinstance(total_info, int):
                    total_hits_value = int(total_info)
            except Exception:
                total_hits_value = 0

            return SearchResponse(
                results=results,
                query=f"Shelf mark: {request.shelf_mark}",
                count=len(results),
                filters_applied={"shelf_mark": request.shelf_mark, "exact_match": request.exact_match},
                processing_time_ms=round(processing_time, 2),
                embedding_data=embedding_data,
                total=total_hits_value,
                page=1,
                page_size=request.num_results or 10,
                total_pages=1,
                has_more=False,
                index_name=search_index
            )

        except Exception as e:
            logger.error(f"Shelf mark search failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Shelf mark search failed: {str(e)}"
            )

    def _calculate_shelfmark_relevance(self, source: Dict[str, Any], query: str, exact_match: bool, search_variants: Optional[List[str]] = None) -> float:
        """Calculate relevance score for shelf mark matches"""
        score = 0.0
        
        # Check each shelf mark field
        shelf_fields = ['shelf_mark', 'shelfmark', 'classmark', 'doc_id']
        
        for field in shelf_fields:
            field_value = source.get(field, '')
            if not field_value:
                continue
            
            field_value_lower = field_value.lower()
            query_lower = query.lower()
                
            if exact_match:
                if field_value == query:
                    # Exact match gets highest score
                    if field == 'shelf_mark':
                        score = max(score, 1.0)
                    elif field == 'shelfmark':
                        score = max(score, 0.95)
                    elif field == 'classmark':
                        score = max(score, 0.9)
                    elif field == 'doc_id':
                        score = max(score, 0.85)
            else:
                # Partial match scoring - check normalized query and all variants
                queries_to_check = [query]
                if search_variants:
                    queries_to_check.extend(search_variants)
                
                for q in queries_to_check:
                    if not q:
                        continue
                    q_lower = q.lower()
                    
                    # Check if query is contained in field value
                    if q_lower in field_value_lower:
                        # Calculate score based on how much of the query matches
                        match_ratio = len(q) / max(len(field_value), len(q))
                        field_score = match_ratio * 0.8  # Base score for partial match
                        
                        # Boost if it's an exact match (normalized or variant)
                        if q == query:
                            field_score = 0.9  # Higher score for normalized match
                        elif field_value_lower == q_lower:
                            field_score = 1.0  # Highest score for exact match
                        
                        # Boost score based on field priority
                        if field == 'shelf_mark':
                            field_score *= 1.0
                        elif field == 'shelfmark':
                            field_score *= 0.95
                        elif field == 'classmark':
                            field_score *= 0.9
                        elif field == 'doc_id':
                            field_score *= 0.85
                        
                        score = max(score, field_score)
        
        return min(score, 1.0)  # Cap at 1.0

    async def search_by_keyword(self, request, index_name: Optional[str] = None) -> SearchResponse:
        """Search documents by keywords in text fields"""
        start_time = time.time()

        try:
            # Build keyword query that searches across multiple text fields
            query = {
                "multi_match": {
                    "query": request.query,
                    "fields": [
                        "transcription_full_text^3.0",
                        "translation_full_text^2.5", 
                        "description^2.0",
                        "title^2.5",
                        "document_type^1.5",
                        "content_type^1.5",
                        "collection^1.2",
                        "language^1.2",
                        "script_type^1.1",
                        "material^1.0"
                    ],
                "type": "best_fields",
                "fuzziness": "AUTO",
                "boost": 1.0
            }
        }

            # Calculate pagination
            page_number = request.page or 1
            page_size = request.num_results or 10
            from_offset = (page_number - 1) * page_size

            # Use provided index or default to configured index
            search_index = index_name or self.index_name
            
            # Execute search
            response = self.es.search(
                index=search_index,
                query=query,
                size=page_size,
                from_=from_offset,
                _source=True
            )

            # Format results
            results = []
            for hit in response['hits']['hits']:
                source = hit["_source"]
                metadata = self._extract_metadata(source)

                # Debug logging for image URLs
                logger.info(f"[KEYWORD] Document {source.get('doc_id', hit['_id'])}:")
                logger.info(f"  - Has actual_image_url: {bool(source.get('actual_image_url'))}")
                logger.info(f"  - Has image_urls: {bool(source.get('image_urls'))}")
                logger.info(f"  - image_urls type: {type(source.get('image_urls'))}")
                logger.info(f"  - image_urls length: {len(source.get('image_urls', [])) if isinstance(source.get('image_urls'), list) else 'N/A'}")
                if source.get('image_urls'):
                    logger.info(f"  - image_urls value: {source.get('image_urls')}")

                doc_id = source.get("doc_id") or hit["_id"]

                results.append(SearchResult(
                    doc_id=doc_id,
                    similarity_score=round(hit["_score"], 4),
                    distance=round(max(0, 10.0 - hit["_score"]), 4),  # Convert to distance-like metric
                    metadata=metadata,
                    embedding=None  # No embeddings for keyword search
                ))

            processing_time = (time.time() - start_time) * 1000

            # Total hits for pagination
            total_hits_value = 0
            try:
                total_info = response.get('hits', {}).get('total')
                if isinstance(total_info, dict):
                    total_hits_value = int(total_info.get('value', 0))
                elif isinstance(total_info, int):
                    total_hits_value = int(total_info)
            except Exception:
                total_hits_value = 0

            total_pages = max(1, int(np.ceil(total_hits_value / page_size))) if page_size else 1
            has_more = (page_number * page_size) < total_hits_value

            return SearchResponse(
                results=results,
                query=request.query,
                count=len(results),
                filters_applied={"search_type": "keyword"},
                processing_time_ms=round(processing_time, 2),
                embedding_data=None,  # No embeddings for keyword search
                total=total_hits_value,
                page=page_number,
                page_size=page_size,
                total_pages=total_pages,
                has_more=has_more,
                index_name=search_index
            )

        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Keyword search failed: {str(e)}"
            )

    async def get_visualization_explorer_data(self, request, index_name: Optional[str] = None) -> SearchResponse:
        """
        Load documents for visualization explorer
        
        Loads a random sample of documents from the collection for full-page
        visualization exploration. Supports loading a configurable number of
        documents or the entire index.
        
        Args:
            request: VisualizationExplorerRequest with configuration
            index_name: Optional name of the Elasticsearch index to use
        """
        start_time = time.time()
        
        # Use provided index_name or fall back to default
        target_index = index_name if index_name else self.index_name
        
        try:
            # Determine how many documents to load
            if request.load_full_index:
                # Get total document count
                stats = self.es.indices.stats(index=target_index)
                total_docs = stats['indices'][target_index]['total']['docs']['count']
                num_docs_to_load = total_docs
            else:
                num_docs_to_load = min(request.num_documents, 10000)  # Cap at 10k for performance
            
            logger.info(f"Loading {num_docs_to_load} documents from index {target_index} for visualization explorer")
            
            # Use scroll API for large result sets
            if num_docs_to_load > 1000:
                # For large sets, use scroll API
                query = {
                    "match_all": {}
                }
                
                # Initial search
                response = self.es.search(
                    index=target_index,
                    query=query,
                    size=min(1000, num_docs_to_load),  # ES scroll size limit
                    scroll='5m',
                    _source=True
                )
                
                all_hits = response['hits']['hits']
                scroll_id = response.get('_scroll_id')
                
                # Continue scrolling if we need more documents
                while len(all_hits) < num_docs_to_load and scroll_id:
                    scroll_response = self.es.scroll(
                        scroll_id=scroll_id,
                        scroll='5m'
                    )
                    
                    hits = scroll_response['hits']['hits']
                    if not hits:
                        break
                    
                    all_hits.extend(hits)
                    
                    # Update scroll_id for next iteration
                    scroll_id = scroll_response.get('_scroll_id')
                    
                    # Safety check to prevent infinite loops
                    if len(all_hits) >= num_docs_to_load:
                        break
                
                # Clear scroll context
                if scroll_id:
                    self.es.clear_scroll(scroll_id=scroll_id)
                
                # Limit to requested number
                all_hits = all_hits[:num_docs_to_load]
                
            else:
                # For smaller sets, use regular search with random sampling
                query = {
                    "function_score": {
                        "query": {"match_all": {}},
                        "random_score": {}
                    }
                }
                
                response = self.es.search(
                    index=target_index,
                    query=query,
                    size=num_docs_to_load,
                    _source=True
                )
                
                all_hits = response['hits']['hits']
            
            # Extract embeddings if requested
            embedding_data = None
            if request.include_embeddings and all_hits:
                result_embeddings = self._get_document_embeddings(all_hits)
                embedding_data = EmbeddingData(
                    query_embedding=None,  # No query for explorer mode
                    result_embeddings=result_embeddings,
                    dimension=len(result_embeddings[0]) if result_embeddings else 128
                )
            
            # Format results with rich metadata
            results = []
            for hit in all_hits:
                doc_id = hit['_id']
                source = hit['_source']
                
                # Extract appropriate metadata based on index type
                if 'bibliography' in target_index:
                    metadata = self._extract_secondary_metadata(source, target_index)
                else:
                    metadata = self._extract_metadata(source, target_index)
                
                # Create search result
                search_result = SearchResult(
                    doc_id=doc_id,
                    similarity_score=1.0,  # All documents have equal weight in explorer
                    metadata=metadata,
                    embedding=source.get('embedding_vector') if request.include_embeddings else None
                )
                results.append(search_result)
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return SearchResponse(
                results=results,
                count=len(results),
                processing_time_ms=processing_time_ms,
                embedding_data=embedding_data,
                page=1,
                page_size=len(results),
                total_pages=1,
                has_more=False,
                index_name=target_index
            )
            
        except Exception as e:
            logger.error(f"Visualization explorer data loading failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load visualization explorer data: {str(e)}"
            )

    async def search_hybrid(self, request, index_name: Optional[str] = None) -> SearchResponse:
        """Perform hybrid search combining semantic and keyword search with configurable weights"""
        start_time = time.time()

        try:
            # Normalize weights to 0-1 range
            semantic_weight = request.semanticWeight / 100.0
            keyword_weight = request.keywordWeight / 100.0
            
            # Generate query embedding for semantic search
            query_embedding = await embedding_client.get_embedding(
                request.query, image=None, use_cache=False
            )

            # Build filter clauses
            filter_clauses = self._build_filters(request.filters)

            # Build base query with filters
            if filter_clauses:
                base_query = {"bool": {"filter": filter_clauses}}
            else:
                base_query = {"match_all": {}}

            # Create semantic search query
            semantic_query = {
                "script_score": {
                    "query": base_query,
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0",
                        "params": {"query_vector": query_embedding.flatten().tolist()}
                    }
                }
            }

            # Create keyword search query
            keyword_query = {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": request.query,
                                "fields": [
                                    "transcription_full_text^3.0",
                                    "translation_full_text^2.5", 
                                    "description^2.0",
                                    "title^2.5",
                                    "document_type^1.5",
                                    "content_type^1.5",
                                    "collection^1.2",
                                    "language^1.2",
                                    "script_type^1.1",
                                    "material^1.0"
                                ],
                                "type": "best_fields",
                                "fuzziness": "AUTO",
                                "boost": 1.0
                            }
                        }
                    ],
                    "filter": filter_clauses
                }
            }

            # Combine both queries with weights using function_score
            hybrid_query = {
                "function_score": {
                    "query": base_query,
                    "functions": [
                        {
                            "filter": {"match_all": {}},
                            "weight": semantic_weight,
                            "script_score": {
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0",
                                    "params": {"query_vector": query_embedding.flatten().tolist()}
                                }
                            }
                        },
                        {
                            "filter": {
                                "multi_match": {
                                    "query": request.query,
                                    "fields": [
                                        "transcription_full_text^3.0",
                                        "translation_full_text^2.5", 
                                        "description^2.0",
                                        "title^2.5",
                                        "document_type^1.5",
                                        "content_type^1.5",
                                        "collection^1.2",
                                        "language^1.2",
                                        "script_type^1.1",
                                        "material^1.0"
                                    ],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO"
                                }
                            },
                            "weight": keyword_weight
                        }
                    ],
                    "score_mode": "sum",
                    "boost_mode": "multiply"
                }
            }

            # Calculate pagination
            page_number = request.page or 1
            page_size = request.num_results or 10
            from_offset = (page_number - 1) * page_size

            # Use provided index or default to configured index
            search_index = index_name or self.index_name
            
            # Execute search
            response = self.es.search(
                index=search_index,
                query=hybrid_query,
                size=page_size,
                from_=from_offset,
                _source=True
            )

            # Extract embeddings if requested
            embedding_data = None
            if request.include_embeddings and response['hits']['hits']:
                result_embeddings = self._get_document_embeddings(response['hits']['hits'])
                embedding_data = EmbeddingData(
                    query_embedding=query_embedding.flatten().tolist(),
                    result_embeddings=result_embeddings,
                    dimension=len(query_embedding.flatten())
                )

            # Format results with rich metadata
            results = []
            for hit in response['hits']['hits']:
                source = hit["_source"]
                metadata = self._extract_metadata(source)

                # Debug logging for image URLs
                logger.info(f"[HYBRID] Document {source.get('doc_id', hit['_id'])}:")
                logger.info(f"  - Has actual_image_url: {bool(source.get('actual_image_url'))}")
                logger.info(f"  - Has image_urls: {bool(source.get('image_urls'))}")
                logger.info(f"  - image_urls type: {type(source.get('image_urls'))}")
                logger.info(f"  - image_urls length: {len(source.get('image_urls', [])) if isinstance(source.get('image_urls'), list) else 'N/A'}")
                if source.get('image_urls'):
                    logger.info(f"  - image_urls value: {source.get('image_urls')}")

                # Include embedding in result if requested
                embedding = None
                if request.include_embeddings:
                    embedding = source.get("embedding_vector", [])

                doc_id = source.get("doc_id") or hit["_id"]

                results.append(SearchResult(
                    doc_id=doc_id,
                    similarity_score=round(hit["_score"], 4),
                    distance=round(max(0, 10.0 - hit["_score"]), 4),  # Convert to distance-like metric
                    metadata=metadata,
                    embedding=embedding
                ))

            processing_time = (time.time() - start_time) * 1000

            # Total hits for pagination
            total_hits_value = 0
            try:
                total_info = response.get('hits', {}).get('total')
                if isinstance(total_info, dict):
                    total_hits_value = int(total_info.get('value', 0))
                elif isinstance(total_info, int):
                    total_hits_value = int(total_info)
            except Exception:
                total_hits_value = 0

            total_pages = max(1, int(np.ceil(total_hits_value / page_size))) if page_size else 1
            has_more = (page_number * page_size) < total_hits_value

            return SearchResponse(
                results=results,
                query=f"Hybrid: {request.query} (Semantic: {request.semanticWeight}%, Keyword: {request.keywordWeight}%)",
                count=len(results),
                filters_applied=request.filters,
                processing_time_ms=round(processing_time, 2),
                embedding_data=embedding_data,
                total=total_hits_value,
                page=page_number,
                page_size=page_size,
                total_pages=total_pages,
                has_more=has_more,
                index_name=search_index
            )

        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            logger.error(f"Full hybrid search error type: {type(e).__name__}")
            logger.error(f"Full hybrid search error message: {str(e)}")
            
            if hasattr(e, 'info'):
                logger.error(f"Hybrid search error info: {json.dumps(e.info, indent=2)}")
            if hasattr(e, 'body'):
                logger.error(f"Hybrid search error body: {e.body}")
            if hasattr(e, 'status_code'):
                logger.error(f"Hybrid search status code: {e.status_code}")
                
            raise HTTPException(
                status_code=500,
                detail=f"Hybrid search failed: {str(e)}"
            )

    def get_available_indices(self) -> List[Dict[str, Any]]:
        """Get list of available Elasticsearch indices"""
        try:
            # Get all indices
            indices = self.es.cat.indices(format='json')
            
            # Filter for relevant indices (those that look like document collections)
            relevant_indices = []
            for index_info in indices:
                index_name = index_info.get('index', '')
                # Skip system indices and hidden indices, but be more permissive
                if (not index_name.startswith('.') and 
                    not index_name.startswith('_') and
                    len(index_name) > 0):
                    
                    doc_count = int(index_info.get('docs.count', 0))
                    # Include indices with documents, or the default index even if empty
                    if doc_count > 0 or index_name == self.index_name:
                        relevant_indices.append({
                            "name": index_name,
                            "document_count": doc_count,
                            "size": index_info.get('store.size', 'unknown'),
                            "is_default": index_name == self.index_name,
                            "description": self._get_index_description(index_name)
                        })
            
            # Sort by document count (descending) and put default first
            relevant_indices.sort(key=lambda x: (not x['is_default'], -x['document_count']))
            
            return relevant_indices
            
        except Exception as e:
            logger.error(f"Failed to get available indices: {e}")
            # Return default index if we can't get the list
            return [{
                "name": self.index_name,
                "document_count": 0,
                "size": "unknown",
                "is_default": True,
                "description": "Default production index"
            }]
    
    def _get_index_description(self, index_name: str) -> str:
        """Generate a description for an index based on its name"""
        name_lower = index_name.lower()
        
        if 'prod' in name_lower or 'production' in name_lower:
            return "Production index with stable data"
        elif 'test' in name_lower or 'experimental' in name_lower:
            return "Test/experimental index for development"
        elif 'v1' in name_lower or 'v2' in name_lower:
            return f"Versioned index ({index_name})"
        elif 'text_only' in name_lower:
            return "Text-only index (no images)"
        elif 'full' in name_lower:
            return "Full index with all metadata"
        else:
            return f"Custom index: {index_name}"

    def get_stats(self):
        """Get index statistics"""
        try:
            stats = self.es.indices.stats(index=self.index_name)
            doc_count = stats['indices'][self.index_name]['total']['docs']['count']
            return {
                "status": "healthy",
                "document_count": doc_count,
                "backend": "elasticsearch",
                "index_name": self.index_name
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "backend": "elasticsearch"
            }

    def _group_shelfmarks_by_range(self, shelfmarks: List[Dict[str, Any]], range_size: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group shelfmarks by numeric ranges based on their numbering.
        For example: A-100 to A-199 -> "A-100", A-200 to A-299 -> "A-200", etc.
        
        Args:
            shelfmarks: List of shelfmark dicts with 'name' and 'count' keys
            range_size: Size of each range (default 100)
        
        Returns:
            Dict mapping range names to lists of shelfmarks in that range
        """
        ranges = {}
        
        for shelfmark in shelfmarks:
            name = shelfmark.get("name", "")
            if not name:
                continue
            
            # Try to extract numeric part from shelfmark
            # Patterns like: A-100, A-101, B-2000, MS-TS-NS-144.1, etc.
            # Extract the last numeric sequence
            match = re.search(r'(\d+)(?:\.\d+)?$', name)
            if not match:
                # No numeric part found, put in "Other" range
                range_key = "Other"
                if range_key not in ranges:
                    ranges[range_key] = []
                ranges[range_key].append(shelfmark)
                continue
            
            number = int(match.group(1))
            # Get the prefix (everything before the number)
            prefix = name[:match.start()]
            
            # Calculate which range this belongs to (round down to nearest range_size)
            range_start = (number // range_size) * range_size
            range_end = range_start + range_size - 1
            
            # Create range key like "A-100" or "B-2000"
            if prefix:
                range_key = f"{prefix}{range_start}"
            else:
                range_key = f"{range_start}"
            
            # Also store the range display name
            range_display = f"{prefix}{range_start}-{range_end}" if prefix else f"{range_start}-{range_end}"
            
            if range_key not in ranges:
                ranges[range_key] = {
                    "name": range_display,
                    "range_start": range_start,
                    "range_end": range_end,
                    "shelfmarks": []
                }
            
            ranges[range_key]["shelfmarks"].append(shelfmark)
        
        # Convert to list format with counts
        result = {}
        for range_key, range_data in ranges.items():
            if isinstance(range_data, dict) and "shelfmarks" in range_data:
                shelfmark_list = range_data["shelfmarks"]
                total_count = sum(s.get("count", 0) for s in shelfmark_list)
                result[range_key] = {
                    "name": range_data["name"],
                    "range_start": range_data["range_start"],
                    "range_end": range_data["range_end"],
                    "count": total_count,
                    "shelfmarks": shelfmark_list
                }
            else:
                # Handle "Other" case
                total_count = sum(s.get("count", 0) for s in range_data)
                result[range_key] = {
                    "name": "Other",
                    "range_start": None,
                    "range_end": None,
                    "count": total_count,
                    "shelfmarks": range_data
                }
        
        return result

    def get_collection_hierarchy(self, index_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get collection hierarchy using Elasticsearch aggregations
        Returns structure: collection -> sub_collection -> shelfmarks (or sub_sub_collections if > 1000 shelfmarks)
        
        This is very fast because it uses aggregations which are optimized
        in Elasticsearch.
        
        For sub-collections with > 1000 shelfmarks, they are automatically grouped
        into sub-sub-collections by numeric ranges (e.g., A-100, A-200, etc.)
        """
        try:
            target_index = index_name or self.index_name
            
            # Try multiple field name variations to handle different index mappings.
            # Use collection and sub_collection fields (NOT source_collection - that's old/incorrect metadata)
            field_variations = [
                ("collection.keyword", "sub_collection.keyword", "shelf_mark.keyword"),
                ("collection.keyword", "sub_collection.keyword", "shelfmark.keyword"),
                ("collection.keyword", "sub_collection.keyword", "classmark.keyword"),
                ("collection", "sub_collection", "shelf_mark"),
                ("collection", "sub_collection", "shelfmark"),
                ("collection", "sub_collection", "classmark"),
            ]
            
            for coll_field, sub_coll_field, shelf_field in field_variations:
                try:
                    # Use nested aggregations for collection -> sub_collection -> shelfmarks
                    aggs = {
                        "collections": {
                            "terms": {
                                "field": coll_field,
                                "size": 100,
                                "missing": "Unknown"  # Handle missing values
                            },
                            "aggs": {
                                "shelfmarks_direct": {
                                    "terms": {
                                        "field": shelf_field,
                                        "size": 2000,
                                        "min_doc_count": 1
                                    }
                                },
                                "sub_collections": {
                                    "terms": {
                                        "field": sub_coll_field,
                                        "size": 100,
                                        "missing": "Unknown"
                                    },
                                    "aggs": {
                                        "shelfmarks": {
                                            "terms": {
                                                "field": shelf_field,
                                                "size": 2000,
                                                "min_doc_count": 1
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                    response = self.es.search(
                        index=target_index,
                        size=0,  # We don't need actual documents, just aggregations
                        query={"match_all": {}},  # Explicitly match all documents
                        aggs=aggs
                    )
                    
                    # Process aggregation results
                    hierarchy = {}
                    collection_buckets = response['aggregations']['collections']['buckets']
                    
                    # Debug logging to understand why shelfmarks are empty
                    if collection_buckets and len(collection_buckets) > 0:
                        first_collection = collection_buckets[0]
                        logger.info(f"First collection: {first_collection.get('key')}, doc_count: {first_collection.get('doc_count')}")
                        if 'sub_collections' in first_collection:
                            sub_cols = first_collection.get('sub_collections', {}).get('buckets', [])
                            if sub_cols:
                                first_sub = sub_cols[0]
                                logger.info(f"First sub-collection: {first_sub.get('key')}, doc_count: {first_sub.get('doc_count')}")
                                logger.info(f"Sub-collection aggregation keys: {list(first_sub.keys())}")
                                shelfmarks_agg = first_sub.get('shelfmarks', {})
                                if shelfmarks_agg:
                                    buckets = shelfmarks_agg.get('buckets', [])
                                    logger.info(f"Shelfmarks aggregation returned {len(buckets)} buckets for sub-collection '{first_sub.get('key')}' using field '{shelf_field}'")
                                    if len(buckets) == 0:
                                        logger.warning(f"No shelfmark buckets found! Field '{shelf_field}' may not exist, be empty, or have wrong mapping.")
                                        # Try to get a sample document to see what fields exist
                                        try:
                                            sample_query = {
                                                "bool": {
                                                    "must": [
                                                        {"term": {coll_field: first_collection.get('key')}},
                                                        {"term": {sub_coll_field: first_sub.get('key')}}
                                                    ]
                                                }
                                            }
                                            sample_resp = self.es.search(
                                                index=target_index,
                                                size=1,
                                                query=sample_query,
                                                _source=True
                                            )
                                            if sample_resp.get('hits', {}).get('hits'):
                                                sample_doc = sample_resp['hits']['hits'][0]['_source']
                                                logger.info(f"Sample document fields: {list(sample_doc.keys())}")
                                                logger.info(f"Sample doc shelf_mark: {sample_doc.get('shelf_mark')}, shelfmark: {sample_doc.get('shelfmark')}, classmark: {sample_doc.get('classmark')}")
                                        except Exception as e:
                                            logger.warning(f"Failed to get sample document: {e}")
                                else:
                                    logger.warning(f"No 'shelfmarks' aggregation found in sub-collection structure! Available keys: {list(first_sub.keys())}")
                    
                    for collection_bucket in collection_buckets:
                        collection_name = collection_bucket['key'] or "Unknown"
                        collection_count = collection_bucket['doc_count']
                        
                        # Process sub_collections
                        sub_collections = {}
                        sub_collection_buckets = collection_bucket.get('sub_collections', {}).get('buckets', [])
                        
                        # If we have sub_collections, use them
                        if sub_collection_buckets:
                            for sub_collection_bucket in sub_collection_buckets:
                                sub_collection_name = sub_collection_bucket['key'] or "Unknown"
                                sub_collection_count = sub_collection_bucket['doc_count']
                                
                                # Process shelfmarks
                                shelfmarks = []
                                shelfmark_buckets = sub_collection_bucket.get('shelfmarks', {}).get('buckets', [])
                                
                                for shelfmark_bucket in shelfmark_buckets:
                                    shelfmark_name = shelfmark_bucket['key'] or "Unknown"
                                    shelfmark_count = shelfmark_bucket['doc_count']
                                    
                                    shelfmarks.append({
                                        "name": shelfmark_name,
                                        "count": shelfmark_count
                                    })
                                
                                if sub_collection_name and sub_collection_name != "Unknown":
                                    shelfmark_count = len(shelfmarks)
                                    
                                    # If aggregation returned no shelfmarks but we have many documents,
                                    # try to fetch shelfmarks using get_shelfmark_distribution
                                    if shelfmark_count == 0 and sub_collection_count > 1000:
                                        logger.info(f"No shelfmarks from aggregation for '{sub_collection_name}', "
                                                   f"fetching directly (docs: {sub_collection_count})")
                                        try:
                                            dist = self.get_shelfmark_distribution(
                                                collection_name, 
                                                sub_collection_name, 
                                                index_name=target_index,
                                                size=10000  # Get more shelfmarks
                                            )
                                            if dist.get("buckets"):
                                                shelfmarks = [{
                                                    "name": b.get("key"),
                                                    "count": b.get("doc_count", 0)
                                                } for b in dist["buckets"] if b.get("key")]
                                                shelfmark_count = len(shelfmarks)
                                                logger.info(f"Fetched {shelfmark_count} shelfmarks for '{sub_collection_name}'")
                                        except Exception as e:
                                            logger.warning(f"Failed to fetch shelfmarks for '{sub_collection_name}': {e}")
                                    
                                    # If sub-collection has > 500 shelfmarks OR > 1000 documents, group into sub-sub-collections
                                    should_group = shelfmark_count > 500 or sub_collection_count > 1000
                                    
                                    if should_group:
                                        logger.info(f"Grouping large sub-collection '{sub_collection_name}' "
                                                   f"(shelfmarks: {shelfmark_count}, docs: {sub_collection_count})")
                                        if shelfmark_count > 0:
                                            sub_sub_collections = self._group_shelfmarks_by_range(shelfmarks, range_size=100)
                                            logger.info(f"Created {len(sub_sub_collections)} sub-sub-collections for '{sub_collection_name}'")
                                            sub_collections[sub_collection_name] = {
                                                "name": sub_collection_name,
                                                "count": sub_collection_count,
                                                "shelfmarks": [],  # Empty - use sub_sub_collections instead
                                                "sub_sub_collections": sub_sub_collections,
                                                "is_large": True
                                            }
                                        else:
                                            # No shelfmarks found, but large collection - mark as large but no sub-sub-collections
                                            logger.warning(f"Large sub-collection '{sub_collection_name}' has no shelfmarks to group")
                                            sub_collections[sub_collection_name] = {
                                                "name": sub_collection_name,
                                                "count": sub_collection_count,
                                                "shelfmarks": [],
                                                "is_large": True
                                            }
                                    else:
                                        sub_collections[sub_collection_name] = {
                                            "name": sub_collection_name,
                                            "count": sub_collection_count,
                                            "shelfmarks": shelfmarks,
                                            "is_large": False
                                        }
                        
                        # If no sub_collections, use shelfmarks directly under collection
                        if not sub_collections:
                            shelfmarks_direct = []
                            shelfmark_buckets_direct = collection_bucket.get('shelfmarks_direct', {}).get('buckets', [])
                            
                            for shelfmark_bucket in shelfmark_buckets_direct:
                                shelfmark_name = shelfmark_bucket['key'] or "Unknown"
                                shelfmark_count = shelfmark_bucket['doc_count']
                                
                                shelfmarks_direct.append({
                                    "name": shelfmark_name,
                                    "count": shelfmark_count
                                })
                            
                            # Create a default sub-collection for direct shelfmarks
                            if shelfmarks_direct:
                                # If direct shelfmarks > 1000 OR collection has > 1000 docs, group into sub-sub-collections
                                shelfmark_count = len(shelfmarks_direct)
                                should_group = shelfmark_count > 1000 or collection_count > 1000
                                
                                if should_group:
                                    logger.info(f"Grouping large direct shelfmarks collection "
                                               f"(shelfmarks: {shelfmark_count}, docs: {collection_count})")
                                    sub_sub_collections = self._group_shelfmarks_by_range(shelfmarks_direct, range_size=100)
                                    logger.info(f"Created {len(sub_sub_collections)} sub-sub-collections for direct shelfmarks")
                                    sub_collections["_all"] = {
                                        "name": "All Shelfmarks",
                                        "count": collection_count,
                                        "shelfmarks": [],
                                        "sub_sub_collections": sub_sub_collections,
                                        "is_large": True
                                    }
                                else:
                                    sub_collections["_all"] = {
                                        "name": "All Shelfmarks",
                                        "count": collection_count,
                                        "shelfmarks": shelfmarks_direct,
                                        "is_large": False
                                    }
                        
                        hierarchy[collection_name] = {
                            "name": collection_name,
                            "count": collection_count,
                            "sub_collections": sub_collections
                        }
                    
                    # If we got results, return them
                    if hierarchy:
                        logger.info(f"Successfully built hierarchy using fields: {coll_field}, {sub_coll_field}, {shelf_field}")
                        return hierarchy
                    
                except Exception as e:
                    logger.warning(f"Failed aggregation with fields {coll_field}, {sub_coll_field}, {shelf_field}: {e}")
                    continue
            
            # If all variations failed, return empty hierarchy
            logger.warning(f"All field variations failed for index {target_index}")
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get collection hierarchy: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {}

    def get_shelfmark_documents(self, shelfmark: str, include_embeddings: bool = True, index_name: Optional[str] = None) -> List[SearchResult]:
        """
        Get all documents for a specific shelfmark with optional embeddings
        This is used when a user selects a shelfmark from the collection browser
        """
        try:
            target_index = index_name or self.index_name
            
            # Build query to find all documents with this shelfmark
            # Try exact keyword matches and phrase matches across common fields
            query = {
                "bool": {
                    "should": [
                        {"term": {"shelf_mark.keyword": shelfmark}},
                        {"term": {"shelf_mark": shelfmark}},
                        {"match_phrase": {"shelf_mark": shelfmark}},
                        {"term": {"shelfmark.keyword": shelfmark}},
                        {"term": {"shelfmark": shelfmark}},
                        {"match_phrase": {"shelfmark": shelfmark}},
                        {"term": {"classmark.keyword": shelfmark}},
                        {"term": {"classmark": shelfmark}},
                        {"match_phrase": {"classmark": shelfmark}},
                        {"term": {"doc_id": shelfmark}}
                    ],
                    "minimum_should_match": 1
                }
            }
            
            # Search for all documents
            response = self.es.search(
                index=target_index,
                query=query,
                size=1000,  # Get all documents for this shelfmark
                _source=True
            )
            
            # Format results
            results = []
            for hit in response['hits']['hits']:
                source = hit["_source"]
                metadata = self._extract_metadata(source)
                
                # Include embedding if requested
                embedding = None
                if include_embeddings:
                    embedding = source.get("embedding_vector", [])
                
                doc_id = source.get("doc_id") or hit["_id"]
                
                results.append(SearchResult(
                    doc_id=doc_id,
                    similarity_score=1.0,
                    metadata=metadata,
                    embedding=embedding
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get shelfmark documents: {e}")
            return []

    def sample_docs_for_collection(self, collection: str, sub_collection: Optional[str] = None, index_name: Optional[str] = None, size: int = 5) -> List[Dict[str, Any]]:
        """
        Return a small sample of documents for a given collection/sub_collection with only relevant fields
        to help debug which shelfmark field is populated in the index.
        """
        target_index = index_name or self.index_name
        # Be lenient about keyword vs text fields by OR-ing both variants
        collection_filter = {
            "bool": {
                "should": [
                    {"term": {"collection": collection}},
                    {"term": {"collection.keyword": collection}}
                ],
                "minimum_should_match": 1
            }
        }
        must_filters = [collection_filter]
        if sub_collection is not None:
            must_filters.append({
                "bool": {
                    "should": [
                        {"term": {"sub_collection": sub_collection}},
                        {"term": {"sub_collection.keyword": sub_collection}}
                    ],
                    "minimum_should_match": 1
                }
            })

        query = {"bool": {"must": must_filters}}

        try:
            resp = self.es.search(
                index=target_index,
                query=query,
                size=size,
                _source=[
                    "doc_id",
                    "collection",
                    "sub_collection",
                    "shelf_mark",
                    "shelfmark",
                    "classmark",
                    "title",
                ],
            )
            return [hit.get("_source", {}) for hit in resp.get("hits", {}).get("hits", [])]
        except Exception as e:
            logger.error(f"Failed to sample docs for {collection}/{sub_collection}: {e}")
            return []

    def get_shelfmark_distribution(self, collection: str, sub_collection: Optional[str] = None, index_name: Optional[str] = None, size: int = 100) -> Dict[str, Any]:
        """
        Return a terms aggregation of shelf marks for a given collection/sub_collection.
        Tries preferred field order and reports which field succeeded.
        """
        target_index = index_name or self.index_name
        collection_filter = {
            "bool": {
                "should": [
                    {"term": {"collection": collection}},
                    {"term": {"collection.keyword": collection}}
                ],
                "minimum_should_match": 1
            }
        }
        must_filters = [collection_filter]
        if sub_collection is not None:
            must_filters.append({
                "bool": {
                    "should": [
                        {"term": {"sub_collection": sub_collection}},
                        {"term": {"sub_collection.keyword": sub_collection}}
                    ],
                    "minimum_should_match": 1
                }
            })

        base_query = {"bool": {"must": must_filters}}

        field_candidates = [
            "shelf_mark.keyword",
            "shelfmark.keyword",
            "classmark.keyword",
            "shelf_mark",
            "shelfmark",
            "classmark",
        ]

        for field in field_candidates:
            try:
                resp = self.es.search(
                    index=target_index,
                    size=0,
                    query=base_query,
                    aggs={
                        "shelfmarks": {
                            "terms": {
                                "field": field,
                                "size": size,
                                "min_doc_count": 1
                            },
                            "aggs": {
                                "sample_docs": {
                                    "top_hits": {
                                        "size": 5,
                                        "_source": ["doc_id"]
                                    }
                                }
                            }
                        },
                        "has_field": {"filter": {"exists": {"field": field}}}
                    }
                )
                buckets = resp.get("aggregations", {}).get("shelfmarks", {}).get("buckets", [])
                has_field = resp.get("aggregations", {}).get("has_field", {}).get("doc_count", 0)
                if buckets or has_field > 0:
                    # Enrich buckets with sample doc_ids
                    enriched = []
                    for b in buckets:
                        hits = b.get("sample_docs", {}).get("hits", {}).get("hits", [])
                        doc_ids = [h.get("_source", {}).get("doc_id") or h.get("_id") for h in hits if (h.get("_source") or h.get("_id"))]
                        e = dict(b)
                        e["doc_ids"] = [d for d in doc_ids if d]
                        enriched.append(e)
                    return {
                        "field_used": field,
                        "has_field_count": has_field,
                        "buckets": enriched
                    }
            except Exception as e:
                logger.warning(f"Shelfmark distribution failed on field {field}: {e}")
                continue

        return {"field_used": None, "has_field_count": 0, "buckets": []}

    def get_shelfmarks_list(self, collection: str, sub_collection: Optional[str] = None, index_name: Optional[str] = None, size: int = 1000) -> Dict[str, Any]:
        """
        Return a list of shelfmarks with counts for a given collection/sub_collection.
        First tries an aggregation; if empty, falls back to scanning documents and counting in Python.
        """
        # Try aggregation path first
        dist = self.get_shelfmark_distribution(collection, sub_collection, index_name, size)
        if dist.get("buckets"):
            return {
                "field_used": dist.get("field_used"),
                "shelfmarks": [{"name": b.get("key"), "count": b.get("doc_count", 0)} for b in dist["buckets"] if b.get("key")]
            }

        # Fallback: scan docs and count
        target_index = index_name or self.index_name
        collection_filter = {
            "bool": {
                "should": [
                    {"term": {"collection": collection}},
                    {"term": {"collection.keyword": collection}}
                ],
                "minimum_should_match": 1
            }
        }
        must_filters = [collection_filter]
        if sub_collection is not None:
            must_filters.append({
                "bool": {
                    "should": [
                        {"term": {"sub_collection": sub_collection}},
                        {"term": {"sub_collection.keyword": sub_collection}}
                    ],
                    "minimum_should_match": 1
                }
            })

        try:
            resp = self.es.search(
                index=target_index,
                query={"bool": {"must": must_filters}},
                size=min(size, 5000),
                _source=["shelf_mark", "shelfmark", "classmark", "doc_id"],
            )
        except Exception as e:
            logger.error(f"Fallback shelfmark scan failed: {e}")
            return {"field_used": None, "shelfmarks": []}

        counts: Dict[str, int] = {}
        def add(name: Optional[str]):
            if not name:
                return
            counts[name] = counts.get(name, 0) + 1

        for hit in resp.get("hits", {}).get("hits", []):
            src = hit.get("_source", {})
            # Prefer shelf_mark > shelfmark > classmark > doc_id
            value = src.get("shelf_mark") or src.get("shelfmark") or src.get("classmark") or src.get("doc_id")
            add(value)

        shelfmarks = sorted(
            ( {"name": k, "count": v} for k, v in counts.items() if k ),
            key=lambda x: (-x["count"], x["name"])
        )

        return {"field_used": dist.get("field_used"), "shelfmarks": shelfmarks}


# Global search service
search_service = ElasticsearchService()