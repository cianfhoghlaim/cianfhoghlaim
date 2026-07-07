# Tasks: 2026-06-28-browserbase-phase-3-decisions

> Implementation tasks for the Phase 3 research output. Each task
> traces to a prompt and an output `.md` file under
> `openspec/research/2026-06-28-browserbase-credit-program/phase-3/`.

## 1. Phase 3 prompts (12 × 75 = 900 credits)

### British Isles (8)
- [ ] 1.1 S01 curriculumonline.ie — `S01-curriculumonline.md`
- [ ] 1.2 S02 examinations.ie — `S02-examinations.md`
- [ ] 1.3 S03 ncca.ie — `S03-ncca.md`
- [ ] 1.4 S04 gov.uk — `S04-govuk.md`
- [ ] 1.5 S05 education.gov.scot — `S05-education-scot.md`
- [ ] 1.6 S06 gov.wales — `S06-gov-wales.md`
- [ ] 1.7 S07 education-ni.gov.uk — `S07-education-ni.md`
- [ ] 1.8 S08 gov.im — `S08-gov-im.md`

### Crown dependencies (2)
- [ ] 1.9 S09 gov.je — `S09-gov-je.md`
- [ ] 1.10 S10 gov.gg — `S10-gov-gg.md`

### Reference (2)
- [ ] 1.11 S11 zotero.org — `S11-zotero.md`
- [ ] 1.12 S12 arxiv.org — `S12-arxiv.md`

## 2. Spec deltas

- [ ] 2.1 ADDED Requirements to `oideachais-pipeline/spec.md` (URL cascades)
- [ ] 2.2 ADDED Requirements to `celtic-asset-generation/spec.md` (BAML extraction strategies per site)

## 3. Validation gate

- [ ] 3.1 `openspec validate 2026-06-28-browserbase-phase-3-decisions --strict`
- [ ] 3.2 All 7 sections present in each `phase-3/*.md` output
- [ ] 3.3 Each Requirement has ≥1 Scenario block

## 4. Persistent accessors (post-research)

- [ ] 4.1 Generate WebMCP for the top-3 highest-frequency sites
  (examinations.ie, ncca.ie, curriculumonline.ie) — saves ~75 credits per future scrape
