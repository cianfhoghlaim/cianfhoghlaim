#!/usr/bin/env python3
"""
cianfhoghlaim-locket-shim.py — v0.2.1

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

FORMAT (v0.2.1): The actual canonical secrets.env format is the
"unwrapped" form `KEY=infisical://<workspace>/<path>/<key>` — NO
`{{ }}` jinja braces and NO `?path=` query string. The workspace
(typically `dev-baile`) is the Infisical project slug, and the
remaining slash-separated path + key is the secret path inside that
project. The path defaults to INFISICAL_DEFAULT_PATH (the stack
folder) when only a key is present, e.g. `infisical://dev-baile/litellm/master_key`
resolves to workspace=dev-baile, path=/litellm, key=master_key.

The Jinja form `{{ infisical:///KEY?path=/X&env=dev }}` is still
accepted for backward compatibility with older secrets.env files.

Usage as a sidecar in any bonneagar/*/sidecar.yaml:
  image: ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.1
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

# Two regex flavors are accepted:
#   1. Unwrapped (canonical, post-v0.2.1):
#      KEY=infisical://<workspace>/<path>/<key>
#      e.g. LITELLM_MASTER_KEY=infisical://dev-baile/litellm/master_key
#      The workspace = Infisical project; the path + key = the secret
#      lookup. If the URI has only 1 segment after workspace
#      (e.g. `infisical://dev-baile/master_key`), the path defaults
#      to INFISICAL_DEFAULT_PATH (set per-sidecar).
#   2. Jinja (legacy, still supported):
#      {{ infisical:///KEY?path=/X&env=dev&project_id=... }}
#      with `?path=` and friends as overrides.
UNWRAPPED_RE = re.compile(
    r"infisical://(?P<workspace>[A-Za-z0-9_\-]+)/(?P<rest>[A-Za-z0-9_.\-/]+)"
)
JINJA_RE = re.compile(
    r"\{\{\s*infisical:///([A-Za-z0-9_.\-]+)\?(?P<q>[^}\s]+)\s*\}\}"
)


def parse_refs(template: str) -> list[tuple[str, dict[str, str]]]:
    """Return [(key, {path, env, project_id, workspace, ...})] for every match.

    For the unwrapped format the tuple is (key, {'workspace': ..., 'path': ..., 'rest': ...}).
    For the jinja format it's (key, {<query-params>}).
    The caller (process_once) reads `workspace`/`path`/`rest` from opts to
    resolve the secret.
    """
    out: list[tuple[str, dict[str, str]]] = []
    # Unwrapped format first (canonical).
    for m in UNWRAPPED_RE.finditer(template):
        workspace = m.group("workspace")
        rest = m.group("rest").strip("/")
        # If the rest is a single segment (no slash), treat it as the key
        # with path defaulted by the caller. Otherwise split into path/key
        # at the rightmost slash.
        if "/" in rest:
            path, key = rest.rsplit("/", 1)
            path = "/" + path
        else:
            path = None  # caller will default to args.default_path
            key = rest
        out.append((key, {"workspace": workspace, "path": path or "", "rest": rest}))
    # Jinja format (legacy).
    for m in JINJA_RE.finditer(template):
        key = m.group(1)
        q = dict(urllib.parse.parse_qsl(m.group("q"), keep_blank_values=True))
        q.setdefault("workspace", "")
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
    """Replace every infisical://... reference with the resolved value.

    Handles both the unwrapped form (KEY=infisical://workspace/path/key) and
    the legacy jinja form ({{ infisical:///KEY?path=... }}).
    """
    def unwrapped_repl(m: re.Match[str]) -> str:
        workspace = m.group("workspace")
        rest = m.group("rest").strip("/")
        # Mirror the parse_refs() logic so the key matches.
        if "/" in rest:
            _, key = rest.rsplit("/", 1)
        else:
            key = rest
        if key in secrets:
            return secrets[key]
        return f"# locket-shim: unresolved {m.group(0)}"

    def jinja_repl(m: re.Match[str]) -> str:
        key = m.group(1)
        if key in secrets:
            return secrets[key]
        return f"# locket-shim: unresolved {m.group(0)}"

    template = UNWRAPPED_RE.sub(unwrapped_repl, template)
    template = JINJA_RE.sub(jinja_repl, template)
    return template


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

    # Load the fallback file (the 15-min hydrated .env mirror) once.
    # Per the env-var fallback pattern (2026-08-21 openspec change), this
    # file is the OCI Infisical source-of-truth with bounded drift (~15 min).
    fallback: dict[str, str] = {}
    fallback_path = Path(getattr(args, "fallback_file", ""))
    if fallback_path.is_file():
        try:
            for line in fallback_path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                fallback[k.strip()] = v.strip().strip('"').strip("'")
            print(
                f"  [shim]   loaded {len(fallback)} fallback(s) from {fallback_path}",
                file=sys.stderr,
            )
        except Exception as e:
            print(
                f"  [shim]   warn: could not read fallback file {fallback_path}: {e}",
                file=sys.stderr,
            )

    secrets: dict[str, str] = {}
    for key, opts in refs:
        # Unwrapped form uses opts['path'] (may be empty -> default).
        # Jinja form uses opts['path'] from query string or defaults.
        secret_path = opts.get("path") or args.default_path
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
        elif key in fallback:
            secrets[key] = fallback[key]
            print(
                f"  [shim]   fallback {secret_path}/{key} = {fallback[key][:20]}...",
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
    p.add_argument(
        "--fallback-file",
        default=os.environ.get(
            "LOCKET_FALLBACK_FILE", "/run/secrets/locket/env-fallback.env"
        ),
        help=(
            "Path to a read-only .env-style file with pre-resolved KEY=VALUE pairs. "
            "When the OCI Infisical is unreachable, each unresolved KEY is looked "
            "up here. Per the env-var fallback pattern added by the 2026-08-21 "
            "openspec change; the file is the 15-min hydrated mirror of the OCI vault."
        ),
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