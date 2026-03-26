# Taisce - Modular Docker Stacks

Modular infrastructure stacks with separate compose, routing, and secrets configurations.

## Architecture

Each stack has four core files:

```
stacks/<name>/
├── compose.yaml     # Docker Compose (standalone compatible)
├── blueprint.yaml   # Pangolin routing (loaded by Newt)
├── secrets.env      # Locket template (used by both exec and sidecar modes)
└── sidecar.yaml     # Locket sidecar mode configuration
```

**Key Benefits:**
- Compose files work standalone for development
- Secrets managed separately via Locket (exec or sidecar mode)
- Routing defined declaratively via Pangolin blueprints
- Clear separation of concerns

## Quick Start

### Development (No Secrets)

```bash
# Copy example env file
cp .env.local.example .env.local

# Start a stack
./scripts/stack.sh langfuse up -d

# View logs
./scripts/stack.sh langfuse logs -f

# Stop
./scripts/stack.sh langfuse down
```

### Production (With Locket)

```bash
# Ensure 1Password Connect token exists
echo "your-token" > op_token

# Start with Locket secret injection
LOCKET_ENABLED=1 ./scripts/stack.sh langfuse up -d
```

## Available Stacks

| Stack | Description | Port | Domain |
|-------|-------------|------|--------|
| autobase | PostgreSQL Cluster Automation | 8082 | autobase.cianfhoghlaim.ie |
| beszel | Server Monitoring | 8090 | beszel.cianfhoghlaim.ie |
| cognee | AI Memory/Knowledge Graph | 8001 | cognee.cianfhoghlaim.ie |
| convex | Backend Platform | 3210 | convex.cianfhoghlaim.ie |
| dozzle | Container Logs | 8080 | dozzle.cianfhoghlaim.ie |
| dragonflydb | Redis Alternative | 6379 | (internal) |
| falkordb | Redis-based Graph DB | 3000 | falkordb.cianfhoghlaim.ie |
| garage | S3-Compatible Storage | 3900 | s3.cianfhoghlaim.ie |
| graphiti | Knowledge Graph MCP | 8000 | graphiti.cianfhoghlaim.ie |
| lakefs | Data Versioning | 8000 | lakefs.cianfhoghlaim.ie |
| lakekeeper | Iceberg REST Catalog | 8181 | lakekeeper.cianfhoghlaim.ie |
| lancedb | Vector Database | 8080 | lancedb.cianfhoghlaim.ie |
| langfuse | LLM Observability | 3000 | langfuse.cianfhoghlaim.ie |
| mathesar | PostgreSQL UI | 8000 | mathesar.cianfhoghlaim.ie |
| memgraph | Graph Database | 3000 | memgraph.cianfhoghlaim.ie |
| mlflow | ML Experiment Tracking | 5000 | mlflow.cianfhoghlaim.ie |
| nimtable | Iceberg Table Manager | 3000 | nimtable.cianfhoghlaim.ie |
| olake-ui | Database to Iceberg Replication | 8000 | olake.cianfhoghlaim.ie |
| qdrant | Vector Search | 6333 | qdrant.cianfhoghlaim.ie |

## Scripts

### stack.sh - Stack Manager

```bash
# Usage
./scripts/stack.sh <stack> <command> [args...]

# Commands
./scripts/stack.sh langfuse up -d      # Start detached
./scripts/stack.sh langfuse down       # Stop
./scripts/stack.sh langfuse logs -f    # Follow logs
./scripts/stack.sh langfuse ps         # List containers
./scripts/stack.sh langfuse restart    # Restart
./scripts/stack.sh langfuse pull       # Update images

# Production mode
LOCKET_ENABLED=1 ./scripts/stack.sh langfuse up -d
```

### sync-blueprints.sh - Pangolin Blueprint Sync

```bash
# List available blueprints
./scripts/sync-blueprints.sh --list

# Preview combined blueprint
./scripts/sync-blueprints.sh --dry-run

# Sync all blueprints to Newt server
./scripts/sync-blueprints.sh

# Sync specific stacks only
./scripts/sync-blueprints.sh langfuse cognee mlflow
```

## Deployment Modes

| Mode | Compose | Secrets | Routing | Command |
|------|---------|---------|---------|---------|
| **Development** | compose.yaml | .env.local | localhost | `./scripts/stack.sh <stack> up` |
| **Production (Exec)** | compose.yaml | secrets.env (Locket) | blueprint.yaml (Newt) | `LOCKET_ENABLED=1 ./scripts/stack.sh <stack> up` |
| **Production (Sidecar)** | compose.yaml + sidecar.yaml | templates/ | blueprint.yaml (Newt) | `docker compose -f compose.yaml -f sidecar.yaml up` |
| **Standalone** | compose.yaml | .env | Manual | `docker compose -f stacks/<stack>/compose.yaml up` |

## Locket Modes

Locket supports two modes for secret injection. Choose based on your application's needs:

### Exec Mode (Default)

Wraps `docker compose` and injects secrets as environment variables before containers start.

**Use when:**
- Application reads secrets from environment variables
- Simple deployment with `LOCKET_ENABLED=1`
- No need for hot-reloading secrets

```bash
# Via stack.sh wrapper
LOCKET_ENABLED=1 ./scripts/stack.sh langfuse up -d

# Or directly
locket exec --provider op-connect \
  --connect.host http://132.145.27.89:8080 \
  --connect.token-file ./op_token \
  --env-file stacks/langfuse/secrets.env \
  -- docker compose -f stacks/langfuse/compose.yaml up -d
```

### Local 1Password CLI (op run) Mode

For local development without 1Password Connect, you can use the 1Password CLI (`op run`) to inject secrets directly from your vault without relying on `.env` files.

**Use when:**
- Running locally on your machine
- You have the 1Password Desktop App and CLI (`op`) installed
- You want to avoid creating `.env` files with sensitive data

```bash
# 1. Start your local 1Password app and unlock it
# 2. Run your stack using op run with a secrets template
op run --env-file=stacks/langfuse/secrets.env -- docker compose -f stacks/langfuse/compose.yaml up -d
```

### Sidecar Mode

Runs Locket as a container that writes secrets to a shared tmpfs volume.

**Use when:**
- Application reads secrets from files (`*_FILE` environment variables)
- Need TLS certificates, SSH keys, or config files with embedded secrets
- Want hot-reloading of secrets without container restart
- Application supports dynamic config reloading (like Traefik)

```bash
# Start with sidecar
cd stacks/langfuse
docker compose -f compose.yaml -f sidecar.yaml up -d
```

**How it works:**
1. Locket sidecar reads templates from `./templates/`
2. Replaces `{{ op://vault/item/field }}` with actual secrets
3. Writes resolved files to shared tmpfs volume `/run/secrets/locket`
4. Application containers mount the volume read-only
5. Secrets never touch disk (tmpfs is memory-backed)

**Sidecar modes:**
- `--mode=watch` - Watch templates and update on change (default)
- `--mode=park` - Inject once, keep process alive for healthchecks
- `--mode=one-shot` - Inject once and exit

### Comparison

| Feature | Exec Mode | Sidecar Mode |
|---------|-----------|--------------|
| Secret delivery | Environment variables | Files in tmpfs |
| Hot-reload | No (restart required) | Yes (file watch) |
| Setup complexity | Simple | Requires sidecar.yaml |
| Best for | Most applications | File-based configs, certs |
| Disk exposure | Never | Never (tmpfs) |

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOCKET_ENABLED` | Enable Locket secret injection | (empty) |
| `OP_CONNECT_HOST` | 1Password Connect URL | http://132.145.27.89:8080 |
| `OP_CONNECT_TOKEN_FILE` | Path to Connect token | ./op_token |
| `TAISCE_DIR` | Base directory | (script parent) |

### Development Secrets (.env.local)

Copy the example file and customize:

```bash
cp .env.local.example .env.local
```

Default passwords are `devpassword` - never use in production.

### Production Secrets (Locket)

Secrets are stored in 1Password vault `taisce-secrets` with items per stack:
- `langfuse-postgres`, `langfuse-clickhouse`, `langfuse-redis`, etc.
- `cognee-postgres`, `cognee-memgraph`, `cognee-llm`
- etc.

Each `secrets.env` file uses Locket template syntax:
```
POSTGRES_PASSWORD={{ op://taisce-secrets/langfuse-postgres/password }}
```

## Pangolin Control Plane

The Pangolin identity-aware proxy runs as the control plane at `pangolin/`.

**Full documentation:** [PANGOLIN-SETUP.md](./PANGOLIN-SETUP.md)

### Quick Reference

| Service | URL | Purpose |
|---------|-----|---------|
| Pangolin Dashboard | pangolin.cianfhoghlaim.ie | Tunnel/resource management |
| Pocket ID | auth.cianfhoghlaim.ie | Passkey-based OIDC |
| TinyAuth | tinyauth.cianfhoghlaim.ie | Forward authentication |
| Middleware Manager | middleware.cianfhoghlaim.ie | Traefik middleware UI |
| Log Dashboard | logs.cianfhoghlaim.ie | Access log visualization |

### Start Control Plane

```bash
# Development
cd pangolin && docker compose up -d

# Production (with secrets)
cd pangolin && docker compose -f compose.yaml -f sidecar.yaml up -d
```

### Features

- **TLS**: Wildcard certificates via Cloudflare DNS challenge
- **Auth**: PocketID passkeys with TinyAuth forward auth
- **Security**: HSTS, secure headers, TLS 1.2+, rate limiting
- **Monitoring**: Log dashboard with OpenTelemetry tracing
- **Protection**: CrowdSec intrusion detection/prevention

## Pangolin Blueprints

Blueprints define public routing via Pangolin/Newt:

```yaml
# stacks/langfuse/blueprint.yaml
public-resources:
  langfuse:
    name: "Langfuse"
    full-domain: "langfuse.cianfhoghlaim.ie"
    protocol: "http"
    targets:
      - site: "arm1-oci"
        hostname: "langfuse-web"
        method: "http"
        port: 3000
```

### Loading Blueprints

1. **Sync to Newt** (recommended):
   ```bash
   ./scripts/sync-blueprints.sh
   ```

2. **Manual via Newt CLI**:
   ```bash
   newt --blueprint-file /path/to/blueprint.yaml
   ```

3. **Via Newt config directory**:
   Place blueprint files in `/opt/newt/blueprints/`

## Stack Profiles

Some stacks have optional services via Docker Compose profiles:

```bash
# Cognee with MCP server
docker compose -f stacks/cognee/compose.yaml --profile mcp up -d

# Graphiti with REST API
docker compose -f stacks/graphiti/compose.yaml --profile api up -d

# Lakekeeper with Jupyter
docker compose -f stacks/lakekeeper/compose.yaml --profile jupyter up -d

# LanceDB with S3 mount
docker compose -f stacks/lancedb/compose.yaml --profile s3 up -d

# Beszel with local agent
docker compose -f stacks/beszel/compose.yaml --profile agent up -d
```

## Directory Structure

```
croí/taisce/
├── .env.local.example      # Development secrets template
├── .env.local              # Local development secrets (git-ignored)
├── op_token                # 1Password Connect token (git-ignored)
├── README.md               # This file
├── config/                 # Shared config files (mounted by stacks)
│   ├── garage.toml
│   └── graphiti.config.yaml
├── projects/               # Custom project directories
│   ├── autobase/           # Autobase project
│   ├── cognee/             # Cognee project files
│   ├── ducklake/           # DuckLake project
│   ├── motherduck-examples/ # MotherDuck examples
│   ├── olake-data/         # OLake data files
│   └── olake-ui/           # OLake UI project
├── stacks/                 # 19 service stacks
│   ├── langfuse/
│   │   ├── compose.yaml    # Docker Compose (standalone)
│   │   ├── blueprint.yaml  # Pangolin routing
│   │   ├── secrets.env     # Locket template (exec & sidecar)
│   │   └── sidecar.yaml    # Locket sidecar mode
│   ├── cognee/
│   │   └── ...
│   └── .../                # (17 stacks total)
└── scripts/
    ├── stack.sh            # Stack manager (exec mode)
    └── sync-blueprints.sh  # Blueprint sync to Newt
```

## Adding a New Stack

1. Create the stack directory:
   ```bash
   mkdir -p stacks/mystack
   ```

2. Create `compose.yaml` with `${VAR:-default}` pattern for all secrets:
   ```yaml
   name: mystack
   services:
     myapp:
       image: myapp:latest
       environment:
         DB_PASSWORD: ${DB_PASSWORD:-devpassword}
   ```

3. Create `blueprint.yaml` for routing:
   ```yaml
   public-resources:
     mystack:
       name: "My Stack"
       full-domain: "mystack.cianfhoghlaim.ie"
       protocol: "http"
       targets:
         - site: "arm1-oci"
           hostname: "myapp"
           method: "http"
           port: 8080
   ```

4. Create `secrets.env` for Locket exec mode:
   ```
   DB_PASSWORD={{ op://taisce-secrets/mystack/db_password }}
   ```

5. Create `sidecar.yaml` for sidecar mode (uses same secrets.env):
   ```yaml
   services:
     locket:
       image: ghcr.io/bpbradley/locket:latest
       user: "65532:65532"
       command:
         - "--provider=op-connect"
         - "--connect.host=${OP_CONNECT_HOST:-http://132.145.27.89:8080}"
         - "--connect.token-file=/run/secrets/op_token"
         - "--map=/templates:/run/secrets/locket"
       secrets:
         - op_token
       volumes:
         - ./secrets.env:/templates/secrets.env:ro
         - mystack-secrets:/run/secrets/locket
       networks:
         - mystack

     myapp:
       depends_on:
         locket:
           condition: service_healthy
       volumes:
         - mystack-secrets:/run/secrets/locket:ro

   secrets:
     op_token:
       file: ${OP_CONNECT_TOKEN_FILE:-../../op_token}

   volumes:
     mystack-secrets:
       driver: local
       driver_opts:
         type: tmpfs
         device: tmpfs
   ```

6. Add defaults to `.env.local.example`:
   ```
   # MYSTACK
   DB_PASSWORD=devpassword
   ```

7. Create 1Password items in `taisce-secrets` vault.

8. Test:
   ```bash
   # Development
   ./scripts/stack.sh mystack up -d
   ./scripts/stack.sh mystack logs -f

   # Production (exec mode)
   LOCKET_ENABLED=1 ./scripts/stack.sh mystack up -d

   # Production (sidecar mode)
   cd stacks/mystack
   docker compose -f compose.yaml -f sidecar.yaml up -d
   ```

## Troubleshooting

### Stack won't start

```bash
# Check compose file syntax
docker compose -f stacks/<stack>/compose.yaml config

# Check for missing env vars
docker compose -f stacks/<stack>/compose.yaml config --quiet
```

### Locket errors

```bash
# Test 1Password Connect
curl http://132.145.27.89:8080/v1/vaults

# Test secret resolution
locket exec --provider op-connect \
  --connect.host http://132.145.27.89:8080 \
  --connect.token-file ./op_token \
  --env-file stacks/langfuse/secrets.env \
  -- env | grep -E '^(POSTGRES|REDIS|MINIO)'
```

### Blueprint not loading

```bash
# Validate YAML syntax
yamllint stacks/<stack>/blueprint.yaml

# Check Newt logs
ssh ubuntu@132.145.27.89 "cd /opt/newt && docker compose logs -f"
```
