import { Link, Outlet, createFileRoute, useNavigate } from "@tanstack/react-router";
import {
  Activity,
  Bot,
  Database,
  FileText,
  Home,
  Layers,
  LineChart,
  LogOut,
  MessageSquare,
  Server,
  Settings,
  User,
  Workflow,
  Grid3X3,
} from "lucide-react";
import { useSession, signOut } from "@/lib/auth-client";
import { authMiddleware } from "@/lib/middleware";

export const Route = createFileRoute("/admin/__layout")({
  component: LayoutComponent,
  server: {
    middleware: [authMiddleware],
  },
});

function LayoutComponent() {
  const { data: session } = useSession();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    await signOut();
    navigate({ to: "/login" });
  };

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-card border-r flex flex-col">
        {/* Logo */}
        <div className="h-16 flex items-center px-4 border-b">
          <span className="text-2xl mr-2">🏰</span>
          <span className="font-semibold">Cianfhoghlaim</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          <NavSection title="Overview">
            <NavLink to="/" icon={<Home size={18} />}>
              Dashboard
            </NavLink>
            <NavLink to="/widgets" icon={<Grid3X3 size={18} />}>
              Widgets
            </NavLink>
            <NavLink to="/stacks" icon={<Server size={18} />}>
              Stacks
            </NavLink>
          </NavSection>

          <NavSection title="AI Agents">
            <NavLink to="/agents" icon={<Bot size={18} />}>
              Agent Registry
            </NavLink>
            <NavLink to="/agents/chat" icon={<MessageSquare size={18} />}>
              Agent Chat
            </NavLink>
            <NavLink to="/tools" icon={<Workflow size={18} />}>
              MCP Tools
            </NavLink>
          </NavSection>

          <NavSection title="Data">
            <NavLink to="/data/pipelines" icon={<Workflow size={18} />}>
              Pipelines
            </NavLink>
            <NavLink to="/data/schemas" icon={<Database size={18} />}>
              Schemas
            </NavLink>
          </NavSection>

          <NavSection title="Monitoring">
            <NavLink to="/monitoring/metrics" icon={<LineChart size={18} />}>
              Metrics
            </NavLink>
            <NavLink to="/monitoring/logs" icon={<FileText size={18} />}>
              Logs
            </NavLink>
            <NavLink to="/monitoring/llm" icon={<Activity size={18} />}>
              LLM Traces
            </NavLink>
          </NavSection>

          <NavSection title="Analytics">
            <NavLink to="/analytics" icon={<Layers size={18} />}>
              Notebooks
            </NavLink>
          </NavSection>
        </nav>

        {/* Footer with User Info */}
        <div className="p-4 border-t space-y-3">
          {session?.user && (
            <div className="flex items-center gap-3 p-2 bg-secondary/50 rounded-lg">
              <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center">
                {session.user.image ? (
                  <img
                    src={session.user.image}
                    alt={session.user.name}
                    className="w-8 h-8 rounded-full"
                  />
                ) : (
                  <User size={16} className="text-primary" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">
                  {session.user.name}
                </div>
                <div className="text-xs text-muted-foreground truncate">
                  {session.user.email}
                </div>
              </div>
              <button
                onClick={handleSignOut}
                className="p-1.5 hover:bg-secondary rounded"
                title="Sign out"
              >
                <LogOut size={16} />
              </button>
            </div>
          )}
          <NavLink to="/settings" icon={<Settings size={18} />}>
            Settings
          </NavLink>
          <div className="text-xs text-muted-foreground">
            <div>API: <span className="text-status-healthy">Connected</span></div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}

function NavSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-6">
      <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 px-3">
        {title}
      </h3>
      <div className="space-y-1">{children}</div>
    </div>
  );
}

function NavLink({
  to,
  icon,
  children,
}: {
  to: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <Link
      to={to}
      className="sidebar-link"
      activeProps={{ className: "sidebar-link active" }}
    >
      {icon}
      <span>{children}</span>
    </Link>
  );
}
