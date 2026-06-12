#!/usr/bin/env python3
"""
Cognee docs/ ingestion script.

Reads all canonical docs from /docs/0*-*/, chunks them per canonical file,
and ingests into Cognee via the cognee-mcp REST API. After ingestion, triggers
a per-dataset cognify() to build the knowledge graph.

Two-phase architecture:
  Phase 1 (add): Stores raw text in the Cognee dataset. No LLM required.
                 Stores up to N canonical files per domain.
  Phase 2 (cognify): Builds the knowledge graph. Requires LLM_API_KEY.

Usage:
  # Ingest the standards domain (2 files, small, good for testing)
  uv run python infrastructure/scripts/cognee-ingest-docs.py --domain standards

  # Ingest all 7 domains
  uv run python infrastructure/scripts/cognee-ingest-docs.py --all

  # Just store (skip cognify if LLM is not yet configured)
  uv run python infrastructure/scripts/cognee-ingest-docs.py --all --no-cognify

  # Show what would be ingested without actually doing it
  uv run python infrastructure/scripts/cognee-ingest-docs.py --all --dry-run
"""

from __future__ import annotations

import argparse
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

DOMAIN_TO_DIR = {
    # 00 - Core + package ecosystem (cross-cutting foundations)
    "core": "00-core",
    "package-ecosystem": "00-package-ecosystem",
    # 01 - Cognee + patterns + platform architecture
    "cognee": "01-cognee",
    "patterns": "01-patterns",
    "platform-architecture": "01-platform-architecture",
    # 02 - Architecture + audit + data platform
    "architecture": "02-architecture",
    "audit": "02-audit",
    "data-platform": "02-data-platform",
    # 03 - Agents + pipelines
    "agents": "03-agents",
    "pipelines": "03-pipelines",
    # 04 - AI/ML
    "ai-ml": "04-ai-ml",
    # 05 - Celtic language + web
    "celtic-language": "05-celtic-language",
    "web": "05-web",
    # 06 - Infrastructure + product
    "infrastructure": "06-infrastructure",
    "product": "06-product",
    # 07 - Skills + standards
    "skills": "07-skills",
    "standards": "07-standards",
    # 08 - Examples + screenshots
    "examples": "08-examples",
    "screenshots": "08-screenshots",
}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass(frozen=True)
class CanonicalDoc:
    domain: str
    path: Path
    title: str
    description: str
    body: str
    frontmatter: dict

    @property
    def dataset_name(self) -> str:
        return f"docs-{self.domain}"


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


def load_domain_docs(domain: str) -> list[CanonicalDoc]:
    dir_name = DOMAIN_TO_DIR[domain]
    domain_dir = DOCS_ROOT / dir_name
    if not domain_dir.is_dir():
        return []
    docs: list[CanonicalDoc] = []
    # Recursive glob — some domains (01-cognee, 06-infrastructure) have
    # nested subdirs with additional canonical docs.
    for path in sorted(domain_dir.rglob("*.md")):
        # Skip files inside node_modules, .venv, or hidden dirs
        if any(part.startswith(".") for part in path.parts):
            continue
        if "node_modules" in path.parts or ".venv" in path.parts:
            continue
        # Robust read: try UTF-8 first, fall back to latin-1 (some Windows-saved
        # .md files in 06-infrastructure/ have non-UTF-8 bytes)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="latin-1")
        fm, body = strip_frontmatter(text)
        docs.append(
            CanonicalDoc(
                domain=domain,
                path=path,
                title=fm.get("title", path.stem),
                description=fm.get("description", ""),
                body=body,
                frontmatter=fm,
            )
        )
    return docs


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
    """Create the dataset if it doesn't exist; return its UUID.

    Cognee v1 REST API uses POST /api/v1/datasets with {name, description}
    and returns {id, name, ...}. Dataset names cannot contain dots or spaces.
    """
    response = get_json("/api/v1/datasets")
    payload = response if isinstance(response, list) else response.get("data", response)
    for d in payload:
        if d.get("name") == dataset_name:
            return d["id"]
    created = post_json(
        "/api/v1/datasets",
        {"name": dataset_name, "description": f"Cianfhoghlaim docs - {dataset_name}"},
    )
    return created["id"]


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


def ingest_doc(doc: CanonicalDoc, dataset_id: str) -> dict:
    text = f"# {doc.title}\n\n{''.join(doc.body)}"
    # NOTE: Cognee v1 REST API uses camelCase: datasetId
    # The /api/v1/add endpoint takes multipart form data, not JSON. For
    # simplicity we use /api/v1/datasets/{id}/data which accepts JSON.
    return post_json(
        f"/api/v1/datasets/{dataset_id}/data",
        {
            "data": text,
        },
    )


def cognify_dataset(dataset_name: str, dataset_id: str) -> dict:
    response = post_json(
        "/api/v1/cognify",
        {"dataset_ids": [dataset_id]},
        timeout=600,
    )
    run_id = response.get("pipeline_run_id") or response.get("id") or response.get("runId")
    if run_id and isinstance(run_id, str):
        return wait_for_cognify(run_id)
    return response


def domain_summary(domain: str) -> dict:
    docs = load_domain_docs(domain)
    total_bytes = sum(len(d.body.encode("utf-8")) for d in docs)
    return {
        "domain": domain,
        "datasetName": f"docs-{domain}",
        "doc_count": len(docs),
        "byte_count": total_bytes,
        "docs": [
            {
                "title": d.title,
                "path": str(d.path.relative_to(REPO_ROOT)),
                "byte_count": len(d.body.encode("utf-8")),
            }
            for d in docs
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", choices=list(DOMAIN_TO_DIR), help="Single domain to ingest")
    parser.add_argument("--all", action="store_true", help="Ingest all 19 domains")
    parser.add_argument("--no-cognify", action="store_true", help="Store data only; skip cognify")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without executing")
    parser.add_argument("--summary", action="store_true", help="Print per-domain summary and exit")
    args = parser.parse_args()

    if not (args.domain or args.all):
        parser.error("specify --domain <name> or --all")

    domains = list(DOMAIN_TO_DIR) if args.all else [args.domain]

    if args.summary:
        for domain in domains:
            print(json.dumps(domain_summary(domain), indent=2))
        return 0

    # Probe Cognee REST API once before processing
    try:
        get_json("/health")
    except requests.exceptions.ConnectionError:
        print(
            f"ERROR: Cognee REST API is not reachable at {COGNEE_API_URL}.\n"
            f"       Start the Cognee stack first: "
            f"`cd infrastructure/stacks/machine_learning/cognee && docker compose up -d`\n"
            f"       Or use the embedded MCP tools (`cognee_remember`, `cognee_cognify`) directly.",
            file=sys.stderr,
        )
        return 1

    if not LLM_API_KEY and not args.no_cognify:
        print(
            "WARN: LLM_API_KEY not set. Phase 2 (cognify) will fail. "
            "Re-run with --no-cognify to store data only, or set LLM_API_KEY and retry.",
            file=sys.stderr,
        )

    if args.dry_run:
        for domain in domains:
            s = domain_summary(domain)
            print(f"[{s['dataset_name']}] {s['doc_count']} docs, {s['byte_count']} bytes")
            for d in s["docs"]:
                print(f"  - {d['path']} ({d['byte_count']} bytes)")
        return 0

    total_added = 0
    for domain in domains:
        docs = load_domain_docs(domain)
        if not docs:
            print(f"[{domain}] no docs found", file=sys.stderr)
            continue
        dataset_name = docs[0].dataset_name
        # Create the dataset (idempotent)
        try:
            dataset_id = ensure_dataset(dataset_name)
            print(f"[{domain}] dataset {dataset_name} -> {dataset_id}")
        except requests.HTTPError as exc:
            print(
                f"[{domain}] failed to create dataset: HTTP {exc.response.status_code if exc.response else '?'} - {exc}",
                file=sys.stderr,
            )
            continue
        print(f"[{domain}] ingesting {len(docs)} canonical docs into {dataset_name}")
        for doc in docs:
            try:
                result = ingest_doc(doc, dataset_id)
                total_added += 1
                print(f"  + {doc.path.name} -> {result.get('data_id', result.get('id', 'queued'))}")
            except requests.HTTPError as exc:
                print(
                    f"  ! {doc.path.name}: HTTP {exc.response.status_code if exc.response else '?'} - {exc}",
                    file=sys.stderr,
                )
        if args.no_cognify:
            print(f"[{domain}] --no-cognify set, skipping graph build")
            continue
        if not LLM_API_KEY:
            print(
                f"[{domain}] skipping cognify: LLM_API_KEY not set",
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
