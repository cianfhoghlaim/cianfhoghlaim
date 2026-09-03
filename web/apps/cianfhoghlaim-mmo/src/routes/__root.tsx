import { createRootRoute, Link, Outlet } from "@tanstack/react-router";
import { Calculator, FlaskConical, Globe, History, BookOpen, Languages, Code, Cog, GraduationCap } from "lucide-react";
import { ConvexProvider, ConvexReactClient } from "convex/react";
import { CopilotKit } from "@copilotkit/react-core/v2";

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

// Per 2026-08-08-docs-informed-quest-and-credential-generation-v1 +
// -agui-generative-credential-ui-v1: the root previously rendered no
// data provider at all (every route was a static shell) and the
// CopilotKit chat panel was literal placeholder text
// ("CopilotKit chat panel will appear here"). Both providers wrap
// every route from here so `useQuery(api...)` and `useCopilotAction`
// work anywhere in the tree, not just inside realm/$subject.tsx.
//
// VITE_CONVEX_URL is set by `npx convex dev` (writes .env.local) —
// falls back to the local dev deployment default so the app doesn't
// crash-on-import before that's run; queries simply won't resolve
// until a real deployment URL is configured.
const convex = new ConvexReactClient(
  import.meta.env.VITE_CONVEX_URL ?? "http://127.0.0.1:3210"
);

// The CopilotKit runtime endpoint — a FastAPI/AG-UI bridge route on
// the agents API (agents/api/routes/), not Convex. Falls back to the
// local agents API dev port.
const COPILOTKIT_RUNTIME_URL =
  import.meta.env.VITE_COPILOTKIT_RUNTIME_URL ?? "http://127.0.0.1:8000/copilotkit";

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  return (
    <ConvexProvider client={convex}>
      <CopilotKit runtimeUrl={COPILOTKIT_RUNTIME_URL}>
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
      </CopilotKit>
    </ConvexProvider>
  );
}

export { SUBJECTS };
export type SubjectSlug = (typeof SUBJECTS)[number]["slug"];
