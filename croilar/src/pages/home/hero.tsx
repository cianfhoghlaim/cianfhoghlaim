import { useTranslation } from "react-i18next";
import { ArrowRight } from "lucide-react";
import { Link } from "@tanstack/react-router";

export function HeroSection() {
  const { t } = useTranslation();

  return (
    <section className="relative min-h-[85vh] flex items-center justify-center overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-background to-background" />
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 tracking-tight">
            <span className="text-primary">Cian</span>{" "}
            <span className="text-foreground">de Búrca</span>
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-4">
            {t("home.role")}
          </p>
          <p className="text-lg text-muted-foreground/80 max-w-2xl mx-auto mb-10">
            {t("home.heroTagline")}
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/cv"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              {t("home.exploreCv")}
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/music"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 border border-border rounded-lg hover:bg-accent transition-colors"
            >
              {t("home.exploreMusic")}
            </Link>
            <Link
              to="/code"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 border border-border rounded-lg hover:bg-accent transition-colors"
            >
              {t("home.exploreCode")}
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

interface SubprojectCardProps {
  to: string;
  icon: string;
  title: string;
  description: string;
}

export function SubprojectGrid({ cards }: { cards: SubprojectCardProps[] }) {
  return (
    <section className="py-20">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-12">Explore</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {cards.map((card) => (
            <Link
              key={card.to}
              to={card.to}
              className="group rounded-2xl bg-card border border-border hover:border-primary/50 transition-colors p-6"
            >
              <span className="text-3xl mb-4 block">{card.icon}</span>
              <h3 className="font-bold text-lg mb-2">{card.title}</h3>
              <p className="text-muted-foreground text-sm">{card.description}</p>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
