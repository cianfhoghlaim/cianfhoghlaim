# Tasks: consolidate-browser-skills

## 1. Create the new router skill

- [x] Create `.agents/skills/browser-tools/SKILL.md` with:
  - 6-tool table (Stagehand, Firecrawl MCP, Firecrawl CLI, crawl4ai, browser, safe-browser)
  - Decision tree (scrape vs crawl vs click vs autonomous)
  - KCG safety rules (no unscraped auth, domain allowlist, no `:latest`, token storage)
  - When to use Firecrawl MCP vs CLI
  - When to use Stagehand v3 agent mode
  - When NOT to use any of these

## 2. Update the 2 kept skills

- [x] Update `.agents/skills/firecrawl/SKILL.md` frontmatter to
      cross-link to `browser-tools` + `firecrawl-cli`
- [x] Update `.agents/skills/firecrawl-cli/SKILL.md` frontmatter to
      cross-link to `browser-tools` + `firecrawl`

## 3. Delete the 17 sub-skill directories

- [x] `git rm -r .agents/skills/browser`
- [x] `git rm -r .agents/skills/browser-to-api`
- [x] `git rm -r .agents/skills/browser-trace`
- [x] `git rm -r .agents/skills/browserbase-cli`
- [x] `git rm -r .agents/skills/cookie-sync`
- [x] `git rm -r .agents/skills/autobrowse`
- [x] `git rm -r .agents/skills/safe-browser`
- [x] `git rm -r .agents/skills/stagehand`
- [x] `git rm -r .agents/skills/ui-test`
- [x] `git rm -r .agents/skills/firecrawl-agent`
- [x] `git rm -r .agents/skills/firecrawl-crawl`
- [x] `git rm -r .agents/skills/firecrawl-download`
- [x] `git rm -r .agents/skills/firecrawl-interact`
- [x] `git rm -r .agents/skills/firecrawl-map`
- [x] `git rm -r .agents/skills/firecrawl-monitor`
- [x] `git rm -r .agents/skills/firecrawl-parse`
- [x] `git rm -r .agents/skills/firecrawl-scrape`
- [x] `git rm -r .agents/skills/firecrawl-search`

## 4. Validate

- [x] `openspec validate consolidate-browser-skills --strict`
- [x] Verify no orphan references to deleted skill names in
      `firecrawl/SKILL.md` and `firecrawl-cli/SKILL.md`
- [x] Verify all 3 remaining skills have valid frontmatter

## 5. Commit + push

- [x] Commit with message
      `consolidate-browser-skills: 20 → 3 (browser-tools router + firecrawl MCP + firecrawl CLI)`
- [x] `git pull --rebase` then `git push`
- [x] Archive the openspec change
