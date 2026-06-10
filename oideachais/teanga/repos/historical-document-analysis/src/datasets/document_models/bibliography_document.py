
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True)
logger = logging.getLogger(__name__)

class BibliographyDocument(BaseModel):
    """Pydantic model representing a single bibliography page entry for indexing.

    The model wraps the structured JSON extracted from academic literature pages and
    provides the required interface for the existing Elasticsearch processor.

    :param doc_id: Unique identifier for the bibliography entry. Defaults to
                   ``{pdf_name}_p{page_number:03d}``.
    :type doc_id: str
    :param shelf_mark: Canonical shelf mark associated with the entry. If multiple
                       are present, the first is used. Falls back to ``pdf_name``.
    :type shelf_mark: str
    :param pdf_name: Name of the source PDF from which this page was processed.
    :type pdf_name: str
    :param page_number: Page number within the PDF (1-based preferred).
    :type page_number: int
    :param shelf_marks_mentioned: List of shelf marks detected on this page.
    :type shelf_marks_mentioned: List[str]
    :param transcriptions: Mapping of shelf mark to its transcribed text on the page.
    :type transcriptions: Dict[str, str]
    :param full_main_text: The full OCRed or extracted text content for the page.
    :type full_main_text: str
    :param summary: Optional summarization of the page content.
    :type summary: Optional[str]
    :param metadata: Additional metadata captured during processing (e.g., model_used).
    :type metadata: Dict[str, Any]

    Example::

        doc = BibliographyDocument(
            doc_id="cairo_to_manchester_1_p058",
            shelf_mark="B 2349-1",
            pdf_name="cairo_to_manchester_1",
            page_number=58,
            shelf_marks_mentioned=["B 2349-1", "B 2349-2"],
            transcriptions={"B 2349-1": "...", "B 2349-2": "..."},
            full_main_text="From Cairo to Manchester ...",
            summary="This page presents studies ...",
            metadata={"model_used": "gemma3:27b"},
        )
    """

    doc_id: str
    shelf_mark: str
    pdf_name: str
    page_number: int
    extracted_page_number: Optional[Any] = None
    shelf_marks_mentioned: Union[List[str], Dict[str, str]] = Field(default_factory=list)
    shelf_marks_mentioned_raw: Optional[Dict[str, str]] = None  # Store original dict format if available
    transcriptions: Dict[str, str] = Field(default_factory=dict)
    full_main_text: str = ""
    summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    page_display: Optional[str] = None
    # Book-level metadata fields
    author: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    title: Optional[str] = None
    isbn: Optional[str] = None
    subject_keywords: List[str] = Field(default_factory=list)

    # Compatibility attributes expected by the processor
    image: Optional[Any] = None

    def create_text_representation(self) -> str:
        """Create a comprehensive text representation for embedding generation.

        The representation prioritizes summary, aggregates transcriptions, and
        includes key metadata for better retrieval.

        :return: Combined text representation of the bibliography page.
        :rtype: str
        """
        parts: List[str] = []

        parts.append(f"Source PDF: {self.pdf_name}, Page: {self.page_number}")
        if self.title:
            parts.append(f"Title: {self.title}")
        if self.authors:
            parts.append(f"Authors: {', '.join(self.authors)}")
        elif self.author:
            parts.append(f"Author: {self.author}")
        if self.subject_keywords:
            parts.append(f"Subjects: {', '.join(self.subject_keywords)}")
        if self.shelf_marks_mentioned:
            if isinstance(self.shelf_marks_mentioned, dict):
                shelf_marks_list = list(self.shelf_marks_mentioned.keys())
                parts.append("Shelf marks mentioned: " + ", ".join(shelf_marks_list))
            else:
                parts.append("Shelf marks mentioned: " + ", ".join(self.shelf_marks_mentioned))

        if self.summary:
            parts.append(f"Summary: {self.summary}")

        if self.full_main_text:
            parts.append(f"Main text: {self.full_main_text}")

        if self.transcriptions:
            for sm, text in self.transcriptions.items():
                if text:
                    parts.append(f"Transcription for {sm}: {text}")

        return "\n".join(parts)

    def get_embedding_cache_key(self) -> str:
        """Return a stable cache key for this document's embedding.

        :return: Cache key string for embeddings.
        :rtype: str
        """
        # The doc_id already encodes pdf/page; include shelf_mark for uniqueness across variants
        return f"biblio::{self.doc_id}::{self.shelf_mark}"

    def to_elasticsearch_document(self, embedding: Optional[Any] = None) -> Dict[str, Any]:
        """Convert this entry to an Elasticsearch document compatible with the indexer.

        :param embedding: Optional dense vector to store for semantic search.
        :type embedding: Optional[Any]
        :return: Dictionary formatted for Elasticsearch indexing.
        :rtype: Dict[str, Any]
        """
        full_text_content = self.create_text_representation()
        es_doc: Dict[str, Any] = {
            "doc_id": self.doc_id,
            "shelf_mark": self.shelf_mark,
            "description": self.summary or "",
            "full_text_content": full_text_content,
            "document_type": "bibliography",
            "source_collection": "academic_literature",
            "main_language": self.metadata.get("language", "Unknown"),
            "page_number": self.page_number,
            "extracted_page_number": self.extracted_page_number,
        }

        # Book-level metadata fields (only include if not None/empty)
        author_str = self.author or (", ".join(self.authors) if self.authors else None)
        if author_str:
            es_doc["author"] = author_str

        if self.authors:
            es_doc["authors"] = self.authors
        elif self.author:
            es_doc["authors"] = [a.strip() for a in self.author.split(",") if a.strip()]

        if self.title:
            es_doc["title"] = self.title

        if self.isbn:
            es_doc["isbn"] = self.isbn

        if self.subject_keywords:
            es_doc["subject_keywords"] = self.subject_keywords

        # Store shelf_marks_mentioned as a list to avoid creating too many dynamic fields
        # Elasticsearch has a limit of 1000 fields, and storing as object creates a field per key
        if isinstance(self.shelf_marks_mentioned, dict):
            es_doc["shelf_marks_mentioned"] = list(self.shelf_marks_mentioned.keys())
        elif isinstance(self.shelf_marks_mentioned, list) and len(self.shelf_marks_mentioned) > 0:
            es_doc["shelf_marks_mentioned"] = self.shelf_marks_mentioned
        else:
            es_doc["shelf_marks_mentioned"] = []

        es_doc["bibliography"] = [
            {
                "citation": self.metadata.get("pdf_name", self.pdf_name),
                "location": f"page {self.page_number}",
                "relations": "mentions",
                "url": self.metadata.get("source_url", ""),
            }
        ]

        # Store transcriptions as a list of objects to suit nested mapping
        es_doc["transcriptions"] = [
            {
                "text": txt,
                "editor": self.metadata.get("model_used", "unknown"),
                "line_count": len(txt.splitlines()) if isinstance(txt, str) else 0,
                "language": self.metadata.get("language", "Unknown"),
            }
            for txt in self.transcriptions.values()
            if isinstance(txt, str) and txt.strip() != ""
        ]

        if embedding is not None:
            # Ensure vector is a flat 1D list of numbers (ES dense_vector requirement)
            try:
                if hasattr(embedding, "ndim") and getattr(embedding, "ndim") > 1:
                    flat = embedding.reshape(-1)
                    es_doc["embedding_vector"] = flat.tolist()
                else:
                    vec = embedding.tolist() if hasattr(embedding, "tolist") else embedding
                    # If nested (e.g., [[...]]), flatten once
                    if isinstance(vec, list) and len(vec) > 0 and isinstance(vec[0], list):
                        es_doc["embedding_vector"] = [x for row in vec for x in row]
                    else:
                        es_doc["embedding_vector"] = list(vec)
            except Exception:
                # Fall back without transformation
                es_doc["embedding_vector"] = embedding

        return es_doc

    @staticmethod
    def from_structured_json(json_path: Path, book_metadata: Optional[Dict[str, Any]] = None) -> "BibliographyDocument":
        """Create a BibliographyDocument from a structured JSON file.

        :param json_path: Path to a JSON file in the academic literature structured format.
        :type json_path: Path
        :return: Parsed BibliographyDocument instance.
        :rtype: BibliographyDocument

        Example::

            doc = BibliographyDocument.from_structured_json(
                json_path=Path("/path/to/page_001_structured.json")
            )
        """
        with open(json_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)

        metadata: Dict[str, Any] = data.get("metadata", {})
        pdf_name: str = metadata.get("pdf_name", "unknown_pdf")

        if not pdf_name or pdf_name == "unknown_pdf":
            logger.warning(f"No pdf_name in metadata for {json_path}, using 'unknown_pdf'")

        # Prefer extracted_page_number if present, else metadata.page_number (can be roman numerals)
        # Handle case where extracted_page_number might be 0 (which is falsy but valid)
        extracted_page_number_raw = data.get("extracted_page_number")
        if extracted_page_number_raw is None:
            raw_page = metadata.get("page_number")
        else:
            raw_page = extracted_page_number_raw

        def roman_to_int(roman: str) -> Optional[int]:
            """Convert a Roman numeral to integer.

            :param roman: Roman numeral string (e.g., 'iv', 'XII').
            :type roman: str
            :return: Integer value or None if not a valid roman numeral.
            :rtype: Optional[int]
            """
            if not isinstance(roman, str) or roman.strip() == "":
                return None
            s = roman.strip().upper()
            valid = set("IVXLCDM")
            if not all(ch in valid for ch in s):
                return None
            values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
            total = 0
            prev = 0
            for ch in reversed(s):
                val = values[ch]
                if val < prev:
                    total -= val
                else:
                    total += val
                    prev = val
            # Basic sanity: re-encode check could be added; keep simple
            return total

        def parse_page(raw: Any) -> tuple[int, str]:
            """Parse page value supporting integers, numeric strings, and Roman numerals.

            :param raw: Raw page value from JSON.
            :type raw: Any
            :return: Tuple of (numeric_page_or_0, display_label)
            :rtype: tuple[int, str]
            """
            if raw is None:
                return 0, "unknown"
            if isinstance(raw, int):
                return raw, str(raw)
            if isinstance(raw, str):
                s = raw.strip()
                if s.isdigit():
                    return int(s), s
                rn = roman_to_int(s)
                if rn is not None:
                    return rn, s
                # fallback: unknown label
                return 0, s
            # unsupported type
            return 0, str(raw)

        page_number, page_label = parse_page(raw_page)

        # Determine shelf_mark: ONLY from shelf_marks_mentioned, use placeholder if empty
        # shelf_marks_mentioned can be either a list of shelf marks OR a dict where keys are shelf marks
        shelf_marks_raw = data.get("shelf_marks_mentioned")
        shelf_marks_mentioned_raw: Optional[Dict[str, str]] = None
        mentioned: Union[List[str], Dict[str, str]]

        if isinstance(shelf_marks_raw, dict):
            # If it's a dict, preserve it for the index, and extract keys for shelf_mark
            shelf_marks_mentioned_raw = shelf_marks_raw
            mentioned = shelf_marks_raw  # Keep as dict for the model
            # Extract keys for the shelf_mark field
            shelf_mark_keys = [k.strip() for k in shelf_marks_raw.keys() if k and str(k).strip()]
            if len(shelf_mark_keys) > 0:
                shelf_mark: str = shelf_mark_keys[0]
            else:
                shelf_mark = "NO_SHELF_MARK"
        elif isinstance(shelf_marks_raw, list):
            mentioned = shelf_marks_raw
            # Filter out empty strings and None values
            mentioned = [str(m).strip() for m in mentioned if m and str(m).strip()]
            if len(mentioned) > 0:
                shelf_mark: str = mentioned[0]
            else:
                shelf_mark = "NO_SHELF_MARK"
        elif shelf_marks_raw is None:
            mentioned = []
            shelf_mark = "NO_SHELF_MARK"
        else:
            # Try to convert to list if it's a single value
            mentioned = [str(shelf_marks_raw)] if shelf_marks_raw else []
            logger.warning \
                (f"shelf_marks_mentioned is not a list or dict in {json_path}, converting: {type(shelf_marks_raw)}")
            if len(mentioned) > 0:
                shelf_mark: str = mentioned[0]
            else:
                shelf_mark = "NO_SHELF_MARK"

        # Build a stable doc_id using numeric page when possible; otherwise use the label directly
        if page_number > 0:
            doc_id = f"{pdf_name}_p{page_number:03d}"
        else:
            safe_label = page_label.replace(" ", "_") if page_label else "unknown"
            doc_id = f"{pdf_name}_p{safe_label}"

        # Extract book-level metadata from book_metadata if provided
        author = None
        authors: List[str] = []
        title = None
        isbn = None
        subject_keywords: List[str] = []

        if book_metadata:
            # Handle authors (can be string or list)
            authors_raw = book_metadata.get("authors", book_metadata.get("author"))
            if isinstance(authors_raw, list):
                authors = authors_raw
                author = ", ".join(authors) if authors else None
            elif isinstance(authors_raw, str):
                author = authors_raw
                authors = [a.strip() for a in authors_raw.split(",") if a.strip()]

            title = book_metadata.get("title")
            isbn = book_metadata.get("isbn") or book_metadata.get("ISBN")

            # Handle subjects/keywords
            subjects_raw = book_metadata.get("subjects", book_metadata.get("subject_keywords", book_metadata.get("keywords")))
            if isinstance(subjects_raw, list):
                subject_keywords = subjects_raw
            elif isinstance(subjects_raw, str):
                subject_keywords = [s.strip() for s in subjects_raw.split(",") if s.strip()]

        # Process transcriptions: handle nested dict structure (Dict[str, Dict[str, str]])
        # where first key is shelf mark and second key is line number
        transcriptions_raw = data.get("transcriptions", {})
        transcriptions_flat: Dict[str, str] = {}

        if isinstance(transcriptions_raw, dict):
            for shelf_mark_key, transcription_value in transcriptions_raw.items():
                if isinstance(transcription_value, dict):
                    # Nested structure: concatenate line transcriptions
                    lines = []
                    # Sort by line number (keys might be strings like "0", "1", "2")
                    sorted_keys = sorted(transcription_value.keys(), key=lambda x: int(x) if str(x).isdigit() else float('inf'))
                    for line_key in sorted_keys:
                        line_text = transcription_value[line_key]
                        if isinstance(line_text, str) and line_text.strip():
                            lines.append(line_text.strip())
                    if lines:
                        transcriptions_flat[shelf_mark_key] = "\n".join(lines)
                elif isinstance(transcription_value, str):
                    # Already flat structure
                    if transcription_value.strip():
                        transcriptions_flat[shelf_mark_key] = transcription_value.strip()

        return BibliographyDocument(
            doc_id=doc_id,
            shelf_mark=shelf_mark,
            pdf_name=pdf_name,
            page_number=page_number,
            extracted_page_number=extracted_page_number_raw,
            page_display=page_label,
            shelf_marks_mentioned=mentioned,
            shelf_marks_mentioned_raw=shelf_marks_mentioned_raw,
            transcriptions=transcriptions_flat,
            full_main_text=data.get("full_main_text", ""),
            summary=data.get("summary"),
            metadata=metadata,
            author=author,
            authors=authors,
            title=title,
            isbn=isbn,
            subject_keywords=subject_keywords,
        )


