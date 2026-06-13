#!/usr/bin/env python3
"""
Cognee archive / loose-file ingestion script.

Ingests the following into Cognee via the cognee REST API:
  1. docs/archive/2026-06-06-*   (date-stamped reference archives)
  2. docs/*.pdf at root          (5 loose reference PDFs)
  3. docs/auto-deploy-stacks.toml (a single loose config file)
  4. docs/INDEX.md, docs/00_index.md (master index files)

Features:
  - SHA-256 dedup at ~/.cache/cognee-dedup.json (per-path)
  - PDF text extraction via pypdf (graceful fallback to "binary blob"
    placeholder if pypdf is not installed)
  - Per-archive datasets (e.g. cognee-archive-2026-06-06-data-engineering)
  - --dry-run shows plan without ingesting
  - --reset clears the dedup cache
  - --no-cognify stores data only (skips graph build)

Usage:
  # Dry run
  uv run python3 infrastructure/scripts/cognee-ingest-archive.py --dry-run

  # Ingest all archives (no cognify)
  uv run python3 infrastructure/scripts/cognee-ingest-archive.py --no-cognify

  # Reset the dedup cache and re-ingest everything
  uv run python3 infrastructure/scripts/cognee-ingest-archive.py --reset --no-cognify
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import requests

COGNEE_API_URL = os.environ.get("COGNEE_API_URL", "http://localhost:8100")
COGNEE_API_KEY = os.environ.get("COGNEE_API_KEY", "")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = REPO_ROOT / "docs"
DEDUP_CACHE_PATH = Path.home() / ".cache" / "cognee-dedup.json"

ARCHIVE_DIRS = sorted(DOCS_ROOT.glob("archive/2026-*"))
LOOSE_PDFS = sorted(DOCS_ROOT.glob("*.pdf"))
LOOSE_MD = [
    DOCS_ROOT / "00_index.md",
    DOCS_ROOT / "INDEX.md",
]
LOOSE_CONFIG = [
    DOCS_ROOT / "auto-deploy-stacks.toml",
]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass(frozen=True)
class IngestTarget:
    path: Path
    archive_name: str  # e.g. "2026-06-06-data-engineering"
    category: str  # "archive" | "loose-pdf" | "loose-md" | "loose-config"
    title: str
    body: str

    @property
    def dataset_name(self) -> str:
        if self.category == "archive":
            safe_archive = re.sub(r"[^a-zA-Z0-9_-]", "_", self.archive_name)
            return f"cognee-archive-{safe_archive}"
        if self.category == "loose-pdf":
            return "cognee-archive-loose-pdfs"
        if self.category == "loose-md":
            return "cognee-archive-loose-md"
        if self.category == "loose-config":
            return "cognee-archive-loose-config"
        return "cognee-archive-misc"

    @property
    def dedup_key(self) -> str:
        return f"{self.path}:{self.body[:64]}"


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_dedup_cache() -> dict[str, str]:
    if not DEDUP_CACHE_PATH.exists():
        return {}
    try:
        return json.loads(DEDUP_CACHE_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_dedup_cache(cache: dict[str, str]) -> None:
    DEDUP_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEDUP_CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True))


def extract_pdf_text(path: Path) -> str:
    """Extract text from a PDF file. Returns a placeholder if pypdf is not installed."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return f"[PDF binary blob: {path.name} ({path.stat().st_size:,} bytes); install pypdf to extract text]"
    try:
        reader = PdfReader(str(path))
        chunks: list[str] = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            chunks.append(f"--- Page {i+1} ---\n{text}")
        return "\n\n".join(chunks)
    except Exception as exc:
        return f"[PDF extraction failed for {path.name}: {exc}]"


def strip_frontmatter(text: str) -> tuple[dict, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    fm_text = match.group(1)
    body = text[match.end():]
    fm: dict = {}
    current_key: str | None = None
    for line in fm_text.splitlines():
        if not line.strip():
            continue
        if line.startswith(("  - ", "    - ")) and current_key:
            value = fm.setdefault(current_key, [])
            if isinstance(value, list):
                value.append(line.split("- ", 1)[1].strip().strip('"').strip("'"))
        elif ":" in line:
            key, _, raw = line.partition(":")
            current_key = key.strip()
            raw = raw.strip()
            if not raw:
                continue
            if raw.startswith("[") and raw.endswith("]"):
                items = [s.strip().strip('"').strip("'") for s in raw[1:-1].split(",") if s.strip()]
                fm[current_key] = items
            else:
                fm[current_key] = raw.strip('"').strip("'")
    return fm, body


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def load_targets() -> list[IngestTarget]:
    targets: list[IngestTarget] = []
    # Archives
    for archive_dir in ARCHIVE_DIRS:
        archive_name = archive_dir.name
        for path in sorted(archive_dir.rglob("*.md")):
            text = read_text(path)
            fm, body = strip_frontmatter(text)
            targets.append(
                IngestTarget(
                    path=path,
                    archive_name=archive_name,
                    category="archive",
                    title=fm.get("title", path.stem),
                    body=body,
                )
            )
    # Loose PDFs
    for path in LOOSE_PDFS:
        body = extract_pdf_text(path)
        targets.append(
            IngestTarget(
                path=path,
                archive_name="loose-pdfs",
                category="loose-pdf",
                title=path.stem,
                body=body,
            )
        )
    # Loose markdown
    for path in LOOSE_MD:
        if not path.exists():
            continue
        text = read_text(path)
        fm, body = strip_frontmatter(text)
        targets.append(
            IngestTarget(
                path=path,
                archive_name="loose-md",
                category="loose-md",
                title=fm.get("title", path.stem),
                body=body,
            )
        )
    # Loose config
    for path in LOOSE_CONFIG:
        if not path.exists():
            continue
        text = read_text(path)
        targets.append(
            IngestTarget(
                path=path,
                archive_name="loose-config",
                category="loose-config",
                title=path.stem,
                body=text,
            )
        )
    return targets


def post_multipart(path: str, files: dict, form_data: dict, timeout: int = 300) -> dict:
    headers: dict = {}
    if COGNEE_API_KEY:
        headers["Authorization"] = f"Bearer {COGNEE_API_KEY}"
    response = requests.post(
        f"{COGNEE_API_URL}{path}",
        files=files,
        data=form_data,
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json() if response.text else {}


def post_json(path: str, payload: dict, timeout: int = 300) -> dict:
    headers: dict = {"Content-Type": "application/json"}
    if COGNEE_API_KEY:
        headers["Authorization"] = f"Bearer {COGNEE_API_KEY}"
    response = requests.post(
        f"{COGNEE_API_URL}{path}",
        json=payload,
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json() if response.text else {}


def get_json(path: str) -> dict:
    headers: dict = {}
    if COGNEE_API_KEY:
        headers["Authorization"] = f"Bearer {COGNEE_API_KEY}"
    response = requests.get(
        f"{COGNEE_API_URL}{path}",
        headers=headers,
        timeout=60,
    )
    response.raise_for_status()
    return response.json() if response.text else {}


def ensure_dataset(dataset_name: str) -> str:
    response = get_json("/api/v1/datasets")
    payload = response if isinstance(response, list) else response.get("data", response)
    for d in payload:
        if d.get("name") == dataset_name:
            return d["id"]
    created = post_json(
        "/api/v1/datasets",
        {"name": dataset_name, "description": f"Cianfhoghlaim archive - {dataset_name}"},
    )
    return created["id"]


def ingest_target(target: IngestTarget, dataset_id: str) -> dict:
    text = f"# {target.title}\n\n{target.body}"
    files = {
        "data": (
            f"{target.path.stem}.md",
            io.BytesIO(text.encode("utf-8")),
            "text/markdown",
        )
    }
    form_data = {"datasetId": dataset_id}
    return post_multipart("/api/v1/add", files, form_data)


def wait_for_cognify(pipeline_run_id: str, timeout_s: int = 600) -> dict:
    start = time.time()
    while time.time() - start < timeout_s:
        try:
            status = get_json(f"/api/v1/cognify/{pipeline_run_id}/status")
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return {"status": "completed"}
            raise
        if status.get("status") in {"completed", "failed"}:
            return status
        time.sleep(5)
    return {"status": "timeout"}


def cognify_dataset(dataset_name: str, dataset_id: str) -> dict:
    response = post_json(
        "/api/v1/cognify",
        {"datasetIds": [dataset_id]},
        timeout=600,
    )
    run_id = response.get("pipeline_run_id") or response.get("id") or response.get("runId")
    if run_id and isinstance(run_id, str):
        return wait_for_cognify(run_id)
    return response


def plan(targets: list[IngestTarget], dedup_cache: dict[str, str]) -> dict:
    by_dataset: dict[str, list[IngestTarget]] = {}
    skipped: list[IngestTarget] = []
    for t in targets:
        dedup_key = t.dedup_key
        if dedup_key in dedup_cache:
            skipped.append(t)
            continue
        by_dataset.setdefault(t.dataset_name, []).append(t)
    return {
        "by_dataset": {k: len(v) for k, v in by_dataset.items()},
        "skipped": len(skipped),
        "total": len(targets),
        "datasets": {k: [t.path.name for t in v] for k, v in by_dataset.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-cognify", action="store_true", help="Store data only; skip cognify")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without executing")
    parser.add_argument("--reset", action="store_true", help="Clear the dedup cache first")
    parser.add_argument("--summary", action="store_true", help="Show summary and exit")
    args = parser.parse_args()

    if args.reset and DEDUP_CACHE_PATH.exists():
        DEDUP_CACHE_PATH.unlink()
        print(f"[reset] removed {DEDUP_CACHE_PATH}")

    dedup_cache = load_dedup_cache()
    targets = load_targets()

    p = plan(targets, dedup_cache)
    if args.summary or args.dry_run:
        print(f"Total targets: {p['total']}")
        print(f"Skipped (in dedup cache): {p['skipped']}")
        print(f"By dataset:")
        for ds, count in p["by_dataset"].items():
            print(f"  {ds}: {count} files")
        return 0

    # Probe Cognee REST API once before processing
    try:
        get_json("/health")
    except requests.exceptions.ConnectionError:
        print(
            f"ERROR: Cognee REST API is not reachable at {COGNEE_API_URL}.",
            file=sys.stderr,
        )
        return 1

    if not LLM_API_KEY and not args.no_cognify:
        print(
            "WARN: LLM_API_KEY not set. Phase 2 (cognify) will fail. "
            "Re-run with --no-cognify to store data only, or set LLM_API_KEY and retry.",
            file=sys.stderr,
        )

    total_added = 0
    total_skipped = 0
    for dataset_name, ds_targets in [
        (ds, [t for t in targets if t.dataset_name == ds and t.dedup_key not in dedup_cache])
        for ds in p["by_dataset"].keys()
    ]:
        if not ds_targets:
            continue
        try:
            dataset_id = ensure_dataset(dataset_name)
            print(f"[{dataset_name}] dataset {dataset_name} -> {dataset_id}")
        except requests.HTTPError as exc:
            print(
                f"[{dataset_name}] failed to create dataset: HTTP {exc.response.status_code if exc.response else '?'} - {exc}",
                file=sys.stderr,
            )
            continue
        for t in ds_targets:
            try:
                result = ingest_target(t, dataset_id)
                total_added += 1
                # Update dedup cache
                dedup_cache[t.dedup_key] = sha256(t.body)
                print(f"  + {t.path.name} -> {result.get('data_id', result.get('id', 'queued'))}")
            except requests.HTTPError as exc:
                print(
                    f"  ! {t.path.name}: HTTP {exc.response.status_code if exc.response else '?'} - {exc}",
                    file=sys.stderr,
                )
        save_dedup_cache(dedup_cache)
        if args.no_cognify:
            print(f"[{dataset_name}] --no-cognify set, skipping graph build")
            continue
        if not LLM_API_KEY:
            print(
                f"[{dataset_name}] skipping cognify: LLM_API_KEY not set",
                file=sys.stderr,
            )
            continue
        try:
            result = cognify_dataset(dataset_name, dataset_id)
            print(f"  cognify status: {result.get('status', 'unknown')}")
        except requests.HTTPError as exc:
            print(
                f"  ! cognify failed: HTTP {exc.response.status_code if exc.response else '?'} - {exc}",
                file=sys.stderr,
            )

    print(f"\nTotal docs added: {total_added}")
    print(f"Total docs skipped (dedup): {total_skipped}")
    print(f"Dedup cache: {DEDUP_CACHE_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
