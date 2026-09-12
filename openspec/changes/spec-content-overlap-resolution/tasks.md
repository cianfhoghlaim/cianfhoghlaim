## 1. Pair 1: oideachais-pipeline ↔ cianfhoghlaim-pipeline

- [x] 1.1 Read oideachais-pipeline's 14 requirements and identify unique items (verify: `rg -c "^### Requirement" openspec/specs/oideachais-pipeline/spec.md` returns 14)
- [x] 1.2 ADD the 14-th requirement's MD5 hash invariant + the cross-reference stub Requirement to cianfhoghlaim-pipeline; verify both new requirements have ≥1 scenario each
- [x] 1.3 REMOVE all 14 requirements from oideachais-pipeline; verify by `openspec validate spec-content-overlap-resolution --strict`

## 2. Pair 2: oideachais-baml-schemas ↔ cianfhoghlaim-baml-schemas

- [x] 2.1 Read oideachais-baml-schemas's 12 requirements and identify unique items (verify: `rg -c "^### Requirement" openspec/specs/oideachais-baml-schemas/spec.md` returns 12)
- [x] 2.2 ADD the 8-jurisdiction BAML compilation + the 50-error resolution to cianfhoghlaim-baml-schemas
- [x] 2.3 REMOVE all 12 requirements from oideachais-baml-schemas

## 3. Pair 3: oideachais-marimo-dashboards ↔ cianfhoghlaim-marimo-dashboards

- [x] 3.1 Read oideachais-marimo-dashboards's 5 requirements and identify unique items
- [x] 3.2 ADD the 5 BAML+CocoIndex tutorial notebooks to cianfhoghlaim-marimo-dashboards
- [x] 3.3 REMOVE all 5 requirements from oideachais-marimo-dashboards

## 4. Pair 4: oideachais-cognify-knowledge-graph ↔ cianfhoghlaim-cognify-knowledge-graph

- [x] 4.1 Read oideachais-cognify-knowledge-graph's 4 requirements; Req 1 is already a retirement marker
- [x] 4.2 ADD the Leabharlann sub-corpora + cross-archive edge ownership to cianfhoghlaim-cognify-knowledge-graph
- [x] 4.3 REMOVE Reqs 2-4 from oideachais-cognify-knowledge-graph (keep Req 1 as the retirement marker)

## 5. Pair 5: british-isles-education-pipeline-v3 ↔ british-isles-education-pipeline

- [x] 5.1 Read british-isles-education-pipeline-v3's 21 requirements and identify unique items (verify: `rg -c "^### Requirement" openspec/specs/british-isles-education-pipeline-v3/spec.md` returns 21)
- [x] 5.2 ADD the 5-milestone + 4-cadence + OCR webhook convention to british-isles-education-pipeline
- [x] 5.3 REMOVE all 21 requirements from british-isles-education-pipeline-v3 (full retirement, not reduction)

## 6. Verification

- [x] 6.1 Run `openspec validate spec-content-overlap-resolution --strict`; verify it passes (verified 2026-09-12)
- [ ] 6.2 After archive, run `openspec list --specs`; verify the count drops from 102 to 97 (5 capabilities retired)
- [ ] 6.3 Run `openspec validate --all --strict`; verify the previously-30-failing TBD-Purpose warnings now drop (each retired spec had a TBD Purpose placeholder)