---
title: 'Education Audit Plan'
status: research
supersedes: []
superseded_by: []
last_touched: 2026-06-13
---

# Education Directory Audit & Reintegration Plan

## Overview
This plan outlines the systematic reintegration of the `education` workspace. The focus is to realign existing capabilities, resolve broken placeholders from previous restructurings (like "sruth" -> "education"), and pivot CI/CD flows toward GitHub Actions, deprecating Forgejo. 

## 1. Root Configurations & Environment 
**Current State:**
- `docker-compose.yaml` references old directories like `./sruth/aleyum/portal`, `./sruth/oideachais/apps/web`, `./sruth/crypteolas/ui`.
- `compose.yaml` references `./apps/web` instead of `./web`.
- `pyproject.toml` references `sruth-browser` workspace but the directory is `browser`.
- Unused/stub `.env` files with missing configurations for Komodo, Pangolin, and Infisical + mise.

**Action Plan:**
- [ ] Update `docker-compose.yaml` and `compose.yaml` to point to the actual subdirectories (`web`, `browser`, `api`, `marimo`, etc.).
- [ ] Standardize the `.env` template strategy (integrating Infisical CLI `infisical export` or `.infisical.env` workflows) for secrets management across sub-agents.
- [ ] Align `pyproject.toml` and `workspace.yaml` (Dagster) to accurately map the internal module references.

## 2. Infrastructure Directory (Komodo, Pangolin, Docker)
**Current State:**
- Existing docker stacks are out of sync with actual folder structures. 
- Local development proxying (Pangolin) and deployment coordination (Komodo) are partially defined but lack actionable compose profiles in the root.

**Action Plan:**
- [ ] Audit `education/infrastructure/` to extract existing Pangolin/Komodo compose templates.
- [ ] Rebuild a unified `docker-compose.yaml` profile system (`dev`, `infra`, `ui`, `ml`) that correctly paths to current services.
- [ ] Add Infisical CLI + mise integration steps to the infrastructure README for local secret injection without `.env` file reliance.

## 3. Browser, ADK, and Machine Learning
**Current State:**
- **Browser:** Capabilities exist for scraping/interaction but are disconnected from the main API and pipelines.
- **ADK (Agent Development Kit):** Has Google ADK for agents mentioned in TOML but needs validation of `education/adk` scripts/modules.
- **Machine Learning:** Schemas and pipelines exist for curriculum vectorization (LanceDB) and NLP, but model endpoints (Gemini Live Hackathon focus vs open-source alternatives like Ollama) need standardizing.

**Action Plan:**
- [ ] Integrate `browser` tools into the Dagster pipelines natively using the DLT integrations.
- [ ] Validate `adk` and `.skills` interactions. Hook sub-agents into the pipeline via defined MCP (Model Context Protocol) JSONs.
- [ ] Configure `machine_learning` directory to define fallback ML models (e.g., Anthropic -> Gemini -> Local/Open Source) ensuring robust parallel capabilities.

## 4. Web & Research Convergence
**Current State:**
- `web` directory contains the frontend but is improperly linked in compose files.
- `research` directory contains Gemini Hackathon artifacts and architecture notes that need to be operationalized.

**Action Plan:**
- [ ] Fix `web` Docker builds to use the correct context.
- [ ] Extract actionable pipelines from `research` into `dagster_defs` and `machine_learning`.

## 5. CI/CD & Parent Directories (.github, .dlt, .beads)
**Current State:**
- Pivot from Forgejo to GitHub flows requires discarding `.forgejo` context and fully embracing `.github/workflows`.
- Hidden folder `.dlt` holds state that must be accounted for in the deployment cache.

**Action Plan:**
- [x] Create robust GitHub Actions workflows for Docker image building, Dagster CI, and Web deployment.
- [x] Update `education/README.md` to establish the new architecture paradigm, emphasizing GitHub CI/CD and the Gemini AI integration.

## Conclusion & Next Steps
1. Execute the root configuration cleanups.
2. Fix Docker compose contexts.
3. Migrate CI/CD to `.github`.
4. Switch to Code mode to implement these systematic changes.