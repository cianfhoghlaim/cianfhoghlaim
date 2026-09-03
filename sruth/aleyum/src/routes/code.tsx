import { createFileRoute } from "@tanstack/react-router";
import { ProjectCard, ProjectCardCompact } from "@/components/code/ProjectCard";
import { Code, Github, Star, GitFork, Activity } from "lucide-react";

export const Route = createFileRoute("/code")({
  component: CodePage,
});

// Placeholder data - will be loaded from API/database
const repositories = [
  {
    id: 1,
    name: "Portfolio",
    description: "Personal portfolio website showcasing music production and software development work.",
    language: "TypeScript",
    stargazers_count: 5,
    forks_count: 1,
    html_url: "https://github.com/Yedya/Portfolio",
    homepage: null,
    updated_at: "2024-12-01T00:00:00Z",
    topics: ["portfolio", "typescript", "react"],
  },
];

// Language statistics placeholder
const languageStats = [
  { language: "TypeScript", percentage: 45, color: "#3178c6" },
  { language: "Python", percentage: 30, color: "#3572A5" },
  { language: "JavaScript", percentage: 15, color: "#f1e05a" },
  { language: "Other", percentage: 10, color: "#6e7681" },
];

function CodePage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Code</h1>
          <p className="text-muted-foreground text-lg">
            Open source projects and contributions on GitHub.
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          <StatCard
            icon={<Code className="h-5 w-5" />}
            label="Repositories"
            value={repositories.length}
          />
          <StatCard
            icon={<Star className="h-5 w-5" />}
            label="Total Stars"
            value={repositories.reduce((acc, r) => acc + r.stargazers_count, 0)}
          />
          <StatCard
            icon={<GitFork className="h-5 w-5" />}
            label="Total Forks"
            value={repositories.reduce((acc, r) => acc + r.forks_count, 0)}
          />
          <StatCard
            icon={<Activity className="h-5 w-5" />}
            label="Languages"
            value={languageStats.length}
          />
        </div>

        {/* Language Breakdown */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Languages</h2>
          <div className="rounded-xl bg-card border border-border p-6">
            {/* Progress bar */}
            <div className="h-3 rounded-full overflow-hidden flex mb-4">
              {languageStats.map((lang) => (
                <div
                  key={lang.language}
                  className="h-full first:rounded-l-full last:rounded-r-full"
                  style={{
                    width: `${lang.percentage}%`,
                    backgroundColor: lang.color,
                  }}
                  title={`${lang.language}: ${lang.percentage}%`}
                />
              ))}
            </div>

            {/* Legend */}
            <div className="flex flex-wrap gap-4">
              {languageStats.map((lang) => (
                <div key={lang.language} className="flex items-center gap-2 text-sm">
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: lang.color }}
                  />
                  <span>{lang.language}</span>
                  <span className="text-muted-foreground">{lang.percentage}%</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Featured Projects */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Featured Projects</h2>
          <div className="grid gap-6">
            {repositories.map((repo) => (
              <ProjectCard key={repo.id} repo={repo} />
            ))}
          </div>
        </section>

        {/* All Repositories Grid */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">All Repositories</h2>
            <a
              href="https://github.com/Yedya?tab=repositories"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-primary hover:underline"
            >
              <Github className="h-4 w-4" />
              View all on GitHub
            </a>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {repositories.map((repo) => (
              <ProjectCardCompact key={repo.id} repo={repo} />
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
}

function StatCard({ icon, label, value }: StatCardProps) {
  return (
    <div className="rounded-xl bg-card border border-border p-4">
      <div className="flex items-center gap-2 text-muted-foreground mb-2">
        {icon}
        <span className="text-sm">{label}</span>
      </div>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
}
