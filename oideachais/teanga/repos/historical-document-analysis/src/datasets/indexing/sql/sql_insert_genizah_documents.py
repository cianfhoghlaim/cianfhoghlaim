#!/usr/bin/env python3
"""
SQL Inserter for Genizah Documents

This script processes JSON files containing Genizah document data and inserts
them into PostgreSQL tables using the genizah_schema.sql schema.

It handles both Cambridge and Princeton format documents, creating proper
relationships between documents, sources, shelf mark variants, and images.

Usage:
    python sql_insert_genizah_documents.py --config config.json --input-dir /path/to/json/files
"""

import json
import logging
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
from dataclasses import dataclass

# Import our document models
from src.datasets.document_models.genizah_document import GenizahDocument

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str
    port: int
    database: str
    user: str
    password: str


class GenizahSQLInserter:
    """Handles insertion of Genizah documents into PostgreSQL database."""
    
    def __init__(self, db_config: DatabaseConfig):
        """Initialize the inserter with database configuration."""
        self.db_config = db_config
        self.connection = None
        self.cursor = None
        
        # Statistics tracking
        self.stats = {
            'documents_processed': 0,
            'documents_inserted': 0,
            'source_records_inserted': 0,
            'shelf_mark_variants_inserted': 0,
            'images_inserted': 0,
            'errors': 0
        }
        
        # Cache for document UUIDs by shelf mark to avoid duplicates
        self.shelf_mark_cache = {}
        
    def connect(self):
        """Connect to the PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(
                host=self.db_config.host,
                port=self.db_config.port,
                database=self.db_config.database,
                user=self.db_config.user,
                password=self.db_config.password,
                cursor_factory=RealDictCursor
            )
            self.cursor = self.connection.cursor()
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from the database."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Disconnected from database")
    
    def process_json_file(self, file_path: str, source_name: str = "unknown", batch_size: int = 100, resume_from: int = 0) -> None:
        """Process a single JSON file and insert documents into the database."""
        logger.info(f"Processing file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON file formats
        documents = self._extract_documents_from_json(data, file_path)
        
        logger.info(f"Found {len(documents)} documents in {file_path}")
        
        if resume_from > 0:
            logger.info(f"Resuming from document {resume_from + 1}")
            documents = documents[resume_from:]
        
        # Process documents in batches
        for i in range(0, len(documents), batch_size):
            batch_end = min(i + batch_size, len(documents))
            batch = documents[i:batch_end]
            actual_start = resume_from + i + 1
            actual_end = resume_from + batch_end
            
            logger.info(f"Processing batch {i // batch_size + 1}: documents {actual_start}-{actual_end}")
            
            for doc_data in batch:
                self._process_document(doc_data, source_name, file_path)
                self.stats['documents_processed'] += 1
            
            # Commit after each batch
            self.connection.commit()
            logger.info(f"Committed batch {i // batch_size + 1}. Processed {self.stats['documents_processed']} documents so far")
        
        logger.info(f"Completed processing {len(documents)} documents from {file_path}")
    
    def _extract_documents_from_json(self, data: Any, file_path: str) -> List[Dict[str, Any]]:
        """Extract document list from various JSON file formats."""
        documents = []
        
        if isinstance(data, dict):
            # Check for Cambridge format with "documents" key
            if 'documents' in data:
                documents = data['documents']
            # Check for Princeton/Rylands format with document IDs as keys
            elif all(isinstance(k, str) and not k.startswith('scraping_metadata') and not k.startswith('metadata_analysis') for k in data.keys()):
                # This is Princeton/Rylands format - document IDs as keys
                documents = list(data.values())
            # Single document
            elif 'doc_id' in data or 'shelf_mark' in data or 'images' in data:
                documents = [data]
            else:
                logger.warning(f"Unknown JSON format in {file_path}")
                logger.warning(f"Keys found: {list(data.keys())[:10]}")  # Show first 10 keys
        elif isinstance(data, list):
            documents = data
        
        return documents
    
    def _process_document(self, doc_data: Dict[str, Any], source_name: str, file_path: str) -> None:
        """Process a single document and insert it into the database."""
        # Create GenizahDocument object to standardize the data
        if source_name.lower() == 'cambridge':
            doc = GenizahDocument.from_cambridge_format(doc_data)
        elif source_name.lower() == 'rylands':
            # Rylands documents use Princeton format but with joins_data
            doc = GenizahDocument.from_princeton_format(doc_data)
        else:
            doc = GenizahDocument.from_princeton_format(doc_data)
        
        # Extract shelf mark - this is critical
        shelf_mark = self._extract_shelf_mark(doc, doc_data)
        if not shelf_mark:
            logger.warning(f"No shelf mark found for document, skipping: {doc.doc_id}")
            return
        
        # Check if document already exists
        existing_uuid = self._get_document_uuid_by_shelf_mark(shelf_mark)
        if existing_uuid:
            logger.info(f"Document with shelf mark {shelf_mark} already exists, merging information from {source_name}")
            document_uuid = existing_uuid
            
            # Merge new information into existing document
            self._merge_document_information(document_uuid, doc, source_name)
        else:
            # Insert new document
            document_uuid = self._insert_document(doc, shelf_mark, source_name)
            self.shelf_mark_cache[shelf_mark] = document_uuid
        
        # Insert source record (will update if exists due to ON CONFLICT)
        self._insert_source_record(document_uuid, doc, source_name, file_path)
        
        # Insert shelf mark variants
        self._insert_shelf_mark_variants(document_uuid, doc, shelf_mark, source_name)
        
        # Insert images
        self._insert_images(document_uuid, doc, source_name)
        
        self.stats['documents_inserted'] += 1
    
    def _extract_shelf_mark(self, doc: GenizahDocument, doc_data: Dict[str, Any]) -> Optional[str]:
        """Extract shelf mark from document data."""
        # Try various sources for shelf mark
        if doc.shelf_mark:
            return doc.shelf_mark
        
        if doc.doc_id:
            # For Cambridge documents, doc_id might include page numbers
            if '/' in doc.doc_id:
                return doc.doc_id.split('/')[0]
            return doc.doc_id
        
        # Try to extract from TEI metadata
        if doc.full_metadata:
            for key, value in doc.full_metadata.items():
                if 'idno' in key.lower() and value:
                    return str(value)
        
        # Try to extract from original URL
        if doc.original_url:
            # Extract MS-* pattern from URL
            match = re.search(r'MS-[A-Z]+-[A-Z]+-\d{5}-\d{5}', doc.original_url)
            if match:
                return match.group()
        
        # For Rylands documents, try joins_data mainShelfmark
        if doc.joins_data and 'mainShelfmark' in doc.joins_data:
            return doc.joins_data['mainShelfmark']
        
        # Fallback: use doc_id from raw data
        if 'doc_id' in doc_data and doc_data['doc_id']:
            return doc_data['doc_id']
        
        return None
    
    def _get_document_uuid_by_shelf_mark(self, shelf_mark: str) -> Optional[str]:
        """Get document UUID by shelf mark, using cache first."""
        if shelf_mark in self.shelf_mark_cache:
            return self.shelf_mark_cache[shelf_mark]
        
        try:
            self.cursor.execute(
                "SELECT uuid FROM genizah_documents WHERE canonical_shelf_mark = %s",
                (shelf_mark,)
            )
            result = self.cursor.fetchone()
            if result:
                uuid_str = str(result['uuid'])
                self.shelf_mark_cache[shelf_mark] = uuid_str
                return uuid_str
        except Exception as e:
            logger.error(f"Error checking existing document: {e}")
        
        return None
    
    def _source_record_exists(self, document_uuid: str, source_name: str, source_id: str) -> bool:
        """Check if a source record already exists for this document and source."""
        try:
            self.cursor.execute(
                "SELECT 1 FROM document_source_records WHERE document_uuid = %s AND source_name = %s AND source_id = %s",
                (document_uuid, source_name, source_id)
            )
            return self.cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking source record existence: {e}")
            return False
    
    def _merge_document_information(self, document_uuid: str, new_doc: GenizahDocument, source_name: str) -> None:
        """Merge new information into existing document, preferring more complete data."""
        
        # Get existing document data
        try:
            self.cursor.execute(
                "SELECT * FROM genizah_documents WHERE uuid = %s",
                (document_uuid,)
            )
            existing_doc = self.cursor.fetchone()
            
            if not existing_doc:
                logger.error(f"Document {document_uuid} not found for merging")
                return
        except Exception as e:
            logger.error(f"Error fetching existing document {document_uuid}: {e}")
            return
        
        # Extract information from new document
        temporal_info = new_doc.extract_temporal_info()
        language_info = new_doc.extract_language_info()
        physical_info = new_doc.extract_physical_info()
        
        # Determine what to update based on completeness and source priority
        updates = {}
        
        # Merge transcription (append if new source has more)
        new_transcription = self._combine_transcriptions(new_doc.transcriptions)
        if new_transcription and (not existing_doc['transcription'] or len(new_transcription) > len(existing_doc['transcription'] or '')):
            updates['transcription'] = new_transcription
            updates['has_transcription'] = True
            logger.info(f"Updated transcription from {source_name}")
        
        # Merge translation (append if new source has more)
        new_translation = ' '.join(new_doc.translations) if new_doc.translations else None
        if new_translation and (not existing_doc['translation'] or len(new_translation) > len(existing_doc['translation'] or '')):
            updates['translation'] = new_translation
            updates['has_translation'] = True
            logger.info(f"Updated translation from {source_name}")
        
        # Merge description (prefer longer, more detailed descriptions)
        if new_doc.description and len(new_doc.description) > len(existing_doc['description'] or ''):
            updates['description'] = new_doc.description
            logger.info(f"Updated description from {source_name}")
        
        # Merge dating information (prefer more specific dates)
        if temporal_info.date_start and not existing_doc['dating_start_year']:
            updates['dating_start_year'] = self._extract_year(temporal_info.date_start)
            updates['dating_text'] = temporal_info.date_display
            logger.info(f"Updated dating from {source_name}")
        
        # Merge language information (prefer more complete language data)
        if language_info.main_language and not existing_doc['language']:
            updates['language'] = [language_info.main_language]
            updates['script'] = [language_info.script_type] if language_info.script_type else []
            logger.info(f"Updated language from {source_name}")
        
        # Merge physical information (prefer more detailed physical data)
        if physical_info.material and not existing_doc['material']:
            updates['material'] = physical_info.material
            logger.info(f"Updated material from {source_name}")
        
        if physical_info.condition and not existing_doc['condition_notes']:
            updates['condition_notes'] = physical_info.condition
            logger.info(f"Updated condition from {source_name}")
        
        # Merge joins information (append new joins)
        if new_doc.joins_data and 'joinedManuscripts' in new_doc.joins_data:
            existing_joins = existing_doc['joins_with'] or []
            new_joins = []
            for join in new_doc.joins_data['joinedManuscripts']:
                if 'shelfmark' in join and join['shelfmark'] not in existing_joins:
                    new_joins.append(join['shelfmark'])
            
            if new_joins:
                updates['joins_with'] = existing_joins + new_joins
                logger.info(f"Added new joins from {source_name}: {new_joins}")
        
        # Merge images (append new images)
        if new_doc.image_urls:
            # Get existing image count
            try:
                self.cursor.execute(
                    "SELECT COUNT(*) FROM genizah_images WHERE document_uuid = %s",
                    (document_uuid,)
                )
                result = self.cursor.fetchone()
                existing_image_count = result[0] if result else 0
                
                if len(new_doc.image_urls) > existing_image_count:
                    updates['image_count'] = len(new_doc.image_urls)
                    updates['has_images'] = True
                    logger.info(f"Updated image count from {source_name}")
            except Exception as e:
                logger.error(f"Error getting image count for document {document_uuid}: {e}")
                # Default to updating image count if we can't check
                updates['image_count'] = len(new_doc.image_urls)
                updates['has_images'] = True
        
        # Update completeness score
        if updates:
            new_completeness = new_doc.calculate_completeness_score()
            if new_completeness > existing_doc['completeness_score']:
                updates['completeness_score'] = new_completeness
                logger.info(f"Updated completeness score from {source_name}")
        
        # Update metadata (merge JSON metadata)
        if new_doc.full_metadata or new_doc.joins_data or new_doc.miscellaneous_info:
            existing_metadata = json.loads(existing_doc['metadata']) if existing_doc['metadata'] else {}
            new_metadata = {
                'original_url': new_doc.original_url,
                'doc_id': new_doc.doc_id,
                'full_metadata': new_doc.full_metadata,
                'joins_data': new_doc.joins_data,
                'miscellaneous_info': new_doc.miscellaneous_info
            }
            
            # Merge metadata, preferring non-null values
            merged_metadata = existing_metadata.copy()
            for key, value in new_metadata.items():
                if value is not None and value != "":
                    merged_metadata[key] = value
            
            updates['metadata'] = json.dumps(merged_metadata)
            logger.info(f"Merged metadata from {source_name}")
        
        # Apply updates if any
        if updates:
            try:
                update_fields = []
                update_values = []
                
                for field, value in updates.items():
                    update_fields.append(f"{field} = %s")
                    update_values.append(value)
                
                update_values.append(document_uuid)
                
                update_query = f"""
                    UPDATE genizah_documents 
                    SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                    WHERE uuid = %s
                """
                
                self.cursor.execute(update_query, update_values)
                logger.info(f"Merged {len(updates)} fields from {source_name} into document {document_uuid}")
            except Exception as e:
                logger.error(f"Error updating document {document_uuid}: {e}")
                raise
        else:
            logger.info(f"No new information to merge from {source_name}")
    
    def _insert_document(self, doc: GenizahDocument, shelf_mark: str, source_name: str) -> str:
        """Insert a new document into genizah_documents table."""
        document_uuid = str(uuid.uuid4())
        
        # Extract standardized information
        temporal_info = doc.extract_temporal_info()
        language_info = doc.extract_language_info()
        physical_info = doc.extract_physical_info()
        institutional_info = doc.extract_institutional_info()
        
        # Determine institution and collection
        institution = institutional_info.institution or "Unknown"
        collection = institutional_info.collection_name or "Unknown"
        
        # Special handling for Rylands documents
        if source_name.lower() == 'rylands':
            institution = "Rylands"
            collection = "Friedberger Collection"
        elif shelf_mark and shelf_mark.startswith('Manchester:'):
            institution = "Rylands"
            collection = "Friedberger Collection"
        
        # Extract subcollection from shelf mark (e.g., AS, NS, F from MS-TS-AS-*)
        subcollection = None
        if shelf_mark.startswith('MS-TS-'):
            parts = shelf_mark.split('-')
            if len(parts) >= 3:
                subcollection = parts[2]
        
        # Extract joins information for Rylands documents
        joins_with = []
        if doc.joins_data and 'joinedManuscripts' in doc.joins_data:
            for join in doc.joins_data['joinedManuscripts']:
                if 'shelfmark' in join:
                    joins_with.append(join['shelfmark'])
        
        # Prepare document data
        doc_data = {
            'uuid': document_uuid,
            'canonical_shelf_mark': shelf_mark,
            'institution': institution,
            'collection': collection,
            'subcollection': subcollection,
            'document_type': doc.infer_document_type(),
            'language': [language_info.main_language] if language_info.main_language else [],
            'script': [language_info.script_type] if language_info.script_type else [],
            'transcription': self._combine_transcriptions(doc.transcriptions),
            'translation': ' '.join(doc.translations) if doc.translations else None,
            'description': doc.description,
            'dating_text': temporal_info.date_display,
            'dating_start_year': self._extract_year(temporal_info.date_start),
            'dating_end_year': self._extract_year(temporal_info.date_end),
            'place_written': None,  # Could be extracted from metadata
            'material': physical_info.material,
            'condition_notes': physical_info.condition,
            'paleographic_notes': None,  # Could be extracted from metadata
            'joins_with': joins_with,  # Now properly populated for Rylands documents
            'related_documents': [],
            'completeness_score': doc.calculate_completeness_score(),
            'has_transcription': bool(doc.transcriptions),
            'has_translation': bool(doc.translations),
            'has_images': bool(doc.image_urls),
            'image_count': len(doc.image_urls) if doc.image_urls else 0,
            'metadata': json.dumps({
                'original_url': doc.original_url,
                'doc_id': doc.doc_id,
                'full_metadata': doc.full_metadata,
                'joins_data': doc.joins_data,
                'miscellaneous_info': doc.miscellaneous_info
            })
        }
        
        # Insert document
        insert_query = """
            INSERT INTO genizah_documents (
                uuid, canonical_shelf_mark, institution, collection, subcollection,
                document_type, language, script, transcription, translation, description,
                dating_text, dating_start_year, dating_end_year, place_written,
                material, condition_notes, paleographic_notes, joins_with, related_documents,
                completeness_score, has_transcription, has_translation, has_images, image_count,
                metadata
            ) VALUES (
                %(uuid)s, %(canonical_shelf_mark)s, %(institution)s, %(collection)s, %(subcollection)s,
                %(document_type)s, %(language)s, %(script)s, %(transcription)s, %(translation)s, %(description)s,
                %(dating_text)s, %(dating_start_year)s, %(dating_end_year)s, %(place_written)s,
                %(material)s, %(condition_notes)s, %(paleographic_notes)s, %(joins_with)s, %(related_documents)s,
                %(completeness_score)s, %(has_transcription)s, %(has_translation)s, %(has_images)s, %(image_count)s,
                %(metadata)s
            )
        """
        
        self.cursor.execute(insert_query, doc_data)
        logger.debug(f"Inserted document: {shelf_mark}")
        
        return document_uuid
    
    def _insert_source_record(self, document_uuid: str, doc: GenizahDocument, source_name: str, file_path: str) -> None:
        """Insert a source record for the document."""
        source_record_uuid = str(uuid.uuid4())
        
        # Determine source ID
        source_id = doc.doc_id or doc.shelf_mark or str(uuid.uuid4())
        
        source_data = {
            'uuid': source_record_uuid,
            'document_uuid': document_uuid,
            'source_name': source_name,
            'source_id': source_id,
            'source_url': doc.original_url,
            'source_shelf_mark': doc.shelf_mark,
            'source_metadata': json.dumps({
                'file_path': file_path,
                'processed_at': datetime.now().isoformat(),
                'full_metadata': doc.full_metadata,
                'joins_data': doc.joins_data
            }),
            'metadata_quality': self._assess_metadata_quality(doc),
            'is_primary_source': True,  # Assume first source is primary
            'scraped_at': datetime.now()
        }
        
        insert_query = """
            INSERT INTO document_source_records (
                uuid, document_uuid, source_name, source_id, source_url, source_shelf_mark,
                source_metadata, metadata_quality, is_primary_source, scraped_at
            ) VALUES (
                %(uuid)s, %(document_uuid)s, %(source_name)s, %(source_id)s, %(source_url)s, %(source_shelf_mark)s,
                %(source_metadata)s, %(metadata_quality)s, %(is_primary_source)s, %(scraped_at)s
            )
            ON CONFLICT (source_name, source_id) DO UPDATE SET
                source_url = EXCLUDED.source_url,
                source_shelf_mark = EXCLUDED.source_shelf_mark,
                source_metadata = EXCLUDED.source_metadata,
                metadata_quality = EXCLUDED.metadata_quality,
                updated_at = CURRENT_TIMESTAMP
        """
        
        self.cursor.execute(insert_query, source_data)
        self.stats['source_records_inserted'] += 1
        logger.debug(f"Inserted source record for document: {document_uuid}")
    
    def _insert_shelf_mark_variants(self, document_uuid: str, doc: GenizahDocument, canonical_shelf_mark: str, source_name: str) -> None:
        """Insert shelf mark variants for the document."""
        variants = set()
        
        # Add canonical shelf mark
        variants.add(canonical_shelf_mark)
        
        # Add doc_id if different
        if doc.doc_id and doc.doc_id != canonical_shelf_mark:
            variants.add(doc.doc_id)
        
        # Add variants from joins_data (especially for Rylands documents)
        if doc.joins_data and 'joinedManuscripts' in doc.joins_data:
            for join in doc.joins_data['joinedManuscripts']:
                if 'shelfmark' in join:
                    variants.add(join['shelfmark'])
        
        # Add mainShelfmark from joins_data if different
        if doc.joins_data and 'mainShelfmark' in doc.joins_data:
            main_shelfmark = doc.joins_data['mainShelfmark']
            if main_shelfmark and main_shelfmark != canonical_shelf_mark:
                variants.add(main_shelfmark)
        
        # Insert variants
        for variant in variants:
            if variant:  # Skip empty variants
                variant_uuid = str(uuid.uuid4())
                
                # Determine variant type
                variant_type = 'normalized'
                if variant != canonical_shelf_mark:
                    if doc.joins_data and 'joinedManuscripts' in doc.joins_data:
                        # Check if this variant is from joins_data
                        is_from_joins = any(join.get('shelfmark') == variant for join in doc.joins_data['joinedManuscripts'])
                        variant_type = 'join' if is_from_joins else 'database'
                    else:
                        variant_type = 'database'
                
                variant_data = {
                    'uuid': variant_uuid,
                    'document_uuid': document_uuid,
                    'variant_shelf_mark': variant,
                    'variant_type': variant_type,
                    'source': source_name
                }
                
                insert_query = """
                    INSERT INTO shelf_mark_variants (
                        uuid, document_uuid, variant_shelf_mark, variant_type, source
                    ) VALUES (
                        %(uuid)s, %(document_uuid)s, %(variant_shelf_mark)s, %(variant_type)s, %(source)s
                    )
                    ON CONFLICT (variant_shelf_mark) DO NOTHING
                """
                
                self.cursor.execute(insert_query, variant_data)
                self.stats['shelf_mark_variants_inserted'] += 1
    
    def _insert_images(self, document_uuid: str, doc: GenizahDocument, source_name: str) -> None:
        """Insert image records for the document."""
        if not doc.image_urls:
            return
        
        for i, image_url in enumerate(doc.image_urls):
            image_uuid = str(uuid.uuid4())
            
            # Extract image metadata if available
            image_metadata = None
            if doc.image_metadata and i < len(doc.image_metadata):
                image_metadata = doc.image_metadata[i]
            
            image_data = {
                'uuid': image_uuid,
                'document_uuid': document_uuid,
                'source_name': source_name,
                'source_record_uuid': None,  # Could be linked to source record
                'image_url': image_url,
                'thumbnail_url': None,  # Could be generated
                'image_order': i + 1,
                'side': self._extract_image_side(image_metadata),
                'folio_number': self._extract_folio_number(image_metadata),
                'image_type': 'color',  # Default
                'width': self._extract_image_dimension(image_metadata, 'width'),
                'height': self._extract_image_dimension(image_metadata, 'height'),
                'resolution': None,
                'file_format': self._extract_file_format(image_url),
                'file_size_bytes': None,
                'quality_score': None,
                'iiif_manifest_url': None,
                'iiif_image_id': None,
                'metadata': json.dumps(image_metadata) if image_metadata else None
            }
            
            insert_query = """
                INSERT INTO genizah_images (
                    uuid, document_uuid, source_name, source_record_uuid, image_url, thumbnail_url,
                    image_order, side, folio_number, image_type, width, height, resolution,
                    file_format, file_size_bytes, quality_score, iiif_manifest_url, iiif_image_id, metadata
                ) VALUES (
                    %(uuid)s, %(document_uuid)s, %(source_name)s, %(source_record_uuid)s, %(image_url)s, %(thumbnail_url)s,
                    %(image_order)s, %(side)s, %(folio_number)s, %(image_type)s, %(width)s, %(height)s, %(resolution)s,
                    %(file_format)s, %(file_size_bytes)s, %(quality_score)s, %(iiif_manifest_url)s, %(iiif_image_id)s, %(metadata)s
                )
                ON CONFLICT (document_uuid, source_name, image_order) DO UPDATE SET
                    image_url = EXCLUDED.image_url,
                    thumbnail_url = EXCLUDED.thumbnail_url,
                    side = EXCLUDED.side,
                    folio_number = EXCLUDED.folio_number,
                    image_type = EXCLUDED.image_type,
                    width = EXCLUDED.width,
                    height = EXCLUDED.height,
                    resolution = EXCLUDED.resolution,
                    file_format = EXCLUDED.file_format,
                    file_size_bytes = EXCLUDED.file_size_bytes,
                    quality_score = EXCLUDED.quality_score,
                    iiif_manifest_url = EXCLUDED.iiif_manifest_url,
                    iiif_image_id = EXCLUDED.iiif_image_id,
                    metadata = EXCLUDED.metadata,
                    updated_at = CURRENT_TIMESTAMP
            """
            
            self.cursor.execute(insert_query, image_data)
            self.stats['images_inserted'] += 1
    
    def _combine_transcriptions(self, transcriptions: List) -> Optional[str]:
        """Combine all transcriptions into a single text."""
        if not transcriptions:
            return None
        
        text_parts = []
        for trans in transcriptions:
            if hasattr(trans, 'lines'):
                if isinstance(trans.lines, dict):
                    text_parts.extend(str(line) for line in trans.lines.values() if line)
                elif isinstance(trans.lines, list):
                    text_parts.extend(str(line) for line in trans.lines if line)
                else:
                    text_parts.append(str(trans.lines))
        
        return ' '.join(text_parts) if text_parts else None
    
    def _extract_year(self, date_string: Optional[str]) -> Optional[int]:
        """Extract year from date string."""
        if not date_string:
            return None
        
        # Extract year from ISO date format
        match = re.search(r'(\d{4})', str(date_string))
        if match:
            year = int(match.group(1))
            # Sanity check for reasonable years
            if -500 <= year <= 2000:
                return year
        
        return None
    
    def _assess_metadata_quality(self, doc: GenizahDocument) -> str:
        """Assess the quality of document metadata."""
        score = doc.calculate_completeness_score()
        
        if score >= 0.8:
            return 'high'
        elif score >= 0.6:
            return 'medium'
        else:
            return 'low'
    
    def _extract_image_side(self, image_metadata: Optional[Dict]) -> Optional[str]:
        """Extract image side from metadata."""
        if not image_metadata:
            return None
        
        # Look for side indicators in metadata
        for key, value in image_metadata.items():
            if 'side' in key.lower() or 'recto' in str(value).lower() or 'verso' in str(value).lower():
                return str(value).lower()
        
        return None
    
    def _extract_folio_number(self, image_metadata: Optional[Dict]) -> Optional[str]:
        """Extract folio number from metadata."""
        if not image_metadata:
            return None
        
        # Look for folio indicators
        for key, value in image_metadata.items():
            if 'folio' in key.lower() or 'page' in key.lower():
                return str(value)
        
        return None
    
    def _extract_image_dimension(self, image_metadata: Optional[Dict], dimension: str) -> Optional[int]:
        """Extract image dimension from metadata."""
        if not image_metadata:
            return None
        
        # Look for dimension indicators
        for key, value in image_metadata.items():
            if dimension.lower() in key.lower():
                try:
                    return int(float(str(value)))
                except (ValueError, TypeError):
                    pass
        
        return None
    
    def _extract_file_format(self, image_url: str) -> Optional[str]:
        """Extract file format from image URL."""
        if not image_url:
            return None
        
        # Extract extension
        match = re.search(r'\.([a-zA-Z0-9]+)(?:\?|$)', image_url)
        if match:
            return match.group(1).lower()
        
        return None
    
    def print_statistics(self) -> None:
        """Print processing statistics."""
        logger.info("=== Processing Statistics ===")
        logger.info(f"Documents processed: {self.stats['documents_processed']}")
        logger.info(f"Documents inserted: {self.stats['documents_inserted']}")
        logger.info(f"Source records inserted: {self.stats['source_records_inserted']}")
        logger.info(f"Shelf mark variants inserted: {self.stats['shelf_mark_variants_inserted']}")
        logger.info(f"Images inserted: {self.stats['images_inserted']}")
        logger.info(f"Errors: {self.stats['errors']}")


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


def main():
    """Main function to run the SQL inserter."""
    parser = argparse.ArgumentParser(description='Insert Genizah documents into PostgreSQL database')
    parser.add_argument('--config', required=True, help='Database configuration JSON file')
    parser.add_argument('--input-dir', required=True, help='Directory containing JSON files to process')
    parser.add_argument('--source-name', default='unknown', help='Source name for documents (e.g., cambridge, princeton)')
    parser.add_argument('--test-mode', action='store_true', help='Process only first 10 documents for testing')
    
    args = parser.parse_args()
    
    # Load database configuration
    db_config = load_database_config(args.config)
    
    # Initialize inserter
    inserter = GenizahSQLInserter(db_config)
    
    try:
        # Connect to database
        inserter.connect()
        
        # Process JSON files
        input_dir = Path(args.input_dir)
        json_files = list(input_dir.glob('*.json'))
        
        if not json_files:
            logger.error(f"No JSON files found in {input_dir}")
            return
        
        logger.info(f"Found {len(json_files)} JSON files to process")
        
        for json_file in json_files:
            logger.info(f"Processing {json_file.name}")
            inserter.process_json_file(str(json_file), args.source_name)
            
            if args.test_mode and inserter.stats['documents_processed'] >= 10:
                logger.info("Test mode: stopping after 10 documents")
                break
        
        # Print final statistics
        inserter.print_statistics()
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        raise
    finally:
        inserter.disconnect()


if __name__ == '__main__':
    main()
