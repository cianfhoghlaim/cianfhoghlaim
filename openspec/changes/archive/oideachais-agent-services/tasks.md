# Tasks: oideachais-agent-services

## Phase 1: Create the ADK Dockerfile

- [ ] Create `sruth/oideachais/Dockerfile.adk`:
  - Base: `python:3.12-slim`
  - Install `google-adk` + the oideachais deps
  - Copy `sruth/oideachais/agents/adk/` source
  - Run `uvicorn` on port 7778

## Phase 2: Add the 2 new services to compose.yaml

- [ ] Add the `agent_os` service (port 7777) after the `frontend` service
- [ ] Add the `adk_agents` service (port 7778) after the `agent_os` service
- [ ] Both services have `depends_on: locket: condition: service_healthy`
- [ ] Both services have `env_file: /run/secrets/locket/secrets.env`
- [ ] Both services have `locket_secrets:/run/secrets/locket:ro` volume mount
- [ ] Both services are on the `cianchoghlaim` + `lakehouse` networks

## Phase 3: Add Traefik routers to pangolin.yaml

- [ ] Add `agent.os.cianfhoghlaim.ie` Traefik router for the agent_os service
- [ ] Add `adk.cianfhoghlaim.ie` Traefik router for the adk_agents service
- [ ] Both routers use the `letsencrypt` cert resolver and `websecure` entrypoint

## Phase 4: Update blueprint.yaml

- [ ] Add `7777` and `7778` to the `metadata.ports` list
- [ ] Add the 2 new services to the description

## Phase 5: Update QUADRANT-TO-STACK-MAP.md

- [ ] Add the 2 new services to the oideachais quadrant row

## Phase 6: Update README.md

- [ ] Update the architecture table with the 2 new services
- [ ] Update the ports table with 7777 and 7778

## Phase 7: Validation

- [ ] `docker compose -f compose.yaml config` parses (2 new services appear)
- [ ] `infrastructure/stacks/sruth/oideachais/README.md` documents the 2 new services
- [ ] `infrastructure/QUADRANT-TO-STACK-MAP.md` includes the 2 new services
- [ ] `openspec validate oideachais-agent-services --strict` passes

## Phase 8: Land the plane

- [ ] Stage the changes
- [ ] Commit: `git commit -m "oideachais-agent-services: add Agno AgentOS + Google ADK as separate services"`
- [ ] `git pull --rebase`
- [ ] `git push origin q3-2026-oideachais-consolidation`
