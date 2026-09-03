# Tasks

## 1. Move the 2 subtrees + rmdir the empty parents

- [x] 1.1 `mv baml/ie/law baml/education/law/`
- [x] 1.2 `rm baml/ie/__init__.py` + `rmdir baml/ie`
- [x] 1.3 `mv dlt/british_isles/ie/law dlt/british_isles/ireland/education/law/`
- [x] 1.4 `rm dlt/british_isles/ie/__init__.py` + `rmdir dlt/british_isles/ie`

## 2. Sed-rewrite the Python + BAML imports (17 refs)

- [x] 2.1 `find cianfhoghlaim/ -name '*.py' | xargs sed -i '' …` (3 passes — `from …` imports, bare docstring refs, `cianfhoghlaim.*` refs)
- [x] 2.2 `find cianfhoghlaim/ -name '*.baml' | xargs sed -i '' …` (4 patterns)

## 3. Fix `_oide_helpers.py:11` import chain

- [x] 3.1 Replace `from common.firecrawl_source import crawl_website, scrape_page`
  with the canonical `dlt.common` path:
  ```python
  from cianfhoghlaim.dlt.common import firecrawl_source
  from cianfhoghlaim.dlt.common.incremental import compute_content_hash
  crawl_website, scrape_page = firecrawl_source.crawl_website, firecrawl_source.scrape_page
  ```

## 4. Sed-rewrite openspec/specs/*.md (31 refs)

- [x] 4.1 `find openspec/specs -name '*.md' | xargs sed -i '' …` (3 patterns)
- [x] 4.2 Confirm 0 active refs remain (the 24 in `openspec/changes/archive/` are intentionally preserved)

## 5. Verify

- [x] 5.1 `grep -rn 'british_isles.ie\|dlt/british_isles/ie\|baml.ie' --include='*.{py,baml,md}' cianfhoghlaim/ openspec/specs/` → 0
- [x] 5.2 `ls dlt/british_isles/ | grep -c '^ie$'` → 0
- [x] 5.3 `ls baml/ | grep -c '^ie$'` → 0
- [x] 5.4 `ls dlt/british_isles/ireland/education/law/` → 5 .py files
- [x] 5.5 `ls baml/education/law/` → 6 .baml files + `__init__.py`

## 6. Openspec change authoring

- [x] 6.1 `mkdir -p openspec/changes/2026-07-10-cleanup-ie-to-ireland-namespace-v1/specs/{cianfhoghlaim-pipeline,cianfhoghlaim-marimo-dashboards}`
- [x] 6.2 `proposal.md` (this change narrative)
- [x] 6.3 `tasks.md` (this file)
- [x] 6.4 `specs/cianfhoghlaim-pipeline/spec.md` (MODIFIED Requirement)
- [x] 6.5 `specs/cianfhoghlaim-marimo-dashboards/spec.md` (MODIFIED Requirement)
- [x] 6.6 `openspec validate 2026-07-10-cleanup-ie-to-ireland-namespace-v1 --strict`

## 7. Commit + push

- [x] 7.1 `git add -A` + review staged diff
- [x] 7.2 `git commit -m 'chore(cleanup): ie -> ireland namespace migration + 17-import rewrite'`
- [x] 7.3 `git push --set-upstream origin pick-4-biep-v1`