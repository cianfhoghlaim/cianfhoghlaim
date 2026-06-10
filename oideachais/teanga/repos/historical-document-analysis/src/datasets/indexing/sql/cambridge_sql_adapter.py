from typing import Dict, List, Optional
import re
from datetime import datetime


class CambridgeDataAdapter:
    """Adapt Cambridge scraped JSON to standardized format"""

    # TEI namespace prefix
    TEI_NS = "{http://www.tei-c.org/ns/1.0}"

    # GCS bucket info
    GCS_BUCKET = "cairo-genizah-es-json"
    GCS_IMAGE_PATH = "Downloads"

    def __init__(self):
        self.source_name = "Cambridge"

    def adapt_document(self, raw_doc: Dict) -> Dict:
        """
        Convert Cambridge scraped JSON to standardized format

        Args:
            raw_doc: Raw scraped document

        Returns:
            Standardized document dict ready for ingestion
        """

        metadata = raw_doc.get('full_metadata_info', {})

        # Extract shelf mark
        shelf_mark = self._extract_shelf_mark(metadata, raw_doc)

        # Extract doc_id for image construction
        doc_id = raw_doc.get('doc_id', '')

        # Build standardized document
        standardized = {
            # Core identification
            'shelf_mark': shelf_mark,
            'doc_id': doc_id,
            'source': 'Cambridge',
            'source_url': raw_doc.get('original_url'),

            # Content
            'description': self._extract_description(metadata),
            'transcription': self._extract_transcription(raw_doc),
            'translation': self._extract_translation(raw_doc),

            # Classification
            'document_type': self._infer_document_type(metadata),
            'language': self._extract_language(metadata, raw_doc),
            'script': self._extract_script(metadata),

            # Dating and provenance
            'dating_text': self._extract_dating(metadata, raw_doc),
            'place_written': self._extract_place(metadata),
            'material': self._extract_material(metadata),
            'provenance': self._extract_provenance(metadata),

            # Images
            'images': self._construct_images(doc_id, raw_doc.get('image_metadata', [])),

            # People and places
            'related_people': raw_doc.get('related_people', []),
            'related_places': raw_doc.get('related_places', []),

            # Bibliography
            'bibliography': raw_doc.get('bibliography', []),

            # Full metadata for reference
            'metadata': {
                'tei_metadata': metadata,
                'raw_doc': raw_doc,
                'scraped_at': datetime.now().isoformat()
            }
        }

        return standardized

    def _extract_shelf_mark(self, metadata: Dict, raw_doc: Dict) -> str:
        """Extract shelf mark from TEI metadata"""

        # Try TEI idno first
        shelf_mark = metadata.get(f"{self.TEI_NS}idno")

        # Fallback to shelf_mark field
        if not shelf_mark:
            shelf_mark = raw_doc.get('shelf_mark')

        # Last resort: extract from title
        if not shelf_mark:
            title = metadata.get('title', '')
            # Example: "Genizah Fragment (Mosseri III.240.3)"
            match = re.search(r'\((.*?)\)', title)
            if match:
                shelf_mark = match.group(1)

        if not shelf_mark:
            # Use doc_id as fallback
            shelf_mark = raw_doc.get('doc_id', 'UNKNOWN')

        return shelf_mark.strip()

    def _extract_description(self, metadata: Dict) -> Optional[str]:
        """Extract description from metadata"""

        # Check various possible description fields
        desc = metadata.get('description')

        if not desc or desc == "No description available":
            # Try TEI summary
            desc = metadata.get(f"{self.TEI_NS}summary")

        if not desc or desc == "No description available":
            # Try TEI msDesc
            desc = metadata.get(f"{self.TEI_NS}msDesc")

        if desc == "No description available":
            return None

        return desc

    def _extract_transcription(self, raw_doc: Dict) -> Optional[str]:
        """Extract transcription if available"""

        transcriptions = raw_doc.get('transcriptions', [])
        if transcriptions:
            # Combine multiple transcriptions
            return "\n\n---\n\n".join(transcriptions)

        return None

    def _extract_translation(self, raw_doc: Dict) -> Optional[str]:
        """Extract translation if available"""

        translations = raw_doc.get('translations', [])
        if translations:
            # Combine multiple translations
            return "\n\n---\n\n".join(translations)

        return None

    def _extract_language(self, metadata: Dict, raw_doc: Dict) -> List[str]:
        """Extract language information"""

        languages = []

        # Try top-level language field
        lang = raw_doc.get('language')
        if lang and lang != "Unknown":
            languages.append(lang)

        # Try TEI textLang
        tei_lang = metadata.get(f"{self.TEI_NS}textLang")
        if tei_lang:
            # Parse language string (might be like "Hebrew, Judaeo-Arabic")
            langs = [l.strip() for l in tei_lang.split(',')]
            languages.extend(langs)

        # Deduplicate
        languages = list(set(languages))

        return languages if languages else ['Unknown']

    def _extract_script(self, metadata: Dict) -> List[str]:
        """Extract script information"""

        # Try TEI scriptNote or textLang attributes
        script_note = metadata.get(f"{self.TEI_NS}scriptNote")
        if script_note:
            return [script_note]

        # Could also infer from language
        return []

    def _extract_dating(self, metadata: Dict, raw_doc: Dict) -> Optional[str]:
        """Extract dating information"""

        # Try top-level date field
        date = raw_doc.get('date')
        if date:
            return date

        # Try TEI origDate
        tei_date = metadata.get(f"{self.TEI_NS}origDate")
        if tei_date:
            return tei_date

        return None

    def _extract_place(self, metadata: Dict) -> Optional[str]:
        """Extract place of writing"""

        # Try TEI origPlace
        place = metadata.get(f"{self.TEI_NS}origPlace")
        if place:
            return place

        # Try provenance field (might mention Fustat)
        provenance = metadata.get(f"{self.TEI_NS}provenance", "")
        if "Fustat" in provenance:
            return "Fustat"

        return None

    def _extract_material(self, metadata: Dict) -> Optional[str]:
        """Extract material (paper, parchment, etc.)"""

        # Try TEI material
        material = metadata.get(f"{self.TEI_NS}material")
        if material:
            return material

        # Try TEI support
        support = metadata.get(f"{self.TEI_NS}support")
        if support:
            return support

        return None

    def _extract_provenance(self, metadata: Dict) -> Optional[str]:
        """Extract provenance information"""

        provenance = metadata.get(f"{self.TEI_NS}provenance")
        return provenance if provenance else None

    def _infer_document_type(self, metadata: Dict) -> Optional[str]:
        """Infer document type from metadata"""

        # Try TEI msItem/title
        title = metadata.get('title', '').lower()

        if 'letter' in title:
            return 'letter'
        elif 'legal' in title or 'contract' in title:
            return 'legal_document'
        elif 'liturgical' in title or 'prayer' in title:
            return 'liturgical'
        elif 'literary' in title or 'poem' in title:
            return 'literary'
        elif 'list' in title:
            return 'list'

        return None

    def _construct_images(self, doc_id: str, image_metadata: List[Dict]) -> List[Dict]:
        """
        Construct image URLs from doc_id and image metadata

        Images are stored in GCS as:
        gs://cairo-genizah-es-json/Downloads/MS-MOSSERI-III-00240-00003-000-00001.jpg
        """

        if not doc_id:
            return []

        images = []

        # Remove trailing "/X" if present (like "/2" in your example)
        base_doc_id = doc_id.split('/')[0]

        for idx, img_meta in enumerate(image_metadata, start=1):
            # Construct GCS URL
            image_filename = f"{base_doc_id}-000-{idx:05d}.jpg"
            gcs_url = f"gs://{self.GCS_BUCKET}/{self.GCS_IMAGE_PATH}/{image_filename}"

            # Get thumbnail from Cambridge IIIF if available
            thumbnail = img_meta.get('thumbnail_src', '')

            # Infer side from page index
            page_idx = img_meta.get('page_index', idx)
            if page_idx == 1:
                side = 'recto'
            elif page_idx == 2:
                side = 'verso'
            else:
                side = f'page_{page_idx}'

            images.append({
                'url': gcs_url,
                'thumbnail': thumbnail,
                'order': idx,
                'side': side,
                'type': 'color',
                'format': 'jpg',
                'iiif_manifest': self._construct_iiif_url(base_doc_id, idx),
                'metadata': img_meta
            })

        return images

    def _construct_iiif_url(self, doc_id: str, image_num: int) -> str:
        """Construct IIIF manifest URL for Cambridge images"""

        image_id = f"{doc_id}-000-{image_num:05d}"
        return f"https://images.lib.cam.ac.uk/iiif/{image_id}.jp2/info.json"

    def adapt_batch(self, raw_documents: List[Dict]) -> List[Dict]:
        """Adapt a batch of documents"""

        adapted = []
        for doc in raw_documents:
            try:
                adapted_doc = self.adapt_document(doc)
                adapted.append(adapted_doc)
            except Exception as e:
                print(f"Error adapting document: {e}")
                # Include raw doc for debugging
                print(f"  Shelf mark: {doc.get('doc_id', 'UNKNOWN')}")

        return adapted