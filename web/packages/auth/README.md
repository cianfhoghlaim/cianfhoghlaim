# @cianfhoghlaim/auth — Better Auth 1.7 + Convex integration

Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1**
openspec change. The canonical Better Auth client + server config for
the Cianfhoghlaim platform.

## Setup

```bash
bun add @cianfhoghlaim/auth
```

The server-side config lives at `web/hono-api/src/auth.ts`. The
client-side React client is re-exported from this package:

```tsx
import { authClient } from "@cianfhoghlaim/auth";

export function SignInButton() {
  return (
    <button onClick={() => authClient.signIn.social({ provider: "pocket-id" })}>
      Sign in
    </button>
  );
}
```

## Convex integration

This package has `convex` as a peer dependency so it can integrate
with the Convex auth adapter at `web/packages/db/convex/auth.ts`.
Per the Better Auth docs (https://www.better-auth.com/docs/integrations/convex):

```ts
// web/packages/db/convex/auth.ts
import { createClient, type GenericCtx } from "@convex-dev/better-auth";
import { convex } from "@convex-dev/better-auth/plugins";
import authConfig from "../../hono-api/src/auth";

export const authClient = createClient({
  authConfig,
  triggers: { user: { create: ... } },
  plugins: [convex()],
});
```

## 3 OIDC audiences

Per the master plan, the 3 OIDC audiences are:
- `convex_backend` (the Convex backend)
- `croilar_web` (the croilar-web app)
- `croilar_portal` (the croilar-portal app)

The 5 consolidated web apps (`cianfhoghlaim`, `oideachais`, `croilar`,
`tuatha`, `game_showcase`) all consume this single auth client.
