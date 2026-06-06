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
    "architecture": "01-platform-architecture",
    "data-platform": "02-data-platform",
    "agents": "03-agents",
    "ai-ml": "04-ai-ml",
    "web": "05-web",
    "product": "06-product",
    "standards": "07-standards",
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
    for path in sorted(domain_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
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


def ingest_doc(doc: CanonicalDoc) -> dict:
    text = f"# {doc.title}\n\n{''.join(doc.body)}"
    return post_json(
        "/api/v1/add",
        {
            "data": text,
            "dataset_name": doc.dataset_name,
        },
    )


def cognify_dataset(dataset_name: str) -> dict:
    response = post_json(
        "/api/v1/cognify",
        {"dataset_name": dataset_name},
        timeout=600,
    )
    run_id = response.get("pipeline_run_id") or response.get("id")
    if run_id and isinstance(run_id, str):
        return wait_for_cognify(run_id)
    return response


def domain_summary(domain: str) -> dict:
    docs = load_domain_docs(domain)
    total_bytes = sum(len(d.body.encode("utf-8")) for d in docs)
    return {
        "domain": domain,
        "dataset_name": f"docs-{domain}",
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
    parser.add_argument("--all", action="store_true", help="Ingest all 7 domains")
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
        print(f"[{domain}] ingesting {len(docs)} canonical docs into {docs[0].dataset_name}")
        for doc in docs:
            try:
                result = ingest_doc(doc)
                total_added += 1
                print(f"  + {doc.path.name} -> {result.get('data_id', 'queued')}")
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
            result = cognify_dataset(docs[0].dataset_name)
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
