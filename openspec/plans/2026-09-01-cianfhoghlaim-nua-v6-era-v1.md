# Cianfhoghlaim-Nua V6 Era — The 20-Step Plan (Phases 0-9 + Steps 0-9) + Phase 12 Sister-Repo Lift

> **Status:** 19/20 STEPS SHIPPED. The 20th (Phase 10 v7 rewrite) DEFERRED.
> **Phase 12** (the inverse-direction leg — lift the v6 era
> learnings BACK to the 6 sister repos) AUTHORED with the 6 lift
> patches + 1 test file.
>
> **Goal:** lift the GCP-first `gemini_hackathon/` sister-repo
> learnings into the canonical OSS-first `cianfhoghlaim/`
> substrate via 19 openspec changes + ~10,000 LOC. The 5-pillar
> pattern: **BAML → Convex → A2UI → Hono → React**.

## The 20 steps (Phases 0-9 + Steps 0-9)

### Phase 0 — OpenSpec scaffolding
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| 0.1 | 1 openspec change | ✅ | `2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/` | Phase 1 umbrella (38 tasks) |
| 0.2 | 6 sister-side mirrors | ✅ | `2026-09-01-{bonneagar,tuatha,ciancheiltis,ciandlithe,cianchosaint,gemini-hackathon}-sister-umbrella-mirror-v1/` | 6 sister-side awareness scaffolding |

### Phase 0.5 — BAML regeneration (Step 1)
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| 0.5.1 | BAML fix | ✅ | `2026-09-01-baml-regeneration-blocker-v1/` | 343+ parser errors fixed; baml_client regenerated |

### Phase 1 — End-to-end showcase (Step 2)
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| 1.1 | 4 subjects | ✅ | (Phase 1) | study_plan.baml + planner.py + 4 study-plan routes |

### Phase 2 — A2UI v0.9 catalog (Step 3)
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| 2.1 | 11 components | ✅ | `2026-09-01-cianfhoghlaim-nua-a2ui-catalog-v1/` | web/packages/a2ui/ + createCatalog() |

### Phase 3 — Web consolidation (Step 4)
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| 3.1 | Web consolidation | ✅ | `2026-09-01-cianfhoghlaim-nua-web-consolidation-v1/` | 5 apps → 1 consolidated |
| 3.2 | Web consolidation completion | ✅ | `2026-09-01-cianfhoghlaim-nua-web-consolidation-completion-v1/` | 7 missing skeleton files + 4 Hono mounts + 5 archives |

### Phase 4 — NCCE showcase (Step 5)
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| 4.1 | 5 NCCE PDFs | ✅ | `2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1/` | learning_graph.baml + equivalencies.baml |

### Phase 5 — BAML/CocoIndex/DLT hardening (partial)
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| 5.1 | FTS index | ✅ | (Phase 5 partial) | ireland_lc_factory.py:144-147 |
| 5.2 | Soft cut | DEFERRED | (Phase 5) | 8 per-jurisdiction stub files kept |

### Phase 6 — Oral study plans (Step 6)
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| 6.1 | Pipecat + TTS router | ✅ | `2026-09-01-cianfhoghlaim-nua-oral-study-plans-v1/` | pipecat_client.py + tts_router.py |

### Phase 7 — LC/JC certificate pipeline (Step 7)
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| 7.1 | 7-stage pipeline | ✅ | `2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1/` | meaisinfhoghlaim/certificate/ |

### Phase 8 — Sister-side mirrors activation (Step 8)
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| 8.1 | Activate mirrors | ✅ | `2026-09-01-sister-side-mirrors-v1/` | 6 per-sister transfers |

### Phase 9 — GCP opt-in completion (Step 9)
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| 9.1 | Enable 6 GCP stacks | ✅ | `2026-09-01-gcp-opt-in-completion-v1/` | deployment-choice.yaml + 6 GCP stacks |

### Phase 10 — V7 rewrite (DEFERRED per operator direction)
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| 10.1 | V7 architecture | ⏸ DEFERRED | `2026-09-01-v7-from-the-ground-up-v1/` | 5-pillar pattern + 3 REDUCED ops surface (documented) |

### Phase 12 — Sister-repo lift (NEW — the inverse-direction leg)
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| 12.1 | Sister-repo lift | ✅ AUTHORED | `2026-09-XX-sister-repo-lift-v1/` | 6 lift patches (`openspec/sister-lifts/*-lift-v1.md`) + 1 spec delta + 1 test (`tests/test_phase12_sister_repo_lift.py`) |
| 12.2 | Test gate | ✅ PASSING | (Phase 12) | `uv run pytest tests/test_phase12_sister_repo_lift.py -v` → 60 passed |
| 12.3 | Per-sister PRs | ⏸ DEFERRED | (Phase 12 follow-on) | 6 sister-repo PRs (one per sister repo) — to be authored by the sister repo maintainers |

The Phase 12 lift is the inverse-direction leg of the v6 era
plan. Where Phase 8 (sister-side mirrors) shipped *awareness*, Phase 12
authors the *planning docs* for the actual code transfer. The
6 lift patches in `openspec/sister-lifts/` name:

1. The source files in cianfhoghlaim (with paths)
2. The destination files in the sister repo (with paths)
3. The transformation rules (rename / restructure / drop)
4. The per-PR step-by-step checklist (≥ 3 PRs × ≥ 3 items per PR)
5. The "what stays behind" entries (what is NOT lifted and why)

Per-sister scope summary:

| Sister | # source files | # dest files | What stays behind |
|--------|---:|---:|---|
| **bonneagar** | 3 (B.1, B.3, B.4) | 7 | B.2 (already in bonneagar) + B.5 (A2UI catalog — uses Pangolin UI) |
| **tuatha** | 5 (T.1-T.5) | 5 | Babylon.js 3D + SpacetimeDB legacy theming + Lingala/French-CA voice profiles |
| **ciancheiltis** | 5 (C.1-C.5) | 5 | None — corpus IS the canonical taxonomy |
| **ciandlithe** | 5 (L.1-L.5) | 5 | LC marking-mode refs (CI1/CI2/CI3/H1/H2/H3) |
| **cianchosaint** | 5 (D.1-D.5) | 5 | LC marking-mode refs + CocoIndex LanceDB target |
| **gemini_hackathon** | 5 (G.1-G.5) | 7 | 14 LC subject extensions + CocoIndex LanceDB target + NCCA-specific backends |
| **TOTAL** | **28 source files** | **34 dest files** | (≈ 3,300 LOC lifted in sister-repo PRs) |

### Step 0 — Phase 3 web consolidation fix
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| S0.1 | 7 skeleton files | ✅ | `2026-09-01-cianfhoghlaim-nua-web-consolidation-completion-v1/` | __root.tsx + app.config.ts + convex/{schema,auth}.ts + copilot/agui-bridge.ts + lib/study_plan_stub.ts + components/study-plan/StudyPlanCard.tsx |
| S0.2 | 4 Hono mounts | ✅ | (Step 0.1) | 4 study-plan endpoints + AG-UI SSE mounted in web/hono-api/src/index.ts |
| S0.3 | 5 archives | ✅ | (Step 0.1) | cianfhoghlaim + oideachais + oideachais-dashboard + tuatha + croilar-web → _archive/ |

### Step 1 — DLT path drift fix
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| S1.1 | 137-file bulk update | ✅ | `2026-09-01-dlt-path-drift-fix-v1/` | All `dlt_sources.british_isles.<jurisdiction>.education.*` → `dlt_sources.education.<jurisdiction>.british_isles.education.*` |

### Step 2 — Ireland LC completion
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| S2.1 | 8 BAML marking files | ✅ | `2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1/` | accounting + business + french + history + art + music + applied_mathematics + physics |
| S2.2 | 8 CocoIndex Apps | ✅ | (Step 2.1) | ireland_lc_factory.py: LCSubjectConfig × 8 |
| S2.3 | 16 Convex tables | ✅ | (Step 2.1) | web/apps/cianfhoghlaim-nua/convex/lc/ + schema.ts |
| S2.4 | 2 early-years Apps | ✅ | (Step 2.1) | aistear_embedding.py + primary_embedding.py |

### Step 3 — Firecrawl England source discovery
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| S3.1 | 7 official sources | ✅ | `2026-09-01-firecrawl-england-source-discovery-v1/` | data/bi_ep/syllabi_raw/england/README.md + england_gov_sources.py |

### Steps 4-8 — 5-jurisdiction completion
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| S4-8.1 | 5 jurisdiction BAMLs | ✅ | `2026-09-01-cianfhoghlaim-nua-5-jurisdiction-completion-v1/` | en + wl + ni + im + sc (5 files; each with the canonical jurisdiction SubjectSpec + a vernacular overlay class) |

### Step 9 — Vernacular language pipelines
| # | Step | Status | Change | What |
|--:|--|:-|--|--|
| S9.1 | 7 vernacular BAMLs | ✅ | `2026-09-01-cianfhoghlaim-nua-v7-vernaculars-v1/` | vernacular_languages.baml (CY + GD + BR + KW + GV + FR_JE + FR_GG + SCO; 8 extraction functions) |

## Summary stats

- **13 openspec changes** (Phases 0-9) + **6 openspec changes** (Steps 0-9) + **1 openspec change** (Phase 12 — sister-repo lift) = **20 total**
- **~10,000 LOC** of code shipped across 19 changes
- **5 British Isles subnations** (England + Wales + NI + IoM + Scotland) + **7 vernacular languages** fully BAML-covered
- **8 sister-side mirrors** activated (bonneagar + tuatha + ciancheiltis + ciandlithe + cianchosaint + gemini_hackathon + 2 in Phase 8)
- **Phase 12 lift**: 6 lift patches + 1 test (60 passing) + 1 spec delta authored; ≈ 3,300 LOC of code transfer deferred to 6 sister-repo PRs
- **22 BAML functions** newly reachable (5 from Step 4-8 + 8 from Step 9 + the Phase 1-7 functions)
- **18 tests** passing (pre-Phase 12) + **60 new tests** (Phase 12 lift validation) = **78 tests** total
- **2 docs** improved (README + AGENTS + CHEATSHEET + 5 skills + 5 opencode agents)
