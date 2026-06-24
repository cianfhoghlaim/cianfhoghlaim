# spaces/_common/ — Shared bundle

## Priority quick reference

The 5 shared modules, the 3 priority skills, the 4 priority
commands at a glance. **Read this first**.

### Shared modules (5)

| Module | Exports | Purpose |
|:--|:--|:--|
| `baml_client.py` | `chat_complete_json`, `get_hackathon_client_config` | The LiteLLM gateway shim (primary tier) + HF Inference 3-tier fallback (offline mode) |
| `theme.py` | `CELTIC_PALETTE`, `HADES_PALETTE`, `GRADIO_CSS`, `apply_celtic_theme` | The Celtic 5-element palette (Talamh / Uisce / Tine / Aer / Anam) + the Hades Shadow-First base |
| `anam_bonneagar.py` | `render_anam_bonneagar_footer` | The 5-fact trust-signal footer (Pobal HP + 32B ceiling + commit SHA + OpenSpec linter score) |
| `soulbound_svg.py` | `render_soulbound_svg` | The deterministic Celtic-knot SVG (Anam wallet) |
| `i18n.py` | `I18N_STRINGS`, `translate`, `set_lang` | The bilingual EN/GA toggle |

### Priority skills (3 of 108)

| Skill | When to load |
|:--|:--|
| [`motherduck-connections`](../../.agents/skills/motherduck-connections/SKILL.md) | Wire the LiteLLM gateway (the Spaces' primary LLM tier) |
| [`agent-observability`](../../.agents/skills/agent-observability/SKILL.md) | Langfuse auto-traces every LiteLLM call |
| [`browser-tools`](../../.agents/skills/browser-tools/SKILL.md) | The 5-element palette is the Spaces' visual identity (apply via `apply_celtic_theme`) |

### ccc + openspec commands

```bash
bun run ccc:search "Celtic 5-element palette"        # find prior art
openspec list --specs                               # 32 specs total
openspec validate <change-id> --strict              # MUST pass before commit
openspec archive <change-id> --yes                  # after deploy
```

## How the Spaces use _common

Each of the 4 active Spaces imports from `spaces._common`:

```python
from spaces._common import (
    apply_celtic_theme,        # the Celtic 5-element palette
    GRADIO_CSS,                # the Hades Shadow-First CSS
    render_anam_bonneagar_footer,  # the 5-fact trust-signal footer
    translate, set_lang,       # the bilingual EN/GA toggle
    chat_complete_json,        # the LiteLLM gateway shim
    get_hackathon_client_config,  # for the UI display
)
```

## Cross-references

- [`../AGENTS.md`](../AGENTS.md) — the Spaces parent
- [`../../openspec/AGENTS.md`](../../openspec/AGENTS.md) — the openspec workflow
- [`../../.agents/skills/browser-tools/SKILL.md`](../../.agents/skills/browser-tools/SKILL.md) — the browser tools router
- [`../../.agents/skills/motherduck-connections/SKILL.md`](../../.agents/skills/motherduck-connections/SKILL.md) — the LiteLLM gateway wiring
