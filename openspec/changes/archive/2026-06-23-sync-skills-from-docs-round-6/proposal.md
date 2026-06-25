# Change: sync-skills-from-docs-round-6

## Why

A sixth round of `docs/*` consolidation. The user listed 12
files (3,941 lines total) covering the `02-data-platform/`,
`03-agents/`, and `05-web/` directories. Five patterns emerge:

1. **Mostly redundant with just-expanded skills.**
   `data-architecture.md` (653), `LANGUAGE_ARCHITECTURE.md`
   (743, mis-titled — actually DuckLake content), `FRONTEND_STACK.md`
   (400, pre-consolidation), `frontend-stack.md` (438, post-
   consolidation), `IRISH_EDUCATION_PLATFORM_BLUEPRINT.md` (246,
   product vision document) — all overlap with skills just
   expanded in rounds 1-5 (`oideachas-pipeline`, `tanstack-start`,
   `celtic-language-ai`, `ducklake`, `lancedb`).

2. **New skills genuinely needed.** 4 new skills emerge:
   - `cross-domain-registry` — the `{nation}.{domain}.{entity}`
     contract for every DLT source / Dagster asset (no current
     skill)
   - `oideachais-storage` — the KCG storage mental model +
     Critical Constraints (write to DuckLake, read from
     MotherDuck, catalogue via Lakekeeper)
   - `frontend-topology` — the 5-surface cross-cutting map
     (sruth/oideachais/web, sruth/croilar/apps/web, sruth/croilar/apps/portal,
     sruth/tuatha/ui, marimo)
   - `ui-components` — the KCG component-library reference
     (shadcn/ui + Radix, dnd-kit exam builder, AG-UI protocol,
     Celtic MMO game UI, 3D asset pipeline, Celtic design
     language)

3. **Old doc, useful patterns.** `browser-automation.md` (125)
   was preserved from round 4 as a KCG landing page. The
   KCG decision tree + BAML `SiteAnalysis` flow + status
   table can now be absorbed into the `browser` skill and the
   doc deleted.

4. **Stale data architecture doc.** `DATA_ARCHITECTURE.md`
   (uppercase, 377 lines) describes a FalkorDB/Graphiti/Cognee
   stack that KCG no longer uses. The current canonical is
   `data-architecture.md` (lowercase, 653 lines, dated 2026-06-06).

## What Changes

### New skills (4)

- `.agents/skills/cross-domain-registry/SKILL.md` — the
  `{nation}.{domain}.{entity}` contract for every DLT source
  and Dagster asset. 8 nations × 5 domains × 7 kinds.
  Sole truth: `sruth/oideachais/sources.yaml`. Includes the
  `SourceFactory` pydantic validator, DuckLake / LanceDB /
  Cognee naming conventions, and the backwards-compat alias
  table.

- `.agents/skills/oideachais-storage/SKILL.md` — the KCG
  storage mental model. Writes → DuckLake (Parquet on Garage
  S3, Postgres catalog). Reads → MotherDuck (`md:oideachais`).
  Long-tail catalogue → Apache Iceberg via Lakekeeper.
  Change-watching → ChangeDetection.io on `arm1-oci`. Includes
  the Critical Constraints table (5 violations + consequences)
  and the destination factory pattern.

- `.agents/skills/frontend-topology/SKILL.md` — the 5-surface
  cross-cutting map. Auth per surface, data plane per surface,
  decision tree for "which front-end to use". Used by 5+
  deploy plans + `STATUS.md` + `tuatha-platform` skill.

- `.agents/skills/ui-components/SKILL.md` — the KCG
  component-library reference. shadcn/ui + Radix + Tailwind 4,
  dnd-kit exam builder, CopilotKit + AG-UI protocol, Tuatha
  game UI (Soul Level, Geasa, Map, NFT gallery), 3D asset
  pipeline, Celtic design language (green/amber/stone
  palette, Cinzel/Cormorant fonts, triskele icons).

### Skills expanded (3)

- `.agents/skills/oideachas-pipeline/SKILL.md` (existing,
  161 lines) — add the **Tripartite Data Landscape** (NCCA /
  SEC / Dept of Education), the **EducationalNode entity
  metamodel + 5 edge types**, the 5 BAML schema classes
  (PrimaryLearningOutcome, ScienceOutcome, MarkingPoint,
  RubricDescriptor, CircularMetadata), and the bilingual
  data strategy (unified concept node, dialect handling via
  `HAS_FORM`). Ignore the stale FalkorDB/Graphiti/Cognee
  content.

- `.agents/skills/browser/SKILL.md` (existing) — add a "KCG
  decision tree" section: 7-row "What is wired today" status
  table, BAML `SiteAnalysis` flow (the fingerprint mode at
  `sruth/oideachais/baml_src/site_analysis.baml`), 6-backend
  `sruth-browser` client enumeration, the 5-backend
  browser ladder.

- `.agents/skills/irish-edtech/SKILL.md` (existing, 344 lines)
  — add the **Product vision: Agentic Academy** section:
  Bardic grade hierarchy (Ollaire → Ollamh, 7 tiers), dual-
  token Pinginn (USDC) / Screpall (SBT) design, Optimistic
  Oracle (UMA) + EAS Merkle Root pattern, cycle-based
  curriculum (Mythological → Ulster → Fenian → Historical),
  Cló Gaelach / Punctum delens orthography, Gemini 3
  "Critic Agent Flow" + System 2 reasoning, T5Gemma-2
  innovations.

### Docs to delete (12 files)

- `docs/02-data-platform/DATA_ARCHITECTURE.md` (377) — stale
  (FalkorDB/Graphiti stack, no longer used)
- `docs/02-data-platform/data-architecture.md` (653) —
  referenced from the `oideachas-pipeline` skill
- `docs/02-data-platform/cross-domain-registry.md` (121) —
  promoted to the new `cross-domain-registry` skill
- `docs/02-data-platform/LANGUAGE_ARCHITECTURE.md` (743) —
  mis-titled; content is DuckLake architecture, not
  Celtic-language AI
- `docs/02-data-platform/STORAGE.md` (298) — promoted to
  the new `oideachais-storage` skill
- `docs/03-agents/browser-automation.md` (125) — KCG
  decision tree absorbed into the `browser` skill
- `docs/03-agents/IRISH_EDUCATION_PLATFORM_BLUEPRINT.md`
  (246) — product vision absorbed into the `irish-edtech`
  skill
- `docs/05-web/FRONTEND_STACK.md` (400) — pre-consolidation,
  superseded by the just-expanded `tanstack-start` skill
- `docs/05-web/frontend-topology.md` (130) — promoted to the
  new `frontend-topology` skill
- `docs/05-web/frontend-stack.md` (438) — post-consolidation,
  superseded by the just-expanded `tanstack-start` skill
- `docs/05-web/ui-components.md` (410) — promoted to the new
  `ui-components` skill

(Note: `data-architecture.md` lowercase is the **current
canonical**; `DATA_ARCHITECTURE.md` uppercase is **stale** and
will be deleted. The two are NOT a pre/post-consolidation pair
despite the frontmatter `supersedes:` field on the uppercase
doc — they have different content.)

## Impact

- **Affected specs (1)**: `oideachais-pipeline` adds 2 new
  requirements (Tripartite Data Landscape + Bilingual Data
  Strategy)
- **Affected code**: none. Skills are documentation.
- **Affected skills** (7 total): 4 new + 3 expanded

## Success criteria

- `openspec validate sync-skills-from-docs-round-6 --strict`
  passes
- The 4 new skills exist at
  `.agents/skills/{cross-domain-registry,oideachais-storage,
  frontend-topology,ui-components}/SKILL.md`
- The 3 expanded skills have new sections
- The 12 listed docs files are removed

## Rollback

Skills-only. Rollback = restore the 12 docs files from git.
No data, code, or runtime state is affected.
