import { createRootRoute, Outlet, Link } from "@tanstack/react-router";
import { Music, Code, User, Home, Github, Instagram, Youtube } from "lucide-react";

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-background/80 backdrop-blur-sm">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <Link to="/" className="text-xl font-bold text-primary">
              Aleyum
            </Link>

            {/* Navigation Links */}
            <div className="flex items-center gap-6">
              <Link
                to="/"
                className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
                activeProps={{ className: "text-foreground" }}
              >
                <Home className="h-4 w-4" />
                <span className="hidden sm:inline">Home</span>
              </Link>
              <Link
                to="/music"
                className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
                activeProps={{ className: "text-foreground" }}
              >
                <Music className="h-4 w-4" />
                <span className="hidden sm:inline">Music</span>
              </Link>
              <Link
                to="/code"
                className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
                activeProps={{ className: "text-foreground" }}
              >
                <Code className="h-4 w-4" />
                <span className="hidden sm:inline">Code</span>
              </Link>
              <Link
                to="/about"
                className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
                activeProps={{ className: "text-foreground" }}
              >
                <User className="h-4 w-4" />
                <span className="hidden sm:inline">About</span>
              </Link>
            </div>

            {/* Social Links */}
            <div className="flex items-center gap-4">
              <a
                href="https://github.com/Yedya"
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <Github className="h-5 w-5" />
              </a>
              <a
                href="https://www.instagram.com/aleyummusic/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <Instagram className="h-5 w-5" />
              </a>
              <a
                href="https://www.youtube.com/@aleyummusic"
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <Youtube className="h-5 w-5" />
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="pt-16">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-8 mt-16">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p>&copy; {new Date().getFullYear()} Aleyum. All rights reserved.</p>
          <p className="text-sm mt-2">Music Producer & Software Developer</p>
        </div>
      </footer>
    </div>
  );
}
