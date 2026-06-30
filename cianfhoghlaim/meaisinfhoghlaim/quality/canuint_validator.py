"""
Quality validation for Canuint.ie alignment dataset.

Validates:
- Audio-transcript alignment consistency
- Duration distribution and filtering
- Phoneme inventory coverage
- Dialect balance analysis
- Speaker diversity metrics
- Train/val/test split generation

Reports quality issues for review before training.
"""
from __future__ import annotations

import json
import random
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from sruth.oideachais.observability.logging import get_logger

logger = get_logger(__name__)


# Irish phoneme inventory (IPA) for coverage analysis
# Based on: https://en.wikipedia.org/wiki/Irish_phonology
IRISH_PHONEME_INVENTORY = {
    # Consonants - broad (velarized)
    "pˠ", "bˠ", "t̪ˠ", "d̪ˠ", "k", "ɡ",  # stops
    "fˠ", "sˠ", "x", "h",  # fricatives
    "mˠ", "n̪ˠ", "ŋ",  # nasals
    "l̪ˠ", "ɾˠ",  # liquids
    "w",  # approximants

    # Consonants - slender (palatalized)
    "pʲ", "bʲ", "tʲ", "dʲ", "c", "ɟ",  # stops
    "fʲ", "ʃ", "ç", # fricatives
    "mʲ", "nʲ", "ɲ",  # nasals
    "lʲ", "ɾʲ",  # liquids
    "j",  # approximants

    # Additional fricatives
    "ɣ", "ʝ", "v",

    # Vowels - short
    "a", "ɛ", "ɪ", "ɔ", "ʊ", "ə",

    # Vowels - long
    "ɑː", "aː", "eː", "iː", "oː", "uː", "æː",

    # Diphthongs
    "iə", "uə", "əi", "əu",
}

# Minimum expected coverage by dialect
MIN_PHONEME_COVERAGE = {
    "connacht": 0.70,  # 70% of inventory
    "munster": 0.70,
    "ulster": 0.65,  # Ulster has some distinct phonemes
}


@dataclass
class ValidationResult:
    """Results from validation check."""

    name: str
    passed: bool
    score: float = 1.0
    issues: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "score": self.score,
            "issues": self.issues[:100],  # Limit issues for report
            "issue_count": len(self.issues),
            "metadata": self.metadata,
        }


@dataclass
class ValidationReport:
    """Complete validation report."""

    total_items: int = 0
    passed_items: int = 0
    results: list = field(default_factory=list)
    overall_score: float = 0.0
    recommendations: list = field(default_factory=list)

    def add_result(self, result: ValidationResult):
        self.results.append(result)

    def compute_overall_score(self):
        if not self.results:
            self.overall_score = 0.0
            return

        weights = {
            "duration": 1.0,
            "alignment": 1.5,
            "phoneme_coverage": 1.0,
            "dialect_balance": 1.0,
            "speaker_diversity": 0.5,
        }

        total_weight = 0
        weighted_sum = 0

        for result in self.results:
            weight = weights.get(result.name, 1.0)
            weighted_sum += result.score * weight
            total_weight += weight

        self.overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "total_items": self.total_items,
            "passed_items": self.passed_items,
            "overall_score": round(self.overall_score, 3),
            "results": [r.to_dict() for r in self.results],
            "recommendations": self.recommendations,
        }


# ============================================================================
# Validation Functions
# ============================================================================

def validate_duration_distribution(
    alignments: list[dict],
    min_duration_ms: int = 50,
    max_duration_ms: int = 5000,
    target_mean_ms: int = 500,
    target_std_ms: int = 300,
) -> ValidationResult:
    """
    Validate duration distribution of word alignments.

    Checks:
    - All durations within valid range
    - Mean duration reasonable
    - Standard deviation not too high (outliers)
    - No suspiciously uniform durations (data issue)
    """
    issues = []
    durations = []

    for alignment in alignments:
        duration_ms = alignment.get("duration_ms") or (
            (alignment.get("end_time", 0) - alignment.get("start_time", 0)) * 1000
        )
        durations.append(duration_ms)

        word_id = alignment.get("word_id", "unknown")

        if duration_ms < min_duration_ms:
            issues.append(f"{word_id}: too short ({duration_ms}ms < {min_duration_ms}ms)")
        elif duration_ms > max_duration_ms:
            issues.append(f"{word_id}: too long ({duration_ms}ms > {max_duration_ms}ms)")

    if not durations:
        return ValidationResult(
            name="duration",
            passed=False,
            score=0.0,
            issues=["No durations to validate"],
        )

    # Calculate statistics
    mean_duration = sum(durations) / len(durations)
    variance = sum((d - mean_duration) ** 2 for d in durations) / len(durations)
    std_duration = variance ** 0.5

    # Score based on how close to target distribution
    mean_score = max(0, 1 - abs(mean_duration - target_mean_ms) / target_mean_ms)
    std_score = max(0, 1 - abs(std_duration - target_std_ms) / target_std_ms)
    range_score = 1 - (len(issues) / len(durations)) if durations else 0

    score = (mean_score + std_score + range_score) / 3

    return ValidationResult(
        name="duration",
        passed=len(issues) < len(durations) * 0.1,  # <10% issues
        score=score,
        issues=issues,
        metadata={
            "count": len(durations),
            "mean_ms": round(mean_duration, 1),
            "std_ms": round(std_duration, 1),
            "min_ms": min(durations),
            "max_ms": max(durations),
            "out_of_range_count": len(issues),
        },
    )


def validate_alignment_consistency(
    alignments: list[dict],
    max_gap_ms: float = 100,
    max_overlap_ms: float = 50,
) -> ValidationResult:
    """
    Validate that alignments don't have gaps or overlaps.

    Groups by recording and checks sequential words.
    """
    issues = []

    # Group by recording
    by_recording = {}
    for alignment in alignments:
        rec_id = alignment.get("recording_id", "")
        if rec_id not in by_recording:
            by_recording[rec_id] = []
        by_recording[rec_id].append(alignment)

    total_pairs = 0
    good_pairs = 0

    for rec_id, words in by_recording.items():
        # Sort by start time
        words = sorted(words, key=lambda x: x.get("start_time", 0))

        for i in range(1, len(words)):
            prev_end = words[i - 1].get("end_time", 0)
            curr_start = words[i].get("start_time", 0)

            gap_ms = (curr_start - prev_end) * 1000
            total_pairs += 1

            if gap_ms > max_gap_ms:
                issues.append(
                    f"{rec_id}: gap of {gap_ms:.1f}ms between words {i-1} and {i}"
                )
            elif gap_ms < -max_overlap_ms:
                issues.append(
                    f"{rec_id}: overlap of {-gap_ms:.1f}ms between words {i-1} and {i}"
                )
            else:
                good_pairs += 1

    score = good_pairs / total_pairs if total_pairs > 0 else 0.0

    return ValidationResult(
        name="alignment",
        passed=score >= 0.95,
        score=score,
        issues=issues,
        metadata={
            "recordings_checked": len(by_recording),
            "word_pairs_checked": total_pairs,
            "consistent_pairs": good_pairs,
            "gap_issues": sum(1 for i in issues if "gap" in i),
            "overlap_issues": sum(1 for i in issues if "overlap" in i),
        },
    )


def validate_phoneme_coverage(
    phoneme_alignments: list[dict],
    min_coverage: float = 0.7,
) -> ValidationResult:
    """
    Validate coverage of Irish phoneme inventory.

    Checks that dataset covers sufficient phoneme diversity.
    """
    observed_phonemes = set()
    phoneme_counts = Counter()

    for alignment in phoneme_alignments:
        phonemes = alignment.get("phonemes", [])
        for phoneme in phonemes:
            # Normalize phoneme (remove stress marks for counting)
            clean = phoneme.strip("ˈˌ")
            observed_phonemes.add(clean)
            phoneme_counts[clean] += 1

    # Calculate coverage
    inventory_size = len(IRISH_PHONEME_INVENTORY)
    covered = len(observed_phonemes.intersection(IRISH_PHONEME_INVENTORY))
    coverage = covered / inventory_size if inventory_size > 0 else 0

    # Find missing phonemes
    missing = IRISH_PHONEME_INVENTORY - observed_phonemes

    # Find rare phonemes (<10 occurrences)
    rare = [p for p, c in phoneme_counts.items() if c < 10]

    issues = []
    if coverage < min_coverage:
        issues.append(f"Coverage {coverage:.1%} below minimum {min_coverage:.1%}")

    for phoneme in list(missing)[:20]:
        issues.append(f"Missing phoneme: {phoneme}")

    return ValidationResult(
        name="phoneme_coverage",
        passed=coverage >= min_coverage,
        score=coverage,
        issues=issues,
        metadata={
            "total_phonemes_observed": len(observed_phonemes),
            "inventory_size": inventory_size,
            "coverage_ratio": round(coverage, 3),
            "missing_count": len(missing),
            "rare_phonemes": rare[:20],
            "top_phonemes": dict(phoneme_counts.most_common(20)),
        },
    )


def validate_dialect_balance(
    alignments: list[dict],
    target_ratio: float = 0.33,  # Equal distribution
    tolerance: float = 0.1,
) -> ValidationResult:
    """
    Validate balance across Irish dialects.

    Target: roughly equal representation of Connacht, Munster, Ulster.
    """
    dialect_counts = Counter()

    for alignment in alignments:
        dialect = alignment.get("dialect", "unknown").lower()
        dialect_counts[dialect] += 1

    total = sum(dialect_counts.values())
    issues = []

    if total == 0:
        return ValidationResult(
            name="dialect_balance",
            passed=False,
            score=0.0,
            issues=["No dialect information found"],
        )

    # Calculate ratios
    expected_dialects = {"connacht", "munster", "ulster"}
    dialect_ratios = {}

    for dialect in expected_dialects:
        count = dialect_counts.get(dialect, 0)
        ratio = count / total
        dialect_ratios[dialect] = ratio

        if ratio < target_ratio - tolerance:
            issues.append(f"{dialect}: underrepresented ({ratio:.1%} vs target {target_ratio:.1%})")
        elif ratio > target_ratio + tolerance:
            issues.append(f"{dialect}: overrepresented ({ratio:.1%} vs target {target_ratio:.1%})")

    # Check for unknown/missing dialects
    unknown = dialect_counts.get("unknown", 0) + dialect_counts.get("", 0)
    if unknown > total * 0.05:
        issues.append(f"{unknown} items ({unknown/total:.1%}) have unknown dialect")

    # Score: average deviation from target
    deviations = [abs(ratio - target_ratio) for ratio in dialect_ratios.values()]
    avg_deviation = sum(deviations) / len(deviations) if deviations else 0
    score = max(0, 1 - avg_deviation / target_ratio)

    return ValidationResult(
        name="dialect_balance",
        passed=len(issues) == 0,
        score=score,
        issues=issues,
        metadata={
            "total_items": total,
            "dialect_counts": dict(dialect_counts),
            "dialect_ratios": {k: round(v, 3) for k, v in dialect_ratios.items()},
            "target_ratio": target_ratio,
        },
    )


def validate_speaker_diversity(
    alignments: list[dict],
    min_speakers: int = 10,
    max_speaker_ratio: float = 0.3,
) -> ValidationResult:
    """
    Validate speaker diversity in dataset.

    Checks:
    - Minimum number of unique speakers
    - No single speaker dominates dataset
    """
    speaker_counts = Counter()

    for alignment in alignments:
        speaker = alignment.get("speaker_name", "unknown")
        speaker_counts[speaker] += 1

    total = sum(speaker_counts.values())
    unique_speakers = len(speaker_counts)

    issues = []

    if unique_speakers < min_speakers:
        issues.append(f"Only {unique_speakers} speakers (minimum: {min_speakers})")

    # Check for dominant speakers
    for speaker, count in speaker_counts.most_common(5):
        ratio = count / total
        if ratio > max_speaker_ratio:
            issues.append(f"Speaker '{speaker}' has {ratio:.1%} of data (max: {max_speaker_ratio:.1%})")

    # Score based on speaker count and distribution
    speaker_score = min(1.0, unique_speakers / min_speakers)
    top_ratio = speaker_counts.most_common(1)[0][1] / total if speaker_counts else 1.0
    distribution_score = 1 - top_ratio

    score = (speaker_score + distribution_score) / 2

    return ValidationResult(
        name="speaker_diversity",
        passed=len(issues) == 0,
        score=score,
        issues=issues,
        metadata={
            "total_items": total,
            "unique_speakers": unique_speakers,
            "top_speakers": dict(speaker_counts.most_common(10)),
            "speaker_ratio_top": round(top_ratio, 3),
        },
    )


def validate_text_quality(
    alignments: list[dict],
    min_text_length: int = 1,
    max_text_length: int = 100,
) -> ValidationResult:
    """
    Validate text content quality.

    Checks:
    - Non-empty text
    - Reasonable length
    - Irish character support (fadas)
    - No suspicious patterns
    """
    issues = []
    fada_count = 0
    total = 0

    for alignment in alignments:
        text = alignment.get("dialectal_text", "") or alignment.get("text", "")
        word_id = alignment.get("word_id", "unknown")
        total += 1

        if not text or len(text.strip()) < min_text_length:
            issues.append(f"{word_id}: empty or too short text")
            continue

        if len(text) > max_text_length:
            issues.append(f"{word_id}: text too long ({len(text)} chars)")

        # Check for fada vowels (Irish-specific)
        if any(c in text for c in "áéíóúÁÉÍÓÚ"):
            fada_count += 1

    # Score based on valid texts and Irish character usage
    valid_ratio = 1 - (len(issues) / total) if total > 0 else 0
    fada_ratio = fada_count / total if total > 0 else 0

    # Irish text should have ~20-40% words with fadas
    fada_score = min(1.0, fada_ratio / 0.2)  # Normalize to expected ratio

    score = (valid_ratio * 0.7) + (fada_score * 0.3)

    return ValidationResult(
        name="text_quality",
        passed=valid_ratio >= 0.95,
        score=score,
        issues=issues,
        metadata={
            "total_items": total,
            "valid_items": total - len(issues),
            "fada_ratio": round(fada_ratio, 3),
            "issue_count": len(issues),
        },
    )


# ============================================================================
# Train/Val/Test Split Generation
# ============================================================================

def generate_splits(
    alignments: list[dict],
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    random_seed: int = 42,
    stratify_by: str = "dialect",
) -> dict:
    """
    Generate train/val/test splits with optional stratification.

    Args:
        alignments: List of alignment dicts
        train_ratio: Proportion for training (default 80%)
        val_ratio: Proportion for validation (default 10%)
        test_ratio: Proportion for testing (default 10%)
        random_seed: Random seed for reproducibility
        stratify_by: Field to stratify by (dialect, speaker_name, etc.)

    Returns:
        Dict with train/val/test lists of word_ids
    """
    random.seed(random_seed)

    # Group by stratification field
    groups = {}
    for alignment in alignments:
        key = alignment.get(stratify_by, "unknown")
        if key not in groups:
            groups[key] = []
        groups[key].append(alignment.get("word_id"))

    splits = {"train": [], "val": [], "test": []}

    for _group_key, word_ids in groups.items():
        random.shuffle(word_ids)
        n = len(word_ids)

        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))

        splits["train"].extend(word_ids[:train_end])
        splits["val"].extend(word_ids[train_end:val_end])
        splits["test"].extend(word_ids[val_end:])

    # Shuffle final lists
    for split in splits.values():
        random.shuffle(split)

    return splits


def export_splits(
    splits: dict,
    output_dir: Path,
) -> dict:
    """
    Export train/val/test splits to files.

    Creates:
    - train.txt: List of word_ids for training
    - val.txt: List of word_ids for validation
    - test.txt: List of word_ids for testing
    - splits.json: Complete split information
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    stats = {}
    for split_name, word_ids in splits.items():
        # Write list file
        list_path = output_dir / f"{split_name}.txt"
        with open(list_path, "w", encoding="utf-8") as f:
            for word_id in word_ids:
                f.write(f"{word_id}\n")

        stats[split_name] = len(word_ids)

    # Write JSON with full info
    json_path = output_dir / "splits.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "splits": {k: list(v) for k, v in splits.items()},
            "counts": stats,
            "ratios": {
                k: v / sum(stats.values())
                for k, v in stats.items()
            },
        }, f, indent=2)

    logger.info("splits_exported",
                output_dir=str(output_dir),
                train=stats.get("train", 0),
                val=stats.get("val", 0),
                test=stats.get("test", 0))

    return stats


# ============================================================================
# Main Validation Pipeline
# ============================================================================

def validate_canuint_dataset(
    word_alignments: list[dict],
    character_alignments: list[dict] | None = None,
    phoneme_alignments: list[dict] | None = None,
    output_dir: Path | None = None,
) -> ValidationReport:
    """
    Run complete validation suite on Canuint dataset.

    Args:
        word_alignments: List of word alignment dicts
        character_alignments: Optional character alignments
        phoneme_alignments: Optional phoneme alignments
        output_dir: Directory for validation report and splits

    Returns:
        ValidationReport with all results
    """
    report = ValidationReport(total_items=len(word_alignments))

    logger.info("starting_validation", total_items=len(word_alignments))

    # Run validation checks
    report.add_result(validate_duration_distribution(word_alignments))
    report.add_result(validate_alignment_consistency(word_alignments))
    report.add_result(validate_dialect_balance(word_alignments))
    report.add_result(validate_speaker_diversity(word_alignments))
    report.add_result(validate_text_quality(word_alignments))

    if phoneme_alignments:
        report.add_result(validate_phoneme_coverage(phoneme_alignments))

    # Count passed items
    passed = sum(1 for a in word_alignments
                 if a.get("duration_ms", 0) >= 50 and a.get("duration_ms", 0) <= 5000)
    report.passed_items = passed

    # Compute overall score
    report.compute_overall_score()

    # Generate recommendations
    for result in report.results:
        if not result.passed:
            if result.name == "duration":
                report.recommendations.append(
                    "Consider filtering extreme duration outliers"
                )
            elif result.name == "dialect_balance":
                report.recommendations.append(
                    "Dataset is imbalanced; consider augmentation or re-sampling"
                )
            elif result.name == "phoneme_coverage":
                report.recommendations.append(
                    "Some phonemes underrepresented; may affect model generalization"
                )
            elif result.name == "speaker_diversity":
                report.recommendations.append(
                    "Limited speaker diversity; consider speaker normalization"
                )

    # Export report and splits
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write report
        report_path = output_dir / "validation_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)

        # Generate and export splits
        splits = generate_splits(word_alignments)
        splits_dir = output_dir / "splits"
        export_splits(splits, splits_dir)

        logger.info("validation_complete",
                    output_dir=str(output_dir),
                    overall_score=report.overall_score,
                    passed=report.passed_items,
                    total=report.total_items)

    return report


def load_and_validate(
    word_alignments_path: Path,
    phoneme_alignments_path: Path | None = None,
    output_dir: Path | None = None,
) -> ValidationReport:
    """
    Load alignments from JSONL files and run validation.

    Convenience function for command-line usage.
    """
    # Load word alignments
    word_alignments = []
    with open(word_alignments_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                word_alignments.append(json.loads(line))

    # Load phoneme alignments if provided
    phoneme_alignments = None
    if phoneme_alignments_path and phoneme_alignments_path.exists():
        phoneme_alignments = []
        with open(phoneme_alignments_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    phoneme_alignments.append(json.loads(line))

    return validate_canuint_dataset(
        word_alignments=word_alignments,
        phoneme_alignments=phoneme_alignments,
        output_dir=output_dir,
    )
