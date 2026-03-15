# TanStack Unified

A complete, production-ready TanStack Start application demonstrating modern web development patterns with authentication, database integration, and beautiful UI components.

## Features

- **TanStack Start** - Full-stack React framework with file-based routing and SSR
- **Better Auth** - Modern authentication with social providers (GitHub) and email/password
- **Drizzle ORM** - Type-safe database access with PostgreSQL
- **Tailwind CSS v4** - Utility-first CSS framework with custom design system
- **Radix UI** - Accessible component primitives
- **Lucide Icons** - Beautiful, consistent icon set
- **Protected Routes** - Server-side authentication middleware
- **TypeScript** - Full type safety across the stack

## Project Structure

```
tanstack-unified/
├── src/
│   ├── components/
│   │   ├── ui/           # Reusable UI components (button, etc.)
│   │   └── Header.tsx    # Navigation header
│   ├── db/
│   │   └── schema.ts     # Drizzle database schema
│   ├── lib/
│   │   ├── auth.ts           # Server-side auth config
│   │   ├── auth-client.ts    # Client-side auth hooks
│   │   ├── auth-middleware.ts # Auth middleware
│   │   ├── auth-server-fn.ts # Server functions
│   │   └── utils.ts          # Utility functions (cn)
│   ├── routes/
│   │   ├── __root.tsx        # Root layout
│   │   ├── index.tsx         # Home page
│   │   ├── dashboard.tsx     # Protected dashboard
│   │   └── api.auth.$.ts     # Auth API catch-all
│   └── styles/
│       └── global.css        # Global styles & Tailwind config
├── app.config.ts         # TanStack Start config
├── vite.config.ts        # Vite configuration
├── drizzle.config.ts     # Drizzle Kit config
├── docker-compose.yaml   # PostgreSQL container
└── package.json
```

## Getting Started

### Prerequisites

- Node.js 18+
- pnpm (recommended) or npm
- Docker (for PostgreSQL)

### Installation

1. Clone the repository or copy this example

2. Install dependencies:

```bash
pnpm install
```

3. Copy environment variables:

```bash
cp .env.example .env
```

4. Configure your `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/tanstack_unified
BETTER_AUTH_SECRET=your-secret-key-min-32-characters-long
BETTER_AUTH_URL=http://localhost:3000
GITHUB_CLIENT_ID=your-github-oauth-client-id
GITHUB_CLIENT_SECRET=your-github-oauth-client-secret
```

### Setting up GitHub OAuth

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in the details:
   - **Application name**: TanStack Unified (or your app name)
   - **Homepage URL**: `http://localhost:3000`
   - **Authorization callback URL**: `http://localhost:3000/api/auth/callback/github`
4. Copy the Client ID and Client Secret to your `.env` file

### Database Setup

1. Start PostgreSQL container:

```bash
pnpm db:start
```

2. Push the database schema:

```bash
pnpm db:push
```

3. (Optional) Open Drizzle Studio to view your database:

```bash
pnpm db:studio
```

### Development

Start the development server:

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `pnpm dev` - Start development server
- `pnpm build` - Build for production
- `pnpm serve` - Preview production build
- `pnpm start` - Start production server
- `pnpm db:start` - Start PostgreSQL container
- `pnpm db:push` - Push database schema
- `pnpm db:studio` - Open Drizzle Studio

## Key Patterns

### Authentication

This example uses Better Auth with both social (GitHub) and email/password authentication:

```tsx
// Client-side sign in
import { signIn } from '~/lib/auth-client'

signIn.social({ provider: 'github', callbackURL: '/dashboard' })
```

### Protected Routes

Routes are protected using server-side middleware:

```tsx
// In your route file
export const Route = createFileRoute('/dashboard')({
  beforeLoad: async () => {
    const userId = await getUserId()
    return { userId }
  },
  loader: async ({ context }) => {
    if (!context.userId) {
      throw redirect({ to: '/' })
    }
    return { userId: context.userId }
  },
})
```

### Server Functions

Create type-safe server functions with middleware:

```tsx
export const getUserId = createServerFn({ method: 'GET' })
  .middleware([authMiddleware])
  .handler(async ({ context }) => {
    return context?.user?.id ?? null
  })
```

### UI Components

Components follow the shadcn/ui pattern with CVA for variants:

```tsx
import { Button } from '~/components/ui/button'

<Button variant="outline" size="lg">
  Click me
</Button>
```

## Database Schema

The project uses Drizzle ORM with PostgreSQL. The schema includes:

- **users** - User accounts
- **sessions** - Active sessions
- **accounts** - OAuth provider accounts
- **verification** - Email verification tokens

See `src/db/schema.ts` for the complete schema definition.

## Merging Patterns

This example consolidates best practices from multiple TanStack examples:

1. **tanstack-better-auth** - Better Auth integration patterns
2. **tanstack-betterauth** - Drizzle ORM setup
3. **orcish-tanstack-dashboard** - Dashboard UI components
4. **orcish-saas** - SaaS navigation patterns

## Deployment

This app can be deployed to any platform that supports Node.js:

- **Vercel** - Recommended for TanStack Start apps
- **Netlify** - Good support for SSR
- **Railway** - Easy database + app deployment
- **Fly.io** - Global edge deployment

Make sure to:
1. Set up environment variables on your platform
2. Provision a PostgreSQL database
3. Run database migrations
4. Configure your OAuth callback URLs for production

## Learn More

- [TanStack Start Documentation](https://tanstack.com/start)
- [TanStack Router Documentation](https://tanstack.com/router)
- [Better Auth Documentation](https://better-auth.com)
- [Drizzle ORM Documentation](https://orm.drizzle.team)
- [Tailwind CSS v4 Documentation](https://tailwindcss.com)

## License

MIT
