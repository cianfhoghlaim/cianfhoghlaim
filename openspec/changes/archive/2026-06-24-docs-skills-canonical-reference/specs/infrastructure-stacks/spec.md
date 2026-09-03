## ADDED Requirements

### Requirement: Skill metadata hygiene

Every skill under `.agents/skills/` MUST have: (1) a YAML frontmatter block with `name:` and `description:`, (2) a `name:` field that equals the parent directory name, (3) a `description:` field of at least 40 characters, and (4) a `SKILL.md` body under 2,000 lines.

#### Scenario: lint:skills passes

- **WHEN** `mise run lint:skills` runs against the current `.agents/skills/` tree (post-consolidation: 110 skills)
- **THEN** all 110 skills pass the 4 metadata checks (frontmatter, name match, description length, line count)
- **AND** the script exits 0

#### Scenario: New skill violates a rule

- **WHEN** a new skill is added without frontmatter, or with a name that does not match its directory, or with a < 40-char description, or with a > 2000-line body
- **THEN** `mise run lint:skills` reports the violation and exits 1

### Requirement: Skill consolidation conventions

KCG skills MUST follow: (5) the canonical name prefixes (motherduck* / browser-tools / ccc / kcg-* / oideachais-* / tuatha-* / croilar-* / meaisinfhoghlaim-*), (6) no vendoring of upstream Anthropic / vendor skills, (7) no skills that duplicate the root `AGENTS.md` "Critical Agent Protocols" content, (8) no embedded git sub-repositories.

#### Scenario: New skill follows the prefixes

- **WHEN** a new skill is added for, e.g., the Convex backend
- **THEN** the directory is `convex/` (not `convex-crm/` or `vendor-convex/`)
- **AND** the frontmatter `name: convex` matches the directory

#### Scenario: Upstream skill is referenced, not vendored

- **WHEN** a third-party tool's docs are needed (e.g. Anthropic's design patterns)
- **THEN** the content lives in a KCG-authored skill (e.g. `frontend-design`) with cross-links to the upstream source
- **AND** the upstream skill directory is NOT vendored into `.agents/skills/`

### Requirement: Skill + openspec alignment

Every openspec capability spec MUST have either a matching `.agents/skills/<spec>/SKILL.md` or an explicit "absorbed into <other-skill>" annotation in `openspec/AGENTS.md`. When an openspec change is archived, the canonical skill SHOULD get a "Post-archive update" note (or be the change's "implementation in skill.md" reference).

#### Scenario: Every spec has a skill pointer

- **WHEN** `openspec list --specs` is run
- **THEN** every spec has either a matching `.agents/skills/<spec>/SKILL.md` OR an entry in `openspec/AGENTS.md` "Capability Specs" table that names a parent skill

#### Scenario: Archived change has a post-archive note

- **WHEN** an openspec change is archived (`openspec archive`)
- **THEN** the canonical skill (if any) gains a "Post-archive update" or "Last archived: <date>" note
- **AND** agents reading the skill know the change is no longer pending
