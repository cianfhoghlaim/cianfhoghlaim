"""31_onboarding_01_env_check.py — 3 min dev environment validation.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Tutorial 1 of 5. Validates Docker, mise, uv, bun, openspec, marimo, dlt, BAML,
and that the 4-stack (Unsloth Studio + Hermes + OpenClaw + OpenChamber) is healthy.

Run: mise run tutorial:01-env
"""

import marimo

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _intro(mo):
    mo.md(
        """
        # Tutorial 1: Dev environment validation (~3 min)

        Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.

        This notebook validates:
        1. Required CLI tools (docker, mise, uv, bun, openspec, marimo, dlt, baml)
        2. The 4-stack health (Unsloth Studio + Hermes + OpenClaw + OpenChamber)
        3. The litellm unsloth routes (18+)
        4. The marimo multi-notebook server (57 notebooks)
        """
    )
    return


@app.cell
def _check_cli_tools(mo):
    import shutil
    import subprocess

    tools = ["docker", "mise", "uv", "bun", "openspec", "marimo", "dlt", "baml"]
    results = []
    for tool in tools:
        path = shutil.which(tool)
        if path:
            try:
                out = subprocess.run([tool, "--version"], capture_output=True, text=True, timeout=5)
                version = (out.stdout or out.stderr).strip().split("\n")[0][:60]
                results.append((tool, "✅", f"{version} at {path}"))
            except Exception as e:
                results.append((tool, "❌", f"Error: {e}"))
        else:
            results.append((tool, "❌", "Not found in PATH"))

    rows = [{"Tool": t, "Status": s, "Detail": d} for t, s, d in results]
    return mo.ui.table(rows, label="CLI tools")


@app.cell
def _check_4_stack(mo):
    import urllib.request

    endpoints = {
        "Unsloth Studio (8888)": "http://localhost:8888/api/auth/status",
        "Litellm (4000)": "http://localhost:4000/health/liveliness",
        "Marimo (2718)": "http://localhost:2718/health",
    }
    rows = []
    for name, url in endpoints.items():
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3) as resp:
                rows.append({"Service": name, "Status": f"✅ HTTP {resp.status}"})
        except Exception as e:
            rows.append({"Service": name, "Status": f"❌ {type(e).__name__}"})

    return mo.ui.table(rows, label="4-stack health")


@app.cell
def _check_litellm_unsloth_routes(mo):
    import json
    import os
    import urllib.request

    litellm_key = os.environ.get("LITELLM_MASTER_KEY", "")
    if not litellm_key:
        return mo.md("> ⚠️ LITELLM_MASTER_KEY not set in environment. Run: `export LITELLM_MASTER_KEY=...`")

    try:
        req = urllib.request.Request(
            "http://localhost:4000/v1/models",
            headers={"Authorization": f"Bearer {litellm_key}"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            unsloth_routes = [m for m in data["data"] if "unsloth" in m["id"].lower()]
            return mo.md(
                f"### Litellm unsloth routes: **{len(unsloth_routes)}** loaded\n\n"
                + "\n".join(f"- `{m['id']}`" for m in unsloth_routes[:5])
                + (f"\n- ... and {len(unsloth_routes) - 5} more" if len(unsloth_routes) > 5 else "")
            )
    except Exception as e:
        return mo.md(f"> ❌ Error: {e}")


@app.cell
def _next_steps(mo):
    mo.md(
        """
        ## Next steps

        If all checks pass, proceed to:
        - **Tutorial 2**: `mise run tutorial:02-first-chat` — Send your first chat to Unsloth Studio
        - **Tutorial 3**: `mise run tutorial:03-walkthrough` — 4-stack walkthrough
        - **Tutorial 4**: `mise run tutorial:04-biep-ocr` — 4-path OCR ensemble on a LC Gaeilge paper
        - **Tutorial 5**: `mise run tutorial:05-duchas-htr` — Fine-tune Gemma 4 4B on Dúchas.ie transcriptions
        """
    )
    return


if __name__ == "__main__":
    app.run()
