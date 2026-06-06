import { Hono } from "hono";
import { query } from "./duckdb";

interface GitHubRepo {
  id: number; name: string; full_name: string; description: string;
  language: string; stargazers_count: number; forks_count: number;
  html_url: string; topics: string; created_at: string; updated_at: string;
}

const githubRoutes = new Hono();

githubRoutes.get("/repos", (c) => {
  const limit = parseInt(c.req.query("limit") ?? "30", 10);
  try {
    const repos = query<GitHubRepo>(
      `SELECT id, name, full_name, description, language,
              stargazers_count, forks_count, html_url, topics,
              created_at, updated_at
       FROM github_data.repos
       ORDER BY stargazers_count DESC
       LIMIT ?`, limit,
    );
    return c.json({ repos });
  } catch {
    return c.json({ repos: [] });
  }
});

export default githubRoutes;
