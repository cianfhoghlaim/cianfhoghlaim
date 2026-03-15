import { Link } from '@tanstack/react-router'
import { Button } from '~/components/ui/button'
import { useSession } from '~/lib/auth-client'
import { Home, Layout } from 'lucide-react'

export function Header() {
  const { data: session } = useSession()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-6">
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-xl font-bold">TanStack Unified</span>
          </Link>
          <nav className="hidden items-center space-x-4 md:flex">
            <Button asChild variant="ghost" size="sm">
              <Link to="/">
                <Home className="mr-2 h-4 w-4" />
                Home
              </Link>
            </Button>
            {session && (
              <Button asChild variant="ghost" size="sm">
                <Link to="/dashboard">
                  <Layout className="mr-2 h-4 w-4" />
                  Dashboard
                </Link>
              </Button>
            )}
          </nav>
        </div>
        <div className="flex items-center gap-4">
          {session && (
            <div className="hidden items-center gap-2 sm:flex">
              {session.user.image && (
                <img
                  src={session.user.image}
                  alt={session.user.name || 'User'}
                  className="h-8 w-8 rounded-full border"
                />
              )}
              <span className="text-sm font-medium">{session.user.name}</span>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
