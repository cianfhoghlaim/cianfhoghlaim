# Embedded Dashboards Example

This example demonstrates how to embed self-hosted dashboards (marimo notebooks and Dagster pipelines) in a TanStack Start application using BetterAuth for authentication, oRPC for type-safe APIs, and proxy patterns for secure embedding.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TanStack Start App                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  BetterAuth │  │    oRPC     │  │   Proxy Routes      │  │
│  │  Session    │  │  Dashboard  │  │  /api/proxy/marimo  │  │
│  │  Validation │  │  Management │  │  /api/proxy/dagster │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│    Marimo       │ │     Dagster     │ │    PostgreSQL   │
│   Container     │ │   Webserver     │ │                 │
│   (port 8080)   │ │   (port 3001)   │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Key Features

### Authentication Flow
1. User authenticates via BetterAuth (email/password or social)
2. Session cookie is set for subsequent requests
3. Proxy routes validate session before forwarding to services
4. Dashboards are embedded in iframes with modified security headers

### Security Headers
The proxy modifies response headers to allow safe iframe embedding:
- Removes restrictive `X-Frame-Options`
- Sets `Content-Security-Policy` with `frame-ancestors 'self'`
- Maintains CORS headers for authenticated requests

### oRPC Integration
Type-safe API endpoints for dashboard management:
- `listDashboards` - Get available dashboards
- `getDashboard` - Get specific dashboard config
- `getDashboardStatus` - Check service health
- `getEmbedConfig` - Get iframe embedding attributes

## Getting Started

### Prerequisites
- Node.js 18+
- Docker and Docker Compose
- pnpm (recommended)

### Installation

```bash
# Install dependencies
pnpm install

# Start the dashboard services
pnpm run docker:up

# Start the development server
pnpm run dev
```

### Environment Variables

Create a `.env` file:

```env
# BetterAuth (optional for social login)
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# Service URLs (defaults shown)
MARIMO_URL=http://localhost:8080
DAGSTER_URL=http://localhost:3001
```

## Project Structure

```
embedded-dashboards/
├── src/
│   ├── routes/
│   │   ├── __root.tsx              # Root layout with navigation
│   │   ├── index.tsx               # Landing/auth page
│   │   ├── dashboards.tsx          # Dashboard selection
│   │   ├── marimo.tsx              # Marimo embedding page
│   │   ├── dagster.tsx             # Dagster embedding page
│   │   ├── api.auth.$.ts           # BetterAuth handler
│   │   ├── api.rpc.$.ts            # oRPC handler
│   │   ├── api.proxy.marimo.$.ts   # Marimo proxy
│   │   └── api.proxy.dagster.$.ts  # Dagster proxy
│   ├── lib/
│   │   ├── auth.ts                 # BetterAuth server config
│   │   ├── auth-client.ts          # BetterAuth client hooks
│   │   ├── auth-server.ts          # Server functions for auth
│   │   └── proxy.ts                # Proxy utilities
│   ├── components/
│   │   ├── EmbeddedDashboard.tsx   # Iframe embedding component
│   │   └── AuthForm.tsx            # Authentication form
│   └── orpc/
│       ├── router.ts               # oRPC router definitions
│       └── client.ts               # oRPC client setup
├── container/
│   ├── Dockerfile.marimo           # Marimo container
│   ├── Dockerfile.dagster          # Dagster webserver
│   ├── Dockerfile.dagster-user-code # Dagster user code
│   ├── dagster.yaml                # Dagster instance config
│   ├── workspace.yaml              # Dagster workspace config
│   ├── definitions.py              # Example Dagster assets
│   └── notebooks/
│       └── analytics.py            # Example marimo notebook
├── docker-compose.yml              # Service orchestration
├── app.config.ts                   # TanStack Start config
└── package.json
```

## How the Proxy Works

### Request Flow

1. **Client Request**: User's browser makes request to `/api/proxy/marimo/path`
2. **Session Validation**: Proxy route checks for valid BetterAuth session
3. **Request Forwarding**: If authenticated, forwards to `http://localhost:8080/path`
4. **Header Modification**: Removes X-Frame-Options, adds CORS headers
5. **Response**: Modified response allows iframe embedding

### Code Example

```typescript
// src/lib/proxy.ts
export async function proxyRequest(
  request: Request,
  targetBaseUrl: string,
  pathPrefix: string
): Promise<Response> {
  // Validate session first
  const isAuthenticated = await validateSession();
  if (!isAuthenticated) {
    return new Response("Unauthorized", { status: 401 });
  }

  // Forward request
  const response = await fetch(targetUrl, {
    method: request.method,
    headers: forwardedHeaders,
    body: request.body,
  });

  // Modify security headers for iframe embedding
  return createProxyResponse(response);
}
```

## Embedding Component

The `EmbeddedDashboard` component provides:
- Loading state with spinner
- Error handling with retry
- Security sandboxing
- Lazy loading optimization

```tsx
<EmbeddedDashboard
  src="/api/proxy/marimo/"
  title="Analytics Dashboard"
  height="700px"
  onLoad={() => setStatus("connected")}
  onError={() => setStatus("error")}
/>
```

## Docker Services

### Marimo
- Interactive Python notebooks
- Runs with `--no-token` (auth handled by proxy)
- Port 8080

### Dagster
- **Webserver**: Port 3001 (mapped from 3000)
- **User Code**: gRPC on port 4000
- **Daemon**: Background job processing
- **PostgreSQL**: Metadata storage

## Production Considerations

1. **Authentication**: Configure proper auth providers (OAuth, SAML)
2. **HTTPS**: Use TLS for all communications
3. **CSP Headers**: Restrict `frame-ancestors` to your domain
4. **Rate Limiting**: Add rate limiting to proxy routes
5. **Secrets**: Use proper secret management (not env vars)
6. **Monitoring**: Add logging and metrics for proxy requests
7. **WebSocket Proxying**: For marimo real-time features, configure WebSocket proxying

## Extending

### Adding New Dashboard Types

1. Create Dockerfile in `container/`
2. Add service to `docker-compose.yml`
3. Add proxy route in `src/routes/api.proxy.[name].$.ts`
4. Add entry to `src/orpc/router.ts`
5. Create embedding page in `src/routes/[name].tsx`

### Custom Authentication

Replace BetterAuth with your auth provider by:
1. Modifying `src/lib/auth.ts` and `src/lib/auth-client.ts`
2. Updating `validateSession()` in `src/lib/proxy.ts`

## Troubleshooting

### Dashboard not loading
- Check Docker services are running: `docker-compose ps`
- Verify ports are not in use: `lsof -i :8080` / `lsof -i :3001`
- Check browser console for CORS errors

### Authentication issues
- Clear browser cookies and retry
- Check BetterAuth configuration
- Verify session is being set correctly

### Iframe security errors
- Check Content-Security-Policy headers
- Verify X-Frame-Options is removed
- Use browser dev tools Network tab to inspect response headers

## License

MIT
