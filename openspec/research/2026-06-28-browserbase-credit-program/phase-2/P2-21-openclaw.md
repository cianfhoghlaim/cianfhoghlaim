# P2-21 — openclaw (Phase 2, Agent-Platform)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** agent-platform

## TL;DR

OpenClaw is the **open-source Minecraft server mod** that powers the `tuatha/mmo` educational game world. It's not strictly an AI/ML tool but is included in the agent-platform stack because the tuatha educational MMO uses it as the runtime environment for the crypteolas achievement ledger.

## Code

| Path | Purpose |
|:--|:--|
| `stacks/openclaw/compose.yaml` | OpenClaw server (port 25565) |
| `stacks/openclaw/world/` | World data (crypteolas achievement zones) |
| `oideachais/agents/tuatha/mmo/server.py` | Tuatha MMO server integration with OpenClaw |
| `cognify/rules/openclaw_worlds.py` | Lists 5 educational worlds |

**Canonical OpenClaw compose**:

```yaml
openclaw:
  image: openclaw/openclaw:latest
  container_name: openclaw-server
  restart: unless-stopped
  ports:
    - "25565:25565"
  volumes:
    - openclaw-world:/opt/openclaw/worlds
  environment:
    JAVA_OPTS: "-Xmx4G -Xms2G"
    SERVER_NAME: "Cianfhoghlaim Educational MMO"
    GAMEMODE: "creative"  # For educational exploration
    DIFFICULTY: "peaceful"
    MAX_PLAYERS: 50
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `OPENCLAW_RCON_PASSWORD` | `infisical://dev-baile/openclaw/rcon_password` | Locket |
| `OPENCLAW_WORLD_BACKUP_S3` | `s3://openclaw-backups/` | compose env |

## CCC anchors

`stacks/openclaw/` · `oideachais/agents/tuatha/mmo/` · `cognify/rules/openclaw_worlds.py`

Search terms: `"openclaw"`, `"rcon_password"`, `"world"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-11 | Initial OpenClaw deploy |
| 2026-02 | Added crypteolas achievement zones |
| 2026-04 | Connected to tuatha/mmo server integration |

## Anti-patterns

1. Don't run OpenClaw with survival mode for educational use — peaceful only
2. Don't expose port 25565 to the public internet — restrict via Pangolin
3. Don't skip world backups — players build educational content that's irreplaceable

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Game mode | Creative + Peaceful | Educational (not combat) |
| Players | 50 max | Class-sized cohort |
| Backups | Daily S3 | Irreplaceable player builds |
| Auth | Pangolin SSO | Same as rest of stack |
| Version | Latest stable | Up-to-date features |

## Files to read next

`stacks/openclaw/` · `oideachais/agents/tuatha/mmo/server.py`
