# Tasks: skills-refresh-2026-09

> Skills refresh — YAML frontmatter fixes + 2 missing routers + trim
> oversized descriptions + lint gate.
> In-progress (1/12).

## 1. Audit (in progress)

- [x] **S1.1** Run the 2026-09-02 skills-refresh audit; identified 7 defects in `.agents/skills/`

## 2. YAML frontmatter fixes

- [ ] **S2.1** Fix unclosed YAML frontmatter blocks (1 skill)
- [ ] **S2.2** Fix unescaped `: ` colons breaking YAML parse (3 skills)
- [ ] **S2.3** Fix oversized descriptions (2 skills trimmed)

## 3. Missing routers

- [ ] **S3.1** Add `copilotkit/skills/` router
- [ ] **S3.2** Add `pydantic/` router

## 4. Trim oversized descriptions

- [ ] **S4.1** Trim `openspec` SKILL.md description (the v1.4 framing needs to be replaced — overlaps with openspec-1-11-migration task O3.1)
- [ ] **S4.2** Trim 1 other oversized skill description

## 5. New lint gate

- [ ] **S5.1** Add `mise run lint:skills-frontmatter` (validates every skill's frontmatter round-trips through a YAML parser)

## 6. Verification

- [ ] **S6.1** Run `mise run lint:skills-frontmatter` — pass
- [ ] **S6.2** Run `mise run lint:skills` — pass

## Verification

```bash
cd ~/dev/cianchosaint-laim 2>/dev/null || cd ~/dev/cianchoshlaim
openspec validate skills-refresh-2026-09 --strict
mise run lint:skills
mise run lint:skills-frontmatter
```
