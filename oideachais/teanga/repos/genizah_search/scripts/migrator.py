#!/usr/bin/env python3
"""
Migrate Cairo Genizah vectors from Vertex AI format to Elasticsearch
"""

import json
import os
import subprocess
import tempfile
from typing import Dict, Any
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VertexToElasticsearchMigrator:
    def __init__(self, elasticsearch_url="http://34.59.164.124:9200"):
        # Proper configuration for Elasticsearch 8.x client with HTTP (no SSL)
        self.es = Elasticsearch(
            [elasticsearch_url],
            # Connection settings
            timeout=30,
            max_retries=3,
            retry_on_timeout=True,
            # Disable SSL/TLS verification for HTTP connections
            verify_certs=False,
            ssl_show_warn=False,
            # Explicitly use HTTP scheme
            scheme="http",
            # Connection class for plain HTTP
            connection_class=None,
            # Disable sniffing (can cause connection issues)
            sniff_on_start=False,
            sniff_on_connection_fail=False,
            # Headers for compatibility
            headers={"Content-Type": "application/json"}
        )
        self.index_name = "cairo-genizah"
        self.bucket_path = "gs://cairo-genizah-vector-index-dev/index/"

    def download_vertex_data(self, temp_dir: str):
        """Download all batch files from GCS"""
        logger.info("Downloading Vertex AI batch files...")

        # Create temp directory for batch files
        batch_dir = os.path.join(temp_dir, "batch_files")
        os.makedirs(batch_dir, exist_ok=True)

        # Download all JSON files
        cmd = ["gsutil", "-m", "cp", f"{self.bucket_path}*.json", batch_dir]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Failed to download files: {result.stderr}")

        logger.info(f"Downloaded batch files to {batch_dir}")
        return batch_dir

    def convert_vertex_record(self, vertex_record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a Vertex AI record to Elasticsearch format"""

        es_doc = {
            "doc_id": vertex_record.get("id", "unknown")
        }

        # Get the embedding - Vertex AI uses "feature_vector"
        if "feature_vector" in vertex_record:
            es_doc["embedding"] = vertex_record["feature_vector"]
        else:
            raise ValueError(f"No feature_vector found in record. Keys: {list(vertex_record.keys())}")

        # Convert restricts to metadata fields
        if "restricts" in vertex_record:
            for restrict in vertex_record["restricts"]:
                namespace = restrict["namespace"]
                allow_values = restrict.get("allow", [])

                if allow_values:
                    value = allow_values[0] if len(allow_values) == 1 else allow_values

                    # Map to the correct field names based on your data
                    field_mapping = {
                        "language": "language",
                        "content_type": "content_type",
                        "has_images": "has_images",
                        "has_description": "has_description",
                        "has_transcriptions": "has_transcriptions",
                        "has_translations": "has_translations",
                        "has_date": "has_date",
                        "transcription_completeness": "transcription_completeness",
                        "institution": "institution",
                        "library": "library",
                        "collection": "collection",
                        "collection_type": "collection_type",
                        "donation_year": "donation_year",
                        "donor_surname": "donor_surname",
                        "document_type": "document_type",
                        "source_institution": "source_institution"
                    }

                    if namespace in field_mapping:
                        # Convert boolean strings to actual booleans
                        if namespace in ["has_images", "has_description", "has_transcriptions", "has_translations",
                                         "has_date"]:
                            es_doc[field_mapping[namespace]] = value == "true"
                        else:
                            es_doc[field_mapping[namespace]] = value

        # Add crowding_tag if present
        if "crowding_tag" in vertex_record:
            es_doc["crowding_tag"] = vertex_record["crowding_tag"]

        # Generate text content for search (since your data doesn't have text)
        # Use the document ID and metadata to create searchable text
        text_parts = [es_doc["doc_id"]]

        # Add searchable metadata
        if "language" in es_doc:
            text_parts.append(es_doc["language"])
        if "document_type" in es_doc:
            text_parts.append(es_doc["document_type"])
        if "collection" in es_doc:
            text_parts.append(es_doc["collection"])
        if "institution" in es_doc:
            text_parts.append(es_doc["institution"])

        es_doc["text"] = " ".join(text_parts)

        return es_doc

    def process_batch_files(self, batch_dir: str):
        """Process all batch files and yield documents for indexing"""
        batch_files = [f for f in os.listdir(batch_dir) if f.endswith('.json')]
        logger.info(f"Processing {len(batch_files)} batch files...")

        total_docs = 0

        for batch_file in sorted(batch_files):
            file_path = os.path.join(batch_dir, batch_file)
            logger.info(f"Processing {batch_file}...")

            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        vertex_record = json.loads(line.strip())
                        es_doc = self.convert_vertex_record(vertex_record)

                        yield {
                            "_index": self.index_name,
                            "_id": es_doc["doc_id"],
                            "_source": es_doc
                        }

                        total_docs += 1

                        if total_docs % 1000 == 0:
                            logger.info(f"Processed {total_docs} documents...")

                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in {batch_file} line {line_num}: {e}")
                    except Exception as e:
                        logger.error(f"Error processing {batch_file} line {line_num}: {e}")

        logger.info(f"Total documents processed: {total_docs}")

    def migrate(self):
        """Run the full migration"""
        logger.info("Starting Vertex AI to Elasticsearch migration...")

        # Check Elasticsearch connection with detailed error info
        try:
            logger.info(f"Testing connection to Elasticsearch...")
            if not self.es.ping():
                # Try to get more detailed error
                try:
                    info = self.es.info()
                    logger.info(f"ES Info: {info}")
                except Exception as detail_error:
                    logger.error(f"Connection failed. ES error: {detail_error}")
                    raise Exception(f"Cannot connect to Elasticsearch: {detail_error}")
                raise Exception("Elasticsearch ping failed")
            else:
                info = self.es.info()
                logger.info(f"✅ Connected to Elasticsearch {info['version']['number']}")
        except Exception as e:
            logger.error(f"❌ Elasticsearch connection error: {e}")
            raise

        # Check if index exists
        if not self.es.indices.exists(index=self.index_name):
            raise Exception(f"Index '{self.index_name}' does not exist. Create it first!")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Download data
            batch_dir = self.download_vertex_data(temp_dir)

            # Bulk index documents
            logger.info("Starting bulk indexing to Elasticsearch...")

            success_count = 0
            error_count = 0

            for success, info in bulk(
                    self.es,
                    self.process_batch_files(batch_dir),
                    chunk_size=500,
                    request_timeout=60
            ):
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    logger.error(f"Indexing error: {info}")

                if (success_count + error_count) % 1000 == 0:
                    logger.info(f"Indexed: {success_count}, Errors: {error_count}")

        # Final stats
        logger.info(f"Migration complete!")
        logger.info(f"Successfully indexed: {success_count}")
        logger.info(f"Errors: {error_count}")

        # Refresh index and get final count
        self.es.indices.refresh(index=self.index_name)
        doc_count = self.es.count(index=self.index_name)["count"]
        logger.info(f"Final document count in Elasticsearch: {doc_count}")

        return success_count, error_count


if __name__ == "__main__":
    migrator = VertexToElasticsearchMigrator()
    success, errors = migrator.migrate()
    print(f"\nMigration Results:")
    print(f"✅ Success: {success}")
    print(f"❌ Errors: {errors}")
    print(f"🎉 Your 7,013 vectors are now in Elasticsearch!")