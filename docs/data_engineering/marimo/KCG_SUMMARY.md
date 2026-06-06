# marimo — KCG Summary

## What It Is
marimo is a reactive Python notebook framework (alternative to Jupyter) with Git-friendly .py file storage, deterministic execution, and built-in UI components. This directory contains the full marimo framework source with 40+ example notebooks covering UI elements, SQL integration, AI/LLM chat, control flow, markdown, layouts, testing, cloud deployment, and third-party integrations (HuggingFace, MotherDuck embeddings, Sage).

## Why This Matters for Kings' College Galway
marimo is the primary notebook/dashboard tool for the oideachais education data platform. The SQL notebooks demonstrate how to build reactive dashboards over DuckDB/MotherDuck curriculum data, the AI examples show how to embed LLM-powered chat into educational analytics, and the framework integration examples (FastAPI, Flask) inform how the Kings' College web frontend (TanStack Start) can embed marimo notebooks as interactive data exploration tools for teachers and students.

## Key Patterns Preserved
38 .md files remain, including:
- `README.md` — Overview of all marimo examples
- `marimo/README.md` — Full marimo framework README with architecture overview
- `marimo/SECURITY.md` — Security policy
- `marimo/README_Chinese.md`, `README_Japanese.md`, `README_Spanish.md`, `README_Traditional_Chinese.md` — Internationalized docs
- `ai/README.md`, `ai/chat/README.md`, `ai/tools/README.md` — AI/LLM integration patterns
- `sql/README.md`, `sql/misc/README.md` — SQL notebook patterns
- `cloud/README.md`, `cloud/modal/README.md`, `cloudflare/README.md` — Cloud deployment patterns
- `frameworks/README.md` + 4 framework-specific READMEs (FastAPI, Flask, FastHTML)
- `control_flow/README.md`, `layouts/README.md`, `markdown/README.md`, `misc/README.md`, `testing/README.md`, `ui/README.md`
- `third_party/README.md` + HuggingFace, MotherDuck, Sage integration READMEs

## Source Files
Full source removed (2026-06-06). Available at https://github.com/marimo-team/marimo

## What Was Removed
Python notebooks (.py), TypeScript/CSS source, JSON/YAML configs, HTML templates, Docker files, shell scripts, test snapshots, SVG images, lock files, .gitignore files
