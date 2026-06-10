# File name: genizah_document.py
# Date 8/22/25
# Author: Isaac Godfried. Coded originally by Claude Sonnet 4.
import logging
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union, ClassVar
import numpy as np
from pydantic import BaseModel, Field, validator
from enum import Enum

logger = logging.getLogger(__name__)
def convert_cambridge_lang_format(the_language):
    """Convert the language format used in Cambridge to the format used in Princeton"""
    if the_language == "heb":
        return "Hebrew"
    elif the_language == "jrb":
        return "Judeo-Arabic"
    elif the_language == "arb":
        return "Arabic"
    elif the_language == "ara":
        return "Aramaic"
    else:
        return "Other"

class ContentQuality(str, Enum):
    """Enumeration for content quality levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class SourceCollection(str, Enum):
    """Enumeration for source collections."""
    CAMBRIDGE = "cambridge"
    PRINCETON = "princeton"
    OTHER = "other"


class DateCertainty(str, Enum):
    """Enumeration for date certainty levels."""
    HIGH = "high"
    PROBABLE = "probable"
    UNCERTAIN = "uncertain"


class TranscriptionSection(BaseModel):
    """Model for transcription sections.

    Example:
        trans = TranscriptionSection(
        ...     name="Editor: John Doe",
        ...     lines={"1": "First line", "2": "Second line"}
        ... )
    """
    name: Optional[str] = None
    lines: Union[Dict[str, str], List[str], str] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {"name": self.name, "lines": self.lines}


class RelatedEntity(BaseModel):
    """Model for related people or places.

    Example:
        person = RelatedEntity(
        ...     name="Solomon Schechter",
        ...     role="editor",
        ...     url="https://example.com/person/123"
        ... )
    """
    name: str
    role: Optional[str] = None
    url: Optional[str] = None
    uncertain: bool = False
    key: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return self.dict()


class BibliographyEntry(BaseModel):
    """Model for bibliography entries.

    Example:
        bib = BibliographyEntry(
        ...     citation="Author, Title (Year)",
        ...     location="pp. 123-145",
        ...     relations=["Edition", "Translation"]
        ... )
    """
    citation: str
    location: Optional[str] = None
    relations: List[str] = Field(default_factory=list)
    url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return self.dict()


class NamedEntities(BaseModel):
    """Model for extracted named entities."""
    persons: List[str] = Field(default_factory=list)
    places: List[str] = Field(default_factory=list)
    organizations: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)


class PhysicalInfo(BaseModel):
    """Model for physical characteristics."""
    material: Optional[str] = None
    height: Optional[float] = None
    width: Optional[float] = None
    condition: Optional[str] = None
    extent: Optional[str] = None


class LanguageInfo(BaseModel):
    """Model for language information."""
    main_language: Optional[str] = None
    other_languages: List[str] = Field(default_factory=list)
    script_type: Optional[str] = None


class TemporalInfo(BaseModel):
    """Model for temporal information."""
    date_start: Optional[str] = None
    date_end: Optional[str] = None
    date_display: Optional[str] = None
    century: Optional[str] = None
    date_certainty: DateCertainty = DateCertainty.UNCERTAIN


class InstitutionalInfo(BaseModel):
    """Model for institutional information."""
    institution: Optional[str] = None
    repository: Optional[str] = None
    collection_name: Optional[str] = None
    source_collection: SourceCollection = SourceCollection.OTHER


class GenizahDocument(BaseModel):
    """Pydantic model for Cairo Genizah documents with Elasticsearch integration.

    This model provides data validation, serialization, and methods for converting
    to Elasticsearch-compatible documents with standardized fields.

    Example:
        doc = GenizahDocument(
        ...     image_urls=["https://example.com/image.jpg"],
        ...     description="Sample Talmud fragment",
        ...     transcriptions=[TranscriptionSection(name="Editor: Test", lines={"1": "Line 1"})],
        ...     translations=["Sample translation"]
        ... )
        es_doc = doc.to_elasticsearch_document(embedding=np.random.randn(768))
        completeness = doc.calculate_completeness_score()
    """

    # Core fields
    image_urls: List[str] = Field(default_factory=list, description="URLs of document images")
    description: str = Field(description="Description of the document")
    transcriptions: List[TranscriptionSection] = Field(default_factory=list, description="Document transcriptions")
    translations: List[str] = Field(default_factory=list, description="Document translations")
    
    # Multi-image support
    primary_image_index: Optional[int] = Field(default=None, description="Index of primary image in image_urls list")

    # Optional metadata
    date: Optional[Dict[str, str]] = Field(default=None, description="Date information")
    image_details: Optional[Dict[str, str]] = Field(default=None, description="Image details")
    language: str = Field(default="Unknown", description="Primary language")
    doc_id: Optional[str] = Field(default=None, description="Document identifier")
    original_url: Optional[str] = Field(default=None, description="Original source URL")
    miscellaneous_info: Optional[str] = Field(default=None, description="Additional information")
    document_category: Optional[str] = Field(default=None, description="Document type/category")
    shelf_mark: Optional[str] = Field(default=None, description="Library shelf mark")
    image_metadata: Optional[List[Dict]] = Field(default=None, description="Image metadata particularly for Cambridge Collection")
    
    # Collection identifiers
    collection: Optional[str] = Field(default=None, description="Primary collection (e.g., Manchester, Paris)")
    sub_collection: Optional[str] = Field(default=None, description="Sub-collection identifier (e.g., A series, AF, H series)")
    institution: Optional[str] = Field(default=None, description="Owning institution derived from shelf mark where possible")

    # Relationships
    related_people: List[RelatedEntity] = Field(default_factory=list, description="Related people")
    related_places: List[RelatedEntity] = Field(default_factory=list, description="Related places")
    bibliography: List[BibliographyEntry] = Field(default_factory=list, description="Bibliography")

    # Enhanced metadata
    full_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata (e.g., TEI)")
    joins_data: Optional[Dict[str, Any]] = Field(default=None, description="Joins data for fragment reconstruction")

    # Image processing
    image: Optional[Any] = Field(default=None, exclude=True, description="Loaded image data")
    actual_image_url: Optional[str] = Field(default=None, description="Actual URL used for embedding")
    
    # Attribution
    attribution_url: Optional[str] = Field(default=None, description="URL to the original collection/database where the document is hosted")

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        extra = "forbid"
        validate_assignment = True

    # ================= Shelf-mark derived institutional mapping =================
    # These mappings provide canonical institution/collection/sub-collection from common
    # Genizah shelf-mark families. Parsing aims to be robust but conservative; fall back
    # to existing heuristics where a mapping cannot be confidently determined.

    GENIZAH_SHELFMARK_MAPPING: ClassVar[Dict[str, Dict[str, Optional[str]]]] = {
        # Cambridge University Library (Taylor-Schechter)
        "T-S": {"institution": "Cambridge University Library", "collection": "Taylor-Schechter", "subcollection": None},
        "T-S AS": {"institution": "Cambridge University Library", "collection": "Taylor-Schechter", "subcollection": "Additional Series"},
        "T-S NS": {"institution": "Cambridge University Library", "collection": "Taylor-Schechter", "subcollection": "New Series"},
        "T-S Ar": {"institution": "Cambridge University Library", "collection": "Taylor-Schechter", "subcollection": "Arabic"},
        "T-S K": {"institution": "Cambridge University Library", "collection": "Taylor-Schechter", "subcollection": "Miscellaneous"},
        "CUL Add": {"institution": "Cambridge University Library", "collection": "Additional Manuscripts", "subcollection": None},
        "ULC Add": {"institution": "Cambridge University Library", "collection": "Additional Manuscripts", "subcollection": None},
        "CUL Or": {"institution": "Cambridge University Library", "collection": "Oriental Manuscripts", "subcollection": None},
        "Mosseri": {"institution": "Cambridge University Library", "collection": "Mosseri", "subcollection": None},
        "L-G": {"institution": "Cambridge University Library / Bodleian Library Oxford", "collection": "Lewis-Gibson", "subcollection": None},

        # JTS / ENA
        "ENA": {"institution": "Jewish Theological Seminary", "collection": "Elkan Nathan Adler", "subcollection": "Main series"},
        "ENA NS": {"institution": "Jewish Theological Seminary", "collection": "Elkan Nathan Adler", "subcollection": "New Series"},
        "ENA II": {"institution": "Jewish Theological Seminary", "collection": "Elkan Nathan Adler", "subcollection": "Second Adler acquisition"},
        "JTS MS": {"institution": "Jewish Theological Seminary", "collection": "General Manuscripts", "subcollection": None},
        "JTS MS Rabbinica": {"institution": "Jewish Theological Seminary", "collection": "General Manuscripts", "subcollection": "Rabbinic literature from ENA"},
        "JTS MS Lutzki": {"institution": "Jewish Theological Seminary", "collection": "General Manuscripts", "subcollection": "Biblical texts from ENA"},
        "JTS Scroll": {"institution": "Jewish Theological Seminary", "collection": "General Manuscripts", "subcollection": "Scrolls from ENA"},
        "KE": {"institution": "Jewish Theological Seminary", "collection": "Kahle Acquisition", "subcollection": None},

        # Manchester / Rylands (Gaster)
        "Gaster A": {"institution": "John Rylands Library, University of Manchester", "collection": "Gaster", "subcollection": "Series A"},
        "Gaster B": {"institution": "John Rylands Library, University of Manchester", "collection": "Gaster", "subcollection": "Series B"},
        "Gaster P": {"institution": "John Rylands Library, University of Manchester", "collection": "Gaster", "subcollection": "Series P"},
        "Gaster L": {"institution": "John Rylands Library, University of Manchester", "collection": "Gaster", "subcollection": "Series L"},
        "Gaster C": {"institution": "John Rylands Library, University of Manchester", "collection": "Gaster", "subcollection": "Series C"},
        "Gaster Ar": {"institution": "John Rylands Library, University of Manchester", "collection": "Gaster", "subcollection": "Arabic Series"},
        "Gaster Hebrew MS": {"institution": "John Rylands Library, University of Manchester", "collection": "Gaster", "subcollection": "Hebrew Manuscripts"},
        "Gaster Hebrew MS Add": {"institution": "John Rylands Library, University of Manchester", "collection": "Gaster", "subcollection": "Hebrew Manuscripts Additional"},
        "Rylands Genizah": {"institution": "John Rylands Library, University of Manchester", "collection": "Pre-Gaster Acquisitions", "subcollection": None},
        "JRL": {"institution": "John Rylands Library, University of Manchester", "collection": "General designation", "subcollection": None},

        # Bodleian
        "MS. Heb.": {"institution": "Bodleian Library, Oxford", "collection": "Hebrew Manuscripts", "subcollection": None},
        "Bodl.": {"institution": "Bodleian Library, Oxford", "collection": "Bodleian Manuscripts", "subcollection": None},

        # Penn
        "Halper": {"institution": "University of Pennsylvania, Katz Center", "collection": "Dropsie College", "subcollection": None},
        "CAJS": {"institution": "University of Pennsylvania, Center for Advanced Judaic Studies", "collection": "CAJS", "subcollection": None},
        "Penn CAJS": {"institution": "University of Pennsylvania, Center for Advanced Judaic Studies", "collection": "CAJS", "subcollection": None},

        # AIU Paris
        "AIU": {"institution": "Alliance Israélite Universelle, Paris", "collection": "Cairo Genizah", "subcollection": None},

        # Budapest
        "Kaufmann": {"institution": "Hungarian Academy of Sciences, Budapest", "collection": "David Kaufmann", "subcollection": None},
        "MS Kaufmann A": {"institution": "Hungarian Academy of Sciences, Budapest", "collection": "David Kaufmann", "subcollection": "Codices"},
        "DKG": {"institution": "Hungarian Academy of Sciences, Budapest", "collection": "David Kaufmann", "subcollection": None},

        # British Library
        "BL Or": {"institution": "British Library, London", "collection": "Oriental Manuscripts", "subcollection": None},
        "BL Add": {"institution": "British Library, London", "collection": "Additional Manuscripts", "subcollection": None},

        # Russia / St. Petersburg
        "RNL": {"institution": "Russian National Library, St. Petersburg", "collection": "Genizah", "subcollection": None},
        "Yevr.": {"institution": "Russian National Library, St. Petersburg", "collection": "Evreiskii (Jewish)", "subcollection": None},
        
        # Dropsie alias
        "Dropsie": {"institution": "University of Pennsylvania (formerly Dropsie College)", "collection": "Dropsie", "subcollection": None},
    }

    @staticmethod
    def _normalize_shelf_mark_for_match(shelf_mark: str) -> str:
        """Normalize a shelf mark string for prefix matching.

        :param shelf_mark: Raw shelf mark (e.g., "MS-TS-AS-00001-00001", "Manchester: A 639")
        :type shelf_mark: str
        :return: A simplified representation suitable for startswith checks
        :rtype: str
        """
        if not shelf_mark:
            return ""
        sm = shelf_mark.strip()
        # Common Cambridge TEI encodings
        sm = sm.replace("MS-TS-AS", "T-S AS")
        sm = sm.replace("MS-TS-NS", "T-S NS")
        sm = sm.replace("MS-TS-K", "T-S K")
        sm = sm.replace("MS-TS-AR", "T-S Ar")
        sm = sm.replace("MS-TS-", "T-S ")
        sm = sm.replace("MS-MOSSERI", "Mosseri")
        sm = sm.replace("MS-L-G", "L-G")
        sm = sm.replace("MS-OR-", "CUL Or ")
        sm = sm.replace("MS-ADD-", "CUL Add ")
        # Manchester style
        if sm.startswith("Manchester:") or sm.startswith("Manchester "):
            # Example: "Manchester: A 639" -> map to Gaster A
            parts = sm.split(":", 1)
            tail = parts[1].strip() if len(parts) > 1 else sm
            if tail.startswith("A "):
                return "Gaster A"
            if tail.startswith("B "):
                return "Gaster B"
            if tail.startswith("P "):
                return "Gaster P"
            if tail.startswith("L "):
                return "Gaster L"
            if tail.startswith("C "):
                return "Gaster C"
        return sm

    def _apply_shelfmark_mapping(self) -> None:
        """Populate institution, collection, and sub-collection from shelf mark when possible.

        This method is idempotent and safe to call multiple times. It will only set fields
        that are currently unset to avoid clobbering explicit assignments.

        Example:
            doc = GenizahDocument(image_urls=[], description="", shelf_mark="MS-TS-AS-00033-00006")
            doc._apply_shelfmark_mapping()
            assert doc.institution == "Cambridge University Library"
            assert doc.collection == "Taylor-Schechter"
            assert doc.sub_collection == "Additional Series"
        """
        if not self.shelf_mark:
            return
        
        shelf_mark = self.shelf_mark.strip()
        
        # Special handling for Paris/AIU shelf marks with Roman numeral sub-collections
        # Examples: "Paris X.10", "Paris VI.120", "Paris AIU: I.A.10", etc.
        if 'Paris' in shelf_mark or 'AIU' in shelf_mark:
            # Set base institution and collection if not already set
            if self.institution is None:
                self.institution = "Alliance Israélite Universelle, Paris"
            if self.collection is None:
                self.collection = "Cairo Genizah"
            
            # Extract Roman numeral sub-collection (I, II, III, IV, V, VI, X, XI, etc.)
            if self.sub_collection is None:
                # Remove "Paris" and "AIU" to get the series identifier
                rest = shelf_mark.replace("Paris", "").replace("AIU", "").strip(' ,:')
                
                # Try to extract Roman numeral at the start (e.g., "X.10", "VI.120", "IV.A.206")
                roman_match = re.match(r'^([IVX]+)', rest)
                if roman_match:
                    roman_numeral = roman_match.group(1)
                    self.sub_collection = f"Series {roman_numeral}"
        
        candidate = self._normalize_shelf_mark_for_match(shelf_mark)
        # Prefer the most specific keys first by sorting keys by length desc
        best_key = None
        for key in sorted(self.GENIZAH_SHELFMARK_MAPPING.keys(), key=len, reverse=True):
            if candidate.startswith(key):
                best_key = key
                break
        if not best_key:
            return
        mapped = self.GENIZAH_SHELFMARK_MAPPING[best_key]
        if self.institution is None and mapped.get("institution"):
            self.institution = mapped["institution"]
        if self.collection is None and mapped.get("collection"):
            self.collection = mapped["collection"]
        if self.sub_collection is None and mapped.get("subcollection"):
            self.sub_collection = mapped["subcollection"]

    @validator('description', pre=True)
    def clean_description(cls, v: str) -> str:
        """Remove 'Description' prefix from description field.

        :param v: Raw description value
        :type v: str
        :return: Cleaned description
        :rtype: str
        """
        if isinstance(v, str):
            return v.replace("Description", "").strip()
        return v

    @validator('transcriptions', pre=True)
    def validate_transcriptions(cls, v: List) -> List[TranscriptionSection]:
        """Convert transcription data to TranscriptionSection objects.

        :param v: Raw transcription data
        :type v: List
        :return: List of TranscriptionSection objects
        :rtype: List[TranscriptionSection]
        """
        if not v:
            return []

        result = []
        for item in v:
            if isinstance(item, TranscriptionSection):
                result.append(item)
            elif isinstance(item, dict):
                result.append(TranscriptionSection(**item))
            elif hasattr(item, 'name') and hasattr(item, 'lines'):
                result.append(TranscriptionSection(name=item.name, lines=item.lines))
            else:
                logger.warning(f"Could not convert transcription item: {item}")

        return result

    @validator('related_people', 'related_places', pre=True)
    def validate_related_entities(cls, v: List) -> List[RelatedEntity]:
        """Convert related entity data to RelatedEntity objects.

        :param v: Raw entity data
        :type v: List
        :return: List of RelatedEntity objects
        :rtype: List[RelatedEntity]
        """
        if not v:
            return []

        result = []
        for item in v:
            if isinstance(item, RelatedEntity):
                result.append(item)
            elif isinstance(item, dict):
                result.append(RelatedEntity(**item))
            elif hasattr(item, 'name'):
                result.append(RelatedEntity(
                    name=item.name,
                    role=getattr(item, 'role', None),
                    url=getattr(item, 'url', None)
                ))
            else:
                logger.warning(f"Could not convert related entity: {item}")

        return result

    @validator('bibliography', pre=True)
    def validate_bibliography(cls, v: List) -> List[BibliographyEntry]:
        """Convert bibliography data to BibliographyEntry objects.

        :param v: Raw bibliography data
        :type v: List
        :return: List of BibliographyEntry objects
        :rtype: List[BibliographyEntry]
        """
        if not v:
            return []

        result = []
        for item in v:
            if isinstance(item, BibliographyEntry):
                result.append(item)
            elif isinstance(item, dict):
                result.append(BibliographyEntry(**item))
            elif hasattr(item, 'citation'):
                result.append(BibliographyEntry(
                    citation=item.citation,
                    location=getattr(item, 'location', None),
                    relations=getattr(item, 'relations', []),
                    url=getattr(item, 'url', None)
                ))
            else:
                logger.warning(f"Could not convert bibliography entry: {item}")

        return result

    def load_images(self, cache_path: str = "./image_cache", cambridge_doc=False) -> None:
        """Load images for the document using existing image caching functionality.

        :param cache_path: Path to cache directory for images
        :type cache_path: str
        :cambridge_doc: Whether this document is from Cambridge versus Princeton or some other place. Cambridge images
        were archive to gcp and have different URL mechanism. Therefore for all Cambridge documents this should be set to True.
        :type cambridge_doc: bool
        :return: None

        Example:
             doc = GenizahDocument(image_urls=["https://example.com/img.jpg"], description="Test")
             doc.load_images(cache_path="./my_cache")
        """
        # Import here to avoid circular dependencies
        from src.etl.scrapers.princeton_genizah_scraper import cache_download_genizah_image, get_largest_image_url

        result = cache_download_genizah_image(
            caching_path=cache_path,
            urls=self.image_urls,
            doc_id=self.doc_id,
            cambridge_doc=cambridge_doc
        )

        if isinstance(result, tuple) and len(result) == 2:
            self.image, self.actual_image_url = result
        else:
            self.image = result
            if self.image_urls:
                if self.doc_id and "/" in self.doc_id:
                    self.actual_image_url = self.image_urls[0]
                else:
                    self.actual_image_url = get_largest_image_url(self.image_urls[0])


    def get_embedding_cache_key(self) -> str:
        """Generate unique cache key for embedding based on document content.

        :return: SHA256 hash of document content
        :rtype: str

        Example:
            doc = GenizahDocument(image_urls=[], description="Test document")
            cache_key = doc.get_embedding_cache_key()
            len(cache_key)
            64
        """
        content_parts = []

        # Core identifiers
        if self.doc_id:
            content_parts.append(str(self.doc_id))
        if self.shelf_mark:
            content_parts.append(str(self.shelf_mark))

        # Content
        if self.description:
            content_parts.append(str(self.description))

        # Transcriptions
        for trans in self.transcriptions:
            if isinstance(trans.lines, dict):
                content_parts.extend(str(line) for line in trans.lines.values() if line)
            else:
                content_parts.append(str(trans.lines))

        # Image URL for visual component
        if self.actual_image_url:
            content_parts.append(self.actual_image_url)
        elif self.image_urls:
            content_parts.append(self.image_urls[0])

        content_string = '|'.join(content_parts)
        return hashlib.sha256(content_string.encode()).hexdigest()

    def get_source_format(self) -> SourceCollection:
        """Detect whether this is a Cambridge or Princeton format document.

        :return: Source collection type
        :rtype: SourceCollection

        Example:
             doc = GenizahDocument(image_urls=[], description="Test")
             doc.full_metadata = {"{http://www.tei-c.org/ns/1.0}title": "Test"}
             doc.get_source_format()
            <SourceCollection.CAMBRIDGE: 'cambridge'>
        """
        # Check for Cambridge TEI indicators
        if self.full_metadata and any('{http://www.tei-c.org/ns/1.0}' in str(k)
                                      for k in self.full_metadata.keys()):
            return SourceCollection.CAMBRIDGE

        # Check for Princeton indicators
        if self.related_people or self.related_places or self.bibliography:
            return SourceCollection.PRINCETON

        # Check doc_id patterns
        if self.doc_id and "/" in self.doc_id:
            return SourceCollection.CAMBRIDGE

        return SourceCollection.CAMBRIDGE

    def extract_temporal_info(self) -> TemporalInfo:
        """Extract and standardize temporal information from document.

        :return: Standardized temporal information
        :rtype: TemporalInfo

        Example:
             doc = GenizahDocument(image_urls=[], description="Test")
             doc.date = {"standard_date": "1000-01-01"}
             temporal = doc.extract_temporal_info()
             temporal.date_start
            '1000-01-01'
        """
        temporal_info = TemporalInfo()

        # Extract from date field
        if self.date:
            for date_field in ['datetime_attr', 'standard_date', 'hebrew_date']:
                if date_field in self.date and self.date[date_field]:
                    date_start, date_end = self._parse_date_string(date_string=self.date[date_field])
                    if date_start or date_end:
                        temporal_info.date_start = date_start
                        temporal_info.date_end = date_end
                        temporal_info.date_display = self.date[date_field]
                        temporal_info.date_certainty = DateCertainty.PROBABLE
                        break

        # Extract from TEI metadata for Cambridge documents
        if self.full_metadata:
            for key, value in self.full_metadata.items():
                if 'origdate' in key.lower() or 'date' in key.lower():
                    date_start, date_end = self._parse_date_string(date_string=str(value))
                    if date_start or date_end:
                        temporal_info.date_start = date_start
                        temporal_info.date_end = date_end
                        temporal_info.date_certainty = DateCertainty.HIGH
                        break

        # Infer century
        if temporal_info.date_start:
            try:
                year = int(temporal_info.date_start[:4])
                century = ((year - 1) // 100) + 1
                temporal_info.century = f"{century}th century"
            except (ValueError, TypeError):
                pass

        return temporal_info

    def extract_language_info(self) -> LanguageInfo:
        """Extract and standardize language information from document.

        :return: Standardized language information
        :rtype: LanguageInfo

        Example:
             doc = GenizahDocument(image_urls=[], description="Test")
             doc.language = "Hebrew"
             lang_info = doc.extract_language_info()
             lang_info.main_language
            'hebrew'
        """
        language_info = LanguageInfo()

        # Use existing language field
        if self.language and self.language != "Unknown":
            language_info.main_language = self.language.lower()

        # Extract from TEI metadata for Cambridge documents
        if self.full_metadata:
            main_lang, other_langs = self._extract_tei_languages(metadata=self.full_metadata)
            if main_lang:
                language_info.main_language = main_lang
            if other_langs:
                language_info.other_languages = other_langs

        # Infer script type
        if language_info.main_language:
            script_mapping = {
                'heb': 'hebrew',
                'arc': 'aramaic',
                'jrb': 'judeo-arabic',
                'ara': 'arabic',
                'per': 'persian'
            }
            language_info.script_type = script_mapping.get(
                language_info.main_language, 'other'
            )

        return language_info

    def extract_physical_info(self) -> PhysicalInfo:
        """Extract physical characteristics from metadata.

        :return: Physical characteristics information
        :rtype: PhysicalInfo

        Example:
             doc = GenizahDocument(image_urls=[], description="Test")
             doc.full_metadata = {"{http://www.tei-c.org/ns/1.0}support": "Paper"}
             physical = doc.extract_physical_info()
             physical.material
            'Paper'
        """
        physical_info = PhysicalInfo()

        if self.full_metadata:
            # Extract from TEI fields
            for key, value in self.full_metadata.items():
                if not value:
                    continue

                key_lower = key.lower()
                if 'support' in key_lower:
                    physical_info.material = str(value)
                elif 'condition' in key_lower:
                    physical_info.condition = str(value)
                elif 'extent' in key_lower:
                    physical_info.extent = str(value)
                elif 'height' in key_lower:
                    try:
                        physical_info.height = float(re.sub(r'[^\d.]', '', str(value)))
                    except (ValueError, TypeError):
                        pass
                elif 'width' in key_lower:
                    try:
                        physical_info.width = float(re.sub(r'[^\d.]', '', str(value)))
                    except (ValueError, TypeError):
                        pass

        return physical_info

    def extract_physical_info_from_other_info(self) -> PhysicalInfo:
        """Extract physical characteristics from other_info field (Princeton-type documents).
        
        :return: Physical characteristics information
        :rtype: PhysicalInfo
        
        Example:
             doc = GenizahDocument(image_urls=[], description="Test")
             doc.miscellaneous_info = '{"material": "Paper", "dimensions": "133.00 × 107.00 mm"}'
             physical = doc.extract_physical_info_from_other_info()
             physical.material
            'Paper'
        """
        physical_info = PhysicalInfo()
        
        # Try to parse other_info from miscellaneous_info if it's a JSON string
        other_info = {}
        if self.miscellaneous_info:
            try:
                import json
                other_info = json.loads(self.miscellaneous_info)
            except (json.JSONDecodeError, TypeError):
                # If it's not JSON, treat it as a string
                pass
        
        # Extract material
        if other_info.get('material'):
            physical_info.material = str(other_info['material'])
        
        # Extract dimensions
        if other_info.get('dimensions'):
            dimensions = other_info['dimensions']
            # Parse dimensions (e.g., "133.00 × 107.00 mm")
            if '×' in dimensions:
                parts = dimensions.split('×')
                if len(parts) == 2:
                    try:
                        height = float(parts[0].strip().split()[0])
                        width = float(parts[1].strip().split()[0])
                        physical_info.height = height
                        physical_info.width = width
                    except (ValueError, IndexError):
                        pass
        
        # Extract other fields
        if other_info.get('rows'):
            physical_info.extent = f"{other_info['rows']} lines"
        
        return physical_info

    def extract_institutional_info(self) -> InstitutionalInfo:
        """Extract institutional and repository information.

        :return: Institutional information
        :rtype: InstitutionalInfo

        Example:
             doc = GenizahDocument(image_urls=[], description="Test")
             doc.original_url = "https://cudl.lib.cam.ac.uk/view/MS-TS-F-00001"
             inst_info = doc.extract_institutional_info()
             inst_info.institution
            'Cambridge University'
        """
        institutional_info = InstitutionalInfo(source_collection=self.get_source_format())

        # First, prefer shelf-mark mapping if present - this sets self.institution, self.collection, self.sub_collection
        self._apply_shelfmark_mapping()
        if self.institution:
            institutional_info.institution = self.institution
        # Note: self.collection and self.sub_collection are set by _apply_shelfmark_mapping() 
        # and will be written directly to ES document, not via collection_name

        # Extract from TEI metadata
        if self.full_metadata:
            for key, value in self.full_metadata.items():
                if not value:
                    continue

                key_lower = key.lower()
                if 'institution' in key_lower:
                    institutional_info.institution = institutional_info.institution or str(value)
                elif 'repository' in key_lower:
                    institutional_info.repository = institutional_info.repository or str(value)
                # Note: collection/sub_collection come from shelf mark mapping, not TEI metadata

        # Infer from URLs
        if self.original_url:
            url_lower = self.original_url.lower()
            if 'cambridge' in url_lower:
                institutional_info.institution = institutional_info.institution or 'Cambridge University'
                institutional_info.repository = institutional_info.repository or 'Cambridge University Library'
            elif 'princeton' in url_lower:
                institutional_info.institution = institutional_info.institution or 'Princeton University'
            elif 'upenn' in url_lower or 'penn' in url_lower:
                institutional_info.institution = institutional_info.institution or 'University of Pennsylvania'
        
        # Infer institution/repository from shelf mark ONLY if shelf mark mapping didn't already set them
        # collection and sub_collection come from shelf mark mapping only, not fallback logic
        if self.shelf_mark and not self.institution:
            shelf_mark = self.shelf_mark.strip()
            
            # Handle Manchester/Rylands documents (only as fallback if not mapped)
            if 'Manchester' in shelf_mark:
                institutional_info.institution = 'Rylands'
                institutional_info.repository = 'John Rylands Library'
            
            # Handle Paris documents (various formats: "Paris AIU:", "Paris, AIU:", etc.)
            # Only as fallback if not mapped
            elif 'Paris' in shelf_mark or 'AIU' in shelf_mark:
                institutional_info.institution = 'Paris'
                institutional_info.repository = 'Alliance Israélite Universelle'
            
            # Handle other potential institutions in shelf marks (fallbacks if mapping not set)
            elif 'Cambridge' in shelf_mark:
                institutional_info.institution = 'Cambridge University'
                institutional_info.repository = 'Cambridge University Library'
            elif 'Bodleian' in shelf_mark or 'Oxford' in shelf_mark:
                institutional_info.institution = 'Oxford University'
                institutional_info.repository = 'Bodleian Library'
            elif 'JTS' in shelf_mark or 'Jewish Theological Seminary' in shelf_mark:
                institutional_info.institution = 'Jewish Theological Seminary'
                institutional_info.repository = 'JTS Library'

        return institutional_info

    def extract_named_entities(self) -> NamedEntities:
        """Extract named entities from document content and relationships.

        :return: Named entities found in the document
        :rtype: NamedEntities

        Example:
             doc = GenizahDocument(image_urls=[], description="Test")
             doc.related_people = [RelatedEntity(name="Solomon Schechter", role="editor")]
             entities = doc.extract_named_entities()
             entities.persons
            ['Solomon Schechter']
        """
        entities = NamedEntities()

        # From related people and places
        for person in self.related_people:
            if person.name:
                entities.persons.append(person.name)

        for place in self.related_places:
            if place.name:
                entities.places.append(place.name)

        # Extract from TEI metadata (editors, donors, etc.)
        if self.full_metadata:
            for key, value in self.full_metadata.items():
                if 'editor' in key.lower() or 'author' in key.lower():
                    if value and isinstance(value, str):
                        # Clean up names like "Schechter, S. (Solomon), 1847-1915"
                        clean_name = re.sub(r'\([^)]*\)', '', value)
                        clean_name = re.sub(r'\d{4}-\d{4}', '', clean_name)
                        clean_name = clean_name.strip(' ,')
                        if clean_name:
                            entities.persons.append(clean_name)

        # Remove duplicates while preserving order
        entities.persons = list(dict.fromkeys(entities.persons))
        entities.places = list(dict.fromkeys(entities.places))
        entities.organizations = list(dict.fromkeys(entities.organizations))
        entities.dates = list(dict.fromkeys(entities.dates))

        return entities

    def calculate_completeness_score(self) -> float:
        """Calculate a completeness score for the document (0.0 to 1.0).

        :return: Completeness score between 0.0 and 1.0
        :rtype: float

        Example:
             doc = GenizahDocument(
            ...     image_urls=["test.jpg"],
            ...     description="Complete document with transcription",
            ...     transcriptions=[TranscriptionSection(lines={"1": "text"})]
            ... )
             score = doc.calculate_completeness_score()
             0.0 <= score <= 1.0
            True
        """
        score = 0.0
        max_score = 10.0

        # Core metadata (30% weight)
        if self.description and len(self.description.strip()) > 10:
            score += 1.0
        if self.doc_id or self.shelf_mark:
            score += 1.0
        if self.date:
            score += 1.0

        # Content (40% weight)
        if self.transcriptions:
            score += 2.0
            # Bonus for detailed transcriptions
            total_lines = 0
            for trans in self.transcriptions:
                if isinstance(trans.lines, dict):
                    total_lines += len([line for line in trans.lines.values() if line])
            if total_lines > 10:
                score += 0.5

        if self.translations:
            score += 1.0

        if self.image_urls:
            score += 1.0

        # Classification and metadata (20% weight)
        if self.document_category:
            score += 1.0
        if self.language and self.language != "Unknown":
            score += 0.5
        if self.related_people or self.related_places:
            score += 0.5

        # Physical/Administrative (10% weight)
        if self.miscellaneous_info:
            score += 0.5
        if self.original_url:
            score += 0.5

        return min(score / max_score, 1.0)


    def assess_content_quality(self) -> ContentQuality:
        """Assess overall content quality level.

        :return: Content quality assessment
        :rtype: ContentQuality

        Example:
             doc = GenizahDocument(image_urls=[], description="Basic document")
             quality = doc.assess_content_quality()
             quality in [ContentQuality.HIGH, ContentQuality.MEDIUM, ContentQuality.LOW, ContentQuality.MINIMAL]
            True
        """
        score = self.calculate_completeness_score()

        if score >= 0.8:
            return ContentQuality.HIGH
        elif score >= 0.6:
            return ContentQuality.MEDIUM
        elif score >= 0.4:
            return ContentQuality.LOW
        else:
            return ContentQuality.MINIMAL

    def infer_document_type(self) -> Optional[str]:
        """Infer document type from content and metadata.

        :return: Inferred document type or None if cannot determine
        :rtype: Optional[str]

        Example:
             doc = GenizahDocument(image_urls=[], description="Marriage contract from Cairo")
             doc.infer_document_type()
            'ketubah'
        """
        if self.document_category:
            return self.document_category

        # Analyze description for type indicators
        if self.description:
            desc_lower = self.description.lower()
            type_keywords = {
                'ketubah': ['ketubah', 'marriage contract', 'wedding'],
                'letter': ['letter', 'correspondence', 'epistle'],
                'legal': ['legal', 'contract', 'deed', 'court', 'testimony'],
                'liturgical': ['prayer', 'piyyut', 'liturgy', 'ritual'],
                'talmud': ['talmud', 'mishnah', 'gemara'],
                'bible': ['bible', 'biblical', 'torah', 'scripture'],
                'medical': ['medical', 'medicine', 'remedy', 'prescription'],
                'business': ['business', 'trade', 'commercial', 'invoice'],
                'poetry': ['poem', 'poetry', 'verse']
            }

            for doc_type, keywords in type_keywords.items():
                if any(keyword in desc_lower for keyword in keywords):
                    return doc_type

        # Check TEI metadata summary
        if self.full_metadata:
            for key, value in self.full_metadata.items():
                if 'summary' in key.lower() and value:
                    summary_lower = str(value).lower()
                    if 'talmud' in summary_lower:
                        return 'talmud'
                    elif 'ketubah' in summary_lower:
                        return 'ketubah'
                    elif 'letter' in summary_lower:
                        return 'letter'

        return None

    def create_full_text_content(self) -> str:
        """Create comprehensive full-text content for search indexing.

        :return: Combined text content from all fields
        :rtype: str

        Example:
             doc = GenizahDocument(
            ...     image_urls=[],
            ...     description="Test document",
            ...     transcriptions=[TranscriptionSection(lines={"1": "First line"})]
            ... )
             content = doc.create_full_text_content()
             "Test document" in content
            True
        """
        text_parts = []

        if self.description and self.description != "No description available":
            text_parts.append(self.description)

        # Add title from metadata if available
        if self.full_metadata:
            for key, value in self.full_metadata.items():
                if 'title' in key.lower() and value:
                    text_parts.append(str(value))
                    break

        # Add summary
        if self.full_metadata:
            for key, value in self.full_metadata.items():
                if 'summary' in key.lower() and value:
                    text_parts.append(str(value))
                    break

        # Add transcription text
        for trans in self.transcriptions:
            if isinstance(trans.lines, dict):
                text_parts.extend(str(line) for line in trans.lines.values() if line)
            else:
                text_parts.append(str(trans.lines))

        # Add translations
        for translation in self.translations:
            if translation and str(translation).strip():
                text_parts.append(str(translation))

        # Add miscellaneous info
        if self.miscellaneous_info:
            text_parts.append(self.miscellaneous_info)

        return ' '.join(text_parts)

    def to_elasticsearch_document(self, embedding: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Convert GenizahDocument to Elasticsearch document format.

        :param embedding: Optional embedding vector for similarity search
        :type embedding: Optional[np.ndarray]
        :return: Dictionary ready for Elasticsearch indexing
        :rtype: Dict[str, Any]

        Example:
             doc = GenizahDocument(image_urls=[], description="Test document")
             es_doc = doc.to_elasticsearch_document()
             "doc_id" in es_doc
            True
             "full_text_content" in es_doc
            True
        """
        # Extract all standardized information
        temporal_info = self.extract_temporal_info()
        language_info = self.extract_language_info()
        
        # Use appropriate physical info extraction method based on document type
        if self.full_metadata:
            # Cambridge-type document with TEI metadata
            physical_info = self.extract_physical_info()
        else:
            # Princeton-type document with other_info in miscellaneous_info
            physical_info = self.extract_physical_info_from_other_info()
        
        institutional_info = self.extract_institutional_info()
        named_entities = self.extract_named_entities()
        if self.description == "No description available":
            # Add summary from metadata if there is no description. This is very common in Cambridge Documents.
            if self.full_metadata:
                for key, value in self.full_metadata.items():
                    if 'summary' in key.lower() and value:
                        self.description = value
                        break
        # Build the Elasticsearch document
        es_doc = {
            # Core identifiers
            "doc_id": self.doc_id,
            "shelf_mark": self.shelf_mark,
            "source_collection": institutional_info.source_collection.value,

            # Content fields
            "description": self.description,
            "full_text_content": self.create_full_text_content(),

            # Temporal information
            "date_start": temporal_info.date_start,
            "date_end": temporal_info.date_end,
            "date_display": temporal_info.date_display,
            "century": temporal_info.century,
            "date_certainty": temporal_info.date_certainty.value,

            # Language information
            "main_language": language_info.main_language,
            "other_languages": language_info.other_languages,
            "script_type": language_info.script_type,

            # Physical characteristics
            "material": physical_info.material,
            "height": physical_info.height,
            "width": physical_info.width,
            "condition": physical_info.condition,
            "extent": physical_info.extent,

            # Institutional information
            "institution": institutional_info.institution,
            "repository": institutional_info.repository,
            "collection_name": institutional_info.collection_name,
            
            # Collection identifiers
            "collection": self.collection,
            "sub_collection": self.sub_collection,

            # Content classification
            "document_type": self.infer_document_type(),
            "named_entities": named_entities.dict(),

            # Structured content
            "transcriptions": self._format_transcriptions_for_es(),
            "has_transcriptions": True if self.transcriptions else False,
            "translations": self._format_translations_for_es(),
            "bibliography": [bib.dict() for bib in self.bibliography],
            "has_bib": True if self.bibliography else False,

            # Digital assets
            "image_urls": self.image_urls,
            "primary_image_index": self.primary_image_index,
            "has_images": bool(self.image_urls),
            "actual_image_url": self.actual_image_url,

            # Quality metrics
            "completeness_score": self.calculate_completeness_score(),
            "content_quality": self.assess_content_quality().value,

            # Administrative
            "original_url": self.original_url,
            "attribution_url": self.attribution_url,
            "indexed_at": datetime.now().isoformat(),
            "miscellaneous_info": self.miscellaneous_info,
            "language": self.language,  # Keep original language field for backward compatibility
            
            # Joins data
            "joins_data": self.joins_data
        }
        if es_doc["language"] == "Unknown":
            es_doc["language"] = convert_cambridge_lang_format(es_doc["main_language"])

        # Add embedding if provided
        if embedding is not None:
            es_doc["embedding_vector"] = embedding.flatten().tolist()

        # Add TEI metadata for Cambridge documents (stored but not indexed)
        if self.full_metadata:
            es_doc["tei_metadata"] = self.full_metadata

        # Remove None values to keep index clean
        return {k: v for k, v in es_doc.items() if v is not None}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for backward compatibility.

        :return: Dictionary representation of the document
        :rtype: Dict[str, Any]

        Example:
             doc = GenizahDocument(image_urls=["test.jpg"], description="Test")
             doc_dict = doc.to_dict()
             doc_dict["description"]
            'Test'
        """
        return {
            "images": self.image_urls,
            "description": self.description,
            "transcriptions": [t.to_dict() for t in self.transcriptions],
            "translations": self.translations,
            "date": self.date,
            "language": self.language,
            "full_metadata_info": self.full_metadata,
            "original_url": self.original_url,
            "doc_id": self.doc_id,
            "shelf_mark": self.shelf_mark,
            "related_people": [p.to_dict() for p in self.related_people],
            "related_places": [p.to_dict() for p in self.related_places],
            "bibliography": [b.to_dict() for b in self.bibliography],
            "image_metadata": self.image_metadata,
            "joins_data": self.joins_data
        }

    # ===== PRIVATE HELPER METHODS =====

    def _parse_date_string(self, date_string: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse various date formats into start and end dates.

        :param date_string: Date string to parse
        :type date_string: str
        :return: Tuple of (start_date, end_date) or (None, None) if unparseable
        :rtype: Tuple[Optional[str], Optional[str]]
        """
        if not date_string or date_string in ['Unknown', '', 'null']:
            return None, None

        date_string = str(date_string).strip()

        # Handle date ranges like "0965-08-31/0966-09-17"
        if '/' in date_string:
            parts = date_string.split('/')
            start_str = parts[0].strip()
            end_str = parts[1].strip()

            if re.match(r'\d{4}-\d{2}-\d{2}', start_str):
                return start_str, end_str

            # Year ranges like "950/1300"
            if re.match(r'\d{3,4}', start_str) and re.match(r'\d{3,4}', end_str):
                return f"{start_str}-01-01", f"{end_str}-12-31"

        # Handle ranges with dash
        if '–' in date_string or ' - ' in date_string:
            separator = '–' if '–' in date_string else ' - '
            parts = date_string.split(separator)
            if len(parts) == 2:
                start_match = re.search(r'\b(\d{3,4})\b', parts[0])
                end_match = re.search(r'\b(\d{3,4})\b', parts[1])
                if start_match and end_match:
                    return f"{start_match.group(1)}-01-01", f"{end_match.group(1)}-12-31"

        # Single dates like "969-03-17"
        if re.match(r'\d{4}-\d{2}-\d{2}', date_string):
            return date_string, date_string

        # Extract year from complex strings
        year_match = re.search(r'\b(\d{3,4})\b', date_string)
        if year_match:
            year = year_match.group(1)
            return f"{year}-01-01", f"{year}-12-31"

        return None, None

    def _extract_tei_languages(self, metadata: Dict[str, Any]) -> Tuple[Optional[str], List[str]]:
        """Extract language information from TEI metadata.

        :param metadata: TEI metadata dictionary
        :type metadata: Dict[str, Any]
        :return: Tuple of (main_language, other_languages)
        :rtype: Tuple[Optional[str], List[str]]
        """
        main_language = None
        other_languages = []

        for key, value in metadata.items():
            if 'textlang' in key.lower() and value:
                # Parse mainLang and otherLangs from key attributes
                if 'mainlang' in key.lower():
                    main_lang_match = re.search(r"'mainLang':\s*'([^']*)'", key)
                    if main_lang_match:
                        main_language = main_lang_match.group(1)

                    other_lang_match = re.search(r"'otherLangs':\s*'([^']*)'", key)
                    if other_lang_match and other_lang_match.group(1):
                        other_langs_str = other_lang_match.group(1)
                        other_languages = [lang.strip() for lang in re.split(r'[,\s]+', other_langs_str) if
                                           lang.strip()]

        return main_language, other_languages

    def _format_transcriptions_for_es(self) -> List[Dict[str, Any]]:
        """Format transcriptions for Elasticsearch nested structure.

        :return: List of transcription dictionaries for ES indexing
        :rtype: List[Dict[str, Any]]
        """
        formatted = []
        for trans in self.transcriptions:
            editor = trans.name.replace('Editor: ', '') if trans.name else None

            # Extract text from lines
            text_parts = []
            line_count = 0
            if isinstance(trans.lines, dict):
                for line in trans.lines.values():
                    if line:
                        text_parts.append(str(line))
                        line_count += 1
            elif isinstance(trans.lines, list):
                text_parts = [str(line) for line in trans.lines if line]
                line_count = len(text_parts)
            else:
                text_parts = [str(trans.lines)] if trans.lines else []
                line_count = len(text_parts)

            formatted.append({
                'editor': editor,
                'text': ' '.join(text_parts),
                'line_count': line_count,
                'language': self.language if self.language != "Unknown" else None
            })

        return formatted

    def _format_translations_for_es(self) -> List[Dict[str, Any]]:
        """Format translations for Elasticsearch nested structure.

        :return: List of translation dictionaries for ES indexing
        :rtype: List[Dict[str, Any]]
        """
        formatted = []
        for i, translation in enumerate(self.translations):
            if translation and str(translation).strip():
                formatted.append({
                    'text': str(translation),
                    'translation_type': f'translation_{i + 1}',
                    'target_language': 'english'  # Assume English unless specified
                })

        return formatted

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GenizahDocument':
        """Create GenizahDocument from dictionary data.

        :param data: Dictionary containing document data
        :type data: Dict[str, Any]
        :return: GenizahDocument instance
        :rtype: GenizahDocument

        Example:
             data = {
            ...     "image_urls": ["test.jpg"],
            ...     "description": "Test document",
            ...     "transcriptions": [],
            ...     "translations": []
            ... }
             doc = GenizahDocument.from_dict(data)
             doc.description
            'Test document'
        """
        # Map legacy field names to new field names
        field_mapping = {
            'images': 'image_urls',
            'other_info': 'miscellaneous_info',
            'orig_url': 'original_url'
        }

        # Apply field mapping
        mapped_data = {}
        for key, value in data.items():
            new_key = field_mapping.get(key, key)
            mapped_data[new_key] = value

        return cls(**mapped_data)

    @classmethod
    def from_cambridge_format(cls, cambridge_data: Dict[str, Any]) -> 'GenizahDocument':
        """Create GenizahDocument from Cambridge TEI format data.

        :param cambridge_data: Cambridge format document data
        :type cambridge_data: Dict[str, Any]
        :return: GenizahDocument instance
        :rtype: GenizahDocument

        Example:
             cambridge_data = {
            ...     "doc_id": "MS-TS-F-00001",
            ...     "description": "Talmud fragment",
            ...     "full_metadata": {"{http://www.tei-c.org/ns/1.0}title": "Babylonian Talmud"},
            ...     "image_urls": ["https://example.com/image.jpg"]
            ... }
             doc = GenizahDocument.from_cambridge_format(cambridge_data)
             doc.doc_id
            'MS-TS-F-00001'
        """
        # Extract basic fields
        doc_data = {
            'image_urls': cambridge_data.get('image_urls', []),
            'description': cambridge_data.get('description', ''),
            'transcriptions': cambridge_data.get('transcriptions', []),
            'translations': cambridge_data.get('translations', []),
            'date': cambridge_data.get('date'),
            'language': "Unknown",
            'doc_id': cambridge_data.get('doc_id'),
            'original_url': cambridge_data.get('original_url'),
            'miscellaneous_info': cambridge_data.get('miscellaneous_info'),
            'document_category': cambridge_data.get('document_category'),
            'shelf_mark': cambridge_data.get('shelf_mark'),
            'image_metadata': cambridge_data.get('image_metadata'),
            'full_metadata': cambridge_data.get('full_metadata_info', cambridge_data.get('full_metadata', {}))
        }

        instance = cls(**doc_data)
        # Populate institution/collection/sub-collection from shelf mark when possible
        instance._apply_shelfmark_mapping()
        return instance

    def create_text_representation(self) -> str:
        """Create a structured textual representation for embedding generation.

        This method creates a formatted text representation that's optimized for
        embedding models, with clear field labels and proper content prioritization.

        :return: Structured text representation for embedding
        :rtype: str

        Example:
            doc = GenizahDocument(
            ...     image_urls=[],
            ...     description="Talmud fragment",
            ...     doc_id="MS-TS-001",
            ...     language="Hebrew"
            ... )
            text_rep = doc.create_text_representation()
            "Document ID: MS-TS-001" in text_rep
            True
            "Description: Talmud fragment" in text_rep
            True
        """
        text_parts = []

        # Add document ID for identification
        if self.doc_id:
            text_parts.append(f"Document ID: {self.doc_id}")

        # Add shelf mark if different from doc_id
        if self.shelf_mark and self.shelf_mark != self.doc_id:
            text_parts.append(f"Shelf Mark: {self.shelf_mark}")

        # Add description (high priority)
        if self.description:
            text_parts.append(f"Description: {self.description}")

        # Add title from metadata if available
        if self.full_metadata:
            for key, value in self.full_metadata.items():
                if 'title' in key.lower() and value:
                    text_parts.append(f"Title: {value}")
                    break

        # Add summary from metadata
        if self.full_metadata:
            for key, value in self.full_metadata.items():
                if 'summary' in key.lower() and value:
                    text_parts.append(f"Summary: {value}")
                    break

        # Add language information
        if self.language and self.language != "Unknown":
            text_parts.append(f"Language: {self.language}")

        # Add document type if inferred
        doc_type = self.infer_document_type()
        if doc_type:
            text_parts.append(f"Document Type: {doc_type}")

        # Add date information
        if self.date:
            date_str = ""
            for key, value in self.date.items():
                if value:
                    date_str += f"{key}: {value}, "
            date_str = date_str.rstrip(", ")

            if date_str:
                text_parts.append(f"Date: {date_str}")

        # Add transcription content (with truncation for very long texts)
        if self.transcriptions:
            combined_transcription = ""
            for transcription in self.transcriptions:
                # Add editor information
                if transcription.name:
                    editor_name = transcription.name.replace('Editor: ', '')
                    combined_transcription += f"[Editor: {editor_name}] "

                # Add transcription lines
                if isinstance(transcription.lines, dict):
                    for line_num, line_text in sorted(transcription.lines.items()):
                        if line_text:
                            combined_transcription += f"{line_text} "
                elif isinstance(transcription.lines, list):
                    for line_text in transcription.lines:
                        if line_text:
                            combined_transcription += f"{line_text} "
                else:
                    if transcription.lines:
                        combined_transcription += f"{transcription.lines} "

            # Truncate if too long to avoid overwhelming the embedding
            max_transcription_length = 1000
            if len(combined_transcription) > max_transcription_length:
                combined_transcription = combined_transcription[:max_transcription_length] + "..."

            if combined_transcription.strip():
                text_parts.append(f"Transcription: {combined_transcription.strip()}")

        # Add translation content (with truncation)
        if self.translations:
            combined_translations = " ".join(
                str(translation) for translation in self.translations
                if translation and str(translation).strip()
            )

            # Truncate if too long
            max_translation_length = 500
            if len(combined_translations) > max_translation_length:
                combined_translations = combined_translations[:max_translation_length] + "..."

            if combined_translations:
                text_parts.append(f"Translation: {combined_translations}")

        # Add related people
        if self.related_people:
            people_names = [person.name for person in self.related_people if person.name]
            if people_names:
                text_parts.append(f"Related People: {', '.join(people_names)}")

        # Add related places
        if self.related_places:
            place_names = [place.name for place in self.related_places if place.name]
            if place_names:
                text_parts.append(f"Related Places: {', '.join(place_names)}")

        # Add physical characteristics from metadata
        physical_info = self.extract_physical_info()
        physical_details = []
        if physical_info.material:
            physical_details.append(f"Material: {physical_info.material}")
        if physical_info.height and physical_info.width:
            physical_details.append(f"Dimensions: {physical_info.height} x {physical_info.width}")
        if physical_info.condition:
            physical_details.append(f"Condition: {physical_info.condition}")

        if physical_details:
            text_parts.append(f"Physical: {'; '.join(physical_details)}")

        # Add miscellaneous information
        if self.miscellaneous_info:
            # Truncate misc info if very long
            misc_text = self.miscellaneous_info
            max_misc_length = 300
            if len(misc_text) > max_misc_length:
                misc_text = misc_text[:max_misc_length] + "..."
            text_parts.append(f"Additional Info: {misc_text}")

        return "\n".join(text_parts)

    @classmethod
    def from_princeton_format(cls, princeton_data: Dict[str, Any]) -> 'GenizahDocument':
        """Create GenizahDocument from Princeton format data.

        :param princeton_data: Princeton format document data
        :type princeton_data: Dict[str, Any]
        :return: GenizahDocument instance
        :rtype: GenizahDocument

        Example:
             princeton_data = {
            ...     "doc_id": "bodl_ms_heb_12_25",
            ...     "description": "Legal document",
            ...     "images": ["https://example.com/image.jpg"],
            ...     "related_people": [{"name": "Test Person", "role": "author"}]
            ... }
             doc = GenizahDocument.from_princeton_format(princeton_data)
             len(doc.related_people)
            1
        """
        # Convert Princeton format to standard format
        # Handle miscellaneous_info - prefer the JSON string version if available
        misc_info = princeton_data.get('miscellaneous_info')
        if misc_info is None:
            # Fall back to other_info and convert to JSON string
            other_info = princeton_data.get('other_info')
            if other_info:
                import json
                misc_info = json.dumps(other_info)
        
        # Handle transcriptions and translations - ensure they are lists
        transcriptions = princeton_data.get('transcriptions', [])
        if isinstance(transcriptions, dict):
            # Convert dictionary transcriptions to TranscriptionSection objects
            transcription_sections = []
            for key, text in transcriptions.items():
                if text and text.strip():  # Only include non-empty transcriptions
                    # Create a TranscriptionSection with the text as lines
                    lines = {str(i+1): line.strip() for i, line in enumerate(text.split('\n')) if line.strip()}
                    if lines:  # Only add if there are actual lines
                        transcription_sections.append(TranscriptionSection(name=f"Transcription {key}", lines=lines))
            transcriptions = transcription_sections
            
        translations = princeton_data.get('translations', [])
        if isinstance(translations, dict):
            # Convert dictionary translations to list
            translations = [text for text in translations.values() if text and text.strip()]
        
        doc_data = {
            'image_urls': princeton_data.get('images', []),
            'description': princeton_data.get('description', ''),
            'transcriptions': transcriptions,
            'translations': translations,
            'date': princeton_data.get('date'),
            'language': princeton_data.get('language', 'Unknown'),
            'doc_id': princeton_data.get('doc_id'),
            'original_url': princeton_data.get('original_url'),
            'attribution_url': princeton_data.get('attribution_url') or princeton_data.get('collection_attribution_url'),  # Support both old and new field names
            'miscellaneous_info': misc_info,
            'shelf_mark': princeton_data.get('shelf_mark'),
            'collection': princeton_data.get('collection'),
            'sub_collection': princeton_data.get('sub_collection'),
            'related_people': princeton_data.get('related_people', []),
            'related_places': princeton_data.get('related_places', []),
            'bibliography': princeton_data.get('bibliography', []),
            'joins_data': princeton_data.get('joins_data')
        }

        instance = cls(**doc_data)
        # Populate institution/collection/sub-collection from shelf mark when possible
        instance._apply_shelfmark_mapping()
        return instance


