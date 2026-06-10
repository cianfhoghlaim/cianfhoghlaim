import json
import logging
from pathlib import Path
from typing import List, Optional
from src.embeddings.embedding_models import MultiModalEmbedding
from src.embeddings.visualizations.document_visualizer import DocumentVisualization
import pickle
import pandas as pd
from google.cloud import storage
from datetime import datetime
import re
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
from collections import Counter
import numpy as np
from typing import Dict

logger = logging.getLogger(__name__)


class StreamingDocumentProcessor:
    """Document processor that uploads embeddings to Elasticsearch as they're generated"""

    def __init__(self, embedding_model: MultiModalEmbedding, visualizer: DocumentVisualization,
                 prefix_name: str = "", project_id: str = None, bucket_name: str = None,
                 elasticsearch_config: dict = None):
        self.embedding_model = embedding_model
        self.visualizer = visualizer
        self.cache_dir = Path("embedding_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.prefix_name = prefix_name

        # Cloud storage integration
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.upload_to_cloud = project_id is not None and bucket_name is not None

        if self.upload_to_cloud:
            self.storage_client = storage.Client(project=project_id)
            self.bucket = self.storage_client.bucket(bucket_name)
            logger.info(f"Cloud upload enabled to bucket: {bucket_name}")
        else:
            logger.info("Cloud upload disabled - only local caching")

        # Elasticsearch integration
        self.elasticsearch_config = elasticsearch_config or {}
        self.use_elasticsearch = bool(elasticsearch_config)


        if self.use_elasticsearch:
            self.index_name = self.elasticsearch_config["index_name"]
            self.elasticsearch_config.pop("index_name")
            self.es_client = Elasticsearch(**elasticsearch_config)
            # Test connection
            if self.es_client.ping():
                logger.info(f"Elasticsearch connection established: {elasticsearch_config['hosts']}")
                self.index_name = elasticsearch_config.get('index_name', 'historical-documents')
            else:
                logger.error("Failed to connect to Elasticsearch")
                self.use_elasticsearch = False
                raise ConnectionError("Failed to connect to Elasticsearch")
        else:
            logger.info("Elasticsearch integration disabled")

    def _parse_transcriptions_properly(self, transcriptions) -> dict:
        """Parse transcriptions while preserving the original structure.
        :param transcriptions: List of transcriptions or dicts with transcriptions.
        """
        result = {
            "transcription_texts": [],
            "transcription_full_text": "",
            "transcription_count": 0,
            "total_transcription_lines": 0,
            "transcription_editors": [],
            "transcription_lines_dict": {}
        }

        if not transcriptions:
            return result

        try:
            for i, transcription in enumerate(transcriptions):
                if isinstance(transcription, dict):
                    # Handle structured transcription with editor and lines
                    if 'name' in transcription and 'lines' in transcription:
                        editor = transcription.get('name', f'Editor {i + 1}')
                        lines_dict = transcription.get('lines', {})

                        result["transcription_editors"].append(editor)

                        # Store the original lines dictionary structure
                        result["transcription_lines_dict"][editor] = lines_dict

                        # Extract text for search
                        if isinstance(lines_dict, dict):
                            line_texts = [str(line) for line in lines_dict.values() if line]
                            result["transcription_texts"].extend(line_texts)
                            result["total_transcription_lines"] += len(line_texts)

                    elif 'lines' in transcription:
                        # Handle simple lines structure
                        lines = transcription['lines']
                        if isinstance(lines, dict):
                            line_texts = [str(line) for line in lines.values() if line]
                        elif isinstance(lines, list):
                            line_texts = [str(line) for line in lines if line]
                        else:
                            line_texts = [str(lines)] if lines else []

                        result["transcription_texts"].extend(line_texts)
                        result["total_transcription_lines"] += len(line_texts)

                elif hasattr(transcription, 'lines'):
                    # Handle object with lines attribute
                    lines = transcription.lines
                    if isinstance(lines, dict):
                        line_texts = [str(line) for line in lines.values() if line]
                    elif isinstance(lines, list):
                        line_texts = [str(line) for line in lines if line]
                    else:
                        line_texts = [str(lines)] if lines else []

                    result["transcription_texts"].extend(line_texts)
                    result["total_transcription_lines"] += len(line_texts)

                elif isinstance(transcription, (str, list)):
                    # Handle simple string or list transcriptions
                    if isinstance(transcription, str):
                        if transcription.strip():
                            result["transcription_texts"].append(transcription.strip())
                            result["total_transcription_lines"] += 1
                    elif isinstance(transcription, list):
                        for line in transcription:
                            if line and str(line).strip():
                                result["transcription_texts"].append(str(line).strip())
                                result["total_transcription_lines"] += 1

            result["transcription_count"] = len(transcriptions)
            result["transcription_full_text"] = ' '.join(result["transcription_texts"])

            # Categorize by transcription completeness
            if result["total_transcription_lines"] == 0:
                result["transcription_completeness"] = "none"
            elif result["total_transcription_lines"] < 5:
                result["transcription_completeness"] = "minimal"
            elif result["total_transcription_lines"] < 15:
                result["transcription_completeness"] = "partial"
            else:
                result["transcription_completeness"] = "complete"

        except Exception as e:
            logger.warning(f"Error parsing transcriptions: {e}")
            # Fallback to simple handling
            result["transcription_texts"] = [str(t) for t in transcriptions if str(t).strip()]
            result["transcription_full_text"] = ' '.join(result["transcription_texts"])
            result["transcription_count"] = len(transcriptions)
            result["total_transcription_lines"] = len(result["transcription_texts"])

        return result

    def _parse_misc_info(self, misc_info: str) -> dict:
        """Parse miscellaneous info to extract structured metadata"""
        parsed = {}

        if not misc_info:
            return parsed

        lines = misc_info.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Parse location
            if line.startswith('Location:'):
                location = line.replace('Location:', '').strip()
                parsed['physical_location'] = location

                # Extract specific institutions
                location_lower = location.lower()
                if 'cambridge' in location_lower:
                    parsed['institution'] = 'cambridge'
                    if 'university library' in location_lower:
                        parsed['library'] = 'cambridge_university_library'
                elif 'princeton' in location_lower:
                    parsed['institution'] = 'princeton'
                elif 'oxford' in location_lower:
                    parsed['institution'] = 'oxford'
                elif 'british library' in location_lower:
                    parsed['institution'] = 'british_library'
                    parsed['library'] = 'british_library'
                else:
                    parsed['institution'] = 'other'

            # Parse classmark/shelf mark
            elif line.startswith('Classmark:'):
                classmark = line.replace('Classmark:', '').strip()
                parsed['classmark'] = classmark

                # Extract collection info from classmark patterns
                if classmark.startswith('T-S'):
                    parsed['collection'] = 'taylor_schechter'
                elif classmark.startswith('Or.'):
                    parsed['collection'] = 'oriental'
                elif classmark.startswith('Add.'):
                    parsed['collection'] = 'additional'
                else:
                    parsed['collection'] = 'other'

            # Parse provenance
            elif line.startswith('Provenance:'):
                provenance = line.replace('Provenance:', '').strip()
                parsed['provenance'] = provenance

                # Extract donation year if mentioned
                year_match = re.search(r'\b(18\d{2}|19\d{2}|20\d{2})\b', provenance)
                if year_match:
                    parsed['donation_year'] = year_match.group(1)

                # Check for specific collections mentioned
                provenance_lower = provenance.lower()
                if 'taylor-schechter' in provenance_lower:
                    parsed['collection'] = 'taylor_schechter'
                if 'genizah collection' in provenance_lower:
                    parsed['collection_type'] = 'genizah'

            # Parse donors
            elif line.startswith('Donated by:'):
                donors_text = line.replace('Donated by:', '').strip()
                parsed['donors'] = donors_text

                # Extract individual donor names and dates
                donor_list = []
                # Split by semicolon and parse each donor
                for donor_part in donors_text.split(';'):
                    donor_part = donor_part.strip()
                    if donor_part:
                        # Extract name and dates using regex
                        # Match pattern like "Surname, First (Middle), birth-death"
                        match = re.match(r'([^,]+),\s*([^,]+),?\s*(\d{4}-\d{4})?', donor_part)
                        if match:
                            surname = match.group(1).strip()
                            first_names = match.group(2).strip()
                            dates = match.group(3) if match.group(3) else None

                            donor_info = {
                                'surname': surname,
                                'first_names': first_names
                            }
                            if dates:
                                donor_info['dates'] = dates

                            donor_list.append(donor_info)

                            # Add searchable donor surnames
                            if 'donor_surnames' not in parsed:
                                parsed['donor_surnames'] = []
                            parsed['donor_surnames'].append(surname.lower())

                if donor_list:
                    parsed['donor_details'] = donor_list

        return parsed

    def _create_elasticsearch_document(self, doc, embedding: np.ndarray, doc_index: int) -> dict:
        """Convert document and embedding to Elasticsearch format with rich searchable content"""
        doc_id = getattr(doc, 'doc_id', f"doc_{doc_index}")

        # Create the base document structure
        es_doc = {
            "id": str(doc_id),
            "doc_id": str(doc_id),
            "embedding": embedding.flatten().tolist(),
            "indexed_at": datetime.now().astimezone().isoformat(timespec='seconds'),  # ← FIXED: removes microseconds
            "content_type": "multimodal"
        }

        # Add basic document attributes
        if hasattr(doc, 'language') and doc.language:
            es_doc["language"] = doc.language

        # Add the actual image URL used for embedding (Fix #1)
        if hasattr(doc, 'actual_image_url') and doc.actual_image_url:
            es_doc["image_url"] = doc.actual_image_url
            es_doc["has_images"] = True
        else:
            es_doc["has_images"] = False
            es_doc["image_url"] = ""

        # Add description for keyword search
        if hasattr(doc, 'description') and doc.description:
            # Clean up the description - remove "Description" prefix if present
            description = doc.description
            if description.startswith('Description'):
                description = description[11:].strip()  # Remove "Description" prefix

            es_doc["description"] = description
            es_doc["has_description"] = True

            # Extract keywords from description for enhanced search
            desc_words = description.lower().split()
            # Common document types that might appear in descriptions
            doc_types = ["letter", "contract", "marriage", "divorce", "legal", "religious",
                         "prayer", "poem", "medical", "business", "court", "fragment", "ketubba",
                         "responsa", "talmud", "bible", "commentary", "liturgy", "magical"]
            found_types = [dt for dt in doc_types if dt in desc_words]
            if found_types:
                es_doc["document_types"] = found_types
                es_doc["primary_document_type"] = found_types[0]
        else:
            es_doc["has_description"] = False

        # Add transcription content with proper structure preservation (Fix #3)
        if hasattr(doc, 'transcriptions') and doc.transcriptions:
            transcription_data = self._parse_transcriptions_properly(doc.transcriptions)

            # Add all the parsed transcription data
            es_doc.update({
                "transcriptions": transcription_data["transcription_texts"],
                "transcription_full_text": transcription_data["transcription_full_text"],
                "has_transcriptions": True,
                "transcription_count": transcription_data["transcription_count"],
                "total_transcription_lines": transcription_data["total_transcription_lines"],
                "transcription_completeness": transcription_data["transcription_completeness"]
            })

            # Add structured transcription data if available
            if transcription_data["transcription_editors"]:
                es_doc["transcription_editors"] = transcription_data["transcription_editors"]

            if transcription_data["transcription_lines_dict"]:
                # es_doc["transcription_lines"] = transcription_data["transcription_lines_dict"]
                print("not now")

        else:
            es_doc["has_transcriptions"] = False
            es_doc["transcription_completeness"] = "none"

        # Add translation content for search
        if hasattr(doc, 'translations') and doc.translations:
            translation_texts = []

            for translation in doc.translations:
                if hasattr(translation, 'text') and translation.text:
                    if translation.text.strip():  # Only add non-empty translations
                        translation_texts.append(translation.text.strip())
                elif isinstance(translation, dict) and 'text' in translation:
                    if translation['text'].strip():
                        translation_texts.append(translation['text'].strip())
                elif isinstance(translation, str) and translation.strip():
                    translation_texts.append(translation.strip())

            if translation_texts:  # Only add if we have actual translation content
                es_doc["translations"] = translation_texts
                es_doc["translation_full_text"] = ' '.join(translation_texts)
                es_doc["has_translations"] = True
                es_doc["translation_count"] = len(translation_texts)
            else:
                es_doc["has_translations"] = False
        else:
            es_doc["has_translations"] = False

        # Add date information
        if hasattr(doc, 'date') and doc.date:
            es_doc["date_info"] = doc.date
            es_doc["has_date"] = True

            # Add individual date fields for easier querying
            for k, v in doc.date.items():
                if v and str(v).strip():  # Only add non-empty date fields
                    es_doc[f"date_{k}"] = str(v).strip()

            # Create period classifications for easier filtering
            if 'century' in doc.date and doc.date['century']:
                century = doc.date['century'].lower()
                if any(x in century for x in ['10', '11', '12']):
                    es_doc["period"] = "early_medieval"
                elif any(x in century for x in ['13', '14', '15']):
                    es_doc["period"] = "late_medieval"
                elif any(x in century for x in ['16', '17', '18']):
                    es_doc["period"] = "early_modern"
                else:
                    es_doc["period"] = "unknown"
        else:
            es_doc["has_date"] = False

        # Add original URL
        if hasattr(doc, 'original_url') and doc.original_url:
            es_doc["original_url"] = doc.original_url
            es_doc["has_source_url"] = True

            # Extract source institution for filtering
            url_lower = doc.original_url.lower()
            if "cambridge" in url_lower:
                es_doc["source_institution"] = "cambridge"
            elif "princeton" in url_lower:
                es_doc["source_institution"] = "princeton"
            elif "upenn" in url_lower or "penn" in url_lower:
                es_doc["source_institution"] = "penn"
            else:
                es_doc["source_institution"] = "other"
        else:
            es_doc["has_source_url"] = False

        # Parse and add miscellaneous info
        if hasattr(doc, 'miscellaneous_info') and doc.miscellaneous_info:
            es_doc["miscellaneous_info"] = doc.miscellaneous_info
            es_doc["has_misc_info"] = True

            # Parse structured metadata from misc info
            misc_parsed = self._parse_misc_info(doc.miscellaneous_info)

            # Add parsed fields directly to the document
            for key, value in misc_parsed.items():
                es_doc[key] = value
        else:
            es_doc["has_misc_info"] = False

        # Create a combined full-text field for comprehensive search
        searchable_fields = []

        if es_doc.get("description"):
            searchable_fields.append(es_doc["description"])

        if es_doc.get("transcription_full_text"):
            searchable_fields.append(es_doc["transcription_full_text"])

        if es_doc.get("translation_full_text"):
            searchable_fields.append(es_doc["translation_full_text"])

        if es_doc.get("miscellaneous_info"):
            searchable_fields.append(es_doc["miscellaneous_info"])

        if searchable_fields:
            es_doc["full_text_search"] = ' '.join(searchable_fields)

        return es_doc

    def _index_batch_to_elasticsearch(self, documents: List[dict], batch_num: int):
        """Index a batch of documents directly to Elasticsearch (FIXED VERSION)"""
        if not self.use_elasticsearch:
            return

        try:
            # Prepare documents for bulk indexing
            actions = []
            for doc in documents:
                action = {
                    "_index": self.index_name,
                    "_id": doc["doc_id"],
                    "_source": doc
                }
                actions.append(action)

            # Bulk index to Elasticsearch - FIXED VERSION
            success_count, failed_items = bulk(
                self.es_client,
                actions,
                # REMOVED: index=self.index_name,  # ← This was causing the deprecation warning and conflicts
                refresh='wait_for',  # Make documents immediately searchable
                request_timeout=60,
                max_retries=3,
                # REMOVED: initial_backoff=2,      # ← These parameters don't exist in ES 8.x bulk()
                # REMOVED: max_backoff=600         # ← These parameters don't exist in ES 8.x bulk()
                raise_on_error=False,  # ← ADDED: Don't raise exception, return failed items
                raise_on_exception=False  # ← ADDED: Handle exceptions gracefully
            )

            logger.info(f"Indexed batch {batch_num}: {success_count} documents successful")

            if failed_items:
                logger.warning(f"Failed to index {len(failed_items)} documents in batch {batch_num}")
                for item in failed_items:
                    logger.error(f"Failed item: {item}")

        except Exception as e:
            logger.error(f"BulkIndexError in batch {batch_num}: {e}")
            # Log specific document errors
            raise ValueError(f"Failed to index batch {batch_num} to Elasticsearch")

    def _upload_batch_to_cloud(self, documents: List[dict], batch_num: int):
        """Upload a batch of documents to cloud storage with proper JSON encoding (Fix #2)"""
        if not self.upload_to_cloud:
            return

        try:
            # Convert to JSONL format with proper Unicode handling
            jsonl_lines = []
            for doc in documents:
                # Ensure proper JSON serialization with Unicode support
                json_line = json.dumps(doc, ensure_ascii=False, separators=(',', ':'))
                jsonl_lines.append(json_line)

            jsonl_content = "\n".join(jsonl_lines)

            # Upload to Cloud Storage with timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            blob_path = f"elasticsearch/batches/batch_{batch_num}_{timestamp}.jsonl"
            blob = self.bucket.blob(blob_path)

            # Upload with UTF-8 encoding
            blob.upload_from_string(jsonl_content, content_type='application/json; charset=utf-8')
            logger.info(
                f"Uploaded batch {batch_num} ({len(documents)} documents) to gs://{self.bucket_name}/{blob_path}")

        except Exception as e:
            logger.error(f"Failed to upload batch {batch_num}: {e}")

    def process_documents_streaming(self, docs: List, use_cache: bool = True,
                                    create_visualizations: bool = True, batch_size: int = 50) -> tuple:
        """Process documents with streaming upload for Elasticsearch"""
        logger.info(f"Processing {len(docs)} documents with streaming upload (batch_size={batch_size})")

        # Check for cached complete results first
        cache_path = self.cache_dir / "all_embeddings.pkl"
        embeddings = None
        uploaded_docs = set()

        # Track what's already been uploaded
        upload_state_path = self.cache_dir / "upload_state.json"
        if 1==2:
            with open(upload_state_path, 'r') as f:
                upload_state = json.load(f)
                uploaded_docs = set(upload_state.get('uploaded_doc_ids', []))
                logger.info(f"Found {len(uploaded_docs)} previously uploaded documents")

        if embeddings is None:
            # Process documents in batches, uploading as we go
            all_embeddings = []
            es_batch = []
            batch_num = 0

            for i, doc in enumerate(docs):
                doc_id = getattr(doc, 'doc_id', f"doc_{i}")

                # Skip if already uploaded (for resume capability)
                if str(doc_id) in uploaded_docs:
                    logger.debug(f"Skipping already uploaded doc: {doc_id}")
                    # Still need to get embedding for local processing
                    text_representation = self.embedding_model.create_text_representation(doc)
                    image = getattr(doc, 'image', None)
                    embedding = self.embedding_model.get_embeddings(image, text_representation, use_cache)
                    all_embeddings.append(embedding)
                    continue

                logger.info(f"Processing document {i + 1}/{len(docs)} (ID: {doc_id})")

                # Get embedding using your existing method
                text_representation = self.embedding_model.create_text_representation(doc)
                image = getattr(doc, 'image', None)
                embedding = self.embedding_model.get_embeddings(image, text_representation, use_cache)

                all_embeddings.append(embedding)

                # Add to Elasticsearch batch
                es_document = self._create_elasticsearch_document(doc, embedding, i)
                es_batch.append(es_document)
                uploaded_docs.add(str(doc_id))

                # Upload batch when it reaches batch_size
                if len(es_batch) >= batch_size:
                    # Index to Elasticsearch
                    if self.use_elasticsearch:
                        self._index_batch_to_elasticsearch(es_batch, batch_num)

                    # Also upload to cloud storage if enabled
                    if self.upload_to_cloud:
                        self._upload_batch_to_cloud(es_batch, batch_num)

                    batch_num += 1
                    es_batch = []

                    # Save upload state
                    with open(upload_state_path, 'w') as f:
                        json.dump({
                            'uploaded_doc_ids': list(uploaded_docs),
                            'last_batch': batch_num,
                            'timestamp': datetime.now().isoformat()
                        }, f)

            # Upload remaining documents in final batch
            if es_batch:
                # Index to Elasticsearch
                if self.use_elasticsearch:
                    self._index_batch_to_elasticsearch(es_batch, batch_num)

                # Also upload to cloud storage if enabled
                if self.upload_to_cloud:
                    self._upload_batch_to_cloud(es_batch, batch_num)

                # Save final upload state
                with open(upload_state_path, 'w') as f:
                    json.dump({
                        'uploaded_doc_ids': list(uploaded_docs),
                        'last_batch': batch_num + 1,
                        'timestamp': datetime.now().isoformat(),
                        'completed': True
                    }, f)

            embeddings = np.vstack(all_embeddings)

            # Cache the embeddings locally too
            with open(cache_path, 'wb') as f:
                pickle.dump({'embeddings': embeddings, 'doc_count': len(docs)}, f)
            logger.info(f"Cached all embeddings to {cache_path}")

        # Create visualizations if requested
        df = None
        if create_visualizations:
            df = self.visualizer.create_all_visualizations(docs, embeddings, prefix=self.prefix_name)

            # Cache the visualization DataFrame
            df_cache_path = self.cache_dir / "viz_dataframe.pkl"
            with open(df_cache_path, 'wb') as f:
                pickle.dump(df, f)
            logger.info(f"Cached visualization DataFrame to {df_cache_path}")

        logger.info(f"Processing complete. {len(docs)} documents processed and uploaded to Elasticsearch")
        return docs, embeddings, df

    def check_elasticsearch_status(self) -> dict:
        """Check Elasticsearch connection and index status"""
        if not self.use_elasticsearch:
            return {"status": "disabled", "reason": "Elasticsearch not configured"}

        try:
            # Check connection
            if not self.es_client.ping():
                return {"status": "error", "reason": "Cannot connect to Elasticsearch"}

            # Check if index exists
            if not self.es_client.indices.exists(index=self.index_name):
                return {"status": "error", "reason": f"Index '{self.index_name}' does not exist"}

            # Get index stats
            stats = self.es_client.indices.stats(index=self.index_name)
            doc_count = stats['indices'][self.index_name]['total']['docs']['count']

            return {
                "status": "ready",
                "index_name": self.index_name,
                "document_count": doc_count,
                "index_size": stats['indices'][self.index_name]['total']['store']['size_in_bytes']
            }

        except Exception as e:
            return {"status": "error", "reason": str(e)}

    def consolidate_batches(self):
        """Consolidate all uploaded batches into a single file for Elasticsearch bulk import"""
        if not self.upload_to_cloud:
            logger.warning("Cloud upload not enabled")
            return

        try:
            # List all batch files
            blobs = list(self.bucket.list_blobs(prefix="elasticsearch/batches/"))

            if not blobs:
                logger.warning("No batch files found to consolidate")
                return

            logger.info(f"Consolidating {len(blobs)} batch files")

            # Download and combine all batches
            all_documents = []
            seen_ids = set()

            for blob in blobs:
                content = blob.download_as_text(encoding='utf-8')  # Ensure UTF-8 decoding
                for line in content.strip().split('\n'):
                    if line:
                        doc = json.loads(line)
                        # Remove duplicates based on doc_id
                        if doc['doc_id'] not in seen_ids:
                            all_documents.append(doc)
                            seen_ids.add(doc['doc_id'])

            # Create Elasticsearch bulk format
            bulk_content = []
            for doc in all_documents:
                # Elasticsearch bulk index action
                action = {"index": {"_id": doc["doc_id"]}}
                bulk_content.append(json.dumps(action, ensure_ascii=False))
                bulk_content.append(json.dumps(doc, ensure_ascii=False))

            # Upload consolidated file
            consolidated_content = "\n".join(bulk_content) + "\n"  # ES bulk format needs trailing newline
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            consolidated_blob = self.bucket.blob(f"elasticsearch/bulk_import_{timestamp}.jsonl")
            consolidated_blob.upload_from_string(consolidated_content, content_type='application/json; charset=utf-8')

            logger.info(
                f"Consolidated {len(all_documents)} unique documents to gs://{self.bucket_name}/elasticsearch/bulk_import_{timestamp}.jsonl")

            return f"gs://{self.bucket_name}/elasticsearch/bulk_import_{timestamp}.jsonl"

        except Exception as e:
            logger.error(f"Error consolidating batches: {e}")
            return None

    def get_upload_status(self) -> dict:
        """Get status of uploads"""
        upload_state_path = self.cache_dir / "upload_state.json"

        if not upload_state_path.exists():
            return {"status": "not_started", "uploaded_count": 0}

        with open(upload_state_path, 'r') as f:
            upload_state = json.load(f)

        # Also include Elasticsearch status
        es_status = self.check_elasticsearch_status()

        return {
            "status": "completed" if upload_state.get('completed') else "in_progress",
            "uploaded_count": len(upload_state.get('uploaded_doc_ids', [])),
            "last_batch": upload_state.get('last_batch', 0),
            "timestamp": upload_state.get('timestamp'),
            "elasticsearch_status": es_status
        }

    # Keep your existing methods for backward compatibility
    def process_documents(self, docs: List, use_cache: bool = True, create_visualizations: bool = True) -> tuple:
        """Legacy method - redirects to streaming version"""
        return self.process_documents_streaming(docs, use_cache, create_visualizations)

    def reload_and_visualize(self) -> Optional[pd.DataFrame]:
        """Reload cached data and recreate visualizations without running the model"""
        df_cache_path = self.cache_dir / "viz_dataframe.pkl"

        if not df_cache_path.exists():
            logger.warning("Cache file not found. Please run process_documents() first.")
            return None

        # Load dataframe
        logger.info("Loading cached data...")
        with open(df_cache_path, 'rb') as f:
            df = pickle.load(f)

        # Recreate visualizations
        logger.info("Recreating visualizations from cached data...")
        embeddings_2d = df[['x', 'y']].values

        self.visualizer.create_main_visualization(df, output_filename=self.prefix_name + "_main_visualization.html")
        self.visualizer.create_language_visualization(df,
                                                      output_filename=self.prefix_name + "_language_visualization.html")
        self.visualizer.create_completeness_visualization(df,
                                                          output_filename=self.prefix_name + "_completeness_visualization.html")

        logger.info("All visualizations recreated successfully from cached data.")
        return df

    def evaluate_clustering(self, docs: List, embeddings: np.ndarray, k: int) -> dict:
        """
        Evaluate clustering performance using k-means clustering on categorized documents.

        This method performs k-means clustering on document embeddings and evaluates how well
        the resulting clusters align with ground truth document categories. It computes multiple
        metrics to assess clustering quality and provides detailed analysis of cluster composition.

        Args:
            docs (List): List of document objects, each must have a 'category' attribute
            embeddings (np.ndarray): Document embeddings matrix of shape (n_documents, embedding_dim)
            k (int): Number of clusters for k-means algorithm (should match number of expected categories)

        Returns:
            dict: Comprehensive evaluation results containing:
                - silhouette_score (float): Measure of cluster cohesion and separation (-1 to 1, higher is better)
                - purity_score (float): Fraction of documents correctly clustered (0 to 1, higher is better)
                - cluster_composition (dict): Detailed breakdown of what categories ended up in each cluster
                - n_clusters (int): Number of clusters used
                - n_documents (int): Total number of documents evaluated
                - categories_found (list): Unique categories detected in the dataset

        Raises:
            ValueError: If not all documents have category attributes

        Example:

            >>> results = processor.evaluate_clustering(docs, embeddings, k=4)
            >>> print(f"Silhouette: {results['silhouette_score']:.3f}")
            >>> print(f"Purity: {results['purity_score']:.3f}")

        Note:
            - Silhouette scores > 0.3 generally indicate reasonable clustering
            - Purity scores > 0.7 suggest good category separation
            - Uses random_state=42 for reproducible results
        """
        logger.info(f"Evaluating clustering with k={k} on {len(docs)} documents")

        # Extract true category labels from documents
        true_labels = []
        doc_categories = []

        for i, doc in enumerate(docs):
            if hasattr(doc, 'document_category') and doc.document_category:
                true_labels.append(doc.document_category)
                doc_categories.append(doc.document_category)
            else:
                error_msg = f"Document {getattr(doc, 'doc_id', f'index_{i}')} missing category attribute"
                logger.error(error_msg)
                return {"error": "Not all documents have categories"}

        logger.info(f"Found categories: {set(true_labels)}")

        # Perform k-means clustering on embeddings
        # Note: Using fixed random_state for reproducible results across runs
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)

        logger.info(f"K-means clustering complete. Computing evaluation metrics...")

        # Calculate silhouette score (measures cluster quality)
        # Range: [-1, 1] where values closer to 1 indicate better clustering
        silhouette = silhouette_score(embeddings, cluster_labels)

        # Calculate cluster purity (measures category homogeneity within clusters)
        # Range: [0, 1] where 1 means perfect category separation
        purity_score = self._calculate_purity(true_labels, cluster_labels)

        # Analyze detailed composition of each cluster
        cluster_composition = self._analyze_cluster_composition(true_labels, cluster_labels, k)

        logger.info(f"Evaluation complete. Silhouette: {silhouette:.3f}, Purity: {purity_score:.3f}")

        return {
            "silhouette_score": float(silhouette),
            "purity_score": float(purity_score),
            "cluster_composition": cluster_composition,
            "n_clusters": k,
            "n_documents": len(docs),
            "categories_found": list(set(true_labels))
        }

    def _calculate_purity(self, true_labels: List[str], cluster_labels: np.ndarray) -> float:
        """
        Calculate cluster purity score.

        Purity measures the extent to which each cluster contains documents from a single category.
        For each cluster, we count the number of documents from the most frequent category,
        then sum across all clusters and divide by total documents.

        Args:
            true_labels (List[str]): Ground truth category labels for each document
            cluster_labels (np.ndarray): Cluster assignments from k-means (integers 0 to k-1)

        Returns:
            float: Purity score between 0 and 1, where:
                - 1.0 = perfect clustering (each cluster contains only one category)
                - 0.0 = worst possible clustering (completely random assignment)

        Mathematical Formula:
            purity = (1/N) * Σ max_j |w_i ∩ c_j|
            where w_i is cluster i, c_j is category j, N is total documents

        Example:
            If cluster 0 has [ketubah, ketubah, talmud] and cluster 1 has [talmud, talmud],
            then purity = (2 + 2) / 5 = 0.8
        """
        total_correct = 0

        # For each cluster, find the most common true category
        for cluster_id in set(cluster_labels):
            # Get indices of documents assigned to this cluster
            cluster_mask = cluster_labels == cluster_id
            cluster_true_labels = [true_labels[i] for i in range(len(true_labels)) if cluster_mask[i]]

            if cluster_true_labels:
                # Count occurrences of each category in this cluster
                category_counts = Counter(cluster_true_labels)
                # Add the count of the most frequent category to our total
                most_common_count = category_counts.most_common(1)[0][1]
                total_correct += most_common_count

                logger.debug(f"Cluster {cluster_id}: {dict(category_counts)}, "
                             f"dominant category contributes {most_common_count} correct")

        # Return fraction of correctly clustered documents
        purity = total_correct / len(true_labels)
        return purity

    def _analyze_cluster_composition(self, true_labels: List[str], cluster_labels: np.ndarray, k: int) -> dict:
        """
        Analyze the composition of each cluster in terms of document categories.

        This method provides detailed insight into what categories ended up in each cluster,
        helping to understand clustering failures and successes. For each cluster, it computes
        the distribution of categories and identifies the dominant category.

        Args:
            true_labels (List[str]): Ground truth category labels
            cluster_labels (np.ndarray): Cluster assignments from k-means
            k (int): Number of clusters

        Returns:
            dict: Nested dictionary with cluster-level analysis:
                {
                    "cluster_0": {
                        "total_documents": int,
                        "categories": {"category_name": count, ...},
                        "dominant_category": str,
                        "purity": float  # fraction of docs from dominant category
                    },
                    ...
                }

        Example Output:
            {
                "cluster_0": {
                    "total_documents": 25,
                    "categories": {"ketubah": 23, "transactional_letter": 2},
                    "dominant_category": "ketubah",
                    "purity": 0.92
                },
                "cluster_1": {
                    "total_documents": 25,
                    "categories": {"talmud": 25},
                    "dominant_category": "talmud",
                    "purity": 1.0
                }
            }

        Note:
            This analysis helps identify:
            - Which categories cluster well together (high purity)
            - Which categories get confused with each other
            - Empty clusters (if k > actual number of meaningful groups)
        """
        composition = {}

        for cluster_id in range(k):
            # Get all true labels for documents assigned to this cluster
            cluster_mask = cluster_labels == cluster_id
            cluster_true_labels = [true_labels[i] for i in range(len(true_labels)) if cluster_mask[i]]

            if cluster_true_labels:
                # Count how many documents of each category are in this cluster
                category_counts = Counter(cluster_true_labels)
                total_in_cluster = len(cluster_true_labels)

                # Find the most common category in this cluster
                dominant_category, dominant_count = category_counts.most_common(1)[0]
                cluster_purity = dominant_count / total_in_cluster

                composition[f"cluster_{cluster_id}"] = {
                    "total_documents": total_in_cluster,
                    "categories": dict(category_counts),
                    "dominant_category": dominant_category,
                    "purity": cluster_purity
                }

                logger.debug(f"Cluster {cluster_id}: {total_in_cluster} docs, "
                             f"dominated by '{dominant_category}' ({cluster_purity:.2%} pure)")
            else:
                # Handle empty clusters
                composition[f"cluster_{cluster_id}"] = {
                    "total_documents": 0,
                    "categories": {},
                    "dominant_category": None,
                    "purity": 0.0
                }
                logger.warning(f"Cluster {cluster_id} is empty")

        return composition

    def run_controlled_experiment(self, docs: List, embeddings: np.ndarray,
                                  expected_categories: List[str]) -> Dict:
        """
        Run a controlled clustering experiment with known document categories.

        This method is designed for evaluating embedding quality on a curated subset of documents
        where the ground truth categories are well-defined. It performs clustering and evaluates
        whether the embeddings can recover the expected categorical structure.

        Ideal for testing multimodal embeddings on document types like:
        - Ketubah (marriage contracts)
        - Transactional letters
        - Piyyut (liturgical poetry)
        - Talmud pages

        Args:
            docs (List): Documents with assigned categories (must have 'category' attribute)
            embeddings (np.ndarray): Document embeddings matrix
            expected_categories (List[str]): Categories we expect to find (e.g., ['ketubah', 'talmud', ...])

        Returns:
            dict: Comprehensive experiment results including:
                - All metrics from evaluate_clustering()
                - experiment_type: Type of experiment run
                - expected_categories: Categories the experiment was designed for
                - success_criteria: Whether the clustering meets predefined thresholds
                - meets_silhouette: Boolean indicating if silhouette score is acceptable
                - meets_purity: Boolean indicating if purity score is acceptable

        Success Criteria:
            - Silhouette score > 0.3 (reasonable cluster separation)
            - Purity score > 0.7 (70% of documents correctly clustered)

        Raises:
            ValueError: If expected categories are missing from the document set

        Example:
            expected = ['ketubah', 'transactional_letter', 'piyyut', 'talmud']
            results = processor.run_controlled_experiment(docs, embeddings, expected)
            if results['success_criteria']['meets_purity']:
            print("Clustering successfully recovered document categories!")
            else:
            >>>     print("Clustering needs improvement")

        Note:
            This method is particularly valuable for:
            - Validating embedding quality before full-scale deployment
            - Comparing different embedding models or hyperparameters
            - Publishing benchmark results on known document types
            - Debugging why certain categories might be getting confused
        """
        logger.info(f"Running controlled experiment with {len(expected_categories)} expected categories")
        logger.info(f"Expected categories: {expected_categories}")

        # Validate that we have all expected categories in our document set
        actual_categories = set()
        category_counts = Counter()

        for doc in docs:
            if hasattr(doc, 'document_category') and doc.document_category:
                actual_categories.add(doc.document_category)
                category_counts[doc.document_category] += 1

        logger.info(f"Document distribution: {dict(category_counts)}")

        # Check for missing expected categories
        missing_categories = set(expected_categories) - actual_categories
        if missing_categories:
            error_msg = f"Missing expected categories: {missing_categories}"
            logger.error(error_msg)
            return {"error": error_msg}

        # Check for unexpected categories (warning, not error)
        unexpected_categories = actual_categories - set(expected_categories)
        if unexpected_categories:
            logger.warning(f"Found unexpected categories: {unexpected_categories}")

        # Run the clustering evaluation
        k = len(expected_categories)
        logger.info(f"Running k-means with k={k} clusters")

        results = self.evaluate_clustering(docs, embeddings, k)

        # Add experiment-specific metadata and success criteria
        results.update({
            "experiment_type": "controlled_category_test",
            "expected_categories": expected_categories,
            "actual_categories": list(actual_categories),
            "category_distribution": dict(category_counts)
        })

        # Define and evaluate success criteria
        # These thresholds are based on common practices in clustering evaluation:
        # - Silhouette > 0.3: Indicates reasonable cluster structure
        #