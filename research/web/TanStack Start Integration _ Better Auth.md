---
title: "TanStack Start Integration | Better Auth"
source: "https://www.better-auth.com/docs/integrations/tanstack"
author:
published:
created: 2025-12-29
description: "Integrate Better Auth with TanStack Start."
tags:
  - "clippings"
---
## TanStack Start Integration

This integration guide is assuming you are using TanStack Start.

Before you start, make sure you have a Better Auth instance configured. If you haven't done that yet, check out the [installation](https://www.better-auth.com/docs/installation).

### Mount the handler

We need to mount the handler to a TanStack API endpoint/Server Route. Create a new file: `/src/routes/api/auth/$.ts`

src/routes/api/auth/$.ts

```
import { auth } from '@/lib/auth'

import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/api/auth/$')({

  server: {

    handlers: {

      GET: ({ request }) => {

        return auth.handler(request)

      },

      POST: ({ request }) => {

        return auth.handler(request)

      },

    },

  },

})
```

### Usage tips

- We recommend using the client SDK or `authClient` to handle authentication, rather than server actions with `auth.api`.
- When you call functions that need to set cookies (like `signInEmail` or `signUpEmail`), you'll need to handle cookie setting for TanStack Start. Better Auth provides a `tanstackStartCookies` plugin to automatically handle this for you.

src/lib/auth.ts

Now, when you call functions that set cookies, they will be automatically set using TanStack Start's cookie handling system.

```
import { auth } from "@/lib/auth"

const signIn = async () => {

    await auth.api.signInEmail({

        body: {

            email: "user@email.com",

            password: "password",

        }

    })

}
```

### Middleware

You can use TanStack Start's middleware to protect routes that require authentication. Create a middleware that checks for a valid session and redirects unauthenticated users to the login page.

src/middleware/auth.ts

You can then use this middleware in your route definitions to protect specific routes:

src/routes/dashboard.tsx

```
import { createFileRoute } from '@tanstack/react-router'

import { authMiddleware } from '@/lib/middleware'

export const Route = createFileRoute('/dashboard')({

  component: RouteComponent,

  server: {

    middleware: [authMiddleware],

  },

})

function RouteComponent() {

  return <div>Hello "/dashboard"!</div>

}
```

[Edit on GitHub](https://github.com/better-auth/better-auth/blob/canary/docs/content/docs/integrations/tanstack.mdx)