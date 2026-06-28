#!/usr/bin/env python3
"""Batch-ingest .md files into Cognee via HTTP API.

Usage:
    uv run python oideachais/scripts/cognee_http_ingest.py <directory> <dataset_name>
Example:
    uv run python oideachais/scripts/cognee_http_ingest.py ../docs/agents docs-agents
"""

import asyncio
import sys
from pathlib import Path

import aiohttp

COGNEE_URL = "http://localhost:8100"


async def login(session: aiohttp.ClientSession) -> str:
    """Register/login and get access token."""
    # Try to register first, then login
    payload = {
        "email": "admin@cianfhoghlaim.ie",
        "password": "kcg-docs-2024!",
    }
    try:
        async with session.post(f"{COGNEE_URL}/api/v1/auth/register", json=payload) as r:
            data = await r.json()
            print(f"  Register: {r.status} — {data.get('message', data)}")
    except Exception:
        pass  # Already registered

    async with session.post(f"{COGNEE_URL}/api/v1/auth/login", json=payload) as r:
        data = await r.json()
        token = data.get("access_token", "")
        print(f"  Login: {'OK' if token else 'FAILED'} (token: {token[:20]}...)")
        return token


async def add_documents(
    session: aiohttp.ClientSession,
    token: str,
    files: list[tuple[str, str]],  # [(filename, content), ...]
    dataset_name: str,
    batch_size: int = 10,
):
    """Add documents in batches via multipart form upload."""
    total = len(files)
    headers = {"Authorization": f"Bearer {token}"}

    for i in range(0, total, batch_size):
        batch = files[i : i + batch_size]
        form = aiohttp.FormData()

        for filename, content in batch:
            form.add_field(
                "data",
                content.encode("utf-8"),
                filename=filename,
                content_type="text/markdown",
            )

        form.add_field("datasetName", dataset_name)

        async with session.post(
            f"{COGNEE_URL}/api/v1/add", data=form, headers=headers
        ) as r:
            status = r.status
            text = await r.text()
            if status != 200:
                print(f"  ERROR batch {i // batch_size + 1}: {status} — {text[:200]}")

        processed = min(i + batch_size, total)
        pct = processed * 100 // total
        bar = "#" * (pct // 5) + "-" * (20 - pct // 5)
        print(f"  [{bar}] {processed}/{total} ({pct}%)")


async def ingest_directory(directory: str, dataset_name: str):
    root = Path(directory).resolve()
    if not root.is_dir():
        print(f"ERROR: {root} is not a directory")
        sys.exit(1)

    # Collect .md files
    md_files = sorted(root.rglob("*.md"))
    files = []
    for fp in md_files:
        try:
            content = fp.read_text()
            if len(content) < 10:
                continue
            rel = str(fp.relative_to(root))
            files.append((rel, content))
        except Exception as e:
            print(f"  SKIP {fp.name}: {e}")

    total = len(files)
    print(f"Ingesting {total} files from {root} -> dataset '{dataset_name}'")
    print(f"Cognee: {COGNEE_URL} | Batch size: 10")
    print("-" * 60)

    async with aiohttp.ClientSession() as session:
        token = await login(session)
        if not token:
            print("ERROR: Could not authenticate with Cognee")
            sys.exit(1)

        await add_documents(session, token, files, dataset_name, batch_size=10)

    print(f"DONE: {total} files added to dataset '{dataset_name}'")
    print(f"  Next: run cognify on {COGNEE_URL}/api/v1/cognify")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cognee_http_ingest.py <directory> <dataset_name>")
        sys.exit(1)
    asyncio.run(ingest_directory(sys.argv[1], sys.argv[2]))
