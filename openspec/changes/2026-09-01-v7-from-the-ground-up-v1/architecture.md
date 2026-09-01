# V7 From-The-Ground-Up — Architecture Goals (DEFERRED)

Per the 2026-09-01-v7-from-the-ground-up-v1 change (Phase 10 of
the cianfhoghlaim-nua v6 era plan, **DEFERRED** per operator
direction 2026-09-01).

## 5-pillar pattern

```
BAML → Convex → A2UI → Hono → React
```

| Pillar | v6 era role | v7 future direction |
|--------|-------------|---------------------|
| **BAML** | Single source of truth for LLM extraction (Phase 0.5) | Same; expand the qpack template + learning_graph + oral_study_plan + certificate to 50+ canonical functions |
| **Convex** | Reactive schema with 12 tables (Phase 1 §3.1 + Phase 4) | Same; consolidate 3 Convex deployments to 1 |
| **A2UI** | 11-component v0.9 catalog (Phase 2) | Same; lift the 3 existing components (MarimoEmbed + CiPdfLibraryPanel + TranslationToggle) into the package |
| **Hono** | 4 + N per-subject action routes (Phase 1 §3.2) | Same; collapse the 39 per-subject Hono routes into 4 generic + per-subject resources |
| **React** | 5 web apps collapsed to `cianfhoghlaim-nua/` (Phase 3) | Same; archive the 4 old apps to `web/apps/_archive/` (per Phase 3 §5) |

## 3 REDUCED ops surface

1. **Drop `_legacy/`** — the 8 deprecated BAML/web/component files
   archived per `2026-08-13-ocr-vision-activation-completion-v1` and
   similar changes. v7 deletes them outright.

2. **Drop `web/packages/`** — the 7 web packages (`api-client` +
   `auth` + `contracts` + `db` + `i18n` + `ui` + `ui-kit`) are
   consolidated into the `cianfhoghlaim-nua/` app per Phase 3. v7
   deletes the 7 package directories.

3. **Consolidate web to 1 app** — the 5 web apps
   (`cianfhoghlaim` + `oideachais` + `oideachais-dashboard` +
   `tuatha` + `croilar-web`) are collapsed into `cianfhoghlaim-nua/`
   per Phase 3. v7 keeps only the 1 consolidated app.

## 4 quality bar improvements

1. **BAML client regenerated** (Phase 0.5 commit `21c0c33d8`) —
   the 343+ BAML 0.226.2 parser errors are fixed; the baml_client
   is regeneratable; all Phase 1 BAML functions are reachable.
2. **Convex schema with 5 new tables** (Phase 1 §3.1 + Phase 4 §5) —
   `study_plans` + `quest_packs` + `oral_study_plans` +
   `formative_attempts` + `audio_segments` + `ncce_learning_graphs`.
3. **A2UI 11-component catalog** (Phase 2) — `web/packages/a2ui/`
   with `createCatalog()` + 11 components (StudyPlanCard +
   WeekTimeline + MilestoneBadge + ExamPaperCard +
   MarksBreakdownTable + KCWeightsBar + StageOverview + SubjectCard
   + MarimoEmbed + CiPdfLibraryPanel + TranslationToggle).
4. **BGE-M3 embedder canonical** — the canonical
   `BAAI/bge-m3` 1024-d embedder is used by all CocoIndex flows
   via `cocoindex_flows/_shared/_lifespan.py`.

## Deferred

The v7 rewrite is DEFERRED per operator direction. Reopen this
change when 4-6 weeks of Phase 1-9 usage has validated the
consolidated architecture as the right target.

---

*Last updated by build subagent at 2026-09-01.*