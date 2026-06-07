# Tasks: leaving-cert-2026

## Phase 1: Infrastructure & Configuration

- [ ] Add MiniMax M3 model entry to `oideachais/data_platform/dlt_utils/foinse/litellm_config.yaml`
- [ ] Create `cianfhoghlaim-leaving-cert` R2 bucket (provisioned via the existing R2 binding in `infrastructure/stacks/infrastructure/r2/`)
- [ ] Create `cianfhoghlaim_leaving_cert` MotherDuck database for public-read aggregate tables
- [ ] Add `leaving-cert-pipeline.yaml` GitHub Action workflow for daily build
- [ ] Add `leaving-cert-pipeline.yaml` Forgejo workflow mirror

## Phase 2: Pipeline — Per-Subject Asset Graph

For each subject (Maths → Irish → Biology → French → History → Business → Construction):

- [ ] Create `oideachais/data_platform/dagster_defs/assets/leaving_cert/{subject}_assets.py`
  - Partition keys: `subject × paper × year × language`
  - Assets: `{subject}_syllabus_pdf`, `{subject}_syllabus_extracted`, `{subject}_past_papers`, `{subject}_past_papers_extracted`, `{subject}_marking_schemes`, `{subject}_marking_schemes_extracted`, `{subject}_topic_frequency`, `{subject}_study_prioritisation`, `{subject}_exam_layout_tips`, `{subject}_portal_page_payload`
- [ ] Create `oideachais/data_platform/dagster_defs/sensors/leaving_cert_annual.py` — watching R2 for new syllabi + SEC for new exam papers
- [ ] Add jobs to `definitions.py` for `leaving_cert_maths`, `leaving_cert_irish`, etc.

## Phase 3: Pipeline — BAML Schemas

- [ ] Create `leaving_cert_syllabus_extraction.baml` — extracts topics, learning outcomes, weightings
- [ ] Create `leaving_cert_past_paper_extraction.baml` — extracts questions, marks, topics, years
- [ ] Create `leaving_cert_marking_scheme_extraction.baml` — extracts PCLM patterns, common mistakes, allocations
- [ ] Run `baml-cli generate` to rebuild the BAML client

## Phase 4: Per-Subject Portal Pages

- [ ] Create shared leaving-cert layout component at `oideachais/web/apps/web/src/routes/leaving-cert/layout.tsx`
  - Reuse: Card, Tabs, Table, Accordion, Badge, Progress, Separator, Skeleton from `@croilar/ui`
- [ ] Create shared leaving-cert data layer at `oideachais/web/apps/web/src/server/leaving-cert.ts`
  - MotherDuck Dives, R2 signed URLs, DuckDB/MotherDuck tables
- [ ] Create per-subject route files:
  - `oideachais/web/apps/web/src/routes/leaving-cert/mathematics.tsx`
  - `oideachais/web/apps/web/src/routes/leaving-cert/irish.tsx`
  - `oideachais/web/apps/web/src/routes/leaving-cert/biology.tsx`
  - `oideachais/web/apps/web/src/routes/leaving-cert/french.tsx`
  - `oideachais/web/apps/web/src/routes/leaving-cert/history.tsx`
  - `oideachais/web/apps/web/src/routes/leaving-cert/business.tsx`
  - `oideachais/web/apps/web/src/routes/leaving-cert/construction-studies.tsx`
  - Each page: Hero + SyllabusAnalysis + PastExamTable + MarkingSchemePatterns + TopicPrioritisation + ExamLayoutTips + CopilotKit chat + PDF viewer tab

## Phase 5: R2 PDF Seeding

- [ ] Write `infrastructure/scripts/seed-leaving-cert-r2.sh` — one-shot upload of existing SEC/NCCA PDFs to R2
- [ ] R2 layout: `syllabus/{subject}/{year}.pdf`, `exam-papers/{subject}/{year}-paper-{n}.pdf`, `marking-schemes/{subject}/{year}-paper-{n}-marking.pdf`

## Phase 6: CopilotKit + MiniMax M3 Agent

- [ ] Create a MiniMax M3 CopilotKit agent for the leaving-cert chat panel
- [ ] Tools: `get_syllabus_topics(subject)`, `get_past_exam_table(subject, year, paper)`, `get_marking_scheme_patterns(subject)`, `get_topic_prioritisation(subject)`, `get_exam_layout_tips(subject)`, `open_pdf(bucket, key)`
- [ ] Wire agent into the per-subject page's CopilotKit chat panel

## Phase 7: Validation & Launch

- [ ] Run `bun run ccc:index` to index the new files
- [ ] Run `openspec validate leaving-cert-2026 --strict`
- [ ] Verify MotherDuck Dives render on the per-subject page
- [ ] Verify R2 signed URLs serve PDFs
- [ ] Verify CopilotKit chat responds with per-subject analysis
- [ ] Manual review pass: Irish-language content on the Irish page, Cluastuiscint audio links
- [ ] Soft launch to beta students (Wed 3 Jun → D-5)
- [ ] Public launch (Mon 8 Jun → D-0 for most subjects; Fri 5 Jun for Maths)
