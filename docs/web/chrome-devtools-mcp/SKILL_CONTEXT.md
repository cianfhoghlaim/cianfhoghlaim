# chrome-devtools-mcp — Skill Context

**Upstream:** [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp)  
**License:** Apache 2.0  
**Purpose:** MCP server that lets AI coding agents control and inspect a live Chrome browser via DevTools Protocol.

## How We Use chrome-devtools-mcp

This is the **canonical reference implementation** for our browser automation stack:
- **`sruth-browser`** — our Stagehand-based browser automation client
- **MCP protocol patterns** — reference for building custom MCP servers
- **Agent browser control** — design patterns for agent-driven browser interaction

## Key Integration Points

- **MCP server architecture** — rollup build, TypeScript, MCP SDK patterns
- **DevTools Protocol** — page navigation, network inspection, console access, performance tracing
- **Agent plugin patterns** — `.claude-plugin/`, `.gemini/` integration examples
- **Skill system** — browser automation skills for agents

## Reference Files (preserved)

- `README.md` — full documentation
- `LICENSE` — Apache 2.0
- `package.json` — npm package manifest
- `tsconfig.json` — TypeScript configuration
- `CHANGELOG.md` — release history
- `AGENTS.md` — agent instructions for this repo
- `CONTRIBUTING.md` — contribution guide
- `docs/` — documentation
- `skills/` — agent skill definitions

## Related Docs

- `docs/agents/browserbase/` — Browserbase integration docs
- `infrastructure/browser/` — our browser automation infrastructure
- `.agents/skills/browser/SKILL.md` — browser automation skill
- `.agents/skills/browserbase-cli/SKILL.md` — Browserbase CLI skill
