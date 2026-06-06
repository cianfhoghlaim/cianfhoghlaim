# Architecture Overview

This document provides a comprehensive overview of the Cloudflare Unified example architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Browser                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  HTML/JavaScript Frontend (embedded in index.ts)     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/HTTPS
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Cloudflare Edge Network                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                Hono Application                       │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  Authentication Middleware (Better Auth)       │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  Geolocation Middleware (CF Context)           │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  Route Handlers                                │  │   │
│  │  │   • Auth Routes (/api/auth/*)                  │  │   │
│  │  │   • AI Routes (/api/ai/*)                      │  │   │
│  │  │   • Cache Routes (/api/cache/*)                │  │   │
│  │  │   • File Routes (/api/files/*)                 │  │   │
│  │  │   • Geo Routes (/api/geo)                      │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
         ┌────────────┼────────────┬──────────────┐
         ▼            ▼            ▼              ▼
    ┌────────┐  ┌─────────┐  ┌─────────┐   ┌──────────┐
    │   D1   │  │   KV    │  │   R2    │   │ Workers  │
    │Database│  │ Storage │  │ Bucket  │   │    AI    │
    └────────┘  └─────────┘  └─────────┘   └──────────┘
```

## Components

### 1. Frontend Layer

**Location:** Embedded in `/src/index.ts` (HTML/JavaScript)

**Responsibilities:**
- User interface rendering
- Client-side authentication state management
- API calls to backend endpoints
- File upload handling

**Key Features:**
- Anonymous login
- Session management
- Service testing (AI, Cache, R2)
- Geolocation display

### 2. Application Layer

**Location:** `/src/index.ts`

**Framework:** Hono (lightweight web framework)

**Responsibilities:**
- Request routing
- Middleware processing
- Response formatting
- Error handling

**Middleware Pipeline:**
```
Request → CORS → Auth Init → Geo Context → Route Handler → Response
```

### 3. Authentication Layer

**Location:** `/src/lib/auth.ts`

**Library:** Better Auth with Cloudflare plugin

**Features:**
- Email/password authentication
- Anonymous login
- Session management with D1
- Rate limiting with KV
- Geolocation tracking
- IP address detection

**Flow:**
```
Login Request → Better Auth → Create Session → Store in D1 → Set Cookie
```

### 4. Database Layer

**Location:** `/src/db/`

**Technology:** Drizzle ORM + Cloudflare D1 (SQLite)

**Schema:**
- `users` - User accounts
- `sessions` - Active sessions with geolocation
- `accounts` - OAuth provider accounts
- `verifications` - Email verification and password reset tokens

**Access Pattern:**
```typescript
const db = initDatabase(c.env.DATABASE);
const user = await db.select().from(users).where(eq(users.id, id)).get();
```

### 5. Cache Layer

**Location:** `/src/storage/kv.ts`

**Technology:** Cloudflare KV (Key-Value storage)

**Use Cases:**
- Better Auth rate limiting
- API response caching
- Session secondary storage
- Temporary data storage

**Access Pattern:**
```typescript
const cached = await getFromCache(kv, key);
await setInCache(kv, key, value, { ttl: 300 });
```

### 6. File Storage Layer

**Location:** `/src/storage/r2.ts`

**Technology:** Cloudflare R2 (Object storage)

**Use Cases:**
- User file uploads
- Static asset storage
- Backup storage

**Access Pattern:**
```typescript
await uploadFile(r2, key, data, { contentType: 'image/png' });
const stream = await downloadFile(r2, key);
```

### 7. AI Layer

**Technology:** Cloudflare Workers AI

**Models Used:**
- `@cf/facebook/bart-large-cnn` - Text summarization
- Others available (see Workers AI docs)

**Access Pattern:**
```typescript
const result = await AI.run('@cf/facebook/bart-large-cnn', {
  input_text: text,
});
```

### 8. Geolocation Layer

**Location:** `/src/lib/geo.ts`

**Source:** Cloudflare request context (`cf` object)

**Data Provided:**
- Timezone
- City, Region, Country
- Latitude, Longitude
- Data center (colo)
- Postal code, Metro code, Continent

## Data Flow Examples

### Authentication Flow

```
1. Client sends login request
   ↓
2. Hono receives POST /api/auth/sign-in/anonymous
   ↓
3. Better Auth creates user and session
   ↓
4. Session stored in D1 with geolocation
   ↓
5. Rate limit tracked in KV
   ↓
6. Cookie set with session token
   ↓
7. Response with user and session data
```

### File Upload Flow

```
1. Client uploads file via FormData
   ↓
2. Auth middleware verifies session
   ↓
3. File received as multipart/form-data
   ↓
4. File stored in R2 with metadata
   ↓
5. Metadata cached in KV (optional)
   ↓
6. Response with file key and URL
```

### AI Processing Flow

```
1. Client sends text to summarize
   ↓
2. Check KV cache for previous result
   ↓
3. If not cached, run Workers AI model
   ↓
4. Cache result in KV for 1 hour
   ↓
5. Return summary to client
```

## Service Integration Patterns

### Pattern 1: Auth + D1 + KV

**Used For:** Session management with rate limiting

```typescript
// D1 stores persistent session data
// KV stores rate limiting counters
// Better Auth coordinates both
const auth = createAuth({
  DATABASE: db,
  CACHE: kv,
}, cf);
```

### Pattern 2: Auth + R2 + KV

**Used For:** Authenticated file uploads with metadata caching

```typescript
// 1. Verify auth (D1 lookup)
const session = await auth.api.getSession();

// 2. Upload to R2
await uploadFile(r2, key, data);

// 3. Cache metadata in KV
await setInCache(kv, `file:${key}`, metadata);
```

### Pattern 3: AI + KV

**Used For:** Cached AI responses

```typescript
// 1. Check KV cache
let result = await getFromCache(kv, cacheKey);

// 2. If miss, run AI
if (!result) {
  result = await AI.run(model, input);
  await setInCache(kv, cacheKey, result, { ttl: 3600 });
}
```

## Security Architecture

### Authentication Security

- **Session Tokens:** Stored in httpOnly cookies
- **CSRF Protection:** Built into Better Auth
- **Rate Limiting:** KV-based rate limiting per route
- **IP Tracking:** Cloudflare's `cf-connecting-ip` header

### Authorization Patterns

```typescript
// Middleware pattern for protected routes
app.use("/api/protected/*", async (c, next) => {
  const auth = c.get("auth");
  const session = await auth.api.getSession({ headers: c.req.raw.headers });

  if (!session?.session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  await next();
});
```

### Data Security

- **D1:** SQLite with query parameterization (SQL injection prevention)
- **KV:** Automatic encryption at rest
- **R2:** Private by default, signed URLs for temporary access
- **AI:** No data persistence, processed at edge

## Performance Optimization

### Caching Strategy

1. **Browser Cache:** Static assets with long TTL
2. **KV Cache:** API responses, AI results
3. **D1 Cache:** Drizzle ORM query caching
4. **Cloudflare Cache:** Edge caching for public endpoints

### Edge Computing Benefits

- **Low Latency:** Code runs at Cloudflare edge (250+ locations)
- **Zero Cold Starts:** Workers AI has no cold start
- **Global Distribution:** D1, KV, and R2 are globally distributed

### Database Optimization

```typescript
// Use indexes for common queries
// Index automatically created on primary keys and unique fields

// Use select() to limit columns
const user = await db
  .select({
    id: users.id,
    email: users.email,
  })
  .from(users)
  .where(eq(users.id, userId))
  .get();

// Use limit() for pagination
const recentUsers = await db
  .select()
  .from(users)
  .orderBy(desc(users.createdAt))
  .limit(20)
  .all();
```

## Scalability Considerations

### Horizontal Scalability

- **Workers:** Auto-scales to millions of requests
- **D1:** Read replicas across edge locations
- **KV:** Eventually consistent, highly scalable
- **R2:** Unlimited storage, auto-scaling

### Service Limits

| Service | Free Tier Limit | Scaling Strategy |
|---------|----------------|------------------|
| Workers | 100k requests/day | Paid plan: 10M requests/month |
| D1 | 5 GB storage | Paid plan: 50 GB per database |
| KV | 100k reads/day | Paid plan: 10M reads/month |
| R2 | 10 GB storage | Paid plan: Per-GB pricing |
| AI | 10k neurons/day | Paid plan: Pay-per-use |

### Best Practices for Scale

1. **Use KV for caching** - Reduces D1 reads
2. **Implement rate limiting** - Prevents abuse
3. **Optimize AI usage** - Cache AI results
4. **Use R2 for large files** - Don't store in D1
5. **Monitor usage** - Use Cloudflare analytics

## Monitoring and Observability

### Built-in Observability

```jsonc
// wrangler.jsonc
{
  "observability": {
    "enabled": true,
    "logs": {
      "enabled": true
    }
  }
}
```

### Logging Strategy

```typescript
// Log important events
console.log("User logged in:", userId);
console.error("AI request failed:", error);

// View logs in real-time
// wrangler tail --format pretty
```

### Health Check Endpoint

```typescript
app.get("/health", (c) => {
  return c.json({
    status: "ok",
    timestamp: new Date().toISOString(),
    services: {
      d1: "✓",
      kv: "✓",
      r2: "✓",
      ai: "✓",
    },
  });
});
```

## Deployment Architecture

### Development Environment

```
Local Machine
├── Wrangler Dev Server (localhost:8787)
├── Local D1 SQLite database
├── Remote KV namespace (or local simulation)
├── Remote R2 bucket
└── Remote Workers AI
```

### Production Environment

```
Cloudflare Edge
├── Workers runtime (global)
├── D1 database (primary + read replicas)
├── KV namespace (globally distributed)
├── R2 bucket (automatically distributed)
└── Workers AI (runs on GPU-equipped edge nodes)
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Framework | Hono | Web application framework |
| Auth | Better Auth | Authentication system |
| ORM | Drizzle | Type-safe database queries |
| Database | Cloudflare D1 | SQLite at the edge |
| Cache | Cloudflare KV | Key-value storage |
| Storage | Cloudflare R2 | Object storage |
| AI | Workers AI | Edge AI inference |
| Runtime | Cloudflare Workers | Serverless compute |
| Language | TypeScript | Type-safe JavaScript |

## Future Enhancements

Potential additions to this architecture:

1. **Durable Objects** - For real-time collaboration
2. **Queues** - For background job processing
3. **Cron Triggers** - For scheduled tasks
4. **Analytics Engine** - For custom analytics
5. **Email Routing** - For transactional emails
6. **Stream** - For video storage and delivery
7. **Vectorize** - For vector search capabilities

## References

- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Hono Framework](https://hono.dev/)
- [Better Auth](https://www.better-auth.com/)
- [Drizzle ORM](https://orm.drizzle.team/)
- [Workers AI Models](https://developers.cloudflare.com/workers-ai/models/)
