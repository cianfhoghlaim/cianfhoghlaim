---
name: per-jurisdiction-education-pdf-ingestion
description: The 5-step pattern for ingesting official education system documentation for each of the 8 British Isles subnations (IE + EN + WL + NI + IM + JE + GG + SC) and 7 vernacular languages (Welsh + Scottish Gaelic + Breton + Cornish + Manx + Channel Islands French × 2 + Ulster Scots). Use when extending the BIEP pattern to a new jurisdiction, adding a new subject's PDF extraction, or wiring a new BAML extractor + DLT source + CocoIndex embedding + Convex table. The 5 steps are: (1) raw PDF source via Firecrawl MCP, (2) DLT source with @dlt.resource, (3) BAML extractor with client Primary, (4) CocoIndex embedding factory with BGE-M3 embedder, (5) Convex table + A2UI surface. Always bilingual EN + GA per operator direction. Triggers: 'per-jurisdiction', '5-step pattern', 'NCCE pattern', 'subject extraction', 'British Isles education', 'BAML extractor', 'DLT source', 'CocoIndex factory', 'Convex table'.
---

# Per-Jurisdiction Education PDF Ingestion — The 5-Step Pattern

The canonical pattern for ingesting official education system
documentation for each of the 8 British Isles subnations and 7
vernacular languages. Applied first to Ireland (the 5 NCCA policy
PDFs) and the 5 NCCE learning-graph PDFs; the pattern is now
applied to all 8 jurisdictions + 7 vernaculars.

## The 5 steps

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. RAW PDF (via Firecrawl MCP)                                       │
│    Use FirecrawlMCPClient.search() to discover the canonical PDF     │
│    URLs for the jurisdiction. Record in                              │
│    data/bi_ep/syllabi_raw/<jurisdiction>/README.md                  │
└──────────────────────┬──────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. DLT SOURCE (@dlt.resource)                                        │
│    dlt_sources/education/<jurisdiction>/british_isles/               │
│      <jurisdiction>_<subject>_source.py                              │
│    @dlt.resource(name="<jurisdiction>_<subject>_syllabus",            │
│    write_disposition="merge", primary_key=["url"])                 │
└──────────────────────┬──────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. BAML EXTRACTOR (client Primary)                                   │
│    baml_src/british_isles/<jurisdiction>/education/                   │
│      <jurisdiction>_extraction.baml                                  │
│    function Extract<Jurisdiction>SubjectSpec(                         │
│      pdf_text: string, subject_slug: string,                         │
│      stage: <Jurisdiction>Stage, source_url: string)                 │
│    Use `client Primary` per the v5 model priority change.            │
│    Always bilingual: text_en + text_ga + display_name_local          │
│    (vernacular translation).                                          │
└──────────────────────┬──────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 4. COCOINDEX EMBEDDING (BGE-M3 1024-d)                              │
│    cocoindex_flows/biep_parity/<jurisdiction>_factory.py            │
│    Or: cocoindex_flows/british_isles/<jurisdiction>/education.py    │
│    Uses cocoindex_flows/_shared/_lifespan.py:                       │
│      EMBED_MODEL = "BAAI/bge-m3" + EMBED_DIM = 1024                │
│    Splits via RecursiveSplitter(chunk_size=2000, chunk_overlap=500)  │
│    Writes to LanceDB at cianhfhoghlaim.<jurisdiction>...             │
└──────────────────────┬──────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 5. CONVEX TABLE + A2UI SURFACE                                       │
│    web/apps/cianfhoghlaim-nua/convex/<jurisdiction>/<subject>.ts    │
│    web/packages/a2ui/src/components/<ComponentName>.tsx              │
│    Re-exports the per-subject table from the canonical schema.ts    │
│    A2UI mounts via createCatalog() in CopilotKitProvider            │
└─────────────────────────────────────────────────────────────────────┘
```

## Per-jurisdiction checklist

For each of the 8 British Isles subnations, the canonical 5-step
checklist is:

1. **Source PDFs** — scrape from the official education authority
   URL to `data/bi_ep/syllabi_raw/<jurisdiction>/<stage>/<subject>/`
2. **DLT source** — `dlt_sources/education/<jurisdiction>/british_isles/<jurisdiction>_<stage>_source.py`
3. **BAML extraction** — `baml_src/british_isles/<jurisdiction>/education/<jurisdiction>_extraction.baml`
4. **CocoIndex embedding** — extend `cocoindex_flows/biep_parity/<jurisdiction>_factory.py`
5. **Convex persistence** — extend `web/apps/cianfhoghlaim-nua/convex/schema.ts`

## Per-jurisdiction source URLs

| Jurisdiction | Official source | URL pattern |
|---|---|---|
| IE (NCCA) | NCCA.ie + examinations.ie + curriculumonline.ie + gov.ie circulars | `ncca.ie/ga/senior-cycle/<subject>/` |
| EN (DfE) | Department for Education | `gov.uk/government/organisations/department-for-education` |
| EN (Ofqual) | Office of Qualifications and Examinations Regulation | `gov.uk/government/organisations/ofqual` |
| EN (AQA) | Assessment and Qualifications Alliance | `aqa.org.uk/subjects/<gcse|a-level>/<subject>` |
| EN (OCR) | Oxford Cambridge and RSA | `ocr.org.uk/qualifications/<subject>` |
| EN (Pearson Edexcel) | Pearson | `qualifications.pearson.com/en/qualifications/edexcel-<subject>` |
| SC (SQA) | Scottish Qualifications Authority | `sqa.org.uk/sqa/<subject>` |
| SC (Education Scotland) | Education Scotland | `education.gov.scot/curriculum-for-excellence` |
| WL (WJEC) | Welsh Joint Education Committee | `wjec.co.uk/qualifications/<subject>` |
| WL (CBAC) | CBAC | `cbac.co.uk` |
| NI (CCEA) | Council for the Curriculum, Examinations & Assessment | `ccea.org.uk/<subject>` |
| IM (IoM Govt) | Isle of Man Government | `gov.im/education` |
| JE (States of Jersey) | States of Jersey Education | `gov.je/education` |
| GG (States of Guernsey) | States of Guernsey | `gov.gg/education` |

## The 7 vernacular languages (Step 9)

| Language | ISO | Sister-repo home | BAML extractor |
|---|---|---|---|
| Welsh (Cymraeg) | cy | `ciancheiltis/` | `ExtractWelshSubjectSpec` |
|Scottish Gaelic (Gàidhlig) | gd | `gemini_hackathon/` | `ExtractScottishGaelicSubjectSpec` |
|Breton (Brezhoneg) | br | `ciancheiltis/` (future) | `ExtractBretonSubjectSpec` |
|Cornish (Kernewek) | kw | `ciancheiltis/` (future) | `ExtractCornishSubjectSpec` |
|Manx (Gaelg) | gv | `ciancheiltis/` + `gemini_hackathon/` | `ExtractManxSubjectSpec` |
|Channel Islands French (Jersey) | fr-je | `ciancheiltis/` (future) | `ExtractJerseyFrenchSubjectSpec` |
|Channel Islands French (Guernsey) | fr-gg | `ciancheiltis/` (future) | `ExtractGuernseyFrenchSubjectSpec` |
|Ulster Scots | sco | `ciancheiltis/` + `gemini_hackathon/` | `ExtractUlsterScotsSubjectSpec` |

## Anti-patterns

- Do NOT use the old `dlt_sources.british_isles.<jurisdiction>.education.*` path — use the new `dlt_sources.education.<jurisdiction>.british_isles.education.*` (per the Step 1 DLT path drift fix)
- Do NOT use `{{ input }}` in BAML prompt bodies — the renamed `{{ text }}` (per the Phase 0.5 BAML regeneration) is canonical
- Do NOT use `catch_all` blocks — BAML 0.226.2 removed this directive (per the Phase 0.5 fix; 223 files stripped)
- Do NOT use `client_resource_fallback` — replaced with the canonical `options { }` block format
- Do NOT use `prompt: string` as a function parameter — it's a reserved keyword in BAML 0.226.2+

## See also

- `.agents/skills/cianfhoghlaim-nua-v6-era/SKILL.md` — the V6 era
  plan + the 19 openspec changes
- `openspec/changes/2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1/`
  — the Ireland completion (Step 2)
- `openspec/changes/2026-09-01-cianfhoghlaim-nua-5-jurisdiction-completion-v1/`
  — the 5-jurisdiction completion (Steps 4-8)
- `openspec/changes/2026-09-01-cianfhoghlaim-nua-v7-vernaculars-v1/`
  — the 7 vernacular languages (Step 9)
- `openspec/changes/2026-09-01-baml-regeneration-blocker-v1/` —
  the BAML 0.226.2 parser fix (Step 0.5)
- `openspec/changes/2026-09-01-dlt-path-drift-fix-v1/` — the
  Wave 1 DLT path fix (Step 1)
- `openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md` — the
  20-step v6 era plan
