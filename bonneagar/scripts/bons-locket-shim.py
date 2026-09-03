#!/usr/bin/env python3
"""
cianfhoghlaim-locket-shim.py — v0.2.0

A drop-in replacement for the locket v0.17.3 sidecar that uses the
CORRECT camelCase field names for the Infisical v0.161+ REST API.

Why this exists: locket v0.17.3 ships snake_case query params
(project_id, secret_path, secret_type) but Infisical v0.161+ requires
camelCase (projectId, secretPath, secretType). Every call returns 422,
the locket falls back to "passthrough" mode, and writes the raw
{{ infisical://... }} template to disk instead of the resolved values.

The next locket release (v0.18.0-rc.1) has the fix in source
(#[serde(rename_all = "camelCase")] in infisical.rs:293). Until that
shipped image is pulled into the agent-platform clusters, this shim
performs the same job correctly.

Usage as a sidecar in any bonneagar/*/sidecar.yaml:
  image: ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0
  environment:
    INFISICAL_URL: http://host.docker.internal:8081
    INFISICAL_CLIENT_ID: <bons-iac uuid>
    INFISICAL_DEFAULT_PROJECT_ID: <workspace uuid>
    INFISICAL_DEFAULT_ENVIRONMENT: dev
    INFISICAL_DEFAULT_PATH: /<stack-folder>
  volumes:
    - ./secrets.env:/templates/secrets.env:ro
    - stack-secrets:/run/secrets/locket
  command: ["watch"]  # or one-shot

This is NOT a permanent replacement — the locket upstream will fix
this in v0.18.0. We use this until the GHCR image is updated.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

REF_RE = re.compile(
    r"\{\{\s*infisical:///([A-Za-z0-9_.\-]+)\?(?P<q>[^}\s]+)\s*\}\}"
)


def parse_refs(template: str) -> list[tuple[str, dict[str, str]]]:
    """Return [(key, {path, env, project_id, ...})] for every {{ infisical:///KEY?path=/X&... }}."""
    out: list[tuple[str, dict[str, str]]] = []
    for m in REF_RE.finditer(template):
        key = m.group(1)
        q = dict(urllib.parse.parse_qsl(m.group("q"), keep_blank_values=True))
        out.append((key, q))
    return out


def fetch_secret(
    *,
    infisical_url: str,
    client_id: str,
    client_secret: str,
    project_id: str,
    environment: str,
    secret_key: str,
    secret_path: str,
    secret_type: str = "shared",
) -> str | None:
    """Call Infisical's /api/v4/secrets/<KEY> with the CORRECT camelCase field names.

    Returns the secret value on 200; None on 404.
    """
    base = infisical_url.rstrip("/")
    qs = urllib.parse.urlencode(
        {
            "projectId": project_id,
            "environment": environment,
            "secretPath": secret_path,
            "type": secret_type,
            "expandSecretReferences": "true",
            "includeImports": "true",
        }
    )
    url = f"{base}/api/v4/secrets/{urllib.parse.quote(secret_key, safe='')}?{qs}"

    # Universal Auth login
    auth_url = f"{base}/api/v1/auth/universal-auth/login"
    auth_body = json.dumps(
        {"clientId": client_id, "clientSecret": client_secret}
    ).encode()
    auth_req = urllib.request.Request(
        auth_url,
        data=auth_body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(auth_req, timeout=10) as resp:
        auth_data = json.load(resp)
    access_token = auth_data["accessToken"]

    # Fetch the secret
    sec_req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    try:
        with urllib.request.urlopen(sec_req, timeout=10) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        body = e.read().decode("utf-8", errors="replace")[:200]
        print(
            f"  warn: GET {secret_key} -> {e.code} {body}",
            file=sys.stderr,
        )
        return None
    return data.get("secret", {}).get("secretValue")


def render(template: str, secrets: dict[str, str], project_id: str) -> str:
    """Replace every {{ infisical:///KEY?... }} with the resolved value."""
    def repl(m: re.Match[str]) -> str:
        key = m.group(1)
        if key in secrets:
            return secrets[key]
        # No value resolved (404 or error) — leave a comment for debugging.
        return f"# locket-shim: unresolved {m.group(0)}"

    return REF_RE.sub(repl, template)


def write_atomic(path: Path, content: str) -> None:
    """Write to a temp file in the same dir + rename to avoid partial reads."""
    import tempfile
    fd, tmp_name = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=str(path.parent),
    )
    os.close(fd)
    tmp = Path(tmp_name)
    tmp.write_text(content)
    os.chmod(tmp, 0o644)  # match the locket `chmod init` convention
    os.replace(tmp, path)


def process_once(args: argparse.Namespace) -> dict[str, str]:
    src = Path(args.src)
    dst = Path(args.dst)
    template = src.read_text()
    refs = parse_refs(template)
    if not refs:
        # No infisical references — just copy the template.
        write_atomic(dst / "secrets.env", template)
        return {}

    print(
        f"  [shim] {len(refs)} reference(s) in {src.name}",
        file=sys.stderr,
    )

    with open(args.client_secret_file) as f:
        client_secret = f.read().strip()

    secrets: dict[str, str] = {}
    for key, opts in refs:
        secret_path = opts.get("path", args.default_path)
        env = opts.get("env", args.environment)
        proj = opts.get("project_id", args.project_id)
        sec_type = opts.get("type", "shared")
        value = fetch_secret(
            infisical_url=args.infisical_url,
            client_id=args.client_id,
            client_secret=client_secret,
            project_id=proj,
            environment=env,
            secret_key=key,
            secret_path=secret_path,
            secret_type=sec_type,
        )
        if value is not None:
            secrets[key] = value
            print(
                f"  [shim]   resolved {secret_path}/{key} = {value[:20]}...",
                file=sys.stderr,
            )
        else:
            print(
                f"  [shim]   unresolved {secret_path}/{key}",
                file=sys.stderr,
            )

    resolved = render(template, secrets, args.project_id)
    write_atomic(dst / "secrets.env", resolved)
    return secrets


def parse_env_args() -> argparse.Namespace:
    """Build argparse from env vars (matches the upstream locket's design)."""
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument(
        "--infisical-url",
        default=os.environ.get(
            "INFISICAL_URL", "https://app.infisical.com"
        ),
    )
    p.add_argument(
        "--client-id",
        default=os.environ.get("INFISICAL_CLIENT_ID", ""),
    )
    p.add_argument(
        "--client-secret-file",
        default=os.environ.get(
            "LOCKET_CLIENT_SECRET_FILE", "/run/secrets/infisical_secret"
        ),
    )
    p.add_argument(
        "--project-id",
        default=os.environ.get("INFISICAL_DEFAULT_PROJECT_ID", ""),
    )
    p.add_argument(
        "--environment",
        default=os.environ.get("INFISICAL_DEFAULT_ENVIRONMENT", "dev"),
    )
    p.add_argument(
        "--default-path",
        default=os.environ.get("INFISICAL_DEFAULT_PATH", "/"),
    )
    p.add_argument(
        "--src",
        default=os.environ.get("LOCKET_SRC", "/templates/secrets.env"),
    )
    p.add_argument(
        "--dst",
        default=os.environ.get("LOCKET_DST", "/run/secrets/locket"),
    )
    p.add_argument(
        "--mode",
        choices=("one-shot", "watch"),
        default=os.environ.get("LOCKET_MODE", "watch"),
    )
    p.add_argument(
        "--debounce",
        type=float,
        default=float(os.environ.get("LOCKET_DEBOUNCE", "2")),
    )
    return p.parse_args()


def main() -> int:
    args = parse_env_args()
    if not args.client_id or not args.project_id:
        print(
            "  [shim] error: INFISICAL_CLIENT_ID and INFISICAL_DEFAULT_PROJECT_ID must be set",
            file=sys.stderr,
        )
        return 78

    src = Path(args.src)
    if src.is_dir():
        # Watch all *.env files in the directory
        files = sorted(src.glob("*.env"))
    else:
        files = [src]

    if args.mode == "one-shot":
        for f in files:
            args.src = str(f)
            process_once(args)
        return 0

    # Watch mode: re-process on file mtime change
    last_mtime: dict[Path, float] = {}
    while True:
        for f in files:
            try:
                mtime = f.stat().st_mtime
            except FileNotFoundError:
                continue
            if last_mtime.get(f) != mtime:
                last_mtime[f] = mtime
                try:
                    args.src = str(f)
                    process_once(args)
                except Exception as e:
                    print(f"  [shim] error: {e}", file=sys.stderr)
        time.sleep(args.debounce)


if __name__ == "__main__":
    sys.exit(main())