# Tasks — Data Engineering Documentation and Refactor Roadmap

## Phase 0 — OpenSpec and capability registration (week 0)

- [ ] 1. Create `openspec/changes/data-engineering-documentation-and-refactor-roadmap/{proposal.md, tasks.md, specs/}` with the spec delta.
- [ ] 2. Add the new capability `data-engineering-pipeline-documentation` to `openspec/AGENTS.md` and `openspec/project.md`.
- [ ] 3. Validate: `openspec validate data-engineering-documentation-and-refactor-roadmap --strict`.

## Phase 1 — Land the docs (week 1)

- [ ] 4. Write `oideachais/STATUS.md` (single source of truth for BAML × dlt × Dagster × CocoIndex × Cognee coverage).
- [ ] 5. Write `oideachais/REFACTORING.md` (refactor backlog with `Status` per item, linking to features 1-4).
- [ ] 6. Write `oideachais/dlt_sources/uk/README.md` (per-nation × per-cycle coverage matrix).
- [ ] 7. Write `oideachais/dlt_sources/ireland/README.md` (Aistear/Primary/JC/SC/Tertiary matrix, highlights the primary.py + junior_cycle.py gap).
- [ ] 8. Rewrite `oideachais/cocoindex_flows/README.md` for the v0/v1 split.
- [ ] 9. Write `oideachais/dagster_defs/assets/README.md` (asset catalogue).
- [ ] 10. Write `baml_src/README.md` (BAML schema catalogue).
- [ ] 11. Write `oideachais/agents/adk/README.md` + `oideachais/agents/agno/README.md`.
- [ ] 12. Write `docs/06-infrastructure/leabharlann-stack-overview.md` (end-to-end stack diagram + description).
- [ ] 13. Re-validate: `openspec validate data-engineering-documentation-and-refactor-roadmap --strict`.
- [ ] 14. Git: `git pull --rebase`, `git add -A`, `git commit -m "docs(oideachais): STATUS + REFACTORING + per-area READMEs + stack overview"`, `git push`.
- [ ] 15. Run `openspec archive data-engineering-documentation-and-refactor-roadmap --yes` to move the change to `archive/`.

## Phase 2 — (Out of scope for this change, queued)

- [ ] 16. Feature 1: openspec change `primary-secondary-british-isles-dlt-baml` + 5 dlt sources + 5 Dagster assets + 5 BAML functions invoked. **Tracked in `oideachais/REFACTORING.md`**.
- [ ] 17. Feature 2: openspec change `cognee-falkordb-leabharlann` + 3 cognify assets + 1 cross-archive edges + 1 FastAPI route + 1 cron sensor. **Tracked in `oideachais/REFACTORING.md`**.
- [ ] 18. Feature 3: openspec change `lancedb-blob-storage-leabharlann` + new compose file + Komodo procedure + blob-mode CocoIndex. **Tracked in `oideachais/REFACTORING.md`**.
- [ ] 19. Feature 4: openspec change `leabharlann-full-stack-demo` + 1 demo Dagster asset + 1 Marimo notebook. **Tracked in `oideachais/REFACTORING.md`**.

## Total: 19 tasks, ~2 weeks for this change (Phases 0-1). Features 1-4 are separate openspec changes.
