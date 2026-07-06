# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.13.0",
# ]
# ///
"""06 — Skill metadata lint via `mise run lint:skills`.

Demonstrates `mise_lint_skills` from
`cianfhoghlaim.agents.adk.tools.dev_env` — runs the 4-rule metadata
lint on all skills in `.agents/skills/`:

1. **Frontmatter** — `--- name / description ---` block present
2. **Name match** — `name:` matches the directory name
3. **Description length** — `description:` is 100-300 chars
4. **Line count** — `SKILL.md` ≤ 500 lines

See also:
- `mise.toml` — `[tasks.lint-skills]` task
- `.agents/skills/_template/SKILL.md`
"""

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    return (mo,)


@app.cell
def _intro(mo):
    mo.md(
        """
        # 06 — mise_lint_skills (4-rule metadata lint)

        Live demo of `mise_lint_skills` from
        `cianfhoghlaim.agents.adk.tools.dev_env`. Runs
        `mise run lint:skills` and parses the output.

        **The 4 rules enforced:**
        1. **Frontmatter** — `--- name / description ---` block present
        2. **Name match** — `name:` matches the directory name
        3. **Description length** — `description:` is 100-300 chars
        4. **Line count** — `SKILL.md` ≤ 500 lines
        """
    )
    return


@app.cell
def _path_picker(mo):
    """Single-select for the skills directory."""
    path = mo.ui.text(
        value=".agents/skills/",
        label="Path to skills dir",
        full_width=True,
    )
    path
    return (path,)


@app.cell
def _run_lint(path):
    """Call `mise_lint_skills` for the selected path."""
    import asyncio
    import importlib.util
    from pathlib import Path

    _tool_path = Path("cianfhoghlaim/agents/adk/tools/dev_env.py")
    _spec = importlib.util.spec_from_file_location("dev_env", _tool_path)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)

    result = asyncio.run(_mod.mise_lint_skills(path=path.value))
    return Path, result


@app.cell
def _render(result, mo):
    """Render the lint report."""
    passed = result.get("passed", 0)
    failed = result.get("failed", 0)
    failures = result.get("failures", [])
    duration = result.get("duration_s", 0)
    rc = result.get("returncode", -1)
    tail = result.get("raw_output_tail", "")

    badge = "🟢" if rc == 0 and failed == 0 else "🔴"

    if not failures:
        failure_section = "_No failures detected._"
    else:
        rows = "\n".join(
            f"| `{f['skill']}` | {f['rule']} | {f['message']} |"
            for f in failures
        )
        failure_section = (
            f"| skill | rule | message |\n"
            f"|-------|------|---------|\n"
            f"{rows}"
        )

    mo.md(
        f"""
        ## {badge} Lint result: **{passed} pass · {failed} fail** in {duration}s

        **Return code:** `{rc}`

        {failure_section}

        **Raw output tail:**
        ```
        {tail}
        ```

        **How to fix failures:**
        - **frontmatter missing** — add a `--- name / description ---`
          block at the top of `SKILL.md`
        - **name mismatch** — rename `name:` to match the directory
        - **description too long/short** — trim to 100-300 chars
        - **line count exceeded** — split into `SKILL.md` + `references/`
          per the dignified-python skill pattern
        """
    )
    return badge, duration, failed, failures, failure_section, passed, rc, tail


if __name__ == "__main__":
    app.run()
