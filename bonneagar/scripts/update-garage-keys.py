#!/usr/bin/env python3
"""Update the lakehouse-garage access keys in Infisical with the real
Garage-generated values."""
import json
import os
import sys
import urllib.request

TOKEN = os.environ.get("INFISICAL_TOKEN", "")
PROJECT_ID = os.environ.get("INFISICAL_PROJECT_ID", "")
API_URL = os.environ.get("INFISICAL_API_URL", "http://localhost:8081/api")

GARAGE_ACCESS_KEY_ID = "GK3b427f19ad3fd54647e9a1ac"
GARAGE_SECRET_ACCESS_KEY = "6fd34220da97ec87dcc8707e0b930f6d7a431df9742ccf556cc801c87e245435"


def upsert(path, key, value):
    url = f"{API_URL}/v3/secrets/raw/{key}"
    body = json.dumps({
        "environment": "dev",
        "workspaceId": PROJECT_ID,
        "secretPath": f"/{path}",
        "secretValue": value,
        "type": "shared",
    }).encode()
    # Try PATCH first (update); fall back to POST (create)
    for method in ("PATCH", "POST"):
        req = urllib.request.Request(url, data=body, method=method, headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        })
        try:
            with urllib.request.urlopen(req) as resp:
                d = json.loads(resp.read())
                if d.get("secret", {}).get("secretValue") or d.get("message"):
                    print(f"  [ok] {path}/{key} ({method})")
                    return
                print(f"  [FAIL] {path}/{key} -> {d}")
                return
        except urllib.error.HTTPError as e:
            if e.code == 400 and "already exists" in e.read().decode("utf-8", errors="replace").lower():
                continue  # try POST
            body = e.read().decode("utf-8", errors="replace")[:200]
            print(f"  [FAIL] {path}/{key} -> HTTP {e.code}: {body}")
            return
    print(f"  [FAIL] {path}/{key} -> both PATCH and POST failed")


def main():
    if not TOKEN or not PROJECT_ID:
        print("ERROR: source the infisical bootstrap file first", file=sys.stderr)
        sys.exit(1)
    print("---Updating lakehouse-garage secrets---")
    upsert("lakehouse-garage", "access_key_id", GARAGE_ACCESS_KEY_ID)
    upsert("lakehouse-garage", "secret_access_key", GARAGE_SECRET_ACCESS_KEY)
    print("\n[ok] done")


if __name__ == "__main__":
    main()