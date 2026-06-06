#!/usr/bin/env python3
"""
render-secrets.py — Fetch secrets from Infisical API and generate resolved .env files.

Usage:
    python3 render-secrets.py --folder /vikunja > resolved.env
    python3 render-secrets.py --folder /n8n > resolved.env
    python3 render-secrets.py --folder /calcom > resolved.env

Environment variables (or use --flags):
    INFISICAL_URL          — self-hosted Infisical URL (default: http://localhost:8081)
    INFISICAL_CLIENT_ID    — Universal Auth client ID
    INFISICAL_CLIENT_SECRET— Universal Auth client secret
    INFISICAL_PROJECT_ID   — project/workspace ID
    INFISICAL_ENVIRONMENT  — environment slug (default: dev-baile)
"""

import urllib.request, urllib.error, json, os, sys, argparse

def login(url, client_id, client_secret):
    data = json.dumps({"clientId": client_id, "clientSecret": client_secret}).encode()
    req = urllib.request.Request(
        f"{url}/api/v1/auth/universal-auth/login",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    resp = json.loads(urllib.request.urlopen(req).read())
    return resp["accessToken"]

def list_secrets(url, token, project_id, env, folder):
    """Fetch secrets from Infisical v3 API."""
    # The v3 list endpoint
    try:
        list_url = f"{url}/api/v3/secrets?workspaceId={project_id}&environment={env}&path={folder}&include_imports=false"
        req = urllib.request.Request(list_url, headers={"Authorization": f"Bearer {token}"})
        resp = json.loads(urllib.request.urlopen(req).read())
        secrets = resp.get("secrets", [])
        return {s["secretKey"]: s.get("secretValue", "") for s in secrets}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  Error fetching secrets for {folder}: HTTP {e.code}", file=sys.stderr)
        return {}

def render_template(template_path, secrets):
    """Replace {{ KEY }} placeholders with secret values."""
    with open(template_path, "r") as f:
        content = f.read()
    
    for key, value in secrets.items():
        content = content.replace("{{ " + key + " }}", value)
        content = content.replace("{{ " + key.upper() + " }}", value)
    
    return content

def main():
    parser = argparse.ArgumentParser(description="Render secrets from Infisical into .env files")
    parser.add_argument("--folder", required=True, help="Infisical folder path (e.g. /vikunja)")
    parser.add_argument("--url", default=os.environ.get("INFISICAL_URL", "http://localhost:8081"))
    parser.add_argument("--client-id", default=os.environ.get("INFISICAL_CLIENT_ID", ""))
    parser.add_argument("--client-secret", default=os.environ.get("INFISICAL_CLIENT_SECRET", ""))
    parser.add_argument("--project-id", default=os.environ.get("INFISICAL_PROJECT_ID", "f3cff583-b74b-4804-b9d3-db8b68885236"))
    parser.add_argument("--env", default=os.environ.get("INFISICAL_ENVIRONMENT", "dev-baile"), dest="environment")
    parser.add_argument("--template", help="Path to secrets.env template file to render")
    parser.add_argument("--output", help="Output file (default: stdout)")
    args = parser.parse_args()

    token = login(args.url, args.client_id, args.client_secret)
    secrets = list_secrets(args.url, token, args.project_id, args.environment, args.folder)
    
    if not secrets:
        print(f"# WARNING: No secrets found at {args.folder}", file=sys.stderr)
    
    output_lines = [f"# Rendered from Infisical {args.folder} ({args.environment})"]
    for key, value in sorted(secrets.items()):
        output_lines.append(f"{key}={value}")
    
    output_text = "\n".join(output_lines)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(output_text)
        print(f"Wrote {len(secrets)} secrets to {args.output}", file=sys.stderr)
    else:
        print(output_text)

if __name__ == "__main__":
    main()
