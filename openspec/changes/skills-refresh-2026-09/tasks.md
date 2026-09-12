## 1. Rewrite the openspec skill for 1.11

- [ ] 1.1 Update `.agents/skills/openspec/SKILL.md` description field to mention openspec 1.11 (not 1.4) and the corrected schema/profile framing; verify by re-reading the file
- [ ] 1.2 Update the openspec skill's `When to use:` section with the verified counts (36 pending / 102 specs / 344 archived) and the new 1.11 subcommands (`doctor`, `config profile`); verify by parsing the file's frontmatter

## 2. Fix the unclosed frontmatter defect

- [ ] 2.1 Add the missing closing `---` to `.agents/skills/dagster/SKILL.md` (after the description block, before the body); verify by round-tripping the file through `python3 -c "import yaml,re; m=re.match(r'^---\n(.+?)\n---', open('.agents/skills/dagster/SKILL.md').read(), re.S); print(yaml.safe_load(m.group(1)))"` without throwing

## 3. Fix unescaped-colon description defects

- [ ] 3.1 Wrap the unescaped `: ` sequences in `.agents/skills/cianfhoghlaim-nua-v6-era/SKILL.md`'s description field in double quotes; verify by round-tripping the frontmatter through yaml.safe_load

## 4. Upgrade the 2 router-only placeholders

- [ ] 4.1 Replace `.agents/skills/copilotkit/SKILL.md` content with a proper router to the 10 `copilotkit/skills/*` sub-skills (develop, debug, setup, upgrade, contribute, integrations, runtime, react-core, a2ui-renderer, copilotkit-agui); verify by re-reading the file
- [ ] 4.2 Replace `.agents/skills/pydantic/SKILL.md` content with a proper router to the 5 `pydantic/*` sub-skills (building-pydantic-ai-agents, logfire-instrumentation, logfire-query, logfire-ui, pydantic-ai-harness); verify by re-reading the file

## 5. Trim oversized descriptions

- [ ] 5.1 Identify the 3 oversized descriptions (`rg -l "^description: .{200,}" .agents/skills/*/SKILL.md`); verify the count is 3 (or close to it)
- [ ] 5.2 For each oversized description, move the trigger phrase into the first 100 chars and defer the longer tail to the body; verify by re-running the size check

## 6. Add the frontmatter lint gate

- [ ] 6.1 Add a `lint:skills-frontmatter` task to `mise.toml` that runs `python3 -c "import os,re,yaml; [yaml.safe_load(m.group(1)) for m in [re.match(r'^---\n(.+?)\n---', open(os.path.join(d, 'SKILL.md')).read(), re.S) for d,_,fs in os.walk('.agents/skills') for f in fs if f=='SKILL.md']]"` and exits non-zero on the first yaml error; verify by running the task against the freshly-fixed skills
- [ ] 6.2 Add a `.github/workflows/lint-skills-frontmatter.yaml` (or add to an existing skills-CI workflow) that runs the gate on every PR; verify the workflow YAML parses

## 7. Verification

- [x] 7.1 Run `openspec validate skills-refresh-2026-09 --strict`; verify it passes (verified 2026-09-12 — passes because of `skip_specs: true`)
- [ ] 7.2 Run `openspec status skills-refresh-2026-09`; verify the 4 artifacts (proposal + design + tasks + skip_specs gate) report done