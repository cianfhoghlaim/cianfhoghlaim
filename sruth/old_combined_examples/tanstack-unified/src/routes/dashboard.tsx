import {
  createFileRoute,
  redirect,
  useNavigate,
} from '@tanstack/react-router'
import { Button } from '~/components/ui/button'
import { Header } from '~/components/Header'
import { signOut } from '~/lib/auth-client'
import { getUserId } from '~/lib/auth-server-fn'
import {
  BarChart3,
  Users,
  Settings,
  FileText,
  LogOut,
  Activity,
  TrendingUp,
} from 'lucide-react'

export const Route = createFileRoute('/dashboard')({
  component: Dashboard,
  beforeLoad: async () => {
    const userId = await getUserId()
    return {
      userId,
    }
  },
  loader: async ({ context }) => {
    if (!context.userId) {
      throw redirect({ to: '/' })
    }
    return {
      userId: context.userId,
    }
  },
})

function Dashboard() {
  const { userId } = Route.useLoaderData()
  const navigate = useNavigate()

  const handleSignOut = async () => {
    await signOut()
    navigate({ to: '/' })
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 bg-muted/40">
        <div className="container mx-auto px-4 py-8">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
              <p className="mt-2 text-muted-foreground">
                Welcome to your protected dashboard
              </p>
            </div>
            <Button variant="outline" onClick={handleSignOut}>
              <LogOut className="mr-2 h-4 w-4" />
              Sign Out
            </Button>
          </div>

          <div className="mb-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Users"
              value="2,345"
              change="+12.5%"
              icon={Users}
            />
            <StatCard
              title="Revenue"
              value="$45,231"
              change="+18.2%"
              icon={TrendingUp}
            />
            <StatCard
              title="Active Sessions"
              value="573"
              change="+5.1%"
              icon={Activity}
            />
            <StatCard
              title="Reports"
              value="48"
              change="+3.7%"
              icon={BarChart3}
            />
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-lg border bg-card p-6 shadow-sm">
              <h2 className="mb-4 text-xl font-semibold">Quick Actions</h2>
              <div className="space-y-3">
                <ActionButton icon={FileText} label="Create New Report" />
                <ActionButton icon={Users} label="Manage Team" />
                <ActionButton icon={Settings} label="Account Settings" />
              </div>
            </div>

            <div className="rounded-lg border bg-card p-6 shadow-sm">
              <h2 className="mb-4 text-xl font-semibold">User Info</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">User ID</span>
                  <code className="rounded bg-muted px-2 py-1 text-sm font-mono">
                    {userId}
                  </code>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Status</span>
                  <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200">
                    Active
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Role</span>
                  <span className="text-sm font-medium">Administrator</span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 rounded-lg border bg-card p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold">Recent Activity</h2>
            <div className="space-y-4">
              <ActivityItem
                action="Updated profile settings"
                time="2 hours ago"
              />
              <ActivityItem action="Created new report" time="5 hours ago" />
              <ActivityItem action="Invited team member" time="1 day ago" />
              <ActivityItem action="Changed password" time="3 days ago" />
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function StatCard({
  title,
  value,
  change,
  icon: Icon,
}: {
  title: string
  value: string
  change: string
  icon: React.ElementType
}) {
  const isPositive = change.startsWith('+')
  return (
    <div className="rounded-lg border bg-card p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="mt-2 text-2xl font-bold">{value}</p>
          <p
            className={`mt-1 text-xs ${
              isPositive ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {change} from last month
          </p>
        </div>
        <div className="rounded-full bg-primary/10 p-3">
          <Icon className="h-5 w-5 text-primary" />
        </div>
      </div>
    </div>
  )
}

function ActionButton({
  icon: Icon,
  label,
}: {
  icon: React.ElementType
  label: string
}) {
  return (
    <Button variant="outline" className="w-full justify-start">
      <Icon className="mr-2 h-4 w-4" />
      {label}
    </Button>
  )
}

function ActivityItem({ action, time }: { action: string; time: string }) {
  return (
    <div className="flex items-center justify-between border-b pb-3 last:border-0 last:pb-0">
      <span className="text-sm">{action}</span>
      <span className="text-xs text-muted-foreground">{time}</span>
    </div>
  )
}
