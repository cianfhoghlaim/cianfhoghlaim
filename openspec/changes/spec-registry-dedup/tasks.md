## 1. Verified retirement-marker classification (executed this change)

- [x] 1.1 Confirm `oideachais-leabharlann` is a single-requirement retirement marker pointing at `cianfhoghlaim-leabharlann` (verify: `rg -c "^### Requirement" openspec/specs/oideachais-leabharlann/spec.md` returns `1` and the requirement text references `cianfhoghlaim-leabharlann`)
- [x] 1.2 Confirm `oideachais-cocoindex-v1-migration` is a single-requirement retirement marker pointing at `cianfhoghlaim-cocoindex-v1-migration` (verify: same as 1.1 for the cocoindex pair)
- [x] 1.3 Confirm `oideachais-university-deep-extraction` is a single-requirement retirement marker pointing at `cianfhoghlaim-university-deep-extraction` (verify: same as 1.1 for the university pair)
- [x] 1.4 Write the REMOVED delta for each of the 3 retirement markers; verify by `openspec validate spec-registry-dedup --strict` returning valid

## 2. Verified typos no longer exist (no change needed)

- [x] 2.1 Confirm `meaisinfoghlaim-ocr-htr` (typo) does NOT exist in `openspec/list --specs` (verify: `openspec list --specs --json | python3 -c "import sys,json; print('meaisinfoghlaim-ocr-htr' in [s['id'] for s in json.load(sys.stdin)['specs']])"` returns `False`)
- [x] 2.2 Confirm `ciandlithe-dlt-sources-carveout-v1` does NOT exist in `openspec/list --specs` (verify: same shape of check; returns `False`)

## 3. Deferred: real content-overlap investigation (follow-up work, not fabricated in this change)

- [ ] 3.1 `oideachais-pipeline` ↔ `cianfhoghlaim-pipeline`: for each of `oideachais-pipeline`'s 14 requirements (starting with "No legacy 972-LOC ie-namespace duplicate pairs remain"), check whether `cianfhoghlaim-pipeline` already states the same invariant; add to `cianfhoghlaim-pipeline` whichever requirements are missing, then convert `oideachais-pipeline` to a single-requirement retirement marker (do not delete outright — some of its requirements may record still-load-bearing invariants like "no duplicate files" that are not duplicated in `cianfhoghlaim-pipeline`)
- [ ] 3.2 `oideachais-baml-schemas` ↔ `cianfhoghlaim-baml-schemas`: same pattern — `oideachais-baml-schemas` is the shorter side (12 vs 19 requirements), so check for content only present on the oideachais side that should migrate to `cianfhoghlaim-baml-schemas` before retirement
- [ ] 3.3 `oideachais-marimo-dashboards` ↔ `cianfhoghlaim-marimo-dashboards`: same pattern — 5 vs 10 requirements
- [ ] 3.4 `oideachais-cognify-knowledge-graph` ↔ `cianfhoghlaim-cognify-knowledge-graph`: same pattern — 4 vs 9 requirements; the oideachais side is the shorter one, so check for content only there
- [ ] 3.5 `british-isles-education-pipeline` ↔ `british-isles-education-pipeline-v3`: the base spec has 1,688 lines (a lot of content) and `-v3` has 585 lines with thematic overlap (both have filesystem/language scanner domain requirements, both have BIEP v3 milestone content); needs a requirement-by-requirement diff to determine whether the base spec already absorbed v3 content in place (in which case `-v3` becomes a retirement marker like the 3 already retired this change) or whether `-v3` has genuinely distinct content to ADD to the base first
- [ ] 3.6 After 3.1-3.5 land, re-run `openspec validate --all --strict` and confirm the TBD-Purpose warning count drops by however many of these specs carried the placeholder

## 4. Verification

- [x] 4.1 Run `rg -l "oideachais-leabharlann\|oideachais-cocoindex-v1-migration\|oideachais-university-deep-extraction" --type-add 'spec:*.md' -tspec .` to enumerate cross-references that need updating after archive; verify the list and update each reference to point at the canonical successor (per task 1.2)
- [x] 4.2 Run `openspec validate spec-registry-dedup --strict`; verify it passes (verified 2026-09-12)
- [ ] 4.3 Run `openspec status spec-registry-dedup`; verify all 4 artifacts report done