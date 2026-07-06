// /en/leaving-cert/$subject/practice/$topic — Practice detail page

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/leaving-cert/$subject/practice/$topic")({
  component: PracticePage,
});

function PracticePage() {
  const { subject, topic } = Route.useParams();

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-6 p-6">
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Link to="/" className="hover:text-emerald-400">Home</Link>
          <span>›</span>
          <Link to={`/en/subjects/${subject}`} className="hover:text-emerald-400">{subject}</Link>
          <span>›</span>
          <span className="text-slate-300">Practice · {topic}</span>
        </div>
        <h1 className="font-cinzel text-2xl font-bold text-slate-100">
          Practice: {topic}
        </h1>
        <p className="text-slate-400">
          The full practice page (formative item + 3-way boon choice +
          4 feedback channels + streak flame + 4-tier mastery) is wired
          to the {subject}_agent + the BAML GenerateFormativeItem +
          ScoreFormativeResponse schemas.
        </p>
      </div>
    </div>
  );
}