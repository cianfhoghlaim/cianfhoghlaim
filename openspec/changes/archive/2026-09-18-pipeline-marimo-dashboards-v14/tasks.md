# Tasks: pipeline-marimo-dashboards-v14

> Cross-batch Marimo v14 dashboard contract.
> Absorbs `2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1` (0/93).

## 1. Ireland + England dashboards refactor (from ireland-england-dashboards-refactor-v1)

- [ ] **M1.1** Apply R1 + R2 + R3 + R4 refactors + P1 + P3 + P4 + P5 + P6 features to `notebooks/19_ireland_biep.py`
- [ ] **M1.2** Apply same to `notebooks/20_ireland_biep_england.py`
- [ ] **M1.3** Apply same to `notebooks/21_ireland_biep_scotland.py`
- [ ] **M1.4** Apply same to `notebooks/22_ireland_biep_wales.py`
- [ ] **M1.5** Apply same to `notebooks/26_england_biep.py`
- [ ] **M1.6** Apply same to `notebooks/27_england_biep_combined.py`
- [ ] **M1.7** Apply R1 + R3 + P3 to `notebooks/10_biep_pipeline_lakehouse_01.py`
- [ ] **M1.8** Apply R1 + R3 + P3 to `notebooks/11_biep_pipeline_lakehouse_02.py` (through 17)
- [ ] **M1.9** Consolidate ~1,650 LOC into 3 reusable helper modules
  - [ ] `_helpers/tabs.py` (P1: `mo.ui.tabs`)
  - [ ] `_helpers/ai.py` (P4: `mo.ui.chat` + `mo.ai.llm`)
  - [ ] `_helpers/dual_mode.py` (P6: dual-mode CLI)

## 2. Add the 6 high-impact marimo v14 features

- [ ] **M2.1** P1: `mo.ui.tabs` (replaces single-cell accordions)
- [ ] **M2.2** P2: `mo.status.progress_bar` (replaces ad-hoc progress divs)
- [ ] **M2.3** P3: `mo.ui.anywidget` (for cross-package composability)
- [ ] **M2.4** P4: `mo.ui.chat` + `mo.ai.llm` (for inline LLM cells)
- [ ] **M2.5** P5: `@app.cell(column=N)` + `layout_file` (for multi-column layouts)
- [ ] **M2.6** P6: dual-mode CLI (for headless operators)

## 3. Verification

- [ ] Run `openspec validate pipeline-marimo-dashboards-v14 --strict` — pass
- [ ] Run `mis run marimo:lint` — pass

## Verification

```bash
cd ~/dev/cianchosaint-laim 2>/dev/null || cd ~/dev/cianchoshlaim
openspec validate pipeline-marimo-dashboards-v14 --strict
```
