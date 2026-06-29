import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { ProjectCard, ProjectCardCompact } from "@/components/code/ProjectCard";
import { Code, Github, Star, GitFork, Activity } from "lucide-react";
import { api } from "@croilar/db";
import { githubRepoToCard } from "@/lib/data-mappers";

export const Route = createFileRoute("/code")({
  component: CodePage,
});

function CodePage() {
  const [repos, setRepos] = useState<ReturnType<typeof githubRepoToCard>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.github.repos(30).then((res) => {
      setRepos(res.repos.map(githubRepoToCard));
    }).catch(() => setRepos([])).finally(() => setLoading(false));
  }, []);

  const totalStars = repos.reduce((acc, r) => acc + r.stargazers_count, 0);
  const totalForks = repos.reduce((acc, r) => acc + r.forks_count, 0);
  const languages = [...new Set(repos.map((r) => r.language).filter(Boolean))];

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Code</h1>
          <p className="text-muted-foreground text-lg">
            Open source projects and contributions on GitHub.
          </p>
        </div>

        {loading ? (
          <div className="text-center py-20 text-muted-foreground">Loading...</div>
        ) : repos.length === 0 ? (
          <div className="text-center py-20 text-muted-foreground">
            No data yet — run the DLT GitHub pipeline to populate repos.
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
              <StatCard icon={<Code className="h-5 w-5" />} label="Repositories" value={repos.length} />
              <StatCard icon={<Star className="h-5 w-5" />} label="Total Stars" value={totalStars} />
              <StatCard icon={<GitFork className="h-5 w-5" />} label="Total Forks" value={totalForks} />
              <StatCard icon={<Activity className="h-5 w-5" />} label="Languages" value={languages.length} />
            </div>

            <section className="mb-12">
              <h2 className="text-2xl font-bold mb-6">Featured Projects</h2>
              <div className="grid gap-6">
                {repos.slice(0, 3).map((repo) => (
                  <ProjectCard key={repo.id} repo={repo} />
                ))}
              </div>
            </section>

            <section>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">All Repositories</h2>
                <a
                  href="https://github.com/Yedya?tab=repositories"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-primary hover:underline"
                >
                  <Github className="h-4 w-4" /> View all on GitHub
                </a>
              </div>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {repos.map((repo) => (
                  <ProjectCardCompact key={repo.id} repo={repo} />
                ))}
              </div>
            </section>
          </>
        )}
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) {
  return (
    <div className="rounded-xl bg-card border border-border p-4">
      <div className="flex items-center gap-2 text-muted-foreground mb-2">
        {icon}<span className="text-sm">{label}</span>
      </div>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
}
