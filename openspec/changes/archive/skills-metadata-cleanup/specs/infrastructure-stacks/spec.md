## ADDED Requirements

### Requirement: Skill metadata hygiene

Every skill under `.agents/skills/` SHALL have:

- A YAML frontmatter block (`---` on line 1, then `name:` and
  `description:`, then `---` closer)
- A `name:` field that equals the parent directory name
- A `description:` field of at least 40 characters describing when to
  load the skill
- A `SKILL.md` body under 2,000 lines (split into a router + reference
  files for larger content)

#### Scenario: Skill is discoverable

- **WHEN** an agent triggers a phrase that matches the skill's
  `description`
- **THEN** the skill loader surfaces the skill and the agent can read
  its `SKILL.md`

#### Scenario: Skill name matches directory

- **WHEN** a skill's `name:` frontmatter field does NOT match its
  parent directory name
- **THEN** the `lint:skills` script reports a `name-mismatch` error
