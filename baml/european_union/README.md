# EU institutional BAML cluster

This cluster contains the BAML extraction schemas for the EU
institutional pipeline (`european-union-official-language-pipeline`).

## Layout

```text
baml/european_union/
├── _shared/
│   ├── eu_languages.baml           # the 24 EU official languages enum
│   ├── eu_institutions.baml        # the 15 EU institution slugs enum
│   └── eu_document.baml            # the canonical multilingual document class
├── eur_lex_extraction.baml         # EUR-Lex regulations / directives / decisions / treaties
├── ema_extraction.baml             # European Medicines Agency register
├── ecdc_extraction.baml            # ECDC surveillance
├── eurydice_extraction.baml        # Eurydice national education structures
└── eurostat_extraction.baml        # Eurostat dataset metadata
```

## Canonical extraction entry point

`b.ExtractEUDocument(language, text) -> EUDocument` (in
`_shared/eu_document.baml`) is the canonical extraction function. It
is the multilingual sibling of `b.ExtractCurriculumSyllabus` (BIEP v1)
and `b.ExtractLC6Syllabus` (per-subject LC6).

The per-institution specialised extractors
(`ExtractEURLexRegulation`, `ExtractEMAMedicine`, etc.) are the
high-fidelity extraction entry points for the institution-specific
DuckLake tables.

## Cross-references

- [`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md) —
  the umbrella contract
- [`european-union-official-language-pipeline`](../../../openspec/specs/european-union-official-language-pipeline/spec.md) —
  the EU pipeline spec
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
