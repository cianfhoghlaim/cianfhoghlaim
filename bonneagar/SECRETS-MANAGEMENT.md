# Secrets Management with Infisical + mise

This document describes the automatic secret injection system for MCP servers and AI tools in the cianfhoghlaim monorepo.

## Overview

The system uses **mise hooks** combined with **Infisical CLI** to automatically inject secrets when entering the project directory. This enables seamless operation of MCP servers across Claude Code, Roo, and OpenCode without manual environment variable setup.

## Architecture

```
                    ┌─────────────────┐
                    │  Infisical      │
                    │  (dev-baile     │
                    │   vault)        │
                    └────────┬────────┘
                             │
                             │ infisical export
                             ▼
┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  .env.infisical    │────▶│    .env         │────▶│  Environment    │
│  (template) │     │  (resolved,     │     │  Variables      │
│             │     │   cached)       │     │                 │
└─────────────┘     └─────────────────┘     └────────┬────────┘
                                                     │
                             ┌───────────────────────┼───────────────────────┐
                             │                       │                       │
                             ▼                       ▼                       ▼
                    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
                    │  Claude Code    │     │     Roo         │     │   OpenCode      │
                    │  (.mcp.json)    │     │ (.roo/mcp.json) │     │ (.opencode.yaml)│
                    └─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Features

### Automatic Injection
- **Directory entry**: Secrets injected automatically when you `cd` into the repo
- **Directory exit**: Secrets unset when you leave (security hygiene)
- **No manual steps**: Works transparently with mise hooks

### Performance Optimization
- **Single API call**: Uses `infisical export` to resolve all secrets at once (~1s)
- **Smart caching**: Only re-injects when `.env.infisical` template changes
- **File locking**: Prevents race conditions in concurrent shells

| Method | Time | API Calls |
|--------|------|-----------|
| Individual `infisical secrets get` | ~12s | 12 |
| `infisical export` | ~1s | 1 |
| Cached `.env` | <10ms | 0 |

### Graceful Fallback
- Falls back to cached `.env` if Infisical CLI unavailable
- Works offline after initial injection
- Silent warnings (no shell spam)

### Security
- `.env` file permissions set to `600` (owner-only)
- Secrets never logged in plaintext
- Automatic cleanup on directory exit
- Template (`.env.infisical`) safe to commit; resolved (`.env`) gitignored

## Files

| File | Purpose | Git Status |
|------|---------|------------|
| `.env.infisical` | Infisical template with `{{ infisical://... }}` references | Committed |
| `.env` | Resolved secrets (auto-generated) | Ignored |
| `.env.lock` | Lock file for concurrent access | Ignored |
| `scripts/infisical-inject.sh` | Injection helper script | Committed |
| `mise.toml` | Hooks configuration | Committed |

## Configuration

### mise.toml Hooks

```toml
[hooks.enter]
shell = "bash"
script = """
source "{{ config_root }}/scripts/infisical-inject.sh"
"""

[hooks.leave]
shell = "bash"
script = """
source "{{ config_root }}/scripts/infisical-inject.sh" unset
"""
```

### Template Syntax (.env.infisical)

Uses Infisical's template syntax:
```bash
# Static values (no injection needed)
INFISICAL_HOST=http://132.145.27.89:8080

# Infisical references
BROWSERBASE_API_KEY={{ infisical://dev-baile/browserbase/api_key }}
BROWSERBASE_PROJECT_ID={{ infisical://dev-baile/browserbase/project_id }}
```

Reference format: `{{ infisical://vault/item/field }}`

## MCP Servers Configured

| Server | Environment Variables | Infisical Item |
|--------|----------------------|----------------|
| Browserbase | `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID` | `browserbase` |
| Firecrawl | `FIRECRAWL_API_KEY` | `firecrawl` |
| Z.ai | `Z_AI_API_KEY` | `zai` |
| HuggingFace | `HUGGINGFACE_TOKEN` | `huggingface` |
| Letta | `LETTA_API_KEY` | `letta` |
| Pydantic Gateway | `PYDANTIC_AI_GATEWAY_API_KEY` | `pydantic-gateway` |
| Logfire | `LOGFIRE_TOKEN` | `pydantic-logfire` |
| Langfuse | `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` | `langfuse` |
| Forgejo | `FORGEJO_TOKEN` | `forgejo` |
| ChunkHound | `OPENAI_API_KEY` | `openai` |
| Infisical | `INFISICAL_TOKEN` | `infisical_cianfhoghlaim` |

## Usage

### Initial Setup

1. **Install Infisical CLI** (already in mise.toml tools):
   ```bash
   mise install
   ```

2. **Authenticate with Infisical**:
   ```bash
   eval $(infisical login)
   ```

3. **Enter the directory** (triggers automatic injection):
   ```bash
   cd /Users/cliste/dev/cianfhoghlaim
   ```

4. **Verify secrets are loaded**:
   ```bash
   echo $BROWSERBASE_API_KEY
   ```

### Force Re-injection

If you update secrets in Infisical:
```bash
# Touch the template to invalidate cache
touch .env.infisical

# Re-enter directory (or source manually)
source scripts/infisical-inject.sh
```

Or delete the cached file:
```bash
rm .env && cd .. && cd -
```

### Manual Injection

For scripts or CI:
```bash
infisical export --in-file .env.infisical --out-file .env
source .env
```

## Adding New Secrets

1. **Create item in Infisical** (dev-baile vault):
   ```bash
   infisical secrets set --vault dev-baile \
     --category "API Credential" \
     --title "new-service" \
     "api_key[password]=your-key-here"
   ```

2. **Add to `.env.infisical` template**:
   ```bash
   NEW_SERVICE_API_KEY={{ infisical://dev-baile/new-service/api_key }}
   ```

3. **Update `scripts/infisical-inject.sh`** (add to `ENV_VARS` array):
   ```bash
   ENV_VARS=(
       ...
       "NEW_SERVICE_API_KEY"
   )
   ```

4. **Update MCP config** (if needed in `.mcp.json`):
   ```json
   "new-service": {
     "command": "...",
     "env": {
       "NEW_SERVICE_API_KEY": "${NEW_SERVICE_API_KEY}"
     }
   }
   ```

## Troubleshooting

### "Infisical CLI (op) not found"
- Ensure mise is activated: `eval "$(mise activate bash)"`
- Install op: `mise install op`

### "authorization timeout"
- Re-authenticate: `eval $(infisical login)`
- Check Infisical app is unlocked

### "could not find item X in vault"
- Create the missing item in dev-baile vault
- Verify vault access: `infisical projects`

### Secrets not loading
- Check mise hooks are enabled: `mise settings`
- Verify hooks ran: check for `[infisical-inject]` messages
- Force re-injection: `rm .env && source scripts/infisical-inject.sh`

### Race condition / "Another injection in progress"
- Wait a moment and re-enter directory
- Or delete lock file: `rm .env.lock .env.lock.pid`

## Comparison with Other Approaches

| Approach | Pros | Cons |
|----------|------|------|
| **mise hooks** (current) | Automatic, cached, fast | Requires mise |
| `infisical run` wrapper | Process-scoped | Slow (~1s per command) |
| direnv + infisical | Standard tooling | Another tool to install |
| Shell profile sourcing | Always available | Security risk, slow startup |
| Manual .env | Simple | Manual updates, insecure |

## Provider parity: Infisical, 1Password, or plain .env

Infisical is the default here, but it is not load-bearing. **Every stack reads
the same variable names regardless of where the values come from**, so the
provider is a swappable implementation detail. Anyone reproducing this
infrastructure can pick whichever they already run.

| | **Infisical** (default) | **1Password** | **Plain `.env`** |
|---|---|---|---|
| Container injection | Locket sidecar resolves `secrets.env` into a tmpfs volume | `op run --env-file` wrapping the entrypoint, or `op inject` at deploy | `env_file:` directly |
| Shell/dev injection | mise hook → `.env` (see above) | `op signin` + `op inject -i .env.tpl -o .env` | `.env` on disk |
| Auth | Machine identity (client id + secret) | Service account token (`OP_SERVICE_ACCOUNT_TOKEN`) | none |
| Template syntax | `{{ infisical "/path" "KEY" }}` | `op://vault/item/field` | literal values |
| Rotation | Central, immediate | Central, immediate | Manual, per host |
| Audit trail | Yes | Yes | No |
| Works offline | No | No | Yes |
| Extra infrastructure | Infisical server | None (SaaS) | None |
| Good for | Self-hosted, multi-host | Teams already on 1Password | Evaluation, single host, bootstrap |

The contract is the variable names. A stack's `secrets.env` template and its
`.env.example` list exactly what it needs; satisfying that list is all any
provider has to do. To switch providers you replace the hydration mechanism,
not the stacks.

`check_op_token.ts` is the minimal 1Password readiness probe (verifies
`OP_SERVICE_ACCOUNT_TOKEN` is present before a deploy attempts injection).

### Do not put bootstrap credentials behind a secrets manager

One deliberate exception runs through this infrastructure: **credentials needed
to establish connectivity are stored as plain files**, not fetched from a vault.

`~/.config/pangolin-newt/newt.env` (mode `600`) holds the Pangolin site
credentials literally, and does so on purpose. Two failure modes justify it:

1. A tunnel agent that cannot start until a remote vault answers has coupled
   your connectivity to that vault's availability.
2. If the vault is itself reachable *through* the tunnel — as Infisical is
   here — then fetching tunnel credentials from it is a deadlock on any cold
   start.

The same reasoning applies to any bootstrap credential: SSH host keys, the
Pangolin `SERVER_SECRET`, the secrets manager's own machine identity. Chase the
dependency chain and make sure it terminates on disk.

## Related Systems

- **Locket**: Container-based secret injection for Docker services
- **Infisical**: Server-side secret resolution for infrastructure
- **Pangolin**: Service mesh with SSO-protected secret access

See also:
- `bonneagar/uirlisí/op/` - Infisical server setup
- `bonneagar/uirlisí/locket/` - Locket sidecar documentation
- `meaisínfhoghlaim/models/secrets/` - LiteLLM secrets templates
