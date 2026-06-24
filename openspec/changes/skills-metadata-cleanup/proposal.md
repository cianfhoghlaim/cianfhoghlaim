## Why

The `.agents/skills/` directory has accumulated 158 skills with several
classes of bugs that make the canonical skills un-discoverable and the
rest of the directory noisy:

1. **`firecrawl` name collision** — both `firecrawl/SKILL.md` and
   `firecrawl-cli/SKILL.md` declare `name: firecrawl` in their YAML
   frontmatter. The skill loader picks one at random; the other is
   effectively hidden. The CLI variant is meant to be `name: firecrawl-cli`.
2. **`oideachas-pipeline` typo** — the directory is named
   `oideachas-pipeline/` (missing the `i` in `oideachais`) and its
   frontmatter is `name: oideachas-pipeline`. Should be
   `oideachais-pipeline` to match the openspec spec id.
3. **`baml/SKILL.md` is invisible to the skill loader** — 530 lines of
   useful BAML-schema content but no YAML frontmatter, so the skill
   loader skips it. Referenced from 4 quadrant `AGENTS.md` files but
   agents cannot discover it.
4. **Skills without frontmatter that duplicate root `AGENTS.md`**:
   - `data-engineer/SKILL.md` — the 3 mandates duplicate the root
     "Critical Agent Protocols" section.
   - `devops-architect/SKILL.md` — the secret-hydration rule is the
     same as the root "Strict Secret Hydration" section.
   - `image-management/SKILL.md` — 5-line "no `:latest`" rule; folded
     into `kcg-convergence/SKILL.md` as the canonical location.
   - `homebrew/SKILL.md` — explicitly says "Not a loadable skill".
5. **13 Anthropic-source skills** (design + productivity):
   `canvas-design`, `frontend-design`, `web-artifacts-builder`,
   `theme-factory`, `internal-comms`, `doc-coauthoring`,
   `brand-guidelines`, `docx`, `pptx`, `xlsx`, `slack-gif-creator`,
   `algorithmic-art`, `pdf`. Per the 2026-06-06 docs round these are
   upstream Anthropic skills, not KCG-authored, and are not used by any
   KCG project.
6. **4 orphan skills in `skills.backup/dagster/erk/.claude/skills/`** —
   `dignified-python-310`, `-311`, `-312`, `-313` are version-detected
   variants of the canonical `dignified-python` skill that got rolled
   up. The `erk/` skills tree itself was archived/deleted in a prior
   session; the entire `skills.backup/` directory is now dead weight.
7. **Stray `Use Agent Skills in VS Code.md`** at the top of
   `.agents/skills/` — a one-off user doc that should not live in the
   skills tree.

After this change, `.agents/skills/` shrinks from 158 to 140 entries
(13 Anthropic + 4 homebrew/data-engineer/devops-architect/image-management
+ 1 VS Code doc + 1 typo'd directory rename that is technically a +1/-1
+ the entire `skills.backup/` tree of ~24 files). The remaining 140
skills all have valid YAML frontmatter and discoverable names.

## What changes

- `.agents/skills/firecrawl-cli/SKILL.md` — frontmatter `name: firecrawl`
  → `name: firecrawl-cli` (A1)
- `.agents/skills/oideachas-pipeline/` → `.agents/skills/oideachais-pipeline/`
  + frontmatter `name: oideachas-pipeline` → `name: oideachais-pipeline` (A2)
- `.agents/skills/baml/SKILL.md` — add proper YAML frontmatter with
  `name: baml` and a 4-sentence `description` (A3)
- `.agents/skills/{homebrew,data-engineer,devops-architect,image-management}/`
  deleted; image-management content merged into
  `.agents/skills/kcg-convergence/SKILL.md` "Image pinning policy" section (A4–A6)
- `.agents/skills/{canvas-design,frontend-design,web-artifacts-builder,theme-factory,internal-comms,doc-coauthoring,brand-guidelines,docx,pptx,xlsx,slack-gif-creator,algorithmic-art,pdf}/`
  deleted (13 Anthropic-source skills) (A7)
- `.agents/skills/skills.backup/` entire directory deleted (4 dignified-python
  backups + hf/ + erk/ trees) (A8)
- `.agents/skills/Use Agent Skills in VS Code.md` deleted (A9)
- `.agents/skills/kcg-convergence/SKILL.md` — add "Image pinning policy" section (A6 cont.)

## Out of scope

- MotherDuck 19 → 5 consolidation (`motherduck-*` sub-skills) — separate change.
- Browser tools 8 → 3 consolidation (`browser`, `stagehand`, etc.) —
  separate change.
- Code search 2 → 1 (`ccc` vs `chunkhound`) — separate change.
- Shared-spec router skills (B4) — separate change.
- Skill content refresh to 2026-06 package state (C) — separate change.
- `docs-skills-canonical-reference` governance (D1) — separate change.
- `skills-as-project-docs` feedback loop (D2) — separate change.
