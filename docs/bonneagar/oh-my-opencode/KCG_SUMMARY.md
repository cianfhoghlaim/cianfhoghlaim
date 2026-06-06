# Oh My OpenCode — KCG Summary

## What It Is
Oh My OpenCode is a powerful OpenCode plugin by Yeongyu Kim (code-yeongyu) that layers Claude Code/AmpCode features onto the OpenCode agent runtime. It provides multi-model AI agent orchestration (Sisyphus, oracle, librarian, explore, frontend-ui-ux-engineer, document-writer, multimodal-looker), 21 lifecycle hooks, 11 LSP/AST-Grep tools, curated MCP servers (context7, websearch_exa, grep_app), and a full Claude Code compatibility layer for commands, skills, agents, and MCPs.

## Why This Matters for Kings' College Galway
Oh My OpenCode is the agent orchestration backbone of our development infrastructure. The Sisyphus primary orchestrator agent drives autonomous infrastructure and curriculum pipeline tasks across the Cianfhoghlaim monorepo. The librarian agent powers multi-repository code analysis across our polyglot TypeScript + Python codebase, while the oracle agent provides strategic architecture review for Dagster pipelines and Cloudflare edge deployments. The Claude Code compatibility layer ensures our existing `.claude/` configuration and skill ecosystem remains functional under OpenCode. The plugin's LSP and AST-Grep tools are directly leveraged by our `códeolas` code intelligence library.

## Key Patterns Preserved
- `README.md` — Full project overview, installation, and agent documentation
- `README.ko.md`, `README.ja.md`, `README.zh-cn.md` — Multilingual READMEs
- `AGENTS.md` — Project knowledge base with architecture map, conventions, agent models table
- `src/agents/AGENTS.md` — Agent system documentation
- `src/hooks/AGENTS.md` — Lifecycle hook documentation
- `src/tools/AGENTS.md` — Tool system documentation
- `src/features/AGENTS.md` — Feature system documentation
- `.opencode/command/*.md` — OpenCode command definitions
- `CONTRIBUTING.md`, `LICENSE.md`, `CLA.md` — Governance documents

## Source Files
Full source removed (2026-06-06), available at https://github.com/code-yeongyu/oh-my-opencode

## What Was Removed
TypeScript source files (agents, hooks, tools, MCPs, features, config, auth, shared), build artifacts (dist/), test files, assets (images, JSON schemas), GitHub workflow definitions, npm package configuration, TypeScript config, index files, and all non-documentation files.
