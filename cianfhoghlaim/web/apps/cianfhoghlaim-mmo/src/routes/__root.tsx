import { createRootRoute, Link, Outlet } from "@tanstack/react-router";
import { Calculator, FlaskConical, Globe, History, BookOpen, Languages, Code, Cog, GraduationCap } from "lucide-react";

const SUBJECTS = [
  { slug: "mathematics", name_en: "Mathematics", name_ga: "Matamaitic", icon: Calculator },
  { slug: "applied_mathematics", name_en: "Applied Mathematics", name_ga: "Matamaitic Fheidhmeach", icon: Cog },
  { slug: "chemistry", name_en: "Chemistry", name_ga: "Ceimic", icon: FlaskConical },
  { slug: "geography", name_en: "Geography", name_ga: "Tíreolaíocht", icon: Globe },
  { slug: "history", name_en: "History", name_ga: "Stair", icon: History },
  { slug: "english", name_en: "English", name_ga: "Béarla", icon: BookOpen },
  { slug: "gaeilge", name_en: "Gaeilge", name_ga: "Gaeilge", icon: Languages },
  { slug: "computer_science", name_en: "Computer Science", name_ga: "Ríomheolaíocht", icon: Code },
] as const;

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
        <div className="container flex h-16 items-center gap-4">
          <Link to="/" className="flex items-center gap-2 font-bold text-lg">
            <GraduationCap className="h-6 w-6 text-primary" />
            <span>Cianfhoghlaim MMO</span>
          </Link>
          <nav className="ml-auto flex items-center gap-2 text-sm">
            {SUBJECTS.map((s) => (
              <Link
                key={s.slug}
                to="/realm/$subject"
                params={{ subject: s.slug }}
                className="px-2 py-1 rounded hover:bg-muted transition-colors"
              >
                {s.name_en}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="container py-8">
        <Outlet />
      </main>
    </div>
  );
}

export { SUBJECTS };
export type SubjectSlug = (typeof SUBJECTS)[number]["slug"];