---
name: browser
description: Automate web browser interactions using natural language via CLI commands. Use when the user asks to browse websites, navigate web pages, extract data from websites, take screenshots, fill forms, click buttons, or interact with web applications. Supports remote Browserbase sessions with Browserbase Identity, Verified browsers, automatic CAPTCHA solving, and residential proxies — ideal for protected websites and JavaScript-heavy pages.
compatibility: "Requires the browse CLI (`npm install -g browse`). Remote Browserbase sessions need `BROWSERBASE_API_KEY`. Local mode uses Chrome/Chromium on your machine."
license: MIT
allowed-tools: Bash
metadata:
  openclaw:
    requires:
      bins:
        - browse
    install:
      - kind: node
        package: "browse"
        bins: [browse]
    homepage: https://github.com/browserbase/skills
---

# Browser Automation

Automate browser interactions using the browse CLI with Claude.

## Setup check

Before running any browser commands, verify the CLI is available:

```bash
which browse || npm install -g browse
```

## Environment Selection (Local vs Remote)

The CLI supports explicit per-command environment flags. If you do nothing, the next session defaults to Browserbase when `BROWSERBASE_API_KEY` is set and to local otherwise.

### Local mode
- `browse open <url> --local` starts a clean isolated local browser
- `browse open <url> --auto-connect` attaches to an already-running debuggable Chrome; use `--local` when no debuggable Chrome is available
- `browse open <url> --cdp <port|url>` attaches to a specific CDP target
- Best for: development, localhost, trusted sites, and reproducible runs

### Remote mode (Browserbase)
- `browse open <url> --remote` starts a Browserbase session
- Without a local flag, Browserbase is also the default when `BROWSERBASE_API_KEY` is set
- Provides: Browserbase Identity, Verified browsers, automatic CAPTCHA solving, residential proxies, session persistence
- **Use remote mode when:** the target site has bot detection, CAPTCHAs, IP rate limiting, Cloudflare protection, or requires geo-specific access
- Get credentials at https://browserbase.com/settings

### When to choose which
- **Repeatable local testing / clean state**: `browse open <url> --local`
- **Reuse your local login/cookies**: `browse open <url> --auto-connect`
- **Simple browsing** (docs, wikis, public APIs): local mode is fine
- **Protected sites** (login walls, CAPTCHAs, anti-scraping): use remote mode
- **If local mode fails** with bot detection or access denied: switch to remote mode

## Commands

Most driver commands work across local, remote, and CDP sessions after the daemon starts.

### Navigation
```bash
browse open <url>                        # Go to URL
browse open <url> --local                # Go to URL in a clean local browser
browse open <url> --remote               # Go to URL in a Browserbase session
browse reload                            # Reload current page
browse back                              # Go back in history
browse forward                           # Go forward in history
```

### Page state (prefer snapshot over screenshot)
```bash
browse snapshot                          # Get accessibility tree with element refs (fast, structured)
browse screenshot --path <path>          # Take visual screenshot (slow, uses vision tokens)
browse get url                           # Get current URL
browse get title                         # Get page title
browse get text <selector>               # Get text content (use "body" for all text)
browse get html <selector>               # Get HTML content of element
browse get value <selector>              # Get form field value
```

Use `browse snapshot` as your default for understanding page state — it returns the accessibility tree with element refs you can use to interact. Only use `browse screenshot` when you need visual context (layout, images, debugging).

### Interaction
```bash
browse click <ref>                       # Click element by ref from snapshot (e.g., @0-5)
browse type <text>                       # Type text into focused element
browse fill <selector> <value>           # Fill input; add --press-enter if Enter is needed
browse select <selector> <values...>     # Select dropdown option(s)
browse press <key>                       # Press key (Enter, Tab, Escape, Cmd+A, etc.)
browse mouse drag <fromX> <fromY> <toX> <toY>  # Drag from one point to another
browse mouse scroll <x> <y> <deltaX> <deltaY>  # Scroll at coordinates
browse highlight <selector>              # Highlight element on page
browse is visible <selector>             # Check if element is visible
browse is checked <selector>             # Check if element is checked
browse wait <type> [arg]                 # Wait for: load, selector, timeout
```

### Session management
```bash
browse stop                              # Stop the browser daemon
browse status                            # Check daemon status and resolved mode
browse tab list                          # List all open tabs
browse tab switch <index-or-target-id>   # Switch to tab by index or target ID
browse tab close [index-or-target-id]    # Close tab
```

### Typical workflow
If the environment matters, put `--local`, `--remote`, `--auto-connect`, or `--cdp <port|url>` on the first browser command.

1. `browse open <url> --local` or `browse open <url> --remote` — navigate to the page
2. `browse snapshot` — read the accessibility tree to understand page structure and get element refs
3. `browse click <ref>` / `browse type <text>` / `browse fill <selector> <value>` — interact using refs from snapshot
4. `browse snapshot` — confirm the action worked
5. Repeat 3-4 as needed
6. `browse stop` — close the browser when done

## Quick Example

```bash
browse open https://example.com
browse snapshot                          # see page structure + element refs
browse click @0-5                        # click element with ref 0-5
browse get title
browse stop
```

## Mode Comparison

| Feature | Local | Browserbase |
|---------|-------|-------------|
| Speed | Faster | Slightly slower |
| Setup | Chrome required | API key required |
| Reuse existing local cookies | With `browse open <url> --auto-connect` | N/A |
| Verified browser | No | Yes (Browserbase Verified browser via Identity) |
| CAPTCHA solving | No | Yes (automatic reCAPTCHA/hCaptcha) |
| Residential proxies | No | Yes (201 countries, geo-targeting) |
| Session persistence | No | Yes (cookies/auth persist via contexts) |
| Best for | Development/simple pages | Protected sites, Browserbase Identity + Verified access, production scraping |

## Best Practices

1. **Choose the local strategy deliberately**: use `browse open <url> --local` for clean state, `browse open <url> --auto-connect` for existing local credentials, and `browse open <url> --remote` for protected sites
2. **Always `browse open` first** before interacting
3. **Use `browse snapshot`** to check page state — it's fast and gives you element refs
4. **Only screenshot when visual context is needed** (layout checks, images, debugging)
5. **Use refs from snapshot** to click/interact — e.g., `browse click @0-5`
6. **`browse stop`** when done to clean up the browser session and clear the env override

## Troubleshooting

- **"No active page"**: Run `browse stop`, then check `browse status`. If it still says running, kill the zombie daemon with `pkill -f "browse.*daemon"`, then retry `browse open`
- **Chrome not found**: Install Chrome, use `browse open <url> --auto-connect` if you already have a debuggable Chrome running, or switch to `browse open <url> --remote`
- **Action fails**: Run `browse snapshot` to see available elements and their refs
- **Browserbase fails**: Verify API key is set

## Switching to Remote Mode

Switch to remote when you detect: CAPTCHAs (reCAPTCHA, hCaptcha, Turnstile), bot detection pages ("Checking your browser..."), HTTP 403/429, empty pages on sites that should have content, or the user asks for it.

Don't switch for simple sites (docs, wikis, public APIs, localhost).

```bash
browse open <url> --local          # clean isolated local browser
browse open <url> --auto-connect   # attach to existing debuggable Chrome
browse open <url> --remote         # Browserbase session
```

Mode flags are applied when a session starts. After `browse stop`, the next start falls back to env-var-based auto detection. Use `browse status` to inspect the resolved mode and target while the daemon is running.

For detailed examples, see [EXAMPLES.md](EXAMPLES.md).
For API reference, see [REFERENCE.md](REFERENCE.md).

## Anti-Bot Fallback (patchright)

When the `browse` CLI is blocked by anti-bot detection
(Cloudflare, DataDome, PerimeterX, etc.), the canonical
fallback is **Patchright** — a stealth fork of Playwright that
patches the Chromium binary to bypass common detection
heuristics.

### When to use patchright

- The `browse` CLI returns a Cloudflare challenge or CAPTCHA
- The site uses `navigator.webdriver` detection
- Headless detection (e.g. via `navigator.plugins.length`)
- Datadome / PerimeterX anti-bot

### Pattern

```python
# patchright is a drop-in Playwright API replacement
from patchright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel="chromium")
    context = browser.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ...",
        viewport={"width": 1920, "height": 1080},
    )
    page = context.new_page()
    page.goto("https://protected-site.com")
    print(page.content())
    browser.close()
```

### Escalation path

```
browse CLI
   ↓ blocked by anti-bot
patchright (local Chromium)
   ↓ still blocked
stagehand + browserbase (cloud, residential proxies)
   ↓ still blocked
cua (computer-use agent)
```

### KCG integration

- `cookie-sync/package.json` pins `patchright-core@1.58.2`
  via `@browserbasehq/stagehand`
- The `infrastructure/stacks/stagehand/` stack
  provides a Cloudflare-Workers + patchright + browserbase
  fallback chain
- For one-off Cloudflare challenges, prefer
  `Browserbase.cloud` with the residential proxy pool

### KCG: What is wired today (status table)

The browser / scraping stack is **multi-backend by design**.
The 6 backends available to KCG agents (in escalation
order):

| # | Backend | When to use | Anti-bot | Cost |
|:--|:--|:--|:--|:--|
| 1 | `firecrawl` (HTTP) | First try for any page | No | Credits |
| 2 | `crawl4ai` (local browser) | No anti-bot + JS rendering | No | Free |
| 3 | `browse` CLI (local Chrome) | Reuse local cookies | No | Free |
| 4 | `browse` CLI (Browserbase) | Cloudflare / IP-blocked | Yes (residential proxy) | $$ |
| 5 | `patchright` (stealth Chromium) | Bot-detection bypass | Yes (patched) | Free |
| 6 | `stagehand` (Cloudflare Workers) | Cookie-gated / paywalled | Yes (residential) | $$$ |
| 7 | `cua` (computer-use agent) | Last resort (login flows) | Yes (genuine browser) | $$$$ |

The `BackendRacer` (below) fires #1-#3 in parallel and
returns the first success.

## BAML `SiteAnalysis` (the page-fingerprint pattern)

For every URL the browser pipeline visits, KCG extracts a
BAML `SiteAnalysis` record (the "fingerprint" of the page):

```baml
// oideachais/baml_src/site_analysis.baml
class SiteAnalysis {
  url: string
  title: string
  content_type: "article" | "documentation" | "api" | "form" | "search" | "other"
  primary_language: "en" | "ga" | "cy" | "gd" | "br" | "fr" | "de" | "other"
  has_anti_bot: bool
  has_login_wall: bool
  estimated_tokens: int
  llm_relevance: "high" | "medium" | "low" | "none"
  notes: string?
}

function FingerprintPage(html: string, url: string) -> SiteAnalysis {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Analyse the page at {{ url }}.

    Identify:
    - content_type (article / documentation / api / form / search / other)
    - primary_language (ISO 639-1, with Celtic codes for ga/cy/gd/br)
    - presence of anti-bot (Cloudflare, DataDome, reCAPTCHA, Turnstile)
    - presence of a login wall
    - estimated tokens to summarise
    - LLM relevance (high = dense pedagogical content, none = ads / nav)

    {{ html }}
    {{ ctx.output_format }}
  "#
}
```

The fingerprint decides:
- Whether to ingest the page at all (`llm_relevance: "none"` → skip)
- Which backend to use next (`has_anti_bot: true` → escalate)
- The asset key prefix (`primary_language: "ga"` → `oideachais.education.ie.curriculum.ga`)

## See also

- `.agents/skills/stagehand/SKILL.md` — the full Stagehand
  V3 reference (the canonical "next step up" from patchright)
- `.agents/skills/crawl4ai/SKILL.md` — the primary scraper
  (try first; falls back to patchright + stagehand)
- `.agents/skills/firecrawl/SKILL.md` — the HTTP-first
  scraper (no browser, no anti-bot issues for most sites)

## Multi-agent patterns (BrowserPipeline = SequentialAgent + LoopAgent)

The KCG production browser pipeline uses a 4-stage
multi-agent pattern (Hunter → Operator → Gatherer → Loop):

```python
# The canonical KCG multi-agent browser pipeline
# (see infrastructure/browser/sruth_browser/agents/orchestrator.py)

from google.adk.agents import SequentialAgent, LoopAgent, TerminationStrategy

# 1. Hunter — finds the page (crawl4ai, firecrawl, etc.)
hunter = Agent(name="Hunter", model="gemini-2.5-flash", tools=[crawl4ai])

# 2. Operator — runs the browser (stagehand + browserbase)
operator = Agent(name="Operator", model="gpt-4o", tools=[stagehand])

# 3. Gatherer — extracts the structured data (BAML)
gatherer = Agent(name="Gatherer", model="gpt-4o", tools=[baml_extractor])

# 4. Loop: Evaluator → Quality Checker → fallback Escalator
loop = LoopAgent(
    name="QualityLoop",
    sub_agents=[evaluator, quality_checker, fallback_escalator],
    termination=TerminationStrategy(
        stop_on=lambda out: "approved" in out,
        max_iterations=3,
    ),
)

# Full pipeline
pipeline = SequentialAgent(
    name="KCG Browser Pipeline",
    sub_agents=[hunter, operator, gatherer, loop],
)
```

Each agent has a single responsibility; the SequentialAgent
hands off state; the LoopAgent retries with a quality
fallback if the Gatherer output fails the RAGAS eval gate.

## Backend racing pattern (BackendRacer)

When multiple scraping backends are available (crawl4ai,
firecrawl, browserbase), the `BackendRacer` fires all in
parallel and uses whichever succeeds first:

```python
# From infrastructure/browser/sruth_browser/agents/durable_orchestrator.py

import asyncio


async def race_backends(url: str) -> str:
    """Fire all backends in parallel; return the first to succeed."""
    tasks = [
        asyncio.create_task(crawl4ai.scrape(url), name="crawl4ai"),
        asyncio.create_task(firecrawl.scrape(url), name="firecrawl"),
        asyncio.create_task(browserbase.scrape(url), name="browserbase"),
    ]

    done, pending = await asyncio.wait(
        tasks, return_when=asyncio.FIRST_COMPLETED,
    )

    # Cancel the slower backends
    for t in pending:
        t.cancel()

    # Return the first successful result
    for t in done:
        try:
            return t.result()
        except Exception:
            continue

    raise RuntimeError("All backends failed")
```

The BackendRacer is the canonical "fastest-backend-wins"
pattern for KCG browser scraping. See
`.agents/skills/pydantic-ai/SKILL.md` §"Restate + DBOS" for
how to make this durable.
