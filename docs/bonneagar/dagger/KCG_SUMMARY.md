# Dagger — KCG Summary

## What It Is
Dagger is an open-source CI/CD pipeline engine that lets you define pipelines as code in Go, TypeScript, or Python. Pipelines run in containers and can be executed locally or in CI — the same pipeline runs everywhere. Created by the Dagger team, it uses BuildKit under the hood.

## Why This Matters for Kings' College Galway
The project uses Dagger for cross-language CI/CD in the polyglot monorepo. A single Dagger pipeline can build the Python Dagster assets, typecheck the TypeScript frontend, run the Rust Locket tests, and deploy infrastructure — all in one execution. The `DAGGER_GUIDE_INDEX.md`, `DAGGER_PATTERNS_ANALYSIS.md`, and `DAGGER_QUICK_REFERENCE.md` files capture the project's Dagger patterns.

## Key Patterns
- **Polyglot pipelines**: Go, TypeScript, or Python — choose your language
- **Containerized execution**: Every pipeline step runs in an isolated container
- **Local-first**: `dagger call` runs pipelines locally during development
- **BuildKit engine**: Incremental builds, layer caching, parallel execution

## Integration
- Dagger pipelines are defined in `infrastructure/pulumi/` and called via `bun run dagger:...` scripts
- Integrates with Komodo for GitOps-triggered deployments
- Uses Pangolin for secure container registry access

## Source Files
Full course website (rawkode-academy) source code removed (2026-06-05). Available at <https://github.com/dagger/dagger>. Key pattern docs retained: `DAGGER_GUIDE_INDEX.md`, `DAGGER_PATTERNS_ANALYSIS.md`, `DAGGER_QUICK_REFERENCE.md`.
