---
name: marimo-embed
description: Pick the right strategy for embedding marimo notebooks in the cianfhoghlaim web apps — iframe vs islands vs WASM. Covers the marimo-server-on-Pangolin pattern (Pocket ID OIDC + sandboxed iframe), the Cloudflare Pages WASM export pattern, and the MarimoIslandGenerator for static SSG embeds. Use when the user asks to "embed a marimo notebook in the web app", "mount the Stage-F dashboards", "share a notebook", or any task involving rendering a marimo .py file inside a React/TanStack Start page.
---

# Marimo Embed

**Version**: 0.14.x (2026-09) | **Upstream**: https://docs.marimo.io/guides/publishing/embedding/
**Companion skill**: `marimo-notebook` (covers authoring + patterns inside .py notebooks)

The cianfhoghlaim dev environment has 3 patterns for embedding marimo notebooks.
Pick by use case:

## 1. The 4 strategies

| Strategy | Best for | Implementation |
|:--|:--|:--|
| **molab iframe** (recommended upstream) | One-off sharing, public notebooks | `https://marimo.app/github/<repo>/blob/main/<nb>.py/wasm?embed=true` — but requires the repo to be **public** on GitHub |
| **WASM HTML export** | Static dashboard surfaces, public notebooks, no server deps | `marimo export html-wasm <nb>.py -o dist/ --include-cloudflare` → deploy to Cloudflare Pages |
| **Marimo Islands** | Embed individual cells in our own TSX pages | `<marimo-island data-app-id data-cell-id>` custom elements + CDN script + payload script |
| **Server-served iframe** (recommended for cianfhoghlaim) | Operational dashboards that call LLM APIs + DuckLake | iframe our own `:2718/notebooks/<path>` with the marimo-recommended sandbox |

The 15 Stage-F dashboards (5 tertiary ADK 2 deep-research + 5 K-12 teacher + 5 K-12 student)
+ the VLM benchmark notebook are **operational** — they call `agents.workflows.*` and
read from DuckLake. **Use strategy #4** (server-served iframe).

## 2. Server-served iframe (the canonical cianfhoghlaim pattern)

The marimo server (`:2718`) runs inside the bunchloch docker network. Expose it as a
Pangolin **private resource** (`marimo.cianfhoghlaim.ie`) gated by Pocket ID OIDC
(via the Pangolin + Tinyauth middleware stack). Inside our TanStack Start app, the
dashboard route renders a sandboxed iframe pointing at the marimo server URL.

### The recommended sandbox attribute set

Per https://docs.marimo.io/guides/publishing/embedding/, the **minimum** attribute is
`allow-scripts`. The **recommended** set is:

```html
<iframe
  src="https://marimo.cianfhoghlaim.ie/notebooks/notebooks/_shared/tertiary/walkthroughs/adk2_jc_deep_research_dashboard.py"
  sandbox="allow-scripts allow-same-origin allow-downloads allow-popups allow-forms"
  allow="microphone"
  allowfullscreen
  width="100%"
  height="600"
/>
```

| Attribute | Why |
|:--|:--|
| `allow-scripts` | Required for JS execution |
| `allow-same-origin` | Persistent localStorage + clipboard API (only safe if the iframe URL is on a different domain OR you trust it) |
| `allow-downloads` | Notebook output CSV exports + screenshots |
| `allow-popups` | Open links in new tabs |
| `allow-forms` | Interactive `mo.ui.form` cells |
| `allowfullscreen` | Slides + outputs in fullscreen |
| `allow="microphone"` | `mo.ui.microphone()` widget |

### Security note

> Only use `allow-same-origin` with trusted content. Combining `allow-scripts` and
> `allow-same-origin` allows the iframe to remove the sandbox attribute entirely,
> making the iframe as powerful as if it weren't sandboxed at all.

Since `marimo.cianfhoghlaim.ie` is a Pangolin private resource that the operator
already controls, `allow-same-origin` is safe.

## 3. The 3 Pangolin + Tinyauth + Pocket ID layers

1. **Tinyauth** (the auth layer in the Pangolin stack): Pocket ID OIDC SSO on every
   request to `*.cianfhoghlaim.ie`. Users log in once.
2. **Pangolin**: routes `marimo.cianfhoghlaim.ie` → the marimo container (`:2718`).
3. **Marimo**: the actual notebook server.

## 4. Implementation pattern (TanStack Start)

```tsx
// web/apps/cianfhoghlaim-web/apps/web/src/routes/en/dashboards/$stage.tsx
export const Route = createFileRoute("/en/dashboards/$stage")({
  component: DashboardComponent,
});

function DashboardComponent() {
  const { stage } = Route.useParams();
  const notebookPath = `notebooks/_shared/${stage}/walkthroughs/${stage}_dashboard.py`;
  const url = `https://marimo.cianfhoghlaim.ie/${notebookPath}`;
  return (
    <div className="max-w-5xl mx-auto">
      <iframe
        src={url}
        sandbox="allow-scripts allow-same-origin allow-downloads allow-popups allow-forms"
        allow="microphone"
        allowfullscreen
        width="100%"
        height="800"
        style={{ border: "1px solid #ddd", borderRadius: "8px" }}
      />
    </div>
  );
}
```

## 5. The 3 unsupported-by-marimo patterns to AVOID

- **WASM export of operational dashboards** — they import `agents.workflows.*` which
  won't load in Pyodide (no DuckLake access, no LLM API key pass-through).
- **molab iframe of private repos** — the repo must be public.
- **`<iframe src="http://localhost:2718/...">`** — won't work for users on other
  devices; only the operator's own browser sees the local container.

## 6. MarimoIslandGenerator (for blog-post-style embeds)

When you want to embed **individual cell outputs** in static content (blog posts,
docs, MDX), use `MarimoIslandGenerator` + the JS custom elements:

```html
<head>
  <script type="module" src="https://cdn.jsdelivr.net/npm/@marimo-team/islands@<version>/dist/main.js"></script>
  <link href="https://cdn.jsdelivr.net/npm/@marimo-team/islands@<version>/dist/style.css" rel="stylesheet">
</head>
<body>
  <marimo-island data-app-id="main" data-cell-id="MJUe" data-reactive="true">
    <marimo-cell-output><span class="markdown">Hello, islands!</span></marimo-cell-output>
  </marimo-island>
</body>
```

Per https://docs.marimo.io/guides/exporting/webassembly_html/#embed-marimo-outputs-in-html-using-islands

## 7. When to use this skill

Activate when the user asks about:
- "mount the Stage-F dashboards in the web app"
- "embed this notebook in the React page"
- "share this notebook publicly"
- "deploy marimo on Cloudflare Pages"
- "set up the marimo server behind Pangolin"
- "use MarimoIslandGenerator for the docs"

## Reference

- Upstream embed docs: https://docs.marimo.io/guides/publishing/embedding/
- Upstream WASM export: https://docs.marimo.io/guides/exporting/webassembly_html/
- Upstream Publishing: https://docs.marimo.io/guides/publishing/
- Spec: `openspec/specs/marimo-pangolin-embed/spec.md`
