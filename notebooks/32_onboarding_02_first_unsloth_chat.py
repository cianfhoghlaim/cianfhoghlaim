"""32_onboarding_02_first_unsloth_chat.py — 5 min first Unsloth Studio chat.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Tutorial 2 of 5. Sends the first chat completion to Unsloth Studio via litellm.
Displays the response in a markdown cell.

Run: mise run tutorial:02-first-chat
"""

import marimo

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _intro(mo):
    mo.md(
        """
        # Tutorial 2: First Unsloth Studio chat (~5 min)

        Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.

        This notebook sends the first chat completion to Unsloth Studio via
        litellm (Unsloth-first fallback chain per the spec).

        **Architecture**:
        ```
        marimo → litellm (4000) → unsloth:8889 → Unsloth Studio (8888) → llama-server
        ```

        If Unsloth Studio is empty, the response is "No model loaded" — that's
        expected (Unsloth Studio doesn't have any model loaded by default in
        this dev env). The important thing is that the route is wired.
        """
    )
    return


@app.cell
def _chat_form(mo):
    import os
    litellm_key = os.environ.get("LITELLM_MASTER_KEY", "")
    if not litellm_key:
        return mo.md("> ⚠️ LITELLM_MASTER_KEY not set. Run: `export LITELLM_MASTER_KEY=...`")

    model_picker = mo.ui.dropdown(
        options=[
            "local/unsloth/qwen3.8-27b",
            "local/unsloth/qwen3-vl-8b-instruct",
            "local/unsloth/qwen3-vl-32b-instruct",
            "local/unsloth/gemma-4-26B-A4B",
            "public/unsloth/qwen3.8-27b",
        ],
        value="local/unsloth/qwen3.8-27b",
        label="Unsloth model (via litellm)",
    )
    prompt = mo.ui.text(
        value="What is the capital of France?",
        label="Prompt",
    )
    send_button = mo.ui.run_button(label="Send to Unsloth Studio")
    return model_picker, prompt, send_button


@app.cell
def _send_request(model_picker, prompt, send_button, mo):
    import json
    import os
    import urllib.request

    if not send_button.value:
        return mo.md("> Click **Send to Unsloth Studio** to send the first chat")

    litellm_key = os.environ.get("LITELLM_MASTER_KEY", "")
    payload = json.dumps({
        "model": model_picker.value,
        "messages": [{"role": "user", "content": prompt.value}],
        "max_tokens": 256,
    }).encode()

    req = urllib.request.Request(
        "http://localhost:4000/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {litellm_key}"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            if "choices" in data:
                content = data["choices"][0]["message"]["content"]
                return mo.md(f"### Response from `{model_picker.value}`\n\n{content}")
            else:
                return mo.md(f"### Error\n\n```json\n{json.dumps(data, indent=2)[:1000]}\n```")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:1000]
        if "No model loaded" in body:
            return mo.md(
                f"### Expected response (no model loaded)\n\n"
                f"**HTTP {e.code}** — The route is working, but no model is loaded in Unsloth Studio yet.\n\n"
                f"To load a model, run from the bunchloch host:\n"
                f"```bash\n"
                f"unsloth studio run --model unsloth/Qwen3.8-27B-GGUF:UD-Q4_K_XL --port 8888\n"
                f"```\n\n"
                f"Or via the Studio UI: Settings → API → Model → Select → Download"
            )
        return mo.md(f"### HTTP {e.code}\n\n```\n{body}\n```")
    except Exception as e:
        return mo.md(f"### Error: {e}")


@app.cell
def _next_steps(mo):
    mo.md(
        """
        ## Next steps

        - **Tutorial 3**: `mise run tutorial:03-walkthrough` — 4-stack walkthrough
        - **Tutorial 4**: `mise run tutorial:04-biep-ocr` — 4-path OCR ensemble
        - **Tutorial 5**: `mise run tutorial:05-duchas-htr` — Fine-tune Gemma 4 4B on Dúchas
        """
    )
    return


if __name__ == "__main__":
    app.run()
