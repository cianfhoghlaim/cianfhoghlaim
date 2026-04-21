"""
Irish-English Bilingual Alignment.

Implements multiple alignment strategies for creating parallel corpora:
- VecAlign: Neural embedding-based alignment (recommended for curriculum)
- HunAlign: Dictionary-based alignment
- GaoisAlign: Irish-specific alignment using Gaois terminology

Based on research from taighde_bonneagar/03-bilingual-dataset-creation/.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
from sentence_transformers import SentenceTransformer


class AlignmentMethod(str, Enum):
    """Alignment method selection."""

    VECALIGN = "vecalign"  # Neural embedding-based
    HUNALIGN = "hunalign"  # Dictionary-based
    GAOISALIGN = "gaoisalign"  # Irish terminology-based
    HYBRID = "hybrid"  # Combine multiple methods


@dataclass
class ParallelPair:
    """A single aligned parallel text pair."""

    source_text: str  # English text
    target_text: str  # Irish text
    source_lang: str = "en"
    target_lang: str = "ga"
    alignment_score: float = 0.0
    source_id: str | None = None
    target_id: str | None = None
    metadata: dict = field(default_factory=dict)

    @property
    def pair_id(self) -> str:
        """Generate unique ID for this pair."""
        content = f"{self.source_text}|{self.target_text}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "pair_id": self.pair_id,
            "en": self.source_text,
            "ga": self.target_text,
            "alignment_score": self.alignment_score,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "metadata": self.metadata,
        }

    def to_chat_format(self, system_prompt: str | None = None) -> dict:
        """Convert to JSONL Chat format for LLM training."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": self.source_text})
        messages.append({"role": "assistant", "content": self.target_text})
        return {"messages": messages}


@dataclass
class AlignmentResult:
    """Result of an alignment operation."""

    pairs: list[ParallelPair]
    method: AlignmentMethod
    source_doc_id: str | None = None
    target_doc_id: str | None = None
    total_source_sentences: int = 0
    total_target_sentences: int = 0
    aligned_count: int = 0
    dropped_count: int = 0
    average_score: float = 0.0

    @property
    def alignment_rate(self) -> float:
        """Percentage of sentences successfully aligned."""
        total = max(self.total_source_sentences, self.total_target_sentences)
        return self.aligned_count / total if total > 0 else 0.0


class IrishEnglishAligner:
    """
    Bilingual alignment for Irish-English parallel text.

    Supports multiple alignment strategies optimized for Irish educational content.
    Uses multilingual embeddings for semantic similarity matching.

    Usage:
        aligner = IrishEnglishAligner(method=AlignmentMethod.VECALIGN)
        result = aligner.align(english_sentences, irish_sentences)
        for pair in result.pairs:
            print(f"{pair.source_text} -> {pair.target_text}")
    """

    # Multilingual model optimized for Irish
    DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # Alignment thresholds
    MIN_ALIGNMENT_SCORE = 0.7
    MIN_LENGTH_RATIO = 0.3
    MAX_LENGTH_RATIO = 3.0

    def __init__(
        self,
        method: AlignmentMethod = AlignmentMethod.VECALIGN,
        model_name: str | None = None,
        min_score: float = MIN_ALIGNMENT_SCORE,
        batch_size: int = 100,
    ):
        """
        Initialize aligner.

        Args:
            method: Alignment method to use
            model_name: Sentence transformer model for embeddings
            min_score: Minimum alignment score threshold
            batch_size: Batch size for embedding computation (min 100)
        """
        self.method = method
        self.model_name = model_name or self.DEFAULT_MODEL
        self.min_score = min_score
        self.batch_size = max(batch_size, 100)  # Enforce minimum batch size

        self._model: SentenceTransformer | None = None
        self._gaois_dict: dict[str, str] | None = None

    @property
    def model(self) -> SentenceTransformer:
        """Lazy-load embedding model."""
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def align(
        self,
        source_sentences: Sequence[str],
        target_sentences: Sequence[str],
        source_doc_id: str | None = None,
        target_doc_id: str | None = None,
    ) -> AlignmentResult:
        """
        Align source (English) and target (Irish) sentences.

        Args:
            source_sentences: List of English sentences
            target_sentences: List of Irish sentences
            source_doc_id: Optional source document identifier
            target_doc_id: Optional target document identifier

        Returns:
            AlignmentResult with aligned pairs and statistics
        """
        if self.method == AlignmentMethod.VECALIGN:
            pairs = self._vecalign(source_sentences, target_sentences)
        elif self.method == AlignmentMethod.HUNALIGN:
            pairs = self._hunalign(source_sentences, target_sentences)
        elif self.method == AlignmentMethod.GAOISALIGN:
            pairs = self._gaoisalign(source_sentences, target_sentences)
        elif self.method == AlignmentMethod.HYBRID:
            pairs = self._hybrid_align(source_sentences, target_sentences)
        else:
            raise ValueError(f"Unknown alignment method: {self.method}")

        # Filter by score threshold
        filtered_pairs = [p for p in pairs if p.alignment_score >= self.min_score]

        avg_score = (
            sum(p.alignment_score for p in filtered_pairs) / len(filtered_pairs)
            if filtered_pairs
            else 0.0
        )

        return AlignmentResult(
            pairs=filtered_pairs,
            method=self.method,
            source_doc_id=source_doc_id,
            target_doc_id=target_doc_id,
            total_source_sentences=len(source_sentences),
            total_target_sentences=len(target_sentences),
            aligned_count=len(filtered_pairs),
            dropped_count=len(pairs) - len(filtered_pairs),
            average_score=avg_score,
        )

    def align_documents(
        self,
        source_doc: str,
        target_doc: str,
        source_doc_id: str | None = None,
        target_doc_id: str | None = None,
    ) -> AlignmentResult:
        """
        Align full documents by first segmenting into sentences.

        Args:
            source_doc: Full English document text
            target_doc: Full Irish document text
            source_doc_id: Optional source document identifier
            target_doc_id: Optional target document identifier

        Returns:
            AlignmentResult with aligned pairs
        """
        source_sentences = self._segment_sentences(source_doc, lang="en")
        target_sentences = self._segment_sentences(target_doc, lang="ga")

        return self.align(
            source_sentences,
            target_sentences,
            source_doc_id=source_doc_id,
            target_doc_id=target_doc_id,
        )

    def _vecalign(
        self,
        source: Sequence[str],
        target: Sequence[str],
    ) -> list[ParallelPair]:
        """
        Neural embedding-based alignment using cosine similarity.

        Embeds all sentences and finds optimal alignment using similarity matrix.
        """
        if not source or not target:
            return []

        # Batch embed for performance (critical: batching is 100x faster)
        source_embeddings = self._batch_embed(list(source))
        target_embeddings = self._batch_embed(list(target))

        # Compute cosine similarity matrix
        similarity_matrix = self._cosine_similarity_matrix(
            source_embeddings, target_embeddings
        )

        # Greedy alignment with length ratio filtering
        pairs = []
        used_source = set()
        used_target = set()

        # Sort by similarity score (descending)
        indices = np.dstack(np.unravel_index(
            np.argsort(similarity_matrix.ravel())[::-1],
            similarity_matrix.shape
        ))[0]

        for src_idx, tgt_idx in indices:
            if src_idx in used_source or tgt_idx in used_target:
                continue

            score = similarity_matrix[src_idx, tgt_idx]
            if score < self.min_score:
                break

            src_text = source[src_idx]
            tgt_text = target[tgt_idx]

            # Check length ratio
            if not self._valid_length_ratio(src_text, tgt_text):
                continue

            pairs.append(ParallelPair(
                source_text=src_text,
                target_text=tgt_text,
                alignment_score=float(score),
            ))

            used_source.add(src_idx)
            used_target.add(tgt_idx)

        return pairs

    def _hunalign(
        self,
        source: Sequence[str],
        target: Sequence[str],
    ) -> list[ParallelPair]:
        """
        Dictionary-based alignment using Gaois terminology.

        Falls back to vecalign for sentences without dictionary matches.
        """
        if not source or not target:
            return []

        # Load Gaois dictionary if not loaded
        if self._gaois_dict is None:
            self._gaois_dict = self._load_gaois_dictionary()

        pairs = []
        used_target = set()

        for src_text in source:
            src_terms = self._extract_terms(src_text)

            best_match = None
            best_score = 0.0

            for tgt_idx, tgt_text in enumerate(target):
                if tgt_idx in used_target:
                    continue

                # Count dictionary term matches
                tgt_terms = self._extract_terms(tgt_text)
                matches = self._count_term_matches(src_terms, tgt_terms)

                if matches > 0:
                    score = matches / max(len(src_terms), len(tgt_terms), 1)
                    if score > best_score:
                        best_score = score
                        best_match = (tgt_idx, tgt_text)

            if best_match and best_score >= 0.3:  # Lower threshold for dict matching
                tgt_idx, tgt_text = best_match
                pairs.append(ParallelPair(
                    source_text=src_text,
                    target_text=tgt_text,
                    alignment_score=best_score,
                    metadata={"method": "dictionary"},
                ))
                used_target.add(tgt_idx)

        return pairs

    def _gaoisalign(
        self,
        source: Sequence[str],
        target: Sequence[str],
    ) -> list[ParallelPair]:
        """
        Irish-specific alignment using Gaois API patterns.

        Optimized for educational terminology and curriculum content.
        """
        # For now, delegate to hybrid which combines dict + neural
        return self._hybrid_align(source, target)

    def _hybrid_align(
        self,
        source: Sequence[str],
        target: Sequence[str],
    ) -> list[ParallelPair]:
        """
        Combine dictionary and neural alignment.

        1. First pass: dictionary alignment for high-confidence matches
        2. Second pass: neural alignment for remaining sentences
        """
        dict_pairs = self._hunalign(source, target)

        # Get unaligned sentences
        aligned_source = {p.source_text for p in dict_pairs}
        aligned_target = {p.target_text for p in dict_pairs}

        remaining_source = [s for s in source if s not in aligned_source]
        remaining_target = [t for t in target if t not in aligned_target]

        # Neural alignment for remaining
        if remaining_source and remaining_target:
            neural_pairs = self._vecalign(remaining_source, remaining_target)
            for p in neural_pairs:
                p.metadata["method"] = "neural"
            dict_pairs.extend(neural_pairs)

        return dict_pairs

    def _batch_embed(self, texts: list[str]) -> np.ndarray:
        """
        Batch embed texts for performance.

        CRITICAL: Batching provides 100x speedup over individual calls.
        """
        if not texts:
            return np.array([])

        # Process in batches
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            embeddings = self.model.encode(
                batch,
                convert_to_numpy=True,
                show_progress_bar=False,
                batch_size=self.batch_size,
            )
            all_embeddings.append(embeddings)

        return np.vstack(all_embeddings) if all_embeddings else np.array([])

    def _cosine_similarity_matrix(
        self,
        embeddings_a: np.ndarray,
        embeddings_b: np.ndarray,
    ) -> np.ndarray:
        """Compute cosine similarity matrix between two sets of embeddings."""
        # Normalize
        norm_a = embeddings_a / np.linalg.norm(embeddings_a, axis=1, keepdims=True)
        norm_b = embeddings_b / np.linalg.norm(embeddings_b, axis=1, keepdims=True)

        return np.dot(norm_a, norm_b.T)

    def _valid_length_ratio(self, source: str, target: str) -> bool:
        """Check if length ratio is within acceptable bounds."""
        src_len = len(source.split())
        tgt_len = len(target.split())

        if src_len == 0 or tgt_len == 0:
            return False

        ratio = src_len / tgt_len
        return self.MIN_LENGTH_RATIO <= ratio <= self.MAX_LENGTH_RATIO

    def _segment_sentences(self, text: str, lang: str = "en") -> list[str]:
        """Segment text into sentences."""
        # Basic sentence segmentation
        # TODO: Use spaCy or stanza for better segmentation
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def _extract_terms(self, text: str) -> set[str]:
        """Extract terms from text for dictionary matching."""
        # Normalize and tokenize
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        return set(words)

    def _count_term_matches(
        self,
        source_terms: set[str],
        target_terms: set[str],
    ) -> int:
        """Count dictionary matches between term sets."""
        if self._gaois_dict is None:
            return 0

        matches = 0
        for src_term in source_terms:
            if src_term in self._gaois_dict:
                ga_term = self._gaois_dict[src_term]
                if ga_term.lower() in target_terms:
                    matches += 1

        return matches

    def _load_gaois_dictionary(self) -> dict[str, str]:
        """
        Load Gaois English-Irish dictionary.

        TODO: Integrate with Téarma.ie API for live lookups.
        """
        # Placeholder with common educational terms
        # In production, load from Téarma.ie or local cache
        return {
            "curriculum": "curaclam",
            "education": "oideachas",
            "learning": "foghlaim",
            "student": "mac léinn",
            "teacher": "múinteoir",
            "school": "scoil",
            "subject": "ábhar",
            "mathematics": "matamaitic",
            "science": "eolaíocht",
            "history": "stair",
            "geography": "tíreolaíocht",
            "language": "teanga",
            "irish": "gaeilge",
            "english": "béarla",
            "assessment": "measúnú",
            "examination": "scrúdú",
            "primary": "bunscoile",
            "secondary": "meánscoile",
            "junior": "sóisearach",
            "senior": "sinsearach",
            "leaving": "ardteistiméireacht",
            "certificate": "teastas",
            "level": "leibhéal",
            "higher": "ardleibhéal",
            "ordinary": "gnáthleibhéal",
            "foundation": "bonnleibhéal",
            "objective": "cuspóir",
            "outcome": "toradh",
            "skill": "scil",
            "knowledge": "eolas",
            "understanding": "tuiscint",
        }


def align_parallel_texts(
    english_texts: Sequence[str],
    irish_texts: Sequence[str],
    method: AlignmentMethod = AlignmentMethod.VECALIGN,
    min_score: float = 0.7,
) -> Iterator[ParallelPair]:
    """
    Convenience function for aligning parallel texts.

    Args:
        english_texts: List of English sentences/paragraphs
        irish_texts: List of Irish sentences/paragraphs
        method: Alignment method to use
        min_score: Minimum alignment score threshold

    Yields:
        ParallelPair objects for each aligned pair
    """
    aligner = IrishEnglishAligner(method=method, min_score=min_score)
    result = aligner.align(english_texts, irish_texts)

    yield from result.pairs
