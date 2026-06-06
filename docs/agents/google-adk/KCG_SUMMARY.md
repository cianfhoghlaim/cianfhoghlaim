# Google ADK — KCG Summary

## What It Is
A **saoi** (base ReAct agent) scaffolded from Google's Agent Development Kit (ADK) starter pack, supporting the Agent2Agent (A2A) protocol. Includes examples for Firecrawl web research, academic research, deep search, bakery launch workflow, and multi-agent coordination. Built on Google Cloud Platform with Terraform deployment, Cloud Build CI/CD, and Vertex AI integration.

## Why This Matters for Kings' College Galway
Google ADK provides a production-grade multi-agent framework with native A2A protocol support — critical for the oideachais platform's need to coordinate between curriculum-scraping agents, embedding agents, and QA agents. The Firecrawl integration example demonstrates the exact web research pattern needed for scraping examinations.ie and curriculum.ie content. The A2A protocol's inter-agent routing maps directly to the planned micro-agent architecture for lesson plan generation, where specialized agents (history, language, science) must coordinate. The agent-starter-pack scaffolding pattern provides a template for standardizing all Cianfhoghlaim agent deployments with consistent CI/CD, testing, and observability.

## Key Patterns Preserved
- `README.md` — Saoi base ReAct agent: project structure, requirements, quick start, A2A protocol, ADK concepts
- `GEMINI.md` — AI-assisted development guide with project conventions and ADK-specific patterns
- `deployment/README.md` — GCP + Terraform deployment guide for production agent hosting
- `tests/load_test/README.md` — Load testing configuration for agent endpoints
- `examples/firecrawl/README.md` — Firecrawl web scraping agent with tool-use examples and agent teams
- `examples/firecrawl/docs/tool-usage-examples.md` — Concrete Firecrawl MCP tool examples
- `examples/firecrawl/docs/agent-team.md` — Multi-agent team coordination pattern with Firecrawl
- `examples/firecrawl/docs/quickstart-streaming.md` — Streaming response quickstart guide
- `examples/launchmybakery/README.md` — End-to-end bakery business workflow agent
- `examples/launchmybakery/google.md` — Google Cloud-specific bakery agent deployment
- `examples/with-adk/README.md` — ADK integration patterns overview
- `examples/with-adk/a2a/typescript/README.md` — TypeScript A2A client example
- `examples/with-adk/a2a/docs/README.md` — A2A protocol documentation
- `examples/with-adk/a2a/docs/ag_ui.md` — Agent-User Interaction (AG-UI) protocol with ADK
- `examples/deep-search/README.md` — Deep search research agent pattern
- `examples/academic-research/README.md` — Academic research agent workflow

## Source Files
Full source removed (2026-06-06), available at:
- ADK: https://github.com/GoogleCloudPlatform/agent-starter-pack
- ADK SDK: https://github.com/google/adk-python

## What Was Removed
Python source (`.py`), Jupyter notebooks (`.ipynb`), Terraform HCL (`.tf`, `.tfvars`), YAML configs (`deployment.yaml`, `cloudbuild.yaml`), lock files (`uv.lock`, `yarn.lock`), `Makefile`, `Dockerfile`, `pyproject.toml`, `.env.example`, shell scripts, JSON configs, and all non-markdown assets.
