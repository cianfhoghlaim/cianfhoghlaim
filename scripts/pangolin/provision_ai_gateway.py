#!/usr/bin/env python3
"""scripts/pangolin/provision_ai_gateway.py — provision the overlapping Public+Private AI Gateway.

Per openspec/changes/2026-09-25-pangolin-aware-bunchloch-vlm-deploy-v1/
specs/pangolin-ai-gateway-vision-bundle/spec.md.

Steps:
  1. Create 1 Custom provider per self-hosted VLM upstream
     (currently `unsloth-local`; later `invokeai-local` + `comfyui-local`)
  2. Create 2 overlapping AI Gateway resources on ai.cianfhoghlaim.ie
     - private (role=Member, auth=client identity, key=`none`)
     - public  (auth=virtual API key, role=CI-Agent, $5/day + $50/day budgets)
  3. Verify the gateway over the Pangolin.app tunnel

Usage:
  PANGOLIN_API_KEY=<fresh_key> uv run python scripts/pangolin/provision_ai_gateway.py
  PANGOLIN_API_KEY=<fresh_key> uv run python scripts/pangolin/provision_ai_gateway.py --dry-run

The API key is minted at https://pangolin.cianfhoglam.ie → Settings → API Keys.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.parse import urljoin

import urllib.request


PANGOLIN_URL = os.environ.get("PANGOLIN_URL", "https://pangolin.cianfhoghlaim.ie")
PANGOLIN_ORG_ID = os.environ.get("PANGOLIN_ORG_ID", "cianfhoghlaim")
API_KEY = os.environ.get("PANGOLIN_API_KEY", "")

PROVIDERS = [
    {
        "slug": "unsloth-local",
        "name": "unsloth-serve (bunchloch CPU/MPS, Qwen3-VL-8B Q4_K_M)",
        "api_base": "http://192.168.148.5:8889/v1",
        "capability": "openai",
        "notes": (
            "Docker network IP for the unsloth-serve container on the cianfhoghlaim "
            "docker network. Reachable from the bunchloch host AND from any container "
            "on the same network (e.g. litellm, newt, opencode). "
            "Find the current IP with: docker inspect unsloth-serve --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{\"\\n\"}}{{end}}'"
        ),
    },
]

RESOURCES = [
    {
        "name": "ai-private",
        "fqdn": "ai.cianfhoghlaim.ie",
        "type": "ai-gateway",
        "auth": "client_identity",
        "roles": ["Member"],
        "providers": ["unsloth-local"],
        "key_placeholder": "none",
        "notes": "Reachable only via Pangolin.app / Pangolin CLI tunnel.",
    },
    {
        "name": "ai-public",
        "fqdn": "ai.cianfhoghlaim.ie",
        "type": "ai-gateway",
        "auth": "virtual_api_key",
        "roles": ["CI-Agent"],
        "providers": ["unsloth-local"],
        "budgets": [
            {"scope": "role", "role": "CI-Agent", "limit_usd_per_day": 5.0},
            {"scope": "global", "limit_usd_per_day": 50.0},
        ],
        "notes": "Reachable from anywhere; requires virtual API key per call.",
    },
]


def api(method: str, path: str, body: dict | None = None) -> dict:
    """Call the Pangolin REST API."""
    url = urljoin(PANGOLIN_URL + "/", path.lstrip("/"))
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8") or "{}")


def list_providers() -> list[dict]:
    return api("GET", f"/api/v1/org/{PANGOLIN_ORG_ID}/ai-providers").get("data", [])


def create_provider(p: dict, dry_run: bool) -> dict:
    body = {
        "name": p["name"],
        "kind": "custom",
        "url": p["api_base"],
        "capabilities": [p["capability"]],
    }
    if dry_run:
        return {"dry_run": True, "would_post": "/api/v1/org/{PANGOLIN_ORG_ID}/ai-providers", "body": body}
    return api("POST", f"/api/v1/org/{PANGOLIN_ORG_ID}/ai-providers", body)


def list_resources() -> list[dict]:
    return api("GET", f"/api/v1/org/{PANGOLIN_ORG_ID}/resources").get("data", [])


def create_resource(r: dict, dry_run: bool) -> dict:
    body = {
        "name": r["name"],
        "type": r["type"],
        "fullDomain": r["fqdn"],
        "auth": r["auth"],
        "roles": r["roles"],
        "providers": r["providers"],
        "keyPlaceholder": r["key_placeholder"],
    }
    if "budgets" in r:
        body["budgets"] = r["budgets"]
    if dry_run:
        return {"dry_run": True, "would_post": f"/api/v1/org/{PANGOLIN_ORG_ID}/resources", "body": body}
    return api("POST", f"/api/v1/org/{PANGOLIN_ORG_ID}/resources", body)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print what would be done without making changes")
    args = parser.parse_args()

    if not API_KEY:
        print("ERROR: PANGOLIN_API_KEY not set", file=sys.stderr)
        print("Mint a fresh key at: https://pangolin.cianfhoghlaim.ie → Settings → API Keys", file=sys.stderr)
        return 2

    if args.dry_run:
        print(f"DRY RUN — would provision against {PANGOLIN_URL} as org {PANGOLIN_ORG_ID}")
        print("\n=== Step 1: Custom providers (would create) ===")
        for p in PROVIDERS:
            print(f"  + {p['slug']} → {p['api_base']} (capability: {p['capability']})")
        print("\n=== Step 2: AI Gateway resources (would create) ===")
        for r in RESOURCES:
            print(f"  + {r['name']} on {r['fqdn']} (auth: {r['auth']}, roles: {r['roles']})")
        print("\n=== Step 3: Verification ===")
        print("After provisioning, run over the Pangolin.app tunnel:")
        print("  curl -s -H 'Authorization: Bearer none' https://ai.cianfhoghlaim.ie/v1/models | jq .")
        return 0

    print("\n=== Step 1: Custom providers ===")
    existing = list_providers()
    existing_slugs = {p.get("slug") for p in existing}
    for p in PROVIDERS:
        if p["slug"] in existing_slugs:
            print(f"  ✓ {p['slug']} already exists")
            continue
        print(f"  + Creating {p['slug']} → {p['api_base']}")
        result = create_provider(p, args.dry_run)
        print(f"    {json.dumps(result, indent=2)[:500]}")

    print("\n=== Step 2: AI Gateway resources ===")
    existing = list_resources()
    existing_names = {r.get("name") for r in existing}
    for r in RESOURCES:
        if r["name"] in existing_names:
            print(f"  ✓ {r['name']} already exists")
            continue
        print(f"  + Creating {r['name']} on {r['fqdn']}")
        result = create_resource(r, args.dry_run)
        print(f"    {json.dumps(result, indent=2)[:500]}")

    print("\n=== Step 3: Verification ===")
    print("Run over the Pangolin.app tunnel:")
    print("  curl -s -H 'Authorization: Bearer none' https://ai.cianfhoghlaim.ie/v1/models | jq .")
    return 0


if __name__ == "__main__":
    sys.exit(main())
