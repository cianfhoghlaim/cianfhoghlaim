# Tasks

## 1. Pre-flight
- [x] Confirm all `dlt_sources.domains.*` importers are tracked (30+ files).
- [x] Confirm shims continue to re-export from legacy paths after move.

## 2. Move canonical files
- [ ] `git mv` all 53 canonical files from `dlt_sources/domains/{domain}/{nation}/` to `dlt_sources/{nation}/{domain}/`.

## 3. Update shims to new paths
- [ ] Update shim `__init__.py` docstrings to reflect new addresses.
- [ ] Re-export strings (lazy + eager) unchanged — they still point at legacy `dlt_sources.{ireland,uk}.*`.

## 4. Update importers (~30 files)
- [ ] All `dlt_sources.domains.*` references → `dlt_sources.{nation}.{domain}.*` or `dlt_sources.{nation}.{entity}` for single-entity modules.

## 5. Delete the old domains/ tree
- [ ] `git rm` the now-empty `dlt_sources/domains/` directory.

## 6. Validate
- [ ] `openspec validate oideachais-audit-phase-3b-drop-domains-wrapper --strict` passes.
- [ ] `python -c "from dlt_sources.ie.education import ncca; from dlt_sources.ie.law import doj_source, irish_statute_book_source; from dlt_sources.en.medicine import gmc_source"` succeeds.
- [ ] `mise run lint:skills` still 123/123.

## 7. Commit + push
- [ ] `git commit -m "refactor(oideachais): round 11 phase 3b — drop dlt_sources/domains/ wrapper, country-first layout"`
- [ ] `git pull --rebase && git push`
