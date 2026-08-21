# CHEATSHEET.md — Cianfhoghlaim in 60 Seconds

> **The quick-reference card.** For the full onboarding, see
> [`NEW-USER-ONBOARDING.md`](NEW-USER-ONBOARDING.md).

## The 5-Minute Setup

```bash
brew install mise
mise install
bun install && uv sync
bun run secrets:env
bun run secrets:init   # requires Infisical on :8081
```

## The 5 Daily Commands

```bash
mise run core                # sync + install + lint + test + format
mise run data                # lakehouse + Dagster + CocoIndex
mise run devops              # IaC + stacks + Komodo/Pangolin
mise run ml                  # OCR/HTR + 12-agent fleet
mise run web                 # web/apps + Turborepo
```

## The 5 CI Gates

```bash
mise run lint:skills              # 65/65 skills pass
mise run lint:drift-docs          # AGENTS.md numbers in sync with reality
mise run lint:registry           # no hardcoded model strings in agents/
mise run cic:stack-doctor         # 94 stacks GOLD_STANDARD conformant
mise run lint:mcp-runtime         # 12/12 enabled MCPs have smoke tasks
```

## The 12-MCP Surface (per `2026-08-21-mcp-server-revival-overview.md`)

| Domain | MCPs |
|:--|:--|
| **code search** | ccc |
| **web data** | firecrawl + crawl4ai + chrome |
| **data engineering** | dlt-workspace + motherduck |
| **knowledge/memory** | cognee + graphiti + design-system |
| **observability** | langfuse |
| **secrets** | infisical |
| **model hub** | huggingface |

## The 3 Secrets You MUST Populate

| Secret | How |
|:--|:--|
| `INFISICAL_CLIENT_ID` | Create machine identity in Infisical UI, copy to `.infisical.env:699` |
| `INFISICAL_CLIENT_SECRET` | Same as above, copy `client_secret` |
| `CRAWL4AI_JWT_SECRET` | `openssl rand -hex 32`, push to vault `cianfhoghlaim/crawl4ai-jwt-secret` |

## The 3 Network Dependencies

| Dependency | Setup |
|:--|:--|
| **Cloudflare DNS for `*.cianfhoghlaim.ie`** | CNAME `*` → Pangolin host |
| **Cloudflare API token** | Cloudflare → API Tokens → Edit zone DNS |
| **The 8 third-party API accounts** | Firecrawl, HuggingFace, OpenAI, Anthropic, DeepSeek, Gemini, Z.ai, Komodo |

## The 5 Most Common Failure Modes

| Symptom | Fix |
|:--|:--|
| `mise can't find task X` | `openspec list 2>&1 \| grep X` |
| `MCP not registering` | `mise run lint:mcp-runtime` |
| `Stack fails stack-doctor` | `bash scripts/stack-doctor.sh` |
| `Infisical returns 401` | populate the 3 `INFISICAL_*` values, re-run `secrets:init` |
| `Browser MCP returns 401` | populate `CRAWL4AI_JWT_SECRET` (v0.9.0 secure-by-default contract) |

## The 3 Openspec Commands You Run Daily

```bash
openspec list                       # what changes are pending
openspec validate <id> --strict     # before commit
openspec archive <id> --yes         # after deploy
```

## The 3 Path Shortcuts

| What | Where |
|:--|:--|
| **The big picture** | [`README.md`](README.md) |
| **The agent surface** | [`AGENTS.md`](AGENTS.md) |
| **The IaC + stacks** | [`bonneagar/README.md`](bonneagar/README.md) |

## The 3 Numbers to Remember

- **94** — total Docker Compose stacks in `bonneagar/stacks/`
- **12** — total enabled MCP servers (after `f63c6a57b`)
- **137** — total openspec items validated (per `openspec validate --all`)

---

Last updated: 2026-08-21.
