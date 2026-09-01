---
name: chrome-devtools
description: Use the chrome MCP server (chrome-devtools-mcp) to verify deployed sites, take screenshots, capture accessibility snapshots, run Lighthouse audits, and profile Core Web Vitals. The 28+ chrome_* tools cover navigation, screenshot, a11y tree snapshots, JS evaluation, network request inspection, console message inspection, performance tracing, heapsnapshots, and viewport emulation. Load this skill when an agent needs to "check if the site is deployed", "screenshot the hero section", "find the broken link", "audit LCP/INP/CLS", or "open Chrome on a URL". Triggers: 'screenshot', 'verify deployment', 'lighthouse', 'performance trace', 'a11y snapshot', 'console error', 'core web vitals', 'CWV', 'heap snapshot'.
---

# chrome-devtools MCP

Use the `chrome-devtools-mcp` server (`bunx -y chrome-devtools-mcp`,
or the `npx chrome-devtools-mcp` variant) to drive a real
Chromium browser from inside an MCP-aware agent (opencode, Cursor,
Claude Desktop, etc.). The server exposes 28+ tools that wrap the
Chrome DevTools Protocol (CDP) so the agent can navigate, snapshot,
interact, audit, and profile any reachable URL — without spinning
up its own Playwright/Crawl4AI session.

## §1. Overview

The `chrome-devtools-mcp` server is the **CDP-native** member of
Cianfhoghlaim's browser-tooling stack. It speaks the Chrome DevTools
Protocol directly, so:

- Every action targets a real Chromium instance (not a headless
  WebKit/Firefox as some other MCP servers do).
- Snapshots use the **accessibility tree** (the same tree the
  browser's accessibility layer exposes to screen readers) — robust
  to CSS changes, works for JS-rendered pages.
- Network + console messages are first-class — you can grep every
  4xx/5xx or `console.error` emitted since the last navigation
  without writing a custom tracer.

**Relation to the other browser tools:**

| Tool | When to prefer chrome-devtools-mcp instead |
|:--|:--|
| **Playwright / CDP** (`browser-tools` skill) | When the agent needs fine-grained control over cookies, multi-context isolation, or a self-hosted Chromium. |
| **Firecrawl MCP** | When the task is "scrape this URL to markdown/JSON" — Firecrawl is one-shot, chrome-devtools-mcp is interactive. |
| **Firecrawl `/interact`** | When the flow is short (single page, simple click sequence). For multi-step flows with rich feedback (a11y snapshots between steps, console inspection), chrome-devtools-mcp wins. |
| **Crawl4AI** | When the task is batch scraping across many URLs. chrome-devtools-mcp is for one browser session at a time. |
| **Crawl4AI MCP** | When the agent is inside an MCP runtime but the page is purely static — Crawl4AI is faster (no JS round-trip). |

**Cost / setup:** `$0` — the server runs locally, talks to a local
Chromium instance. Wire it into opencode by adding it under
`mcp.chrome` in `opencode.json`:

```json
{
  "mcp": {
    "chrome": {
      "command": "bunx",
      "args": ["-y", "chrome-devtools-mcp"]
    }
  }
}
```

## §2. The 28+ tools, grouped by category

### Navigation

| Tool | Purpose |
|:--|:--|
| `chrome_navigate_page` | Navigate to a URL, back/forward, or reload. Supports `initScript` for pre-navigation JS. |
| `chrome_new_page` | Open a new tab (foreground, background, or isolated browser context). |
| `chrome_close_page` | Close a tab by `pageId`. The last open page cannot be closed. |
| `chrome_select_page` | Select an open page as the target for subsequent tool calls. |
| `chrome_list_pages` | List all open tabs/pages. |

### Snapshot / screenshot

| Tool | Purpose |
|:--|:--|
| `chrome_take_snapshot` | **Accessibility-tree snapshot** — the canonical way to read the page. Each element gets a `uid` for subsequent click/fill calls. Pass `verbose: true` for the full a11y tree. |
| `chrome_take_screenshot` | PNG / JPEG / WebP screenshot of the viewport, an element by `uid`, or the full page (`fullPage: true`). Element-scoped screenshots are perfect for design-review diffs. |
| `chrome_take_heapsnapshot` | Capture a V8 heap snapshot for memory-leak forensics. Writes a `.heapsnapshot` file. |

### Interaction

| Tool | Purpose |
|:--|:--|
| `chrome_click` | Click an element by `uid`. Supports `dblClick: true`. |
| `chrome_fill` | Type into an input / textarea / select. Pass `"true"` / `"false"` for checkboxes. |
| `chrome_fill_form` | **Batch fill** multiple form elements in a single call — strongly preferred over multiple `fill` calls (fewer round trips, atomic). |
| `chrome_hover` | Hover over an element — useful for triggering tooltips, dropdowns, focus rings. |
| `chrome_drag` | Drag one element onto another (`from_uid` → `to_uid`). |
| `chrome_upload_file` | Upload one or more local file paths to a `<input type="file">` (or any element that opens a chooser). |
| `chrome_press_key` | Press a key combo — `Enter`, `Tab`, `Control+A`, `Control+Shift+R`, etc. |
| `chrome_type_text` | Keyboard typing into the currently focused element. Useful after `chrome_click` focuses a non-input. |

### Execution

| Tool | Purpose |
|:--|:--|
| `chrome_evaluate_script` | Run a JS function inside the page. Returns must be JSON-serializable. Use `dialogAction` to handle `alert/confirm/prompt` triggered by the script. |
| `chrome_handle_dialog` | Respond to a `beforeunload` / `alert` / `confirm` / `prompt` triggered by navigation or JS. |

### Performance

| Tool | Purpose |
|:--|:--|
| `chrome_performance_start_trace` | Start a Chrome Performance recording. Pass `reload: true` to reload as part of the trace, `autoStop: true` to finish when the page settles, and `filePath` to persist the trace JSON. |
| `chrome_performance_stop_trace` | End the recording, optionally persist the trace. |
| `chrome_performance_analyze_insight` | Drill into one insight (`LCPBreakdown`, `DocumentLatency`, etc.) on a recorded trace. |

> Lighthouse performance is **not** in `chrome_performance_*` — use `chrome_lighthouse_audit` for perf or `chrome_performance_start_trace` for raw traces.

### Audit

| Tool | Purpose |
|:--|:--|
| `chrome_lighthouse_audit` | Run a Lighthouse audit. Covers **accessibility, SEO, best-practices, agentic-browsing**. **Performance is excluded** by design — use `chrome_performance_start_trace` for that. |

### Network

| Tool | Purpose |
|:--|:--|
| `chrome_list_network_requests` | List recent requests since the last navigation. Filter by `resourceTypes` (document, stylesheet, image, xhr, fetch, etc.), paginate with `pageSize` / `pageIdx`. |
| `chrome_get_network_request` | Drill into one request — headers, status, response body. Persist bodies to disk with `requestFilePath` / `responseFilePath`. |

### Console

| Tool | Purpose |
|:--|:--|
| `chrome_list_console_messages` | List console messages (`log`, `debug`, `info`, `warn`, `error`, etc.) since the last navigation. Filter by `types`, include stack traces. |
| `chrome_get_console_message` | Get one message by id — for the full body and stack trace. |

### Emulation

| Tool | Purpose |
|:--|:--|
| `chrome_emulate` | Emulate network throttling (`Slow 3G`, `Fast 4G`), CPU slowdown (1–20×), geolocation, user agent, color scheme (light/dark/auto), viewport (mobile/tablet/desktop with `,mobile`, `,touch`, `,landscape` modifiers), and injected HTTP headers. |
| `chrome_resize_page` | Resize the page viewport (`width`, `height`) — useful when `chrome_emulate`'s viewport shorthand isn't expressive enough. |

### Inspection

| Tool | Purpose |
|:--|:--|
| `chrome_wait_for` | Block until one of the listed texts appears on the page, or until the timeout fires. Use after `chrome_click` for SPAs that need to settle. |

## §3. Decision tree

```
Need to verify a deployed site renders?
  → chrome_navigate_page + chrome_take_snapshot + chrome_list_console_messages
  → If errors: drill into chrome_get_console_message for the stack trace.

Need to capture a screenshot for design review?
  → chrome_take_screenshot(format: "png", fullPage: true) for the full page,
    or pass uid: for a single component.

Need to find a broken link / failed asset?
  → chrome_list_network_requests, filter status 4xx/5xx,
    then chrome_get_network_request to see the response body.

Need to capture Core Web Vitals (LCP / INP / CLS)?
  → chrome_performance_start_trace(reload: true, autoStop: true)
    → wait for the trace to finish
    → chrome_performance_analyze_insight for LCPBreakdown, DocumentLatency, etc.

Need to audit accessibility / SEO / best-practices?
  → chrome_lighthouse_audit(mode: "navigation", device: "mobile").
  → Performance is excluded — use the trace workflow above for that.

Need to drive a multi-step flow (login, click-through, checkout)?
  → chrome_navigate_page + chrome_take_snapshot → chrome_click / chrome_fill /
    chrome_fill_form → chrome_take_snapshot (re-read the DOM) → repeat.
  → Spawn a fresh isolated context with chrome_new_page(isolatedContext: ...)
    if the flow needs its own cookies.

Need to inspect memory leaks?
  → chrome_take_heapsnapshot at t0, perform the suspect action,
    chrome_take_heapsnapshot at t1, diff in DevTools externally.

Need to test a mobile layout?
  → chrome_emulate(viewport: "375x812x2,mobile,touch") then snapshot/screenshot.
```

## §4. Cianfhoghlaim integration

Cianfhoghlaim's `browser-tools` skill (`SKILL.md`) routes between
**6 backends** for browser automation. The `chrome-devtools-mcp`
backend slots in as a **7th** — the one to reach for when:

- The agent already lives in an MCP-aware runtime (opencode,
  Cursor, Claude Desktop) and you don't want to spawn a Python
  subprocess to drive Playwright.
- The task is **interactive verification** of an already-deployed
  site: "did the last PR break the hero section?", "what does
  the build look like on iPhone 13?", "did the Lighthouse a11y
  score regress below 90?"
- The task requires **CDP-specific** introspection: heap
  snapshots, full performance traces with insight drill-down,
  per-request response bodies.
- The user wants a screenshot for **design review** (full page or
  element-scoped) — chrome-devtools-mcp renders with the exact
  browser engine the user has installed locally.

**When NOT to prefer it** (use the other browser-tools backends):

- Batch scraping 10k URLs → **Crawl4AI REST**.
- Multi-page research synthesis with `web search + scrape` →
  **Firecrawl MCP**.
- Authenticated flows with persistent cookies across many
  isolated profiles → **Playwright CDP** (more flexible).
- Anti-bot / JS-heavy one-shot scrape → **Firecrawl** (managed
  proxy pool).

Pair this skill with:

- `.agents/skills/browser-tools/SKILL.md` — the high-level router
  (which backend to pick overall)
- `.agents/skills/web-perf/SKILL.md` — for Core Web Vitals
  interpretation once you have a trace
- `.agents/skills/crawl4ai/SKILL.md` — for batch / static-page
  alternatives

## §5. Quickstart — example calls

### Verify a deployed site

```text
chrome_navigate_page(type: "url", url: "https://cianfhoghlaim.example.com")
chrome_take_snapshot()                            # a11y tree
chrome_list_console_messages(types: ["error", "warn"])
chrome_list_network_requests(resourceTypes: ["xhr", "fetch", "document"])
```

### Screenshot the hero on mobile

```text
chrome_new_page(url: "https://cianfhoghlaim.example.com")
chrome_emulate(viewport: "390x844x3,mobile,touch")
chrome_wait_for(text: ["Hero"])
chrome_take_screenshot(format: "png", fullPage: true,
                       filePath: "./hero-mobile.png")
```

### Find the broken link

```text
chrome_list_network_requests(pageSize: 200)       # 200 reqs is plenty for one page
# filter client-side: status >= 400
chrome_get_network_request(reqid: <id>)            # inspect body
```

### Profile LCP

```text
chrome_performance_start_trace(reload: true, autoStop: true,
                               filePath: "./trace.json")
# wait ~5–10s
chrome_performance_analyze_insight(insightSetId: <id>,
                                   insightName: "LCPBreakdown")
```

### Audit accessibility

```text
chrome_navigate_page(type: "url",
                     url: "https://cianfhoghlaim.example.com")
chrome_lighthouse_audit(mode: "navigation", device: "mobile",
                        outputDirPath: "./lh-report")
```

### Drive a multi-step flow (login + screenshot)

```text
chrome_navigate_page(type: "url", url: "https://app.cianfhoghlaim.example.com/login")
chrome_take_snapshot()                            # get uids for the form
chrome_fill_form(elements: [
  {uid: <email_uid>,    value: "<email>"},
  {uid: <password_uid>, value: "<password>"}
])
chrome_click(uid: <submit_uid>)
chrome_wait_for(text: ["Dashboard"])
chrome_take_screenshot(filePath: "./after-login.png")
```

## §6. Smoke task reference

The MCP smoke task for this server is `mise run mcp:smoke:chrome`
(per `mise.toml`). It opens a localhost URL, navigates to a known
page, takes an a11y snapshot, lists console messages, and asserts
zero errors. Run it after a fresh `bunx -y chrome-devtools-mcp`
install, or as part of the post-deploy gate.

If `mise run mcp:smoke:chrome` is not yet defined in the repo,
add it under `[tasks.mcp.smoke]` in `mise.toml` and have it call
`bun ./scripts/mcp_smoke/chrome_smoke.ts` (or a Python equivalent
in `scripts/mcp_smoke/`). The smoke covers: navigate, snapshot,
console-list, screenshot, lighthouse (if enabled).
