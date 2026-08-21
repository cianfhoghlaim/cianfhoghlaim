# 2026-08-22 — ccc grep + ccc doctor + ccc version (adopt the newest cocoindex-code features)

## Why

We use `ccc search` extensively (14 refs across mise.toml + workflows + agents) but never `ccc grep`, `ccc doctor`, or `ccc version`. Cocoindex-code 0.2.37+ shipped three new subcommands that are direct improvements:

- **`ccc grep <pattern>`** (0.2.37+) — STRUCTURAL code search by example. Doesn't need the index daemon (works offline / during index rebuilds). Per the upstream docs: "Compiles the pattern per language and matches every supported source file under PATH in parallel."
- **`ccc doctor`** (0.2.40+) — system health check. Surfaces daemon-side exception tracebacks + index freshness + LMDB map size warnings.
- **`ccc version`** (0.2.40+) — explicit version command (we currently can't get the ccc version, only `ccc --help`).

The biggest win is `ccc grep` — much faster for the common case of "find this function signature" because it doesn't require the embedding index. Today when an agent needs to find a function across the repo, it has to either:
1. Use `ccc search <query>` (semantic; needs index daemon; ~1s)
2. Use `rg` (text-only; misses AST matching)

`ccc grep` adds option 3: AST-aware pattern matching, no daemon. Particularly useful for the 9 domain agents + the 4 primary agents when they need to find a specific class/method signature.

## What changes

1. Add 4 new tasks to the `core` namespace in `mise.toml`:
   - `core:ccc:grep` — structural search (no daemon)
   - `core:ccc:doctor` — system health check
   - `core:ccc:version` — print version
   - `core:ccc:search:json` — semantic search with JSON output (for tool integration)

2. Update 9 domain-specific agent `.md` files (`.opencode/agents/{data-platform,infrastructure,agent-platform,frontend-apps,notebooks,baml,dagster,mise,proposal-author}.md`) to recommend `ccc grep` for quick code lookups.

## Dependencies

- **Blocked by:** none
- **Blocked by (soft):** `2026-08-19-dev-tooling-refactor-mise-opencode-openspec-v1` (extends the opencode agent markdown format)
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. `mise run core:ccc:grep "def <method>(" orchestration/` returns matches without invoking the daemon
2. `mise run core:ccc:doctor` exits 0
3. `mise run core:ccc:version` prints `0.2.41`
4. `mise run core:ccc:search:json "dagster asset"` emits JSON on stdout
5. All 9 domain agent `.md` files reference `ccc grep` in their "Direct references" section
6. `openspec validate --all --strict` exits 0

## Out of scope

- Updating `bun.lock` to include ccc 0.2.41 (it's already installed)
- Adding `ccc grep` to the primary agents (build, plan, research, orchestrator) — they can use it via `bun run ccc:grep` directly
- Migrating from `ccc search` to `ccc grep` (they're complementary — semantic vs structural)

## Rollback plan

Single commit. Revert via `git revert` if any task fails. The agent `.md` updates are additive (no existing prompts removed).
