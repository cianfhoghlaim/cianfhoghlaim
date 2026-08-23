# Auth credential priority chain — design note

## Why this order?

The pipeline resolves two secrets: `OOG_STUDENT_ID` and `OOG_STUDENT_PASSWORD`.
Three candidate backends exist in the wider Cianfhoghlaim platform:

| Backend | Default in our setup? | Used by our runner? |
|---|---|---|
| **Self-hosted Infisical** | ✅ | ✅ — primary |
| Local `.env` file | ✅ | ✅ — fallback when Infisical absent |
| 1Password CLI (`op`) | ❌ | ❌ — doc-only option for cloners |

The choice mirrors how the rest of the platform already serves vision-language
models:

```
VM serving chain (VLM example):              Secret chain (this design):
─────────────────────────────              ───────────────────────────
1. Unsloth Studio (self-hosted GPU)         1. Self-hosted Infisical
2. LightLM (local LLM)                      2. Local .env file
3. Commercial Gemini API                     3. 1Password CLI (doc-only)
```

The principle is **local first, remote last**. Both chains try
self-hosted before they touch a cloud provider, and both keep a plain
local fallback so that a developer who has never heard of Infisical
or 1Password can still run the pipeline with a 2-line `.env` edit.

## The chain, in detail

### Tier 1 — Self-hosted Infisical

Set these env vars to enable:

```bash
INFISICAL_TOKEN=<machine-identity-token>
INFISICAL_URL=https://infisical.internal.example.com
INFISICAL_PROJECT=uog-exam-pipeline
INFISICAL_ENV=dev        # or `staging`, `prod`
```

The resolver issues a single HTTP `GET` per missing secret:

```
GET ${INFISICAL_URL}/api/v3/secrets/raw/${SECRET_NAME}?projectId=${INFISICAL_PROJECT}&environment=${INFISICAL_ENV}
Authorization: Bearer ${INFISICAL_TOKEN}
```

- 200 → value returned, log `secrets_backend_resolved: backend="infisical"`.
- 404 → fall through to tier 2.
- 401/403 → log a warning and fall through (the token might be expired).
- Connection error → fall through, do not retry inside a single read.

### Tier 2 — Local `.env` file

The Pydantic `BaseSettings(env_file=".env")` pattern is already used by
`bonneagar/stacks/browser/sruth_browser/config.py::BrowserConfig`. We extend
that pattern with a thin wrapper `SecretsResolver.get(name)` so the BAML
extraction code doesn't need to know which backend won.

The `.env` keys are namespaced with `OOG_` to avoid collision with the
many other platform secrets:

```bash
OOG_STUDENT_ID=12345678
OOG_STUDENT_PASSWORD=fixture-only
```

The CI runner ships with `.env` containing `OOG_STUDENT_PASSWORD=fixture-only`.
That **does not count** as real credentials (see `UoGSsoConfig.has_real_credentials()`).

### Tier 3 — 1Password CLI (`op`) — **documented only**

We deliberately do **not** invoke `op read op://...` from the runner. The
reason is operational, not technical:

- The runner container may or may not have `op` installed.
- `OP_SERVICE_ACCOUNT_TOKEN` is a long-lived bearer; storing it in CI
  means another surface to rotate.
- Feature parity with Infisical (path templating, dynamic secrets) is
  not needed for a single-user thesis pipeline.

For cloners who prefer 1Password over Infisical, the design note
documents the manual swap:

```python
# In bonneagar/stacks/browser/sruth_browser/core/secrets.py

def get_op_secret(name: str) -> str | None:
    """1Password CLI integration — disabled by default. See
    spec/design/auth-credential-priority-chain.md."""
    import subprocess
    try:
        out = subprocess.check_output(
            ["op", "read", f"op://Private/University SSO/{name}"],
            stderr=subprocess.DEVNULL,
            timeout=2.0,
        )
        return out.decode().strip()
    except Exception:
        return None
```

…then re-order the `_resolve()` chain in `SecretsResolver` to put
`get_op_secret` above `_get_env_secret`. The default shipped in the repo
keeps Infisical → `.env` so a fresh clone does not unexpectedly fail
with an `op not found` error.

## Log-once

The resolver emits exactly one `secrets_backend_resolved` log line per
process (per secret name), via a `functools.lru_cache` wrapper, so the
extractor batch logs don't drown in noise.

## What this design does NOT do

- Does not introduce a new Pydantic-settings library.
- Does not introduce a per-call async secret fetch (all are sync, cache
  for 60 s to amortise when the BAML batch loop hits
  `SecretsResolver.get` many times).
- Does not implement secret **rotation** — that is a separate ops concern.
