import { createFileRoute, useParams } from "@tanstack/react-router";

export const Route = createFileRoute("/teacher/$class/quests")({
  component: TeacherQuestDesignerPage,
});

function TeacherQuestDesignerPage() {
  const { class: classSlug } = useParams({ from: "/teacher/$class/quests" });
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Teacher view — class {classSlug}</h1>
      <p className="text-sm text-muted-foreground">
        Marimo-embedded quest designer. Teachers can browse all NCCA LOs
        across the 8 subjects, search the quest-pack corpus semantically, and
        generate custom formative items via the BAML client.
      </p>
      <div className="p-6 rounded-lg border bg-card">
        <p className="text-sm text-muted-foreground italic">
          (Marimo notebook iframe will be embedded here.)
        </p>
      </div>
    </div>
  );
}