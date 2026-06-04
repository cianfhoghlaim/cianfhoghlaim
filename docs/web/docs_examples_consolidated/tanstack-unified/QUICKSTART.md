# Quick Start Guide

Get up and running with TanStack Unified in 5 minutes!

## Prerequisites

- Node.js 18+ installed
- pnpm installed (`npm install -g pnpm`)
- Docker Desktop installed and running

## Step-by-Step Setup

### 1. Install Dependencies (1 minute)

```bash
cd /Users/cliste/dev/bonneagar/hackathon/web/examples-working/tanstack-unified
pnpm install
```

### 2. Set Up Environment Variables (1 minute)

```bash
cp .env.example .env
```

Edit `.env` and update:

```env
# Database - keep as is for local development
DATABASE_URL=postgresql://user:password@localhost:5432/tanstack_unified

# Auth Secret - generate a random 32+ character string
BETTER_AUTH_SECRET=your-super-secret-key-min-32-chars

# Base URL - keep as is for local development
BETTER_AUTH_URL=http://localhost:3000

# GitHub OAuth - follow step 3 to get these
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

### 3. Create GitHub OAuth App (2 minutes)

1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in:
   - **Name**: TanStack Unified Dev
   - **Homepage URL**: `http://localhost:3000`
   - **Callback URL**: `http://localhost:3000/api/auth/callback/github`
4. Click "Register application"
5. Copy **Client ID** to `.env` as `GITHUB_CLIENT_ID`
6. Click "Generate a new client secret"
7. Copy the secret to `.env` as `GITHUB_CLIENT_SECRET`

### 4. Start Database (30 seconds)

```bash
pnpm db:start
```

Wait for PostgreSQL to start (you'll see "database system is ready to accept connections")

### 5. Initialize Database Schema (10 seconds)

```bash
pnpm db:push
```

You should see: "Everything is up to date"

### 6. Start Development Server (10 seconds)

```bash
pnpm dev
```

### 7. Open Browser

Navigate to: **http://localhost:3000**

## What You Should See

### Home Page (/)
- Title: "TanStack Unified"
- Description of the stack
- "Sign in with GitHub" button
- Three feature cards

### After Signing In
- Your GitHub avatar and name
- "Go to Dashboard" button
- "Sign Out" button

### Dashboard (/dashboard)
- Header with your info
- Stats cards (Users, Revenue, Sessions, Reports)
- Quick Actions panel
- User Info panel
- Recent Activity list

## Troubleshooting

### Port 3000 Already in Use
```bash
# Kill the process using port 3000
lsof -ti:3000 | xargs kill -9

# Or change the port in vite.config.ts
```

### Database Connection Failed
```bash
# Check if PostgreSQL container is running
docker ps

# Restart the container
docker-compose down
pnpm db:start

# Push schema again
pnpm db:push
```

### GitHub OAuth Not Working
- Check callback URL matches exactly: `http://localhost:3000/api/auth/callback/github`
- Verify CLIENT_ID and CLIENT_SECRET are correct
- Make sure there are no trailing spaces in `.env`

### TypeScript Errors
```bash
# Generate route types
pnpm dev
# Wait for Vite to start, then stop it (Ctrl+C)
# Route tree should be generated at src/routeTree.gen.ts
```

## Next Steps

### Test the App
1. Sign in with GitHub
2. Navigate to Dashboard
3. Click "Sign Out"
4. Try to access `/dashboard` directly (should redirect to home)

### Explore the Code
- **Routes**: `src/routes/*.tsx` - Add new pages here
- **Components**: `src/components/**/*.tsx` - Reusable UI
- **Auth**: `src/lib/auth*.ts` - Authentication logic
- **Database**: `src/db/schema.ts` - Add new tables here

### View Database
```bash
pnpm db:studio
```
Opens Drizzle Studio at http://localhost:4983

### Development Commands

```bash
pnpm dev          # Start dev server
pnpm build        # Build for production
pnpm serve        # Preview production build
pnpm db:start     # Start PostgreSQL
pnpm db:push      # Update database schema
pnpm db:studio    # Open database GUI
```

## Project Structure Explained

```
src/
├── routes/           # File-based routing
│   ├── __root.tsx    # Layout wrapper for all pages
│   ├── index.tsx     # Home page (/)
│   ├── dashboard.tsx # Dashboard (/dashboard)
│   └── api/          # API routes
│       └── auth/     # Better Auth endpoints
├── components/       # Reusable components
│   ├── Header.tsx    # Navigation header
│   └── ui/           # shadcn-style components
├── lib/              # Utilities and configs
│   ├── auth.ts       # Server auth setup
│   ├── auth-client.ts # Client auth hooks
│   └── utils.ts      # Helper functions
├── db/               # Database
│   └── schema.ts     # Drizzle schema
└── styles/           # CSS
    └── global.css    # Tailwind + design tokens
```

## Making Your First Changes

### Add a New Route

1. Create `src/routes/about.tsx`:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { Header } from '~/components/Header'

export const Route = createFileRoute('/about')({
  component: About,
})

function About() {
  return (
    <div>
      <Header />
      <main className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold">About</h1>
        <p>This is the about page!</p>
      </main>
    </div>
  )
}
```

2. Navigate to http://localhost:3000/about

### Add a Protected Route

Follow the pattern in `src/routes/dashboard.tsx`:
- Use `beforeLoad` to get user
- Use `loader` to check auth and redirect

### Add a UI Component

Follow the pattern in `src/components/ui/button.tsx`:
- Use CVA for variants
- Export component and variants
- Use `cn()` for class merging

## Common Tasks

### Change Color Scheme
Edit `src/styles/global.css` and modify the `@theme` colors

### Add a New Database Table
1. Add table to `src/db/schema.ts`
2. Run `pnpm db:push`
3. View in Drizzle Studio

### Add Email/Password Auth
Better Auth is already configured! Just add the UI:

```tsx
import { signIn, signUp } from '~/lib/auth-client'

// Sign up
await signUp.email({
  email: 'user@example.com',
  password: 'securePassword123',
  name: 'User Name'
})

// Sign in
await signIn.email({
  email: 'user@example.com',
  password: 'securePassword123'
})
```

## Resources

- [Full README](./README.md)
- [Project Summary](./PROJECT_SUMMARY.md)
- [TanStack Start Docs](https://tanstack.com/start)
- [Better Auth Docs](https://better-auth.com)
- [Drizzle Docs](https://orm.drizzle.team)

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Review the full README.md
3. Check TanStack/Better Auth documentation
4. Ensure all environment variables are set correctly
5. Verify Docker is running and PostgreSQL is accessible

Happy coding! 🚀
