import { createRootRoute, Link, Outlet } from "@tanstack/react-router";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import {
  Server,
  Layers,
  Container,
  MessageSquare,
  Github,
  Settings,
} from "lucide-react";

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  return (
    <CopilotKit runtimeUrl="/api/copilot">
      <div className="min-h-screen bg-background text-foreground">
        {/* Header */}
        <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur">
          <div className="container mx-auto px-4">
            <div className="flex h-16 items-center justify-between">
              {/* Logo */}
              <Link to="/" className="flex items-center gap-2">
                <Server className="h-6 w-6 text-primary" />
                <span className="text-xl font-bold">Selfhost</span>
              </Link>

              {/* Navigation */}
              <nav className="flex items-center gap-6">
                <Link
                  to="/"
                  className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors [&.active]:text-foreground"
                >
                  Dashboard
                </Link>
                <Link
                  to="/stacks"
                  className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors [&.active]:text-foreground"
                >
                  <Layers className="h-4 w-4" />
                  Stacks
                </Link>
                <Link
                  to="/deploy"
                  className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors [&.active]:text-foreground"
                >
                  <Container className="h-4 w-4" />
                  Deploy
                </Link>
                <Link
                  to="/chat"
                  className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors [&.active]:text-foreground"
                >
                  <MessageSquare className="h-4 w-4" />
                  Assistant
                </Link>
              </nav>

              {/* Actions */}
              <div className="flex items-center gap-4">
                <a
                  href="https://github.com/Yedya"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 rounded-md hover:bg-muted transition-colors"
                >
                  <Github className="h-5 w-5" />
                </a>
                <Link
                  to="/settings"
                  className="p-2 rounded-md hover:bg-muted transition-colors"
                >
                  <Settings className="h-5 w-5" />
                </Link>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main>
          <Outlet />
        </main>

        {/* CopilotKit Sidebar */}
        <CopilotSidebar
          labels={{
            title: "Selfhost Assistant",
            initial: "How can I help you with your homelab today?",
          }}
          defaultOpen={false}
        />

        {/* Footer */}
        <footer className="border-t border-border py-8 mt-16">
          <div className="container mx-auto px-4">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <p className="text-sm text-muted-foreground">
                Selfhost Dashboard - Powered by Komodo + Pangolin
              </p>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <a href="#" className="hover:text-foreground">
                  Documentation
                </a>
                <a href="#" className="hover:text-foreground">
                  API
                </a>
                <a
                  href="https://github.com/Yedya"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-foreground"
                >
                  GitHub
                </a>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </CopilotKit>
  );
}
