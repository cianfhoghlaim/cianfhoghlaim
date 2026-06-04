# Quick Start Guide

Get the Cloudflare Unified example running in 5 minutes.

## Prerequisites

- Node.js 18+ and pnpm installed
- Cloudflare account (free tier works)
- Wrangler CLI installed globally: `npm install -g wrangler`

## Step-by-Step Setup

### 1. Login to Cloudflare

```bash
wrangler login
```

### 2. Install Dependencies

```bash
cd web/examples-working/cloudflare-unified
pnpm install
```

### 3. Create Cloudflare Resources

#### Create D1 Database

```bash
wrangler d1 create cloudflare-unified-db
```

**Output:**
```
✅ Successfully created DB 'cloudflare-unified-db'
database_id = "abc123-def456-ghi789"
```

Copy the `database_id` and update `wrangler.jsonc`:

```jsonc
{
  "d1_databases": [{
    "database_id": "abc123-def456-ghi789"  // Replace with your ID
  }]
}
```

#### Create KV Namespace

```bash
wrangler kv:namespace create CACHE
```

**Output:**
```
✅ Success!
Add the following to your wrangler.toml:
id = "xyz789abc123def456"
```

Update `wrangler.jsonc`:

```jsonc
{
  "kv_namespaces": [{
    "id": "xyz789abc123def456"  // Replace with your ID
  }]
}
```

#### Create R2 Bucket

```bash
wrangler r2 bucket create cloudflare-unified-files
```

**Output:**
```
✅ Created bucket 'cloudflare-unified-files'
```

No configuration update needed - the bucket name is already in `wrangler.jsonc`.

### 4. Generate Database Schema

```bash
# Generate migrations
pnpm db:generate

# Apply migrations locally
pnpm db:migrate
```

You should see:
```
✅ Migrations applied successfully!
```

### 5. Start Development Server

```bash
pnpm dev
```

Open http://localhost:8787 in your browser.

### 6. Test the Application

1. Click "Login Anonymously" button
2. You should see:
   - User information
   - Geolocation data
   - Test buttons for AI, Cache, and R2

3. Try each test:
   - **Test Workers AI** - Summarizes sample text
   - **Test KV Cache** - Stores and retrieves cached data
   - **Test R2 Storage** - Lists files in R2 bucket

## Common Commands

### Development

```bash
# Start dev server
pnpm dev

# Type generation
pnpm cf-typegen

# View database in browser
pnpm db:studio
```

### Database

```bash
# Generate new migrations
pnpm db:generate

# Apply migrations locally
pnpm db:migrate

# Apply migrations to production
pnpm db:migrate:prod

# Query local database
wrangler d1 execute cloudflare-unified-db --local --command "SELECT * FROM users"
```

### Deployment

```bash
# Deploy to production
pnpm deploy
```

## Troubleshooting

### Error: "No such binding DATABASE"

**Solution:** Make sure you've created the D1 database and updated `wrangler.jsonc` with the correct `database_id`.

### Error: "KV namespace not found"

**Solution:** Create the KV namespace and update `wrangler.jsonc` with the correct `id`.

### Error: "R2 bucket not found"

**Solution:** Create the R2 bucket with the exact name `cloudflare-unified-files`.

### Database migrations not applying

**Solution:**
```bash
# Delete local database
rm -rf .wrangler/state

# Regenerate migrations
pnpm db:generate

# Reapply migrations
pnpm db:migrate
```

### Type errors in VS Code

**Solution:**
```bash
# Generate Cloudflare types
pnpm cf-typegen

# Restart TypeScript server in VS Code
# Cmd+Shift+P > "TypeScript: Restart TS Server"
```

## Next Steps

### Add OAuth Providers

1. Create `.dev.vars` from `.dev.vars.example`
2. Add OAuth credentials:

```env
BETTER_AUTH_SECRET=your-secret-here
BETTER_AUTH_URL=http://localhost:8787

GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

3. Update `src/lib/auth.ts` to enable OAuth providers

### Deploy to Production

```bash
# First deployment
pnpm db:migrate:prod  # Migrate production database
pnpm deploy           # Deploy worker

# Subsequent deployments
pnpm deploy
```

### Add Custom Routes

Edit `src/index.ts` to add new routes:

```typescript
app.get("/api/custom", async (c) => {
  // Your custom logic here
  return c.json({ message: "Hello from custom route!" });
});
```

### Customize Database Schema

1. Edit `src/db/schema.ts` to add tables
2. Run `pnpm db:generate` to create migrations
3. Run `pnpm db:migrate` to apply changes

## Project Structure

```
cloudflare-unified/
├── src/
│   ├── index.ts              # Main app with routes
│   ├── env.d.ts              # TypeScript environment types
│   ├── db/
│   │   ├── schema.ts         # Drizzle database schema
│   │   └── index.ts          # Database initialization
│   ├── lib/
│   │   ├── auth.ts           # Better Auth config
│   │   └── geo.ts            # Geolocation utilities
│   └── storage/
│       ├── kv.ts             # KV cache helpers
│       └── r2.ts             # R2 storage helpers
├── wrangler.jsonc            # Cloudflare configuration
├── drizzle.config.ts         # Drizzle Kit config
├── tsconfig.json             # TypeScript config
└── package.json              # Dependencies & scripts
```

## Resources

- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [D1 Database Docs](https://developers.cloudflare.com/d1/)
- [KV Storage Docs](https://developers.cloudflare.com/kv/)
- [R2 Storage Docs](https://developers.cloudflare.com/r2/)
- [Workers AI Docs](https://developers.cloudflare.com/workers-ai/)
- [Better Auth Docs](https://www.better-auth.com/)
- [Drizzle ORM Docs](https://orm.drizzle.team/)
- [Hono Framework Docs](https://hono.dev/)

## Support

If you encounter issues:

1. Check the main [README.md](./README.md) for detailed documentation
2. Review Cloudflare Workers logs: `wrangler tail`
3. Check the Cloudflare dashboard for resource status
4. Verify all environment variables are set correctly
