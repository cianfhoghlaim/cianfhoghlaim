# Official Media Pipeline — British Isles Government Source Enrichment from Instagram Exports

## Why

Three converging pressures motivate this change:

1. **The deplatforming thesis.** Major social platforms (Meta, X, TikTok) have
   progressively tightened user experience, ramped mandated advertising, eroded
   chronological feeds, and used engagement-maximising algorithms that are
   documented to harm adolescent mental health (the same regulatory lineage
   we cite in `leabharlann/gemini_deep_research/technology/regulating_big_tech_in_british_isles.pdf`).
   For British Isles users — especially those in regulated data environments
   (NHS, TCI, courts, civil service) — the response is to **build a
   side-loadable, user-owned, ad-free alternative** that pulls official
   British Isles information (government, political, public services,
   universities, emergency services, intelligence agencies) directly from
   the organisations' own websites and fediverse presences.

2. **The Instagram-export-to-pipeline gap.** A user exporting their Instagram
   data receives a JSON bundle (the format Instagram ships via
   `Settings → Accounts Center → Your information and permissions → Download`
   — `connections/followers_and_following/{followers_1,following}.json`,
   `apps_and_websites_off_of_instagram/`, `logged_information/`,
   `ads_information/`, `media/posts/YYYYMM/`). Today this export is
   effectively write-only: once downloaded, nothing in the `cianfhoghlaim`
   stack ingests it. We close that gap with a DLT source that:
   - parses the export's documented schema,
   - filters out the noise (friends, family, celebrities) via a curated
     allowlist + BAML fallback,
   - identifies the **canonical official source** for each surviving
     British-Isles-government-adjacent account (Wikipedia, Companies House,
     CRO Ireland, Mastodon webfinger, Bluesky xrpc),
   - writes the enriched records to the lakehouse where every other
     `oideachais` asset (Dagster, marimo, TanStack, Cognee) can already
     consume them.

3. **The user-supplied seed data.** The user has asked us to research and
   seed the allowlist with the real public Instagram handles of the
   following British Isles bodies (verified by Wikipedia / press release,
   not derived from any private data):

   | Category | Initial seeds |
   |:--|:--|
   | Intelligence & signals | `mi5official`, `mi6official`, `gchq`, `hmgcc` |
   | Universities | University of Galway, Queen's University Belfast, University College London (and Irish Russell Group equivalents) |
   | Political parties | Fianna Fáil, Fine Gael, Irish Labour, Liberal Democrats, Plaid Cymru, SNP, plus Northern Ireland parties (Alliance, DUP, UUP, SDLP, Sinn Féin) |
   | Jurisdictions (PR 1) | Ireland (gov.ie departments + agencies), Northern Ireland (nidirect + departments), England (gov.uk departments + emergency services) |

   The first PR covers **3 jurisdictions** (IE, NI, EN) per the locked
   decision; SCT/WLS/IoM/JEY/GGY are PR 2.

## What Changes

### 1. New openspec capability `official-media-pipeline`

A new DLT source + Dagster asset group that:

- Parses Instagram export JSON in the format Meta ships
  (`connections/followers_and_following/*.json`,
  `logged_information/recent_searches/*.json`, `ads_information/ads_and_topics/*.json`).
- Filters profiles via a two-stage filter (curated allowlist + BAML
  fallback gated on a cheap regex heuristic).
- Resolves the canonical official source for each surviving profile
  through 4 parallel lookups: Wikipedia REST summary endpoint,
  Companies House (UK) / CRO (ROI), Mastodon webfinger, Bluesky public
  xrpc.
- Writes the enriched records to `oideachais.official_media.{candidates,
  resolved_sources, posts, embeddings}` (DuckLake), groups them under
  `group_name="official_media"`, and registers a monthly ScheduleDefinition.

The first iteration runs **completely offline** when `USE_LOCAL_SCRAPES=true`
(set automatically in CI), against a fixture derived from publicly-known
handles. Live `Wikipedia` / `Companies House` / `CRO` / `webfinger` /
`xrpc` lookups are gated on `USE_LIVE_LOOKUPS=true` and rate-limited
through the existing `shared.http` client with a 1-req/sec budget per
authority.

### 2. New openspec capability `official-media-fediverse`

Independent of (1), a small library at
`sruth/oideachais/dlt_sources/official_media/fediverse.py` that:

- Resolves a Mastodon handle (`@user@host`) via webfinger
  (`https://host/.well-known/webfinger?resource=acct:user@host`).
- Resolves a Bluesky DID via the public
  `public.api.bsky.app/xrpc/app.bsky.actor.searchActors?q=...` endpoint.
- Returns a normalised `{platform, handle, url, verified, follower_count,
  resolved_at, source}` dict.

The library is pure (no Dagster dependency) so it can be reused by the
side-loadable-app phase.

### 3. New openspec capability `official-media-marimo`

A new marimo notebook at
`sruth/oideachais/notebooks/dashboards/official_media.py` plus a TanStack Start
route at `sruth/oideachais/web/src/routes/official-media/index.tsx` plus a
Cognee dataset `oideachais_official_media` with the edge types:

- `ig_profile → official_website` (via Wikipedia or override)
- `ig_profile → fediverse_account` (via webfinger)
- `ig_profile → companies_house_entity` (for UK public bodies registered
  as companies)
- `official_website → wikipedia_article` (bi-directional)

Both UI surfaces carry a **strong-stance footer card** reading
*"Why we built this →"* linking back to this proposal. The card is
non-dismissible in PR 1; a future PR may add a dismiss toggle.

### 4. Domain rename — `intelligence` → `official_media`

Per the locked decision, the domain is named **`official_media`** (not
`intelligence`) to reflect the broader scope (government + political +
public services + universities + emergency services + intelligence
agencies). The first entries in the new domain are the 4 intelligence
agencies; PR 2 will fill out universities, parties, and the rest of the
jurisdictions.

## What's Out of Scope (deferred to Phase 2)

- The side-loadable PWA / iOS / Android app that consumes the resolved
  sources. Tracked in the follow-up issues filed by this change.
- The Instagram → Mastodon bridge (i.e. using the resolved
  Mastodon/Bluesky handle to migrate the user's follow list). Tracked
  separately.
- Public-body re-identification (Crown bodies vs. registered companies)
  beyond what Companies House / CRO can answer from the canonical
  search.

## Anti-Patterns Honoured

Per `AGENTS.md` "Critical Agent Protocols":

- **No absolute namespaces** — the new DLT modules use relative imports.
- **Respect the cache** — `USE_LOCAL_SCRAPES=true` is the default; live
  Wikipedia/Companies House/Bluesky are gated on
  `USE_LIVE_LOOKUPS=true` (a separate flag from
  `USE_LOCAL_SCRAPES`).
- **No hand-edited `.env`** — no new secrets are introduced; we reuse
  `FIRECRAWL_API_KEY`, `BROWSERBASE_API_KEY`, `OPENCODE_GO_API_KEY`
  (all already managed by Infisical).
- **BAML must call `client LiteLLM`** — the new
  `ClassifyOfficialMedia` function uses the existing `extract` alias.
- **All assets group-tagged `official_media`** — matches the convention
  in `sruth/oideachais/dagster_defs/assets/site_analysis/extract.py`.
- **Every DLT resource declares `write_disposition` and `primary_key`** —
  matches the `site_analysis_source()` pattern.

## Validation Gates

1. `openspec validate official-media-pipeline --strict` — must pass
   before any code lands.
2. `mise turbo lint && mise turbo typecheck` — must pass.
3. `uv run pytest -q sruth/oideachais/tests/official_media/` — must pass with
   `USE_LOCAL_SCRAPES=true` and `USE_LIVE_LOOKUPS=false`.
4. `uv run dagster dev -m data_platform.dagster_defs.definitions` —
   confirm 5 new assets appear in the UI under group `official_media`.
5. `uv run marimo edit notebooks/dashboards/official_media.py` —
   confirm dashboard renders against the seed allowlist.
6. `openspec archive official-media-pipeline --yes` after deployment.

## Cross-References

- [`sruth/oideachais/AGENTS.md`](../../sruth/oideachais/AGENTS.md) — the quadrant
  routing for adding a new domain
- [`openspec/AGENTS.md`](../AGENTS.md) — the openspec workflow
- [`sruth/oideachais/sources.yaml`](../../sruth/oideachais/sources.yaml) — the
  canonical source registry we are extending
- [`sruth/oideachais/dlt_sources/domains/site_analysis.py`](../../sruth/oideachais/dlt_sources/domains/site_analysis.py)
  — the closest-pattern existing source (iterates `sources.yaml` + emits
  DLT rows + groups as Dagster asset)
- [`sruth/oideachais/site_analysis/extractor.py`](../../sruth/oideachais/site_analysis/extractor.py)
  — the firecrawl/browserbase JSON-RPC pattern we mirror for the
  source-resolver
- [`sruth/oideachais/agents/adk/callbacks/citation_callbacks.py:287-332`](../../sruth/oideachais/agents/adk/callbacks/citation_callbacks.py)
  — the existing gov-domain classification we extend with the
  `official_media` bucket
- [`.agents/skills/dlt/SKILL.md`](../../../.agents/skills/dlt/SKILL.md) —
  the master DLT router
- [`.agents/skills/dagster/SKILL.md`](../../../.agents/skills/dagster/SKILL.md)
  — the Dagster asset patterns
- [`.agents/skills/baml/SKILL.md`](../../../.agents/skills/baml/SKILL.md) —
  the BAML schema pattern for `ClassifyOfficialMedia`

## Related Historical Research

- `leabharlann/gemini_deep_research/technology/regulating_big_tech_in_british_isles.pdf`
  — UK / Ireland regulatory landscape; motivates the "British
  DeepMind first" closed-source policy that this change respects.
- `leabharlann/gemini_deep_research/technology/us_tech_infiltration_and_uk_ireland_defense.pdf`
  — the threat model for US-only and PRC-origin closed-source providers;
  informs the strong-stance dashboard footer.
