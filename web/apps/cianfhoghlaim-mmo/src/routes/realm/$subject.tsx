import { createFileRoute, useParams } from "@tanstack/react-router";
import { SUBJECTS } from "../__root";

export const Route = createFileRoute("/realm/$subject")({
  component: RealmPage,
});

function RealmPage() {
  const { subject } = useParams({ from: "/realm/$subject" });
  const meta = SUBJECTS.find((s) => s.slug === subject);

  if (!meta) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold">Unknown subject</h1>
        <p className="text-muted-foreground mt-2">
          No realm exists for subject "{subject}".
        </p>
      </div>
    );
  }

  const Icon = meta.icon;

  return (
    <div className="space-y-8">
      <header className="flex items-center gap-4">
        <Icon className="h-12 w-12 text-primary" />
        <div>
          <h1 className="text-3xl font-bold">{meta.name_en}</h1>
          <p className="text-lg text-muted-foreground italic">{meta.name_ga}</p>
        </div>
      </header>

      <section>
        <h2 className="text-xl font-semibold mb-4">Quest packs</h2>
        <div className="grid gap-4">
          <QuestPackCard
            level="hl"
            levelName="Higher Level / Ardleibhéal"
            estItems={20}
          />
          <QuestPackCard
            level="ol"
            levelName="Ordinary Level / Gnáthleibhéal"
            estItems={18}
          />
          <QuestPackCard
            level="fl"
            levelName="Foundation Level / Bonnleibhéal"
            estItems={15}
          />
        </div>
      </section>

      <section>
        <h2 className="text-xl font-semibold mb-4">
          Talk to the {meta.name_en} tutor
        </h2>
        <div className="p-6 rounded-lg border bg-card">
          <p className="text-sm text-muted-foreground">
            CopilotKit chat panel will appear here. The subject specialist
            agent (e.g. <code>math_agent</code>) routes keyword-level
            traffic to this realm.
          </p>
        </div>
      </section>
    </div>
  );
}

function QuestPackCard({
  level,
  levelName,
  estItems,
}: {
  level: string;
  levelName: string;
  estItems: number;
}) {
  return (
    <div className="p-4 rounded-lg border bg-card">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold">{levelName}</h3>
          <p className="text-sm text-muted-foreground">
            ≈ {estItems} formative items, generated from NCCA syllabus + past papers
          </p>
        </div>
        <button className="px-3 py-1 rounded bg-primary text-primary-foreground text-sm">
          Start
        </button>
      </div>
    </div>
  );
}