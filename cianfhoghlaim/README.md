# cianfhoghlaim

> **cianfhoghlaim** — a self-hostable consolidation of Leaving
> Certificate (LC) education system resources. Anyone can `git clone`
> and run their own instance. Built on the open-source agentic stack
> (TanStack Start + CopilotKit v2 + Convex + better-auth + 8 NCCA ADK
> subject agents + 1 cianfhoghlaim operator agent + dlt + cocoindex + baml
> + meaisinfhoghlaim).
>
> Reduce barriers to education.

## TL;DR

`cianfhoghlaim` is a polyglot (`bun + uv`) monorepo that ingests the
NCCA Leaving Certificate curriculum (8 subjects + 5 root-level PDFs),
makes it interactive and bilingual-friendly through self-hosted AI, and
serves as a personal research-and-deployment platform for **Cian
Mac an Déisigh Uí Liatháin** of Galway — a Mathematics & Education
teacher (BSc Hons First Class, NUI Galway), Dioplóma C1 in Irish, current
MSc AI (University of Galway), Fine Gael + Alliance Party of Northern
Ireland + Liberal Democrats + Royal Book Club member, dual
Irish-British citizen, grandchild of the late Neil Deacy of Cooke's
Corner, Shantalla, Galway, member of the **Deacy-Morris-Conroy tribe**
(triple-crown union of Deacy + Lyons + Conroy from the 7 lineage
clippings at
`cian_mac_an_deisigh_ui_liathain/identity/lineage/references/clippings/`).

## What's in the repo

| Subpackage | Path | Purpose |
|:--|:--|:--|
| `dlt/` | `cianfhoghlaim/dlt/` | DLT extraction: reads NCCA syllabus + past papers + marking schemes + writes to MotherDuck / DuckLake |
| `cocoindex/` | `cianfhoghlaim/cocoindex/` | CocoIndex v1 apps: embed the extracted content into LanceDB (BGE-M3 1024-dim) for semantic search |
| `baml_src/` | `cianfhoghlaim/baml_src/` | BAML typed extraction schemas: 8 qpack_<subject>.baml + 4 diagram_renderer.baml + 5 root_pdf_extraction.baml |
| `agents/` | `cianfhoghlaim/agents/tuatha/agents/` | 8 NCCA subject ADK agents (math / appm / chem / geog / hist / engl / gael / comp) + 1 cianfhoghlaim operator |
| `meaisinfhoghlaim/` | `cianfhoghlaim/meaisinfhoghlaim/` | The 24-entry OCR/VLM registry (Unsloth-first fallback chain) + 6 backend adapters |
| `notebooks/` | `cianfhoghlaim/notebooks/` | Marimo dashboards: 8 per-subject teacher notebooks + 1 root_pdfs_explorer + 1 diagram_library |
| `apps/web/` | `cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/web/` | TanStack Start + CopilotKit v2 + Convex + better-auth |
| `apps/api/` | `cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/api/` | Hono + oRPC + CopilotKit AG-UI runtime |
| `leaving_certificate/` | `cianfhoghlaim/leaving_certificate/` | The 8 NCCA subject folders (PDFs) + the 5 root-level PDFs |
| `cian_mac_an_deisigh_ui_liathain/` | `cianfhoghlaim/cian_mac_an_deisigh_ui_liathain/` | The personal identity / lineage / triple-crown (operator-only) |

## What's deployed at `apps/cianfhoghlaim-leaving-cert/`

The deployed `apps/web` is the **agentic tutorial for the repo itself**.
The cianfhoghlaim website exposes the 9 ADK agents + the 8 NCCA subjects
+ the 5 NCCA root-level PDFs + the practice page + the 4 diagram modes.

The 9th agent — the `cianfhoghlaim_operator` — is the repo self-reference.
It has tools to:
- `list_subjects` — the 8 NCCA subjects + their agent + cocoindex + baml paths
- `list_agents` — the 9 ADK agents
- `list_foundations` — the 5 NCCA root-level PDFs
- `show_dlt_pipeline` — explain the DLT extraction for a topic
- `show_cocoindex_index` — explain the CocoIndex v1 app for a topic
- `show_baml_schema` — show the BAML schema for a function
- `list_eiraic_treasures` — the 13-tier mastery progression

## Self-host in 5 minutes

```bash
git clone https://github.com/cianfhoghlaim/cianfhoghlaim.git
cd cianfhoghlaim
bun install
bun run dev
# Web: http://localhost:3082/
# API: http://localhost:8787/
```

See [`apps/cianfhoghlaim-leaving-cert/docs/SELF-HOST.md`](apps/cianfhoghlaim-leaving-cert/docs/SELF-HOST.md)
for the full self-host guide.

## License

BUSL-1.1 with a 4-year transition to AGPL v3. The personal
triple-crown lineage + the ard-rí na hÉireann aspirations are documented
in the operator-only lore document — not deployed to the public surface.

Built by **Cian Mac an Déisigh Uí Liatháin** of the Deacy-Morris-Conroy
tribe of Galway.

> *Enduring learning · Reduce barriers to education · Open source*
