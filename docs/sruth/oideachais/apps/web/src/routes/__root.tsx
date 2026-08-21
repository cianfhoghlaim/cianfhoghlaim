import { createRootRoute, Link, Outlet, useRouterState } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { BookOpen, MessageSquare, Languages, GitCompare, Menu, X, Globe } from "lucide-react";
import { useState } from "react";
import { Toaster } from "sonner";
import { cn } from "../lib/utils";
import "../index.css";

const navigation = [
  { name: "Home", href: "/", icon: BookOpen },
  { name: "Chat", href: "/chat", icon: MessageSquare },
  { name: "Compare", href: "/curriculum/compare", icon: GitCompare },
  { name: "Translation", href: "/translation", icon: Languages },
];

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  const routerState = useRouterState();
  const pathname = routerState.location.pathname;
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [language, setLanguage] = useState<"en" | "ga">("en");

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
          <div className="mr-4 flex">
            <Link to="/" className="mr-6 flex items-center space-x-2">
              <BookOpen className="h-6 w-6 text-primary" />
              <span className="font-bold text-lg">Cianfhoghlaim</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    "flex items-center space-x-1 transition-colors hover:text-foreground/80",
                    isActive ? "text-foreground" : "text-foreground/60"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Language Selector */}
          <div className="hidden md:flex items-center ml-auto mr-4">
            <button
              onClick={() => setLanguage(language === "en" ? "ga" : "en")}
              className={cn(
                "flex items-center gap-1.5 rounded-md px-2 py-1 text-sm",
                "border border-input bg-background hover:bg-accent"
              )}
            >
              <Globe className="h-4 w-4" />
              <span className="uppercase">{language}</span>
            </button>
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden ml-auto p-2"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="md:hidden border-t p-4 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    "flex items-center space-x-2 p-2 rounded-md transition-colors",
                    isActive
                      ? "bg-primary/10 text-primary"
                      : "text-foreground/60 hover:bg-muted"
                  )}
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
            {/* Mobile Language Selector */}
            <button
              onClick={() => setLanguage(language === "en" ? "ga" : "en")}
              className="flex items-center gap-2 p-2 rounded-md text-foreground/60 hover:bg-muted w-full"
            >
              <Globe className="h-5 w-5" />
              <span>Language: {language === "en" ? "English" : "Gaeilge"}</span>
            </button>
          </nav>
        )}
      </header>

      {/* Main Content */}
      <main className="container py-6">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t py-6 md:py-0">
        <div className="container flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row">
          <p className="text-sm text-muted-foreground">
            Celtic Curriculum Comparison Platform
          </p>
          <p className="text-sm text-muted-foreground">
            Ireland | England | Scotland | Wales | Northern Ireland
          </p>
        </div>
      </footer>

      {/* Toaster for notifications */}
      <Toaster richColors position="top-right" />

      {/* Router DevTools - only in development */}
      {import.meta.env.DEV && (
        <TanStackRouterDevtools position="bottom-left" />
      )}
    </div>
  );
}
