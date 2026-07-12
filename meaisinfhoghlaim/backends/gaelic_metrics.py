"""
Gaelic-Specific OCR Evaluation Metrics.

Provides metrics tailored for Irish handwriting recognition:
- Character Error Rate (CER) with Unicode normalization
- Word Error Rate (WER)
- Tironian et accuracy
- Punctum delens (lenition) precision
- Fada (accent) accuracy

Based on research in:
- taighde_teanga/Finetuning Qwen3-VL for Gaelic OCR.md
- taighde_new/document-intelligence-ocr.md

Usage:
    from cianfhoghlaim.ocr import GaelicMetrics, calculate_cer, calculate_wer

    metrics = GaelicMetrics()
    result = metrics.evaluate(prediction, reference)
    print(f"CER: {result['cer']:.2%}, Tironian: {result['tironian_accuracy']:.2%}")
"""

import unicodedata
from dataclasses import dataclass
from typing import Any


def _normalize_irish_text(text: str) -> str:
    """
    Normalize Irish text for comparison.

    - Unicode normalization (NFC)
    - Lowercase
    - Normalize whitespace
    - Handle common OCR confusions
    """
    # Unicode normalization
    text = unicodedata.normalize("NFC", text)

    # Lowercase
    text = text.lower()

    # Normalize whitespace
    text = " ".join(text.split())

    # Common OCR substitutions
    substitutions = {
        "⁊": "agus",  # Tironian et to word (optional)
        "7": "⁊",  # Common OCR confusion
        "'": "'",
        "'": "'",
        """: '"',
        """: '"',
        "—": "-",
        "–": "-",
    }

    for old, new in substitutions.items():
        text = text.replace(old, new)

    return text


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein edit distance."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def calculate_cer(prediction: str, reference: str, normalize: bool = True) -> float:
    """
    Calculate Character Error Rate.

    CER = (insertions + deletions + substitutions) / reference_length

    Args:
        prediction: OCR output
        reference: Ground truth
        normalize: Whether to normalize Irish text

    Returns:
        CER value (0.0 = perfect, 1.0+ = very bad)
    """
    if normalize:
        prediction = _normalize_irish_text(prediction)
        reference = _normalize_irish_text(reference)

    if len(reference) == 0:
        return 0.0 if len(prediction) == 0 else 1.0

    distance = _levenshtein_distance(prediction, reference)
    return distance / len(reference)


def calculate_wer(prediction: str, reference: str, normalize: bool = True) -> float:
    """
    Calculate Word Error Rate.

    WER = (word_insertions + word_deletions + word_substitutions) / reference_word_count

    Args:
        prediction: OCR output
        reference: Ground truth
        normalize: Whether to normalize Irish text

    Returns:
        WER value (0.0 = perfect)
    """
    if normalize:
        prediction = _normalize_irish_text(prediction)
        reference = _normalize_irish_text(reference)

    pred_words = prediction.split()
    ref_words = reference.split()

    if len(ref_words) == 0:
        return 0.0 if len(pred_words) == 0 else 1.0

    distance = _levenshtein_distance(pred_words, ref_words)
    return distance / len(ref_words)


@dataclass
class GaelicEvaluationResult:
    """Result of Gaelic OCR evaluation."""

    cer: float
    wer: float
    tironian_accuracy: float
    punctum_delens_precision: float
    fada_accuracy: float
    char_accuracy: float
    word_accuracy: float
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cer": self.cer,
            "wer": self.wer,
            "tironian_accuracy": self.tironian_accuracy,
            "punctum_delens_precision": self.punctum_delens_precision,
            "fada_accuracy": self.fada_accuracy,
            "char_accuracy": self.char_accuracy,
            "word_accuracy": self.word_accuracy,
            "details": self.details,
        }


class GaelicMetrics:
    """
    Gaelic-specific OCR evaluation metrics.
    """

    # Characters with lenition marks (punctum delens)
    LENITED_CHARS = set("ḃċḋḟġṁṗṡṫḂĊḊḞĠṀṖṠṪ")

    # Vowels with síneadh fada
    FADA_CHARS = set("áéíóúÁÉÍÓÚ")

    # Tironian et variants
    TIRONIAN_VARIANTS = {"⁊", "7", "&"}

    def __init__(
        self,
        normalize_tironian: bool = False,
        case_sensitive: bool = False,
    ):
        """
        Initialize metrics calculator.

        Args:
            normalize_tironian: Convert ⁊ to "agus" before comparison
            case_sensitive: Whether comparison is case-sensitive
        """
        self.normalize_tironian = normalize_tironian
        self.case_sensitive = case_sensitive

    def evaluate(
        self,
        prediction: str,
        reference: str,
    ) -> GaelicEvaluationResult:
        """
        Comprehensive evaluation of OCR output.

        Args:
            prediction: OCR output
            reference: Ground truth

        Returns:
            GaelicEvaluationResult with all metrics
        """
        # Basic metrics
        cer = calculate_cer(prediction, reference)
        wer = calculate_wer(prediction, reference)

        # Gaelic-specific metrics
        tironian = self._evaluate_tironian(prediction, reference)
        punctum = self._evaluate_punctum_delens(prediction, reference)
        fada = self._evaluate_fada(prediction, reference)

        # Accuracy metrics
        char_accuracy = 1.0 - cer
        word_accuracy = 1.0 - wer

        details = {
            "prediction_length": len(prediction),
            "reference_length": len(reference),
            "prediction_words": len(prediction.split()),
            "reference_words": len(reference.split()),
            "tironian_details": tironian,
            "punctum_details": punctum,
            "fada_details": fada,
        }

        return GaelicEvaluationResult(
            cer=cer,
            wer=wer,
            tironian_accuracy=tironian["accuracy"],
            punctum_delens_precision=punctum["precision"],
            fada_accuracy=fada["accuracy"],
            char_accuracy=char_accuracy,
            word_accuracy=word_accuracy,
            details=details,
        )

    def _evaluate_tironian(
        self, prediction: str, reference: str
    ) -> dict[str, Any]:
        """Evaluate Tironian et (⁊) recognition."""
        # Count Tironian et in reference
        ref_count = sum(1 for c in reference if c in self.TIRONIAN_VARIANTS)

        if ref_count == 0:
            return {
                "accuracy": 1.0,
                "reference_count": 0,
                "prediction_count": 0,
                "correct": 0,
            }

        # Count in prediction
        pred_count = sum(1 for c in prediction if c in self.TIRONIAN_VARIANTS)

        # Simple accuracy: ratio of counts
        if pred_count == 0:
            accuracy = 0.0
        else:
            accuracy = min(pred_count, ref_count) / ref_count

        return {
            "accuracy": accuracy,
            "reference_count": ref_count,
            "prediction_count": pred_count,
            "correct": min(pred_count, ref_count),
        }

    def _evaluate_punctum_delens(
        self, prediction: str, reference: str
    ) -> dict[str, Any]:
        """Evaluate punctum delens (lenition dot) recognition."""
        # Count lenited characters in reference
        ref_lenited = set()
        for i, c in enumerate(reference):
            if c in self.LENITED_CHARS:
                ref_lenited.add((i, c))

        if not ref_lenited:
            return {
                "precision": 1.0,
                "recall": 1.0,
                "f1": 1.0,
                "reference_count": 0,
                "prediction_count": 0,
            }

        # Count in prediction
        pred_lenited = set()
        for i, c in enumerate(prediction):
            if c in self.LENITED_CHARS:
                pred_lenited.add((i, c))

        # Calculate precision, recall, F1
        # This is approximate since positions may shift
        ref_chars = {c for _, c in ref_lenited}
        pred_chars = {c for _, c in pred_lenited}

        true_positives = len(ref_chars & pred_chars)
        precision = true_positives / len(pred_chars) if pred_chars else 0.0
        recall = true_positives / len(ref_chars) if ref_chars else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "reference_count": len(ref_lenited),
            "prediction_count": len(pred_lenited),
        }

    def _evaluate_fada(
        self, prediction: str, reference: str
    ) -> dict[str, Any]:
        """Evaluate síneadh fada (accent) recognition."""
        # Count fada in reference
        ref_fada = sum(1 for c in reference if c in self.FADA_CHARS)

        if ref_fada == 0:
            return {
                "accuracy": 1.0,
                "reference_count": 0,
                "prediction_count": 0,
                "correct": 0,
            }

        # Count in prediction
        pred_fada = sum(1 for c in prediction if c in self.FADA_CHARS)

        # Count matching fada (character-level)
        ref_lower = reference.lower()
        pred_lower = prediction.lower()

        correct = 0
        for fada in ["á", "é", "í", "ó", "ú"]:
            ref_count = ref_lower.count(fada)
            pred_count = pred_lower.count(fada)
            correct += min(ref_count, pred_count)

        accuracy = correct / ref_fada if ref_fada > 0 else 1.0

        return {
            "accuracy": accuracy,
            "reference_count": ref_fada,
            "prediction_count": pred_fada,
            "correct": correct,
        }

    def batch_evaluate(
        self,
        predictions: list[str],
        references: list[str],
    ) -> dict[str, float]:
        """
        Evaluate batch of predictions.

        Args:
            predictions: List of OCR outputs
            references: List of ground truths

        Returns:
            Aggregated metrics
        """
        if len(predictions) != len(references):
            raise ValueError("Predictions and references must have same length")

        results = [
            self.evaluate(pred, ref) for pred, ref in zip(predictions, references)
        ]

        n = len(results)
        return {
            "mean_cer": sum(r.cer for r in results) / n,
            "mean_wer": sum(r.wer for r in results) / n,
            "mean_tironian_accuracy": sum(r.tironian_accuracy for r in results) / n,
            "mean_punctum_precision": sum(r.punctum_delens_precision for r in results) / n,
            "mean_fada_accuracy": sum(r.fada_accuracy for r in results) / n,
            "mean_char_accuracy": sum(r.char_accuracy for r in results) / n,
            "mean_word_accuracy": sum(r.word_accuracy for r in results) / n,
            "sample_count": n,
        }
