# Tasks: consolidate-code-search-skills

## 1. Update ccc skill

- [x] Append "Appendix A: Alternative engines" section to
      `.agents/skills/ccc/SKILL.md` covering:
      - ChunkHound two-layer architecture
      - Multi-hop exploration + 5-second convergence
      - Adaptive token budgets (30k-150k)
      - 29+ language support
      - DuckDB + LanceDB dual store
      - Performance benchmarks (Recall@5, SWE-bench, query latency)
      - "When to consider ChunkHound over ccc" decision
      - "How to install ChunkHound if needed" snippet

## 2. Delete the chunkhound skill

- [x] `git rm -r .agents/skills/chunkhound`

## 3. Validate

- [x] `openspec validate consolidate-code-search-skills --strict`
- [x] Verify only 1 code-search skill remains (`ccc`)
- [x] Verify ccc skill still loads (frontmatter intact)

## 4. Commit + push + archive

- [x] Commit with message
      `consolidate-code-search-skills: 2 → 1 (ccc canonical, chunkhound absorbed)`
- [x] Archive the openspec change
- [x] `git push`
