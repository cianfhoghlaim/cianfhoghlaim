# Tasks: skills-metadata-cleanup

## 1. A1: Fix firecrawl-cli name collision

- [x] Edit `.agents/skills/firecrawl-cli/SKILL.md` frontmatter:
      `name: firecrawl` → `name: firecrawl-cli`

## 2. A2: Rename oideachas-pipeline → oideachais-pipeline

- [x] `git mv .agents/skills/oideachas-pipeline .agents/skills/oideachais-pipeline`
- [x] Edit `.agents/skills/oideachais-pipeline/SKILL.md` frontmatter:
      `name: oideachas-pipeline` → `name: oideachais-pipeline`

## 3. A3: Add YAML frontmatter to baml/SKILL.md

- [x] Prepend YAML frontmatter with `name: baml` and 4-sentence description
      covering static + dynamic (TypeBuilder) + multimodal + streaming
      patterns, named clients, polyglot codegen, 8-stage BAML lifecycle

## 4. A4–A6: Delete + merge noise skills

- [x] `git rm -r .agents/skills/homebrew`
- [x] `git rm -r .agents/skills/data-engineer`
- [x] `git rm -r .agents/skills/devops-architect`
- [x] `git rm -r .agents/skills/image-management`
- [x] Append "Image pinning policy (no `:latest`)" section to
      `.agents/skills/kcg-convergence/SKILL.md` before "Cross-references"

## 5. A7: Delete 13 Anthropic-source skills

- [x] `git rm -r .agents/skills/canvas-design`
- [x] `git rm -r .agents/skills/frontend-design`
- [x] `git rm -r .agents/skills/web-artifacts-builder`
- [x] `git rm -r .agents/skills/theme-factory`
- [x] `git rm -r .agents/skills/internal-comms`
- [x] `git rm -r .agents/skills/doc-coauthoring`
- [x] `git rm -r .agents/skills/brand-guidelines`
- [x] `git rm -r .agents/skills/docx`
- [x] `git rm -r .agents/skills/pptx`
- [x] `git rm -r .agents/skills/xlsx`
- [x] `git rm -r .agents/skills/slack-gif-creator`
- [x] `git rm -r .agents/skills/algorithmic-art`
- [x] `git rm -r .agents/skills/pdf`

## 6. A8: Delete entire skills.backup/ directory

- [x] `git rm -r .agents/skills/skills.backup` (removes erk/ tree,
      hf/ tree, 4 dignified-python-310..313 backups)

## 7. A9: Delete stray VS Code doc

- [x] `git rm .agents/skills/Use Agent Skills in VS Code.md`

## 8. Validate

- [x] `openspec validate skills-metadata-cleanup --strict` (only
      requires the change to exist; no spec deltas needed)
- [x] Verify `.agents/skills/` has 140 entries (158 - 18)
- [x] Verify no skill has malformed frontmatter (every
      `*/SKILL.md` starts with `---` then `name:`)

## 9. Commit + push

- [x] Commit with message
      `skills-metadata-cleanup: fix frontmatter bugs, remove 18 noise skills`
- [x] `git pull --rebase` then `git push`
- [x] Verify `git status` shows "up to date with origin"
