# docling-serve

## Purpose for the Cianfhoghlaim project

Docling Serve is an HTTP API server wrapping IBM's Docling library, which converts PDF documents into structured formats (markdown, JSON, DocTags XML). Unlike traditional OCR, Docling understands document layout — it can identify headings, paragraphs, tables, figures, and equations, preserving the document's logical structure rather than just extracting raw text.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the personal/utility fleet. Reproducible via the IaC bootstrap; no cianfhoghlaim project dependencies.

## Cross-references

- **Ops**: `bonneagar/stacks/docling-serve/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:personal-utility`
- - **Pangolin**: `https://docling.cianfhoghlaim.ie` (if exposed)

## Tags

- `host:bunchloch`
- `tier:personal-utility`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
