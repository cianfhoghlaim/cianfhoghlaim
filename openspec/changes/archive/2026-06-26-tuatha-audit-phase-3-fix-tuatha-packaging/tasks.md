# Tasks: Round 11 Phase 11 (tuatha Phase 3) — Fix tuatha packaging issue + add 5 missing `__init__.py` + fix 3 wrong import names + add `fix-pth.sh`

## Pre-flight

- [x] Confirmed `sruth/tuatha/__init__.py` does NOT exist (the umbrella package is missing)
- [x] Confirmed `from tuath.api.main import app` (conftest:8, wrong import name) fails: `ModuleNotFoundError: No module named 'tuath'`
- [x] Confirmed `import tuath` (basic) fails: `ModuleNotFoundError: No module named 'tuath'`
- [x] Confirmed `import tuatha` (correct import name, matching the dir) also fails: no .pth exists in venv for tuatha
- [x] Confirmed 3 sub-packages in `pyproject.toml` lack `__init__.py`: `api/`, `agents/`, `cocoindex_flows/`
- [x] Confirmed `from cocoindex_flows.transforms.celtic_multilingual import ...` fails: `ModuleNotFoundError: No module named 'cocoindex_flows.transforms.celtic_multilingual'` (PEP 420 namespace packages can't contain sub-packages)
- [x] Confirmed the other 9 sub-packages listed in `pyproject.toml` all have `__init__.py`: `dlt_sources`, `dagster_assets`, `knowledge_graph`, `storage`, `asset_generation`, `dlt_utils`, `fibo_generation`, `demo`, `tests`
- [x] Confirmed 3 test files use wrong import name `tuath` (no 'a'): `tests/conftest.py:8`, `tests/test_graphiti_integration.py:8`, `tests/test_hybrid_search.py:8`
- [x] Confirmed the croilar fix pattern from commit `e9e0fc7d2` (per README #3): create umbrella `__init__.py` + change `[tool.hatch.build.targets.wheel]` to `.packages = ["."]` + post-install `fix-pth.sh`
- [x] Confirmed `sruth/tuatha/cocoindex_flows/mythology_embedding.py` (7339 bytes) is real cocoindex transform_flow code, NOT a stub
- [x] Confirmed `sruth/tuatha/cocoindex_flows/transforms/celtic_multilingual.py` is real language-detection code

## Implementation

- [x] Create openspec change directory `openspec/changes/tuatha-audit-phase-3-fix-tuatha-packaging/`
- [x] Write `proposal.md` (done)
- [x] Write `tasks.md` (this file)
- [x] Write `specs/tuatha-platform/spec.md` delta with 1 ADDED Requirement (no-missing-package-init-py-in-tuatha)
- [x] Run `openspec validate tuatha-audit-phase-3-fix-tuatha-packaging --strict` (must pass before commit)
- [x] Create `sruth/tuatha/__init__.py` — 14-line docstring (canonical package marker, matching `croilar/__init__.py` pattern)
- [x] Create empty `sruth/tuatha/api/__init__.py` (1-line content)
- [x] Create empty `sruth/tuatha/agents/__init__.py` (1-line content)
- [x] Create empty `sruth/tuatha/cocoindex_flows/__init__.py` (1-line content)
- [x] Create empty `sruth/tuatha/cocoindex_flows/transforms/__init__.py` (1-line content)
- [x] Modify `sruth/tuatha/pyproject.toml` — change `[tool.hatch.build.targets.wheel].packages` from explicit list to `packages = ["."]` (matching croilar pattern)
- [x] Create `sruth/tuatha/scripts/fix-pth.sh` — 64-line bash script (mirrors `croilar/scripts/fix-pth.sh` pattern)
- [x] Run `bash sruth/tuatha/scripts/fix-pth.sh` to rewrite the `.pth` file in the venv
- [x] Verify post-state: `import tuatha` returns OK
- [x] Verify post-state: `from tuatha.api.main import app` returns OK
- [x] Verify post-state: `from tuatha.cocoindex_flows.transforms.celtic_multilingual import detect_celtic_language` returns OK
- [x] Fix `sruth/tuatha/tests/conftest.py:8`: `from tuath.api.main import app` → `from tuatha.api.main import app`
- [x] Fix `sruth/tuatha/tests/test_graphiti_integration.py:8`: `from tuath.knowledge_graph.graphiti import` → `from tuatha.knowledge_graph.graphiti import`
- [x] Fix `sruth/tuatha/tests/test_hybrid_search.py:8`: `from tuath.knowledge_graph import` → `from tuatha.knowledge_graph import`
- [x] Update `sruth/tuatha/README.md` "Known issues" table — add 2 RESOLVED rows: umbrella packaging fix + 3 missing __init__.py
- [x] Verify post-state: `ls sruth/tuatha/__init__.py sruth/tuatha/api/__init__.py sruth/tuatha/agents/__init__.py sruth/tuatha/cocoindex_flows/__init__.py sruth/tuatha/cocoindex_flows/transforms/__init__.py sruth/tuatha/scripts/fix-pth.sh` shows all 6 files
- [x] Run `mise run lint:skills` (123/123 pass)

## Commit + push

- [ ] Stage only files for this phase: 6 new files (5 __init__.py + 1 fix-pth.sh) + 4 modifications (pyproject.toml + 3 test files + README.md) + 3 openspec files
- [ ] **Do NOT stage**: pre-existing in-flight work in `.agents/skills/`, `.infisical.env`, `infrastructure/AGENTS.md`, ROOT `pyproject.toml`, `sruth/oideachais/notebooks/dashboards/education/all_nations.py`, `sruth/oideachais/celtic/duchas.py`, `sruth/oideachais/subjects/subjects/*`, `spaces/data-engineering`, `infrastructure/komodo/*`, `infrastructure/stacks/monitoring/*`, `openspec/changes/add-open{chamber,claw}-*`, `infrastructure/stacks/open{chamber,claw}/`, `.venv/lib/python3.13/site-packages/_editable_impl_tuath.pth` (the .pth file is gitignored environment config — generated locally)
- [ ] Commit 1: `refactor(tuatha): round 11 phase 11 (tuatha phase 3) — fix tuatha packaging issue + 5 missing __init__.py + 3 wrong import names + add fix-pth.sh`
- [ ] Push to `q3-2026-oideachais-consolidation`
- [ ] Run `openspec archive tuatha-audit-phase-3-fix-tuatha-packaging --yes`
- [ ] Commit 2: `docs(openspec): apply Phase 11 spec delta to tuatha-platform`
- [ ] Push to `q3-2026-oideachais-consolidation`
- [ ] Verify `git status` shows "up to date with origin"

## Post-archive

- [ ] Verify `openspec/changes/tuatha-audit-phase-3-fix-tuatha-packaging/` is now in `archive/` subdirectory
- [ ] Confirm spec delta is now part of `openspec/specs/tuatha-platform/spec.md`
- [ ] Confirm 18 changes archived in Round 11 (10 oideachais + 5 meaisinfhoghlaim + 3 tuatha)