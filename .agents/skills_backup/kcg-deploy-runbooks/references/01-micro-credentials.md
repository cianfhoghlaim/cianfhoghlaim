---
title: 'Deploy Plan 01 — Micro-Credentials & Cross-Border Equivalence Ledger'
domain: deploy-plan
status: draft
description: 'W3C Verifiable Credentials + DIDs for ROI↔UK NFQ↔RQF micro-credentials, built on the oideachais data platform, BAML extraction, and Pocket ID for identity.'
read_when:
  - 'planning cross-border credential work'
  - 'reviewing DLT sources for NCCA/SEC/CCEA/Ofqual/DfE'
supersedes: []
superseded_by: []
related_specs:
  - curriculum-ingestion
  - bilingual-content
  - knowledge-graph
related_apps:
  - sruth/cianfhoghlaim/web
  - sruth/cianfhoghlaim/dlt_sources/ireland
  - sruth/cianfhoghlaim/dlt_sources/uk
related_llm_stack:
  - 'BAML (structured extraction of marking schemes)'
  - 'litellm (BAML→Ollama/openai/anthropic routing)'
  - 'cognee (knowledge graph of learning outcomes)'
truth: sole
last_touched: 2026-06-13
---

# Deploy Plan 01 — Micro-Credentials & Cross-Border Equivalence Ledger

## 0. Why this plan

Replace the original Tangent 1 framing (which leaned on political
endorsement and named parties) with a technology-first deploy plan that
grounds the micro-credentials work in the actual monorepo. The goal is
a **decentralised credentialing ledger** that maps Irish NFQ levels and
UK RQF levels into verifiable micro-credentials, allowing students to
own, share, and migrate their academic record across the UCAS↔CAO
boundary. None of this requires political alignment; it requires
**correct ingestion of curriculum specs**, **BAML-structured extraction
of learning outcomes**, and a **verifiable credential issuer** wired to
the existing infrastructure.

## 1. Monorepo grounding

| Asset | Path | Use |
|:--|:--|:--|
| Quadrant | `sruth/cianfhoghlaim/` | Data platform (DLT, Dagster, BAML, knowledge graph) |
| Quadrant | `sruth/tuatha/` | Crypto layer (Solana, x402 micropayments) — *deferred for v1* |
| Quadrant | `infrastructure/` | Pocket ID (OIDC), Pangolin (routing), Komodo (deploy) |
| Skill | `.agents/skills/baml/SKILL.md` | BAML extraction patterns |
| Skill | `.agents/skills/dlt/SKILL.md` | DLT pipeline design |
| Skill | `.agents/skills/lancedb/SKILL.md` | Vector storage of outcome embeddings |
| Skill | `.agents/skills/cognee/SKILL.md` | Knowledge graph of learning outcomes |

The full 5-quadrant topology is in `docs/00-core/CLAUDE.md` §QUADRANT_MAP.

## 2. Equivalence matrix (data, not opinion)

The first deliverable is a **canonical equivalence matrix** between
NFQ (Ireland) and RQF (UK). It is *not* a static lookup table — it is
a versioned, auditable dataset that follows the same ingestion path as
any other DLT source.

### 2.1. DLT sources to ingest

The 8 source registries already declared in `sruth/cianfhoghlaim/sources.yaml`:

- `ncca_junior_cycle_specs`     — ROI Junior Cycle
- `ncca_leaving_cert_specs`     — ROI Leaving Certificate
- `sec_examinations`            — State Examinations Commission papers
- `ccea_ni_curriculum`          — NI Council for Curriculum, Examinations & Assessment
- `dfe_england_national_curriculum` — England DfE
- `sqa_scotland_curriculum_for_excellence`
- `welsh_gov_curriculum_for_wales`
- `dcls_uk_statutory_assessments`    — Crown Dependencies (IoM, Jersey, Guernsey)

Each source yields a `CurriculumSpec` row with:

```
{ nation, level, qualification, subject, learning_outcome_id, description, source_url, last_updated, source_version }
```

### 2.2. The mapping table (BAML-extracted)

For each pair `(ROI_<level>, UK_<level>)` we extract a BAML-typed
`EquivalenceAssertion`:

```baml
class EquivalenceAssertion {
  nfq_level int
  rqf_level int
  jurisdiction_roi string          // "ROI" | "NI" | "UK-England" | ...
  jurisdiction_uk string
  qualification_roi string        // "Junior Cycle" | "Leaving Cert" | ...
  qualification_uk string         // "GCSE" | "AS-Level" | "A-Level" | ...
  confidence float                // 0..1 — cosine similarity of outcome embeddings
  evidence_url string[]
  valid_from date
  valid_to date?
}
```

The BAML prompt is grounded in the **NFQ↔RQF correspondence
publications** (currently the UK ENIC-NARIC framework). We do NOT
hardcode political preferences.

### 2.3. Storage

Writes go to **DuckLake** (`sruth/cianfhoghlaim/dlt_utils/destinations.py:create_ducklake_destination`).
Reads go to **MotherDuck** (managed DuckDB). The reasoning is in
`docs/02-data-platform/storage-mental-model.md`.

The equivalence matrix lives in `motherduck.cianfhoghlaim_equivalence.equivalence_assertion`.

## 3. Granular skill extraction

Replace the "mark scheme" abstraction with **BAML-extracted micro-credential
assertions** over the SEC exam-paper corpus. For each paper:

1. DLT pipeline `sec_examinations` ingests the paper + marking scheme.
2. BAML extracts per-question skill tags:
   ```baml
   class SkillAssertion {
     paper_id string
     question_id string
     skills string[]                  // e.g. ["data-analysis", "calculus", "financial-mathematics"]
     bloom_level string               // "remember" | "understand" | "apply" | "analyse" | "evaluate" | "create"
     max_marks int
   }
   ```
3. Skill tags map to the equivalence matrix in §2.

Result: a paper that says "H1 in Leaving Cert Mathematics" becomes
`{ data-analysis: 0.85, calculus: 0.78, financial-mathematics: 0.62, ... }`
— a **fingerprint** that survives the cross-border translation.

## 4. Identity: Pocket ID + DIDs

Pocket ID (deployed on `arm1-oci` via the `pangolin.private-resources.identity.*` stack)
provides **OIDC** for the platform. We extend it with a **DID layer**:

| Layer | Purpose | Implementation |
|:--|:--|:--|
| OIDC | Web login | Pocket ID + PocketBase |
| DID | Verifiable credential subject | `did:key` for v1, `did:web` for v2 (anchored to `cianfhoghlaim.ie`) |
| VC issuance | Sign credentials | BAML-typed JWT over ES256K (`sruth/tuatha/sruth/crypteolas/` provides the signer) |

For v1 we use **`did:key`** (no ledger) because adding a blockchain
introduces cost and regulatory risk without changing the trust model
for a closed pilot. v2 with `did:web` is in `sruth/tuatha/codeolas/`.

## 5. Verifiable Credentials (VCs)

A credential is a BAML-typed `MicroCredential`:

```baml
class MicroCredential {
  id string                           // VC id
  issuer string                       // DID of the issuer (Pocket ID service DID)
  issuance_date date
  expiration_date date?
  subject_did string                  // student's DID
  credential_subject MicroCredentialSubject
  proof VerifiableProof
}

class MicroCredentialSubject {
  student_name string
  roi_qualification string?           // "Leaving Cert 2024" | null
  uk_qualification string?            // "A-Level 2024" | null
  nfq_level int?
  rqf_level int?
  micro_skills SkillAssertion[]
  equivalence_anchor string           // id of the EquivalenceAssertion used
}
```

The credential is signed with a service key held in Infisical
(`/sruth/cianfhoghlaim/credentials/issuer-key`) and validated client-side
via the `sruth/tuatha/sruth/crypteolas/` ES256K verifier.

## 6. The student wallet

A **TanStack Start** route at `sruth/cianfhoghlaim/web/routes/wallet.$studentId.tsx`
renders the wallet. It:

1. Authenticates via Pocket ID (OIDC).
2. Resolves the student's DID from the OIDC `sub` claim.
3. Fetches all VCs from MotherDuck (`cianfhoghlaim_credentials.micro_credential`).
4. Allows sharing via:
   - **QR code** (one-time, expiring, scan-to-verify)
   - **Direct link** with short-lived token
   - **PDF export** with embedded proof (for offline use)

## 7. UCAS↔CAO migration

For the cross-border use case, a student moving from ROI to UK (or
vice versa) submits their **VC bundle** to the receiving institution.
The bundle is verified against the platform's `EquivalenceAssertion`
table to produce a translated qualification record.

**v1 scope:** the translation is *advisory*. The receiving institution
still reviews. v2 (deferred) would integrate with UCAS and CAO APIs
directly.

## 8. Phased action plan

| Phase | Scope | Exit criteria | Where it lives |
|:--|:--|:--|:--|
| 0 | Source registry in `sruth/cianfhoghlaim/sources.yaml` complete (8 nations, 7 kinds) | `openspec validate cianfhoghlaim-pipeline` passes | `sruth/cianfhoghlaim/sources.yaml` |
| 1 | DLT pipelines for NCCA + DfE + CCEA + SQA + Welsh Gov | All 5 sources materialise in DuckLake | `sruth/cianfhoghlaim/dlt_sources/{ireland,uk}/` |
| 2 | BAML `EquivalenceAssertion` extractor | 90% precision on a 50-paper gold set | `sruth/cianfhoghlaim/baml_src/equivalence.baml` |
| 3 | BAML `SkillAssertion` extractor over SEC papers | 10,000 skill assertions extracted | `sruth/cianfhoghlaim/baml_src/skills.baml` |
| 4 | Knowledge graph (cognee) of learning outcomes | Graph queryable via `cognee.search()` | `sruth/cianfhoghlaim/cognee_integration/` |
| 5 | Pocket ID + DID layer | OIDC login works, `did:key` resolves | `infrastructure/stacks/identity/` |
| 6 | VC issuance + wallet UI | Student can issue + share a VC | `sruth/cianfhoghlaim/web/routes/wallet.*` |
| 7 | Pilot with 5 schools (3 ROI, 2 NI) | 50 students, 200 VCs issued | `infra/komodo/procedures/pilot-credentials.toml` |

## 9. Risks and mitigations

| Risk | Mitigation |
|:--|:--|
| BAML extraction drift on new spec releases | Quarterly re-evaluation set; `EquivalenceAssertion.valid_to` enforces freshness |
| Privacy / GDPR | All PII stays in Pocket ID; VCs carry only `did:` references; MotherDuck row-level access via Pangolin |
| Trust model collapse if issuer key leaks | Issuer key in Infisical + quarterly rotation; per-school delegated issuers in v2 |
| Cross-border mapping contested by regulators | The mapping is **advisory** in v1; we do not claim legal equivalence |

## 10. Out of scope (deferred)

- On-chain anchoring (Solana, Ethereum) — `sruth/tuatha/sruth/crypteolas/` is ready when needed
- x402 micropayments for paid verification — Phase 2 of the tuatha roadmap
- Mobile wallet (iOS/Android) — web wallet is the v1 surface

## 11. Cross-references

- `docs/00-core/CLAUDE.md` — 5-quadrant topology
- `docs/02-data-platform/STORAGE.md` — DuckLake writes / MotherDuck reads
- `docs/02-data-platform/storage-mental-model.md` — storage mental model
- `docs/02-data-platform/cross-domain-registry.md` — `sruth/cianfhoghlaim/sources.yaml`
- `docs/04-ai-ml/llm-stack-hierarchy.md` — BAML → litellm → Cognee ordering
- `docs/05-web/frontend-topology.md` — TanStack Start routes
- `openspec/specs/curriculum-ingestion/spec.md` — DLT patterns
- `openspec/specs/bilingual-content/spec.md` — Irish/English content
- `openspec/specs/knowledge-graph/spec.md` — outcome graph
- `.agents/skills/baml/SKILL.md` — BAML extraction cookbook
- `.agents/skills/cognee/SKILL.md` — knowledge graph patterns
- `.agents/skills/dlt/SKILL.md` — DLT pipeline design
- `.agents/skills/lancedb/SKILL.md` — outcome embeddings
