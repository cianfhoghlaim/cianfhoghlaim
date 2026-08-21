# Chop-and-Change Guide for the cianfhoghlaim Monorepo

> **Companion to the [README addendum](../README.md#addendum--a-note-for-anyone-looking-at-this-project-right-now).**
> Read this if you want to fork, retarget, or rewire any single slice
> of the monorepo for your own use case. The TL;DR per area is here;
> the full deep-cuts (the 9 subagent reports that informed this guide)
> are appended below in collapsible blocks.
>
> **Last-verified-against**: `2026-07-26` — the date the 9 read-only
> deep-cuts subagents ran. The cianfhoghlaim monorepo is **mid-rollout
> of BIEP v3** (24 active openspec changes, see §10). Regenerate this
> guide on or after **2026-08-30** to refresh the per-area pointers.

---

## 0. Quick orientation

### 0.0 Repo shape (post-v7 flattening, 2026-07-17)

- **Single repo** — the `bonneagar/` IaC is now a subdirectory (no
  longer a separate GitHub repo). The Python package IS the repo root
  (no more `cianfhoghlaim/` nesting).
- **`leabharlann/`** is the **only** remaining separately-managed repo
  (3.4 GB corpus). Per `AGENTS.md` "Hard rule", you **must not write**
  into it from this worktree — treat it as read-only source material.
- The build orchestration is `mise.toml` at root + `bun run turbo dev`
  for the TypeScript graph + `uv sync` for the Python graph.
- The 88 Docker Compose stacks + 12-agent fleet + 4 BIEP MotherDuck
  Dives + 30 Dives total + 21 Flights are all live, **but** the BIEP
  v3 batch is in active deployment — see §9-§10 below.

### 0.1 The four cheap coding agents

This is the **only recommended tooling stack** for chop-and-change work.
The numbers are in the order you should reach for them.

| Tool | Cost | Best for | Weak at | Recommendation |
|:--|:--|:--|:--|:--|
| **Gemini Deep Research Pro** | €20/mo | First-hour research: finding authoritative ministry / exam-board / medical-register endpoints and licensing constraints | Multi-file repo refactors | Use for the first hour, then put it down |
| **MiniMax coding plan** | $10-30/mo | Repetitive file-local Python refactors; multi-hour context for IaC rewrites; BAML schema edits | Web research; autonomous browsing | Use for IaC + BAML work |
| **OpenCode Go** (local CLI) | €0/mo | Multi-file repo edits with the in-stack `ccc` skill + the `agent-fleet-orchestration` skill; already integrated via `mise` hooks | Pure research; needs skill ramp-up | Use as your default — already wired |
| **GitHub Copilot** | €10/mo | Single-file edits, IDE-anchored completion, no-SQL FIM | Cross-cutting refactors; weak sandboxing | Single-file copilot only |

**Pair them**: Gemini Deep Research for the first hour → OpenCode Go or MiniMax for the next two days → GitHub Copilot as a single-file copilot.

### 0.2 The "first-hour clone" — the cleanest entry point

If you want a sub-1-hour "does the chop-and-change work?" sanity test,
clone the **Celtic morphology agent**:

- File: `agents/meaisinfhoghlaim/educational/celtic_morphology_agent.py`
- 210 LoC, 4 trivial tool wrappers (`extract_morphology`,
  `extract_verb_conjugation`, `extract_noun_declension`,
  `compare_adjective`), no manifest, no Convex dependency, no BAML
  compound types.
- If your domain is "morphology of X" (legal contract clauses, music
  chord progressions, recipe steps), the structure maps 1:1 — rename
  the 4 tool functions + the BAML imports, set `LITELLM_BASE_URL`,
  and you're running in ~30 minutes.

### 0.3 Named-hazard names — the post-v7 ground truth

If you read any older documentation / openspec / blog post that uses
any of these, **it is stale**:

| Stale name | Current (post-v7) name | Where | Fixed in |
|:--|:--|:--|:--|
| `dlt/` (sub-package) | `dlt_sources/` | `dlt_sources/` | `2026-07-19-2026-07-14-fix-foundation-v7-flattening-and-baml-drift-v1` |
| `bge-large-en-v1.5` | `BAAI/bge-m3` (1024-d, multilingual) | `cocoindex_flows/_shared/_lifespan.py:107` | `2026-08-06-biep-v3-critical-path-fixes-v1` |
| `md:oideachais` | `md:cianfhoghlaim` | `notebooks/_shared/db.py:26` | `2026-08-06-biep-v3-critical-path-fixes-v1` |
| `oideachais.*` (BAML namespace) | `cianfhoghlaim.*` | `baml_src/baml.toml`, every `.baml` file | `2026-07-26-biep-v3-root-namespace-rename-v1` (active) |
| `cianchoghlaim` (typo) | `cianfhoghlaim` | 3,633 occurrences across 228 files (Docker network, container name prefix, DuckLake schema, S3 bucket, docstrings, prompts) | `2026-07-19-fix-cianchoghlaim-typo-v1` |

---

## 1. `bonneagar/` — Infrastructure mesh

### 1.1 TL;DR

**What this is.** `bonneagar/` (Irish for "infrastructure") is the
self-hosted IaC mesh: **88 Docker Compose stacks** under
`bonneagar/stacks/` following a 6-file `GOLD_STANDARD` pattern
(`compose.yaml + pangolin.yaml + sidecar.yaml + secrets.env +
blueprint.yaml + .env.example`); a **TypeScript IaC at `bonneagar/iac/`**
with 25 commands orchestrating **Komodo** (Docker orchestration, ~109
`.toml` stack/procedure/resource-sync definitions),
**Pangolin** (Fosrl identity-aware reverse proxy + WireGuard via
Gerbil + Traefik + Pocket ID SSO + TinyAuth forward-auth + CrowdSec
IDS), **Infisical** (self-hosted secrets vault, source of truth for
the `dev-baile` environment); plus a **Locket** sidecar pattern that
resolves `infisical://dev-baile/...` URI refs into runtime env. Hosted
on a 2-host topology: `arm1-oci` (Oracle Cloud London free-tier ARM,
4 OCPUs + 24 GB) + `bunchloch` (MacBook M4 Max, 48 GB).

**OSS value (5 named open-source packages):**

- **Komodo + Pangolin + Newt + Gerbil + Traefik + Pocket ID** — a
  complete multi-host container mesh with zero-trust SSO tunnels,
  identity-aware reverse proxy, forward-auth, and CrowdSec IDS, with
  no Kubernetes, no Istio, no cert-manager, no external Vault.
- **Infisical + Locket + mise hooks 3-way contract** — Locket sidecar
  injects `infisical://dev-baile/<svc>/<key>` references at container
  boot; mise directory hooks re-hydrate `.env` (chmod 600) on `cd`;
  audited by `bun run stack-doctor`.
- **IaC-as-TypeScript** that replaces 8 bash + 5 v0 JS files —
  `iac/` (CLI + 25 commands + 4 source discoverers + 3 typed
  clients: `KomodoClient` / `PangolinClient` / `InfisicalClient`) drives
  plan/deploy/teardown/health/sync:secrets/sync:resources against
  live Komodo + Pangolin + Infisical REST APIs in a single
  `bun run iac:bootstrap` state machine.
- **Curated 5-group, 30-key-stack deployment manifest** —
  `iac/sources/key-stacks.ts` enforces an infra / data-engineering /
  agent-platform / language-model / user-facing-web model.
- **Reference data-plane stack: Lakehouse** (`bonneagar/stacks/lakehouse/`)
  — Garage v2.3.0 S3 + Postgres + Lakekeeper (Iceberg REST) + Lance
  namespace, all wired via the 6-file pattern.

**Chop-and-change steps (5):**

1. **Copy the gold-standard exemplars verbatim, delete everything
   else.** Keep `garage/`, `litellm/`, `pangolin/`, `lakehouse/` (the
   4 reference impls per `GOLD_STANDARD.md §Exemplars`); delete
   `oideachais/`, `croilar/`, `tuatha/`, `meaisinfhoghlaim/`,
   `openclaw/`, `openchamber/`, `hermes/` (personal fleet);
   `motherduck/` (SaaS stub); `olm-arm1-oci/`; `wave2/`; the 5
   `unstract` sidecar placeholders; `legacy/`.
2. **Replace the domain + two hostnames in one `sed` pass** —
   `cianfhoghlaim.ie` (in ~50 files), `arm1-oci` (in `servers.toml` +
   ~109 stack TOMLs), `bunchloch` (workload host). Run
   `rg 'cianfhoghlaim\.ie|arm1-oci|bunchloch' -l` first.
3. **Swap the 9 hard-coded env vars in `setup-iac-env.sh` + `.env`** —
   `DOMAIN`, `CF_DNS_API_TOKEN`, `PANGOLIN_API_KEY`,
   `POCKETID_*_CLIENT_ID/SECRET` (3 pairs), `CROWDSEC_BOUNCER_KEY`,
   `PANGOLIN_LICENCE` (Enterprise — remove if going FOSS-only),
   `INFISICAL_UNIVERSAL_AUTH_*` + `INFISICAL_PROJECT_ID`.
4. **Swap any one of the 6 backends** — Komodo → Coolify/Portainer/Dokku;
   Pangolin → Cloudflare Tunnel + Cloudflare Access (note the
   Enterprise licence); Pocket ID → Authelia/Authentik/Keycloak;
   Infisical → Doppler/Vault; Traefik → Caddy/Nginx Proxy Manager;
   Garage → MinIO.
5. **Replace `iac/pulumi/oci/`** with whatever cloud you actually use
   (`iac/pulumi/oci/Pulumi.prod.yaml:5` hard-codes `arm1-oci`).
   Delete `iac/pulumi/oci/` + `iac/pulumi/hetzner/` and write a new
   `iac/pulumi/<your-cloud>/index.ts`.

**Hardest escape hatch.** The coupled assumptions of "Pangolin +
Pocket ID + Infisical + CrowdSec run on a $0/month Oracle Cloud ARM
box at `arm1-oci`" AND "all 88 services expose at `*.cianfhoghlaim.ie`
via Cloudflare DNS-01 wildcard cert" together make the entire mesh
free to operate. Replacing just one costs the cheap-fork promise
(a $5-20/mo VPS replaces the $0 OCI ARM; a different wildcard DNS
provider replaces Cloudflare). Replacing both blows the "no ongoing
infra cost" thesis.

**Best cheap coding agent.** **MiniMax coding plan**. The job needs
~50+ coordinated file renames + env swaps + stack deletes; only a
long-context coding agent can hold the whole IaC + Locket sidecar
pattern + 6-file `GOLD_STANDARD.md` in one prompt. MiniMax-M3 was the
model that built this monorepo (it's the agent fleet's LLM backbone)
so it knows the Pangolin Enterprise + Komodo + Infisical mesh
topology natively.

### 1.2 Full deep-cuts report

<details>
<summary><b>Click to expand the full `bonneagar/` deep-cuts report (verified against the source)</b></summary>

**Reality check.** The IaC mesh is mature: 88 stacks, 109 Komodo
TOML files, 25 IaC commands, 3 typed REST clients, 6-file GOLD
STANDARD pattern. The 4-stack exemplar set (garage + litellm +
pangolin + lakehouse) is the canonical 1-day "what does a working
stack look like?" reference.

**Key file paths to study first** (in order):

1. `bonneagar/iac/README.md` — 15 CLI commands + the 4 blockers the
   IaC fixes
2. `bonneagar/GOLD_STANDARD.md` — the 6-file template
3. `bonneagar/DEPLOYMENT-STRATEGY.md` §1 (2-host topology) and §3
   (6-step golden path)
4. `bonneagar/SECRETS-MANAGEMENT.md` — Infisical + mise hooks
   architecture
5. `bonneagar/PANGOLIN-SETUP.md` §Manual Steps 1-4
6. `bonneagar/QUADRANT-TO-STACK-MAP.md` §1-5 — 1-page stack → port
   → domain → Dagster code-location map
7. `bonneagar/stacks/INDEX.md` — the canonical 88-stack inventory
8. `bonneagar/iac/sources/key-stacks.ts` — the curated 30-stack
   5-group model
9. `bonneagar/iac/pulumi/oci/Pulumi.prod.yaml` — the `arm1-oci`
   Oracle Cloud ARM London free-tier hook

**Identified drift / bugs**:

- `HEALTH_REPORT.md` flags 105 CRITICAL findings — a known drift
  baseline.
- The Pangolin Enterprise licence `PER-D09BF259-...` in
  `stacks/control-plane/secrets.env:41` is single-tenant; remove if
  going FOSS-only.
- The 5 unstract sidecar placeholders (`backend/`, `platform-service/`,
  `runner/`, `workers/`, `x2text-service/`) are placeholder Docker
  Compose stubs awaiting real Unstract deploys.

</details>

---

## 2. `agents/` — the agent fleet umbrella

### 2.1 TL;DR

**What this is.** The `agents/` package bundles four cooperating
agent frameworks + a shared tool library + an HTTP/AG-UI transport
layer + a Celtic-education-themed orchestration system. Canonical home
for **Google ADK** (`agents/adk/`, deprecated but still the largest
single surface — 17+ specialist modules + 8 NCCA subject agents),
**Agno** (`agents/agno/`, the active primary — 6-agent `education_team`
+ 5 stage teams for Aistear/Primary/Junior Cycle/Senior Cycle/Tertiary),
the **9th repo-operator agent** (`agents/tuatha/agents/cianfhoghlaim_operator.py`),
the **3 latest specialist agents** (`agents/meaisinfhoghlaim/educational/`
— academic_history, celtic_grammar, celtic_morphology, added 2026-07),
the **shared tool library** (`agents/tools/` — 9 modules: corpus,
curriculum, geospatial, statistics, terminology, translation), the
**HTTP/AgentOS FastAPI layer** (`agents/api/`). All agent calls route
through a single **LiteLLM gateway** (`http://litellm:4000`) and emit
traces to Langfuse + Logfire + MLflow + Datadog LLMObs, with memory
split between **Letta Cloud** (long-term conversational) and **Cognee
/ Graphiti / LanceDB** (knowledge + vector).

**OSS value (5 named open-source packages):**

- **Google ADK v2.1+** (`google.adk.agents.LlmAgent`, `SequentialAgent`,
  `BuiltInPlanner`) — marked *deprecated* in `agents/__init__.py:6`
  but still the most heavily-used framework in this layer.
- **Agno v2.0+** (`agno.Team`, `agno.agent.Agent`, `agno.os.AgentOS`,
  `agno.db.sqlite.SqliteDb`) — marked *active primary* in
  `agents/__init__.py:15`. The `team.Team(members=[...],
  share_member_interactions=True, db=SqliteDb(...))` pattern is the
  canonical "context-sharing between agents" composition.
- **Pydantic AI + Pydantic Logfire** (`pydantic_ai.Agent`,
  `pydantic_ai.ag_ui.StateDeps`) — the gateway layer
  (`agents/pydantic_gateway.py`) + HITL surface
  (`agents/hitl_agent.py`) + cost-limit + multi-provider fallback.
- **LiteLLM** (`http://litellm:4000` with `LITELLM_MASTER_KEY=sk-1234`)
  — the single canonical LLM gateway for every agent in the package.
- **Letta Cloud** (`letta_client.Letta`,
  `client.agents.archival_memory.insert/search/list`) — the
  `ProjectArchitect` agent that holds archival memory of every
  `AGENTS.md` / `CLAUDE.md` / skill file in the repo.

Plus the deeper stack: **BAML** (extraction), **AG-UI / CopilotKit**
(SSE streaming), **NLLB-200 / Opus-MT / M2M-100** (Celtic translation),
**InvokeAI** (image gen at `INVOKEAI_URL=http://localhost:9090`).

**Chop-and-change steps (5):**

1. **Start at `agents/agno/education_team.py`** (520 lines). This is
   the smallest *complete* loop in the package: 6 specialists
   (curriculum, research, translation, corpus, geospatial, statistics)
   wired into one `agno.team.Team` with `share_member_interactions=True`.
2. **Adopt Agno over ADK.** `agents/__init__.py:62-82` flags ADK as
   deprecated. For a fork, copy `agents/agno/` + `agents/agno/stage_teams/`
   and ignore `agents/adk/` (the 848-line `root_agent.py:1` is a
   maintenance trap).
3. **Swap LLM routing via two env vars + one config line.** Edit
   `LITELLM_BASE_URL` (`agents/baml_integration.py:51`), then change
   `gateway_config.default_model` (`agents/pydantic_gateway.py:78`).
   Or bypass LiteLLM entirely: replace `from agno.models.openai import
   OpenAIChat` with `from agno.models.anthropic import Claude`
   (already lazy-loaded).
4. **Add a new specialist agent in 4 lines.** Open
   `agents/routing_keywords.py:32` (the 102-line canonical
   `ROUTING_KEYWORDS: dict[str, list[str]]`) and add a new bucket —
   e.g. `"legal_agent": ["contract", "tort", "case-law"]`. Then
   implement the specialist in `agents/agno/stage_teams/_shared/`
   or in `agents/adk/<name>_agent.py` following the 8 NCCA subject
   specialists at `agents/tuatha/agents/{gael,math,appm,chem,comp,engl,geog,hist}_agent.py`
   as templates.
5. **Wire a new channel by following the AG-UI FastAPI pattern** at
   `agents/api/_oideachais_api/main.py:1-80`. The Telegram / Slack /
   Discord / WhatsApp / Teams channel-fanout gateway is **not** in
   `agents/` — you must add it as a new `agents/api/_<channel>_fanout/`
   package.

**Hardest escape hatch.** The **13-bucket routing map** in
`agents/routing_keywords.py:32-99` hard-codes the entire fleet around
Irish / Welsh / Scottish Gaelic / Manx / Cornish / Breton vocabulary
and the NCCA / CfE / CfW / CCEA / SQA curriculum frameworks. Three
structural dependencies make this an *escape hatch* rather than a
*config toggle*: (1) the BAML extraction contract in
`agents/baml_integration.py:72-78` takes `(subject, cycle, language)`
as first-class parameters; (2) the 8 NCCA subject specialists each
carry their own BAML prefix + CocoIndex flow; (3) the Agno stage
teams at `agents/agno/stage_teams/__init__.py:54-121` are keyed on
**5 Irish educational stages**. Replacing the LiteLLM model map or
the Letta memory backend is one-line; replacing the Celtic-education
assumption is roughly a 40% rewrite of `agents/`.

**Best cheap coding agent.** **OpenCode Go** (free, OSS, already
wired to the in-stack skill surface). MiniMax coding plan is the
close runner-up if you need the long-context variant.

### 2.2 Full deep-cuts report

<details>
<summary><b>Click to expand the full `agents/` deep-cuts report</b></summary>

[Full deep-cuts verbatim from the broad `agents/` subagent — covers
the polyglot agent runtime layer, the 4 cooperating frameworks, the
shared tool library, the HTTP/AG-UI transport layer, and the Celtic-
education-themed orchestration system. Includes file-path references
for `agents/agno/education_team.py`, `agents/baml_integration.py`,
`agents/pydantic_gateway.py`, `agents/routing_keywords.py`, and the
13-bucket routing map.]

</details>

---

## 3. `agents/meaisinfhoghlaim/` — the educational Celtic agents

### 3.1 TL;DR

**What this is.** A thin Python subpackage containing **three
BAML-calling educational agents** (`academic_history_agent.py`,
`celtic_grammar_agent.py`, `celtic_morphology_agent.py`) and one
Pydantic-v2 manifest loader (`academic_history_manifest.py`). Every
agent is a deliberately import-safe consumer of BAML extraction
functions (`b.ExtractAcademicHistorySnapshot`, `b.ExtractCelticGrammar`,
`b.ExtractCelticMorphology`) with graceful `try/except` fallbacks.
The subdirectory is 4 files / 1,090 LoC total — the wider "12-agent
meaisínfhoghlaim fleet" framing is distributed across `agents/agno/`,
`agents/adk/`, `agents/tuatha/`, NOT here. This subdirectory is the
**13th bucket** (T5, added 2026-07-11 by
`2026-07-11-uog-math-statistics-academic-history-v1`) plus the
Celtic-language pair added 2026-07-17 by
`2026-07-17-gaois-celtic-language-pipeline-v1`.

**OSS value (4 named open-source packages):**

- **BAML extraction functions as typed LLM tool sources** — wrap
  `b.ExtractCelticMorphology(...)` and return Pydantic-style `specs`
  lists with graceful `{"error": "BAML not available"}` fallbacks
  (`celtic_morphology_agent.py:99-101`). Consumer-side contract:
  **never let BAML availability crash the agent**.
- **`SubjectAgentWiring` frozen dataclass pattern** — local fallback
  stub of the canonical `SubjectAgentWiring` from
  `agents/tuatha/wiring.py:56-80` (8 fields). The fallback is the
  valuable idea: the agent works whether or not the wiring library
  is installed. LBYL + graceful degradation pattern.
- **Pydantic v2 + YAML manifest for portable, privacy-gated
  bring-your-own data** — `AcademicHistoryManifest` (Pydantic v2),
  `ModuleRoot`, `ArtifactRoots`, `Privacy` (with `pseudonym_salt_env`
  + opt-in `include_identity_records`), `PrivacyOverrides.skip_patterns`,
  `StudentProfile`. The `pseudonym_hash()` method does
  `hashlib.sha256(f"{pseudonym}:{salt}").hexdigest()[:32]` — no PII
  ever leaves the user's machine.
- **Per-language LiteLLM routing via shared helper** — both agents
  call `route_language("celtic_curriculum", language)` which routes
  `IRISH → uccix-mistral-24b` (UCCIX) and
  `WELSH/SCOTTISH_GAELIC/BRETON/MANX/CORNISH → gemma-4-26B-A4B`.

**Chop-and-change steps (5):**

1. **Pick the right starting agent** — `celtic_morphology_agent.py`
   is the cleanest fork target: 210 LoC, 4 trivial tool wrappers,
   no manifest, no Convex dependency. **Skip `academic_history_agent.py`
   first** — 10 tools, Convex schema dependency, `MemoryBackend`
   Protocol that doesn't yet exist in `meaisinfhoghlaim/` — that's a
   week of work.
2. **Adopt the Agno framework first (not ADK)** —
   `agents/__init__.py:62-82` flags ADK as deprecated. Use
   `agents/agno/education_team.py:317-375` as the canonical pattern:
   `agno.team.Team(members=[...], db=team_storage,
   share_member_interactions=True)`.
3. **Swap the LiteLLM model map in 3 places, not 30** — set
   `AGNO_DEFAULT_MODEL=openai/gpt-4o-mini` or your gateway alias,
   `LITELLM_BASE_URL` to your gateway, and update `baml/clients.baml`
   to point at your LiteLLM proxy.
4. **Retarget OpenClaw channels** — there is no OpenClaw in this
   subdirectory. The actual channel layer lives at `web/apps/openclaw/`.
   For an outsider: **skip OpenClaw entirely** and substitute your
   own channel (Slack bot, Discord webhook, plain REST endpoint, or
   a CopilotKit `<CopilotKit runtime>` mount).
5. **Which agent to clone first** — `celtic_morphology_agent.py`,
   hands-down. 210 LoC, 4 verbs × 6 languages = 24 combinations, all
   with a single-line graceful fallback.

**Hardest escape hatch.** The BAML `ExtractCelticGrammar` /
`ExtractCelticMorphology` / `ExtractAcademicHistorySnapshot` schema
dependency. Every tool requires a `baml_client` Python wheel compiled
from `baml_src/celtic/grammar_patterns.baml` / `baml_src/celtic/morphology.baml` /
`baml_src/academic_history.baml`. Those BAML sources reference Irish
linguistic categories (`mutation`, `copula`, `verbal noun`, `initial
consonant mutation`) that are baked into the prompt templates and the
typed outputs. The second-hardest: the per-language LLM routing
(`IRISH → uccix-mistral-24b`, others → `gemma-4-26B-A4B`) — both
domain-specialised open-weight models that don't port for free to
Spanish or Vietnamese.

**Best cheap coding agent.** **OpenCode Go**. The chop-and-change is
a multi-file Python refactor with hidden imports, BAML clients,
Pydantic v2 models, and graceful-degradation fallbacks. OpenCode Go
has direct filesystem access + can read `agent-fleet-orchestration`
skill + can run `mise run ccc:search "SubjectAgentWiring"` + can write
new files in a sandboxed git branch.

### 3.2 Full deep-cuts report

<details>
<summary><b>Click to expand the full `agents/meaisinfhoghlaim/` deep-cuts report</b></summary>

[Full deep-cuts verbatim — covers the 4-file reality of this
subdirectory, the 13th-bucket routing position, the import-safe
`try/except` fallback pattern, the `AcademicHistoryManifest`
privacy gate, and the per-language `route_language()` routing
helper. Includes the `celtic_morphology_agent.py` `extract_morphology`,
`extract_verb_conjugation`, `extract_noun_declension`,
`compare_adjective` 4-tool template.]

</details>

---

## 4. `dlt_sources/` — the DLT ingestion pipeline

### 4.1 TL;DR

**What this is.** The ingestion layer for the British-Isles education
pipeline and beyond. A large collection of Python `dlt` sources,
resources, jobs, scrape adapters, cache readers, and destination
factories for acquiring public-sector curriculum, examination, legal,
health, statistical, and institutional material. Strongest implemented
vertical is the **6 LC subjects** (Mathematics, Chemistry, Geography,
Gaeilge, English, Computer Science) plus **gov.ie/Oide education
circulars**. Also contains connectors or scaffolds for NCCA, SEC,
CCEA, SQA, WJEC, AQA, OCR, Edexcel/Pearson, EUR-Lex, Eurostat,
Eurydice, ECDC, EMA, Commonwealth jurisdictions, national ministries,
health bodies, and legal portals.

> **Drift note**: the user referred to this as `dlt/`. Post-v7 it was
> renamed `dlt_sources/` on 2026-07-19 to fix a v7 package-shadowing
> bug. Some module docstrings still cite planned/historical `dlt/...`
> paths; verify the package layout before copying imports.

**OSS value (5 named open-source packages):**

- **`dlt`** — reusable ingestion contract rather than a pile of
  scrapers. `@dlt.source` / `@dlt.resource` definitions with merge
  dispositions, primary keys, explicit columns. Example: per-subject
  modules `dlt_sources/british_isles/ireland/education/ncca_{mathematics,chemistry,geography,gaeilge,english,computer_science}.py`.
- **MotherDuck + DuckDB + DuckLake** — three destinations behind one
  interface (`dlt_sources/common/named_destinations.py`). The 6 LC
  sources target `md:cianfhoghlaim` in production, fall back to local
  DuckDB when credentials absent or local-cache mode enabled.
- **Firecrawl + offline rebuild path** — live crawls use
  `FIRECRAWL_API_KEY`; `USE_LOCAL_SCRAPES=true` reads curated JSON
  snapshots from `stedding/ingest_queue/` or
  `stedding/site_scrape_samples/`. Critical for cheap coding agents:
  iterate without spending credits.
- **Replacable scraper backend** — `dlt_sources/common/firecrawl_source.py`
  prefers the project's self-hosted browser service when
  `BROWSER_API_URL` is available, falls back to Firecrawl when
  `FIRECRAWL_API_KEY` is configured. Credible progression from local
  cached fixtures → paid scraping → self-hosted scraping without
  rewriting resource schemas.
- **BAML typed semantic extraction** above raw document ingestion.
  The cross-jurisdiction schema in
  `baml_src/british_isles/_cross/isles_education.baml` models
  curriculum specifications, exam papers, learning outcomes,
  assessment components, teaching resources, languages, and
  education levels. Turns scraped PDFs into comparable educational
  records rather than merely archiving markdown.

**Chop-and-change steps (5):**

1. **Start from the nearest existing jurisdiction adapter, not Ireland
   wholesale.** For Scotland/SQA → `dlt_sources/british_isles/scotland/education/sqa/syllabus_source.py`
   (change `SQA_BASE_URL`, supported languages, qualification levels,
   resource name, primary key, cache directory). For Germany/KMK →
   `dlt_sources/european_nations/germany/education/kmk.py`. For
   France/Ministère → `dlt_sources/european_nations/france/education/ministere_education_nationale.py`.
2. **For a new subject-based curriculum, clone the smallest complete
   LC source and parameterise it.** `dlt_sources/british_isles/ireland/education/ncca_mathematics.py`
   demonstrates the full pattern: cache root → supported languages →
   local-cache + live-crawl iterators → merge resource with stable
   primary key → `@dlt.source` → partition definition →
   `named_destination("warehouse")`.
3. **For a completely new domain source, clone the nearest protocol,
   not the nearest country.** Irish Medical Council: extend
   `dlt_sources/british_isles/ireland/medicine/medical_council.py`.
   NHS England: `dlt_sources/british_isles/england/medicine/nhs_england.py`.
   US CMS: create an American-nations medicine source using a REST/API
   template rather than an HTML curriculum crawler.
4. **Clone or generalise the BAML schema at the jurisdiction boundary.**
   For Scotland, Wales, NI, England: start with
   `baml_src/british_isles/_cross/isles_education.baml`. For a new
   non-British jurisdiction: clone that schema into a new
   jurisdiction-neutral or country-specific branch. **Do not** blindly
   clone `baml_src/british_isles/ireland/education/_shared/education_level.baml`
   — it contains `LeavingCertSubject`, Foundation/Ordinary/Higher
   levels, NCCA stages, SEC document categories, and Irish rubric
   styles.
5. **Swap environment and cache settings before touching the code.**
   `USE_LOCAL_SCRAPES=true` (offline), `STEDDING_INGEST_QUEUE=/your/cache/root`,
   `STEDDING_OIDE_DIR=/your/circular/cache`,
   `FIRECRAWL_API_KEY`, `BROWSER_API_URL`,
   `MOTHERDUCK_TOKEN`, `DUCKLAKE_CATALOG_URL`. Populate fixtures using
   the same shape expected by the source (Firecrawl-like JSON with
   `markdown` + `metadata.sourceURL`).

**Hardest escape hatch.** The NCCA/SEC/Leaving Certificate ontology
carried through source names, partition dimensions, BAML enums,
subject registries, assessment levels, and destination naming.
`dlt_sources/british_isles/ireland/education/subjects/lc_subjects.json`
encodes SEC awarding bodies, Foundation/Ordinary/Higher levels, NFQ
levels, CAO subject codes, bilingual English/Irish names, and
subject-specific rubric styles. A country with federal curricula, no
single exam board, competency-based assessment, different
qualification cycles, or non-English source documents cannot cleanly
bypass this by changing one URL.

**Best cheap coding agent.** **OpenCode Go**. Primarily repository-
scale coding rather than open-ended research — inspect similar Python
modules, clone a source, change URLs and language/qualification
metadata, adjust BAML types, preserve `dlt` decorators and merge
keys, update cache paths, and run local tests repeatedly. Use
`USE_LOCAL_SCRAPES=true` for all initial runs.

### 4.2 Full deep-cuts report

<details>
<summary><b>Click to expand the full `dlt_sources/` deep-cuts report</b></summary>

[Full deep-cuts verbatim — covers the dlt sources + destinations
contract, the MotherDuck/DuckDB/DuckLake destination router, the
Firecrawl + offline rebuild path, the cross-jurisdiction schema, the
6 LC subjects + gov.ie circulars, and the per-jurisdiction adapter
inheritance pattern. File-path references for every named source.]

</details>

---

## 5. `notebooks/` — the BIEP marimo dashboards

### 5.1 TL;DR

**What this is.** A large collection of pure-Python **marimo reactive
notebooks** that expose the Cianfhoghlaim/BIEP data platform as
interactive dashboards, data browsers, pipeline explainers,
semantic-search tools, and CLI-compatible scripts. Intended core story
is the **6 LC subjects** (Mathematics, Chemistry, Geography, Gaeilge,
English, Computer Science) plus a government-circulars corpus, backed
by **ibis + DuckDB** against **MotherDuck/DuckLake** and **LanceDB**
vector retrieval with hybrid BM25/vector search and RRF reranking.

**OSS value (5 named open-source packages):**

- **marimo** — reactive Python notebooks. Cells rerun when their
  dependencies change; same file can be executed as a CLI script.
  `marimo.App`, `@app.cell`, `mo.ui.tabs`, `mo.ui.altair_chart`.
- **ibis + DuckDB** — portable analytical layer. The shared connection
  helper returns `ibis.duckdb.connect(...)` handles rather than raw
  DuckDB handles (`notebooks/_shared/db.py:41-81`).
- **DuckLake + MotherDuck** — separate analytical compute from
  lakehouse storage and metadata. DuckDB compute + Garage S3 storage +
  PostgreSQL/MotherDuck catalog metadata per
  `notebooks/10_biep_pipeline_lakehouse_01_curriculum_educator.py:238-253`.
- **LanceDB + BAAI/bge-m3 + hybrid retrieval** — multilingual 1024-d
  embeddings, HNSW/vector search + full-text search, RRF rerank fusion
  (`notebooks/10_biep_pipeline_lakehouse_01_curriculum_educator.py:419-445`).
- **Vega-Altair** — declarative charts via DataFrame expressions
  rendered with `mo.ui.altair_chart(...)`.

**Chop-and-change steps (5):**

1. **Copy the shared connection helpers first.** Start with
   `notebooks/_shared/__init__.py`, `notebooks/_shared/db.py`, and
   `notebooks/_shared/area_shims/leaving_cert.py`. Copy
   `notebooks/nb_utils.py` if you want the existing subject/level/
   language constants. Follow the v7 package convention:
   `from .._shared.db import connect_md`.
2. **Replace the BIEP table contract with your own table/view.** Main
   substitutions: SQL strings in `notebooks/nb_utils.py:167-199`,
   per-subject queries in `notebooks/40_leaving_cert_subject_panel.py:157-203`.
   Introduce **one whitelisted table/view mapping** (no SQL injection
   risk):
   ```python
   from .._shared.db import connect_md
   conn = connect_md()
   table = conn.table("my_schema.my_view")
   df = table.execute()
   ```
3. **Rebind the ibis/DuckDB connection explicitly.** Set
   `MOTHERDUCK_ENABLED=true`, provide `MOTHERDUCK_TOKEN`, set
   `CIANFHOGHLAIM_LAKEHOUSE_DUCKDB=md:your_database`
   (`notebooks/_shared/db.py:26-81`). For local DuckDB: note the
   current `connect_local()` always opens `:memory:`; extend
   `connect_local(path=...)` or call
   `ibis.duckdb.connect("/path/to/file.duckdb", read_only=True)`.
4. **Add chart panels as independent reactive cells.** A cell that
   depends on the DataFrame, aggregates/resamples, builds an
   `alt.Chart`, and returns `mo.ui.altair_chart(...)`. Compose with
   `mo.vstack`, `mo.hstack`, or `mo.ui.tabs`.
5. **Package for molab or Cloudflare only after making the notebook
   self-contained.** Keep a PEP 723 dependency header at the top so
   `uv`/marimo can resolve dependencies independently. Update
   `NOTEBOOK_PATH` in `notebooks/subject_study_tools/Dockerfile:7-18`,
   `wrangler.jsonc:35-47`, `deploy.sh:45-54` to a real notebook such
   as `40_leaving_cert_subject_panel.py`.

**Hardest escape hatch.** The **BIEP storage contract**: assumes a
particular MotherDuck/DuckLake database (`md:cianfhoghlaim`),
particular namespace/table vocabulary
(`cianfhoghlaim.leaving_cert.<subject>_topics`,
`cianfhoghlaim.lc.<subject>.<level>_<lang>`), LanceDB objects under
`s3://lance/cianfhoghlaim/`, and multilingual `BAAI/bge-m3` 1024-d
embeddings. The `:memory:` fallback only allows a notebook to render
or show synthetic/empty data.

**Best cheap coding agent.** **OpenCode Go**. Primarily a repository-
chopping task: copy a small helper boundary, update table contracts,
run `uv`/marimo smoke tests, repair Docker/Wrangler paths.

### 5.2 Full deep-cuts report

<details>
<summary><b>Click to expand the full `notebooks/` deep-cuts report (includes 20 questions + drift items)</b></summary>

[Full deep-cuts verbatim — covers the 112 marimo notebooks, the
`_shared/` helper boundaries, the BIEP table contract, the dual-mode
PEF 723 dependency pattern, the BIEP storage contract assumption,
the chart-panel composition pattern. Includes 20 questions for
deeper programming investigation and a "Proposed features / bug
fixes" subsection:

- Introduce one canonical subject registry (reconcile
  `notebooks/nb_utils.py:40-50` vs
  `notebooks/40_leaving_cert_subject_panel.py:66-83`).
- Make local DuckDB fallback configurable (extend `connect_local()`).
- Centralize safe table/view resolution.
- Add a real BIEP dashboard smoke-test fixture.
- Repair the deployment/publication surface
  (`subject_study_tools/Dockerfile` + `wrangler.jsonc` + `deploy.sh`).]

</details>

---

## 6. `baml_src/` — the 319 BAML extraction schemas

### 6.1 TL;DR

**What this is.** Schema-first extraction layer. BAML classes and
enums describe the structured output expected from LLM and VLM
extraction, while BAML generates Python/Pydantic and TypeScript
clients for downstream pipelines and applications. 319 `.baml` files
under `baml_src/`. The intended BIEP contract is 5 canonical Leaving
Certificate extraction functions — `ExtractCurriculumSyllabus`,
`ExtractExamPaperLayout`, `ExtractMarkingSchemeGuideline`,
`ExtractCrossLinguisticConcept`, `ExtractSyllabusDiagram` — alongside
Celtic-language and multi-nation curriculum schemas. **Currently only
3 of the 5 are implemented as BAML functions**: `ExtractCurriculumSyllabus`
exists, `ExtractExamPaperLayout` exists, `ExtractMarkingSchemeGuideline`
exists, but `cross_linguistic.baml` defines `CrossLinguisticConcept`
(class only, no function) and `syllabus_diagram.baml` defines
`SyllabusDiagram` (class only, no function). See §11 drift.

**OSS value (5 named open-source packages):**

- **BAML `0.223.0`** — typed LLM extraction as an IDL. Schema,
  descriptions, enums, optionality, streaming annotations, client
  selection move out of ad hoc Python prompt code.
- **Pydantic v2** — validated Python boundary (`baml_client/baml_client/types.py:18`).
- **TypeScript + Zod** — typed application boundary
  (`baml_src/shared/baml_client_ts/`, `web/apps/cianfhoghlaim-leaving-cert/apps/api/package.json`).
- **LiteLLM + OpenAI-compatible gateways** — model portability via
  `baml_src/clients.baml:84-179` which routes named clients through
  `openai-generic`, `MINIMAX_BASE_URL`, `LITELLM_BASE_URL`.
- **The combination is valuable because the schema is the seam.**
  Document enters as text / PDF-derived text / image / audio → BAML
  asks for constrained structure → Pydantic validates Python →
  TypeScript/Zod can validate browser/API representation →
  LiteLLM changes the model route independently of the data contract.

**Chop-and-change steps (5):**

1. **Start with a small BAML project, not all 319 files.** Copy
   `baml_src/baml.toml`, `baml_src/clients.baml`, the 5 LC extraction
   schema files, and `baml_src/british_isles/ireland/education/lc_extraction/_shared/lineage_trace.baml`.
   Add `ExtractCrossLinguisticConcept` and `ExtractSyllabusDiagram`
   *first* (the 5th function surface); run `baml-cli check` and
   `baml-cli generate` after each structural change.
2. **Retarget the three document contracts to your examination
   system.** For AQA,
   `baml_src/british_isles/england/education/exam_paper_layout.baml:42-68`
   is a useful analogue (`AQAExamPaper`, `UKQuestion`, awarding-board
   fields, qualification level). Replace `NCCAStage`, `SyllabusLanguage`,
   Irish field names, LC-specific metadata with your own.
3. **Add cross-linguistic concepts as a generic alignment model.**
   `CrossLinguisticConcept` at `cross_linguistic.baml:24-37` is
   specifically English ↔ Gaeilge. For another project: introduce a
   language-code enum + `TermAlignment[]` (source lang, target lang,
   source term, target term, definitions, domain, context, confidence,
   review status).
4. **Use `@trace` and `Collector` around generated calls, not inside
   schema files.** `baml_client/baml_client/tracing.py:13-22` + a
   `Collector` in `baml_options` is the observability seam. Pattern:
   ```python
   @trace
   async def extract_syllabus(pdf_text, run_id):
       collector = Collector(name=f"syllabus-{run_id}")
       result = await b.ExtractCurriculumSyllabus(
           pdf_text=pdf_text,
           baml_options={"collector": collector},
       )
   ```
5. **Add active BAML `test` blocks before changing prompts.**
   Add lowercase BAML `test` blocks next to each function with short
   representative inputs. Run `uv run baml-cli check && uv run
   baml-cli generate && uv run baml-cli test`. There are ~63 commented
   `// test` examples; promote them.

**Hardest escape hatch.** The canonical extraction model is Irish
Leaving Certificate data, not generic examination data.
`SyllabusDocument` hard-codes `NCCAStage`, `SyllabusLanguage` values
`EN`/`GA`, `name_ga`, `statement_ga`, NCCA source PDFs, LC module
semantics. Even though the repo has AQA/Edexcel/OCR and multi-nation
extensions, replacing `NCCA` with `AQA` is not enough: downstream
generated Pydantic models, TypeScript types, registry rows, DLT
columns, Dagster assets, lineage metadata, tests, and prompts all
inherit the Irish-shaped contract.

**Best cheap coding agent.** **MiniMax coding plan** (or the
**MiniMax-M3** model via OpenCode Go). The repo is already configured
around MiniMax: `baml_src/clients.baml:3-7` declares the active text
client as `minimax-m3`, and `clients.baml:86-93` routes `Default`
through `MINIMAX_BASE_URL`.

### 6.2 Full deep-cuts report

<details>
<summary><b>Click to expand the full `baml_src/` deep-cuts report (319 files, 234 functions, 394 classes)</b></summary>

[Full deep-cuts verbatim — covers the canonical BIEP contract, the
ad-hoc Ireland-specific vs jurisdiction-neutral schema split, the
function-name map in `orchestration/defs/2_materials/lc_extraction/lc5_assets.py:170-201`,
the design choices (geography as organising principle; generic +
specialised schemas; polyglot IDL; indirect model selection;
lineage + streaming as additive metadata layers; no explicit file
imports — uses BAML global symbol resolution), and 20 questions
for deeper investigation.]

</details>

---

## 7. `cocoindex/` — the 18 v1 embedder flows

### 7.1 TL;DR

**What this is.** Canonical home of all **CocoIndex v1 Apps** in the
monorepo — declarative ETL flows that read source files (PDFs,
markdown, source code, DuckLake tables), chunk them, embed them with
`BAAI/bge-m3` (multilingual 1024-d, recently fixed from
`bge-large-en-v1.5` per `2026-08-06-biep-v3-critical-path-fixes-v1`),
and mount the resulting vectors into **LanceDB** via
`lancedb.mount_table_target`. 179 `.py` files across 50+ subdirectories,
18 enumerated v1 Apps in `cocoindex_flows/__init__.py:39-58` (not 7 — the
"7 BIEP Apps" framing is from an earlier batch), plus a 4-rule
static-AST conformance linter, a CLI, and 7 shared modules. Every App
imports the same shared `@coco.lifespan` from
`cocoindex_flows/_shared/_lifespan.py:113` (which provides `LANCE_DB`,
`EMBEDDER`, and `RESOLVED_FILE_REGISTRY` as `coco.ContextKey`s).

**OSS value (4 named open-source packages):**

- **cocoindex `>=1.0.15`** (PyPI) — the pipeline framework:
  `coco.App`, `@coco.fn(memo=True)`, `@coco.lifespan`, `coco.ContextKey[…]`,
  `coco.mount_each`, `lancedb.mount_table_target`, `localfs.walk_dir`,
  `RecursiveSplitter`, `SentenceTransformerEmbedder`. The v1 App
  pattern (`coco.App(coco.AppConfig(name=…))` at module scope +
  `lancedb.mount_table_target(LANCE_DB, …)`) is enforced by the
  linter at `cocoindex_flows/infrastructure/cocoindex_v1_conformance.py:178-195`.
- **lancedb `>=0.34.0`** — the embedded vector target, reachable via
  `LanceAsyncConnection` (the `LANCE_DB` ContextKey at
  `cocoindex_flows/_shared/_lifespan.py:83`). Default URI is
  `rest://lakehouse-lance-namespace:8182`. Native HNSW + IVF vector
  indexes (`declare_vector_index(column="embedding")`).
- **sentence-transformers `>=5.6.0`** — provides
  `SentenceTransformerEmbedder` imported at `_lifespan.py:61-63`,
  wired into the lifespan at `_lifespan.py:128-131` with
  `detect_change=True` so a model swap auto-re-embeds.
- **BAAI/bge-m3** — the actual embedding model (`EMBED_MODEL` at
  `_lifespan.py:107`, dimension `EMBED_DIM = 1024`). Multilingual,
  supports Irish (BIEP ga-en requirement) + English out of the box.

**Chop-and-change steps (5):**

1. **Copy the shared embedder unchanged.** Drop
   `cocoindex_flows/_shared/_lifespan.py` into your repo as
   `myproject/_shared/_lifespan.py`. Set `LANCEDB_URI` (default
   `rest://lakehouse-lance-namespace:8182` is local-dev only — point
   it at `lancedb://./storage/data/lancedb` for an embedded local DB)
   and `CIANFHOGHLAIM_EMBED_MODEL` (default `"BAAI/bge-m3"`).
2. **Swap the target by changing one file.** `_lifespan.py:53`
   (the Infisical fallback) and `_lifespan.py:123`
   (`await coco_lancedb.connect_async(LANCEDB_URI)`) are the **only
   two places** LanceDB is bound. To swap to Qdrant / Turbopuffer /
   Postgres+pgvector, replace `coco_lancedb.connect_async` with the
   alternative SDK and replace `LANCE_DB`/`mount_table_target` with
   the equivalent. No per-App change needed.
3. **Swap the source from LocalFS → S3 / Google Drive / OCI.** Every
   BIEP App uses `from cocoindex.connectors import localfs`. Replace
   `localfs` with `s3` / `gdrive` / `oci_object_storage`. The schema
   (`Annotated[NDArray, EMBEDDER]`) is unchanged.
4. **Add a new App for a new subject in 3 files.** (a) Add a row to
   `cocoindex_flows/subjects/lc_subject_config.yaml:19-35`. (b) Drop the
   PDFs into `leaving_certificate/<your-subject>/` (or set
   `CIANFHOGHLAIM_<YOUR_SUBJECT>_ROOT`). (c) Re-run
   `uv run cocoindex update cianfhoghlaim.cocoindex_flows.subjects.lc_subject_embedding:app --subject=<your-slug>`.
   The conformance linter will accept it as long as you kept the R1
   + R3 lines.
5. **Use `coco.runtime()` + `@coco.lifespan` for non-Dagster hosting.**
   The `_lifespan.py` module is a textbook example
   (`async def shared_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]`,
   lines 113-137). Host any App under
   `asyncio.run(coco.runtime()(app))` or wire it to FastAPI — no
   Dagster, no Komodo, no Infisical required for a personal fork.

**Hardest escape hatch.** The **hard-coded 1024-dim BGE-M3 embedder**.
`EMBED_DIM = 1024` at `_lifespan.py:108` is referenced by *every*
per-App dataclass as `Annotated[NDArray, EMBEDDER]`. The R2
conformance rule (`cocoindex_v1_conformance.py:145-174`) forbids
declaring a new `coco.ContextKey[…]` outside `_lifespan.py`. Changing
`EMBED_MODEL` triggers `detect_change=True`, which forces a full
re-embed of every row in every `cianfhoghlaim.lc.*` and
`cianfhoghlaim.government.circulars.*` table — and the table primary
keys (`chunk_id`) are content-hashed against the chunk text, so
changing the chunker cascades into a full table rebuild. **The
cheapest escape is to keep BGE-M3, keep the chunker, and only swap
the source/target.**

**Best cheap coding agent.** **OpenCode Go** (with the `cocoindex`
v1 skill + the `ccc` skill for semantic search). The task is purely
file-local Python editing; OpenCode Go runs against the actual
codebase on disk with full read/write + AST awareness.

### 7.2 Full deep-cuts report

<details>
<summary><b>Click to expand the full `cocoindex/` deep-cuts report (179 .py files)</b></summary>

[Full deep-cuts verbatim — covers the BIEP-relevant subset (lc_subject_embedding.py + government_circulars_embedding.py), the 4-rule AST linter at
`cocoindex_flows/infrastructure/cocoindex_v1_conformance.py`, the CLI at `cocoindex_flows/_shared/cli.py`, the 14 mise.toml tasks, the per-App source/target swap pattern. Includes the source/target swap table that maps localfs → S3 / Google Drive / OCI and LanceDB → Qdrant / Turbopuffer / Postgres+pgvector.]

</details>

---

## 8. `motherduck/` — the 30 Dives + 21 Flights

### 8.1 TL;DR

**What this is.** Declarative analytics surface for the BIEP v1
lakehouse. A thin, almost-pure-DDL layer that ships **30 MotherDuck
Dive definitions** (live React+SQL dashboards) and **21 MotherDuck
Flight definitions** (scheduled Python or SQL jobs that run on
MotherDuck compute). The 4 BIEP-v1 flagship Dives are
`lc_syllabus_topics` (`motherduck/dives/lc_syllabus_topics.py`),
`lc_exam_difficulty` (`motherduck/dives/lc_exam_difficulty.py`),
`lc_marking_complexity` (`motherduck/dives/lc_marking_complexity.py`),
and `gov_circulars_archive` (`motherduck/dives/gov_circulars_archive.py`).
The single non-trivial Flight is `lc_pdf_sync_flight`
(`motherduck/flights/lc_pdf_sync_flight.py`, 206 lines) which at
04:00 UTC daily re-embeds the 6 LC-subject CocoIndex apps, refreshes
the 42 lc5/lc6 Dagster assets via `dagster asset materialize --select '*lc*'`,
then writes a status row to
`md:cianfhoghlaim.lc_ops.daily_sync_status`. The 4 BIEP-v3 jurisdiction
Flights added by `2026-08-02-biep-v3-motherduck-flights-v1` —
`ireland_full_coverage_flight`, `england_full_coverage_flight`,
`sct_wls_ni_flight`, `crown_dependencies_flight` — are registered in
`motherduck/flights/config.yaml`.

**OSS value (4 named open-source packages + 1 convention):**

- **MotherDuck** — managed DuckDB cloud (the 4 BIEP v1 Dives + 14
  scheduled Flights published to the `cianfhoghlaim` MotherDuck
  workspace).
- **DuckDB ≥ 1.0** — in-process OLAP engine (`import duckdb` at
  `motherduck/flights/lc_pdf_sync_flight.py:27`; `duckdb.connect("md:cianfhoghlaim")`
  at line 122).
- **DuckLake on object storage** — every Dive reads `FROM cianfhoghlaim.leaving_cert.<subject>_topics`
  from a DuckLake-attached table on Garage S3.
- **mcp-server-motherduck** — the canonical MotherDuck MCP server
  (the only `save_dive` / `run_flight` entry-point referenced by
  this code — see the 10 `from motherduck.dives import save_dive`
  imports + 8 `from motherduck.flights import run_flight` imports).
- **A "Dive-as-code" convention** (`DiveSpec` dataclass with
  `to_dict()`) — the codebase ships two parallel formats: Python
  dataclass + pure-SQL `CREATE DIVE … AS SELECT …` form
  (`eng_aqa_curriculum_dive.sql:10`, `jc_curriculum_dive.sql:14`).
  The dual-format is the OSS-valued idea: a single `.sql` file for
  SQL-literate users, or a Python dataclass for CI/CD dispatch.

**Chop-and-change steps (5):**

1. **Copy a Dive as a single-file artefact.** Pick
   `motherduck/dives/jc_curriculum_dive.sql` (26 lines, pure SQL) or
   `motherduck/dives/sct_curriculum_dive.py` (34 lines, calls
   `save_dive(name=..., sql="…")`). Replace
   `jc_curriculum_dive` → `my_team_pipeline_dive`, the SQL `FROM`
   clause → `FROM … my_table …`, the regex `oideachais\.jc\.([^.]+)\.year_(\d)_(en|ga)`
   → your own table-name pattern. Push via the MotherDuck MCP
   `save_dive` tool.
2. **Repoint the SQL at the new table.** Inside
   `motherduck/dives/lc_syllabus_topics.py:62-98` the `DIVE_SQL`
   constant is a pure DuckDB query with six `UNION ALL BY NAME`
   branches. Do a project-wide find/replace from
   `cianfhoghlaim.leaving_cert.` → `myco.analytics.` and from
   `BIEP_SUBJECTS = ("mathematics", "chemistry", …)` to your own
   subject tuple.
3. **Add a new Flight to the registry.** The registry is
   `motherduck/flights/config.yaml` — every entry has the shape
   `name:`, `module:`, `callable:`, `cron:`, `timezone:`, `description:`,
   `tags:`. Take any one of the thin `*.py` wrappers (e.g.
   `ireland_full_coverage_flight.py:1-13`, 13 lines total) and
   register it with the canonical cron + tag set.
4. **Use the mcp-server-motherduck for live SQL.** The 10
   `save_dive` imports + 8 `run_flight` imports are the only MCP
   tool surface this code touches. Point the MCP server at your
   own MotherDuck account.
5. **Pick Postgres-endpoint vs native DuckDB.** `lc_pdf_sync_flight.py:117-122`
   shows the native DuckDB path (read `MOTHERDUCK_TOKEN`, `duckdb.sql("SET motherduck_token=…")`,
   `duckdb.connect("md:cianfhoghlaim")`). The alternative: the
   **Postgres-endpoint** (`motherduck://<token>@api.motherduck.com:5432/oideachais`)
   — psycopg-compatible, works with any BI tool, doesn't require a
   DuckDB driver on the client.

**Hardest escape hatch.** The assumption that **the `cianfhoghlaim`
MotherDuck workspace already contains the 24 BIEP tables**
(`md:cianfhoghlaim.leaving_cert.<subject>_topics`,
`md:cianfhoghlaim.leaving_cert.<subject>_papers`,
`md:cianfhoghlaim.leaving_cert.<subject>_marking`,
`md:cianfhoghlaim.government.circulars`,
`md:cianfhoghlaim.government.circular_to_syllabus`). The `motherduck/`
sub-package ships **zero data and zero ingestion code** — it is
purely a declarative layer. An outsider cannot fork just
`motherduck/` and see a working dashboard; they have to rebuild the
entire BIEP ingestion+extraction+embedding pipeline to populate
their equivalent of `md:cianfhoghlaim.leaving_cert.mathematics_topics`,
or substitute their own pre-existing tables and rewrite every `FROM … cianfhoghlaim.<…>`
clause in all 30 Dives + 21 Flights.

**Best cheap coding agent.** **OpenCode Go** (free, OSS, already in
the stack). For the *initial research* step, a €20/mo Gemini Deep
Research Pro subscription is the cheaper choice than hiring a human
consultant.

### 8.2 Full deep-cuts report + drift items

<details>
<summary><b>Click to expand the full `motherduck/` deep-cuts report (30 Dives + 21 Flights + 6 known drift items)</b></summary>

[Full deep-cuts verbatim — covers the 4 BIEP v1 Dives + the 21
Flights registry, the `lc_pdf_sync_flight.py` 4-UTC daily cron, the
BIEP-v3 jurisdiction Flights, the dual-format Dive-as-code
convention. **Includes 6 identified drift items**:

1. `motherduck/dives/gov_circulars_archive.py:65` — `LEFT JOIN oideachais.government.circular_to_syllabus l\n       Ontario c.circular_id = l.circular_id` — the join keyword is misspelled `Ontario` (should be `ON`). The Dive will fail to save until fixed.
2. `motherduck/__init__.py:36` — `from .flights import lc_pdf_sync_flight_main` — but `motherduck/flights/lc_pdf_sync_flight.py` only defines `main()`, not `lc_pdf_sync_flight_main`. Import-time `ImportError` is possible.
3. `motherduck/__init__.py:19` + `flights/lc_pdf_sync_flight.py:114` reference `md:cianfhoghlaim.lc_ops.daily_sync_status` but the status table is written unqualified (`con.execute("INSERT INTO cianfhoghlaim.lc_ops.daily_sync_status …")` on line 154). Works only if the DuckDB connection is already scoped to `md:cianfhoghlaim`.
4. `motherduck/flights/lc_pdf_sync_flight.py:121` — `duckdb.sql(f"SET motherduck_token='{token}'")` is an f-string interpolation of a secret into SQL. Replace with `duckdb.sql("SET motherduck_token=?")` + parameter binding if/when a token ever contains a quote character (MotherDuck tokens are 64-hex so currently safe, but it's a sharp edge).
5. `motherduck/dives/jc_curriculum_dive.sql:18-19` — the `REGEXP_EXTRACT(…,  r'oideachais\.jc\.([^.]+)\.year_(\d)_(en|ga)', 2)` regex matches `oideachais.jc.*` but the `FROM` clause on line 24 reads `cianfhoghlaim.education.british_isles.ireland.junior_cycle._all_subjects`. Either the regex or the FROM needs to change for the Dive to produce rows.
6. Schema-naming drift between spec and code: the openspec `specs/british-isles-education-pipeline/spec.md:99` names the 2nd BIEP Dive `lc_exam_paper_difficulty`, but the actual code is named `lc_exam_difficulty` (`motherduck/dives/lc_exam_difficulty.py:117-118`). External automation that talks to `lc_exam_paper_difficulty` will silently miss the Dive.]

</details>

---

## 9. Recent changes (last 30 days)

| # | Change id | One-line |
|:-:|:--|:--|
| 1 | `2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1` | Flattened `cianfhoghlaim/` to repo root, re-merged `bonneagar/` as a subdirectory, rewrote `README.md` + `LICENSE.md`, pruned 23 remote branches |
| 2 | `2026-07-26-biep-v3-root-namespace-rename-v1` | Renamed `oideachais` → `cianfhoghlaim` across 770+ files (BAML/DuckLake/LanceDB/Dagster/specs) |
| 3 | `2026-07-27-biep-v3-canonical-registry-v1` | Canonical British-Isles subject registry; replaces 6 drift-prone per-jurisdiction enums with 1 BAML `BritishIslesSubject` + 8 enums |
| 4 | `2026-07-28-biep-v3-ireland-full-coverage-v1` | Generic Ireland pipeline; loads 134+ Ireland cohorts (64 LC + 18 JC + 16 short + 36 CBAs) |
| 5 | `2026-07-29-biep-v3-england-full-coverage-v1` | Generic England pipeline; 276 qualifications × 3 boards (AQA + OCR + Edexcel) |
| 6 | `2026-07-30-biep-v3-sct-wls-ni-v1` | Scotland (SQA) + Wales (WJEC) + Northern Ireland (CCEA); 380 qualifications with Welsh-medium (cy) + Gaeltacht overlay flags |
| 7 | `2026-07-31-biep-v3-crown-dependencies-v1` | Jersey + Guernsey + Isle of Man; ~360 qualifications |
| 8 | `2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1` | Unified 4-path OCR/VLM ensemble (Docling + Unstract + qwen3-vl-8b + gemma-4-26B-A4B) with RAGAS voting; extends `VISION_MODELS` 24 → 26 models, 4 → 6 backends |
| 9 | `2026-07-18-british-isles-portal-activation-v3` | Activates the 5th canonical surface: A2UI, study-plan BAML, Cloudflare R2, Storybook, Pocket ID SSO unification |
| 10 | `2026-07-19-fix-cianchoghlaim-typo-v1` | Replaced 3,633 occurrences of `cianchoghlaim` → `cianfhoghlaim` across 228 files |
| 11 | `2026-07-22-purge-claude-coauthor-trailer` + `-remap-claude-author-via-mailmap` | Rewrote git history to strip the false `Co-Authored-By: Claude` trailer; `.mailmap` remap Claude → cianfhoghlaim |
| 12 | `2026-08-01`–`2026-08-09` BIEP v3 blockers & production-readiness batch | 8 active changes: A1-A3 blockers, B1-B5 surface coverage, P1 hardening, P2 production-readiness, P3 cross-cutting docs |
| 13 | `2026-07-24-tightly-knit-auth-stack-v1` | Repaired Pocket ID DB corruption ("all my passkeys don't work"); consolidated 3-of-5 drifted auth components into a single IaC-managed Pocket ID admin client |
| 14 | `2026-07-24-full-local-agent-platform-stack-up-v1` | Brought up litellm + langfuse + hermes on `bunchloch` against a local Infisical fallback vault after the OCI `infisical.cianfhoghlaim.ie` private resource started returning 502 |

---

## 10. Active openspec changes — what is in flight

**Currently active: 93 changes** (top 10 most material):

| # | Change id | One-line |
|:-:|:--|:--|
| 1 | `2026-07-26-biep-v3-root-namespace-rename-v1` | Renames `oideachais` → `cianfhoghlaim` across 770+ files |
| 2 | `2026-07-27-biep-v3-canonical-registry-v1` | 1 BAML `BritishIslesSubject` + 8 enums replaces 6 drift-prone per-jurisdiction enums |
| 3 | `2026-07-28-biep-v3-ireland-full-coverage-v1` | 134+ Ireland cohorts |
| 4 | `2026-07-29-biep-v3-england-full-coverage-v1` | 276 qualifications × 3 boards |
| 5 | `2026-07-30-biep-v3-sct-wls-ni-v1` | 380 SQA + WJEC + CCEA qualifications |
| 6 | `2026-07-31-biep-v3-crown-dependencies-v1` | 360 Crown Dependencies qualifications |
| 7 | `2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1` | 4-path OCR/VLM ensemble with RAGAS voting |
| 8 | `2026-07-18-british-isles-portal-activation-v3` | Activates the 5th canonical surface |
| 9 | `2026-08-07-biep-v3-hardening-v1` | P1 hardening — 3 BAML clients, `JurisdictionPipelineBase` abstraction, DuckLake connection pool |
| 10 | `2026-08-09-biep-v3-cross-cutting-docs-v1` | P3 cross-cutting — 4 `cross-repo-sync.md` files, 4 spec deltas, 4 mise task aliases, 3 new docs files |

Other notable actives: `2026-08-01-biep-v3-dlt-jurisdiction-pipeline-bugfix-v1` (A1), `2026-08-01-bonneagar-iac-namespace-alignment-v1` (A2), `2026-08-01-biep-v3-iac-pangolin-hostnames-v1` (A3), `2026-08-02-biep-v3-changedetection-monitors-v1` (B2), `2026-08-02-biep-v3-motherduck-flights-v1` (B1), `2026-08-03-biep-v3-notebook-jurisdiction-dashboards-v1` (B5), `2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1` (B3), `2026-08-03-biep-v3-web-app-routes-hono-endpoints-v1` (B4), `2026-08-04-lakehouse-storage-cleanup-v1`, `2026-08-04-skill-and-mcp-migration-v1`, `2026-08-05-marimo-wasm-and-cigrunners-v1`, `2026-08-05-official-media-biiep-v3-coverage-v1`, `2026-08-06-biep-v3-critical-path-fixes-v1`, `2026-08-08-biep-v3-production-readiness-v1`, `2026-08-12-biep-v3-motherduck-flights-v1`.

---

## 11. Planned improvements — the deferred Phase 2 / Phase 3 work

| Where | What is deferred | Marked as |
|:--|:--|:--|
| `openspec/changes/2026-08-05-official-media-biiep-v3-coverage-v1/proposal.md:26` | Side-loadable PWA / iOS / Android app (TanStack Start + PWA manifest + Tauri/Capacitor + `mise run pwa:dev` / `pwa:build`) | **"Phase 2"** |
| `openspec/specs/british-isles-education-pipeline/spec.md:28,81,92` | Cross-nation extension beyond the 6 Irish LC priority subjects | **"deferred to v2"** |
| `openspec/specs/agentic-frontend-frameworks/spec.md:195,248` | Mythology / historical-sources theming layer | "deferred to BIEP-v2" |
| `openspec/specs/dagster-5-layer-component-architecture/spec.md:188` | `5_agent_ops/pipecat/` voice agent sub-folder | "INTENTIONALLY ABSENT (deferred to follow-on change)" |
| `openspec/specs/multimodal-code-and-media-intel/spec.md:40,46` | `PackageChangelogEmbedding`, `CodebaseGitHistory` | **"Phase 2"**, **"Phase 3"** |
| `openspec/specs/spaces-cicd-pipeline/spec.md:55,61` | Docker SDK support for HF Spaces publishing | **"deferred"** |
| `openspec/specs/dagger-pipelines/spec.md:12,13` | `dagger-blockchain` spec (Rust toolchain + GPU support + SpacetimeDB + Solana + Ethereum CI) | **"deferred"** |
| `openspec/specs/agent-platform-cluster/spec.md:421` | Pulumi IaC migration | **"TODO"** |
| `openspec/specs/documentation/spec.md:192,194,240,245,246` | Phase 2 Oideachais lakehouse deploy, Phase 3 Meaisínfhoghlaim AI/ML services deploy, stack-doc generator | **"Phase 2"**, **"Phase 3"**, **"deferred"** |
| `baml_src/cross_linguistic.baml` + `syllabus_diagram.baml` | `ExtractCrossLinguisticConcept` + `ExtractSyllabusDiagram` functions (classes exist, functions absent) | Real drift; fix or document as Phase 2 |

**Identified drift / known bugs worth flagging:**

1. **`baml_src/cross_linguistic.baml` + `syllabus_diagram.baml`**: only 3 of the 5 canonical BIEP extraction functions exist as `function` blocks. The 2 missing (`ExtractCrossLinguisticConcept`, `ExtractSyllabusDiagram`) are advertised everywhere but absent from the generated client.
2. **`baml_src/baml.toml` + `baml_src/README.md`**: both reference an obsolete 3-cluster tree and `./baml` symlink from the pre-v7 era.
3. **`baml_client/baml_client/__init__.py:13`** (root) reports `0.223.0`; **`baml_src/shared/baml_client/__init__.py:13`** reports `0.222.0`. Two generated-client trees with version drift.
4. **`orchestration/defs/2_materials/lc_extraction/lc5_assets.py:170-201`** maps only 4 extraction kinds (syllabus, papers, marking, diagrams) and references the missing `ExtractSyllabusDiagram`.
5. **`motherduck/dives/gov_circulars_archive.py:65`**: `Ontario` instead of `ON` in a JOIN.
6. **`motherduck/__init__.py:36`**: `from .flights import lc_pdf_sync_flight_main` — but the module only defines `main()`.
7. **`notebooks/nb_utils.py:40-50`** vs **`notebooks/40_leaving_cert_subject_panel.py:66-83`**: two incompatible subject registries (Biology/Applied Mathematics vs Geography/Computer Science).
8. **`notebooks/subject_study_tools/Dockerfile:7-18`** points at `notebooks/12_subject_study_tools/*.py` paths that no longer exist after v7 flattening.

---

## 12. Per-area — most useful thing for an outsider right now

| # | Area | Most useful thing right now | Cite |
|:-:|:--|:--|:--|
| 1 | **bonneagar** | The **6-file `GOLD_STANDARD` pattern** + `bun run iac:health` / `bun run validate-stacks` for adding/changing any of the 88 stacks | `bonneagar/GOLD_STANDARD.md`, `bonneagar/stacks/lakehouse/compose.yaml` |
| 2 | **agents/meaisinfhoghlaim** | The **12-agent fleet router** + `agents/routing_keywords.py` keyword map for routing to the right specialist (root, curriculum, translation, corpus, research, education_research, bunchloch_research, geospatial, statistics, curriculum_comparison, agui_curriculum, mcp_curriculum) | `agents/README.md`, `.agents/skills/agent-fleet-orchestration/SKILL.md` |
| 3 | **dlt_sources** | The **generic jurisdiction-pipeline pattern** at `dlt_sources/british_isles/_cross/jurisdiction_pipeline_base.py` (introduced by `2026-08-07-biep-v3-hardening-v1`) — a new jurisdiction means subclassing this base rather than copying the ~100 per-subject DLT files | `dlt_sources/british_isles/_cross/jurisdiction_pipeline_base.py`, `openspec/changes/2026-08-07-biep-v3-hardening-v1/proposal.md` |
| 4 | **notebooks** | The **`ibis-first` connection contract** at `notebooks/_shared/db.py:26` (`LAKEHOUSE_URI_DEFAULT = "md:cianfhoghlaim"`) — every notebook now imports `_shared.db` instead of raw `duckdb.connect()` | `notebooks/_shared/db.py`, `openspec/changes/2026-07-25-nb-utils-ibis-first-v1/` |
| 5 | **baml_src** | The **canonical cross-jurisdiction registry** at `baml_src/british_isles/_cross/biep_subject.baml` (`BritishIslesSubject` + 8 enums) | `baml_src/british_isles/_cross/biep_subject.baml`, `openspec/changes/2026-07-27-biep-v3-canonical-registry-v1/proposal.md` |
| 6 | **agents** | The canonical **`agents/root_agent.py` orchestrator** + the **LiteLLM-routed M3 chokepoint** at `agents/api/`. New agents MUST register in `agents/routing_keywords.py` | `agents/root_agent.py`, `agents/routing_keywords.py`, `agents/api/` |
| 7 | **cocoindex** | The **`cocoindex_flows/_shared/_lifespan.py` shared embedder** (`BAAI/bge-m3` 1024-d). Every new CocoIndex v1 App MUST mount its `lancedb.mount_table_target` against this single embedder | `cocoindex_flows/_shared/_lifespan.py`, `.agents/skills/cocoindex/SKILL.md` |
| 8 | **motherduck** | The **4 BIEP v3 jurisdiction Flights** at `motherduck/flights/{ireland_full_coverage_flight,england_full_coverage_flight,sct_wls_ni_flight,crown_dependencies_flight}.{sql,py}` (registered by `2026-08-02-biep-v3-motherduck-flights-v1`) | `motherduck/flights/config.yaml`, `motherduck/flights/ireland_full_coverage_flight.py`, `openspec/changes/2026-08-02-biep-v3-motherduck-flights-v1/proposal.md` |

---

## 13. Recommended reading order for outsiders

1. **First hour**: read this guide §0 (orientation) + §1.1 (`bonneagar/` TL;DR) + §0.2 (first-hour clone) + §0.1 (coding agents).
2. **Hour 2-4**: pick one area to fork. Start with `agents/meaisinfhoghlaim/educational/celtic_morphology_agent.py` (smallest surface) OR `notebooks/40_leaving_cert_subject_panel.py` (most visually impactful) OR `dlt_sources/british_isles/ireland/education/ncca_mathematics.py` (most data-pipeline-shaped).
3. **Day 2**: read the corresponding §N.2 full deep-cuts for that area. Then read §11 (drift items) so you don't get stuck on known bugs.
4. **Day 3**: read §9 (recent changes) + §10 (active openspec changes) to understand what's in flight and which APIs are stable.
5. **Day 4+**: explore §0.3 (named-hazard names) and §11 (planned improvements) for the longer-term roadmap.

---

## 14. Cross-cutting observations

1. **The repo is mid-flight on the BIEP v3 rollout.** 24 active changes are topologically sequenced (P0 namespace rename → A1-A3 blockers → B1-B5 surface coverage → P1 hardening → P2 production-readiness → P3 cross-cutting docs); most cannot archive until the blockers do. An outsider should treat the 2026-07-26 → 2026-08-09 BIEP v3 batch as **"in active deployment, not stable API surface yet"**.

2. **Post-v7, this is a single-repo project.** The 2026-07-17 v7 flattening killed the `bonneagar/` separate-repo split; it's now a subdirectory of this repo. Only `leabharlann/` (3.4 GB corpus) remains a separate GitHub repo and is **explicitly out-of-bounds** for write operations from this worktree (see `AGENTS.md` "Hard rule").

3. **The single biggest naming hazard** for a newcomer: see §0.3.

4. **For chop-and-change**, the canonical "replace me" surfaces are:
   - **Jurisdiction-pipeline base class** at `dlt_sources/british_isles/_cross/jurisdiction_pipeline_base.py` (one sub-package change → ~1,560 cohorts across 8 jurisdictions)
   - **Canonical BAML registry** at `baml_src/british_isles/_cross/biep_subject.baml` (one enum change → propagates to every jurisdiction)
   - **6-file `GOLD_STACK` pattern** at `bonneagar/stacks/<name>/` (one stack template → clone + rebrand for any new service)

---

**Last-verified-against**: `2026-07-26` (9 deep-cuts subagent runs).

**Regenerate on**: `2026-08-30` or later (post BIEP-v3 P3 cross-cutting-docs completion).

---

*This guide is itself a forkable artefact: the markdown source is at `docs/CHOP_AND_CHANGE_GUIDE.md` in the cianfhoghlaim monorepo. Treat it as a worked example of how to write a chop-and-change guide for any open-source monorepo.*
