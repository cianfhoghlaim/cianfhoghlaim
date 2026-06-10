"""
Gramadóir Grammar Validation Dagster Asset.

Quality gate for Irish curriculum content using Kevin Scannell's
Gramadóir grammar checker (https://github.com/kscanne/gramadoir).

Usage:
    from dagster_assets.grammar_validation import grammar_validated_curriculum

    @job
    def validate_curriculum():
        grammar_validated_curriculum()
"""


import logging
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Path to gramadoir data files
GRAMADOIR_DATA_DIR = Path(__file__).parents[4] / "taighde" / "teanga" / "kscanne" / "gramadoir"


@dataclass
class GrammarIssue:
    """A single grammar issue detected by Gramadóir."""

    line: int
    column: int
    error_code: str
    message_ga: str
    message_en: str
    context: str
    suggestion: str | None = None
    severity: str = "warning"  # "error", "warning", "info"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "line": self.line,
            "column": self.column,
            "error_code": self.error_code,
            "message_ga": self.message_ga,
            "message_en": self.message_en,
            "context": self.context,
            "suggestion": self.suggestion,
            "severity": self.severity,
        }


@dataclass
class GrammarValidationResult:
    """Result of grammar validation on a text."""

    text: str
    language: str
    issues: list[GrammarIssue] = field(default_factory=list)
    is_valid: bool = True
    error_count: int = 0
    warning_count: int = 0
    source: str = "gramadoir"

    @property
    def has_issues(self) -> bool:
        """Check if any issues were found."""
        return len(self.issues) > 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text_length": len(self.text),
            "language": self.language,
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issue_count": len(self.issues),
            "issues": [issue.to_dict() for issue in self.issues],
            "source": self.source,
        }


class GramadoirValidator:
    """
    Irish grammar validation using Gramadóir.

    Gramadóir checks Irish text for:
    - Spelling errors
    - Grammar errors (mutations, agreement, etc.)
    - Punctuation issues
    - Pre-standard spellings

    Can use either the Perl CLI or pattern-based validation.
    """

    def __init__(
        self,
        gramadoir_dir: Path | str | None = None,
        language: str = "ga",
        use_cli: bool = True,
    ):
        """
        Initialize Gramadóir validator.

        Args:
            gramadoir_dir: Path to gramadoir installation
            language: Language code (ga, gd, cy for Irish, Scottish Gaelic, Welsh)
            use_cli: Whether to use Perl CLI (more accurate) or pattern-based
        """
        self.gramadoir_dir = Path(gramadoir_dir) if gramadoir_dir else GRAMADOIR_DATA_DIR
        self.language = language
        self.use_cli = use_cli
        self._cli_available = self._check_cli_available() if use_cli else False

        # Common Irish grammar patterns for quick validation
        self._mutation_patterns = self._load_mutation_patterns()

    def _check_cli_available(self) -> bool:
        """Check if Perl and gramadoir are available."""
        try:
            result = subprocess.run(
                ["perl", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                logger.warning("Perl not available for Gramadóir CLI")
                return False

            # Check for gr.pl script
            gr_script = self.gramadoir_dir / "gr.pl"
            if not gr_script.exists():
                logger.warning(f"gr.pl not found at {gr_script}")
                return False

            return True
        except Exception as e:
            logger.warning(f"Gramadóir CLI check failed: {e}")
            return False

    def _load_mutation_patterns(self) -> dict[str, re.Pattern]:
        """Load Irish mutation validation patterns."""
        return {
            # Lenition after particles
            "lenition_after_a": re.compile(r"\ba\s+[bcdfgmpt][^h]", re.IGNORECASE),
            # Eclipsis after prepositions
            "eclipsis_after_i": re.compile(r"\bi\s+[bcdfgpt](?![mbndgc])", re.IGNORECASE),
            # Article mutations
            "an_masc": re.compile(r"\ban\s+[bcdfgmpt]h", re.IGNORECASE),
            # Common errors
            "double_fada": re.compile(r"[áéíóú]{2,}"),
        }

    def validate(self, text: str, track_context: bool = True) -> GrammarValidationResult:
        """
        Validate Irish text for grammar issues.

        Args:
            text: Text to validate
            track_context: Whether to include context snippets

        Returns:
            GrammarValidationResult with detected issues
        """
        if not text or not text.strip():
            return GrammarValidationResult(
                text="",
                language=self.language,
                is_valid=True,
            )

        if self._cli_available and self.use_cli:
            return self._validate_with_cli(text, track_context)
        return self._validate_with_patterns(text, track_context)

    def _validate_with_cli(self, text: str, track_context: bool) -> GrammarValidationResult:
        """Validate using Gramadóir Perl CLI."""
        gr_script = self.gramadoir_dir / "gr.pl"
        issues: list[GrammarIssue] = []

        try:
            # Write text to temp file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False, encoding="utf-8"
            ) as f:
                f.write(text)
                input_path = f.name

            # Run gramadoir
            result = subprocess.run(
                ["perl", str(gr_script), "-a", "-f", input_path],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.gramadoir_dir),
                encoding="utf-8",
            )

            # Parse output
            # Format: filename:line:column: message
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                match = re.match(r".*?:(\d+):(\d+):\s*(.+)", line)
                if match:
                    line_num = int(match.group(1))
                    col_num = int(match.group(2))
                    message = match.group(3)

                    # Extract context if requested
                    context = ""
                    if track_context:
                        lines = text.split("\n")
                        if 0 < line_num <= len(lines):
                            context = lines[line_num - 1]

                    issues.append(
                        GrammarIssue(
                            line=line_num,
                            column=col_num,
                            error_code="GRAM",
                            message_ga=message,
                            message_en=message,  # CLI output is already in user's locale
                            context=context,
                            severity="warning",
                        )
                    )

            # Cleanup temp file
            Path(input_path).unlink(missing_ok=True)

        except subprocess.TimeoutExpired:
            logger.error("Gramadóir CLI timeout")
            return GrammarValidationResult(
                text=text,
                language=self.language,
                is_valid=False,
                source="gramadoir-cli-timeout",
            )
        except Exception as e:
            logger.error(f"Gramadóir CLI error: {e}")
            return self._validate_with_patterns(text, track_context)

        error_count = sum(1 for i in issues if i.severity == "error")
        warning_count = sum(1 for i in issues if i.severity == "warning")

        return GrammarValidationResult(
            text=text,
            language=self.language,
            issues=issues,
            is_valid=error_count == 0,
            error_count=error_count,
            warning_count=warning_count,
            source="gramadoir-cli",
        )

    def _validate_with_patterns(self, text: str, track_context: bool) -> GrammarValidationResult:
        """Validate using pattern-based rules."""
        issues: list[GrammarIssue] = []
        lines = text.split("\n")

        for line_num, line in enumerate(lines, 1):
            for pattern_name, pattern in self._mutation_patterns.items():
                for match in pattern.finditer(line):
                    issues.append(
                        GrammarIssue(
                            line=line_num,
                            column=match.start() + 1,
                            error_code=pattern_name.upper(),
                            message_ga=f"Fadhb fhéideartha: {pattern_name}",
                            message_en=f"Potential issue: {pattern_name}",
                            context=line if track_context else "",
                            severity="warning",
                        )
                    )

        return GrammarValidationResult(
            text=text,
            language=self.language,
            issues=issues,
            is_valid=len(issues) == 0,
            error_count=0,
            warning_count=len(issues),
            source="gramadoir-patterns",
        )

    def batch_validate(
        self,
        texts: list[str],
        **kwargs,
    ) -> list[GrammarValidationResult]:
        """Validate multiple texts."""
        return [self.validate(text, **kwargs) for text in texts]


# =============================================================================
# Dagster Asset
# =============================================================================

try:
    from dagster import AssetExecutionContext, Config, asset
    from pydantic import Field as PydanticField

    class GrammarValidationConfig(Config):
        """Configuration for grammar validation asset."""

        use_cli: bool = PydanticField(
            default=True,
            description="Use Gramadóir Perl CLI (more accurate)",
        )
        fail_on_errors: bool = PydanticField(
            default=False,
            description="Fail the asset if grammar errors are found",
        )
        min_text_length: int = PydanticField(
            default=10,
            description="Minimum text length to validate",
        )

    @asset(
        name="grammar_validated_curriculum",
        description="Curriculum content validated for Irish grammar using Gramadóir",
        group_name="nlp",
        compute_kind="gramadoir",
    )
    def grammar_validated_curriculum(
        context: AssetExecutionContext,
    ) -> dict[str, Any]:
        """
        Validate Irish curriculum content for grammar issues.

        This asset:
        1. Loads curriculum text from upstream assets
        2. Runs Gramadóir grammar validation
        3. Logs issues and returns validation summary

        Returns:
            Dictionary with validation statistics and issues
        """
        validator = GramadoirValidator(use_cli=True)

        # For now, return a placeholder - integrate with curriculum asset
        context.log.info("Grammar validation asset initialized")
        context.log.info(f"Gramadóir CLI available: {validator._cli_available}")

        return {
            "status": "ready",
            "validator_source": validator._cli_available and "gramadoir-cli" or "gramadoir-patterns",
            "config": {
                "use_cli": config.use_cli,
                "fail_on_errors": config.fail_on_errors,
                "min_text_length": config.min_text_length,
            },
        }

except ImportError:
    # Dagster not installed
    def grammar_validated_curriculum(*args, **kwargs):
        raise ImportError("Dagster is required for this asset")


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Validate Irish text grammar with Gramadóir")
    parser.add_argument("text", nargs="?", help="Text to validate (or use stdin)")
    parser.add_argument("--file", "-f", help="Input file path")
    parser.add_argument("--no-cli", action="store_true", help="Use pattern-based validation")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    validator = GramadoirValidator(use_cli=not args.no_cli)

    # Get input text
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    # Validate
    result = validator.validate(text)

    # Output
    if result.has_issues:
        print(f"Found {len(result.issues)} issue(s):")
        for issue in result.issues:
            print(f"  Line {issue.line}, Col {issue.column}: {issue.message_en}")
            if issue.context:
                print(f"    Context: {issue.context[:50]}...")
    else:
        print("No grammar issues found.")

    if args.verbose:
        print("\n--- Stats ---")
        print(f"Source: {result.source}")
        print(f"Valid: {result.is_valid}")
        print(f"Errors: {result.error_count}")
        print(f"Warnings: {result.warning_count}")
