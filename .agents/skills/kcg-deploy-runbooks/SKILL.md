---
name: kcg-deploy-runbooks
description: The 5 deferred deploy plans from `openspec/plans/tangent_*` rewritten as KCG-anchored phased action plans — micro-credentials ledger (NFQ↔RQF), generative cross-lingual tutoring, automated OCR-based assessment, immersive flashcard + marimo content generation, and the policy simulator for temporal curriculum diff. Each runbook is grounded in the oideachais data platform (DLT + BAML + Dagster + Cognee), Pocket ID for identity, and the 3-tier KCG topology. Use when planning cross-border credential work, designing a BAML-grounded tutor, wiring OCR-based grading, generating cross-border flashcard corpora, building a policy diff simulator, or asking "how do we deploy tangent 1-5 against the actual monorepo?".
---

# KCG Deploy Runbooks

## When to use this skill

Use when you need to:

- "Plan a deploy of micro-credentials / micro-credential ledger"
- "Build a generative cross-lingual tutor (BAML + litellm + Cognee)"
- "Add OCR-based automated assessment to the curriculum pipeline"
- "Generate flashcards or marimo dashboards from NCCA / SEC papers"
- "Build a temporal policy diff simulator (DuckLake + BAML SpecDiff)"
- "Understand the 5 deferred roadmap tangents (formerly
  `openspec/plans/tangent_*`) in their post-restructure form"
- "Pick the right pattern for a credential, tutor, assessment,
  content, or policy system"

## Overview

The 5 deploy plans in this skill are the **post-restructure
counterparts of the 5 deferred roadmaps** that originally
lived as ~50-line research fragments under
`openspec/plans/tangent_1..5_*.md`. After the 2026-06-06
docs consolidation they were rewritten as **~250-line KCG-anchored
phased action plans** that name the actual data platform
assets, BAML extractors, Dagster asset groups, identity
provider, and infrastructure stack each plan depends on —
not abstract research wishlists.

The 5 plans cover orthogonal surfaces of the oideachais /
tuatha stack:

| # | Plan | Primary surface | Key KCG stack |
|:--|:--|:--|:--|
| 1 | **Micro-credentials & cross-border equivalence ledger** | Identity + credentials | DLT × 8 nations → DuckLake → MotherDuck; BAML `EquivalenceAssertion`; Pocket ID + `did:key`; W3C VCs |
| 2 | **Generative cross-lingual tutor** | Tutoring | BAML `TutorStep` + UCCIX-Llama / Gemini 2.5; litellm; Cognee cognify; LanceDB HNSW |
| 3 | **Automated assessment (OCR + grading)** | Assessment | OCR (Pylaia / PaddleOCR / dots.ocr) → BAML rubric → historical grade forecast via Cognee |
| 4 | **Immersive content (cross-border concept + flashcard + marimo)** | Content gen | NCCA / SQA / CCEA / DfE scrape → BAML `Concept` + `Flashcard` → Dagster `flashcard_assets` → marimo notebook |
| 5 | **Policy simulator (temporal curriculum diff)** | Policy + temporal KG | Append-only DuckLake; BAML `SpecDiff`; Cognee ripple; Graphiti bi-temporal |

Each plan is **self-contained**: it lists the quadrants it
touches, the source registries it ingests, the BAML schemas
it adds, the Dagster assets it materialises, the identity /
secret / observability wiring it requires, and a phased
action plan with exit criteria. All 5 plans **defer the
on-chain anchoring and x402 payment layer** to the tuatha
quadrant — the v1 surfaces are web / DLT / BAML / Cognee
only.

## The 5 phased action plans (canonical references)

| # | Plan | Reference | Phases |
|:--|:--|:--|:--|
| 1 | Micro-credentials & cross-border equivalence ledger | `references/01-micro-credentials.md` | 8 (source registry → DLT → BAML extractor × 2 → Cognee → Pocket ID + DID → VC issuance → wallet → pilot) |
| 2 | Generative cross-lingual tutor | `references/02-generative-tutoring.md` | 6 (BAML tutor schema → Cognee curriculum KG → litellm fallback chain → LanceDB index → tutor UI → evaluation) |
| 3 | Automated assessment (OCR + BAML grading) | `references/03-automated-assessment.md` | 6 (OCR backend selection → BAML rubric extractor → grading model → historical grade forecast → assessment UI → pilot) |
| 4 | Immersive content (flashcard + marimo synth) | `references/04-immersive-content.md` | 7 (cross-border concept KG → flashcard extractor → marimo generation → Dagster assets → spaced-repetition scheduler → student dashboard) |
| 5 | Policy simulator (temporal curriculum diff) | `references/05-policy-simulator.md` | 7 (append-only DuckLake → BAML `SpecDiff` → Cognee ripple → Graphiti bi-temporal → simulator UI → regulator view) |

Each reference carries:

- **§0 Why this plan** — replaces the original "Tangent N"
  framing with a technology-first deploy narrative
- **§1 Monorepo grounding** — table of `oideachais/`,
  `tuatha/`, `infrastructure/`, and skill assets the plan
  consumes
- **§2-N domain body** — BAML schemas, source registries,
  storage shape, identity layer, phased action plan
- **§N Risks and mitigations** — model drift, GDPR, trust
  model collapse, regulator contestation
- **§N+1 Out of scope (deferred)** — explicit deferral to
  the tuatha / crypteolas quadrant
- **§N+2 Cross-references** — back into the KCG skills
  (`baml`, `cognee`, `dlt`, `lancedb`, `dagster`,
  `kcg-bunchloch`, `secrets-management`)

## The common pattern (across all 5 plans)

All 5 plans share the same 4-stage pattern:

```
Source authorities (NCCA / SEC / DfE / SQA / Welsh Gov / CCEA / DfE NI)
    │
    ▼  (DLT)
DuckLake (Parquet on Garage S3, Postgres catalog) + MotherDuck (md:oideachais)
    │
    ▼  (BAML)
Typed curriculum objects (Concept / EquivalenceAssertion / TutorStep / SpecDiff / …)
    │
    ▼  (Cognee + Graphiti)
Knowledge graph (static) + bi-temporal layer (policies, exam papers)
    │
    ▼  (LanceDB HNSW)
Vector search (RAG) + retrieval-augmented tutor / wallet / simulator UI
```

The same pattern, with the same stack choices, is the basis
of the leabharlann PDF pipeline (`kcg-leabharlann-pipeline`)
and the Celtic asset generation pipeline
(`celtic-asset-generation`). The deploy plans are
**vertical slices** of the data platform applied to a
specific surface (credentials / tutor / assessment /
content / policy).

## The 3 deferred capabilities (consistent across all 5 plans)

| Capability | Owner | Reason for deferral |
|:--|:--|:--|
| **On-chain anchoring** (Solana, Ethereum) | `tuatha/crypteolas/` | Adds cost + regulatory risk; not needed for v1 closed pilot |
| **x402 micropayments** for paid verification | `tuatha/crypteolas/` | Phase 2 of the tuatha roadmap; v1 is free + web-wallet-only |
| **Mobile wallet (iOS / Android)** | `tuatha/` (the KMP bridge) | Web wallet is the v1 surface; iOS KMP bridge arrives with the Anam MMO |

These are **explicit** in every plan's "Out of scope"
section — they are not omissions, they are deferred by
design.

## Identity + secret + observability (the 3 cross-cutting concerns)

Every plan inherits these from the KCG platform:

- **Identity** — Pocket ID (deployed on `arm1-oci` via
  the `pangolin.private-resources.identity.*` stack). OIDC
  for the web; `did:key` (v1) / `did:web` (v2) for VCs.
- **Secrets** — Infisical (`dev-baile`) + Locket sidecars
  + mise directory hooks. The VC issuer key, the BAML
  model API keys, the OCR backend keys all live in
  Infisical; never in plain `.env` on disk.
- **Observability** — Langfuse (cognify traces, BAML
  client calls, OCR cost) + MLflow (BAML eval scores,
  grading-model accuracy) + Dagster (asset lineage,
  freshness, asset_check gates).

The plan-specific asset names live in the per-plan
reference; the wiring is identical across all 5.

## Phasing (the canonical 7-step pattern)

Every plan is staged as **0 → N**, with each phase carrying
an explicit exit criterion. The phasing is **not** a Gantt
chart — it's the **dependency graph** the implementation
must respect:

| Phase | Generic description | Example (plan 01) |
|:--|:--|:--|
| 0 | Source registry complete (8 nations × 5 kinds) | `oideachais/sources.yaml` populated; `openspec validate oideachais-pipeline` passes |
| 1 | DLT pipelines ingest the source authorities | `sec_examinations`, `ccea_ni_curriculum`, `dfe_england_national_curriculum` materialise in DuckLake |
| 2 | BAML extractor (v1, gold-set validated) | `EquivalenceAssertion` at 90% precision on a 50-paper gold set |
| 3 | BAML extractor (v2, scale-up) | `SkillAssertion` extracts 10,000 skill tags from SEC corpus |
| 4 | Knowledge graph (Cognee) | `cognee.search("ROI↔UK equivalence")` returns the matrix |
| 5 | Identity + secret wiring | Pocket ID + Locket + mise work end-to-end |
| 6 | Application surface | Student wallet / tutor UI / assessment UI / content dashboard / policy simulator |
| 7 | Pilot | 5 schools × 50 students × 200 VCs / tutor sessions / assessments |

The exact phase names and exit criteria are in each
plan's reference.

## Cross-references

- `.agents/skills/baml/SKILL.md` — the BAML extraction
  language and the `ExtractEn` / `ExtractEnStrong` clients
  every plan depends on
- `.agents/skills/dlt/SKILL.md` — DLT pipeline patterns
  for the 8 source registries
- `.agents/skills/dagster/SKILL.md` — Dagster asset /
  asset_check / sensor patterns
- `.agents/skills/cognee/SKILL.md` — the Cognee cognify
  pattern + 8 canonical edge types
- `.agents/skills/lancedb/SKILL.md` — LanceDB HNSW +
  FTS hybrid search for RAG
- `.agents/skills/celtic-asset-generation/SKILL.md` —
  the 5-stage Celtic pipeline that the plans are vertical
  slices of
- `.agents/skills/kcg-leabharlann-pipeline/SKILL.md` —
  the leabharlann PDF variant of the same 5-stage flow
- `.agents/skills/kcg-bunchloch/SKILL.md` — the 3-tier
  topology (where each plan's services run)
- `.agents/skills/secrets-management/SKILL.md` —
  Infisical + Locket for the VC issuer key
- `.agents/skills/better-auth/SKILL.md` — Pocket ID
  OIDC + DID layer for the identity surface
- `.agents/skills/agent-observability/SKILL.md` —
  Langfuse + MLflow for plan-specific eval + cost gates
- `oideachais/sources.yaml` — the 8-nation × 5-kind
  source registry
- `oideachais/baml_src/` — the BAML schemas the plans add
- `infrastructure/stacks/identity/` — the Pocket ID
  stack
- `tuatha/crypteolas/` — the deferred x402 / on-chain
  surface
- `openspec/specs/{curriculum-ingestion,bilingual-content,knowledge-graph}/` — the
  capability specs each plan implements
