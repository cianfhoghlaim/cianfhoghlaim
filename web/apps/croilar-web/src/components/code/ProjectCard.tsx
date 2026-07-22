import { Star, GitFork, ExternalLink, Github, Calendar } from "lucide-react";
import { cn, formatNumber } from "@/lib/utils";

interface Repository {
  id: number;
  name: string;
  description: string | null;
  language: string | null;
  stargazers_count: number;
  forks_count: number;
  html_url: string;
  homepage: string | null;
  updated_at: string;
  topics?: string[];
}

interface ProjectCardProps {
  repo: Repository;
  className?: string;
}

// Language colors (subset of GitHub's language colors)
const languageColors: Record<string, string> = {
  TypeScript: "#3178c6",
  JavaScript: "#f1e05a",
  Python: "#3572A5",
  Rust: "#dea584",
  Go: "#00ADD8",
  Java: "#b07219",
  "C++": "#f34b7d",
  C: "#555555",
  HTML: "#e34c26",
  CSS: "#563d7c",
  Shell: "#89e051",
  Ruby: "#701516",
};

export function ProjectCard({ repo, className }: ProjectCardProps) {
  const languageColor = repo.language
    ? languageColors[repo.language] || "#6e7681"
    : "#6e7681";

  const updatedDate = new Date(repo.updated_at).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  return (
    <div
      className={cn(
        "group relative rounded-xl bg-card border border-border p-6 hover:border-primary/50 transition-colors flex flex-col h-full",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <Github className="h-5 w-5 text-muted-foreground" />
          <h3 className="font-semibold text-lg hover:text-primary transition-colors">
            <a href={repo.html_url} target="_blank" rel="noopener noreferrer">
              {repo.name}
            </a>
          </h3>
        </div>

        {/* External links */}
        <div className="flex items-center gap-2">
          {repo.homepage && (
            <a
              href={repo.homepage}
              target="_blank"
              rel="noopener noreferrer"
              className="p-1.5 rounded-md hover:bg-muted transition-colors"
              title="Live demo"
            >
              <ExternalLink className="h-4 w-4 text-muted-foreground" />
            </a>
          )}
          <a
            href={repo.html_url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-1.5 rounded-md hover:bg-muted transition-colors"
            title="View on GitHub"
          >
            <Github className="h-4 w-4 text-muted-foreground" />
          </a>
        </div>
      </div>

      {/* Description */}
      <p className="text-muted-foreground text-sm mb-4 flex-grow line-clamp-3">
        {repo.description || "No description available"}
      </p>

      {/* Topics/Tags */}
      {repo.topics && repo.topics.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {repo.topics.slice(0, 4).map((topic) => (
            <span
              key={topic}
              className="px-2 py-0.5 text-xs rounded-full bg-primary/10 text-primary"
            >
              {topic}
            </span>
          ))}
          {repo.topics.length > 4 && (
            <span className="px-2 py-0.5 text-xs rounded-full bg-muted text-muted-foreground">
              +{repo.topics.length - 4}
            </span>
          )}
        </div>
      )}

      {/* Footer stats */}
      <div className="flex items-center gap-4 text-sm text-muted-foreground pt-4 border-t border-border mt-auto">
        {/* Language */}
        {repo.language && (
          <div className="flex items-center gap-1.5">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: languageColor }}
            />
            <span>{repo.language}</span>
          </div>
        )}

        {/* Stars */}
        <div className="flex items-center gap-1">
          <Star className="h-4 w-4" />
          <span>{formatNumber(repo.stargazers_count)}</span>
        </div>

        {/* Forks */}
        <div className="flex items-center gap-1">
          <GitFork className="h-4 w-4" />
          <span>{formatNumber(repo.forks_count)}</span>
        </div>

        {/* Updated date */}
        <div className="flex items-center gap-1 ml-auto">
          <Calendar className="h-4 w-4" />
          <span>{updatedDate}</span>
        </div>
      </div>
    </div>
  );
}

// Compact version for grid layouts
export function ProjectCardCompact({ repo, className }: ProjectCardProps) {
  const languageColor = repo.language
    ? languageColors[repo.language] || "#6e7681"
    : "#6e7681";

  return (
    <a
      href={repo.html_url}
      target="_blank"
      rel="noopener noreferrer"
      className={cn(
        "block rounded-lg bg-card border border-border p-4 hover:border-primary/50 hover:bg-card/80 transition-colors",
        className
      )}
    >
      <div className="flex items-center gap-2 mb-2">
        {repo.language && (
          <span
            className="w-2.5 h-2.5 rounded-full flex-shrink-0"
            style={{ backgroundColor: languageColor }}
          />
        )}
        <h4 className="font-medium truncate">{repo.name}</h4>
      </div>

      <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
        {repo.description || "No description"}
      </p>

      <div className="flex items-center gap-3 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <Star className="h-3 w-3" />
          {repo.stargazers_count}
        </span>
        <span className="flex items-center gap-1">
          <GitFork className="h-3 w-3" />
          {repo.forks_count}
        </span>
      </div>
    </a>
  );
}
