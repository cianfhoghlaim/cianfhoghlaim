# File name: index_cairo_documents.py
#
import json
import os
import logging
from tqdm import tqdm
from typing import List, Dict
from src.datasets.cairo_genizah.indexing.elastic_index_genizah import ElasticsearchGenizahProcessor
from src.datasets.document_models.genizah_document import GenizahDocument
from src.datasets.cairo_genizah.indexing.image_url_helpers import ImageURLHelper
from src.embeddings.embedding_models import NomicsEmbedding
import dotenv
import re
dotenv.load_dotenv()
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',   force=True)
logger = logging.getLogger(__name__)
logger.info("Logging configuration test - this should appear!")


class UniversalURLConverter:
    def __init__(self, bucket_base_url="https://storage.googleapis.com/cairo-genizah-es-json/raw_images"):
        self.bucket_base_url = bucket_base_url
        # Pattern to match any MS-{TYPE}-{TYPE}-{numbers} format
        self.pattern = r'MS-[A-Z]+-[A-Z]+-\d{5}-\d{5}-\d{3}-\d{5}'
        self.shelf_pattern = r'MS-[A-Z]+-[A-Z]+-\d{5}-\d{5}'

    def extract_full_id(self, url):
        """Extract the full MS ID including page numbers"""
        # Handle split format first
        if '/1-000-00001' in url:
            base_match = re.search(self.shelf_pattern, url)
            suffix_match = re.search(r'/(\d+-\d{3}-\d{5})', url)
            if base_match and suffix_match:
                return base_match.group() + '-' + suffix_match.group(1)

        # Handle standard format
        match = re.search(self.pattern, url)
        return match.group() if match else None

    def extract_shelf_mark(self, url):
        """Extract just the shelf mark (without page numbers)"""
        match = re.search(self.shelf_pattern, url)
        return match.group() if match else None

    def convert_url(self, cambridge_url):
        """Convert Cambridge URL to your bucket URL"""
        full_id = self.extract_full_id(cambridge_url)
        if full_id:
            return f"{self.bucket_base_url}/{full_id}.jpg"
        return None

def extract_shelf_mark(url):
    pattern = r'MS-TS-AS-\d{5}-\d{5}'
    match = re.search(pattern, url)
    return match.group() if match else "unknown-shelfmark"

def deduplicate_cambridge_documents(documents: List[Dict]) -> List[Dict]:
    """
    Deduplicate Cambridge documents by merging entries with the same shelf mark.
    
    Documents with the same shelf mark but different page suffixes (e.g., /1, /2) 
    are merged into a single unified document entry.
    
    :param documents: List of Cambridge document dictionaries
    :type documents: List[Dict]
    :return: List of deduplicated documents
    :rtype: List[Dict]
    """
    logger.info(f"Starting deduplication of {len(documents)} Cambridge documents...")
    
    # Group documents by shelf mark
    shelf_mark_groups = {}
    
    for doc in documents:
        # Extract shelf mark from TEI metadata
        shelf_mark = None
        if 'full_metadata_info' in doc:
            shelf_mark = doc['full_metadata_info'].get('{http://www.tei-c.org/ns/1.0}idno')
        
        # If no shelf mark in metadata, try to extract from doc_id
        if not shelf_mark and 'doc_id' in doc and doc['doc_id']:
            # Remove page suffix (e.g., MS-MOSSERI-I-00033-00006/1 -> MS-MOSSERI-I-00033-00006)
            shelf_mark = doc['doc_id'].split('/')[0]
        
        if not shelf_mark:
            logger.warning(f"No shelf mark found for document {doc.get('doc_id', 'unknown')}")
            # Use doc_id as fallback
            shelf_mark = doc.get('doc_id', f"unknown_{len(shelf_mark_groups)}")
        
        # Group by shelf mark
        if shelf_mark not in shelf_mark_groups:
            shelf_mark_groups[shelf_mark] = []
        shelf_mark_groups[shelf_mark].append(doc)
    
    logger.info(f"Found {len(shelf_mark_groups)} unique shelf marks")
    
    # Merge documents with the same shelf mark
    merged_documents = []
    
    for shelf_mark, doc_group in shelf_mark_groups.items():
        if len(doc_group) == 1:
            # Single document - no merging needed
            merged_doc = doc_group[0].copy()
            merged_doc['shelf_mark'] = shelf_mark
            merged_doc['doc_id'] = shelf_mark  # Use shelf mark as unified doc_id
            merged_documents.append(merged_doc)
        else:
            # Multiple documents - merge them
            logger.info(f"Merging {len(doc_group)} documents for shelf mark: {shelf_mark}")
            merged_doc = merge_document_group(doc_group, shelf_mark)
            merged_documents.append(merged_doc)
    
    logger.info(f"Deduplication complete: {len(documents)} -> {len(merged_documents)} documents")
    return merged_documents


def merge_document_group(doc_group: List[Dict], shelf_mark: str) -> Dict:
    """
    Merge a group of documents with the same shelf mark into a single document.
    
    :param doc_group: List of documents to merge
    :type doc_group: List[Dict]
    :param shelf_mark: The unified shelf mark
    :type shelf_mark: str
    :return: Merged document
    :rtype: Dict
    """
    if not doc_group:
        return {}
    
    # Start with the first document as base
    merged_doc = doc_group[0].copy()
    
    # Set unified identifiers
    merged_doc['shelf_mark'] = shelf_mark
    merged_doc['doc_id'] = shelf_mark
    
    # Merge image metadata from all documents
    all_image_metadata = []
    all_images = []
    
    for doc in doc_group:
        # Collect image metadata
        if 'image_metadata' in doc and doc['image_metadata']:
            all_image_metadata.extend(doc['image_metadata'])
        
        # Collect image URLs
        if 'images' in doc and doc['images']:
            all_images.extend(doc['images'])
    
    # Remove duplicates from image lists while preserving order
    seen_images = set()
    unique_images = []
    for img in all_images:
        if img not in seen_images:
            seen_images.add(img)
            unique_images.append(img)
    
    merged_doc['images'] = unique_images
    merged_doc['image_metadata'] = all_image_metadata
    
    # Merge transcriptions from all documents
    all_transcriptions = []
    for doc in doc_group:
        if 'transcriptions' in doc and doc['transcriptions']:
            all_transcriptions.extend(doc['transcriptions'])
    merged_doc['transcriptions'] = all_transcriptions
    
    # Merge translations from all documents
    all_translations = []
    for doc in doc_group:
        if 'translations' in doc and doc['translations']:
            all_translations.extend(doc['translations'])
    merged_doc['translations'] = all_translations
    
    # Merge related people and places
    all_related_people = []
    all_related_places = []
    all_bibliography = []
    
    for doc in doc_group:
        if 'related_people' in doc and doc['related_people']:
            all_related_people.extend(doc['related_people'])
        if 'related_places' in doc and doc['related_places']:
            all_related_places.extend(doc['related_places'])
        if 'bibliography' in doc and doc['bibliography']:
            all_bibliography.extend(doc['bibliography'])
    
    merged_doc['related_people'] = all_related_people
    merged_doc['related_places'] = all_related_places
    merged_doc['bibliography'] = all_bibliography
    
    # Use the most complete description (longest non-empty one)
    best_description = ""
    for doc in doc_group:
        desc = doc.get('description', '')
        if desc and len(desc) > len(best_description):
            best_description = desc
    merged_doc['description'] = best_description
    
    # Use the most complete metadata (prefer documents with more metadata fields)
    best_metadata = {}
    max_metadata_fields = 0
    for doc in doc_group:
        metadata = doc.get('full_metadata_info', {})
        if len(metadata) > max_metadata_fields:
            max_metadata_fields = len(metadata)
            best_metadata = metadata
    merged_doc['full_metadata_info'] = best_metadata
    
    logger.debug(f"Merged document {shelf_mark}: {len(unique_images)} images, {len(all_transcriptions)} transcriptions")
    
    return merged_doc


def index_genizah_to_elasticsearch(file_path: str, index_name: str = "cairo_genizah_text_only_v1.0.0", document_origin: str = "princeton", document_type: str = "tanakh", bucket_base_url: str = "https://storage.googleapis.com/cairo-genizah-es-json/raw_images", embedding_mode: str = "text", use_cache=False):
    """
    Index documents from a JSON file to Elasticsearch.
    :param file_path: Path to the JSON file containing transcribed documents.
    :type file_path: str
    :param index_name: Name of the Elasticsearch index to use.
    :type index_name: str
    :param document_origin: Whether the document came from Princeton or Cambridge. Determines loading logic for different sources.
    :type document_origin: str
    :param document_type: Type of document in terms of scholary analysis (e.g. ketubah, letter, Mishnah, Talmud, Piyyut, etc). Used for filtering. Currently PGP supplies this automatically however
    Cambridge documents require supplying this manually.
    :type document_type: str
    :param bucket_base_url: Base URL for the image bucket.
    :type bucket_base_url: str
    :param embedding_mode: Embedding mode to use. Options: "text" (text-only embeddings, skips image loading), "image" (image-only embeddings, requires image loading), or "multimodal" (combines text and image embeddings, requires image loading).
    :type embedding_mode: str
    :param use_cache: Whether to use embedding cache.
    :type use_cache: bool
    :return: None
    :rtype: None

    Example::
        index_genizah_to_elasticsearch(
            file_path="/path/to/documents.json",
            index_name="genizah_index",
            document_origin="princeton",
            document_type="letter",
            embedding_mode="text"  # Use text-only embeddings
        )
    """
    # Validate embedding mode
    valid_modes = ["text", "image", "multimodal"]
    if embedding_mode not in valid_modes:
        raise ValueError(f"embedding_mode must be one of {valid_modes}, got '{embedding_mode}'")
    
    # Initialize the embeddings model based on mode
    logger.info(f"Initializing embeddings model in {embedding_mode} mode...")
    text_only = (embedding_mode == "text")
    image_only = (embedding_mode == "image")
    embeddings_model = NomicsEmbedding(text_only=text_only, image_only=image_only)

    # Configure Elasticsearch connection
    elastic_config = {
        'hosts': [{'host': os.environ["ELASTIC_SEARCH_HOST"], 'port': 443, 'scheme': 'https'}],
        'basic_auth': (os.environ["ELASTIC_USER"], os.environ["ELASTIC_PASSWORD"]),
    }

    # Initialize the Elasticsearch processor and image helper
    logger.info("Initializing Elasticsearch processor...")
    processor = ElasticsearchGenizahProcessor(embeddings_model, elasticsearch_config=elastic_config, index_name=index_name, use_cache=use_cache)
    image_helper = ImageURLHelper(bucket_base_url)
    transcribed_file_path = file_path

    # Load all documents from the JSON file
    logger.info(f"Loading documents from {transcribed_file_path}...")
    with open(transcribed_file_path, "r") as f:
        transcribed_docs = json.load(f)

    logger.info(f"Found {len(transcribed_docs)} documents to process")

    # Process documents in batches to avoid memory issues
    batch_size = 10
    all_doc_ids = list(transcribed_docs.keys())
    if document_origin == "cambridge":
        all_doc_ids = transcribed_docs["documents"]
        
        # Apply deduplication for Cambridge documents
        logger.info("Applying deduplication for Cambridge documents...")
        deduplicated_docs = deduplicate_cambridge_documents(all_doc_ids)
        all_doc_ids = deduplicated_docs
        logger.info(f"After deduplication: {len(all_doc_ids)} documents to process")
    for i in range(0, len(all_doc_ids), batch_size):
        batch_ids = all_doc_ids[i:i + batch_size]
        logger.info(
            f"Processing batch {i // batch_size + 1}/{(len(all_doc_ids) + batch_size - 1) // batch_size}: documents {i + 1}-{min(i + batch_size, len(all_doc_ids))}")

        batch_documents = []
        for doc_obj in tqdm(batch_ids):
            if  document_origin == "princeton":
                # Create GenizahDocument from the Princeton format
                doc = GenizahDocument.from_princeton_format(transcribed_docs[doc_obj])
                doc.doc_id = doc_obj

                # Process images - handles both Princeton URLs and Friedberger filenames
                doc.image_urls = image_helper.process_princeton_or_friedberger_images(doc.image_urls)
                doc.primary_image_index = image_helper.get_primary_image_index(doc.image_urls)
                
                # Set actual_image_url to first image URL for Rylands documents
                if doc.image_urls:
                    doc.actual_image_url = doc.image_urls[0]
                
                # Load images for the document if using image or multimodal embeddings
                if embedding_mode in ["image", "multimodal"]:
                    doc.load_images()

                batch_documents.append(doc)
            else:
                # For Cambridge documents, doc_obj is now a dictionary (after deduplication)
                doc = GenizahDocument.from_cambridge_format(doc_obj)
                
                # Set doc_id if missing
                if doc.doc_id is None and doc.shelf_mark is not None:
                    doc.doc_id = doc.shelf_mark
                else:
                    if doc.original_url is not None:
                        improvised_id = extract_shelf_mark(doc.original_url)
                        doc.doc_id = improvised_id
                if doc.shelf_mark is None:
                    # Extract shelf mark from TEI metadata idno field
                    shelf_mark = doc.full_metadata.get('{http://www.tei-c.org/ns/1.0}idno')
                    if shelf_mark:
                        doc.shelf_mark = shelf_mark
                        # Also set doc_id if it's missing or unknown
                        if doc.doc_id is None or doc.doc_id == "unknown-shelfmark":
                            doc.doc_id = shelf_mark
                    else:
                        logging.error(f"No shelf mark found in metadata for document {doc.doc_id}")
                        logging.error(f"Available metadata keys: {list(doc.full_metadata.keys())}")
                        logging.error(f"Document keys: {list(doc_obj.keys()) if isinstance(doc_obj, dict) else 'Not a dict'}")
                        # Skip this document - we cannot index without a shelf mark
                        continue
                # Apply shelf-mark based institutional mapping after shelf mark is finalized
                try:
                    doc._apply_shelfmark_mapping()
                except Exception:
                    # Mapping is best-effort; proceed even if mapping fails
                    pass
                
                # Process Cambridge images using image metadata
                if hasattr(doc, 'image_metadata') and doc.image_metadata:
                    doc.image_urls = image_helper.process_cambridge_images(doc.doc_id, doc.image_metadata)
                else:
                    # Fallback to existing image_urls if no metadata
                    doc.image_urls = doc.image_urls or []
                
                doc.primary_image_index = image_helper.get_primary_image_index(doc.image_urls)
                doc.document_category = document_type
                
                # Load images for the document if using image or multimodal embeddings
                if embedding_mode in ["image", "multimodal"]:
                    doc.load_images(cambridge_doc=True)
                
                batch_documents.append(doc)
        # Process and index the batch of documents
        if batch_documents:
            logger.info(f"Indexing batch of {len(batch_documents)} documents to Elasticsearch...")
            processor.process_documents(batch_documents)

    logger.info("Document indexing complete!")

def index_princeton_document_full():
    """
    Index the full Genizah dataset from Princeton to Elasticsearch.
    """
    index_genizah_to_elasticsearch("/Users/isaac1/Documents/GitHub/multimodal-document-analysis/tests/test_data/f_docs_updated.json", index_name="cairo_genizah_text_only_v1.0.6")

def index_cambridge_docs_tanakh():
    index_genizah_to_elasticsearch(
        file_path="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/etl/hebrew_tanak.json",
        index_name="cairo_genizah_text_only_v1.0.4", document_origin="cambridge", document_type="Tanakh")
    index_genizah_to_elasticsearch(file_path="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/etl/hebrew_tanakh_2.json", index_name="cairo_genizah_text_only_v1.0.6", document_origin="cambridge", document_type="Tanakh")

def index_cambridge_docs_piyyut():
    index_genizah_to_elasticsearch(file_path="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/etl/piyyut.json", index_name="cairo_genizah_text_only_v1.0.6", document_origin="cambridge", document_type="piyyut")

def index_cambridge_docs_talmud():
    index_genizah_to_elasticsearch(file_path="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/etl/talmud_output.json", index_name="cairo_genizah_text_only_v1.0.6", document_origin="cambridge", document_type="Talmud")
    index_genizah_to_elasticsearch(
        file_path="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/etl/talmud_output_2.json",
        index_name="cairo_genizah_text_only_v1.0.6", document_origin="cambridge", document_type="Talmud")

def test_indexing_rylands_documents(index_name="cairo_genizah_text_only_v1.0.9"):
    """
    index_genizah_to_elasticsearch(
        file_path="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/princeton/princeton_allupdated__image_docs_10_9.json",
        index_name=index_name,
        document_origin="princeton", document_type="assorted",

    )

    index_genizah_to_elasticsearch(
        file_path="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/friedberger/friedberger_vienna_documents.json",
        index_name=index_name,
        document_origin="princeton", document_type="assorted",
        bucket_base_url="https://storage.googleapis.com/cairo-genizah-es-json/images"

        )
    """
    index_genizah_to_elasticsearch(
        file_path="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/friedberger/friedberger_cambridge_documents.json",
        index_name=index_name, document_origin="princeton", document_type="assorted",
        bucket_base_url="https://storage.googleapis.com/cairo-genizah-es-json/images")

    index_genizah_to_elasticsearch(
        file_path="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/friedberger/friedberger_oxford_documents.json",
        index_name=index_name, document_origin="princeton", document_type="assorted",
        bucket_base_url="https://storage.googleapis.com/cairo-genizah-es-json/images")

    index_genizah_to_elasticsearch(
        file_path="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/friedberger/friedberger_manchester_documents.json",
        index_name=index_name, document_origin="princeton", document_type="assorted", bucket_base_url="https://storage.googleapis.com/cairo-genizah-es-json/images")

    index_genizah_to_elasticsearch(file_path="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/friedberger/friedberger_paris_documents.json",
                                   index_name=index_name,
                                   document_origin="princeton", document_type="assorted",
                                   bucket_base_url="https://storage.googleapis.com/cairo-genizah-es-json/images")

    index_genizah_to_elasticsearch(
        file_path="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/friedberger/friedberger_penn_documents.json",
        index_name=index_name,
        document_origin="princeton", document_type="assorted",
        bucket_base_url="https://storage.googleapis.com/cairo-genizah-es-json/images"

        )



def test_large_cambridge_idx():
    this_file = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.realpath(__file__))))
    file_path = os.path.join(this_file, "raw_data/cairo_genizah/cambridge_university/cambridge_full_08_scrape.json")
    file_path_2 = os.path.join(this_file, "/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/cambridge_university/cambridge_genizah_2025-10-09_v2.json")
    index_genizah_to_elasticsearch(
        file_path=file_path,
        index_name="cambridge_large_idx_test4", document_origin="cambridge", document_type="assorted", bucket_base_url="https://storage.googleapis.com/cairo-genizah-es-json/Downloads")
    index_genizah_to_elasticsearch(file_path=file_path_2,
                                   index_name="cambridge_large_idx_test3", document_type="assorted",
                                   bucket_base_url="https://storage.googleapis.com/cairo-genizah-es-json/Downloads")

def test_princeton_reindex():
    index_genizah_to_elasticsearch(
        file_path="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/princeton/princeton_allupdated__image_docs_10_9.json",
        index_name="princeton",
        document_origin="princeton", document_type="assorted",

    )

def full_index_text_only():
    index_genizah_to_elasticsearch(
        file_path="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/friedberger/friedberger_princeton_all_documents.json",
        index_name="index_name=cairo_genizah_text_only_v1.0.12",
        bucket_base_url="https://storage.googleapis.com/cairo-genizah-es-json/images"
    )

def _make_whole_full_combined_index():
    index_genizah_to_elasticsearch(
        file_path="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/merged_princeton_friedberger_all_documents_final.json",
        index_name="cairo_genizah_text_v_1.1.8",
        bucket_base_url="https://storage.googleapis.com/cairo-genizah-es-json/images",
        embedding_mode="text",
        use_cache=False

    )
if __name__ == "__main__":
    # index_cambridge_docs_tanakh()
    # index_cambridge_docs_piyyut()
    # index_princeton_document_full()
    #  index_cambridge_docs_talmud()
    # test_indexing_rylands_documents()
    # est_indexing_rylands_documents()
    # test_large_cambridge_idx()
    # test_indexing_rylands_documents()
    #test_indexing_rylands_documents()
    #full_index_text_only()
    _make_whole_full_combined_index()
    #test_indexing_rylands_documents()
