# Tasks: sync-skills-from-docs-round-7

## 1. Create OpenSpec change scaffolding
- [x] Create change directory.
- [x] Write `proposal.md`.
- [x] Write `tasks.md` (this file).
- [x] Write 1 spec delta (infrastructure-stacks).
- [x] Validate `--strict`.

## 2. New skills (4)
- [x] Create `.agents/skills/kcg-bunchloch/SKILL.md` (3-tier
      host topology + service relationships + ports).
- [x] Create `.agents/skills/kcg-leabharlann-pipeline/SKILL.md`
      (5-stage PDF flow + 6 docker-compose layer integration).
- [x] Create `.agents/skills/kcg-ml-models/SKILL.md` (70+
      models + 5 fallback chains + 3 backends).
- [x] Create `.agents/skills/kcg-convergence/SKILL.md`
      (6 docker-compose categories + port allocation map).

## 3. Skills expanded (6)
- [x] Expand `.agents/skills/stack-ops/SKILL.md` (6
      docker-compose categories + per-category inventory).
- [x] Expand `.agents/skills/pangolin/SKILL.md` (3-tier
      convergence zones).
- [x] Expand `.agents/skills/oideachais-storage/SKILL.md`
      (Lance vs Iceberg dual-format strategy).
- [x] Expand `.agents/skills/dagster/SKILL.md` (21-asset /
      7-group inventory + 5-stage leabharlann order).
- [x] Expand `.agents/skills/secrets-management/SKILL.md`
      (rewrite provider section to Infisical-only; drop
      1Password + 1Password Connect + Bitwarden).
- [x] Expand `.agents/skills/celtic-language-ai/SKILL.md`
      (KCG production model fallback chains).

## 4. Delete the ~75 docs
- [x] Delete the 5 1Password-only files.
- [x] Delete the ~50 upstream-tool material files
      (komodo.md, pangolin.md, all komodo/*.md, all
      pangolin/*.md, all cloudflare-*.md, all dagger-*.md,
      etc.).
- [x] Delete the ~15 KCG-content files (bunchloch.md,
      leabharlann-stack-overview.md, ML_MODELS_REGISTRY.md,
      etc.) whose content is absorbed into new skills.
- [x] Delete the trivial / out-of-scope files
      (Register a GCP Instance.md, termix.md, etc.).

## 5. Verify
- [ ] Re-validate `--strict`.
- [ ] `secrets-management/SKILL.md` no longer references
      1Password.

## 6. Archive
- [ ] `openspec archive sync-skills-from-docs-round-7 --yes`.

## 7. Land the plane
- [ ] `git add` only my changes (avoid the pre-existing
      .gitignore, .infisical.env, stirling-pdf, cocoindex_flows,
      untracked top-level docs changes).
- [ ] `git commit -m "..."`.
- [ ] `git push`.
