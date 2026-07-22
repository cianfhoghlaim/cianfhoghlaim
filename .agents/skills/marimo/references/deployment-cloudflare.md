# Marimo on Cloudflare Workers + Container (KCG production)

The KCG production deployment for marimo is a Cloudflare
Worker that proxies requests to a marimo Container via a
Durable Object. This is the canonical "deploy a marimo
notebook as a public dashboard" pattern.

## Architecture

```
User's browser
       │
       │ HTTPS
       ▼
┌──────────────────┐
│  Cloudflare      │
│  Worker          │  ← src/index.ts (Durable Object)
└────────┬─────────┘
         │ fetch() / WebSocket
         ▼
┌──────────────────┐
│  marimo          │  ← Docker container (port 8080)
│  Container       │
│  (Dockerfile)    │
└──────────────────┘
```

## Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir marimo[server] pandas polars duckdb lancedb

COPY notebook.py /app/notebook.py

EXPOSE 8080
CMD ["marimo", "run", "notebook.py", "--host", "0.0.0.0", "--port", "8080"]
```

## wrangler.jsonc

```jsonc
{
  "name": "marimo-dashboard",
  "main": "src/index.ts",
  "compatibility_date": "2024-12-01",
  "durable_objects": {
    "bindings": [
      { "name": "MARIMO", "class_name": "MarimoContainer" }
    ]
  },
  "containers": [
    {
      "class_name": "MarimoContainer",
      "image": "./Dockerfile",
      "max_instances": 1
    }
  ]
}
```

## src/index.ts (Durable Object)

```typescript
export class MarimoContainer implements DurableObject {
  async fetch(request: Request): Promise<Response> {
    // The Worker has a TCP socket to the marimo Container on port 8080
    const url = new URL(request.url);
    return await fetch(`http://marimo-container.local:8080${url.pathname}${url.search}`, {
      method: request.method,
      headers: request.headers,
      body: request.body,
    });
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const id = env.MARIMO.idFromName("singleton");
    const obj = env.MARIMO.get(id);
    return obj.fetch(request);
  },
};
```

## KCG examples

- `infrastructure/stacks/marimo/` — the canonical
  KCG Cloudflare Workers + marimo stack
- `notebooks/` — example notebooks (curriculum,
  leabharlann, etc.) that follow this pattern
- The 5 educational-stage dashboards at
  `/dashboards/aistear|primary|junior_cycle|senior_cycle|tertiary`

## When to use this pattern

✅ **Use when:**
- The dashboard is public (or auth-gated via `web/apps/croilar-portal`)
- The dashboard is read-heavy (lots of users, few writes)
- You need global edge caching (Cloudflare's network)
- You're deploying to `arm1-oci` or a Cloudflare Enterprise
  customer

❌ **Don't use when:**
- The notebook needs a private DB connection (MotherDuck
  with a private token won't work behind a Worker)
- The notebook needs long-lived state (Durable Objects help
  but are not a full replacement for a server)
- The notebook requires GPU access (use Modal instead)

## Resources

- Cloudflare Workers + Containers: <https://developers.cloudflare.com/workers/runtime/apis/durable-objects/>
- Marimo server docs: <https://docs.marimo.io/guides/deploying/>
- KCG example: `infrastructure/stacks/marimo/`
