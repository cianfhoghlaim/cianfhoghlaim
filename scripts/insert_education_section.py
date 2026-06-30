"""Insert a new section between 'Purpose of Cian...' and 'Licensing' at line 1592-1593."""
from __future__ import annotations
from pathlib import Path

MARKER = "p. 6).\n\n\n---\n\n## Licensing"

NEW_SECTION = '''p. 6).


---

## The openspec plans for educational assets and the educational game

The cianfhoghlaim project combines **real, syllabus-accurate
educational assets** with **in-game formative assessment questions**
to create a Leaving Cert / A-Level preparation experience that is
both rigorous and engaging. The 8 NCCA LC subject asset groups
(see "The 11 NCCA Leaving Cert subject asset groups" above) generate
the syllabus-accurate assets; the educational game (the
[Cianfhoghlaim MMO](https://github.com/cianfhoghlaim/cianfhoghlaim-mmo))
turns those assets into a quest-driven, NPC-guided, BAML-graded
experience. This section summarises the openspec plans for both
halves of the loop and how they interlock.

### Real, syllabus-accurate assets (the 8 NCCA LC subject asset groups)

The 8 NCCA Leaving Cert subjects with full DLT + BAML + CocoIndex
+ Cognee + RAGAS pipelines are the **authoritative asset layer**.
For each of `mathematics`, `english`, `gaeilge`, `applied_mathematics`,
`chemistry`, `computer_science`, `biology`, `business`, `french`,
`geography`, `history` (the 11 NCCA LC subjects, of which the 8 most
mature have full end-to-end coverage):

- **The 6-asset dagster pattern** (per subject) produces:
  1. `*_syllabus_raw` — DLT ingest of the NCCA syllabus PDFs into
     DuckLake (per level × language partition: HL/OL/FL × en/ga)
  2. `*_syllabus_structured` — BAML `ExtractLeavingCertSyllabus` per
     PDF row, with `confidence ≥ 0.7` threshold (the
     `low_confidence_review` asset_check flags the rest for human
     review)
  3. `*_quest_pack` — BAML `Generate{Subject}QuestPack` per level
     (FL/OL/HL), producing 4-step graduated-hint items aligned to
     the NCCA learning outcomes
  4. `*_embedding` — CocoIndex v1 embedding of the syllabus into
     LanceDB (BGE-M3, 1024-dim, HNSW)
  5. `*_cognify` — Cognee cognify pass (subject knowledge graph)
  6. `*_dashboard` — marimo notebook execution

- **The 8-asset PDF processing pipeline** (per the PDF processing
  section above) processes the 133 leaving_certificate/ PDFs through:
  discover → convert (5 converters) → ocr_compare (24 OCR models) →
  extract_baml (3 BAML extraction functions) → embed_cocoindex →
  cognify → evaluate (RAGAS) → quality_check (fada + dialect)

- **The 5-converter stack** at
  `meaisinfhoghlaim/document_factory/converters/`
  (deepseekocr, docling, marker, pymupdf4llm, unstructured) produces
  5 alternative renderings of each PDF; the best one (per the
  fada-preservation + RAGAS quality metric) is promoted to the
  canonical extraction.

- **The 24-OCR-model registry** at
  `meaisinfhoghlaim/models/registry.py` (9 vision + 4 classical +
  3 image-gen + 8 alignment) provides the comparison baseline.
  The Irish-content metric is **fada preservation rate** (the
  canonical metric for Irish-language extraction quality).

The 8 mature subjects each have a marimo notebook in
`notebooks/dashboards/education/{subject}_full_pipeline.py` that
demonstrates the full DLT → BAML → CocoIndex → Cognee → marimo
end-to-end flow on real NCCA syllabus PDFs.

### The educational game (the Cianfhoghlaim MMO) and the in-game questions

The [Cianfhoghlaim MMO](https://github.com/cianfhoghlaim/cianfhoghlaim-mmo)
(the educational MMO front-end in `web/apps/cianfhoghlaim-mmo/`)
turns the syllabus-accurate assets into a quest-driven, NPC-guided,
BAML-graded learning experience. The 8 NCCA subject quest-packs
are the source of truth for the in-game questions:

- **Quest generation**: each `qpack_*.baml` file (in
  `baml/education/subjects/`) defines a `Generate{Subject}QuestPack`
  function that produces formative items with:
  - `BilingualText` (Irish canonical + optional English helper)
  - `4 graduated hints` (Level 1 nudge → Level 4 step-by-step)
  - `expected_answer` (canonical solution + marking scheme reference)
  - `common_errors` (the 2-3 typical student mistakes)
  - `evidence` (NCCA PDF page + excerpt + URL)

- **In-game delivery**: the 8 NCCA subject `dagster_assets` expose
  the quest-packs via the marimo notebook + the AG-UI agent + the
  Tuatha MMO front-end. The MMO renders each quest as an NPC dialogue
  with the 4 graduated hints revealed one at a time on student request.

- **Real-time grading**: when a student submits an answer, the MMO
  sends it to `b.{Subject}ScoreQuestResponse(quest_item, student_response)`
  via the LiteLLM `minimax` 7-tier fallback alias. The grading prompt
  includes the 4 hints + the expected answer + the common errors
  + the NCCA PDF page reference, so the grading is rubric-anchored
  and syllabus-accurate.

- **NPC agent fleet**: the 8 NCCA subject NPCs (math, appm, chem,
  comp, bio, bus, eng, gael) are 8 of the 12 agents in
  `agents/adk/root_agent.py` (plus geospatial, statistics,
  education-research, bunchloch-research). The `root_agent`
  orchestrates which NPC to route a question to.

### The asset ↔ game loop (the complete workflow)

The asset and game halves interlock via the `*_quest_pack` dagster
assets and the BAML `Generate{Subject}QuestPack` functions:

1. **Asset production** — the 6-asset pattern produces
   `*_quest_pack` artifacts in DuckLake (one per subject × level).
   Each quest-pack contains 10-20 graded items per the NCCA
   learning outcomes.

2. **Game consumption** — the MMO reads the `*_quest_pack`
   artifacts via the `baml_client.b.{Subject}QuestPackResponse`
   Pydantic models and renders them as NPC dialogue.

3. **Feedback loop** — when a student submits an answer, the MMO
   logs the result to the Cognee knowledge graph (per the
   `*_cognify` asset). Over time, the cognify graph builds a
   per-student mastery map that the 12-agent fleet uses to personalise
   the next quest recommendation.

4. **RAGAS quality loop** — the `*_evaluate` asset runs the RAGAS
   evaluation on the grading quality (extraction accuracy, fada
   preservation, common-error recall), feeding back to the
   `low_confidence_review` asset_check that flags low-quality
   quest-packs for human review.

### The plans in detail

The openspec plans for the educational assets and the educational game
are documented in:

- [`refactor-dlt-cocoindex-baml-dagster-with-pdf-pipeline/`](openspec/changes/refactor-dlt-cocoindex-baml-dagster-with-pdf-pipeline/proposal.md)
  — the 7-phase R1-R7 plan (R1 baml drift, R2 cocoindex drift, R3
  dlt drift, R4 dagster reorg, R5 11 subject asset files, R6 PDF
  processing pipeline, R7 extensive notebooks)
- [`baml-reorganize-by-cluster/`](openspec/changes/baml-reorganize-by-cluster/proposal.md)
  — the 3-cluster BAML taxonomy (education/celtic/processing) that
  the 8 subject asset groups + the PDF processing pipeline consume
- [`wire-baml-to-consolidated-pipelines/`](openspec/changes/wire-baml-to-consolidated-pipelines/proposal.md)
  — the consumer wiring that updated 17 dagster/cocoindex/notebooks
  files to use the canonical cianfhoghlaim.dlt.* paths
- [`consolidate-cianfhoghlaim-subdirs/`](openspec/changes/consolidate-cianfhoghlaim-subdirs/proposal.md)
  — the dlt-lateralise + dagster-by_domain + cocoindex-clustering +
  agents-flattening + notebooks-reorg plans
- [`celtic-ai-institute-roadmap/`](openspec/changes/) (planned) — the
  30-year Cultural Archipelago roadmap (Phase I 2026-2036
  Stabilization, Phase II 2036-2046 Integration, Phase III
  2046-2056 Normalization) anchored at the Celtic AI Institute in
  the Isle of Man
- [`sãoí-education-standard/`](openspec/changes/) (planned) — the
  capstone Phase III credential: a Leaving Cert / A-Level
  distinction that requires a multidisciplinary project combining
  a Celtic language with a STEM discipline, directly enabled by
  the 6-asset subject pipeline + the MMO quest-pack rendering

The combination of the 6-asset dagster pattern, the 8-asset PDF
processing pipeline, the 5-converter + 24-OCR-model stack, the
3-cluster BAML taxonomy, the 8 NCCA LC subject quest-packs, and the
12-agent fleet feeding the Cianfhoghlaim MMO is the concrete
operationalisation of the 30-year Cultural Archipelago roadmap. It
is, in essence, the v4 platform: a working BAML+DLT+CocoIndex+Cognee
loop that produces syllabus-accurate Celtic-language assets and
turns them into graded, in-game, NPC-delivered formative assessment
for Leaving Cert students across the 8 nations.


'''


def main() -> None:
    path = Path("/Users/cianmacandeisigh/dev/kings_college_galway/README.md")
    text = path.read_text()

    if MARKER not in text:
        raise SystemExit(f"Could not find marker: {MARKER!r}")

    new_text = text.replace(MARKER, NEW_SECTION + MARKER)
    path.write_text(new_text)
    print(f"Wrote {len(new_text)} chars (was {len(text)}, added {len(new_text) - len(text)})")


if __name__ == "__main__":
    main()