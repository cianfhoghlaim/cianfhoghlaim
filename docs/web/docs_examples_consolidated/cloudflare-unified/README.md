# Cloudflare Unified Example

A comprehensive Cloudflare Workers example that demonstrates integration of all major Cloudflare services in a single cohesive application.

## Features

This example consolidates patterns from multiple Cloudflare projects:

- **Authentication** - Better Auth with email/password and anonymous login
- **Database** - Cloudflare D1 with Drizzle ORM
- **Caching** - Cloudflare KV for secondary storage
- **File Storage** - Cloudflare R2 for object storage
- **AI** - Cloudflare Workers AI for text processing
- **Geolocation** - Automatic geolocation tracking from Cloudflare context

## Architecture

```
cloudflare-unified/
├── src/
│   ├── index.ts          # Main Hono application
│   ├── db/
│   │   ├── schema.ts     # Drizzle schema (users, sessions, accounts)
│   │   └── index.ts      # Database initialization
│   ├── lib/
│   │   ├── auth.ts       # Better Auth configuration
│   │   └── geo.ts        # Geolocation helpers
│   └── storage/
│       ├── kv.ts         # KV cache helpers
│       └── r2.ts         # R2 file storage helpers
├── wrangler.jsonc        # Cloudflare Workers configuration
├── drizzle.config.ts     # Drizzle Kit configuration
└── package.json
```

## Services Used

### 1. D1 Database
- SQLite database at the edge
- Managed with Drizzle ORM
- Stores users, sessions, accounts, and verification tokens

### 2. KV Namespace
- Key-value cache for Better Auth rate limiting
- Secondary storage for session data
- General-purpose caching

### 3. R2 Bucket
- Object storage for file uploads
- Supports metadata and custom tags
- S3-compatible API

### 4. Workers AI
- Text summarization with BART model
- Runs at the edge with zero cold starts

### 5. Geolocation
- Automatic extraction from `cf` object
- Tracks timezone, city, country, region, coordinates
- Stored with each session

## Setup

### 1. Install Dependencies

```bash
pnpm install
```

### 2. Create D1 Database

```bash
# Create database
wrangler d1 create cloudflare-unified-db

# Update wrangler.jsonc with the database_id from output
```

### 3. Create KV Namespace

```bash
# Create KV namespace
wrangler kv:namespace create CACHE

# Update wrangler.jsonc with the id from output
```

### 4. Create R2 Bucket

```bash
# Create R2 bucket
wrangler r2 bucket create cloudflare-unified-files
```

### 5. Generate Database Schema

```bash
# Generate Drizzle migrations
pnpm db:generate

# Apply migrations locally
pnpm db:migrate

# Apply migrations to production
pnpm db:migrate:prod
```

### 6. Development

```bash
pnpm dev
```

Visit http://localhost:8787 to see the application.

## API Endpoints

### Authentication
- `GET/POST /api/auth/*` - Better Auth endpoints
  - `/api/auth/sign-in/anonymous` - Anonymous login
  - `/api/auth/sign-in/email` - Email/password login
  - `/api/auth/sign-out` - Logout
  - `/api/auth/get-session` - Get current session

### Geolocation
- `GET /api/geo` - Get geolocation data from Cloudflare

### AI
- `POST /api/ai/summarize` - Summarize text using Workers AI
  ```json
  {
    "text": "Your text to summarize"
  }
  ```

### Cache
- `GET /api/cache/test` - Test KV cache functionality

### File Storage
- `GET /api/files/list` - List uploaded files
- `POST /api/files/upload` - Upload a file (multipart/form-data)
- `GET /api/files/:key` - Download a file

### Health
- `GET /health` - Service health check

## Database Schema

### Users Table
```typescript
{
  id: string (PK)
  name: string
  email: string (unique)
  emailVerified: boolean
  image: string?
  createdAt: timestamp
  updatedAt: timestamp
  isAnonymous: boolean?
}
```

### Sessions Table
```typescript
{
  id: string (PK)
  userId: string (FK)
  token: string (unique)
  expiresAt: timestamp
  ipAddress: string?
  userAgent: string?
  // Geolocation fields
  timezone: string?
  city: string?
  country: string?
  region: string?
  regionCode: string?
  colo: string?
  latitude: string?
  longitude: string?
}
```

### Accounts Table
```typescript
{
  id: string (PK)
  userId: string (FK)
  accountId: string
  providerId: string
  accessToken: string?
  refreshToken: string?
  // ... OAuth fields
}
```

## Configuration

### Environment Variables

Create a `.dev.vars` file for local development:

```env
# Better Auth (auto-generated on first run)
BETTER_AUTH_SECRET=your-secret-key
BETTER_AUTH_URL=http://localhost:8787
```

### Wrangler Configuration

Update `wrangler.jsonc` with your actual IDs:

```jsonc
{
  "d1_databases": [{
    "database_id": "your-actual-d1-id"
  }],
  "kv_namespaces": [{
    "id": "your-actual-kv-id"
  }]
}
```

## Deployment

```bash
pnpm deploy
```

This will:
1. Bundle the application
2. Minify the output
3. Deploy to Cloudflare Workers

## Features Demonstrated

### From hn-summary
- KV caching patterns
- Workers AI integration
- Hono JSX rendering

### From cloudflare-auth-worker
- Better Auth with Hono
- Drizzle ORM setup
- Authentication flows

### From better-auth-cloudflare
- Geolocation tracking
- D1 database adapter
- KV secondary storage
- Rate limiting

### From cloudflare-data-ops
- Monorepo structure patterns
- Multiple service integration
- TypeScript best practices

## Best Practices

1. **Error Handling** - All endpoints have try-catch blocks
2. **Authentication** - Session verification on protected routes
3. **Type Safety** - Full TypeScript coverage with Cloudflare types
4. **Caching** - Smart use of KV for performance
5. **Geolocation** - Automatic tracking with opt-in support
6. **Rate Limiting** - Better Auth rate limiting via KV

## Development Tips

### View Database
```bash
pnpm db:studio
```

### Type Generation
```bash
pnpm cf-typegen
```

### Local D1 Queries
```bash
wrangler d1 execute cloudflare-unified-db --local --command "SELECT * FROM users"
```

## License

MIT
