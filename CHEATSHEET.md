# CHEATSHEET — Cianfhoghlaim 60-Second Quick Path

> **The 60-second quick path for operators + agents.** For the
> 10-minute onboarding see [`NEW-USER-ONBOARDING.md`](NEW-USER-ONBOARDING.md).
> For the canonical agent instructions see [`AGENTS.md`](AGENTS.md).
> For the V6 era plan see [`openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md`](openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md).

## V6 era + 10 follow-on Steps quick path (2026-09-01)

```bash
# 1. Open the consolidated app
cd web/apps/cianfhoghlaim-nua && bun install && bun dev

# 2. Verify the BAML client is reachable
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.GenerateStudyPlanAssets)"

# 3. Run the integration test suite
uv run pytest tests/test_adk_subject_actions.py tests/test_phase7_certificate_pipeline.py -v

# 4. Validate all openspec changes
for d in openspec/changes/2026-09-01-*/; do
  uv run openspec validate "$(basename $d)" --strict
done

# 5. Try the 7-stage certificate pipeline
uv run python -c "
import asyncio
from meaisinfhoghlaim.certificate import run_certificate_pipeline
result = asyncio.run(run_certificate_pipeline(
    learner_id='learner-1', learner_name='Test',
    subject_slug='chemistry', stage='scoil_sinsearach',
    lo_codes=['LC-CHEM-LO-3.1'],
    ncca_policy_pdfs=[('SC-L1-L2-Programme-Statement.pdf', 'Sample NCCA text...')],
))
print(f'PNG: {result.png_bytes[:8]!r}')
"

# 6. Test the per-jurisdiction extraction
uv run python -c "
from baml_client.baml_client.sync_client import b
fns = ['GenerateStudyPlanAssets', 'GenerateOralStudyPlan', 'ExtractNCCAPolicyCriteria', 'ExtractComputerScienceLearningGraph', 'ExtractEnglandSubjectSpec', 'ExtractWelshSubjectSpec', 'ExtractScottishGaelicSubjectSpec', 'ExtractManxSubjectSpec', 'ExtractWelshSubjectSpec']
for f in fns:
    if hasattr(b, f): print(f'  ✓ {f}')
"
```

## 19 priority openspec changes (V6 era + 10 follow-on Steps)

### Phases 0-9 (the original v6 era)

| Phase | Change | Key surface |
|--:|--|--|
| 0 | `2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/` | Phase 1 umbrella |
| 0.1 | `2026-09-01-{bonneagar,tuatha,ciancheiltis,ciandlithe,cianchosaint,gemini-hackathon}-sister-umbrella-mirror-v1/` | 6 sister-side mirrors |
| 0.5 | `2026-09-01-baml-regeneration-blocker-v1/` | BAML regenerated |
| 1 | `2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/` | Study-plan + oral-plan BAML |
| 2 | `2026-09-01-cianfhoghlaim-nua-a2ui-catalog-v1/` | 11-component A2UI v0.9 catalog |
| 3 | `2026-09-01-cianfhoghlaim-nua-web-consolidation-v1/` | 5 apps → 1 consolidated |
| 3.2 | `2026-09-01-cianfhoghlaim-nua-web-consolidation-completion-v1/` | 7 skeleton files + 4 Hono mounts + 5 archives |
| 4 | `2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1/` | 5 NCCE PDFs + 48 equivalencies |
| 5 | (partial) FTS index added | `ireland_lc_factory.py:139-141` |
| 6 | `2026-09-01-cianfhoghlaim-nua-oral-study-plans-v1/` | Pipecat + TTS router |
| 7 | `2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1/` | 7-stage certificate pipeline |
| 8 | `2026-09-01-sister-side-mirrors-v1/` | 6 sister-side transfers |
| 9 | `2026-09-01-gcp-opt-in-completion-v1/` | 6 GCP mirror stacks enabled |
| 10 | `2026-09-01-v7-from-the-ground-up-v1/` (DEFERRED) | V7 architecture goals |

### Steps 0-9 (the 10 follow-on Steps)

| Step | Change | What |
|--:|--|--|
| S0 | `2026-09-01-cianfhoghlaim-nua-web-consolidation-completion-v1/` | 7 missing skeleton files + 4 Hono mounts + 5 archives |
| S1 | `2026-09-01-dlt-path-drift-fix-v1/` | 137-file DLT path bulk update |
| S2 | `2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1/` | 8 NCCA-adjacent + physics BAML + 16 Convex + 2 early-years Apps |
| S3 | `2026-09-01-firecrawl-england-source-discovery-v1/` | 7 official England sources + DLT scaffold |
| S4-S8 | `2026-09-01-cianfhoghlaim-nua-5-jurisdiction-completion-v1/` | EN + WL + NI + IM + SC BAML |
| S9 | `2026-09-01-cianfhoghlaim-nua-v7-vernaculars-v1/` | 7 vernacular language BAMLs |

## Top 10 priority mise tasks

| Task | Purpose |
|:--|:--|
| `cic:stack-doctor` | Validate all 94 stacks against the 6-file GOLD_STANDARD |
| `stack-doctor:strict` | `cic:stack-doctor` + grammar checks |
| `lint:mcp-runtime` | Verify every enabled MCP has a corresponding smoke test |
| `deploy:full` | 10-phase full-stack deploy orchestrator |
| `preflight:arm-oci` | Mandatory safety gate for iac:bootstrap / iac:plan |
| `baml:generate` | Regenerate the baml_client from baml_src |
| `baml:check` | Validate BAML source files parse cleanly |
| `lint:registry` | 0 hardcoded model strings |
| `lint:skills` | All 167 skills pass |
| `openspec:validate-all` | All 19+ openspec changes pass strict validation |

## Top 10 priority skills (V6 era + 10 Steps)

| Skill | Purpose |
|:--|:--|
| `cianfhoghlaim-nua-v6-era` | The 5-pillar pattern + the 19 openspec changes + the 8 British Isles subnations + the 7 vernaculars |
| `openspec` | The canonical openspec workflow |
| `baml` | The BAML v0.226.2 schema + the Phase 0.5 regeneration |
| `cocoindex` | The CocoIndex factory pattern + the NCCE flow |
| `agentic-frontend-frameworks` | The A2UI v0.9 catalog + the 11 components |
| `agent-fleet-orchestration` | The 12-agent fleet + the ADK 2 integration |
| `agent-memory-systems` | The 5 memory backends + the Phase 7 certificate |
| `agent-observability` | The 5 observability pillars |
| `infrastructure-stacks` | The 6 GCP mirror stacks + the 89 self-hosted stacks |
| `mise` | The mise task catalog |
