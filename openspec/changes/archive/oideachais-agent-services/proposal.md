# oideachais-agent-services — Add Agno AgentOS + Google ADK as separate compose services

## Why

The oideachais quadrant has **two agent frameworks** currently
running **in-process inside the `api` image**:

1. **Google ADK** — 12 active agent files in
   `sruth/oideachais/agents/adk/` that import `google.adk.agents`,
   `google.adk.planners`, `google.adk.tools`, `google.adk.events`,
   etc. (verified by `grep` on the 12 files; matches in
   `agui_curriculum_agent.py:19-20`, `research_agent.py:18-20`,
   `education_research_agent.py:14-19`, `bunchloch_research_agent.py:21-22`,
   `geospatial_agent.py:10-11`, `mcp_curriculum_agent.py:12`,
   `statistics_agent.py:10-11`, `curriculum_comparison_agent.py:9-10`,
   `callbacks/citation_callbacks.py:11`,
   `agents/api/curriculum_endpoint.py:18-19`,
   `tools/statistics_query.py:11`, `tools/spatial_query.py:12`,
   `agents/tools/curriculum_search.py:18`,
   `agents/tools/statistics_query.py:11`,
   `agents/tools/spatial_query.py:12`)

2. **Agno (AgentOS)** — full source at
   `sruth/oideachais/agent_os/` with `Dockerfile`, `config.yaml`,
   `main.py`, `README.md`. The Dockerfile uses
   `uvicorn agent_os.main:app --host 0.0.0.0 --port 7777`
   and exposes port 7777. The Dockerfile is **complete and
   ready to build** but is NOT wired into any compose file.

**Current problem**: Both frameworks run inside the `api` Docker
image. This causes:
- **Observability is mixed**: the ADK and Agno traces are
  interleaved with the FastAPI traces
- **Resource isolation is poor**: heavy ADK LLM calls and Agno
  AgentOS server can starve the FastAPI
- **Independent scaling is impossible**: the `api` service
  cannot scale separately from the agent runtimes
- **Local dev is heavier**: the `api` image must include
  `google-adk` + `agno` dependencies even for endpoints that
  don't use them
- **The agent_os Dockerfile is dead code**: it was built but
  never wired into compose

**This change makes ADK and Agno first-class compose services**
in the oideachais stack, with their own Dockerfiles, their own
containers, their own Traefik routes, and their own resource
limits.

## What

### 1. Add the 2 new services to compose.yaml
In `infrastructure/stacks/sruth/oideachais/compose.yaml`, add 2 new
service definitions after the `frontend` service:

```yaml
# ---------------------------------------------------------------------------
# AGENT OS (Agno) - Celtic Education Agent runtime
# ---------------------------------------------------------------------------
agent_os:
  image: oideachais-dev-agentos:latest
  pull_policy: never
  build:
    context: ../../../..
    dockerfile: sruth/oideachais/agent_os/Dockerfile
  container_name: cianfhoghlaim-oideachais-agent-os
  restart: unless-stopped
  ports:
    - "${AGENT_OS_PORT:-7777}:7777"
  environment:
    OPENAI_API_KEY: ${OPENAI_API_KEY:-}
    LLM_API_KEY: ${LITELLM_MASTER_KEY:-${LLM_API_KEY:-}}
    LLM_PROVIDER: ${LLM_PROVIDER:-litellm}
    LLM_BASE_URL: ${LLM_BASE_URL:-http://litellm:4000}
    LLM_MODEL: ${LLM_MODEL:-gemini/gemini-2.0-flash}
  healthcheck:
    test: ["CMD-SHELL", "curl -fs http://localhost:7777/health || exit 1"]
    interval: 30s
    timeout: 10s
    retries: 5
    start_period: 60s
  depends_on:
    locket:
      condition: service_healthy
  env_file:
    - /run/secrets/locket/secrets.env
  volumes:
    - locket_secrets:/run/secrets/locket:ro
  networks:
    - cianfhoghlaim
    - lakehouse
  deploy:
    resources:
      limits:
        cpus: "2"
        memory: 4G

# ---------------------------------------------------------------------------
# ADK AGENTS (Google ADK) - Multi-agent orchestrator
# ---------------------------------------------------------------------------
adk_agents:
  image: oideachais-dev-adk-agents:latest
  pull_policy: never
  build:
    context: ../../../..
    dockerfile: sruth/oideachais/Dockerfile.adk
  container_name: cianfhoghlaim-oideachais-adk-agents
  restart: unless-stopped
  ports:
    - "${ADK_PORT:-7778}:7778"
  environment:
    GOOGLE_API_KEY: ${GOOGLE_API_KEY:-}
    LLM_API_KEY: ${LITELLM_MASTER_KEY:-${LLM_API_KEY:-}}
    LLM_PROVIDER: ${LLM_PROVIDER:-litellm}
    LLM_BASE_URL: ${LLM_BASE_URL:-http://litellm:4000}
    LLM_MODEL: ${LLM_MODEL:-gemini/gemini-2.0-flash}
  healthcheck:
    test: ["CMD-SHELL", "curl -fs http://localhost:7778/health || exit 1"]
    interval: 30s
    timeout: 10s
    retries: 5
    start_period: 60s
  depends_on:
    locket:
      condition: service_healthy
  env_file:
    - /run/secrets/locket/secrets.env
  volumes:
    - locket_secrets:/run/secrets/locket:ro
  networks:
    - cianfhoghlaim
    - lakehouse
  deploy:
    resources:
      limits:
        cpus: "2"
        memory: 4G
```

### 2. Create the ADK Dockerfile
Create `sruth/oideachais/Dockerfile.adk` that:
- Uses `python:3.12-slim` as the base
- Installs `google-adk` + the oideachais deps
- Copies the `sruth/oideachais/agents/adk/` source
- Runs `uvicorn` on port 7778

### 3. Add Traefik routers to pangolin.yaml
In `infrastructure/stacks/sruth/oideachais/pangolin.yaml`, add 2
new routers for the agent endpoints:

```yaml
- traefik.http.routers.oideachais-agent-os:
    rule: "Host(`agent.os.cianfhoghlaim.ie`)"
    service: oideachais-agent-os
    tls.certresolver: letsencrypt
    entrypoints: websecure
    middlewares: [default@file, secure-headers@file]
- traefik.http.routers.oideachais-adk-agents:
    rule: "Host(`adk.cianfhoghlaim.ie`)"
    service: oideachais-adk-agents
    tls.certresolver: letsencrypt
    entrypoints: websecure
    middlewares: [default@file, secure-headers@file]
```

### 4. Update blueprint.yaml
Add the 2 new services to the `metadata.ports` list:
```yaml
metadata:
  ports: [3335, 8000, 3080, 7777, 7778]
```

### 5. Update QUADRANT-TO-STACK-MAP.md
Add the 2 new services to the oideachais quadrant row.

## Impact

### Affected files
- **MODIFIED:** `infrastructure/stacks/sruth/oideachais/compose.yaml`
  (+ 2 new service definitions)
- **NEW:** `sruth/oideachais/Dockerfile.adk` (ADK runtime image)
- **MODIFIED:** `infrastructure/stacks/sruth/oideachais/pangolin.yaml`
  (+ 2 new Traefik routers)
- **MODIFIED:** `infrastructure/stacks/sruth/oideachais/blueprint.yaml`
  (+ 2 new ports)
- **MODIFIED:** `infrastructure/QUADRANT-TO-STACK-MAP.md`
  (+ 2 new services)
- **MODIFIED:** `infrastructure/stacks/sruth/oideachais/README.md`
  (update architecture table)

### Affected specs
- MODIFIED `oideachais-pipeline` — the rule that ADK agents and
  Agno AgentOS MUST run as separate compose services, not
  in-process inside the `api` image.

### Backward compatibility
- The new services are additive (no existing services modified)
- The `api` service can still invoke ADK agents and the Agno
  AgentOS via HTTP (using the new Traefik routes or direct
  container-to-container on the `cianfhoghlaim` network)
- Existing deployments that do not need ADK / Agno can simply
  not start the new services (`docker compose up --scale
  adk_agents=0`)

## Non-Goals

- No changes to the agent source code in `sruth/oideachais/agents/adk/`
  or `sruth/oideachais/agent_os/`
- No BAML or Cognee changes
- No changes to the existing 3 services
- No change to the Komodo deployment procedure
  (the 5-stage procedure already deploys the oideachais stack
  as a unit; adding 2 services to the unit is automatic)

## Risk Assessment

- **Risk: the ADK Dockerfile is novel and may have missing
  dependencies.** Mitigation: the Dockerfile is a simple
  pattern (copy + pip install + uvicorn); if the build fails,
  the user can iterate. The first build will be slow (the
  google-adk package is large) but should succeed.
- **Risk: the agent_os Dockerfile is already in the repo but
  was never tested.** Mitigation: the existing Dockerfile
  is left unchanged; the compose change just wires it in.
  If the Dockerfile has issues, the agent_os container will
  fail healthcheck but the rest of the stack works.
- **Risk: the 2 new services require the LLM gateway (LiteLLM)
  which may not be configured in dev environments.** Mitigation:
  the healthcheck only checks the HTTP server is up (not that
  the LLM calls succeed); the agents will gracefully degrade
  when the LLM is unavailable.

## Validation

1. `docker compose -f compose.yaml config` parses
2. The 2 new services appear in `docker compose -f compose.yaml config` output
3. `infrastructure/stacks/sruth/oideachais/README.md` documents the 2 new services
4. `infrastructure/QUADRANT-TO-STACK-MAP.md` includes the 2 new services
5. `openspec validate oideachais-agent-services --strict` passes
