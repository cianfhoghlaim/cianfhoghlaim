"""
Registry audit script for the `centralized-model-registry` capability.

Detects hardcoded **model names / model IDs** (not generic identifiers)
in Python files under `agents/`, `baml_src/`, `notebooks/`, `web/`,
`orchestration/`, `spaces/`, and `meaisinfhoghlaim/` that are NOT routed through
`MODEL_REGISTRY`. Exits non-zero if any hardcoded string is found
(with --strict).

Usage:
    mise run lint:registry
    mise run lint:registry --strict

Part of: openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1

## How it works

The audit uses a tight whitelist of "model-family prefixes" + the
canonical MODEL_REGISTRY key set to detect real model string drift.
Generic identifiers like "baml-cli", "end-to-end", "5-layer" are
NOT matched because they don't start with a known family prefix.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


# ─── Canonical MODEL_REGISTRY keys (must match the live registry) ────────────


_KNOWN_MODEL_KEYS: set[str] = {
    # OCR / Vision
    "deepseek-ocr-2", "docling-serve", "dots-ocr", "gemma-3-4b", "gemma-3-27b",
    "glm-4.6v-flash", "internvl3-8b", "llama-3.2-vision-11b",
    "molmo2-4b", "molmo2-8b", "olmocr-2-7b-1025", "paddleocr-vl-1.6",
    "qwen3-vl-30b-a3b", "qwen3-vl-4b", "qwen3-vl-8b", "qwen3.6-27b-mtp",
    "uccix-llama-3.1-8b", "uccix-llama2-13b", "uccix-mistral-24b",
    "unstract-api", "gemma-4-E2B", "gemma-4-E4B", "gemma-4-12B",
    "gemma-4-26B-A4B",
    # Text LLM (LiteLLM M3 chokepoint + agent defaults)
    "kimi-k2.6", "glm-5.1", "minimax-m2.5", "mimo-v2.5",
    "deepseek-v4-flash", "minimax-m3",
    "claude-sonnet-4-20250514", "gpt-4o-mini", "gemini-2.5-pro",
    "gemini-2.0-flash",
    # Embedder
    "BAAI/bge-m3", "BAAI/bge-large-en-v1.5", "all-MiniLM-L6-v2",
    # Rerank
    "jina-reranker-v2-base-multilingual", "rerank-v3.5", "gte-rerank-v2",
    # Image gen (LiteLLM aliases — long keys)
    "local/image/flux2-dev", "local/image/z-image-turbo",
    "local/image/qwen-image", "local/image/sdxl", "local/image/fibo",
    # Voice
    "whisper-large", "wav2vec2-irish", "chatterbox", "aba-tts",
    "ResembleAI/chatterbox",
    # Translation
    "opus-mt", "m2m100", "nllb",
    "Helsinki-NLP/opus-mt-{src}-{tgt}",
    "facebook/m2m100_418M", "facebook/nllb-200-distilled-600M",
    "ReliableAI/UCCIX-Mistral-24B", "ReliableAI/UCCIX-Llama-3.1-8B",
    # Older HF org/model patterns that are still canonical
    "Qwen/Qwen3-VL-8B-Instruct", "Qwen/Qwen3-VL-4B-Instruct",
    "Qwen/Qwen3-VL-30B-A3B-Instruct", "Qwen/Qwen3.6-27B",
    "Qwen/Qwen3-Omni", "Qwen/Qwen-Image",
    "google/gemma-4-E2B-it", "google/gemma-4-E4B-it",
    "google/gemma-4-12B-it", "google/gemma-4-26B-A4B-it",
    "unsloth/gemma-4-E2B-it-GGUF", "unsloth/gemma-4-E4B-it-GGUF",
    "unsloth/gemma-4-12b-it-GGUF", "unsloth/gemma-4-26B-A4B-it-GGUF",
    "unsloth/Qwen3-VL-4B-Instruct-GGUF", "unsloth/Qwen3-VL-8B-Instruct-GGUF",
    "unsloth/Qwen3-VL-30B-A3B-Instruct-GGUF", "unsloth/Qwen3.6-27B-MTP-GGUF",
    "unsloth/GLM-4.6V-Flash-GGUF", "unsloth/Llama-3.2-11B-Vision-Instruct-unsloth-bnb-4bit",
    "unsloth/InternVL3-8B-GGUF",
    "zai-org/GLM-4.6V-Flash",
    "meta-llama/Llama-3.2-11B-Vision-Instruct",
    "OpenGVLab/InternVL3_5-8B",
    "allenai/Molmo2-4B", "allenai/Molmo2-8B",
    "allenai/olmOCR-2-7B-1025",
    "PaddlePaddle/PaddleOCR-VL-1.6-GGUF",
    "google/gemma-3-4b-it",
    "ibm-granite/granite-docling-258M",
    "rednote-hilab/dots.ocr",
    "deepseek-ai/DeepSeek-OCR-2",
    # LiteLLM M3 chokepoint variants / canonical aliases
    "kimi/k2", "glm/5.1", "minimax/m2.5", "mimo/2.5", "deepseek/flash",
    "anthropic/claude-sonnet-4-20250514", "openai/gpt-4o-mini",
    "gemini/gemini-2.5-pro", "gemini/gemini-2.0-flash",
}


# ─── Family prefixes (separators: `,`, space, `=`, `(`, `[`, `"`, `'`) ─────


_PREFIXES = (
    # LLM families
    "gemini-", "gemma-", "claude-", "gpt-", "minimax-", "kimi-",
    "glm-", "mimo-", "deepseek-", "qwen", "llama-", "mistral-",
    "nllb", "opus-mt", "m2m100", "molmo", "internvl", "olmo",
    "starling", "yi-", "phi-", "mixtral-", "deepseek-ocr",
    # Provider prefixes (HF org/model)
    "BAAI/", "ResembleAI/", "ReliableAI/", "Helsinki-NLP/",
    "facebook/", "Qwen/", "google/", "meta-llama/", "allenai/",
    "OpenGVLab/", "unsloth/", "zai-org/", "PaddlePaddle/",
    "deepseek-ai/", "rednote-hilab/", "ibm-granite/",
    # LiteLLM aliases
    "local/vision/", "local/image/", "minimax",
    "anthropic/", "openai/", "opencode-go/",
    # Voice / ASR / TTS
    "whisper-", "wav2vec2-", "chatterbox", "aba-tts",
    # Embedder / Rerank
    "jina-", "rerank-", "gte-",
    # Sentence-transformers
    "sentence-transformers/",
    # Docling / Unstract
    "docling", "unstract",
    # Legacy models referenced in comments / regex patterns (the
    # canonical MODEL_REGISTRY marks these deprecated or removed;
    # the strings survive in non-runtime contexts like drift reports)
    "gemma-3-27b",
)

# Build a single regex: a quoted or bare token that starts with a prefix.
_PREFIX_ALT = "|".join(re.escape(p) for p in _PREFIXES)

# Capture a quoted model OR a bare-word model, anchored by a separator.
# The separator ensures we don't match substrings like "xgemini-foo".
_MODEL_LIKE_PATTERN = re.compile(
    r"(?:^|[\s=,(\[])"               # start anchor
    r"([\"\']?"                       # optional opening quote
    r"(?:" + _PREFIX_ALT + r")"       # the prefix
    r"[\w./\-]+"                       # the model name remainder
    r"[\"\']?"                         # optional closing quote
    r")"
)


# ─── Directories + skip rules ──────────────────────────────────────────────


_AUDIT_DIRS = [
    "agents",
    "baml_src",
    "notebooks",
    "web",
    "orchestration",
    "spaces",
    "meaisinfhoghlaim",  # the OCR/HTR/alignment sub-package (per the 2026-07-30-drift-remediation-everything-bagel-v1 change)
]

_SKIP_PATTERNS = [
    "*/model_registry.py",      # the registry itself
    "*/registry.py",            # the OCR/VLM registry (canonical home)
    "*/registry_audit.py",      # this file
    "*/registry_loader.py",
    "*/registry_api.py",
    "*/registry_linter.py",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/.venv/*",
    "*/node_modules/*",
    "*/.next/*",
    "*/dist/*",
    "*/build/*",
    "*/baml_client/*",
    "*/_generated/*",
]


def _is_skipped(path: Path) -> bool:
    posix = path.as_posix()
    return any(Path(posix).match(pat) for pat in _SKIP_PATTERNS)


def _is_docstring_or_comment(line: str, src_lines: list[str], lineno: int) -> bool:
    """Rough check: skip lines in docstrings or starting with ``#``."""
    if line.lstrip().startswith("#"):
        return True
    in_triple = False
    for prev_line in src_lines[: lineno - 1]:
        stripped = prev_line.split("#", 1)[0]
        for q in ('"""', "'''"):
            n = stripped.count(q)
            if n % 2 == 1:
                in_triple = not in_triple
        if in_triple:
            break
    return in_triple


def _normalize(match: str) -> str:
    s = match.strip()
    if len(s) >= 2 and (
        (s.startswith('"') and s.endswith('"'))
        or (s.startswith("'") and s.endswith("'"))
    ):
        return s[1:-1]
    return s


def audit_file(path: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeDecodeError):
        return findings

    src_lines = text.splitlines()
    for lineno, line in enumerate(src_lines, start=1):
        if _is_docstring_or_comment(line, src_lines, lineno):
            continue
        for match in _MODEL_LIKE_PATTERN.finditer(line):
            candidate = _normalize(match.group(1))
            if candidate in _KNOWN_MODEL_KEYS:
                continue
            # Length sanity
            if len(candidate) < 6 or len(candidate) > 120:
                continue
            # Filter: must contain at least one separator (-/./:) OR a digit
            # (model IDs almost always have these — filters out generic
            # identifiers like "non-representational").
            if not any(c in candidate for c in "-./:") and any(
                c.isdigit() for c in candidate
            ):
                continue
            findings.append({
                "file": str(path),
                "lineno": lineno,
                "line": line.strip()[:120],
                "match": candidate,
            })
    return findings


def audit_repo(repo_root: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for dir_name in _AUDIT_DIRS:
        dir_path = repo_root / dir_name
        if not dir_path.exists():
            continue
        for path in dir_path.rglob("*.py"):
            if _is_skipped(path):
                continue
            findings.extend(audit_file(path))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parent.parent),
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    findings = audit_repo(repo_root)

    drift_findings: list[dict[str, object]] = []
    drift_script = Path(__file__).resolve().parent / "lint_drift_docs.py"
    if drift_script.exists():
        import subprocess
        try:
            subprocess.run(
                [sys.executable, str(drift_script), "--json", "--dry-run"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
        except subprocess.TimeoutExpired:
            drift_findings.append({"warning": "lint_drift_docs timed out"})
    if drift_findings:
        findings = findings + drift_findings  # type: ignore[operator]

    if args.json:
        print(json.dumps({"findings": findings, "count": len(findings)}, indent=2))
    elif not findings:
        print("Found 0 hardcoded model strings in audited files")
    else:
        print(f"Found {len(findings)} potential hardcoded model string(s):")
        by_file: dict[str, list[dict[str, object]]] = {}
        for f in findings:
            file_path = str(f["file"])
            by_file.setdefault(file_path, []).append(f)
        for file_path, file_findings in sorted(by_file.items()):
            print(f"\n  {file_path} ({len(file_findings)} finding(s)):")
            for f in file_findings[:5]:
                print(f"    :{f['lineno']}: {f['match']!r}")
            if len(file_findings) > 5:
                print(f"    ... and {len(file_findings) - 5} more")

    return 1 if (findings and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
