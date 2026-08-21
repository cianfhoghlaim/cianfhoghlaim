# Sruth Development Environments

## Overview
Each sruth (data flow) now has a dedicated development compose file that enables hot-reload, debugging, and local development with connection to shared bonneagar infrastructure.

## Quick Start

### Prerequisites
1. Docker Desktop or Docker Engine installed
2. Shared bonneagar infrastructure running (optional but recommended)
3. Environment variables configured in `.env` files

### Starting a Sruth in Development Mode

#### OIDEACHAIS (Education Platform)
```bash
cd sruth/oideachais
docker compose -f compose.yaml -f compose.dev.yaml up -d

# Access services
open http://localhost:8000/docs  # API docs
open http://localhost:3000       # Frontend
```

#### ALEYUM (Music Intelligence)
```bash
cd sruth/aleyum
docker compose -f compose.yaml -f docker-compose.dev.yml --profile dagster up -d

# Access services
open http://localhost:3106       # Dagster UI
```

#### BROWSER (Web Automation)
```bash
cd sruth/browser
docker compose -f compose.yaml -f docker-compose.dev.yml up -d

# Access services
open http://localhost:8003/docs  # API docs
open http://localhost:8080       # Skyvern UI
open http://localhost:3100       # Stagehand
```

#### CÓDEOLAS (Code Intelligence)
```bash
cd sruth/códeolas
docker compose -f compose.yaml -f docker-compose.dev.yml up -d

# Access services
open http://localhost:8002/docs  # API docs
open http://localhost:3102       # Dagster UI
```

#### CRYPTEOLAS (Crypto/Finance)
```bash
cd sruth/crypteolas
docker compose -f docker-compose.yaml -f docker-compose.dev.yml up -d

# Access services
open http://localhost:8001/docs  # API docs
open http://localhost:3001       # UI
open http://localhost:3002       # Dagster UI
open http://localhost:3003       # Memgraph Lab
```

#### TUATH (Community/Gaming)
```bash
cd sruth/tuath
docker compose -f docker-compose.yaml -f docker-compose.dev.yml up -d

# Access services
open http://localhost:8002/docs  # API docs
open http://localhost:3010       # UI
open http://localhost:3012       # Dagster UI
open http://localhost:8080       # Game client
```

## Shared Infrastructure

### Why Shared Infrastructure?
Multiple sruth connect to common services for:
- **Observability**: Langfuse for LLM tracing
- **Storage**: Garage for S3-compatible artifact storage
- **Graph**: FalkorDB for temporal knowledge graphs
- **Catalog**: Lakekeeper for Iceberg table management

### Starting Shared Services

#### FalkorDB (Graph + Vector Database)
```bash
cd bonneagar/storage/falkordb
docker compose up -d

# Access
open http://localhost:3000       # Web UI
# bolt://falkordb:6379          # Bolt protocol
```

#### Langfuse (LLM Observability)
```bash
cd bonneagar/storage/langfuse
docker compose up -d

# Access
open http://localhost:3000       # Web UI
```

#### Garage (S3-compatible Storage)
```bash
cd bonneagar/storage/garage
docker compose up -d

# Access
open http://localhost:3902       # Web UI
# http://localhost:3900          # S3 API
```

#### Lakekeeper (Iceberg REST Catalog)
```bash
cd bonneagar/storage/lakekeeper
docker compose up -d

# Access
open http://localhost:8181       # REST API
open http://localhost:8182       # Admin UI
```

## Development Features

### Hot-Reload
All development compose files include volume mounts for live code reloading:
- **API**: Changes to `./api/` reflect immediately
- **UI**: Changes to `./ui/src/` or `./apps/web/src/` trigger rebuild
- **Dagster**: Changes to `./dagster_assets/` reload pipelines

### Debug Logging
Development mode enables:
- `LOG_LEVEL=DEBUG` for verbose output
- Console logs accessible via `docker compose logs -f`
- Stack traces and error details

### Resource Limits
Development mode removes resource constraints for faster iteration.

### Data Persistence
All data persists in local directories:
- `./storage/` - Application data
- `./dagster_home/` - Dagster state
- Named volumes for databases (PostgreSQL, etc.)

## Environment Variables

### Required Variables

Each sruth needs specific environment variables. Copy `.env.example` to `.env`:

```bash
# OIDEACHAIS
cd sruth/oideachais
cp .env.example .env
# Edit .env with your values

# ALEYUM
cd sruth/aleyum
cp .env.example .env
# Add Spotify API credentials
# Add R2 credentials (or use local Garage)

# BROWSER
cd sruth/browser
cp .env.example .env
# Add LLM API keys (Anthropic, OpenAI, etc.)
# Add Browserbase/Firecrawl keys (optional)

# CÓDEOLAS
cd sruth/códeolas
cp .env.example .env
# Add LLM API keys

# CRYPTEOLAS
cd sruth/crypteolas
cp .env.example .env
# Add LLM API keys
# Add GitHub token for repo scanning

# TUATH
cd sruth/tuath
cp .env.example .env
# Add LLM API keys
# Add MapLibre style URL (optional)
```

### Common Variables

```bash
# LLM Providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# Observability
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST=http://langfuse:3000

# Storage
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_ENDPOINT=http://garage:3900
```

## Port Allocations

See [PORTS.md](../../PORTS.md) for complete port mappings across all sruth and infrastructure.

### Quick Reference

| Sruth | API | UI | Dagster | Other |
|-------|-----|----|---------|-------|
| OIDEACHAIS | 8000 | 3000 | - | - |
| ALEYUM | - | - | 3106 | Redis: 6381 |
| BROWSER | 8003 | 8080 | - | Stagehand: 3100 |
| CÓDEOLAS | 8002 | - | 3102 | - |
| CRYPTEOLAS | 8001 | 3001 | 3002 | Memgraph: 3003 |
| TUATH | 8002 | 3010 | 3012 | Game: 8080 |

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
export API_PORT=8010
docker compose up -d
```

### Network Connection Issues
```bash
# Verify bonneagar_default network exists
docker network ls | grep bonneagar

# Create if missing
docker network create bonneagar_default

# Inspect network
docker network inspect bonneagar_default
```

### Hot-Reload Not Working
```bash
# Check volume mounts
docker compose config

# Rebuild with --build flag
docker compose -f compose.yaml -f docker-compose.dev.yml up -d --build

# Check file permissions
ls -la ./api/
```

### Database Connection Errors
```bash
# Check if database is running
docker compose ps

# View database logs
docker compose logs -f postgres

# Connect to database
docker compose exec postgres psql -U postgres
```

### Container Won't Start
```bash
# View logs
docker compose logs -f <service>

# Check health status
docker compose ps

# Rebuild from scratch
docker compose down -v
docker compose -f compose.yaml -f docker-compose.dev.yml up -d --build
```

## Common Workflows

### Adding a New Dependency
```bash
# Python dependencies
cd sruth/<name>
uv add <package>
# Update Dockerfile if needed

# Node dependencies
cd sruth/<name>/ui
pnpm add <package>
```

### Running Tests
```bash
cd sruth/<name>

# Python tests
uv run pytest tests/

# With coverage
uv run pytest tests/ --cov=api

# Watch mode
uv run pytest tests/ -f
```

### Accessing Database Shells
```bash
# PostgreSQL (if sruth uses it)
docker compose exec postgres psql -U postgres

# Redis/DragonflyDB
docker compose exec dragonfly redis-cli

# Memgraph
docker compose exec memgraph mgconsole

# DuckDB (direct file access)
docker compose exec api duckdb /data/service.duckdb
```

### Viewing Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api

# Last 100 lines
docker compose logs --tail=100 api

# Real-time with grep
docker compose logs -f api | grep ERROR
```

### Stopping Services
```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# Stop specific service
docker compose stop api

# Restart service
docker compose restart api
```

## Production Deployment

Development compose files are **NOT** suitable for production. For production:

1. Use base `compose.yaml` or `docker-compose.yaml` without dev overrides
2. Set `ENVIRONMENT=production`
3. Use secrets management (1Password, HashiCorp Vault)
4. Enable resource limits
5. Use external databases (managed services)
6. Enable TLS/SSL
7. Configure backups

```bash
# Production example
cd sruth/oideachais
export ENVIRONMENT=production
locket exec --env-file secrets.env -- docker compose up -d
```

## Best Practices

### Development
1. **Always use dev overrides** for local development
2. **Check logs** when services fail to start
3. **Use .env files** for secrets (never commit them)
4. **Monitor resource usage** via Docker Desktop
5. **Clean up** unused containers and volumes regularly

### Code Organization
1. **Keep dev files separate** from production configs
2. **Document environment variables** in `.env.example`
3. **Use volume mounts** for hot-reload, not builds
4. **Test in dev** before deploying to production

### Collaboration
1. **Document port changes** in PORTS.md
2. **Update README** when adding services
3. **Use consistent naming** across sruth
4. **Share infrastructure** where possible

## Additional Resources

- [PORTS.md](../../PORTS.md) - Complete port allocations
- [CLAUDE.md](../../CLAUDE.md) - Project instructions
- [Bonnieagar README](../../bonneagar/README.md) - Infrastructure guide
- Individual sruth README files for specific documentation

## Support

For issues or questions:
1. Check individual sruth README files
2. Review logs with `docker compose logs`
3. Consult PORTS.md for port conflicts
4. Check bonneagar infrastructure status

---

**Last Updated**: 2025-01-05
**Maintainer**: Cianfhoghlaim Infrastructure Team
