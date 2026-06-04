# TanStack Unified - Project Summary

## Overview

This is a consolidated TanStack Start example that merges best practices from four different example projects into a single, production-ready application.

## Source Examples Merged

1. **tanstack-better-auth** - Better Auth integration patterns
2. **tanstack-betterauth** - Drizzle ORM database setup
3. **orcish-tanstack-dashboard** - Dashboard UI components and layouts
4. **orcish-saas** - SaaS navigation and header patterns

## File Structure

```
tanstack-unified/
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore rules
├── README.md                 # Complete setup documentation
├── app.config.ts             # TanStack Start configuration
├── docker-compose.yaml       # PostgreSQL container setup
├── drizzle.config.ts         # Drizzle Kit configuration
├── package.json              # Dependencies and scripts
├── tsconfig.json             # TypeScript configuration
├── vite.config.ts            # Vite + plugins configuration
├── public/                   # Static assets
├── src/
│   ├── components/
│   │   ├── Header.tsx                # Navigation header with auth state
│   │   └── ui/
│   │       └── button.tsx            # Reusable button component (shadcn)
│   ├── db/
│   │   └── schema.ts                 # Drizzle database schema
│   ├── lib/
│   │   ├── auth.ts                   # Server-side Better Auth config
│   │   ├── auth-client.ts            # Client-side auth hooks
│   │   ├── auth-middleware.ts        # TanStack middleware for auth
│   │   ├── auth-server-fn.ts         # Server functions (getUserId, getUser)
│   │   └── utils.ts                  # Utility functions (cn)
│   ├── routes/
│   │   ├── __root.tsx                # Root layout with providers
│   │   ├── index.tsx                 # Public home page
│   │   ├── dashboard.tsx             # Protected dashboard route
│   │   └── api/
│   │       └── auth/
│   │           └── $.ts              # Better Auth API catch-all
│   └── styles/
│       └── global.css                # Tailwind v4 + design tokens
```

## Key Features Implemented

### 1. Authentication System
- **Better Auth** with GitHub OAuth
- Email/password authentication support
- Client-side hooks (`useSession`, `signIn`, `signOut`)
- Server-side middleware for protected routes
- Session management with PostgreSQL

### 2. Database Integration
- **Drizzle ORM** with PostgreSQL
- Type-safe schema definitions
- Docker Compose for local development
- Migration support via Drizzle Kit
- Four tables: users, sessions, accounts, verification

### 3. Routing & Navigation
- **TanStack Router** file-based routing
- Protected routes with server-side auth checks
- Automatic redirects for unauthenticated users
- Type-safe route parameters and loaders
- Catch-all API route for Better Auth

### 4. UI Components
- **Tailwind CSS v4** with custom design tokens
- **Radix UI** primitives for accessibility
- shadcn/ui pattern for component composition
- Responsive header with user avatar
- Dashboard with stats cards and action buttons
- Light/dark mode support

### 5. Developer Experience
- Full TypeScript type safety
- Path aliases (`~/` for src)
- Hot module replacement
- Vite dev server
- pnpm workspace support
- Docker for database

## Routes

### Public Routes
- `/` - Home page with sign-in option

### Protected Routes
- `/dashboard` - User dashboard (requires authentication)

### API Routes
- `/api/auth/*` - Better Auth endpoints (handled by catch-all)

## Authentication Flow

1. User clicks "Sign in with GitHub" on home page
2. Better Auth redirects to GitHub OAuth
3. GitHub redirects back to `/api/auth/callback/github`
4. Better Auth creates session and stores in database
5. User is redirected to `/dashboard`
6. Dashboard route checks authentication via server function
7. If authenticated, shows dashboard; otherwise redirects to `/`

## Database Schema

### users
- id (primary key)
- name
- email (unique)
- emailVerified
- image
- createdAt
- updatedAt

### sessions
- id (primary key)
- token (unique)
- expiresAt
- userId (foreign key)
- ipAddress
- userAgent
- createdAt
- updatedAt

### accounts
- id (primary key)
- accountId
- providerId
- userId (foreign key)
- accessToken
- refreshToken
- OAuth tokens
- createdAt
- updatedAt

### verification
- id (primary key)
- identifier
- value
- expiresAt
- createdAt
- updatedAt

## Technologies Used

- **@tanstack/react-start** v1.132.0 - Full-stack framework
- **@tanstack/react-router** v1.132.0 - Type-safe routing
- **better-auth** v1.3.4 - Authentication
- **drizzle-orm** v0.44.4 - Database ORM
- **tailwindcss** v4.1.11 - Styling
- **react** v19.2.0 - UI framework
- **typescript** v5.8.3 - Type safety
- **vite** v7.0.6 - Build tool
- **@radix-ui/react-*** - UI primitives
- **lucide-react** v0.544.0 - Icons
- **class-variance-authority** - Component variants
- **clsx** + **tailwind-merge** - Class utilities

## Scripts Available

```bash
pnpm dev          # Start dev server on port 3000
pnpm build        # Build for production
pnpm serve        # Preview production build
pnpm start        # Start production server
pnpm db:start     # Start PostgreSQL container
pnpm db:push      # Push schema to database
pnpm db:studio    # Open Drizzle Studio
```

## Environment Variables Required

```env
DATABASE_URL              # PostgreSQL connection string
BETTER_AUTH_SECRET        # Min 32 characters
BETTER_AUTH_URL          # Base URL (http://localhost:3000)
GITHUB_CLIENT_ID         # GitHub OAuth app ID
GITHUB_CLIENT_SECRET     # GitHub OAuth secret
```

## Next Steps for Developers

1. **Add More Auth Providers**: Better Auth supports Google, Discord, etc.
2. **Implement Email/Password**: Already configured, just need UI forms
3. **Add More Protected Routes**: Use the dashboard pattern
4. **Enhance Database Schema**: Add your app's tables
5. **Add More UI Components**: Follow the button.tsx pattern
6. **Set Up Production Deploy**: Vercel, Railway, or Fly.io
7. **Add Testing**: Already has vitest configured
8. **Add API Routes**: Use TanStack Start server functions

## Design Patterns Used

### 1. Server Functions
```tsx
export const getUserId = createServerFn({ method: 'GET' })
  .middleware([authMiddleware])
  .handler(async ({ context }) => context?.user?.id ?? null)
```

### 2. Protected Routes
```tsx
export const Route = createFileRoute('/dashboard')({
  beforeLoad: async () => ({ userId: await getUserId() }),
  loader: async ({ context }) => {
    if (!context.userId) throw redirect({ to: '/' })
    return { userId: context.userId }
  },
})
```

### 3. Component Variants (CVA)
```tsx
const buttonVariants = cva(
  "base-classes",
  { variants: { variant: {...}, size: {...} } }
)
```

### 4. Utility Function Pattern
```tsx
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

## Consolidated Best Practices

- ✅ Type-safe routing with loaders and params
- ✅ Server-side authentication checks
- ✅ Middleware for context injection
- ✅ Database-backed sessions
- ✅ OAuth + email/password ready
- ✅ Responsive UI with Tailwind v4
- ✅ Accessible components via Radix UI
- ✅ Path aliases for clean imports
- ✅ Docker for development database
- ✅ Complete TypeScript coverage

## License

MIT - Free to use in your projects
