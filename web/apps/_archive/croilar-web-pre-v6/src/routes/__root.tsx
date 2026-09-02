import { createRootRoute, Outlet, Link, useSearch } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";
import { useEffect, useState, createContext, useContext } from "react";
import {
  Home, FileText, Music, Code, FlaskConical,
  School, BarChart3, Shield, Mail, Github,
} from "lucide-react";
import type { Persona } from "@/personas/_schema";
import { resolvePersona, PERSONAS } from "@/personas/_registry";
import { getThemeCss } from "@/personas/_schema";

export const Route = createRootRoute({
  component: RootLayout,
});

export const PersonaContext = createContext<Persona | null>(null);
export function usePersona(): Persona | null {
  return useContext(PersonaContext);
}

const ICONS: Record<string, typeof Home> = {
  home: Home, user: FileText, music: Music, code: Code,
  flask: FlaskConical, school: School, "book-open": School,
  "bar-chart": BarChart3, shield: Shield, mail: Mail,
  "file-text": FileText, gamepad: Code,
};

function resolveIcon(name: string) {
  return ICONS[name] ?? Home;
}

function PersonaSwitcher({ current, onChange }: {
  current: string;
  onChange: (slug: string) => void;
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") setOpen(!open); }}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm border border-border hover:bg-accent transition-colors"
      >
        <span>{PERSONA_MAP.get(current)?.i18n.en ?? current}</span>
        <span className="text-muted-foreground text-xs">▾</span>
      </button>
      {open && (
        <>
          <div role="presentation" className="fixed inset-0 z-40" onClick={() => setOpen(false)} onKeyDown={(e) => { if (e.key === "Escape") setOpen(false); }} />
          <div className="absolute top-full mt-1 right-0 z-50 bg-card border border-border rounded-md shadow-lg py-1 min-w-[160px]">
            {PERSONAS.map((p) => (
              <button
                type="button"
                key={p.slug}
                onClick={() => { onChange(p.slug); setOpen(false); }}
                className={`block w-full text-left px-3 py-2 text-sm hover:bg-accent transition-colors ${
                  p.slug === current ? "text-foreground font-medium" : "text-muted-foreground"
                }`}
              >
                {p.i18n.en}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
const PERSONA_MAP = new Map(PERSONAS.map((p) => [p.slug, p]));

function RootLayout() {
  const { t, i18n } = useTranslation();
  const search = useSearch({ strict: false }) as Record<string, string | undefined>;
  const persona = resolvePersona(search.persona);
  const paramLang = search.lang;
  const paramPersona = search.persona;

  // Apply theme CSS tokens for the active persona
  useEffect(() => {
    const style = document.createElement("style");
    style.setAttribute("data-persona-theme", persona.slug);
    style.textContent = `:root { ${getThemeCss(persona.slug)} }`;
    document.head.appendChild(style);
    return () => style.remove();
  }, [persona.slug]);

  // Apply language from search param
  useEffect(() => {
    if (paramLang && paramLang !== i18n.language) {
      i18n.changeLanguage(paramLang);
    }
  }, [paramLang, i18n]);

  const navRoutes = persona.routes;
  const rootPath = paramPersona ? `/?persona=${persona.slug}` : "/";

  return (
    <PersonaContext.Provider value={persona}>
      <div className="min-h-screen bg-background">
        <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-background/80 backdrop-blur-sm">
          <div className="container mx-auto px-4">
            <div className="flex h-16 items-center justify-between">
              <div className="flex items-center gap-3">
                <Link
                  to={rootPath}
                  className="text-xl font-bold text-primary tracking-tight"
                >
                  Croílár
                </Link>
                <PersonaSwitcher
                  current={persona.slug}
                  onChange={(slug) => {
                    const url = new URL(window.location.href);
                    url.searchParams.set("persona", slug);
                    window.location.href = url.toString();
                  }}
                />
              </div>
              <div className="hidden md:flex items-center gap-1">
                {navRoutes.map((item) => {
                  const Icon = resolveIcon(item.icon);
                  const href = paramPersona
                    ? `/?persona=${persona.slug}${item.path === "/" ? "" : item.path}`
                    : item.path;
                  return (
                    <Link
                      key={item.path}
                      to={href}
                      className="flex items-center gap-1.5 px-2.5 py-2 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                      activeProps={{ className: "text-foreground bg-accent" }}
                    >
                      <Icon className="h-3.5 w-3.5" />
                      <span>{t(item.label.en, item.label.ga)}</span>
                    </Link>
                  );
                })}
                <a
                  href="https://oideachais.cianfhoghlaim.ie/leaving-cert/mathematics"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-emerald-400 hover:text-emerald-300 transition-colors"
                >
                  Leaving Cert 2026
                </a>
                {/* Leaving Cert 2026 — external link to oideachais */}
                <a
                  href="https://oideachais.cianfhoghlaim.ie/leaving-cert/mathematics"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 px-2.5 py-2 rounded-md text-sm text-emerald-400 hover:text-emerald-300 hover:bg-emerald-950/50 transition-colors border border-emerald-800/30"
                >
                  <svg className="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
                    <path d="M6 12v5c0 2 2 3 6 3s6-1 6-3v-5" />
                  </svg>
                  <span>Leaving Cert 2026</span>
                </a>
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
              {navRoutes.map((item) => {
                const href = paramPersona
                  ? `/?persona=${persona.slug}${item.path === "/" ? "" : item.path}`
                  : item.path;
                return (
                  <Link
                    key={item.path}
                    to={href}
                    className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {t(item.label.en)}
                  </Link>
                );
              })}
            </div>
          </div>
        </footer>
      </div>
    </PersonaContext.Provider>
  );
}
