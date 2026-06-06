import { createRootRoute, Outlet, Link } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";
import {
  Home, FileText, Music, Code, FlaskConical,
  School, BarChart3, Shield, Mail, Github,
} from "lucide-react";

export const Route = createRootRoute({
  component: RootLayout,
});

const NAV = [
  { to: "/", icon: Home, label: "nav.home" },
  { to: "/cv", icon: FileText, label: "nav.cv" },
  { to: "/music", icon: Music, label: "nav.music" },
  { to: "/code", icon: Code, label: "nav.code" },
  { to: "/research", icon: FlaskConical, label: "nav.research" },
  { to: "/teaching", icon: School, label: "nav.teaching" },
  { to: "/data", icon: BarChart3, label: "nav.data" },
  { to: "/identity", icon: Shield, label: "nav.identity" },
  { to: "/contact", icon: Mail, label: "nav.contact" },
] as const;

function RootLayout() {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-background">
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-background/80 backdrop-blur-sm">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            <Link to="/" className="text-xl font-bold text-primary tracking-tight">
              Croílár
            </Link>
            <div className="hidden md:flex items-center gap-1">
              {NAV.map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  className="flex items-center gap-1.5 px-2.5 py-2 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                  activeProps={{ className: "text-foreground bg-accent" }}
                >
                  <item.icon className="h-3.5 w-3.5" />
                  <span>{t(item.label)}</span>
                </Link>
              ))}
            </div>
            <a
              href="https://github.com/Yedya"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              <Github className="h-5 w-5" />
            </a>
          </div>
        </div>
      </nav>

      <main className="pt-16">
        <Outlet />
      </main>

      <footer className="border-t border-border py-8 mt-16">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p>&copy; {new Date().getFullYear()} {t("footer.copyright")}</p>
          <p className="text-sm mt-2">{t("footer.tagline")}</p>
          <div className="flex justify-center gap-4 mt-4">
            {NAV.map((item) => (
              <Link
                key={item.to}
                to={item.to}
                className="text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                {t(item.label)}
              </Link>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}
