import { createFileRoute, Link } from "@tanstack/react-router";
import { MessageSquare, GitCompare, Languages, Search, BookOpen, Globe } from "lucide-react";
import { cn } from "../lib/utils";

export const Route = createFileRoute("/")({
  component: HomePage,
});

const features = [
  {
    name: "AI Curriculum Chat",
    description: "Ask questions about curricula across Ireland, UK, and Celtic nations",
    href: "/chat",
    icon: MessageSquare,
  },
  {
    name: "Cross-Curriculum Comparison",
    description: "Compare learning outcomes between nations at equivalent levels",
    href: "/curriculum/compare",
    icon: GitCompare,
  },
  {
    name: "Translation Review",
    description: "Review and approve AI translations for Celtic languages",
    href: "/translation",
    icon: Languages,
  },
];

const stats = [
  { label: "Nations Covered", value: "5" },
  { label: "Learning Outcomes", value: "10,000+" },
  { label: "Cross-Alignments", value: "5,000+" },
  { label: "Languages", value: "5" },
];

function HomePage() {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center space-y-4">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          Pan-Celtic Educational Platform
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Compare and explore curricula across Ireland, England, Scotland, Wales, and Northern Ireland.
          AI-powered search with Celtic language support.
        </p>
        <div className="flex justify-center gap-4 pt-4">
          <Link
            to="/chat"
            className={cn(
              "inline-flex items-center justify-center rounded-md text-sm font-medium",
              "bg-primary text-primary-foreground hover:bg-primary/90",
              "h-10 px-4 py-2"
            )}
          >
            <MessageSquare className="mr-2 h-4 w-4" />
            Start Chatting
          </Link>
          <Link
            to="/curriculum/compare"
            className={cn(
              "inline-flex items-center justify-center rounded-md text-sm font-medium",
              "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
              "h-10 px-4 py-2"
            )}
          >
            <GitCompare className="mr-2 h-4 w-4" />
            Compare Curricula
          </Link>
        </div>
      </section>

      {/* Stats */}
      <section className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="rounded-lg border bg-card p-4 text-center"
          >
            <div className="text-2xl font-bold text-primary">{stat.value}</div>
            <div className="text-sm text-muted-foreground">{stat.label}</div>
          </div>
        ))}
      </section>

      {/* Features */}
      <section className="space-y-6">
        <h2 className="text-2xl font-bold text-center">Features</h2>
        <div className="grid gap-6 md:grid-cols-3">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Link
                key={feature.name}
                to={feature.href}
                className="group rounded-lg border bg-card p-6 hover:border-primary transition-colors"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="rounded-md bg-primary/10 p-2">
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                  <h3 className="font-semibold group-hover:text-primary transition-colors">
                    {feature.name}
                  </h3>
                </div>
                <p className="text-sm text-muted-foreground">
                  {feature.description}
                </p>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Nations */}
      <section className="space-y-6">
        <h2 className="text-2xl font-bold text-center">Supported Nations</h2>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
          {[
            { name: "Ireland", code: "IE", languages: ["en", "ga"] },
            { name: "England", code: "EN", languages: ["en"] },
            { name: "Scotland", code: "SC", languages: ["en", "gd"] },
            { name: "Wales", code: "WA", languages: ["en", "cy"] },
            { name: "N. Ireland", code: "NI", languages: ["en", "ga"] },
          ].map((nation) => (
            <div
              key={nation.code}
              className="rounded-lg border bg-card p-4 text-center space-y-2"
            >
              <Globe className="h-8 w-8 mx-auto text-primary" />
              <div className="font-medium">{nation.name}</div>
              <div className="flex justify-center gap-1">
                {nation.languages.map((lang) => (
                  <span
                    key={lang}
                    className="text-xs bg-muted px-2 py-0.5 rounded"
                  >
                    {lang.toUpperCase()}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Quick Search */}
      <section className="rounded-lg border bg-card p-6 space-y-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Search className="h-5 w-5" />
          Quick Search
        </h2>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Search learning outcomes, subjects, or topics..."
            className={cn(
              "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm",
              "ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium",
              "placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2",
              "focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            )}
          />
          <button
            className={cn(
              "inline-flex items-center justify-center rounded-md text-sm font-medium",
              "bg-primary text-primary-foreground hover:bg-primary/90",
              "h-10 px-4"
            )}
          >
            Search
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          <span className="text-sm text-muted-foreground">Popular:</span>
          {["Junior Cycle Maths", "GCSE Science", "Leaving Cert Irish", "A-Level History"].map(
            (term) => (
              <button
                key={term}
                className="text-sm text-primary hover:underline"
              >
                {term}
              </button>
            )
          )}
        </div>
      </section>
    </div>
  );
}
