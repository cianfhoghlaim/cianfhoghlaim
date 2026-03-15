# Usage Examples

Real-world examples of using Cloudflare services in this unified application.

## Table of Contents

- [Authentication](#authentication)
- [Database Operations](#database-operations)
- [KV Caching](#kv-caching)
- [R2 File Storage](#r2-file-storage)
- [Workers AI](#workers-ai)
- [Geolocation](#geolocation)
- [Combined Examples](#combined-examples)

## Authentication

### Anonymous Login

```typescript
// Client-side JavaScript
const response = await fetch('/api/auth/sign-in/anonymous', {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({})
});

const { user, session } = await response.json();
console.log('Logged in as:', user.id);
```

### Email/Password Login

```typescript
// Client-side JavaScript
const response = await fetch('/api/auth/sign-in/email', {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'secure-password'
  })
});
```

### Check Session

```typescript
// Server-side in Hono route
app.get("/api/protected", async (c) => {
  const auth = c.get("auth");
  const session = await auth.api.getSession({
    headers: c.req.raw.headers,
  });

  if (!session?.session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  return c.json({
    message: "Protected data",
    userId: session.user.id,
  });
});
```

## Database Operations

### Query Users with Drizzle

```typescript
import { eq } from "drizzle-orm";
import { initDatabase, users } from "./db";

app.get("/api/users/:id", async (c) => {
  const db = initDatabase(c.env.DATABASE);
  const userId = c.req.param("id");

  const user = await db
    .select()
    .from(users)
    .where(eq(users.id, userId))
    .get();

  if (!user) {
    return c.json({ error: "User not found" }, 404);
  }

  return c.json(user);
});
```

### List Recent Sessions

```typescript
import { desc, limit } from "drizzle-orm";
import { sessions } from "./db";

app.get("/api/sessions/recent", async (c) => {
  const db = initDatabase(c.env.DATABASE);

  const recentSessions = await db
    .select()
    .from(sessions)
    .orderBy(desc(sessions.createdAt))
    .limit(10)
    .all();

  return c.json({ sessions: recentSessions });
});
```

### Join Users and Sessions

```typescript
import { eq } from "drizzle-orm";
import { users, sessions } from "./db";

app.get("/api/users/:id/sessions", async (c) => {
  const db = initDatabase(c.env.DATABASE);
  const userId = c.req.param("id");

  const userSessions = await db
    .select({
      sessionId: sessions.id,
      createdAt: sessions.createdAt,
      city: sessions.city,
      country: sessions.country,
    })
    .from(sessions)
    .where(eq(sessions.userId, userId))
    .all();

  return c.json({ sessions: userSessions });
});
```

## KV Caching

### Basic Cache Operations

```typescript
import { getFromCache, setInCache, deleteFromCache } from "./storage/kv";

// Cache API response for 5 minutes
app.get("/api/data/:id", async (c) => {
  const id = c.req.param("id");
  const cacheKey = `data:${id}`;

  // Try to get from cache
  let data = await getFromCache(c.env.CACHE, cacheKey);

  if (data) {
    return c.json({ ...data, cached: true });
  }

  // Fetch fresh data
  data = await fetchDataFromAPI(id);

  // Cache for 5 minutes
  await setInCache(c.env.CACHE, cacheKey, data, { ttl: 300 });

  return c.json({ ...data, cached: false });
});
```

### Cache with Expiration

```typescript
// Cache until specific timestamp
const expirationDate = new Date('2024-12-31T23:59:59Z');
const ttl = Math.floor((expirationDate.getTime() - Date.now()) / 1000);

await setInCache(c.env.CACHE, 'limited-offer', {
  discount: 50,
  validUntil: expirationDate.toISOString()
}, { ttl });
```

### Cache Invalidation

```typescript
import { deleteFromCache } from "./storage/kv";

app.post("/api/data/:id/invalidate", async (c) => {
  const id = c.req.param("id");
  await deleteFromCache(c.env.CACHE, `data:${id}`);

  return c.json({ message: "Cache invalidated" });
});
```

### List Cached Keys

```typescript
import { listCacheKeys } from "./storage/kv";

app.get("/api/cache/keys", async (c) => {
  const prefix = c.req.query("prefix");
  const keys = await listCacheKeys(c.env.CACHE, prefix, 100);

  return c.json({ keys, count: keys.length });
});
```

## R2 File Storage

### Upload File

```typescript
import { uploadFile } from "./storage/r2";

app.post("/api/upload", async (c) => {
  const formData = await c.req.formData();
  const file = formData.get("file") as File;

  if (!file) {
    return c.json({ error: "No file provided" }, 400);
  }

  const auth = c.get("auth");
  const session = await auth.api.getSession({ headers: c.req.raw.headers });

  if (!session?.session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  const key = `uploads/${session.user.id}/${Date.now()}-${file.name}`;
  const arrayBuffer = await file.arrayBuffer();

  await uploadFile(c.env.FILES, key, arrayBuffer, {
    contentType: file.type,
    customMetadata: {
      uploadedBy: session.user.id,
      originalName: file.name,
      uploadedAt: new Date().toISOString(),
    },
  });

  return c.json({
    success: true,
    key,
    url: `/api/files/${encodeURIComponent(key)}`,
  });
});
```

### Download File

```typescript
import { downloadFile, getFileMetadata } from "./storage/r2";

app.get("/api/files/:key", async (c) => {
  const key = decodeURIComponent(c.req.param("key"));

  const metadata = await getFileMetadata(c.env.FILES, key);

  if (!metadata) {
    return c.json({ error: "File not found" }, 404);
  }

  const stream = await downloadFile(c.env.FILES, key);

  return new Response(stream, {
    headers: {
      "Content-Type": metadata.contentType || "application/octet-stream",
      "Content-Length": metadata.size.toString(),
      "Content-Disposition": `attachment; filename="${metadata.customMetadata?.originalName || 'file'}"`,
    },
  });
});
```

### List User Files

```typescript
import { listFiles } from "./storage/r2";

app.get("/api/my-files", async (c) => {
  const auth = c.get("auth");
  const session = await auth.api.getSession({ headers: c.req.raw.headers });

  if (!session?.session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  const prefix = `uploads/${session.user.id}/`;
  const files = await listFiles(c.env.FILES, prefix, 100);

  return c.json({
    files: files.map(f => ({
      key: f.key,
      name: f.customMetadata?.originalName || f.key,
      size: f.size,
      uploaded: f.uploaded,
      url: `/api/files/${encodeURIComponent(f.key)}`,
    })),
  });
});
```

### Delete File

```typescript
import { deleteFile } from "./storage/r2";

app.delete("/api/files/:key", async (c) => {
  const key = decodeURIComponent(c.req.param("key"));
  await deleteFile(c.env.FILES, key);

  return c.json({ message: "File deleted successfully" });
});
```

## Workers AI

### Text Summarization

```typescript
app.post("/api/summarize", async (c) => {
  const { text } = await c.req.json();

  const result = await c.env.AI.run("@cf/facebook/bart-large-cnn", {
    input_text: text,
    max_length: 1024,
  });

  return c.json({ summary: result.summary });
});
```

### Text Generation

```typescript
app.post("/api/generate", async (c) => {
  const { prompt } = await c.req.json();

  const result = await c.env.AI.run("@cf/meta/llama-3.1-8b-instruct", {
    messages: [
      { role: "system", content: "You are a helpful assistant." },
      { role: "user", content: prompt }
    ],
  });

  return c.json({ response: result.response });
});
```

### Image Classification

```typescript
app.post("/api/classify-image", async (c) => {
  const formData = await c.req.formData();
  const image = formData.get("image") as File;

  const arrayBuffer = await image.arrayBuffer();

  const result = await c.env.AI.run("@cf/microsoft/resnet-50", {
    image: Array.from(new Uint8Array(arrayBuffer)),
  });

  return c.json({ classification: result });
});
```

### Cached AI Responses

```typescript
import { getFromCache, setInCache } from "./storage/kv";

app.post("/api/ai/cached-summary", async (c) => {
  const { text } = await c.req.json();

  // Create cache key from text hash
  const cacheKey = `ai:summary:${await hashText(text)}`;

  // Check cache
  let result = await getFromCache(c.env.CACHE, cacheKey);

  if (result) {
    return c.json({ ...result, cached: true });
  }

  // Run AI model
  result = await c.env.AI.run("@cf/facebook/bart-large-cnn", {
    input_text: text,
  });

  // Cache for 1 hour
  await setInCache(c.env.CACHE, cacheKey, result, { ttl: 3600 });

  return c.json({ ...result, cached: false });
});

async function hashText(text: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  const hash = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
}
```

## Geolocation

### Get Request Location

```typescript
import { extractGeolocation, formatLocation } from "./lib/geo";

app.get("/api/location", async (c) => {
  const cf = c.get("cf");
  const geo = extractGeolocation(cf);

  return c.json({
    ...geo,
    formatted: formatLocation(geo),
  });
});
```

### Country-Based Content

```typescript
import { isFromCountry } from "./lib/geo";

app.get("/api/content", async (c) => {
  const cf = c.get("cf");

  if (isFromCountry(cf, "US")) {
    return c.json({ message: "Welcome, US visitor!" });
  } else if (isFromCountry(cf, "GB")) {
    return c.json({ message: "Welcome, UK visitor!" });
  } else {
    return c.json({ message: "Welcome, international visitor!" });
  }
});
```

### Location-Based Restrictions

```typescript
import { isFromContinent } from "./lib/geo";

app.get("/api/restricted", async (c) => {
  const cf = c.get("cf");

  // Only allow European users
  if (!isFromContinent(cf, "EU")) {
    return c.json(
      { error: "Service not available in your region" },
      403
    );
  }

  return c.json({ data: "Restricted content" });
});
```

### Session Geolocation Tracking

```typescript
// Geolocation is automatically tracked in sessions via better-auth-cloudflare
app.get("/api/session-history", async (c) => {
  const auth = c.get("auth");
  const session = await auth.api.getSession({ headers: c.req.raw.headers });

  if (!session?.session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  const db = initDatabase(c.env.DATABASE);
  const userSessions = await db
    .select({
      city: sessions.city,
      country: sessions.country,
      createdAt: sessions.createdAt,
    })
    .from(sessions)
    .where(eq(sessions.userId, session.user.id))
    .all();

  return c.json({ history: userSessions });
});
```

## Combined Examples

### Authenticated File Upload with AI Analysis

```typescript
import { uploadFile } from "./storage/r2";
import { setInCache } from "./storage/kv";

app.post("/api/analyze-upload", async (c) => {
  // 1. Verify authentication
  const auth = c.get("auth");
  const session = await auth.api.getSession({ headers: c.req.raw.headers });

  if (!session?.session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  // 2. Get uploaded file
  const formData = await c.req.formData();
  const file = formData.get("file") as File;

  if (!file) {
    return c.json({ error: "No file provided" }, 400);
  }

  // 3. Upload to R2
  const key = `uploads/${session.user.id}/${Date.now()}-${file.name}`;
  const arrayBuffer = await file.arrayBuffer();

  await uploadFile(c.env.FILES, key, arrayBuffer, {
    contentType: file.type,
    customMetadata: {
      uploadedBy: session.user.id,
      uploadedAt: new Date().toISOString(),
    },
  });

  // 4. Analyze with AI (if text file)
  let analysis = null;
  if (file.type.startsWith("text/")) {
    const text = await file.text();
    const result = await c.env.AI.run("@cf/facebook/bart-large-cnn", {
      input_text: text.substring(0, 5000), // Limit to 5000 chars
    });
    analysis = result.summary;
  }

  // 5. Cache metadata
  await setInCache(
    c.env.CACHE,
    `file-meta:${key}`,
    {
      key,
      name: file.name,
      size: file.size,
      analysis,
    },
    { ttl: 3600 }
  );

  return c.json({
    success: true,
    key,
    analysis,
    url: `/api/files/${encodeURIComponent(key)}`,
  });
});
```

### User Activity Dashboard

```typescript
app.get("/api/dashboard", async (c) => {
  const auth = c.get("auth");
  const session = await auth.api.getSession({ headers: c.req.raw.headers });

  if (!session?.session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  const db = initDatabase(c.env.DATABASE);

  // Get user sessions with geolocation
  const userSessions = await db
    .select()
    .from(sessions)
    .where(eq(sessions.userId, session.user.id))
    .orderBy(desc(sessions.createdAt))
    .limit(10)
    .all();

  // Get user files from R2
  const files = await listFiles(
    c.env.FILES,
    `uploads/${session.user.id}/`,
    50
  );

  // Get current location
  const cf = c.get("cf");
  const currentGeo = extractGeolocation(cf);

  return c.json({
    user: session.user,
    currentLocation: formatLocation(currentGeo),
    recentSessions: userSessions.map(s => ({
      location: `${s.city}, ${s.country}`,
      timestamp: s.createdAt,
    })),
    files: files.map(f => ({
      name: f.customMetadata?.originalName || f.key,
      size: f.size,
      uploaded: f.uploaded,
    })),
  });
});
```

## Best Practices

### Error Handling

```typescript
app.post("/api/safe-operation", async (c) => {
  try {
    const result = await performOperation();
    return c.json({ success: true, data: result });
  } catch (error) {
    console.error("Operation failed:", error);
    return c.json(
      {
        error: "Operation failed",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      500
    );
  }
});
```

### Rate Limiting (via Better Auth)

```typescript
// Rate limiting is automatically applied by better-auth-cloudflare
// Configure in src/lib/auth.ts:

rateLimit: {
  enabled: true,
  window: 60, // seconds
  max: 100,   // requests per window
  customRules: {
    "/sign-in/email": {
      window: 60,
      max: 5, // Only 5 login attempts per minute
    },
  },
}
```

### Input Validation

```typescript
import { z } from "zod";

const uploadSchema = z.object({
  name: z.string().min(1).max(255),
  description: z.string().max(1000).optional(),
});

app.post("/api/upload-with-meta", async (c) => {
  const body = await c.req.json();

  const validation = uploadSchema.safeParse(body);
  if (!validation.success) {
    return c.json(
      { error: "Validation failed", details: validation.error },
      400
    );
  }

  // Proceed with validated data
  const { name, description } = validation.data;
  // ...
});
```
