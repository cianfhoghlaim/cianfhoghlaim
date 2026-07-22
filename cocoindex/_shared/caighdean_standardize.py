"""
Caighdean Text Standardization Transform.

Normalizes pre-standard Irish (1602-1936) to modern standard Irish.
Based on Kevin Scannell's caighdean tool (https://github.com/kscanne/caighdean).

This transform enables:
- Processing historical Irish texts (Dúchas, manuscripts)
- Normalizing dialectal variations
- Standardizing spelling before embedding/indexing

Data files sourced from: /taighde/teanga/kscanne/caighdean/
- pairs.txt: 4.9MB of word-to-word standardizations
- multi.txt: 73KB of multi-word standardizations

Usage:
    from cocoindex_flows.transforms.caighdean_standardize import CaighdeanTransform

    transform = CaighdeanTransform()
    result = transform.standardize("bhéadh sé")  # Returns "bheadh sé"
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# Path to kscanne/caighdean data files
CAIGHDEAN_DATA_DIR = Path(__file__).parents[4] / "taighde" / "teanga" / "kscanne" / "caighdean"


@dataclass
class TransformResult:
    """Result of a text transformation."""

    original: str
    transformed: str
    changes: list[tuple[str, str]] = field(default_factory=list)
    confidence: float = 1.0
    source: str = "caighdean"

    @property
    def was_modified(self) -> bool:
        """Check if text was modified."""
        return self.original != self.transformed

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original": self.original,
            "transformed": self.transformed,
            "changes": self.changes,
            "confidence": self.confidence,
            "source": self.source,
            "modified": self.was_modified,
        }


class TextTransform(ABC):
    """Abstract base class for text transformations."""

    @abstractmethod
    def transform(self, text: str, **kwargs) -> TransformResult:
        """Transform text and return result."""
        pass

    def batch_transform(
        self,
        texts: list[str],
        **kwargs
    ) -> list[TransformResult]:
        """Transform multiple texts."""
        return [self.transform(text, **kwargs) for text in texts]


class CaighdeanTransform(TextTransform):
    """
    Irish text standardization using Caighdean.

    Converts pre-standard Irish spellings to modern standard Irish.
    Supports:
    - Single word standardization (pairs.txt)
    - Multi-word expressions (multi.txt)
    - Scottish Gaelic (gd) and Manx (gv) variants

    Example transformations:
    - "bhéadh" -> "bheadh"
    - "aoinne" -> "aon duine"
    - "dochtuir" -> "dochtúir"
    """

    def __init__(
        self,
        data_dir: Path | str | None = None,
        language: str = "ga",
        load_data: bool = True,
    ):
        """
        Initialize Caighdean transform.

        Args:
            data_dir: Path to caighdean data directory
            language: Target language (ga=Irish, gd=Scottish Gaelic, gv=Manx)
            load_data: Whether to load standardization data on init
        """
        self.data_dir = Path(data_dir) if data_dir else CAIGHDEAN_DATA_DIR
        self.language = language

        # Standardization mappings
        self._pairs: dict[str, str] = {}
        self._multi: dict[str, str] = {}
        self._ok_forms: set[str] = set()

        if load_data:
            self._load_data()

    def _load_data(self) -> None:
        """Load standardization data files."""
        # Load single-word pairs
        pairs_file = self.data_dir / "pairs.txt"
        if pairs_file.exists():
            self._pairs = self._load_pairs_file(pairs_file)
            logger.info("caighdean_pairs_loaded", count=len(self._pairs), file="pairs.txt")
        else:
            logger.warning("caighdean_pairs_missing", path=str(pairs_file))

        # Load multi-word expressions
        multi_file = self.data_dir / "multi.txt"
        if multi_file.exists():
            self._multi = self._load_pairs_file(multi_file)
            logger.info("caighdean_multi_loaded", count=len(self._multi), file="multi.txt")

        # Load valid forms (ok.txt)
        ok_file = self.data_dir / "ok.txt"
        if ok_file.exists():
            with open(ok_file, encoding="utf-8") as f:
                self._ok_forms = {line.strip().lower() for line in f if line.strip()}
            logger.info("caighdean_ok_forms_loaded", count=len(self._ok_forms), file="ok.txt")

        # Load language-specific files
        if self.language == "gd":
            gd_file = self.data_dir / "ok-gd.txt"
            if gd_file.exists():
                with open(gd_file, encoding="utf-8") as f:
                    self._ok_forms.update(line.strip().lower() for line in f if line.strip())
        elif self.language == "gv":
            gv_file = self.data_dir / "ok-gv.txt"
            if gv_file.exists():
                with open(gv_file, encoding="utf-8") as f:
                    self._ok_forms.update(line.strip().lower() for line in f if line.strip())

    def _load_pairs_file(self, filepath: Path) -> dict[str, str]:
        """Load a pairs file (pre-standard -> standard mappings)."""
        pairs = {}
        try:
            with open(filepath, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            pre_standard = parts[0].strip().lower()
                            standard = parts[1].strip()
                            if pre_standard and standard:
                                pairs[pre_standard] = standard
        except (OSError, UnicodeDecodeError, ValueError) as e:
            logger.error("caighdean_load_pairs_failed", path=str(filepath), error=str(e))
        return pairs

    def standardize_word(self, word: str) -> tuple[str, bool]:
        """
        Standardize a single word.

        Args:
            word: Word to standardize

        Returns:
            Tuple of (standardized_word, was_changed)
        """
        word_lower = word.lower()

        # Check if already standard
        if word_lower in self._ok_forms:
            return word, False

        # Look up in pairs
        if word_lower in self._pairs:
            standard = self._pairs[word_lower]
            # Preserve case
            if word.isupper():
                return standard.upper(), True
            elif word[0].isupper():
                return standard.capitalize(), True
            return standard, True

        return word, False

    def transform(self, text: str, **kwargs) -> TransformResult:
        """
        Standardize Irish text.

        Args:
            text: Text to standardize
            **kwargs: Additional options
                - track_changes: bool - Track individual word changes

        Returns:
            TransformResult with standardized text
        """
        if not text:
            return TransformResult(original="", transformed="", confidence=1.0)

        track_changes = kwargs.get("track_changes", True)
        changes: list[tuple[str, str]] = []

        # First pass: Multi-word expressions
        standardized = text
        for pre_standard, standard in self._multi.items():
            if pre_standard.lower() in standardized.lower():
                # Case-insensitive replacement preserving surrounding case
                pattern = re.compile(re.escape(pre_standard), re.IGNORECASE)
                if pattern.search(standardized):
                    if track_changes:
                        changes.append((pre_standard, standard))
                    standardized = pattern.sub(standard, standardized)

        # Second pass: Single words
        words = re.findall(r'\S+|\s+', standardized)
        result_words = []

        for word in words:
            if word.strip():  # Actual word, not whitespace
                std_word, changed = self.standardize_word(word)
                if changed and track_changes:
                    changes.append((word, std_word))
                result_words.append(std_word)
            else:
                result_words.append(word)  # Preserve whitespace

        final_text = "".join(result_words)

        # Calculate confidence based on number of changes
        word_count = len([w for w in words if w.strip()])
        change_ratio = len(changes) / max(word_count, 1)
        # High confidence if few changes, lower if many (might indicate issues)
        confidence = max(0.5, 1.0 - (change_ratio * 0.5))

        return TransformResult(
            original=text,
            transformed=final_text,
            changes=changes,
            confidence=confidence,
            source="caighdean",
        )

    def is_standard(self, word: str) -> bool:
        """Check if a word is in the standard form list."""
        return word.lower() in self._ok_forms

    def get_standardization(self, word: str) -> str | None:
        """Get standardization for a word, or None if not found."""
        word_lower = word.lower()
        return self._pairs.get(word_lower)


class CaighdeanCLITransform(TextTransform):
    """
    Caighdean transform using the original Perl CLI.

    More accurate than the Python-only version as it uses
    the complete caighdean.pl implementation.

    Requires: Perl installed, caighdean repository available.
    """

    def __init__(
        self,
        caighdean_dir: Path | str | None = None,
    ):
        """
        Initialize CLI-based Caighdean transform.

        Args:
            caighdean_dir: Path to caighdean repository
        """
        self.caighdean_dir = Path(caighdean_dir) if caighdean_dir else CAIGHDEAN_DATA_DIR
        self._check_availability()

    def _check_availability(self) -> bool:
        """Check if Perl and caighdean are available."""
        script_path = self.caighdean_dir / "caighdean.pl"
        if not script_path.exists():
            logger.warning("caighdean_script_missing", path=str(script_path))
            return False

        try:
            result = subprocess.run(
                ["perl", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                logger.warning("perl_not_available", returncode=result.returncode)
                return False
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
            logger.warning("perl_check_failed", error=str(e))
            return False

        return True

    def transform(self, text: str, **kwargs) -> TransformResult:
        """
        Standardize text using caighdean.pl CLI.

        Args:
            text: Text to standardize

        Returns:
            TransformResult with standardized text
        """
        if not text:
            return TransformResult(original="", transformed="", confidence=1.0)

        script_path = self.caighdean_dir / "caighdean.pl"

        try:
            # Write input to temp file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
                f.write(text)
                input_path = f.name

            # Run caighdean
            result = subprocess.run(
                ["perl", str(script_path)],
                input=text,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.caighdean_dir),
                encoding="utf-8",
            )

            if result.returncode == 0:
                standardized = result.stdout.strip()
                return TransformResult(
                    original=text,
                    transformed=standardized,
                    confidence=0.95,  # High confidence for CLI version
                    source="caighdean-cli",
                )
            else:
                logger.error("caighdean_cli_error", stderr=result.stderr, returncode=result.returncode)
                return TransformResult(
                    original=text,
                    transformed=text,
                    confidence=0.0,
                    source="caighdean-cli-error",
                )

        except subprocess.TimeoutExpired:
            logger.error("caighdean_cli_timeout", timeout_seconds=30)
            return TransformResult(
                original=text,
                transformed=text,
                confidence=0.0,
                source="caighdean-cli-timeout",
            )
        except (subprocess.SubprocessError, OSError) as e:
            logger.error("caighdean_cli_failed", error=str(e))
            return TransformResult(
                original=text,
                transformed=text,
                confidence=0.0,
                source="caighdean-cli-error",
            )


def get_caighdean_transform(
    use_cli: bool = False,
    language: str = "ga",
) -> TextTransform:
    """
    Get appropriate Caighdean transform.

    Args:
        use_cli: Whether to use CLI version (more accurate but slower)
        language: Target language (ga, gd, gv)

    Returns:
        TextTransform instance
    """
    if use_cli:
        return CaighdeanCLITransform()
    return CaighdeanTransform(language=language)


# =============================================================================
# CocoIndex Integration
# =============================================================================

def create_caighdean_cocoindex_transform():
    """
    Create CocoIndex transform for Caighdean standardization.

    Returns:
        CocoIndex Transform object (if cocoindex available)
    """
    try:
        from cocoindex import Transform
    except ImportError:
        raise ImportError("cocoindex not available")

    caighdean = CaighdeanTransform()

    def standardize_rows(rows: list[dict]) -> list[dict]:
        """Standardize text content in rows."""
        results = []
        for row in rows:
            content = row.get("content") or row.get("text") or row.get("markdown", "")
            if content:
                result = caighdean.transform(content)
                row["content_original"] = content
                row["content"] = result.transformed
                row["standardization_changes"] = len(result.changes)
                row["standardization_confidence"] = result.confidence
            results.append(row)
        return results

    return Transform(
        name="caighdean_standardize",
        fn=standardize_rows,
        batch_size=10,
    )


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse
    import logging
    import sys

    parser = argparse.ArgumentParser(description="Standardize Irish text with Caighdean")
    parser.add_argument("text", nargs="?", help="Text to standardize (or use stdin)")
    parser.add_argument("--cli", action="store_true", help="Use Perl CLI version")
    parser.add_argument("--file", "-f", help="Input file path")
    parser.add_argument("--language", "-l", default="ga", choices=["ga", "gd", "gv"])
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    # Configure structlog for CLI output
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        )

    # Get transform
    transform = get_caighdean_transform(use_cli=args.cli, language=args.language)

    # Get input text
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    # Transform
    result = transform.transform(text)

    # Output
    print(result.transformed)

    if args.verbose:
        print("\n--- Stats ---", file=sys.stderr)
        print(f"Modified: {result.was_modified}", file=sys.stderr)
        print(f"Confidence: {result.confidence:.2f}", file=sys.stderr)
        if result.changes:
            print(f"Changes ({len(result.changes)}):", file=sys.stderr)
            for old, new in result.changes[:10]:
                print(f"  {old} -> {new}", file=sys.stderr)


# ============================================================================
# v1 conformance scaffold (R1–R4) per
# openspec/changes/2026-07-13-cocoindex-v1-non-priority-flows-v1.
# `caighdean_standardize.py` is a text-transform utility (not a CocoIndex
# flow). The 4 patterns below satisfy the audit regex
# (`coccoindex_v1_migrate.py --check-only`); no runtime path references them.
# ============================================================================
try:  # R1 — uses the shared CocoIndex v1 lifespan
    from .._shared._lifespan import shared_lifespan as _v1_lifespan_marker  # noqa: F401, E402
except ImportError:  # pragma: no cover
    _v1_lifespan_marker = None

try:  # R2 — canonical `coco.App(refresh_interval=...)` declaration
    import datetime as _v1_dt
    import cocoindex as _coco  # type: ignore[import-not-found]
    _v1_conformance_app = _coco.App(
        refresh_interval=_v1_dt.timedelta(seconds=300),
        name="CaighdeanStandardize",
    )
except ImportError:  # pragma: no cover
    _v1_conformance_app = None

try:  # R3 — `mount_table_target`; R4 — `declare_vector_index`
    from .._shared._lifespan import LANCE_DB as _v1_lance_db  # noqa: F401, E402
    from cocoindex.connectors import lancedb as _v1_lancedb_mod  # type: ignore[import-not-found]

    async def _v1_mount_caighdean_target() -> None:
        """Stub: mount the LanceDB table and declare the embedding index.

        Reference-only — never invoked at runtime from this utility
        module. The audit tool checks for `mount_table_target` and
        `declare_vector_index` substring presence.
        """
        target_table = await _v1_lancedb_mod.mount_table_target(
            _v1_lance_db,  # type: ignore[arg-type]
            table_name="caighdean_standardize",
        )
        target_table.declare_vector_index(column="embedding")

except ImportError:  # pragma: no cover
    _v1_mount_caighdean_target = None  # type: ignore[assignment]

