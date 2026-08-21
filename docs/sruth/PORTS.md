# Port Allocation - Sruth Data Flows

This document defines the standardized port allocation across all sruth (data flow) projects to prevent conflicts during development and deployment.

## Frontend Applications (Development)

| Port | Application | Purpose | Internal Port |
|------|-------------|---------|---------------|
| 3000 | **Aleyum Portal** | Main developer dashboard (AG-UI, MCP tools, stack management) | 3000 |
| 3002 | **Crypteolas UI** | DeFi research and code analysis RAG interface | 3002 |
| 3003 | Aleyum Portfolio | Personal portfolio site (future) | - |
| 3004 | **Tuath UI** | Celtic educational MMO frontend | 3004 |
| 3005 | **Oideachais Web** | Celtic education curriculum platform | 3000 (mapped) |
| 3006 | **Oideachais Dashboard** | OCR comparison dashboard and analytics | 3006 |
| 3007-3010 | Reserved | Future frontend applications | - |

## Backend APIs

| Port | Application | Purpose |
|------|-------------|---------|
| 8000 | Oideachais API | Celtic education platform backend (FastAPI) |
| 8001 | Crypteolas API | DeFi research backend |
| 8002 | Browser Agent | Browser automation and scraping service |

## Internal Services (Container-to-Container)

These ports are used for inter-container communication and are NOT exposed externally:

| Service | Internal Port | External Exposure |
|---------|---------------|-------------------|
| Dagster Webserver | 3000 | Mapped to 3102-3106 per flow |
| Langfuse | 3000 | Container-only |
| SpaceTimeDB | 3000 | Container-only |
| Databases | Various | Container-only |

## Docker Compose Port Mappings

### Aleyum Portal
```yaml
ports:
  - "${PORTAL_PORT:-3000}:3000"  # External:Internal
```

### Oideachais
```yaml
# Frontend (apps/web)
ports:
  - "${FRONTEND_PORT:-3005}:3000"  # External 3005:Internal 3000

# API
ports:
  - "${API_PORT:-8000}:8000"
```

### Crypteolas
```yaml
# UI
ports:
  - "3002:3000"

# API
ports:
  - "8001:8000"
```

### Tuath
```yaml
# UI
ports:
  - "3004:3000"

# API
ports:
  - "8000:8000"
```

## Development Notes

### Running Multiple Frontends
To run multiple frontend applications simultaneously:

```bash
# Terminal 1: Aleyum Portal
cd sruth/aleyum/portal
pnpm dev  # Runs on :3000

# Terminal 2: Oideachais Web
cd sruth/oideachais/apps/web
pnpm dev  # Runs on :3005

# Terminal 3: Oideachais Dashboard
cd sruth/oideachais/dashboard
pnpm dev  # Runs on :3006

# Terminal 4: Tuath UI
cd sruth/tuath/ui
pnpm dev  # Runs on :3004

# Terminal 5: Crypteolas UI
cd sruth/crypteolas/ui
pnpm dev  # Runs on :3002
```

### CORS Configuration
When updating CORS settings in backends, ensure all frontend ports are allowed:

```python
allow_origins=[
    "http://localhost:3000",  # Aleyum Portal
    "http://localhost:3002",  # Crypteolas UI
    "http://localhost:3004",  # Tuath UI
    "http://localhost:3005",  # Oideachais Web
    "http://localhost:3006",  # Oideachais Dashboard
    "http://localhost:5173",  # Vite dev server fallback
]
```

### Port Conflicts
If you encounter port conflicts:

1. Check what's using the port: `lsof -i :3000`
2. Kill the process if needed: `kill -9 <PID>`
3. Or use the environment variable override: `PORTAL_PORT=3010 docker compose up`

## Environment Variables

Each service supports port overrides via environment variables:

- `PORTAL_PORT` - Aleyum Portal external port (default: 3000)
- `FRONTEND_PORT` - Oideachais Web external port (default: 3005)
- `API_PORT` - Oideachais API external port (default: 8000)

## Reserved Ports (3007-3010)

These ports are reserved for future frontend applications. Do not allocate without updating this document.

## Related Files

- `/sruth/aleyum/portal/vite.config.ts` - Port 3000
- `/sruth/aleyum/portal/compose.yaml` - Port mapping
- `/sruth/crypteolas/ui/vite.config.ts` - Port 3002
- `/sruth/tuath/ui/vite.config.ts` - Port 3004
- `/sruth/oideachais/apps/web/vite.config.ts` - Port 3005
- `/sruth/oideachais/compose.yaml` - Frontend port mapping
- `/sruth/oideachais/dashboard/vite.config.ts` - Port 3006
- `/sruth/oideachais/dashboard/Dockerfile` - Port 3006 exposure

## Changes Made (2025-01-05)

- Moved Oideachais Dashboard from port 3000 to **3006** (resolves conflict with Aleyum Portal)
- Updated Oideachais Web Docker Compose mapping from 3000 to **3005**
- Updated all CORS configurations to include new ports
- Updated MCP tool endpoints to point to API backend (8000) instead of frontend (3000)
- Created this documentation file

## Maintenance

When adding new frontend services:
1. Choose next available port from 3007-3010 range
2. Update this document
3. Update CORS settings in relevant backends
4. Document any Docker Compose port mappings
