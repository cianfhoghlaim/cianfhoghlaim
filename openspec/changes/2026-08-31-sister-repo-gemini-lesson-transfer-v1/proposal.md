# Change: Sister-repo gemini_hackathon Lesson Transfer v1

> **Status:** AUTHORED, ready for execution.
>
> **Phase 4 of 6** in the v5 refactor umbrella.
>
> **Anchor:** the gemini_hackathon GCP-first IaC refactor +
> Stackdriver AI Agent ADK instrumentation + Document AI OCR
> ensemble + AG-UI/A2UI/CopilotKit automatic UI generation
> patterns. Transferred to the 5 sister repos (bonneagar +
> tuatha + ciancheiltis + ciandlithe + cianchosaint), each with
> their own deeply-per-sister-repo customisation.

## Why

The gemini_hackathon repo implemented 6 GCP-first + ADK-2 +
AG-UI/A2UI/CopilotKit patterns over 2026-08-30 that cianfhoghlaim
should transfer to its 5 sister repos. Each sister repo gets a
deeply-per-sister-repo customisation (NOT a wholesale copy), per
the user's direction on 2026-08-31:

- **bonneagar** (the IaC substrate) — promotes the 6 GCP mirror
  stacks from Phase 3 to canonical location + adds the GCP-first
  documentation.
- **tuatha** (the British Isles Formative Assessment MMO) — gets
  the BAML extraction pipeline (Primary + UnslothGemma4 +
  VertexGemini35Flash) + Document AI for character data +
  AG-UI/A2UI/CopilotKit for per-persona dashboards.
- **ciancheiltis** (the Celtic-language corpus) — gets the
  Gemma 4 26B-A4B-vision path for the 6 Celtic languages +
  BGE-M3 embedder swap + Document AI for manuscript OCR.
- **ciandlithe** (the British-Isles OSINT legal-data platform) —
  gets Document AI for the OSINT legal-doc pipeline + the
  dossier-generator CopilotKit UI per the gemini_hackathon
  Stitch + `/api/stitch` pattern.
- **cianchosaint** (the British-Isles OSINT defence platform) —
  gets the OSINT defence pipeline + Cloud Run ADK + automatic
  UI generation via AG-UI per persona.

## What changes

### §1 — `2026-08-31-bonneagar-gcp-mirror-iac-promotion-v1`

The 6 GCP mirror stacks from Phase 3 (`bonneagar/stacks/gcp-*/`)
are promoted to canonical IaC surfaces. Documentation updated in
`bonneagar/AGENTS.md` to reference the GCP-first pattern + the
Stackdriver AI Agent ADK instrumentation.

### §2 — `2026-08-31-tuatha-google-adk-biep-extract-v1`

Transfers to `~/dev/tuatha/`:

- The Primary + UnslothGemma4 + VertexGemini35Flash BAML clients.
- Document AI for character data (replaces the qwen3-vl-8b path).
- AG-UI/A2UI/CopilotKit per-persona dashboards.
- ADK 2-stage coordinators (the per-subject quest-pack pattern).

### §3 — `2026-08-31-ciancheiltis-celtic-baml-gemma-v1`

Transfers to `~/dev/ciancheiltis/`:

- The 6 Celtic-language BAML extraction path lifted to
  gemma-4-26b-a4b (Irish priority: gaeilge + manx + cornish +
  breton + welsh + scottish gaelic).
- BGE-M3 embedder swap (the canonical cianfhoghlaim embedder).
- Document AI for manuscript OCR (the 6 Celtic-language DLT
  sources).

### §4 — `2026-08-31-ciandlithe-legal-doc-gcp-v1`

Transfers to `~/dev/ciandlithe/`:

- Document AI OCR-ensemble path-1 for the legal-doc pipeline.
- The OSINT legal-doc DLT source (BAILII + ICLR + CaseMine +
  Courts.ie + NICTS + scotcourts.gov.uk + judiciary.uk + Crown
  Dependencies + NHS Resolution + courtserve.net + HSE + GMC + WRC).
- The dossier-generator CopilotKit UI per the gemini_hackathon
  Stitch + `/api/stitch` pattern.

### §5 — `2026-08-31-cianchosaint-defence-osint-gcp-v1`

Transfers to `~/dev/cianchosaint/`:

- The OSINT defence DLT source (CSO Ireland + data.police.uk +
  gov.uk + MoD corporate reports + court judgments + NAO/C&AG
  reports + Public Inquiries + ISC/IPC/IPT reports).
- Cloud Run ADK 2-stage coordinators.
- AG-UI per-persona dashboards.

### §6 — Reciprocal sister-side mirrors

Each sister repo gets a per-PR reciprocal mirror at
`openspec/changes/2026-MM-DD-<sister>-<change-name>-mirror-v1/`,
following the existing pattern from the
`2026-09-XX-gemini-hackathon-sister-umbrella-mirror-v1/` change.

## Impact

- 5 sister-side sub-changes (1 per sister repo).
- 6 reciprocal mirrors.
- 0 breaking changes in cianfhoghlaim — the transfer is
  additive.

## Dependencies

- Phase 1 (`2026-08-31-cianfhoghlaim-v5-opencode-model-priority-v1`)
  — the opencode + model registry refactor.
- Phase 2 (`2026-08-31-baml-primary-alias-and-fallback-v1`) — the
  Primary alias + per-function fallback chain.
- Phase 3 (`2026-08-31-gcp-mirror-stacks-v1`) — the 6 GCP mirror
  stacks.
- Phase 5 (`2026-08-31-meaisinfhoghlaim-unsloth-priority-v1`) —
  the meaisinfhoghlaim Unsloth-prioritised refactor.

## Out of scope

- Wholesale file-level transfers (the user explicitly requested
  deeply-per-sister-repo customisation, NOT wholesale copies).
- Sister-repo PR creation in `~/dev/<sister>/` — this change
  authors the plan + the tasks; the actual PR creation is a
  follow-on change in each sister repo's openspec directory.

## Quality gates (must pass before archive)

```bash
mise run openspec:validate 2026-08-31-sister-repo-gemini-lesson-transfer-v1 --strict
mise run lint:registry          # 0 drift — MODEL_REGISTRY covers every model string
mise run lint:skills            # 66 skills pass
```

---

*Last updated by build subagent at 2026-08-31.*