# British Isles Medicine + Law DLT Sources — Registry

## Provenance

The 6 crown-dependencies (Isle of Man, Jersey, Guernsey) medicine + law
DLT sources were added per `kings_college_galway#19`. The 6 source files
reference that issue in their docstrings:

| File | Jurisdiction | Domain |
|---|---|---|
| `dlt_sources/medicine/guernsey/british_isles/health_social_care.py` | Guernsey (GGY) | Medicine (Health & Social Care) |
| `dlt_sources/medicine/jersey/british_isles/health_community_services.py` | Jersey (JEY) | Medicine (Health & Community Services) |
| `dlt_sources/medicine/isle_of_man/british_isles/health_social_care.py` | Isle of Man (IOM) | Medicine (Health & Social Care) |
| `dlt_sources/law/guernsey/british_isles/legislation.py` | Guernsey (GGY) | Law (Laws of Guernsey) |
| `dlt_sources/law/jersey/british_isles/legislation.py` | Jersey (JEY) | Law (Jersey Legal Information Board) |
| `dlt_sources/law/isle_of_man/british_isles/legislation.py` | Isle of Man (IOM) | Law (Isle of Man Statute Books) |

## Open data-integrity follow-up

In the docstring of each file, the GitHub URL was renamed mechanically on
**2026-08-27** as part of the `kings_college_galway` → `cianfhoghlaim`
refactor (Phase 2d — Subagent 4: `scripts/dlt_sources/openspec`):

```
- old: https://github.com/cianfhoghlaim/kings_college_galway/issues/19
- new: https://github.com/cianfhoghlaim/cianfhoghlaim/issues/19
```

If issue #19 was re-numbered when the repo was renamed
(`kings_college_galway` → `cianfhoghlaim`), the new URL will 404. The
follow-up is:

1. Browse `https://github.com/cianfhoghlaim/cianfhoghlaim/issues?q=is%3Aissue+crown+dependencies+lateralise`
   to find the equivalent issue number in the renamed repo.
2. Search the repo's closed-issues 2026-06 archive for the lateralise
   change that wired these 6 sources.
3. Update the docstring URL in all 6 files to the new issue number.
4. Re-run `bun run scripts/cianfhoghlaim-brand-lint.ts dlt_sources`.

Tracked as a known follow-up. Not blocking the refactor — these URLs are
documentation-only (no runtime code fetches them).
