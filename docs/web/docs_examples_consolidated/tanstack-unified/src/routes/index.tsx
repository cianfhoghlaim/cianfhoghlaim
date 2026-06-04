import { createFileRoute, Link } from '@tanstack/react-router'
import { Button } from '~/components/ui/button'
import { Header } from '~/components/Header'
import { signIn, signOut, useSession } from '~/lib/auth-client'
import { Github, LogOut, Layout } from 'lucide-react'

export const Route = createFileRoute('/')({
  component: Home,
})

function Home() {
  const { data: session, isPending } = useSession()

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-16">
          <div className="flex flex-col items-center justify-center space-y-8 text-center">
            <div className="space-y-4">
              <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl">
                TanStack Unified
              </h1>
              <p className="mx-auto max-w-[700px] text-lg text-muted-foreground">
                A complete TanStack Start example with Better Auth, Drizzle ORM,
                and modern UI components
              </p>
            </div>

            {isPending && (
              <div className="text-muted-foreground">Loading...</div>
            )}

            {!session && !isPending && (
              <div className="flex flex-col gap-4 sm:flex-row">
                <Button
                  size="lg"
                  onClick={() =>
                    signIn.social({
                      provider: 'github',
                      callbackURL: '/dashboard',
                    })
                  }
                >
                  <Github className="mr-2 h-4 w-4" />
                  Sign in with GitHub
                </Button>
              </div>
            )}

            {session && (
              <div className="flex flex-col items-center gap-6">
                <div className="flex flex-col items-center space-y-2">
                  {session.user.image && (
                    <img
                      src={session.user.image}
                      alt={session.user.name || 'User avatar'}
                      className="h-16 w-16 rounded-full border-2 border-border"
                    />
                  )}
                  <div className="space-y-1 text-center">
                    <p className="text-lg font-medium">
                      Welcome, {session.user.name}!
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {session.user.email}
                    </p>
                  </div>
                </div>

                <div className="flex gap-3">
                  <Button asChild size="lg">
                    <Link to="/dashboard">
                      <Layout className="mr-2 h-4 w-4" />
                      Go to Dashboard
                    </Link>
                  </Button>
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={() => signOut()}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    Sign Out
                  </Button>
                </div>
              </div>
            )}

            <div className="mt-12 grid gap-6 sm:grid-cols-3">
              <FeatureCard
                title="TanStack Start"
                description="Full-stack React framework with file-based routing and SSR"
              />
              <FeatureCard
                title="Better Auth"
                description="Modern authentication with social providers and email/password"
              />
              <FeatureCard
                title="Drizzle ORM"
                description="Type-safe database access with PostgreSQL"
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function FeatureCard({
  title,
  description,
}: {
  title: string
  description: string
}) {
  return (
    <div className="rounded-lg border bg-card p-6 shadow-sm">
      <h3 className="mb-2 font-semibold">{title}</h3>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  )
}
