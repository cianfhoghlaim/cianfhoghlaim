# Tasks — Cianfhoghlaim-Nua 5-Jurisdiction Completion v1

> 3 sections, 7 tasks. All tasks PASSED before
> `openspec archive 2026-09-01-cianfhoghlaim-nua-5-jurisdiction-completion-v1 --yes`.

## Phase A — OpenSpec scaffolding (5 min)

- [x] **A.1** Author `proposal.md` + `tasks.md` + spec delta
- [x] **A.2** `uv run openspec validate 2026-09-01-cianfhoghlaim-nua-5-jurisdiction-completion-v1 --strict` exits 0

## Phase B — Author the 5 jurisdiction BAML files (§1, 5 tasks)

- [x] **B.1** `baml_src/british_isles/en/education/en_extraction.baml` (England: ExtractEnglandSubjectSpec)
- [x] **B.2** `baml_src/british_isles/wl/education/wl_extraction.baml` (Wales: ExtractWalesSubjectSpec + WelshMediumOverlay)
- [x] **B.3** `baml_src/british_isles/ni/education/ni_extraction.baml` (NI: ExtractNorthernIrelandSubjectSpec + GaeltachtOverlay)
- [x] **B.4** `baml_src/british_isles/im/education/im_extraction.baml` (IoM: ExtractIsleOfManSubjectSpec + ManxOverlay)
- [x] **B.5** `baml_src/british_isles/sc/education/sc_extraction.baml` (Scotland: ExtractScotlandSubjectSpec + ScottishGaelicOverlay)

## Phase C — Regenerate baml_client + spec delta (§2-§3, 2 tasks)

- [x] **C.1** `uv run baml-cli generate --from baml_src` — regenerated `baml_client/`
- [x] **C.2** Spec delta to `british-isles-education-pipeline` — 1 ADDED Requirement

---

*Last updated by build subagent at 2026-09-01.*