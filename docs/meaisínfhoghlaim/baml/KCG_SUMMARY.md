# BAML — KCG Summary

## What It Is
Two workshop repositories from Boundary ML's "AI That Works" series demonstrating BAML (Basically A Made-up Language) — a domain-specific language for defining structured LLM outputs. The "Generative UIs" episode covers semantic streaming of partial, valid JSON objects for interactive AI experiences. The "Dynamic Schemas" episode demonstrates LLM-driven schema generation where the model first describes a schema, then extracts data against it — enabling extraction from unknown document structures.

## Why This Matters for Kings' College Galway
BAML is the structured-output backbone of the Celtic education pipeline. The generative UI pattern directly applies to the interactive Leaving Certificate problem solver: streaming structured step-by-step solutions (with LaTeX math, Irish translations, marking scheme points) as they generate, rather than waiting for the full response. The dynamic schema pattern enables extracting structured data from varied Irish curriculum documents (exam papers, syllabi, textbooks) without pre-defining schemas for every format — the LLM discovers the structure. This is essential for building a scalable ingestion pipeline that handles the full diversity of Celtic educational materials across exam boards (State Examinations Commission, CCEA, SQA, WJEC).

## Key Patterns Preserved
- `2025-09-09-generative-uis/README.md` — Generative UIs workshop: structured streaming patterns
- `2025-09-09-generative-uis/email.md` — Follow-up email with workshop resources
- `2025-09-09-generative-uis/meta.md` — Workshop metadata and links
- `2025-09-09-generative-uis/my-app/README.md` — Demo app: NextJS + BAML recipe generator
- `2025-09-30-dyanmic-schemas/README.md` — Dynamic schemas workshop: LLM-driven schema generation
- `2025-09-30-dyanmic-schemas/email.md` — Follow-up email with workshop resources
- `2025-09-30-dyanmic-schemas/meta.md` — Workshop metadata and links
- `2025-09-30-dyanmic-schemas/backend/README.md` — Backend: Python + FastAPI + BAML dynamic extraction
- `2025-09-30-dyanmic-schemas/frontend/README.md` — Frontend: React dynamic schema UI

## Source Files
Full source removed (2026-06-06). Available at:
- BAML: https://github.com/BoundaryML/baml

## What Was Removed
TypeScript/JavaScript source code, Python source, BAML schema files (.baml), React/NextJS components, package.json, lockfiles, CSS/HTML, Dockerfiles, CI/CD configs, Git metadata.
