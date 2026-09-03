import { createFileRoute, Link } from "@tanstack/react-router";
import { SUBJECTS } from "./__root";

export const Route = createFileRoute("/")({
  component: LandingPage,
});

function LandingPage() {
  return (
    <div className="space-y-8">
      <section className="text-center py-12">
        <h1 className="text-4xl font-bold tracking-tight">
          Cianfhoghlaim Educational MMO
        </h1>
        <p className="mt-4 text-lg text-muted-foreground">
          Formative assessment for the NCCA Junior Cycle + Leaving Certificate.
        </p>
        <p className="text-base text-muted-foreground italic">
          Measúnú leanúnach don Sraith Shóisearach agus don Ardteistiméireacht.
        </p>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-6 text-center">
          Choose your subject / Roghnaigh d'ábhar
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          {SUBJECTS.map((s) => {
            const Icon = s.icon;
            return (
              <Link
                key={s.slug}
                to="/realm/$subject"
                params={{ subject: s.slug }}
                className="block p-6 rounded-lg border bg-card hover:bg-accent transition-colors"
              >
                <Icon className="h-8 w-8 text-primary mb-2" />
                <h3 className="font-semibold">{s.name_en}</h3>
                <p className="text-sm text-muted-foreground">{s.name_ga}</p>
              </Link>
            );
          })}
        </div>
      </section>

      <section className="mt-12 p-6 rounded-lg border bg-muted/50">
        <h2 className="text-xl font-semibold mb-2">About the MMO</h2>
        <p className="text-sm text-muted-foreground">
          Each subject realm is a 2D TanStack Start page with a quest-pack list
          (bilingual EN + GA) and a CopilotKit chat panel connected to the
          subject specialist agent. Quest packs are generated from the official
          NCCA syllabus PDFs and past papers. Completing quests earns
          verifiable SkillTreeBadge credentials, anchored daily to Base L2 via
          the hybrid x402 educational credential subsystem.
        </p>
      </section>
    </div>
  );
}