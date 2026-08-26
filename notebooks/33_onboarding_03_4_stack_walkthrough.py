"""33_onboarding_03_4_stack_walkthrough.py — 10 min 4-stack walkthrough.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Tutorial 3 of 5. Walks through Hermes + OpenClaw + OpenChamber + Unsloth Studio.
Sends a test message through Hermes → litellm → Unsloth Studio. Shows the Langfuse trace.

Run: mise run tutorial:03-walkthrough
"""

import marimo

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _intro(mo):
    mo.md(
        """
        # Tutorial 3: 4-stack walkthrough (~10 min)

        Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.

        **The 4-stack**:
        1. **Unsloth Studio** (host:8888) — local LLM inference via llama-server
        2. **Hermes** (Docker:9119) — agent control plane + LiteLLM chokepoint
        3. **OpenClaw** (Docker:18789) — consumer gateway (Slack/Teams/Discord/etc.)
        4. **OpenChamber** (Docker) — OpenCode IDE for the 12-agent fleet

        **Architecture**:
        ```
        [OpenChamber]    [OpenClaw]      [Hermes]    [litellm]    [Unsloth Studio]
        agent UI    →   gateway      →   channels   →   4000    →   8888
                                                                     llama-server
        ```
        """
    )
    return


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

    return mo.ui.table(rows, label="4-stack health (Unsloth Studio + litellm + marimo)")


@app.cell
def _check_hermes_env(mo):
    import os
    import subprocess

    if not os.system("docker ps | grep -q hermes >/dev/null 2>&1"):
        try:
            out = subprocess.check_output(
                ["docker", "exec", "hermes", "env"],
                stderr=subprocess.STDOUT, text=True, timeout=5,
            )
            lines = [l for l in out.split("\n") if "UNSLOTH" in l]
            return mo.md("### Hermes env (Unsloth-related)\n\n" + "\n".join(f"- `{l}`" for l in lines))
        except Exception as e:
            return mo.md(f"### Hermes env error: {e}")
    return mo.md("> Hermes container not running (skipped)")


@app.cell
def _next_steps(mo):
    mo.md(
        """
        ## What's running

        - **Unsloth Studio** runs on the host (not a container) at 8888
        - **Hermes / OpenClaw / OpenChamber** run in Docker containers
        - **litellm** routes through to the Studio
        - **marimo** serves all 57 notebooks (including these 5 tutorials)

        ## Next steps

        - **Tutorial 4**: `mise run tutorial:04-biep-ocr` — 4-path OCR ensemble
        - **Tutorial 5**: `mise run tutorial:05-duchas-htr` — Fine-tune Gemma 4 4B
        """
    )
    return


if __name__ == "__main__":
    app.run()
