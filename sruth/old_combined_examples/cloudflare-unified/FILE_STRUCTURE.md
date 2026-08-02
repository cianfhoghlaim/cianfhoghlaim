# File Structure

Complete file listing for the Cloudflare Unified example.

## Project Files (18 total)

```
cloudflare-unified/
├── Documentation (4 files)
│   ├── README.md                   # Main documentation
│   ├── QUICKSTART.md              # 5-minute setup guide
│   ├── EXAMPLES.md                # Code examples for all services
│   └── ARCHITECTURE.md            # System architecture overview
│
├── Configuration (5 files)
│   ├── package.json               # Dependencies and scripts
│   ├── wrangler.jsonc             # Cloudflare Workers config
│   ├── tsconfig.json              # TypeScript configuration
│   ├── drizzle.config.ts          # Drizzle ORM configuration
│   └── .dev.vars.example          # Environment variables template
│
├── Source Code (8 files)
│   ├── src/
│   │   ├── index.ts               # Main Hono application
│   │   ├── env.d.ts               # TypeScript type definitions
│   │   │
│   │   ├── db/
│   │   │   ├── schema.ts          # Database schema (Drizzle)
│   │   │   └── index.ts           # Database initialization
│   │   │
│   │   ├── lib/
│   │   │   ├── auth.ts            # Better Auth configuration
│   │   │   └── geo.ts             # Geolocation utilities
│   │   │
│   │   └── storage/
│   │       ├── kv.ts              # KV cache helpers
│   │       └── r2.ts              # R2 storage helpers
│
└── Git (1 file)
    └── .gitignore                 # Git ignore rules
```

## File Purposes

### Documentation Files

| File | Purpose | Size |
|------|---------|------|
| `README.md` | Main project documentation, features, API reference | ~6KB |
| `QUICKSTART.md` | Step-by-step setup guide for new users | ~6KB |
| `EXAMPLES.md` | Code examples for each service and common patterns | ~15KB |
| `ARCHITECTURE.md` | System architecture, data flow, security patterns | ~12KB |
| `FILE_STRUCTURE.md` | This file - complete file listing and descriptions | ~3KB |

### Configuration Files

| File | Purpose | Lines |
|------|---------|-------|
| `package.json` | npm dependencies, scripts, metadata | 30 |
| `wrangler.jsonc` | Cloudflare Workers, D1, KV, R2, AI bindings | 50 |
| `tsconfig.json` | TypeScript compiler options | 20 |
| `drizzle.config.ts` | Database migrations configuration | 7 |
| `.dev.vars.example` | Environment variables template | 10 |
| `.gitignore` | Files to exclude from git | 25 |

### Source Files

| File | Purpose | Lines | Exports |
|------|---------|-------|---------|
| `src/index.ts` | Main Hono app, routes, HTML frontend | ~400 | `app` (default) |
| `src/env.d.ts` | TypeScript type definitions for bindings | ~50 | Types |
| `src/db/schema.ts` | User, session, account, verification tables | ~100 | `users`, `sessions`, `accounts`, `verifications`, `schema` |
| `src/db/index.ts` | Database initialization with Drizzle | ~15 | `initDatabase()` |
| `src/lib/auth.ts` | Better Auth with D1, KV, geolocation | ~80 | `createAuth()`, `auth` |
| `src/lib/geo.ts` | Geolocation extraction and utilities | ~150 | 8 functions |
| `src/storage/kv.ts` | KV cache operations | ~100 | 8 functions |
| `src/storage/r2.ts` | R2 file storage operations | ~180 | 11 functions |

## Detailed File Descriptions

### `/src/index.ts` (Main Application)

**Routes:**
- `GET /` - Homepage with interactive dashboard
- `GET/POST /api/auth/*` - Better Auth endpoints
- `GET /api/geo` - Geolocation data
- `POST /api/ai/summarize` - AI text summarization
- `GET /api/cache/test` - KV cache test
- `GET /api/files/list` - List R2 files
- `POST /api/files/upload` - Upload to R2
- `GET /api/files/:key` - Download from R2
- `GET /health` - Health check

**Dependencies:**
- Hono (web framework)
- Better Auth (authentication)
- Cloudflare Workers types

### `/src/db/schema.ts` (Database Schema)

**Tables:**
1. `users` - User accounts (id, email, name, etc.)
2. `sessions` - Sessions with geolocation (8 geo fields)
3. `accounts` - OAuth provider accounts
4. `verifications` - Email verification tokens

**Features:**
- SQLite-compatible (D1)
- Timestamp fields with auto-defaults
- Foreign key relationships
- Unique constraints on email and tokens

### `/src/lib/auth.ts` (Authentication)

**Features:**
- Email/password authentication
- Anonymous login
- D1 database adapter
- KV secondary storage for rate limiting
- Automatic geolocation tracking
- IP address detection from Cloudflare headers

**Configuration:**
- Rate limiting: 100 requests per 60 seconds
- Session storage in D1
- Geolocation tracking enabled by default

### `/src/lib/geo.ts` (Geolocation)

**Functions:**
1. `extractGeolocation()` - Extract from CF context
2. `formatLocation()` - Format as "City, State, Country"
3. `getCoordinates()` - Parse lat/long coordinates
4. `isFromCountry()` - Check if request from country
5. `isFromContinent()` - Check if request from continent
6. `getDistance()` - Calculate distance between coordinates

**Data Extracted:**
- timezone, city, country, region, regionCode
- colo (data center), latitude, longitude
- postalCode, metroCode, continent

### `/src/storage/kv.ts` (KV Cache)

**Functions:**
1. `getFromCache()` - Get JSON value
2. `setInCache()` - Set JSON value with TTL
3. `getTextFromCache()` - Get text value
4. `setTextInCache()` - Set text value
5. `deleteFromCache()` - Delete key
6. `existsInCache()` - Check if key exists
7. `listCacheKeys()` - List keys with prefix

**Features:**
- Automatic JSON serialization
- TTL with 60-second minimum (KV requirement)
- Type-safe generics

### `/src/storage/r2.ts` (R2 Storage)

**Functions:**
1. `uploadFile()` - Upload with metadata
2. `downloadFile()` - Get as ReadableStream
3. `getFileAsArrayBuffer()` - Get as ArrayBuffer
4. `getFileAsText()` - Get as text
5. `getFileMetadata()` - Get metadata only
6. `deleteFile()` - Delete file
7. `fileExists()` - Check if exists
8. `listFiles()` - List with prefix
9. `copyFile()` - Copy within bucket
10. `generatePublicUrl()` - Generate public URL

**Features:**
- Content type handling
- Custom metadata support
- HTTP metadata (cache-control, etc.)
- Stream-based for large files

## Lines of Code Summary

| Category | Files | Total Lines |
|----------|-------|-------------|
| Documentation | 4 | ~1,200 |
| Configuration | 6 | ~150 |
| Source Code | 8 | ~1,275 |
| **Total** | **18** | **~2,625** |

## Dependencies

### Production Dependencies (5)

```json
{
  "better-auth": "^1.3.7",              // Authentication
  "better-auth-cloudflare": "^0.2.8",   // Cloudflare integration
  "drizzle-orm": "^0.44.5",             // ORM
  "hono": "^4.9.4",                     // Web framework
  "zod": "^4.1.5"                       // Schema validation
}
```

### Dev Dependencies (4)

```json
{
  "@cloudflare/workers-types": "^4.20250606.0",  // TypeScript types
  "@types/node": "^22.17.2",                     // Node.js types
  "drizzle-kit": "^0.31.4",                      // Database migrations
  "wrangler": "^4.30.0"                          // Cloudflare CLI
}
```

## Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `dev` | `wrangler dev` | Start local development server |
| `deploy` | `wrangler deploy --minify` | Deploy to production |
| `cf-typegen` | `wrangler types` | Generate TypeScript types |
| `db:generate` | `drizzle-kit generate` | Generate database migrations |
| `db:migrate` | `wrangler d1 migrations apply` | Apply migrations locally |
| `db:migrate:prod` | Same with prod flag | Apply migrations to production |
| `db:studio` | `drizzle-kit studio` | Open database GUI |
| `auth:generate` | Better Auth CLI | Generate auth schema |

## File Size Estimates

| Category | Estimated Size |
|----------|---------------|
| Source Code | ~50 KB |
| Documentation | ~40 KB |
| Configuration | ~5 KB |
| **Total (without node_modules)** | **~95 KB** |
| **With dependencies** | **~50 MB** |

## Generated Files (Not in Git)

These files are created during development:

```
node_modules/           # Dependencies (~50 MB)
.wrangler/             # Wrangler cache and local state
dist/                  # Build output (if using build step)
drizzle/migrations/    # Generated SQL migrations
*.log                  # Log files
.dev.vars             # Local environment variables (secret)
```

## File Relationships

```
index.ts
├── imports: db/schema.ts
├── imports: db/index.ts
├── imports: lib/auth.ts
├── imports: lib/geo.ts
├── imports: storage/kv.ts
└── imports: storage/r2.ts

lib/auth.ts
├── imports: db/schema.ts
└── imports: db/index.ts

db/index.ts
└── imports: db/schema.ts

All TypeScript files
└── types from: env.d.ts
```

## Key Patterns

### 1. Helper Functions Pattern

Each service has a dedicated helper module:
- `storage/kv.ts` - KV operations
- `storage/r2.ts` - R2 operations
- `lib/geo.ts` - Geolocation utilities

### 2. Configuration Separation

Configuration is split by purpose:
- `wrangler.jsonc` - Cloudflare resources
- `tsconfig.json` - TypeScript settings
- `drizzle.config.ts` - Database migrations
- `.dev.vars` - Environment secrets

### 3. Type Safety

All Cloudflare bindings are typed:
- `env.d.ts` defines `CloudflareBindings`
- Used in Hono app: `Hono<{ Bindings: CloudflareBindings }>`
- Full autocomplete and type checking

## File Checklist

Use this checklist to verify your setup:

- [ ] `package.json` - Dependencies configured
- [ ] `wrangler.jsonc` - All IDs updated (D1, KV)
- [ ] `tsconfig.json` - TypeScript configured
- [ ] `drizzle.config.ts` - Migrations configured
- [ ] `.dev.vars` - Created from `.dev.vars.example`
- [ ] `src/index.ts` - Main app routes defined
- [ ] `src/db/schema.ts` - Database schema complete
- [ ] `src/lib/auth.ts` - Authentication configured
- [ ] `README.md` - Documentation read
- [ ] `QUICKSTART.md` - Setup steps followed
- [ ] Dependencies installed (`pnpm install`)
- [ ] Migrations generated (`pnpm db:generate`)
- [ ] Migrations applied (`pnpm db:migrate`)
- [ ] Dev server running (`pnpm dev`)
- [ ] App accessible at http://localhost:8787

## Next Steps

After reviewing this file structure:

1. Read `QUICKSTART.md` for setup instructions
2. Explore `EXAMPLES.md` for code patterns
3. Review `ARCHITECTURE.md` for system design
4. Check `README.md` for API documentation
5. Start coding!
