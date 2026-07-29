# Cianfhoghlaim — Coláiste na Déisigh

> **Cianfhoghlaim** — *long-distance, enduring learning*. A research-and-deployment platform for the **British Isles education corpus** (8 nations × 5 stages × bilingual Goidelic + Brythonnic), agentic AI, self-hosted infrastructure, and minority-language machine learning. Maintained by **Cian Mac an Déisigh Uí Liatháin (Deacy-Lyons)**.

[![Leabharlann](https://img.shields.io/badge/leabharlann-2.4k_files_/_3.4_GB-blueviolet)](https://github.com/cianfhoghlaim/leabharlann)
[![Bonneagar](https://img.shields.io/badge/bonneagar-IN_THIS_REPO_(%2Fbonneagar%2F)-green)](./bonneagar/)
[![License](https://img.shields.io/badge/license-BUSL_1.1-green)](LICENSE.md)
[![v7 flat](https://img.shields.io/badge/v7-flattened_2026--07--17-informational)](openspec/changes/2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1/)

> **Useful companion resources:** To understand the container, data, indexing,
> storage, and infrastructure patterns used throughout this project, see the
> hands-on labs at [iximiuz Labs](https://labs.iximiuz.com/), the database
> references at [DBQuacks](https://dbquacks.com/), and the official
> documentation, blogs, and examples for
> [CocoIndex](https://cocoindex.io/), [dlt](https://dlthub.com/docs/),
> [LanceDB](https://lancedb.com/), [DuckDB](https://duckdb.org/docs/),
> [MotherDuck](https://motherduck.com/docs/), [Komodo](https://komo.do/), and
> [Pangolin](https://docs.pangolin.net/). These are useful external guides to
> the key technologies and design choices represented in the repository.

---

## Mise Tasks (priority quick reference)

The 3 priority `mise run` tasks shipped by the 2026-07-30 → 2026-08-01 trilogy at a glance. **Read this first**; the full priority quick-refs are in [`AGENTS.md`](AGENTS.md).

| Task | One-line purpose |
|:--|:--|
| [`cic:stack-doctor`](AGENTS.md) | Validate all 89 Docker Compose stacks against the 6-file `GOLD_STANDARD` (the canonical CI gate) |
| [`stack-doctor:strict`](AGENTS.md) | `cic:stack-doctor` + `--strict --check-grammar` — fails on missing `infisical://` refs OR mixed bare/Jinja grammar in any `secrets.env` (Change 1, 2026-07-30) |
| [`deploy:full`](bonneagar/AGENTS.md#deployfull-orchestrator) | One-command 7-phase full-stack deploy orchestrator (preflight → control-plane → lakehouse → data → agents → materialize → sensor health), with a resumable checkpoint at `~/.cianfhoghlaim/deploy-state.json` (Change 3, 2026-08-01) |

---

## Addendum — A note for anyone looking at this project right now

> **The project is sprawling on purpose.** It is a research-and-deployment
> platform for the British Isles education corpus, an agentic AI fleet, a
> self-hosted infrastructure mesh, and a minority-language ML playground
> — all federated by a single `bun + uv + turbo` monorepo. Because the
> goal is a deliberately overcomplicated Master's completed in a year,
> many subsystems that *do* work are partially obscured by the design
> choices meant for *my* team's downstream use. Read this section before
> forming an opinion about the repo.
>
> **The value for anyone looking at this project today is in the
> specific combinations of already well-calculated open-source
> packages.** The data engineering (DLT + Dagster + BAML + CocoIndex +
> DuckLake + LanceDB + MotherDuck + Marimo), the DevOps (Komodo +
> Pangolin + Infisical + Locket + Pocket ID + Traefik + Garage S3), the
> web-development (TanStack Start + Convex + Hono + CopilotKit + oRPC +
> AG-UI + Cloudflare), and the agent layer (Agno + Google ADK + Pydantic
> AI + LiteLLM + Letta + Cognee + Graphiti + Langfuse + MLflow) are each
> real, working open-source compositions. You can copy any slice
> independently.
>
> **You can take the same data pipelines and rewire them for any other
> jurisdiction.** The `dlt_sources/` + `baml_src/` + `cocoindex/` +
> `motherduck/` + `notebooks/` stack already produces the official
> legal, medical, education, and government documents for the British
> Isles. Retargeting it for, say, the US CMS, the WHO IRIS repository,
> the *Bundesministerium für Bildung*, or the French *Ministère de
> l'Éducation* means changing the jurisdiction enum, the BAML schemas,
> the scrape cache roots, and the destination namespaces — the core
> pipeline shape stays the same. Use `USE_LOCAL_SCRAPES=true` while you
> rebuild; the curated cache at `stedding/ingest_queue/` lets you iterate
> without spending scrape credits.
>
> **The cheapest way to do this is a cheap coding agent.** A
> €20/month **Gemini Deep Research Pro** subscription is the right tool
> for the *first* hour — finding the authoritative ministry, exam-board,
> or medical-register endpoints and the licensing constraints. A
> **MiniMax coding plan** (or the local **OpenCode Go** CLI) is the right
> tool for the *next* two days — the iterative file-local refactor
> across `dlt_sources/` + `baml_src/` + `cocoindex/` + `motherduck/`.
> **GitHub Copilot** is a fine runner-up for single-file edits. None of
> them need the full monorepo.
>
> **Use my notes as a blueprint for your own deep-research tangent.**
> The [`leabharlann`](https://github.com/cianfhoghlaim/leabharlann)
> repository (3.4 GB, 216 docs × 6 subdirs) holds the source materials
> that informed *every* sub-agent, BAML schema, and CocoIndex flow in
> this repo. They are unique to my circumstances; treat them as a
> worked example of *how* to do a deep-research tangent in this domain,
> not as *what* to copy. The benefit of doing this kind of testing with
> the named tools is that you get a working knowledge graph + a working
> pipeline + a working dashboard in roughly one weekend.
>
> **The full per-area deep-cuts report — what each package composes,
> which 3-5 files to copy, which 5 lines to change, which 1 assumption
> is hardest to escape, and which coding agent to point at which job
> — lives at [`docs/CHOP_AND_CHANGE_GUIDE.md`](docs/CHOP_AND_CHANGE_GUIDE.md).**

---

> ## ⚠️ Important Disclaimer
>
> The **data engineering pipelines** in this repository — DLT ingestion,
> BAML extraction, CocoIndex v1 embeddings, Cognee cognify passes, the
> 11 NCCA Leaving Certificate subject asset groups — process official
> Government syllabus exam papers + marking schemes of the Republic of
> Ireland (NCCA Leaving Certificate, Junior Cycle, Primary) and the
> wider British Isles education system. They are **grounded in the 8
> British Isles nations** (Ireland, England, Scotland, Wales,
> Northern Ireland, Isle of Man, Jersey, Guernsey) and bilingualised
> in EN + GA (Gaeilge).
>
> The **web UIs** (`cianfhoghlaim-web`, `tuatha-ui`, `croilar-web`,
> `croilar-portal`, `game_showcase`, `tuatha-demo`, the Hono API
> gateway) are packaged demos that prove the agentic-web wiring works.
> They are **not yet** the final pedagogical surface — the UI work is
> deferred until the data pipeline has produced the canonical
> syllabus-accurate assets.

---

## 🚀 Quick Start for New Operators — Pocket ID + Komodo + Pangolin Onboarding

> **If you're new to this repo, start here.** This section gets the
> Pocket ID + Komodo + Pangolin + TinyAuth stack wired up so you can
> use a single Pocket ID passkey to log in to ALL services. The
> entire flow is automated via 4 bash scripts + 1 openspec change.

The 5 steps that were once manual (and the scripts that automate them):

| # | Step | Was manual | Now automated by |
|---|---|---|---|
| 1 | Create Pocket ID OIDC client for Komodo | ❌ | `scripts/wire-pocketid-pangolin-komodo.sh` |
| 2 | Update Komodo's OIDC config | ❌ | `scripts/wire-pocketid-pangolin-komodo.sh` |
| 3 | Add Pocket ID as Pangolin Identity Provider | ❌ | `scripts/wire-pocketid-pangolin-komodo.sh` |
| 4 | Bind PocketID IdP to every Pangolin Resource | ❌ | `scripts/wire-pocketid-resource-idp.sh` |
| 5 | Self-configure Komodo + Periphery | ❌ | `scripts/bootstrap-komodo-periphery.sh` |

Plus 2 supporting scripts for ongoing maintenance:

| Script | Purpose | When to run |
|---|---|---|
| `scripts/onboard-pocketid.sh` | Guided TUI/CLI wizard for non-technical operators | Once per cluster (or when adding a new operator) |
| `scripts/rotate-pocketid-secrets.sh` | 90-day cron for OIDC client secret rotation | Cron: `0 3 1 */3 * *` |

---

### 1. The 3 things you need (TL;DR for non-technical operators)

You need **3 credentials** (one-time, to paste into the onboarding wizard):

| Credential | Where to get it | Scope |
|---|---|---|
| `POCKETID_API_KEY` | https://auth.cianfhoghlaim.ie → Settings → API Keys → Create (Admin scope) | Admin API key for Pocket ID |
| `PANGOLIN_API_KEY` | https://pangolin.cianfhoghlaim.ie → Settings → API Keys → Create (Orgs/Resources scope) | Pangolin API key for resource binding |
| `KOMODO_PASSWORD` | Your Komodo admin user's password (or skip if Komodo isn't deployed yet) | Komodo admin login |

**That's it.** The wizard handles the rest: validation, persistence, and
the full Pocket ID + Komodo + Pangolin wiring.

---

### 2. The guided onboarding wizard (one command for the whole flow)

```bash
./scripts/onboard-pocketid.sh
```

The wizard will:
1. **Ask 3 questions** (the 3 credentials above + optional URL/username overrides)
2. **Validate each** against its source service via live HTTP calls
3. **Write to .env** at the repo root (idempotent upsert)
4. **Optionally persist to local Infisical** (if --with-infisical)
5. **Optionally run the wire script** (with --skip-wire to skip)

Options for the wizard:

| Flag | Purpose |
|---|---|
| `--non-interactive` | Use existing .env values (for CI / non-TTY) |
| `--pocketid-api-key=KEY` | Skip the prompt for the Pocket ID key |
| `--pangolin-api-key=KEY` | Skip the prompt for the Pangolin key |
| `--skip-komodo` | Skip the Komodo step (if Komodo isn't deployed yet) |
| `--skip-wire` | Don't run the wire script (just write to .env) |
| `--with-infisical` | Also persist to the local Infisical vault |
| `--domain=DOMAIN` | Override the cluster domain (default: cianfhoghlaim.ie) |
| `--help` | Full help |

**For non-technical users (interactive):** just run `./scripts/onboard-pocketid.sh` and follow the prompts.

**For CI / non-TTY (automated):**
```bash
./scripts/onboard-pocketid.sh --non-interactive --skip-wire
```

---

### 3. The 5-step wiring flow (after the wizard completes)

```bash
# Step 1: Pocket ID OIDC client + Komodo OIDC + Pangolin IdP
./scripts/wire-pocketid-pangolin-komodo.sh

# Step 2: Bind PocketID to every Pangolin Resource (4th manual step)
./scripts/wire-pocketid-resource-idp.sh --all

# Step 3: Bootstrap Komodo + Periphery (5th step, auto-configure)
./scripts/bootstrap-komodo-periphery.sh

# Step 4: Verify end-to-end
curl -ksS https://komodo.cianfhoghlaim.ie/api/v1/system-info | jq
curl -ksS https://langfuse.cianfhoghlaim.ie/api/public/health | jq
# Visit https://mlflow.cianfhoghlaim.ie in a browser and click "Login with Pocket ID"
```

For per-step flags (e.g. --dry-run, --skip-komodo, --skip-pangolin), run each
script with `--help`.

---

### 4. The 90-day cron rotation (for long-term maintenance)

Pocket ID rotates the OIDC client_secret on every fetch. So we need a
fresh secret every time we need one (never store one). The `rotate-pocketid-secrets.sh`
script does this automatically:

```bash
# Add the cron job (runs at 3am on the 1st of every 3rd month)
echo "0 3 1 */3 * * $PWD/scripts/rotate-pocketid-secrets.sh" | crontab -

# Test the rotation script manually
./scripts/rotate-pocketid-secrets.sh
```

This will:
1. Fetch a fresh secret via Pocket ID admin API (X-API-Key auth)
2. Use it immediately to get a fresh Pocket ID access_token
3. Mint a fresh Pangolin API key (7-day TTL)
4. Update .env with the new key
5. Write an audit record to /tmp/pocketid-rotation-{ts}.json

---

### 5. The 4 scripts (TL;DR reference)

| Script | Lines | What it does |
|---|---|---|
| `scripts/onboard-pocketid.sh` | ~230 | Guided TUI/CLI wizard for non-technical operators (asks 3 questions, validates, persists to .env) |
| `scripts/wire-pocketid-pangolin-komodo.sh` | ~320 | Creates Pocket ID OIDC client + updates Komodo OIDC config + adds Pangolin IdP (3 of 5 steps) |
| `scripts/wire-pocketid-resource-idp.sh` | ~125 | Binds the PocketID IdP to every Pangolin Resource (4th step) |
| `scripts/bootstrap-komodo-periphery.sh` | ~200 | Self-registers Periphery with Pangolin, auto-derives the wire between Komodo+Periphery (5th step) |
| `scripts/rotate-pocketid-secrets.sh` | ~115 | 90-day cron job for OIDC client secret rotation |

Plus 1 openspec change:
`openspec/changes/2026-07-28-pocketid-komodo-periphery-onboarding-v1/` (proposal + tasks + 2 spec ADDED Requirements).

---

### 6. The openspec change + audit log

The 5-step flow + 2 supporting scripts are documented in:
- `openspec/changes/2026-07-28-pocketid-komodo-periphery-onboarding-v1/proposal.md`
- `openspec/changes/2026-07-28-pocketid-komodo-periphery-onboarding-v1/tasks.md`
- `openspec/changes/2026-07-28-pocketid-komodo-periphery-onboarding-v1/specs/infrastructure-stacks/spec.md`

The earlier (3-step) wiring change is in:
- `openspec/changes/2026-07-28-pocketid-pangolin-komodo-oidc-wiring-v1/` (4 files)

The 30-day refactor (fix for the locket v0.17.3 → Infisical v0.161+ API mismatch) is in:
- `scripts/bons-locket-shim.py` (the v0.2.0 Python-based drop-in replacement)
- `bons-locker-shim:infisical-0.2.0` (the local Docker image)

---

### 7. What if a step fails (the troubleshooting matrix)

| Symptom | Likely cause | Fix |
|---|---|---|
| "Invalid client secret" on Pocket ID | Stale `POCKETID_PANGOLIN_CLIENT_SECRET` in .env | Re-run `onboard-pocketid.sh` (the refactored `pocketIdLogin` fetches a fresh secret) |
| "CSRF token missing" on Pangolin session | Browser-flow required (Pangolin needs a real user-agent) | Use the dashboard to mint the API key, or implement a headless browser (Playwright/Puppeteer) |
| "Resource not found" on Resource IdP binding | The Resource hasn't been deployed yet, or the FQDN is wrong | Run `./scripts/wire-pocketid-resource-idp.sh --all` to bind to all Resources |
| "401 Unauthorized" on Pocket ID admin API | Stale `POCKETID_API_KEY` | Re-mint the API key at https://auth.cianfhoghlaim.ie → Settings → API Keys |
| "PocketID IdP not found" | The 3-step wire script hasn't been run | Run `./scripts/wire-pocketid-pangolin-komodo.sh` first (creates the IdP) |

---

### 8. The non-technical user TL;DR (copy/paste this for your team)

```bash
# 1. Get the 3 credentials (ask the previous operator if you're not sure):
#    - POCKETID_API_KEY from https://auth.cianfhoghlaim.ie → Settings → API Keys
#    - PANGOLIN_API_KEY from https://pangolin.cianfhoghlaim.ie → Settings → API Keys
#    - KOMODO_PASSWORD from your Komodo admin

# 2. Run the wizard (interactive)
./scripts/onboard-pocketid.sh
#    (paste the credentials when prompted)

# 3. Run the wire script (5 manual steps → 1 command)
./scripts/wire-pocketid-pangolin-komodo.sh

# 4. Bind PocketID to all your Resources
./scripts/wire-pocketid-resource-idp.sh --all

# 5. Bootstrap Komodo+Periphery (5th step)
./scripts/bootstrap-komodo-periphery.sh

# 6. Add the 90-day cron rotation
echo "0 3 1 */3 * * $PWD/scripts/rotate-pocketid-secrets.sh" | crontab -

# 7. Verify (in a browser)
#    Visit https://komodo.cianfhoghlaim.ie → click "Login with Pocket ID"
#    Or visit https://mlflow.cianfhoghlaim.ie → click "Login with Pocket ID"
#    Both should work with a single Pocket ID passkey.
```

That's it. The entire Pocket ID + Komodo + Pangolin wiring is now a 1-line
interactive wizard + 4 commands for the operator.

---

## 🚀 Quick Start for New Operators — Tuatha (Educational MMO)

Tuatha is the educational Massive Multiplayer Online game world of the
Cianfhoghlaim platform — the public face where students pilot avatars
through procedurally-generated Celtic landscapes and run quests tied to
the BIEP Leaving Certificate syllabus. Tuatha is the **only stack that
is publicly reachable**: game at `https://tuath.cianfhoghlaim.ie`,
API + UI TinyAuth passkey-gated.

The Tuatha IaC stack now ships the same GOLD_STANDARD contract that
Pocket ID has demonstrated works (7 files, 4 onboarding scripts, 90-day
cron rotation). To bring it up from scratch:

```bash
# 1. Run the Tuatha onboarding wizard (12 secrets collected, written to .env)
./scripts/onboard-tuatha.sh

# 2. One-command local dev (builds api/ui/game containers, seeds SpacetimeDB,
#    runs both dlt sources → local DuckDB at ./tuatha.duckdb)
./tuatha/scripts/bootstrap.sh

# 3. Optionally install the 90-day secret rotation cron
sudo ./scripts/rotate-tuatha-secrets.sh --install-cron
```

| Surface | URL | Auth |
|:--|:--|:--|
| Babylon.js game client | `https://tuath.cianfhoghlaim.ie` | public, rate-limited |
| FastAPI surface | `https://tuath-api.cianfhoghlaim.ie` | TinyAuth passkey (Pocket ID) |
| TanStack UI dashboard | `https://tuath-ui.cianfhoghlaim.ie` | TinyAuth passkey (Pocket ID) |

The 4 onboarding scripts in `scripts/` follow the exact same naming
convention, colour scheme, arg shape, and audit-record pattern as the 4
Pocket ID scripts. Once you learn one set you've learned the other.

| Script | Purpose | Mirrors |
|:--|:--|:--|
| `scripts/onboard-tuatha.sh` | TUI/CLI wizard → writes 12 secrets to `.env` | `scripts/onboard-pocketid.sh` |
| `scripts/wire-tuatha.sh` | ONE-SHOT Pocket ID OIDC client + 3 Pangolin resources + Komodo trigger + Infisical seed | `scripts/wire-pocketid-pangolin-komodo.sh` |
| `scripts/wire-tuatha-resource-idp.sh` | Binds Pocket ID as Resource IdP for the 2 TinyAuth-gated routes | `scripts/wire-pocketid-resource-idp.sh` |
| `scripts/rotate-tuatha-secrets.sh --install-cron` | 90-day cron rotation of Pocket ID + Pangolin + Komodo + Infisical keys | `scripts/rotate-pocketid-secrets.sh` |

The dlt pipeline surfaces both Tuatha event streams into the central
`md:cianfhoghlaim` MotherDuck lakehouse at
`cianfhoghlaim.tuatha.player_assets` and
`cianfhoghlaim.tuatha.credential_events`. See
[`tuatha/README.md`](./tuatha/README.md) and the dlt sub-dir
[`tuatha/dlt/`](./tuatha/dlt/) for the full reference.

---

## TL;DR — What this is, today

`cianfhoghlaim` is a **polyglot monorepo** (`bun + uv + turbo`) that:
1. **Ingests** the curriculums, exam papers, marking schemes, and
   syllabi of the **8 British Isles nations** (with bilingual EN + GA
   extraction for the Irish strand).
2. **Extracts** structured data via 30+ BAML schemas (NCCA, SEC, CCEA,
   SQA, WJEC, Edexcel + the European Union EUR-Lex / ECDC / EMA /
   Eurostat / Eurydice + the multi-nation Commonwealth + Americas
   expansions).
3. **Embeds** in vector + graph form via 42+ CocoIndex v1 Apps +
   Cognee cognify layers + the Graphiti temporal knowledge graph.
4. **Surfaces** through marimo reactive notebooks, MotherDuck Dives,
   TanStack Start web apps, and a 12-agent meaisínfhoghlaim fleet
   (LiteLLM-routed via OpenCode Go API).
5. **Hosts itself** on the `bunchloch` MacBook M4 Max (data plane) +
   `arm1-oci` Oracle Cloud free-tier (control plane) + Garage S3
   storage + 88 Docker Compose stacks + the Komodo / Pangolin /
   Infisical / Locket / Pocket ID / TinyAuth / Traefik mesh.

The author is a Mathematics & Education teacher / Dioplóma C1 in
Irish / agentic-AI engineer based in Galway and East Belfast — a
[registered member of the Teaching
Council](cian_mac_an_déisigh_uí_liatháin/teaching/teaching_registration.pdf),
with verified memberships in [Fine
Gael](cian_mac_an_déisigh_uí_liatháin/identity/politics/fine_gael_member_latest.pdf)
and the [Alliance
Party](cian_mac_an_déisigh_uí_liatháin/identity/politics/alliance_membership.pdf)
of Northern Ireland, and the
[Deacy Tribe of the Morris-Conroy tribes of
Galway](cian_mac_an_déisigh_uí_liatháin/identity/lineage).

## Monorepo Topology (v7 — Flattened Polyglot)

Two language graphs live side by side, orchestrated by `turbo.json`
and a single `mise.toml` toolchain. Post-v7 (2026-07-17), the
Python package IS the repo root — no more `cianfhoghlaim/`
nesting.

### TypeScript graph (bun workspaces)
| Workspace | Path | Purpose |
|:--|:--|:--|
| `cianfhoghlaim-web` | `web/apps/cianfhoghlaim-web/` | TanStack Start + React front-end (the public web app) |
| `tuatha-ui` | `web/apps/tuatha-ui/` | Túatha educational MMO front-end |
| `croilar-web` | `web/apps/croilar-web/` | Croílár multi-persona portfolio |
| `croilar-portal` | `web/apps/croilar-portal/` | Croílár portfolio dashboard |
| `tuatha-demo` | `web/apps/tuatha-demo/` | Tuatha Babylon.js demo |
| `game_showcase` | `web/apps/game_showcase/` | Web game showcase |
| `cianfhoghlaim-mcp-filesystem` | `web/apps/cianfhoghlaim-mcp-filesystem/` | Filesystem MCP server for the data platform |
| `hono-api` | `web/hono-api/` | Hono API gateway |

### Python sub-packages (uv at root)
| Sub-package | Path | Purpose |
|:--|:--|:--|
| `agents` | `agents/` | The 12-agent meaisínfhoghlaim fleet + ADK shims |
| `baml` | `baml/` | The BAML extraction schemas (LC + Celtic + multi-nation) |
| `cocoindex` | `cocoindex/` | 42+ CocoIndex v1 Apps |
| `dlt` | `dlt/` | DLT sources + destinations |
| `orchestration` | `orchestration/` | Dagster assets + jobs + schedules + sensors |
| `codeolas` | `libraries/codeolas/` | Publishable code intelligence sub-package |

### IaC subdirectory
The GitOps infrastructure lives in the `bonneagar/` subdirectory and
is reached via `bun run --cwd bonneagar iac:<command>` from the
root `package.json`. The IaC is no longer a separate GitHub repo —
the `archive-bonneagar` remote is a frozen read-only archive.

| IaC area | Path |
|:--|:--|
| IaC source (TypeScript) | `bonneagar/iac/` |
| 88 Docker Compose stacks | `bonneagar/stacks/<name>/` |
| Komodo resource-syncs | `bonneagar/komodo/` |
| Pangolin config | `bonneagar/pangolin/` |
| Deploy runbooks | `bonneagar/deploy-runbooks/` |
| Audit scripts | `bonneagar/audit/scripts/` |

## What changed in v7 (2026-07-17)

- **Flattened `cianfhoghlaim/`.** The Python package is the repo
  itself; the redundant nesting from the v4 consolidation is gone.
- **Re-merged `bonneagar/`.** The IaC is now a subdirectory of this
  repo (not a separate GitHub repo). It's still wrapped with the
  same `--cwd bonneagar` shim so the iac:* scripts work the same.
- **Updated LICENSE.md.** The "companion repository cianfhoghlaim/bonneagar"
  sentence is removed; the leabharlann companion sentence stays.
- **Pruned remote branches.** The 23 shipped `feat/*` + `pick-*` +
  `q3-2026-*` branches are deleted from `origin` (local branches
  preserved per the user's instruction).

See [`openspec/changes/2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1/`](openspec/changes/2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1/)
for the full change record (proposal + tasks + cross-repo-sync +
5 spec deltas + migration-audit).

## The 5-stage architecture

The pipeline walks a corpus from raw disk to an agent-consumable,
semantically-indexed artifact. Five sequential stages live under
`orchestration/defs/<stage>/`:

| Stage | Home | What it does |
|:--|:--|:--|
| 1. Ingestion | `orchestration/defs/1_ingestion/` | DLT sources for 8 nations × 4 domains + filesystem + api + language special sources. Auto-discover via the global-region-source-contract. |
| 2. Materials | `orchestration/defs/2_materials/` | BAML extraction (the 30+ baml/ schemas) + pdf processing + asset pre-processing |
| 3. Model Lifecycle | `orchestration/defs/3_model_lifecycle/` | CocoIndex v1 embedding Apps (42 flows) + LanceDB / DuckLake materialisation + RAGAS eval |
| 4. Asset Generation | `orchestration/defs/4_asset_generation/` | Subject-specific asset packs (8 NCCA LC subjects × per-subject quest packs + the 8-ADK agent fleet) |
| 5. Agent Operations | `orchestration/defs/5_agent_ops/` | The 12-agent meaisínfhoghlaim fleet + OpenChamber/OpenClaw/Hermes/Croílár surfaces + RisingWave event stream |

## British Isles Education Pipeline (BIEP) — the flagship

The 6 Irish LC priority subjects — **Mathematics, Chemistry,
Geography, Gaeilge, English, Computer Science** — get the deep
treatment: NCCA syllabus + SEC exam papers + marking schemes + 7
v1 CocoIndex flows + 42 Dagster assets + 6 marimo notebooks + 4
MotherDuck Dives + a daily MotherDuck Flight.

The BAML extraction schemas (`baml/education/lc_extraction/*.baml`)
produce structured `LeavingCertSyllabus`, `LeavingCertPastPaper`,
`LeavingCertMarkingScheme` objects — rubric-anchored to NCCA PDF
page references. Web search by the 12-agent fleet always lands on
an in-pipeline asset, never on a stale URL.

## The 12-agent meaisínfhoghlaim fleet

Located at `agents/`. One root agent orchestrates 11 specialists,
all routed through the canonical LiteLLM alias `minimax` (with a
7-tier model fallback):

| Agent | Domain |
|:--|:--|
| `root_agent.py` | The orchestrator — routes questions to the right specialist |
| `curriculum_agent.py` | NCCA LC subject routing |
| `curriculum_comparison_agent.py` | Cross-nation curriculum diff |
| `corpus_agent.py` | Leabharlann corpus queries |
| `research_agent.py` + `research_assistant_agent.py` | British Isles education research |
| `education_research_agent.py` | Pedagogy literature + annotation |
| `bunchloch_research_agent.py` | Local MacBook M4 Max inference routing |
| `geospatial_agent.py` | OS Maps + GIS queries |
| `statistics_agent.py` | CSO + Eurostat + UK ONS data |
| `translation_agent.py` | EN ↔ GA ↔ GBC ↔ Cyr ↔ BrK ↔ BrL bilingual |
| `mythology_narrator_agent.py` | Tuatha Dé Danann + Celtic lore retrieval |
| `agui_curriculum_agent.py` | AG-UI protocol surface for the leaving cert portal |

Each agent has its own Langfuse trace + MLflow experiment +
RAGAS asset_check. Full observability via the unified stack at
`observability/`.

## Personal credential corpus (verified references)

These are the records that ground the project's claims. They live
in `cian_mac_an_déisigh_uí_liatháin/` at the repo root:

| Credential | Verified PDF |
|:--|:--|
| Teaching Council of Ireland registration | `cian_mac_an_déisigh_uí_liatháin/teaching/teaching_registration.pdf` |
| MSc AI admission (2026-2027, University of Galway) | `cian_mac_an_déisigh_uí_liatháin/achievement/2026_2027_msc_in_ai_university_gaillimhe.pdf` |
| BSc Maths & Education (First Class Honours, 78.84%) | `cian_mac_an_déisigh_uí_liatháin/achievement/ba_and_hdip_transcript.pdf` + `bachelors_degree_parchment.jpeg` |
| Higher Diploma in Software Design (First Class Honours) | `cian_mac_an_déisigh_uí_liatháin/achievement/higher_diploma_parchment.jpeg` |
| PGCE (BCS Computing scholarship) | `cian_mac_an_déisigh_uí_liatháin/teaching/bcs_pgce_computing_scholarship.png` |
| Torthaí Gaeilge (Irish-language exam results) | `cian_mac_an_déisigh_uí_liatháin/achievement/torthai_ghaeilge.pdf` |
| Apple Award (2013) | `cian_mac_an_déisigh_uí_liatháin/achievement/apple_award.pdf` |
| Royal Book Club (Buckingham letter) | `cian_mac_an_déisigh_uí_liatháin/achievement/buckingham_letter.pdf` |
| Deacy lineage (1986 Galway Advertiser article) | `cian_mac_an_déisigh_uí_liatháin/identity/lineage/neil_deacy_cookes_corner-galway_advertiser.pdf` |
| Late uncle's memorial (Éamonn "Chick" Deacy) | `cian_mac_an_déisigh_uí_liatháin/identity/lineage/uncle_eamonn_memorial_combined.pdf` |
| Dual citizenship (ROI + UK) | `cian_mac_an_déisigh_uí_liatháin/identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf` |
| Fine Gael membership | `cian_mac_an_déisigh_uí_liatháin/identity/politics/fine_gael_member_latest.pdf` |
| Alliance Party membership | `cian_mac_an_déisigh_uí_liatháin/identity/politics/alliance_membership.pdf` |

The full family history (the Triple Crown of the Corrib, the 4
kindreds, the dual-monarchy synthesis) lives in the section
preserved at the bottom of this README.

## Verified academic archive (in leabharlann/)

The course material + examination scripts + the personal academic
corpus live at `github.com/cianfhoghlaim/leabharlann` (a separate
3.4 GB repo, the only remaining separately-managed repo):

- `ollscoil_na_gaillimhe/` — BSc Mathematics & Education +
  Higher Diploma in Software Design (9 Mathematics modules × 7
  Software Design modules)
- `mae/` — Marimo notebook library
- `gemini_deep_research/` — 7 culture-PDF warrants grounding the
  family history narrative
- `gaeilge/`, `aigne/`, `zotero/` — Irish-language + AI research
  corpora

## Repository constellation (post-v7)

| Repo | Path | URL | Purpose |
|:--|:--|:--|:--|
| cianfhoghlaim (this) | `.` (root) | `github.com/cianfhoghlaim/cianfhoghlaim` | The Python package IS the repo |
| bonneagar (in-tree) | `bonneagar/` | (was `github.com/cianfhoghlaim/bonneagar`; now archived) | The 88-stack GitOps fleet + Komodo + Pangolin + Infisical |
| leabharlann (separate) | `leabharlann/` | `github.com/cianfhoghlaim/leabharlann` | 3.4 GB digital library corpus |

The `archive-bonneagar` remote at
`github.com/cianfhoghlaim/bonneagar.git` is frozen — no further
commits will be pushed; its history is preserved in-tree.

## Cross-cutting concerns

### OpenSpec workflow (canonical change management)
`openspec/` is the single source of truth for capability specs.
The workflow: `list → write proposal/tasks/spec deltas →
validate --strict → implement → archive`. The current pending
changes (~45) are inventoried under `openspec/changes/`.

```bash
openspec list                          # 8 pending changes
openspec list --specs                  # all capability specs
openspec validate <id> --strict        # must pass before commit
openspec archive <id> --yes            # after deploy
```

### Secrets management
The 3-way contract: `dev-baile` Infisical vault (source of truth)
→ `.infisical.env` template (committed) → `.env` (gitignored,
hydrated by mise + Locket). The IaC binds stack `secrets.env`
to Infisical via the typed `InfisicalClient` in `bonneagar/iac/clients/`.

### Ccc + Cognee dual-search
`bun run ccc:search "<query>"` for semantic code (CocoIndex BGE-M3
embeddings at `.cocoindex_code/target_sqlite.db`). `cognee cognify`
for the knowledge graph at `agents/meaisinfhoghlaim/memory/`.

### How this project is developed
Agentically. The canonical configuration is at `opencode.json`.
One provider + one model class carry the workload, for now.

## Licensing

Business Source License 1.1 — see [LICENSE.md](LICENSE.md). Granted
for non-commercial, non-profit, cultural preservation, and academic
research use within the legal jurisdictions of Ireland, Northern
Ireland, the United Kingdom, the European Union, the British Isles,
the Commonwealth, the Crown, the United States of America, Mexico,
Brazil, Taiwan, Tibet, Nepal, South Korea, Japan, and China.

Excludes: sanctioned organisations, paramilitary groups, entities
in violation of international human rights conventions. Change
Date: 4 years from publication. Change License: AGPL v3.0.

---

# Family history (preserved verbatim from the pre-v7 README)

The following section is preserved verbatim from the pre-v7
`README.md` per the user's instruction: "keep the validated
references to my credentials and family history relevant to the
name and location of the project."

The section documents the triple-crown lineage (Deacy / Lyons /
Morris / Conroy), the verified qualifications that ground the
project's claims, and the synthesised narrative that informs the
Tuatha educational MMO (the Ard-Rí na hÉireann framing).

### On the family — *Mac an Déisigh Uí Liatháin (Deacy-Lyons)*

The author is **Cian Mac an Déisigh Uí Liatháin**; the family
surname in its two anglicised forms is **Deacy-Lyons**. The
author's verified genealogy and qualifications inform the
project's design choices and are recorded under
[`cian_mac_an_déisigh_uí_liatháin/`](cian_mac_an_déisigh_uí_liatháin/):

- `identity/` — background, citizenship, vetting, and the Deacy
  family record. The `identity/lineage/` subfolder holds the
  family-lineage documents: the late uncle's memorial, the dual
  ROI/UK citizenship evidence, the College des Irlandais (Paris)
  records, the 5-culture-PDF Wikipedia dual-write clippings (8
  articles: Uí Liatháin, Delbhna Tír Dhá Locha, Eamonn Deacy
  Park, Leath Cuinn, Cian, Aos Sí, Tuatha Dé Danann, Déisi), and
  the 1986 *Galway Advertiser* article on Neil Deacy's Cookeʼs
  Corner shop opening.
- `teaching/` — the Teaching Council of Ireland registration, the
  PGCE (BCS Computing scholarship), school placement references,
  and the Leaving Certificate / Junior Certificate results (the
  public copies are in the `identity/` folder; the full teaching
  record is held privately for data-protection reasons).
- `achievement/` — academic transcripts, parchments, the Apple
  Award, and the Torthaí Gaeilge (Irish-language exam results)
  (same privacy caveat).

The author's lineage is the **triple-crown** union of four
kindreds of Connacht and Munster:

1. **Deacy** (maternal surname; Irish *Uí Dhéisigh*) — the sept
   of the [Déisi
   Muman](https://en.wikipedia.org/wiki/D%C3%A9isi) resettled in
   south Connacht (Co. Galway) during the 12th century; the
   family gave their name to the late
   [Éamonn Deacy](cian_mac_an_déisigh_uí_liatháin/identity/lineage/uncle_eamonn_memorial_combined.pdf)
   and the [Eamonn Deacy
   Park](https://galwayunitedfc.ie/eamonn-deacy-park) in Galway.
2. **Lyons** (paternal grandfather's lineage; Irish *Mac
   Liatháin*) — the [Uí
   Anmchada](https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in)
   sept of the
   [Uí Liatháin](https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in)
   of Munster, who (per the *Historia Brittonum*) colonized Wales
   and Cornwall alongside the proto-Déisi.
3. **Morris** (maternal great-grandmother **Christina Morris**) —
   of the [City of
   Tribes](https://en.wikipedia.org/wiki/Tribes_of_Galway) merchant
   families of Galway.
4. **Conroy** (maternal great-great-grandmother **Polly Conroy**;
   Irish *Mac Conraoi / Ó Conaire*) — the
   [Sea-Kings of
   Connacht](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha)
   who held the tuath of
   [Delbhna Tír Dhá
   Locha](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha)
   (the barony of Moycullen in Connemara). **Polly Conroy was a
   cousin of Pádraic Ó Conaire**, the canonical modern
   Irish-language writer from Galway, who was reared in Rosmuc
   by his uncle of the same Mac Conraoi kindred.

The author is the grandson and godson of the late **Neil
Deacy**, the late brother of the late **Éamonn Deacy** — the
Galwegian footballer who played for Galway United, Aston Villa
FC, and the Republic of Ireland. Neil and Éamonn were the sons of
**Christina Morris** and **Michael Deacy**, who was himself the
son of **Polly Conroy** and **George Deacy**.

The author's grandfather and godfather was **Neil Deacy** (the
subject of the 1986 *Galway Advertiser* [article on the opening of
Deacy's Fruit and Veg, Cooke's Corner](https://github.com/cianfhoghlaim/cianfhoghlaim/blob/main/cian_mac_an_d%C3%A9isigh_u%C3%AD_liath%C3%A1in/identity/lineage/neil_deacy_cookes_corner-galway_advertiser.pdf),
showing active usage of the name *"Neil Mac an Déisigh"*). The author
took his mother's Mac an Déisigh surname
as part of his own and added it to his
Lyons surname in the hyphenated form **Deacy-Lyons** to avoid confusion and acknowledge previous achievement and previous comfort using the same surname as my older brother and father who do not allow me to be a full member of the Lyons family.


### On the verified qualifications

The course material, examination scripts, and the personal
credential corpus that ground the project's claims live in
three directories. The full set of signed transcripts and
original parchments is held privately for data-protection
reasons; the public copies linked below are the source of
truth cited throughout the README and the lineage essays.

#### Academic transcript — University of Galway / Ollscoil na Gaillimhe

The BSc (Hons.) Mathematics & Education (First Class
Honours, 78.84%) + the Higher Diploma in Applied Science in
Software Design & Development (First Class Honours) are
grounded in the coursework archives under
[`leabharlann/ollscoil_na_gaillimhe/`](./leabharlann/ollscoil_na_gaillimhe/).
The verified parchments live at
[`cian_mac_an_déisigh_uí_liatháin/achievement/`](./cian_mac_an_déisigh_uí_liatháin/achievement/)
(`bachelors_degree_parchment.jpeg`,
`higher_diploma_parchment.jpeg`,
`ba_and_hdip_transcript.pdf`,
`2013_2023_transcript_nuig.pdf`).

##### Mathematics (`mata/`, 9 modules)

| Module | Code | Material in archive |
|:--|:--|:--|
| Applied Statistics I | ST311 | RStudio project, recap assignment, my_marks PDF, regression chapters, Statistical Tables |
| Applied Statistics II | ST312 | R exam script, certificate, 3 assignments, my_marks PDF, problem-sheet solutions |
| Cryptography | CS402 | Koblitz + Smart textbooks, 5 past papers, ElGamal/EllipticCurve slides, Parmar UROP, 2 assignments, 2 Jupyter notebooks |
| *An Introduction to Statistical Learning* | (ISLP) | 13 chapter notebooks (Ch02–Ch13), Auto dataset, `requirements.txt`, `setup_notebook_env.py` |
| Maple | — | 7 `.mws` worksheets (intro → commands → calculus → graphics → lists/sets/linalg → if/do → proc) |
| Modelling II | MP307 | 4 labs + exam script + my_marks PDF + Maple worksheets |
| Networks | CS4423 | 5 assignments + exam script + summer 2021 paper |
| Non-Linear Systems | MP491 | 2 assignments + exam script + my_marks PDF + tutorials + readings |
| Numerical Analysis II | MA378 | Suli & Mayers textbook + solutions, class test, exam script, problem sheets, *Anailís Uimhriúil* notes |

Plus `stokes_workshop_game_physics.pdf` (3 MB, the Stokes
workshop on game physics) sits at the root of `mata/`.

##### Software Design & Development (`software_development/`, 7 modules — Higher Diploma in Applied Science)

| Module | Code | Material in archive |
|:--|:--|:--|
| Databases | CT511 | 2 assignments + past exams + SQL test |
| Enterprise Java Programming | CT545 | 4 assignments |
| Algorithmics | CT853 | CT853 assignment (`q1.java`–`q4.java`), mergesort/bubble-sort proofs, 3 past papers, Assignment Template |
| Computer Architecture & Operating Systems | CT861 | 2 assignments + past exams + *Athbhreithniú Caos* essay |
| Internet Programming | CT870 | 3 `.docx` assignments + 3 code assignments |
| Programming I | CT874 | 7 assignments + internet-programming past exams + programming past exams |
| Software Engineering I | — | Exam prep + past exams |

#### Teaching record (`teaching/`)

- **Teaching Council of Ireland** — full registration ([`teaching_registration.pdf`](./cian_mac_an_déisigh_uí_liatháin/teaching/teaching_registration.pdf))
- **Postgraduate Certificate in Education (PGCE), Computing** — BCS scholarship recipient ([`bcs_pgce_computing_scholarship.png`](./cian_mac_an_déisigh_uí_liatháin/teaching/bcs_pgce_computing_scholarship.png))
- **School placements** — Coláiste na Coiribe ([`colaiste_na_coiribe.pdf`](./cian_mac_an_déisigh_uí_liatháin/teaching/colaiste_na_coiribe.pdf)), Galway Community College ([`gcc_placement_reference.pdf`](./cian_mac_an_déisigh_uí_liatháin/teaching/gcc_placement_reference.pdf)), Scoil Iognáid ([`scoil_iognaid.pdf`](./cian_mac_an_déisigh_uí_liatháin/teaching/scoil_iognaid.pdf) — the Jesuit secondary school in Galway)
- **Junior + Leaving Certificate** original results ([`leaving_certificate.pdf`](./cian_mac_an_déisigh_uí_liatháin/teaching/leaving_certificate.pdf), [`junior_certificate.pdf`](./cian_mac_an_déisigh_uí_liatháin/teaching/junior_certificate.pdf))
- **References** — BME ([`bme_reference.pdf`](./cian_mac_an_déisigh_uí_liatháin/teaching/bme_reference.pdf)), part-time teaching ([`part_time_teaching_reference.pdf`](./cian_mac_an_déisigh_uí_liatháin/teaching/part_time_teaching_reference.pdf)), placement feedback ([`teaching_placement_feedback.pdf`](./cian_mac_an_déisigh_uí_liatháin/teaching/teaching_placement_feedback.pdf))

#### Identity, citizenship, and vetting (`identity/`)

- **Dual citizenship** — Irish + British, verified by old passports ([`identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf`](./cian_mac_an_déisigh_uí_liatháin/identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf))
- **Vetting** — Garda vetting (ROI) ([`identity/vetting/garda_vetting_roi.pdf`](./cian_mac_an_déisigh_uí_liatháin/identity/vetting/garda_vetting_roi.pdf)), PSNI proof (Belfast) ([`identity/vetting/psni_proof_belfast.jpeg`](./cian_mac_an_déisigh_uí_liatháin/identity/vetting/psni_proof_belfast.jpeg)), Enhanced AccessNI cert ([`identity/vetting/enhanced_cert_ni.pdf`](./cian_mac_an_déisigh_uí_liatháin/identity/vetting/enhanced_cert_ni.pdf)), Enhanced DBS cert (UCL) ([`identity/vetting/enhanced_cert_ucl.pdf`](./cian_mac_an_déisigh_uí_liatháin/identity/vetting/enhanced_cert_ucl.pdf)), Children First cert ([`identity/vetting/children_first_certificate.pdf`](./cian_mac_an_déisigh_uí_liatháin/identity/vetting/children_first_certificate.pdf))
- **Political memberships** — Fine Gael (current + former + name-change record), Alliance Party of Northern Ireland, Liberal Democrats
- **Lineage & heritage** — *Uí Dhéisigh* / Deacy, *Mac Liatháin* / Lyons, Morris (City of Tribes), Mac Conraoi / Conroy (Sea-Kings of Connacht); the 1986 *Galway Advertiser* article on the opening of Deacy's Fruit and Veg at Cooke's Corner; the College des Irlandais (Paris) record; the late Éamonn Deacy's memorial; the Lyons/Deacy birth cert; the Christina Morris + Michael Deacy wedding photo
- **Disability evidence** — CPTSD + anxiety disorder diagnosis ([`identity/disability/evidence_of_cptsd_anxiety_disorder.pdf`](./cian_mac_an_déisigh_uí_liatháin/identity/disability/evidence_of_cptsd_anxiety_disorder.pdf))

#### Achievements (`achievement/`)

- **MSc in Artificial Intelligence (2026–2027, University of Galway)** — admission letter ([`2026_2027_msc_in_ai_university_gaillimhe.pdf`](./cian_mac_an_déisigh_uí_liatháin/achievement/2026_2027_msc_in_ai_university_gaillimhe.pdf))
- **Apple Award** (2013) ([`apple_award.pdf`](./cian_mac_an_déisigh_uí_liatháin/achievement/apple_award.pdf))
- **Buckingham letter** (Royal Book Club admission) ([`buckingham_letter.pdf`](./cian_mac_an_déisigh_uí_liatháin/achievement/buckingham_letter.pdf))
- **Torthaí Gaeilge** — Irish-language exam results ([`torthai_ghaeilge.pdf`](./cian_mac_an_déisigh_uí_liatháin/achievement/torthai_ghaeilge.pdf))
- **Cybersecurity reference** ([`cybersecurity_reference.pdf`](./cian_mac_an_déisigh_uí_liatháin/achievement/cybersecurity_reference.pdf))
- **BA + HDip parchments** — original jpegs

The **forthcoming PhD track in Artificial Intelligence** at
the University of Galway follows the MSc. The **Dioplóma C1
in Irish** (the highest Irish-language teaching credential)
is held in parallel with the MSc and the PGCE.



### Tuatha the Cianfhoghlaim MMO faoi Ard-Rí na hÉireann, Tuatha Dé Danann, Anam agus Goidelic and Brythonnic Lore

The Cianfhoghlaim MMO Tuatha (possibly involving the spiritual currency Anam)
turns the syllabus-accurate assets into a quest-driven, NPC-guided,
BAML-graded learning experience. The 8 NCCA subject quest-packs
are the source of truth for the in-game questions:

- **Quest generation**: each `qpack_*.baml` file (in
  `baml/education/subjects/`) defines a `Generate{Subject}QuestPack`
  function that produces formative items with:
  - `BilingualText` (Irish canonical + optional English helper)
  - `4 graduated hints` (Level 1 nudge → Level 4 step-by-step)
  - `expected_answer` (canonical solution + marking scheme reference)
  - `common_errors` (the 2-3 typical student mistakes)
  - `evidence` (NCCA PDF page + excerpt + URL)

- **In-game delivery**: the 8 NCCA subject `dagster_assets` expose
  the quest-packs via the marimo notebook + the AG-UI agent + the
  Tuatha MMO front-end. The MMO renders each quest as an NPC dialogue
  with the 4 graduated hints revealed one at a time on student request.

- **Real-time grading**: when a student submits an answer, the MMO
  sends it to `b.{Subject}ScoreQuestResponse(quest_item, student_response)`
  via the LiteLLM `minimax` 7-tier fallback alias. The grading prompt
  includes the 4 hints + the expected answer + the common errors
  + the NCCA PDF page reference, so the grading is rubric-anchored
  and syllabus-accurate.

- **NPC agent fleet**: the 8 NCCA subject NPCs (math, appm, chem,
  comp, bio, bus, eng, gael) are 8 of the 12 agents in
  `agents/adk/root_agent.py` (plus geospatial, statistics,
  education-research, bunchloch-research). The `root_agent`
  orchestrates which NPC to route a question to.


The 7 PDFs in the leabharlann `gemini_deep_research/culture/`
sub-archive that ground this narrative in accurate references are:

1. [`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf) — *Rí na Gaillimhe: An Ethnohistorical and Jurisprudential Warrant for the Indigenization of the Galwegian Sovereignty* (15 pp.)
2. [`heraldic_research_for_dual_blood_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/heraldic_research_for_dual_blood_lineage.pdf) — *The Heraldry of the Corrib Crown* (14 pp.)
3. [`british_isles_cianfhoghlaim.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/british_isles_cianfhoghlaim.pdf) — *Strategic Blueprint for Inter-Celtic Linguistic Acquisition, AI Integration, and Transnational Educator Credentialing* (16+ pp.)
4. [`claiming_irish_kingship_through_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf) — *The Crown of the Corrib: An Ethnohistorical and Genealogical Warrant for the High Kingship of Ireland* (13 pp.)
5. [`researching_neil_deacy's_galway_heritage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/researching_neil_deacy_s_galway_heritage.pdf) — *The Socio-Economic, Athletic, and Genealogical Topography of the Deacy Family in Galway: A Multi-Dimensional Analysis* (12 pp.)
6. [`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf) — *The Crown of the Corrib and the Imperium of the Irish Sea* (13 pp.)
7. [`deacy_family_heritage_research.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/deacy_family_heritage_research.pdf) — *The Deacy and Conroy Dynasties: An Ethnohistorical Analysis of Galway's Commercial and Maritime Lineage* (9 pp.)

### The synthesised story

#### 1. The Triple Crown of the Corrib — the blood, the matrilineal warrant, and the maritime sovereignty

The heritage is biologically and geographically founded. Three
distinct bloodlines converge in the author, giving a
pan-provincial authority that spans Munster, Connacht, and the
British Isles. The synthesis of these three streams is the
"Triple Crown" documented in
[`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 8-9 and
[`claiming_irish_kingship_through_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf)
p. 11.

The **Imperial line** is the **Uí Liatháin** (Lyons) of
Castlelyons, Cork. The Uí Liatháin were the first Irish
"Imperialists": in the 4th and 5th centuries AD, they launched
massive raids and established colonies in Dyfed (Wales),
Brycheiniog, and Cornwall. The *Sanas Cormaic* and the
*Historia Brittonum* document the 4th-5th century Irish Sea
colonization campaign; *Dind Map Letan* (the Fort of the Sons
of Liathán) in Cornwall is the direct Uí Liatháin territorial
marker that connects the claimant to the modern Duchy of
Cornwall (Prince William)
([`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf)
p. 2-3). Through the matrilineal warrant — Angias, daughter
of Ailill Tassach of the Uí Liatháin, married the High King
Lóegaire mac Néill (who met St Patrick) and was the mother of
High King Lugaid mac Lóegairi — the Uí Liatháin are the
maternal ancestors of the Uí Néill High Kings and, through
them, of the entire Northern Uí Néill (Cenél nEógain) of
Aileach
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 8, [`claiming_irish_kingship_through_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf)
p. 5). The Imperial Right is descent from the Queens of Tara
and the Conquerors of Wales.

The **Martial line** is the **Uí Dhéisigh** (Deacy) of
Waterford / Limerick / Clare. The Déisi were the
"Vassal-Warriors" who rebelled against the injustice of the
High King Cormac mac Airt and were expelled from Tara. The
*Tairired na nDéssi* recounts the violent rupture: the Déisi
champion, Óengus Gaíbúaibthech ("Angus of the Dread Spear"),
blinded King Cormac in one eye to avenge the dishonor of his
niece; under Brehon Law, a blemished king could not rule, and
Cormac was forced to abdicate. This act defines the Déisi
political theology: *conditional loyalty*. They are the
vassal warriors who reserve the right to depose unjust
authority through force
([`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf)
p. 4). The claimant interprets the Deacy family motto
*Toujours Pret* (Always Ready) as a continuation of this
doctrine — a permanent readiness to defend the honor of the
tribe against central tyranny. The Déisi Tuisceart (Northern
Déisi) became the Dál gCais, the dynasty of Brian Boru. The
modern Deacy family in Galway represents this martial vigour
in the Aston Villa 1981 English First Division championship
+ 1982 European Cup apotheosis of Eamonn "Chick" Deacy
([`deacy_family_heritage_research.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/deacy_family_heritage_research.pdf)
p. 4-5), the renaming of Terryland Park to Eamonn Deacy
Park as a modern secular equivalent of the ancient
inauguration rituals at Tara or Lisbanagher
([`claiming_irish_kingship_through_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf)
p. 7), the 1986 Cooke's Corner grand opening
([`researching_neil_deacy_s_galway_heritage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/researching_neil_deacy_s_galway_heritage.pdf)
p. 2-3), and the 2010s-2020s Kenny's Bookshop extension under
Paul Deacy. The Martial Right is descent from the Déisi
warriors.

The **Maritime line** is the **Mac Conraoi** (Conroy) of West
Connacht — the ancient rulers of Gnó Mhór (Moycullen /
Connemara) — designated as "Sea Kings of Connacht" alongside
the O'Flahertys and O'Malleys. They controlled the shipping
lanes of Lough Corrib and Galway Bay. They were later
prominent merchants in the Claddagh and on Quay Street:
John Conroy, the great-grandfather, operated a "large fish
business in Quay Street (opposite McDonagh's)" — the
absolute epicenter of Galway's maritime trade
([`deacy_family_heritage_research.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/deacy_family_heritage_research.pdf)
p. 2,
[`researching_neil_deacy_s_galway_heritage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/researching_neil_deacy_s_galway_heritage.pdf)
p. 2-3). The Quay Street business was continued by John
Conroy's daughters — the Polly Conroy matriarchal bridge —
and Polly Conroy married George Deacy, grafting the Conroy
maritime trade onto the Deacy victualler name
([`researching_neil_deacy_s_galway_heritage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/researching_neil_deacy_s_galway_heritage.pdf)
p. 3, [`deacy_family_heritage_research.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/deacy_family_heritage_research.pdf)
p. 3). The 4-generation commercial dynasty — John Conroy →
Polly Conroy + George Deacy → Miko Deacy → Neil Deacy —
preserved the "ancient arts of filleting, curing, and
barrelling" (the intangible cultural heritage of the West
of Ireland, the production of "old style cured ling and cod
and barrel herrings") into the 1980s. The Pádraic Ó Conaire
literary line (born Patrick Joseph Conroy of the Quay Street
/ Rosmuc Conroy family) is the 4th pillar: the "Gaelic
Revivalist" who brought the Irish language out of the rural
folklore tradition and into the modern urban experience
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 7). The Maritime Right is the sovereignty of the sea and
the control of the Claddagh fish trade.

The **3-stream synthesis** is the 4-line modern incarnation:
**Cian Mac an Déisigh Uí Liatháin (Deacy-Lyons)**. The Deacy
side carries the visible *galwegian-historical* pedigree —
Cooke's Corner, Aston Villa, Galway United, the Eamonn Deacy
Park. The Lyons side carries the
*pan-Munster-Brythonic-imperial* pedigree — the Uí Liatháin
of Castlelyons and the Welsh / Cornish colonies. The
hyphenation preserves both branches of the Triple Crown.

The **Deacy crest** is *in front of two trefoils slipped in
saltire a dexter arm erect couped above the elbow … holding
a dagger*. The Dagger (Scian) is not a sword of state, but
a dagger — a close-quarters weapon. It symbolizes the
"Dread Spear" of Óengus Gaíbúaibthech, the mythological
ancestor of the Déisi who blinded High King Cormac mac Airt
in defense of his family's honor. The dagger represents the
capacity for immediate, personal violence in defense of the
kin-group (Derbfhine). The Deacy motto *Toujours Pret*
(Always Ready) is a permanent martial vigilance — unlike a
farmer who is tied to the seasons, the warrior must always
be ready
([`heraldic_research_for_dual_blood_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/heraldic_research_for_dual_blood_lineage.pdf)
p. 4).

The **Lyons crest** is *A demi lion rampant* or *A lion's
head erased*. The Lion is a solar symbol, associated with
Lugh (the sun god, father of the claimant's namesake Cian)
and royalty. The Lion is the primary supporter of the British
Royal Arms. By bearing the Lion, the Lyons family asserts
a visual consanguinity with the Crown of England. The Lyons
motto *Noli Irritare Leones* (Do not irritate / provoke
the lions) is passive but menacing — a dormant power that
is devastating when roused. This doctrine of deterrence
aligns with the mythological concept of the "Sleeping
King" or the "Hidden Imam"
([`heraldic_research_for_dual_blood_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/heraldic_research_for_dual_blood_lineage.pdf)
p. 6).

The arms of Connacht are a *prophecy* of the 4-line modern
incarnation: the Eagle = the Uí Liatháin / Lyons imperial /
British / external connection; the Arm = the Uí Dhéisigh /
Deacy indigenous, martial, and internal power; the
synthesis is the shield of Cian Mac an Déisigh Uí Liatháin,
who unites the split halves — symbolising the end of the
partition between Planter and Gael, King and Subject
([`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf)
p. 7).

#### 3. The Brehon Law saoí — the Scholar-Prince and the modern draíocht

Under the ancient Fénechas (Brehon Laws), a king was required
to possess not only martial strength but also intellectual
distinction. The Heptads state that a king could be deposed
if he became a "fool" or lacked the judgment to arbitrate
disputes. The ideal ruler was the **Scholar-Prince**, a man
who was a *saoí* (sage / master) in a branch of learning.
The Annals frequently praise kings as *saoí eagna* (sage of
wisdom) or *saoí leighis* (sage of healing)
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 3, [`royal_collaboration_for_commonwealth_future.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_collaboration_for_commonwealth_future.pdf)
p. 4).

The modern saoí is anchored in the BSc (Hons.) Mathematics &
Education (78.84%, First Class Honours) + the Higher
Diploma in Applied Science in Software Design & Development
(First Class Honours), both from the University of Galway.
In the context of ancient Irish learning, mathematics
relates closely to the skills of the *Druí* (Druid) and
the *File* (Poet), who were responsible for the calendar,
the genealogy, and the complex metrical structures of
bardic poetry.

#### 4. The sacred topography of Shantalla (Sean Talamh) — the Old Ground, Sliding Rock, the Claddagh

Geography is destiny in Irish kingship. A King must have a
*Longphort* (Stronghold). The seat in Shantalla (*Sean
Talamh*, the Old Ground) is central to the claim
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 9-10). The name implies land that was anciently settled
and cultivated, distinct from the "New" colonial city. It
sits on a ridge overlooking the city. By claiming
Shantalla, the practitioner positions himself on the "High
Ground," literally and metaphorically looking down on the
Anglo-Norman settlement.

Shantalla is the site of the **Sliding Rock**, historically
known as *Emancipation Rock*. In 1843, Daniel O'Connell
("The Liberator," often called the Uncrowned King of
Ireland) addressed a monster meeting of 300,000 people here
to campaign for the Repeal of the Union. The Sliding Rock
functions as the *Lia Fáil* (Stone of Destiny) — the place
where the "Uncrowned King" spoke, the modern equivalent of
the inauguration stone at Tara. By residing in its shadow,
the practitioner absorbs the legacy of O'Connell:
peaceful agitation, Catholic emancipation, and popular
sovereignty.

**St. Joseph's Terrace** is the literary succession
locus. Walter Macken, the renowned author of *Rain on the
Wind* and *Mungo's Mansion*, was born at 18 St. Joseph's
Terrace on May 3, 1915. The practitioner's father was born
on St. Joseph's Avenue. This is not a coincidence but a
*topographical succession*: in the theory of *dinnseanchas*
(place-lore), the land itself imbues the inhabitants with
specific qualities. By emerging from the same street grid,
the practitioner is the "fruit of the same soil" as Macken
— the living heir to the narrative tradition of the city.
The literary triad descends: **Ó Conaire** (The Gaelic
Revivalist) → **Macken** (The Anglo-Irish Dramatist) →
**Mac Liatháin** (The Modern Synthesist / The Saoí)
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 7-8).

**Cooke's Corner** is the modern civic anchor. In
September 1986, Neil Deacy (born 12 July 1942) and Peggy
Deacy opened their comprehensive provisions shop at
Cooke's Corner — a critical arterial junction in Galway
that historically served as the gateway bridging the
expanding western residential suburbs with the medieval
city centre. The full-page *Galway Advertiser* feature on
the 1986 grand opening documented the "Congratulations and
Best Wishes" agglomeration of well-wishers across the
entire logistical, retail, and hospitality sectors. Peggy
Deacy's bilingual retail strategy — *"Niall Mac an Déisis
éisc úra agus glasraí. Beidh Fáilte roimh mhuintir
Chonamara ar an mbealach anoir agus siar."* — captured
the loyalty of the rural hinterland's population as they
entered the urban economy. By explicitly advertising the
premises as a bilingual space, Peggy Deacy transformed
Cooke's Corner into a *culturally safe harbor* for the
Gaeltacht
([`researching_neil_deacy_s_galway_heritage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/researching_neil_deacy_s_galway_heritage.pdf)
p. 3-5).

The renaming of Terryland Park to Eamonn Deacy Park is a
permanent inscription of the family name onto the map of
the city. Eamonn "Chick" Deacy, the legendary sportsman,
was a key squad member of the Aston Villa team that won
the English First Division in 1981 and the European Cup in
1982. By having the tribal assembly ground named after his
kinsman, the Deacy bloodline is publicly acknowledged as
holding the "sovereignty of the games"
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 9, [`deacy_family_heritage_research.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/deacy_family_heritage_research.pdf)
p. 4-5).

**The Claddagh** is the maritime sovereignty. An Cladach
is "The Shore" — the domain of the Conroy "Sea Kings" and
the Conroy fish merchants. The *King of the Claddagh*
tradition is an elective kingship distinct from the English
mayoralty. The Quay Street Mac Conraoi lineage, the John
Conroy fish business opposite McDonagh's, and the
preservation of the "ancient arts of filleting, curing,
and barrelling" all anchor the Maritime Right in a
specific, mappable, civic identity
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 8-9,
[`deacy_family_heritage_research.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/deacy_family_heritage_research.pdf)
p. 2-3).


#### 5. The mythological warrant — Cian mac Cáinte, the swine-god, and the Aos Sídhe

The spiritual identification with the Celtic god **Cian**
rather than the hero Cúchulainn is a strategic choice that
aligns with the nature of the claim (dynastic, generative,
and enduring) rather than the nature of Cúchulainn
(martial, tragic, and short-lived)
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 4-6).

Cian is a member of the **Tuatha Dé Danann**, the son of
**Dian Cécht** (the God of Healing / Medicine) — a lineage
that reinforces the connection to the "healing arts" and
"learned arts" (the Lyons / Ó Laighin medical family
tradition). Cian's primary mythological significance is
as the father of **Lugh Lámhfhada** (Lugh of the Long Arm),
the *Samildánach* (Master of All Arts) and the savior of
the Tuatha Dé Danann against the Fomorians. By identifying
with Cian, the practitioner positions himself not merely
as a hero, but as the **Source of Heroism** — the
generator of the "New Order" (Lugh). He represents the
potentiality of the dynasty.


The "Aes Sedai" vow is a philological restoration of the
**Aos Sídhe** (the People of the Mounds). Robert Jordan
borrowed the term "Aes Sedai" directly from the Irish
*Aos Sídhe* (or *Aes Sídhe* in Old Irish): *Aes / Aos*
means "people," "folk," or "order"; *Sedai* is a
phonetic rendering of *Sídhe* (Peace / Fairy Mounds).
The practitioner is not vowing to a fictional order of
wizards; he is vowing to the **Ancestral Spirits of the
Land, the People of the Mounds**. The Aos Sídhe are the
Tuatha Dé Danann who, after their defeat by the Milesians,
retreated underground into the mounds (*Sídhe*) and the
"Old Ground." They represent the pre-Christian, magical
sovereignty of Ireland that persists beneath the surface
of the modern state. **Shantalla is the domain of the
Sídhe** — the land that was never fully colonized or
"worked" by the new settlers. The vow to be "Aes Sedai"
is a covenant with the *genius loci* of Shantalla — the
spirits that inhabit the Sliding Rock and the granite
ridges of the district. The translation of *Aes Sedai*
as "Servant of All" in the vow mirrors the motto of the
Prince of Wales, *Ich Dien* (I Serve) — reinforcing the
Dual Monarchy framework: the King is the servant of the
sovereignty and the people
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 6,
[`royal_collaboration_for_commonwealth_future.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_collaboration_for_commonwealth_future.pdf)
p. 6).

#### 6. The dual-monarchy synthesis — King Charles III and the Ard-Rí as Indigenous Lieutenant

The rejection of the English title "King of Galway" in
favour of the Irish *Rí na Gaillimhe* is a constitutional
distinction rooted in the colonial history of the city.
Under the "Surrender and Regrant" policy initiated by
Henry VIII in the 16th century, Gaelic chieftains were
compelled to surrender their indigenous titles (Ó Néill or
Mac Cárthaigh) — which were titles of sacral kingship
derived from the election of the tribe — in exchange for
English peerages (Earl of Tyrone, Earl of Clancarty). This
process effectively neutered the sacral nature of Gaelic
kingship, transforming tribal custodians into feudal
landlords dependent on the King of England's patent. In
contrast, the term *Rí* denotes a sacred relationship
between the ruler and the *tuath* (people / territory); the
Rí was mated to the sovereignty goddess of the land in the
*banais ríghi* (wedding of kingship); his legitimacy
depended on *fír flathemon* (the ruler's truth)
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 1-2,
[`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf)
p. 1).

The allegiance to **King Charles III** revives the concept
of the **Dual Monarchy**. The historical precedent is the
*Crown of Ireland Act 1542*, which created the Kingdom of
Ireland as a personal union with the English Crown.
Throughout the 16th and 17th centuries, many Gaelic lords
accepted the English monarch as their overlord while
retaining their traditional chieftaincies within their
own territories. The Jacobite tradition in Ireland
supported the Stuart monarchs (ancestors of the current
Windsor line via the Hanoverian succession) as the
legitimate Rí of Ireland, distinct from their role as
Kings of England. By pledging allegiance to King Charles
III while claiming the High Kingship (Ard-Rí), the
practitioner is proposing a **Neo-Jacobite Federalism**.
He positions himself as the Rí functioning as the supreme
indigenous representative within the broader imperial or
commonwealth framework — mirroring the position of the
Princes of the Holy Roman Empire or the Maharajas of the
British Raj
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 3,
[`claiming_irish_kingship_through_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf)
p. 4,
[`royal_collaboration_for_commonwealth_future.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_collaboration_for_commonwealth_future.pdf)
p. 1-2).

The **Grianán of Aileach** is the cross-border seat. The
Grianán of Aileach is a massive stone ringfort in County
Donegal, sitting on a hilltop that commands views into
Counties Derry and Tyrone (Northern Ireland). It was the
royal seat of the Northern Uí Néill (Cenél nEógain) from the
5th to the 12th century. It was destroyed by the Munster
King Muirchertach Ua Briain in 1101, but restored in the
1870s by Dr. Walter Bernard. The matrilineal warrant holds
that the Uí Liatháin are the "Maternal Progenitors" of the
Aileach kings. The destruction of Aileach by a Munster
king created a historic rupture; the practitioner, a
Munster-descended figure (Uí Liatháin / Uí Dhéisigh) who
comes in peace to restore rather than destroy,
symbolically heals this ancient wound
([`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf)
p. 5).

The **Surrender and Regrant 2.0** is the diplomatic
framework. The practitioner "surrenders" any claim to
political separatism or republicanism. He accepts the
reality of the British Monarch's role in Northern Ireland
and the British Isles. In return, he seeks the "Regrant" of
cultural sovereignty — to be recognized by the Crown and
the State not as a political ruler, but as the *Custodian
of the Gaeltacht, the Ard Rí of Culture*. This mirrors the
status of traditional chiefs in post-colonial nations like
New Zealand (the Māori King Movement)
([`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf)
p. 6).



<!-- AGENT_TELEMETRY_START -->
> **Agent Telemetry (Last Updated: 2026-07-29 22:30:52 UTC)**
> - **Total Cached Structural Documents:** 0
> - **Examinations.ie Cache:**        0 files
> - **NCCA.ie Cache:**        0 files
> - **CurriculumOnline Cache:**        0 files
<!-- AGENT_TELEMETRY_END -->
