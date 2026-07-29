# Tasks

## 1. Audit the 12 per-subject notebooks

- [x] Identify dead-code `status: invoked` dictionaries in the six `12_subject_study_tools/<subject>.py` notebooks.
- [x] Identify stale or wrong-argument `Generate<Subject>QuestPack` calls in the six `leaving_cert/<subject>.py` dashboards.
- [x] Confirm canonical generated signatures from `qpack_<subject>.baml` and `baml_client/baml_client/sync_client.py`.

## 2. Fix the six `12_subject_study_tools/` notebooks

- [x] Replace the fake `GenerateMathFormativeItem` state dict with a real `b.GenerateMathFormativeItem(...)` call.
- [x] Replace the fake `GenerateChemFormativeItem` state dict with a real `b.GenerateChemFormativeItem(...)` call.
- [x] Replace the fake `GenerateCompFormativeItem` state dict with a real `b.GenerateCompFormativeItem(...)` call.
- [x] Replace the fake `GenerateEnglFormativeItem` state dict with a real `b.GenerateEnglFormativeItem(...)` call.
- [x] Replace the fake `GenerateGaelFormativeItem` state dict with a real `b.GenerateGaelFormativeItem(...)` call.
- [x] Replace the fake `GenerateGeogFormativeItem` state dict with a real `b.GenerateGeogFormativeItem(...)` call.
- [x] Surface each result or error in the marimo output.

## 3. Fix the six `leaving_cert/` dashboards

- [x] Mathematics: replace `(topic, level, language, n_items)` with `(syllabus, past_papers, marking_schemes, level)`.
- [x] Chemistry: replace `(topic, level, language, n_items)` with `(syllabus, past_papers, marking_schemes, level)`.
- [x] Computer Science: replace `GenerateComputerScienceQuestPack(...)` with `GenerateCompQuestPack(syllabus=..., past_papers=..., marking_schemes=..., level=...)`.
- [x] English: replace `GenerateEnglishQuestPack(...)` with `GenerateEnglQuestPack(syllabus=..., past_papers=..., marking_schemes=..., level=...)`.
- [x] Gaeilge: replace `GenerateGaeilgeQuestPack(...)` with `GenerateGaelQuestPack(syllabus=..., past_papers=..., marking_schemes=..., level=...)`.
- [x] Geography: replace `GenerateGeographyQuestPack(...)` with `GenerateGeogQuestPack(syllabus=..., past_papers=..., marking_schemes=..., level=...)`.

## 4. Verify

- [x] AST-parse all 12 notebooks.
- [x] Check that the six study-tool notebooks no longer contain `status: invoked` placeholders.
- [x] Check that the six leaving_cert dashboards use generated qpack function names and the canonical 4-argument signature.
- [x] Run OpenSpec validation for this change.
- [ ] Run `baml:generate` / BAML codegen check if available in the branch (attempted; blocked by pre-existing BAML syntax/duplicate-function errors outside this change).
- [ ] Run the data-platform quality gates: `mise run lint && mise run py:typecheck && mise run turbo typecheck` (attempted; `mise run lint` fails on pre-existing lint errors in `spaces/` and legacy `tests/`; `mise run py:typecheck` fails because the task invokes `mypy` without targets; `mise run turbo typecheck` fails in `tuatha-ui` Vite/Rolldown type resolution).

## 5. Commit and push

- [ ] Stage only the 12 notebook files and this change directory (do not stage unrelated parallel-agent dirty state).
- [ ] Commit on `pick-4-biep-v1`.
- [ ] Push to `origin/pick-4-biep-v1`.
