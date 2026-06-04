import { useTranslation } from "react-i18next";
import { MessageSquare, Star } from "lucide-react";

const PLACEHOLDER_FEEDBACK = [
  {
    source: "Cooperating Teacher, Coláiste Iognáid",
    quote: "Cian demonstrates excellent classroom management and builds strong rapport with students. His Irish-language resources are particularly creative and well-structured.",
    rating: 5,
  },
  {
    source: "PME Supervisor, University of Galway",
    quote: "Outstanding lesson planning with strong integration of technology. The use of Python notebooks to teach probability in Mathematics was a genuine innovation.",
    rating: 5,
  },
  {
    source: "Student, Leaving Cert Gaeilge class",
    quote: "Bhí na ceachtanna suimiúil agus cabhrach. Mhúin sé dúinn conas an Ghaeilge a úsáid go nádúrtha agus go muiníneach.",
    rating: 5,
  },
];

export function FeedbackSection() {
  const { t } = useTranslation();

  return (
    <section id="feedback">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <MessageSquare className="h-6 w-6" />
        {t("teaching.feedback")}
      </h2>
      <div className="space-y-4">
        {PLACEHOLDER_FEEDBACK.map((fb, i) => (
          <div key={i} className="rounded-xl bg-card border border-border p-6">
            <div className="flex items-center gap-1 mb-2">
              {Array.from({ length: fb.rating }).map((_, j) => (
                <Star key={j} className="h-4 w-4 fill-amber-400 text-amber-400" />
              ))}
            </div>
            <blockquote className="text-muted-foreground italic mb-3">
              &ldquo;{fb.quote}&rdquo;
            </blockquote>
            <p className="text-sm text-primary">&mdash; {fb.source}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
