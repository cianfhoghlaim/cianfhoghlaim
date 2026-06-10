# file_name
import json
import logging
import pickle
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

logger = logging.getLogger(__name__)
logging.getLogger('elasticsearch').setLevel(logging.DEBUG)


class ElasticsearchGenizahProcessor:
    """Simple processor for indexing GenizahDocument objects to Elasticsearch.

    This processor handles embedding generation, caching, and Elasticsearch indexing
    for Pydantic GenizahDocument objects.

    Example:
        config = {
        ...     'hosts': ['localhost:9200'],
        ...     'index_name': 'genizah-documents'
        ... }
        processor = ElasticsearchGenizahProcessor(
        ...     embedding_model=my_model,
        ...     elasticsearch_config=config
        ... )
        results = processor.process_documents(documents=my_docs)
    """

    def __init__(self,
                 embedding_model,
                 elasticsearch_config: Dict[str, Any],
                 index_name = "genizah_documents_text1",
                 cache_dir: str = "embedding_cache",
                 use_cache: bool = False,
                 embedding_dims: int = 128):
        """Initialize the Elasticsearch processor.

        :param embedding_model: Model for generating document embeddings
        :type embedding_model: Any
        :param elasticsearch_config: The dictionary configuration of instantiating the Elasticsearch client. Should contain
        hosts, basic_auth, etc...
        :type elasticsearch_config: Dict[str, Any]
        :param cache_dir: Directory for caching the generated embedding model embeddings.
        :type cache_dir: str
        """
        self.embedding_model = embedding_model
        self.es_client = Elasticsearch(**elasticsearch_config)
        self.index_name = index_name
        self.embedding_dims = embedding_dims

        # Setup caching
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.use_cache = False
        if use_cache:
            self.embedding_cache = self._load_embedding_cache()
            self.use_cache = True


        # Statistics
        self.stats = {
            'processed': 0,
            'cached_hits': 0,
            'cache_misses': 0,
            'errors': 0
        }

        # Create index if it doesn't exist
        self._create_index_if_needed()

    def process_documents(self,
                          documents: List,
                          batch_size: int = 100) -> Dict[str, Any]:
        """Process and index documents in batches - fail fast if anything goes wrong."""

        start_time = time.time()
        logger.info(f"Processing {len(documents)} documents in batches of {batch_size}")

        total_processed = 0

        # Process in batches
        for batch_start in range(0, len(documents), batch_size):
            batch_end = min(batch_start + batch_size, len(documents))
            batch = documents[batch_start:batch_end]

            logger.info(f"Processing batch {batch_start // batch_size + 1}: documents {batch_start + 1}-{batch_end}")

            # Process this batch
            es_documents = []
            for i, doc in enumerate(batch):
                actual_index = batch_start + i
                logger.info(f"Processing document {actual_index + 1}/{len(documents)}: {doc.doc_id}")

                # Generate embedding - fail if this doesn't work
                embedding = self._get_embedding_for_document(document=doc)
                if embedding is None:
                    raise Exception(f"Failed to generate embedding for document {doc.doc_id}")

                # Validate document has required fields
                if not doc.shelf_mark or doc.shelf_mark.strip() == "":
                    logger.error(f"Document {doc.doc_id} has blank or missing shelf_mark - skipping")
                    continue
                
                # Convert to ES format
                es_doc = doc.to_elasticsearch_document(embedding=embedding)
                es_documents.append({
                    '_index': self.index_name,
                    '_id': doc.doc_id or f"doc_{actual_index}",
                    '_source': es_doc
                })

            # Index this batch immediately - fail if this doesn't work
            if es_documents:
                logger.info(f"Indexing batch of {len(es_documents)} documents")
                self._bulk_index_documents_fail_fast(es_documents)
                total_processed += len(es_documents)
                logger.info(f"Successfully indexed batch. Total so far: {total_processed}/{len(documents)}")

        # Save cache
        if self.use_cache:
            self._save_embedding_cache()

        total_time = time.time() - start_time
        logger.info(f"Processing complete: {total_processed}/{len(documents)} documents in {total_time:.1f}s")

        return {
            'processed_count': total_processed,
            'total_time': total_time,
            'documents_per_second': len(documents) / max(total_time, 0.001)
        }

    def _bulk_index_documents_fail_fast(self, documents: List[Dict[str, Any]]) -> None:
        """Bulk index documents - fail immediately if anything goes wrong."""

        # Preprocess dates
        for doc in documents:
            if '_source' in doc:
                doc['_source'] = self._preprocess_document_dates(doc['_source'])

        # Do the bulk index
        try:
            success, failed = bulk(
                client=self.es_client,
                actions=documents,
                refresh='wait_for'
            )
            if failed:
                logger.warning(f"Failed to index {len(failed)} documents")
                for i, fail in enumerate(failed):
                    try:
                        idx_err = fail.get('index', {})
                        err = idx_err.get('error', {})
                        reason = err.get('reason', '')
                        etype = err.get('type', '')
                        caused_by = err.get('caused_by', {})
                        cid = idx_err.get('_id', 'unknown_id')
                        status = idx_err.get('status', 'unknown_status')
                        logger.error(
                            f"Bulk error #{i+1} id={cid} status={status} type={etype} reason={reason} caused_by={caused_by}"
                        )
                    except Exception:
                        logger.error(f"Bulk error (unparsable): {fail}")

            logger.info(f"Successfully bulk indexed {success} documents")
        except Exception as e:
            # Try to surface detailed bulk errors if available
            try:
                from elasticsearch.helpers import BulkIndexError
                if isinstance(e, BulkIndexError):
                    logger.error(f"BulkIndexError during indexing: {e}")
                    errors = getattr(e, 'errors', [])
                    logger.error(f"{len(errors)} document(s) failed to index.")
                    for i, fail in enumerate(errors):
                        try:
                            idx_err = fail.get('index', {})
                            err = idx_err.get('error', {})
                            reason = err.get('reason', '')
                            etype = err.get('type', '')
                            caused_by = err.get('caused_by', {})
                            cid = idx_err.get('_id', 'unknown_id')
                            status = idx_err.get('status', 'unknown_status')
                            logger.error(
                                f"Bulk error #{i+1} id={cid} status={status} type={etype} reason={reason} caused_by={caused_by}"
                            )
                        except Exception:
                            logger.error(f"Bulk error (unparsable): {fail}")
                else:
                    logger.error(f"Failed to index documents: {e}")
            except Exception:
                logger.error(f"Failed to index documents: {e}")



    def search_documents(self,
                         query_text: str,
                         query_embedding: Optional[np.ndarray] = None,
                         filters: Optional[Dict[str, Any]] = None,
                         size: int = 10) -> Dict[str, Any]:
        """Search documents using text and/or semantic similarity.

        :param query_text: Text query for lexical search
        :type query_text: str
        :param query_embedding: Embedding vector for semantic search
        :type query_embedding: Optional[np.ndarray]
        :param filters: Additional filters to apply
        :type filters: Optional[Dict[str, Any]]
        :param size: Number of results to return
        :type size: int
        :return: Search results
        :rtype: Dict[str, Any]

        Example:
             results = processor.search_documents(
            ...     query_text="Talmud fragment",
            ...     size=5
            ... )
            results['total'] >= 0
            True
        """
        search_body = {
            "size": size,
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            }
        }

        # Add text search
        if query_text:
            text_query = {
                "multi_match": {
                    "query": query_text,
                    "fields": [
                        "description^2",
                        "full_text_content",
                        "transcriptions.text",
                        "translations.text"
                    ],
                    "type": "best_fields"
                }
            }
            search_body["query"]["bool"]["must"].append(text_query)

        # Add semantic search
        if query_embedding is not None:
            semantic_query = {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0",
                        "params": {"query_vector": query_embedding.tolist()}
                    }
                }
            }

            if query_text:
                # Combine text and semantic search
                search_body["query"] = {
                    "bool": {
                        "should": [
                            {"bool": search_body["query"]["bool"]},
                            semantic_query
                        ]
                    }
                }
            else:
                search_body["query"] = semantic_query

        # Add filters
        if filters:
            filter_queries = self._build_filter_queries(filters=filters)
            search_body["query"]["bool"]["filter"].extend(filter_queries)

        # Execute search
        response = self.es_client.search(index=self.index_name, body=search_body)

        return {
            'hits': [
                {
                    'id': hit['_id'],
                    'score': hit['_score'],
                    'source': hit['_source']
                }
                for hit in response['hits']['hits']
            ],
            'total': response['hits']['total']['value'],
            'max_score': response['hits']['max_score']
        }

    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by its ID.

        :param doc_id: Document ID to retrieve
        :type doc_id: str
        :return: Document data or None if not found
        :rtype: Optional[Dict[str, Any]]

        Example:
            doc = processor.get_document_by_id(doc_id="MS-TS-F-00001")
            doc is not None
            True
        """
        response = self.es_client.get(index=self.index_name, id=doc_id, ignore=[404])

        if response['found']:
            return response['_source']
        return None

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the Elasticsearch index.

        :return: Index statistics
        :rtype: Dict[str, Any]

        Example:
                stats = processor.get_index_stats()
                'document_count' in stats
                 True
        """
        count_response = self.es_client.count(index=self.index_name)
        stats_response = self.es_client.indices.stats(index=self.index_name)

        index_stats = stats_response['indices'][self.index_name]['total']

        return {
            'document_count': count_response['count'],
            'index_size_bytes': index_stats['store']['size_in_bytes'],
            'index_size_mb': index_stats['store']['size_in_bytes'] / (1024 * 1024)
        }

    # ===== PRIVATE METHODS =====
    def _preprocess_document_dates(self, es_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess document dates by normalizing all dates as strings.
        Much simpler approach - all dates stored as keywords for consistent handling.

        :param es_doc: Elasticsearch document dictionary
        :type es_doc: Dict[str, Any]
        :return: Processed document with normalized string dates.
        :rtype: Dict[str, Any]
        """
        # Process all date fields as strings
        for date_field in ['date_start', 'date_end', 'date_display']:
            if date_field in es_doc and es_doc[date_field]:
                original_date = es_doc[date_field]

                if date_field == 'date_display' and '/' in str(original_date):
                    # Handle ranges like "0932-09-03/0933-09-22" or "888/987"
                    parts = str(original_date).split('/')
                    cleaned_parts = [self._normalize_date_string(part) for part in parts]
                    es_doc[date_field] = '/'.join(cleaned_parts)
                else:
                    # Single date - just normalize
                    es_doc[date_field] = self._normalize_date_string(original_date)

                logger.debug(f"Normalized {date_field}: {original_date} -> {es_doc[date_field]}")

        return es_doc

    @staticmethod
    def _normalize_date_string(date_str) -> str:
        """Normalize date string by removing leading zeros.
        :param date_str: Date string to normalize (e.g., 0932-01-01)
        :type date_str: str
        :return: Normalized date string (e.g., 932-01-01)
        :rtype: str
        """
        if not date_str:
            return date_str

        try:
            date_str = str(date_str)
            # Handle leading zeros: 0932-01-01 -> 932-01-01
            if date_str.startswith('0') and len(date_str) > 4:
                normalized = date_str.lstrip('0')
                if normalized.startswith('-'):
                    normalized = '0' + normalized
                return normalized
            return date_str
        except (ValueError, AttributeError):
            return date_str

    def _create_index_if_needed(self) -> None:
        """Create Elasticsearch index with string-based date fields for historical documents."""
        if self.es_client.indices.exists(index=self.index_name):
            logger.info(f"Index {self.index_name} already exists")
            return

        mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "multilingual": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "asciifolding"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    # Core fields
                    "doc_id": {"type": "keyword"},
                    "shelf_mark": {"type": "keyword"},
                    "description": {"type": "text", "analyzer": "multilingual"},
                    "full_text_content": {"type": "text", "analyzer": "multilingual"},

                    # All dates as strings - handles any historical date
                    "date_start": {
                        "type": "keyword",  # String dates work for any year
                        "fields": {
                            "text": {"type": "text"}
                        }
                    },
                    "date_end": {
                        "type": "keyword",  # String dates work for any year
                        "fields": {
                            "text": {"type": "text"}
                        }
                    },
                    "date_display": {
                        "type": "keyword",  # Can handle ranges and any format
                        "fields": {
                            "text": {
                                "type": "text",
                                "analyzer": "multilingual"
                            }
                        }
                    },
                    "date_certainty": {"type": "keyword"},
                    "century": {"type": "keyword"},

                    # Classification fields
                    "document_type": {"type": "keyword"},
                    "main_language": {"type": "keyword"},
                    "other_languages": {"type": "keyword"},
                    "script_type": {"type": "keyword"},
                    "content_quality": {"type": "keyword"},
                    "source_collection": {"type": "keyword"},
                    "language": {"type": "keyword"},

                    # Bibliography-specific fields
                    "author": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "authors": {"type": "keyword"},
                    "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "isbn": {"type": "keyword"},
                    "subject_keywords": {"type": "keyword"},
                    "page_number": {"type": "integer"},
                    "extracted_page_number": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "numeric": {"type": "long"}
                        }
                    },
                    "shelf_marks_mentioned": {
                        "type": "keyword"  # Store as keyword array to avoid dynamic field creation
                    },

                    # Named entities
                    "named_entities": {
                        "type": "object",
                        "properties": {
                            "persons": {"type": "keyword"},
                            "places": {"type": "keyword"},
                            "organizations": {"type": "keyword"},
                            "dates": {"type": "keyword"}
                        }
                    },

                    # Nested structures
                    "transcriptions": {
                        "type": "nested",
                        "properties": {
                            "text": {"type": "text", "analyzer": "multilingual"},
                            "editor": {"type": "keyword"},
                            "line_count": {"type": "integer"},
                            "language": {"type": "keyword"}
                        }
                    },
                    "translations": {
                        "type": "nested",
                        "properties": {
                            "text": {"type": "text", "analyzer": "multilingual"}
                        }
                    },
                    "bibliography": {
                        "type": "nested",
                        "properties": {
                            "citation": {"type": "text"},
                            "location": {"type": "text"},
                            "relations": {"type": "keyword"},
                            "url": {"type": "keyword"}
                        }
                    },

                    # Images
                    "image_urls": {"type": "keyword"},
                    "primary_image_index": {"type": "integer"},
                    "has_images": {"type": "boolean"},
                    "actual_image_url": {"type": "keyword"},

                    # Embedding vector
                    "embedding_vector": {
                        "type": "dense_vector",
                        "dims": self.embedding_dims,
                        "index": True,
                        "similarity": "cosine"
                    },

                    # Other fields
                    "completeness_score": {"type": "float"},
                    "indexed_at": {"type": "date"},  # Keep this as date since it's modern
                    
                    # Joins data
                    "joins_data": {
                        "type": "object",
                        "properties": {
                            "joinedManuscripts": {
                                "type": "nested",
                                "properties": {
                                    "shelfmark": {"type": "keyword"},
                                    "index": {"type": "integer"},
                                    "source": {"type": "keyword"}
                                }
                            },
                            "mainShelfmark": {"type": "keyword"},
                            "source": {"type": "keyword"},
                            "metadata": {
                                "type": "object",
                                "properties": {
                                    "pageUrl": {"type": "keyword"},
                                    "extractedAt": {"type": "date"},
                                    "extractionMethod": {"type": "keyword"}
                                }
                            }
                        }
                    }
                }
            }
        }
        self.es_client.indices.create(index=self.index_name, body=mapping)
        logger.info(f"Created index {self.index_name} with string-based historical dates")

    def _get_embedding_for_document(self, document) -> Optional[np.ndarray]:
        """Generate or retrieve cached embedding for a document.

        :param document: GenizahDocument to get embedding for
        :type document: GenizahDocument
        :return: Embedding vector or None if generation fails
        :rtype: Optional[np.ndarray]
        """
        # Check cache first
        if self.use_cache:
            cache_key = document.get_embedding_cache_key()
            if cache_key in self.embedding_cache:
                self.stats['cached_hits'] += 1
                return self.embedding_cache[cache_key]

        # Check if using image-only mode - skip text representation
        is_image_only = hasattr(self.embedding_model, 'image_only') and self.embedding_model.image_only
        
        if is_image_only:
            # For image-only mode, pass doc_id as text for better caching (embedding model will ignore it for processing)
            text_representation = document.doc_id or ""
        else:
            # Generate new embedding using the document's text representation method
            text_representation = document.create_text_representation()
        
        embedding = self.embedding_model.get_embeddings(
            image=document.image,
            text=text_representation,
            use_cache=False
        )

        if embedding is not None and self.use_cache:
            # Cache the new embedding
            cache_key = document.get_embedding_cache_key()
            self.embedding_cache[cache_key] = embedding
            self.stats['cache_misses'] += 1

        return embedding

    def _build_filter_queries(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build Elasticsearch filter queries from filter dictionary.

        :param filters: Filter criteria
        :type filters: Dict[str, Any]
        :return: List of Elasticsearch filter queries
        :rtype: List[Dict[str, Any]]
        """
        filter_queries = []

        if 'document_type' in filters:
            filter_queries.append({"term": {"document_type": filters['document_type']}})

        if 'language' in filters:
            filter_queries.append({"term": {"main_language": filters['language']}})

        if 'source_collection' in filters:
            filter_queries.append({"term": {"source_collection": filters['source_collection']}})

        if 'date_start' in filters or 'date_end' in filters:
            date_range = {}
            if 'date_start' in filters:
                date_range['gte'] = filters['date_start']
            if 'date_end' in filters:
                date_range['lte'] = filters['date_end']
            filter_queries.append({"range": {"date_start": date_range}})

        if 'has_transcriptions' in filters:
            if filters['has_transcriptions']:
                filter_queries.append({"exists": {"field": "transcriptions"}})
            else:
                filter_queries.append({"bool": {"must_not": [{"exists": {"field": "transcriptions"}}]}})

        if 'min_completeness' in filters:
            filter_queries.append({"range": {"completeness_score": {"gte": filters['min_completeness']}}})

        return filter_queries

    def _load_embedding_cache(self) -> Dict[str, np.ndarray]:
        """Load embedding cache from disk.

        :return: Dictionary of cached embeddings
        :rtype: Dict[str, np.ndarray]
        """
        cache_file = self.cache_dir / "embeddings.pkl"

        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                cache = pickle.load(f)
            logger.info(f"Loaded {len(cache)} cached embeddings")
            return cache

        return {}

    def _save_embedding_cache(self) -> None:
        """Save embedding cache to disk."""
        cache_file = self.cache_dir / "embeddings.pkl"

        with open(cache_file, 'wb') as f:
            pickle.dump(self.embedding_cache, f)

        logger.info(f"Saved {len(self.embedding_cache)} embeddings to cache")

    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate.

        :return: Cache hit rate as float between 0.0 and 1.0
        :rtype: float
        """
        total_requests = self.stats['cached_hits'] + self.stats['cache_misses']
        if total_requests == 0:
            return 0.0
        return self.stats['cached_hits'] / total_requests