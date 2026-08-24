"""Phase 2b cross-check extraction for the LC chemistry pilot.

This is the Phase 2b cross-check helper for the
``2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1``
openspec change. It runs each lc6 syllabus extraction twice:

- PRIMARY: MiniMax-M3 via the BAML client ``ExtractEn`` (the default
  client of ``ExtractLC6Syllabus`` / ``ExtractChemSyllabus``).
- SECONDARY: qwen3.7-plus via the BAML client ``ExtractQwenCrossCheck``
  (openai-generic, ``DASHSCOPE_BASE_URL`` + ``DASHSCOPE_API_KEY``),
  selected purely Python-side with
  ``baml_options={"client": "ExtractQwenCrossCheck"}`` — no .baml edits.

Cross-model disagreements (field-level diffs on the key LCSyllabus
scalars) are logged to local Langfuse per the
``specs/british-isles-education-pipeline-v3`` spec delta scenario
"Cross-model disagreement is observable": a trace ``lc6_cross_check``,
a span carrying the disagreements, and a ``cross_check_agreement``
score (1.0 agree / 0.0 disagree / 0.5 secondary_failed).

The PRIMARY value is canonical — it is what gets loaded downstream.
The Qwen secondary call is expected to FAIL with an auth / missing-env
error until a real ``DASHSCOPE_API_KEY`` lands in the Infisical vault;
that is expected, not a bug. This module never fabricates or substitutes
API keys and never reads ``*.secrets.toml``.

All Langfuse calls are wrapped so they NEVER raise: the local Langfuse
at http://localhost:3000 may be down, in which case the helper degrades
to structlog-only logging.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog

if TYPE_CHECKING:
    from baml_client.baml_client.types import LCSyllabus

logger = structlog.get_logger(__name__)

MAX_TEXT_CHARS = 200_000

SECONDARY_CLIENT = "ExtractQwenCrossCheck"

# Key LCSyllabus scalar fields the cross-check diffs on.
_DIFF_FIELDS: tuple[str, ...] = (
    "topic_count",
    "learning_outcome_count",
    "level",
    "source_pages",
)

# Non-secret, publicly documented endpoint defaults (openspec change
# 2026-08-06-token-plan-apis..., tasks.md §1.6). NEVER API keys.
_ENDPOINT_DEFAULTS: dict[str, str] = {
    "MINIMAX_BASE_URL": "https://api.minimax.io/v1",
    "DASHSCOPE_BASE_URL": "https://coding.dashscope.aliyuncs.com/v1",
    "LANGFUSE_HOST": "http://localhost:3000",
}

_baml_cache: Any = None
_baml_loaded: bool = False


@dataclass
class CrossCheckResult:
    """Outcome of one primary/secondary cross-check extraction run."""

    source_pdf: str
    language: str
    baml_function: str
    status: str  # "agree" | "disagree" | "secondary_failed" | "primary_failed"
    primary: "LCSyllabus | None" = None
    secondary: "LCSyllabus | None" = None
    disagreements: list[str] = field(default_factory=list)
    secondary_error: str | None = None
    primary_error: str | None = None


def _ensure_endpoint_defaults() -> None:
    """Set documented non-secret endpoint env vars, only if absent.

    Must run BEFORE the first baml_client import: the BAML runtime
    snapshots os.environ at import time. Never touches API keys.
    """
    for name, value in _ENDPOINT_DEFAULTS.items():
        if not os.environ.get(name):
            os.environ[name] = value
            logger.info("endpoint_default_set", var=name, value=value)


def _load_baml() -> Any:
    """Lazily import the generated BAML sync client (cached)."""
    global _baml_cache, _baml_loaded
    if _baml_loaded:
        return _baml_cache
    try:
        from baml_client import b
    except ImportError:
        try:
            from baml_client.baml_client.sync_client import b
        except ImportError:
            b = None
    if b is None:
        logger.warning("baml_client_not_importable")
    _baml_cache = b
    _baml_loaded = True
    return b


def _call_baml(
    baml_function: str,
    subject: str,
    text: str,
    language: str,
    client_override: str | None = None,
) -> "LCSyllabus":
    """Dispatch one BAML extraction call, optionally to a named client."""
    b = _load_baml()
    if b is None:
        raise RuntimeError("baml_client not importable")
    kwargs: dict[str, Any] = {}
    if client_override is not None:
        kwargs["baml_options"] = {"client": client_override}
    if baml_function == "ExtractLC6Syllabus":
        return b.ExtractLC6Syllabus(subject, text, language, **kwargs)
    if baml_function == "ExtractChemSyllabus":
        return b.ExtractChemSyllabus(text, language, **kwargs)
    raise ValueError(f"unsupported baml_function: {baml_function}")


def _scalars(syllabus: "LCSyllabus") -> dict[str, Any]:
    return {name: getattr(syllabus, name, None) for name in _DIFF_FIELDS}


def _diff_syllabus(
    primary: "LCSyllabus", secondary: "LCSyllabus"
) -> list[str]:
    """Human-readable field-level diff descriptions between two results."""
    disagreements: list[str] = []
    for name in _DIFF_FIELDS:
        pv = getattr(primary, name, None)
        sv = getattr(secondary, name, None)
        if pv != sv:
            disagreements.append(f"{name}: primary={pv} secondary={sv}")
    return disagreements


def _langfuse_helpers() -> Any:
    """Import the canonical Langfuse helpers; None when unavailable."""
    try:
        from observability import langfuse_config

        return langfuse_config
    except ImportError as exc:
        logger.warning("langfuse_helpers_import_failed", error=str(exc))
        return None


def _log_to_langfuse(result: CrossCheckResult) -> None:
    """Log the cross-check outcome to Langfuse; NEVER raises."""
    try:
        helpers = _langfuse_helpers()
        if helpers is None:
            logger.warning(
                "langfuse_degraded", reason="observability helpers unavailable"
            )
            return

        client = helpers.get_langfuse_client()
        if client is None:
            logger.warning(
                "langfuse_degraded",
                reason="client None (langfuse not installed or init failed)",
            )

        score_value = {
            "agree": 1.0,
            "disagree": 0.0,
            "secondary_failed": 0.5,
        }.get(result.status, 0.5)

        with helpers.langfuse_trace(
            name="lc6_cross_check",
            metadata={
                "source_pdf": result.source_pdf,
                "language": result.language,
                "baml_function": result.baml_function,
                "status": result.status,
            },
            tags=["lc6", "cross-check", "chemistry-pilot"],
        ) as trace:
            if trace is None:
                logger.warning(
                    "langfuse_degraded",
                    reason="trace unavailable (local Langfuse down?)",
                    host=os.environ.get("LANGFUSE_HOST"),
                )
                return
            helpers.create_span(
                trace,
                name="cross_check_disagreements",
                input_data=(
                    _scalars(result.primary) if result.primary else None
                ),
                output_data=(
                    _scalars(result.secondary) if result.secondary else None
                ),
                metadata={
                    "disagreements": result.disagreements,
                    "secondary_error": result.secondary_error,
                },
            )
            helpers.score_trace(
                trace,
                name="cross_check_agreement",
                value=score_value,
                comment=(
                    "; ".join(result.disagreements)
                    or result.secondary_error
                    or "models agree"
                ),
            )
    except Exception as exc:  # noqa: BLE001 — Langfuse must never break extraction
        logger.warning("langfuse_degraded", reason=str(exc))


def extract_with_cross_check(
    text: str,
    subject: str,
    language: str,
    source_pdf: str,
    baml_function: str = "ExtractLC6Syllabus",
) -> CrossCheckResult:
    """Run MiniMax-primary / Qwen-secondary extraction and diff them.

    The PRIMARY result is canonical. The secondary runs with
    ``baml_options={"client": "ExtractQwenCrossCheck"}`` and is expected
    to fail auth until DASHSCOPE_API_KEY is hydrated from Infisical.
    """
    result = CrossCheckResult(
        source_pdf=source_pdf,
        language=language,
        baml_function=baml_function,
        status="primary_failed",
    )

    try:
        result.primary = _call_baml(baml_function, subject, text, language)
    except Exception as exc:  # noqa: BLE001 — BAML error types are not stable API
        result.primary_error = str(exc)
        logger.error(
            "cross_check_primary_failed",
            source_pdf=source_pdf,
            baml_function=baml_function,
            error=result.primary_error[:200],
        )
        return result

    try:
        result.secondary = _call_baml(
            baml_function,
            subject,
            text,
            language,
            client_override=SECONDARY_CLIENT,
        )
    except Exception as exc:  # noqa: BLE001 — BAML error types are not stable API
        result.secondary_error = str(exc)
        result.status = "secondary_failed"
        logger.warning(
            "cross_check_secondary_failed",
            source_pdf=source_pdf,
            baml_function=baml_function,
            client=SECONDARY_CLIENT,
            error=result.secondary_error[:200],
        )
        _log_to_langfuse(result)
        return result

    result.disagreements = _diff_syllabus(result.primary, result.secondary)
    result.status = "disagree" if result.disagreements else "agree"
    logger.info(
        "cross_check_complete",
        source_pdf=source_pdf,
        baml_function=baml_function,
        status=result.status,
        disagreements=result.disagreements,
    )
    _log_to_langfuse(result)
    return result


def _extract_pdf_text(pdf_path: Path) -> tuple[str, int]:
    """Extract the text layer of a PDF via pypdf. Returns (text, pages)."""
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages), len(reader.pages)


def _summarize(result: CrossCheckResult, char_count: int) -> str:
    p_tc = result.primary.topic_count if result.primary else None
    s_tc = result.secondary.topic_count if result.secondary else None
    p_lo = result.primary.learning_outcome_count if result.primary else None
    s_lo = result.secondary.learning_outcome_count if result.secondary else None
    secondary_err = ""
    if result.secondary_error:
        secondary_err = f" secondary_error={result.secondary_error[:200]!r}"
    primary_err = ""
    if result.primary_error:
        primary_err = f" primary_error={result.primary_error[:200]!r}"
    return (
        f"{result.source_pdf} [{result.baml_function}/{result.language}] "
        f"chars={char_count} status={result.status} "
        f"topic_count primary={p_tc} secondary={s_tc} "
        f"lo_count primary={p_lo} secondary={s_lo} "
        f"disagreements={result.disagreements}{secondary_err}{primary_err}"
    )


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    # Must precede any baml_client import (env snapshot at import time).
    _ensure_endpoint_defaults()
    logger.info(
        "env_presence",
        MINIMAX_API_KEY=bool(os.environ.get("MINIMAX_API_KEY")),
        DASHSCOPE_API_KEY=bool(os.environ.get("DASHSCOPE_API_KEY")),
        MINIMAX_BASE_URL=os.environ.get("MINIMAX_BASE_URL"),
        DASHSCOPE_BASE_URL=os.environ.get("DASHSCOPE_BASE_URL"),
        LANGFUSE_HOST=os.environ.get("LANGFUSE_HOST"),
    )

    chem_en = repo_root / "leaving_certificate/chemistry/en/SCSEC09_Chemistry_syllabus_Eng.pdf"
    chem_ga = repo_root / "leaving_certificate/chemistry/ga/SCSEC09_Chemistry_syllabus_Gaeilge.pdf"

    runs: list[tuple[Path, str, str]] = [
        (chem_en, "en", "ExtractLC6Syllabus"),
        (chem_ga, "ga", "ExtractLC6Syllabus"),
        (chem_en, "en", "ExtractChemSyllabus"),
    ]

    texts: dict[Path, str] = {}
    for pdf_path, _, _ in runs:
        if pdf_path in texts:
            continue
        try:
            text, page_count = _extract_pdf_text(pdf_path)
        except Exception as exc:  # noqa: BLE001 — report unreadable PDFs honestly
            logger.error("pdf_read_failed", pdf=str(pdf_path), error=str(exc))
            texts[pdf_path] = ""
            continue
        texts[pdf_path] = text
        logger.info(
            "pdf_text_extracted",
            pdf=pdf_path.name,
            pages=page_count,
            chars=len(text),
            has_text=bool(text.strip()),
        )

    print("=== lc6_cross_check dev runner ===")
    for pdf_path, language, baml_function in runs:
        text = texts.get(pdf_path, "")
        if not text.strip():
            print(
                f"{pdf_path.name} [{baml_function}/{language}] "
                f"SKIPPED: no extractable text layer (empty pypdf output); "
                f"not fabricating text"
            )
            continue
        truncated = len(text) > MAX_TEXT_CHARS
        if truncated:
            text = text[:MAX_TEXT_CHARS]
            logger.info(
                "text_truncated",
                pdf=pdf_path.name,
                kept_chars=MAX_TEXT_CHARS,
            )
        result = extract_with_cross_check(
            text=text,
            subject="chemistry",
            language=language,
            source_pdf=pdf_path.name,
            baml_function=baml_function,
        )
        print(_summarize(result, len(text)) + (f" TRUNCATED={truncated}" if truncated else ""))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
