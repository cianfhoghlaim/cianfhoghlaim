# `spaces/_common/` — Cianfhoghlaim Build Small 2026 Shared Bundle

This directory is the **cross-cutting foundation** for the 4 HuggingFace Spaces
in the Build Small 2026 hackathon submission. Every Space imports from
`spaces._common` so the visual identity, BAML client, i18n strings, and
"anam bonneagar" trust signal stay consistent.

## Layout

```
spaces/_common/
├── __init__.py             # Re-exports for the 5 components
├── theme.py                # Celtic 5-element palette + Hades Shadow-First
├── anam_bonneagar.py       # Per-Space footer (5 trust signals)
├── soulbound_svg.py        # Deterministic Celtic-knot SVG (Anam wallet)
├── social_card.py          # 1200x630 PNG social card auto-renderer
├── i18n.py                 # Bilingual EN/GA toggle (5 Celtic TODOs)
├── demo_recorder.py        # Programmatic demo recording
├── baml_client.py          # 3-tier HF Inference fallback chain
├── baml/
│   └── clients_hackathon.baml   # BAML source-of-truth for the same chain
└── README.md               # (this file)
```

## Usage from a Space

```python
# spaces/an_scrudu/app.py
import gradio as gr
from spaces._common import (
    apply_celtic_theme, GRADIO_CSS,
    render_anam_bonneagar_footer,
    render_social_card,
    I18N_STRINGS, translate, set_lang,
    chat_complete, get_hackathon_client_config,
)

with gr.Blocks(theme=apply_celtic_theme(), css=GRADIO_CSS) as demo:
    # ... Space body ...
    render_anam_bonneagar_footer(space_id="cianfhoghlaim/an-scrudu")
    set_lang("ga")  # toggle to Gaeilge
    gr.Markdown(translate("space1.title"))
```

## Model Layer (3-tier fallback)

| Tier | Model | Params | Role |
|:-|:--|:-:|:-:|
| 1 (primary) | `Qwen/Qwen2.5-7B-Instruct` | 7.6B | Fast JSON, strong structured output |
| 2 (fallback) | `meta-llama/Llama-3.1-8B-Instruct` | 8.1B | Broad coverage, multilingual |
| 3 (fallback) | `google/gemma-2-9b-it` | 9.2B | Safety-tuned, last resort |

All three are **≤32B** (the hackathon ceiling). All three live on
HuggingFace Inference — no local model server, no GPU in the Space.

Triggers for fallback:
- HTTP timeout (60s default)
- 5xx response
- 429 rate limit (after 1 retry)
- JSON schema parse failure

The chain is implemented twice (once in BAML source for type safety,
once in `baml_client.py` for the Gradio runtime), so the source of
truth is the `.baml` file and the Python is the runtime mirror.

## 5-Element Connective Tissue

| Element | Color | Token | Space |
|:--|:--|:--|:--|
| **Talamh** (Earth) | `#28955e` emerald | `--celtic-emerald` | Space 1 (An Scrúdú) |
| **Uisce** (Water) | `#1e80c6` azure | `--celtic-azure` | Space 2 (Meaisín Cliste, Scoil theme) |
| **Tine** (Fire) | `#d68c1c` amber | `--celtic-amber` | Space 4 (OCR Gaelscríbhneoir) |
| **Aer** (Air) | `#5a4fcf` indigo | `--celtic-indigo` | Space 2 (Foclóir + Curaclam) + Space 3 |
| **Anam** (Spirit) | `#cc9966` gold | `--celtic-gold` | Space 3 + Space 4 (soulbound) |

These map to the Five Elements framework in
`docs/bunchloch/tuatha/learn-to-earn-model.md:224-233`.

## "Anam Bonneagar" Footer (Trust Signal)

The footer is the **architectural homage** to the 3-way secret contract
and 6-file linter, both of which are *deferred* for this hackathon.
What the footer actually shows:

1. **Space slug** (e.g. `cianfhoghlaim/an-scrudu`)
2. **Pobal HP Deprivation Index 2022** for the home county (Dublin 8, -9.8)
3. **Model alias + param count** (asserts ≤32B)
4. **Bun+uv+Turbo monorepo SHA** (current HEAD, e.g. `e9a24d0ac`)
5. **6-file linter score** (stubbed at 97.2% — to be wired in Day 6)
6. **3-way secret contract** label (Infisical dev-baile)
7. **Tamper-evident hash** (SHA-256 of `SPACE_ID-anam-bonneagar`)

The infrastructure quadrant is ARCHIVED for this hackathon (see
`doc/hackathons/build-small-2026-plan.md`); the footer is the visible
artifact of the deferred design.

## Anam Soulbound SVG (ERC-5192 mirror)

Mirrors the on-chain logic in
`tuatha/apps/crypteolas_demo/anam-contracts/src/CuchulainnNFT.sol:1-231`:

- **Sétanta** (juvenile): single ring + Anam center
- **Cúchulainn** (warrior): 3 rings + spear
- **Ríastrad** (warp spasm): full triskelion + crimson core

Deterministic given `(stage, wallet_short)` — the on-chain base64 is
computed from the same algorithm. The Space renders it client-side;
no on-chain transaction is needed (Anvil sidecar is local-only).

## Bilingual EN/GA (with 5 Celtic TODOs)

The hackathon scope is **EN + Gaeilge** as the active pair, with 5 other
Celtic languages (Manx, Scottish, Welsh, Cornish, Breton) as typed
placeholders. The pattern is from `croilar/packages/i18n/`:
typed dict, no missing-key crashes, EN fallback with `(TODO: <lang>)` marker.

## Demo Recording

`demo_recorder.py` provides a programmatic way to record demo sequences
for the 4 Spaces. Each Space gets a `record_demo.py` shim that builds
a `DemoSequence`, renders a storyboard PNG, and exports a voiceover
script. The actual YouTube video is human-narrated (Day 6).

## Environment Variables

| Variable | Required? | Purpose |
|:--|:-:|:--|
| `HF_TOKEN` | **Yes** | HuggingFace Inference API key (write-only Space secret) |
| `HF_INFERENCE_URL` | No | Override the Inference base URL (default: `https://api-inference.huggingface.co`) |
| `SPACE_ID` | No | HF Space slug (used for the tamper hash; defaults to `dev-baile`) |

## License

Inherits from the monorepo root license. All 4 Spaces ship under the same terms.
