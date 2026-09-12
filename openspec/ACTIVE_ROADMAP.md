# Active Openspec Roadmap

**Status (2026-09-13):** 58 active openspec changes (37 dated + 21 metadata/pipeline bundles). Generated from `ls openspec/changes/` (excluding `archive/`).

> Refresh note: this file was previously stale (last update 2026-07-29 claimed "0 active changes"). This refresh captures the post-2026-08-13 reality: 5 critical production blockers, ~12 in-flight changes, ~15 narrative/pipeline bundles, plus 21 dated feature changes.

## Active changes by severity

### 🔴 Critical (blocks production / public mesh)

| Change | Why critical |
|:--|:--|
| `2026-08-13-biep-v3-orchestration-activation-v1` | Litellm crash-looping + 17 GGUF weights missing locally. Every BAML `ExtractSyllabusDiagram` is dark. |
| `2026-08-13-bonneagar-infra-remediation-v3` | `storage-infrastructure.toml:14` references `cliste/bonneagar`; Komodo resource-sync silently failing. |
| `2026-08-13-edge-routing-and-offline-site-remediation-v1` | 10 of 17 `*.cianfhoghlaim.ie` hostnames unreachable (litellm, langfuse, vikunja, n8n, glance, changedetection, paperless, infisical, openchamber, komodo). |
| `2026-08-13-web-monorepo-consolidation-and-agent-integration-v1` | Phase A-B 0/17 — `web/packages/ui-kit/` not merged. |
| `2026-09-06-adk-gemini-deep-research-control-plane-v1` | In untracked state on cianfhoghlaim + tuatha + bonneagar. Cannot `openspec validate` until committed. |

### 🟡 In-flight (actively being worked)

| Change | Status |
|:--|:--|
| `2026-08-10-ocr-vision-activation-v1` | ~80% done; 3 tasks deferred to `2026-08-13-ocr-vision-activation-completion-v1` (still throws `NotImplementedError`). |
| `2026-08-13-biep-v3-jurisdiction-sensor-jobs-v1` | Code DONE (`orchestration/sensors/jobs.py:1-76`); only `--strict` + archive pending. |
| `2026-08-13-knowledge-graph-population-activation-v1` | 5 stage dirs exist as shells; only `cross_stage_cognify/defs.yaml` registered. |
| `2026-09-06-ciancheiltis-v1` | PR0.1-PR0.9 done; 6 jurisdictions shipped. |
| `2026-09-12-youtube-source-playlist-support-and-agent-training-v1` | Partial: 4 files modified, 1 created. |

### 🟠 Narrative / bundling (proposal-only)

| Change | Type |
|:--|:--|
| `2026-08-18-mega-3-roadmap-v1` | 4-Stage Plane modernization meta-plan (-25,799 LOC target) |
| `2026-08-18-mega-3-fast-follow-v1` | 18 sub-tasks |
| `2026-08-26-mega-3a-baml-and-adk-v1` | -9,700 LOC dedup target |
| `2026-09-30-mega-3b-cocoindex-and-copilotkit-v1` | -5,000 LOC net target |
| `2026-12-XX-mega-3d-baml-quality-v1` | Future-dated (impossible); work shipped via `b0099a6bd`. **Needs rename + archive.** |
| `2026-08-19-readme-restore-depth-and-cross-link-to-leabharlaim-v1` | 0/19 sections; current README is 1020 lines. |
| `2026-10-06-spacetimedb-babylonjs-adr-clean-break-v1` | Retire Babylon.js from `tuatha-ui`. |
| `cianchosaint-handoff-v1` | Sister-repo handoff umbrella |
| `openspec-1-11-migration` | 1.11 doctor + config.yaml |
| `pipeline-baml-extraction`, `pipeline-biep-v3-orchestration`, `pipeline-british-isles-synthesis-v1`, `pipeline-celtic-corpus`, `pipeline-chemistry-v1`, `pipeline-computer_science-v1`, `pipeline-english-v1`, `pipeline-gaeilge-v1`, `pipeline-geography-v1`, `pipeline-knowledge-graph-indexing`, `pipeline-lakehouse-data-plane`, `pipeline-marimo-dashboards-v14`, `pipeline-mathematics-v1`, `pipeline-naming-taxonomy`, `pipeline-ocr-vision-activation`, `pipeline-web-monorepo` | 16 per-pipeline bundling changes |
| `skills-refresh-2026-09`, `spec-content-overlap-resolution`, `spec-registry-dedup` | 3 housekeeping changes |

### 🟢 Forward seed (no current activity)

| Change | Scope |
|:--|:--|
| `2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1` | Token-plan APIs + LC doc pipeline + edge TLS remediation |
| `2026-08-10-baml-extraction-completion-v1` | LC5/6 un-stubbing (T1.1 done; T1.2, T2.1-T2.3 open) |
| `2026-08-10-copilotkit-action-wiring-v1` | Real CopilotKit handlers (0/17 tasks) |
| `2026-08-10-england-biiep-pipeline-v1` | England BIEP pipeline |
| `2026-08-10-knowledge-graph-population-v1` | KG 5-stage cognify (0/23; Cognee not running) |
| `2026-08-10-marimo-v14-cascading-effects-verification-v1` | v14 cascading drift verifier (0/446) |
| `2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1` | 6 v14 features |
| `2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1` | Collapse 10 sync dashboards → 1 |
| `2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1` | Collapse 36 Tier-3 dashboards → 6 |
| `2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1` | Fix 7 stale count claims + INDEXING_AND_COGNITION.md drift |
| `2026-08-13-guides-yml-repair-and-docs-integrations-index-v1` | 18 dead paths in `.cocoindex_code/guides.yml` |
| `2026-08-13-ocr-vision-activation-completion-v1` | Close OCR vision activation (stubs→real) |
| `2026-08-13-skill-consolidation-and-extension-v1` | Add OCR/VLM section to skills (0/36) |
| `2026-08-15-lakehouse-unified-data-plane-v1` | Consolidate 5 graph DB stacks (0/8 phases) |
| `2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1` | 6-day Unsloth integration (0/67) |
| `2026-09-01-celtic-mythology-content-system-v1` | 6 Celtic pantheons + Irish dynastic history (0/40; spec dir not created) |
| `2026-09-08-ogham-celtic-stones-pipeline-v1` | CISP + Megalithic Portal (spec dir not created) |
| `2026-09-15-celtic-language-corpus-extension-v1` | Scots + Cornish + Manx + Corpas CC + CEFR (spec dirs not created) |
| `2026-09-22-geospatial-british-isles-twin-v1` | OS MasterMap + Tailte Éireann + Met Office + Met Éireann (spec dir not created) |
| `2026-09-29-familiar-dynamic-nft-system-v1` | Convex tables + Anam Progression Agent (spec dir not created) |

## Open issues (carry-forward from 2026-07-29)

| # | Title | Status |
|:--|:--|:--|
| 81 | Pre-deploy: replace placeholder SHA256 image digests in openclaw + openchamber | help wanted |
| 82 | Pre-deploy: arm1-oci headroom check before openclaw + openchamber | help wanted |
| 107 | Follow up T1 stack docs and secrets env generation | open |
| 139 | Force-push remaining 33 feat/* branches after Claude Code trailer rewrite | open |
| 140 | BIEP v3 extension: Scotland/Wales/NI + Crown Dependencies | enhancement |
| 141 | Complete remaining MODEL_REGISTRY migrations | open |
| 142 | Activate BAML TypeScript codegen | open |
| 143 | Build web UI control panel | open |
| 144 | Pydantic dedup rollout | open |
| 145 | CocoIndex factory rollout | open |
| 146 | Refactor 10 per-jurisdiction Dagster assets | open |

## Recommended next wave

Highest leverage: **archive the 5 fully-implemented critical-path changes** (`2026-08-10-ocr-vision-activation-v1`, `2026-08-13-biep-v3-jurisdiction-sensor-jobs-v1`, `2026-09-06-ciancheiltis-v1` PR0.1-PR0.9, plus rename + archive `2026-12-XX-mega-3d-baml-quality-v1`). Then address Tier 2 production blockers (litellm/GGUF, Traefik, namespace, ΔE math).
