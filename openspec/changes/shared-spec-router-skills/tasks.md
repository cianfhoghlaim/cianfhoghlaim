# Tasks: shared-spec-router-skills

## 1. Create the 4 router skills

- [x] Create `.agents/skills/agent-memory-systems/SKILL.md` (5-backend
      router: Cognee + Graphiti + LanceDB + FalkorDB + Memgraph)
- [x] Create `.agents/skills/dagger-pipelines/SKILL.md` (8 functions +
      4 build pipelines)
- [x] Create `.agents/skills/infrastructure-stacks/SKILL.md` (6-file
      GOLD_STANDARD + 3-tier host + 5-stage deploy)
- [x] Create `.agents/skills/data-engineering-pipeline-documentation/SKILL.md`
      (STATUS.md + REFACTORING.md + per-area READMEs + 5-stage pipeline)

## 2. Spec deltas

- [x] `openspec/changes/shared-spec-router-skills/specs/agent-memory-systems/spec.md`
      - 1 ADDED Requirement: Agent memory router skill
- [x] `openspec/changes/shared-spec-router-skills/specs/dagger-pipelines/spec.md`
      - 1 ADDED Requirement: Dagger pipelines router skill
- [x] `openspec/changes/shared-spec-router-skills/specs/infrastructure-stacks/spec.md`
      - 1 ADDED Requirement: Infrastructure stacks router skill
- [x] `openspec/changes/shared-spec-router-skills/specs/data-engineering-pipeline-documentation/spec.md`
      - 1 ADDED Requirement: Data engineering pipeline documentation router skill

## 3. Validate

- [x] `openspec validate shared-spec-router-skills --strict`
- [x] Verify all 4 new skills have valid frontmatter

## 4. Commit + push + archive

- [x] Commit with message
      `shared-spec-router-skills: add 4 thin router skills for shared capabilities`
- [x] Archive the openspec change
- [x] `git push`
