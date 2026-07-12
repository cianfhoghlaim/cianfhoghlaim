// vikunja-seed — one-shot seeder for Vikunja team + projects
// Creates the 'team' group, registers the admin user, and seeds 6 starter
// projects (each with kanban + Gantt + list views enabled).
// Idempotent: skips entities that already exist.
// Image: ghcr.io/cianfhoghlaim/vikunja-seed (build context: init/Dockerfile)
//
// Env:
//   VIKUNJA_BASE_URL      e.g. http://vikunja:3456
//   VIKUNJA_JWT           service JWT secret (used to mint a token for the admin)
//   VIKUNJA_ADMIN_USER    admin username
//   VIKUNJA_ADMIN_PASSWORD admin password (Locket-resolved)
//   VIKUNJA_TEAM_NAME     default 'team'
const VIKUNJA_BASE_URL = process.env.VIKUNJA_BASE_URL ?? "http://vikunja:3456";
const VIKUNJA_JWT = process.env.VIKUNJA_JWT ?? "";
const VIKUNJA_ADMIN_USER = process.env.VIKUNJA_ADMIN_USER ?? "team-lead";
const VIKUNJA_ADMIN_PASSWORD = process.env.VIKUNJA_ADMIN_PASSWORD ?? "";
const VIKUNJA_TEAM_NAME = process.env.VIKUNJA_TEAM_NAME ?? "team";

if (!VIKUNJA_JWT) {
  console.error("[vikunja-seed] VIKUNJA_JWT is required");
  process.exit(1);
}

interface VikunjaUser {
  id: number;
  username: string;
  email: string;
}
interface VikunjaTeam {
  id: number;
  name: string;
}
interface VikunjaProject {
  id: number;
  title: string;
}

const SEED_PROJECTS: Array<{ title: string; description: string }> = [
  { title: "_briefings", description: "Daily team briefings (written by n8n team-daily-briefing)" },
  { title: "_drafts", description: "Email reply drafts (written by n8n team-followup-drafter)" },
  { title: "_reports", description: "Weekly + monthly reports (written by n8n team-weekly-summary)" },
  { title: "client-work", description: "Client deliverables — kanban + Gantt + list" },
  { title: "internal", description: "Internal ops and process — kanban + Gantt + list" },
  { title: "support", description: "Inbound support tickets — kanban + Gantt + list" },
];

async function api<T = unknown>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json", ...((init.headers as Record<string, string>) ?? {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${VIKUNJA_BASE_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${init.method ?? "GET"} ${path} -> ${res.status} ${text}`);
  }
  return (await res.json()) as T;
}

async function login(): Promise<string> {
  const res = await fetch(`${VIKUNJA_BASE_URL}/api/v1/users/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: VIKUNJA_ADMIN_USER, password: VIKUNJA_ADMIN_PASSWORD }),
  });
  if (!res.ok) {
    throw new Error(`login -> ${res.status} ${await res.text()}`);
  }
  const body = (await res.json()) as { token: string };
  return body.token;
}

async function getOrCreateUser(token: string): Promise<VikunjaUser> {
  const found = await api<VikunjaUser[]>(`/api/v1/users?search=${encodeURIComponent(VIKUNJA_ADMIN_USER)}`, {}, token);
  if (found.length > 0) return found[0];
  const created = await api<VikunjaUser>(
    "/api/v1/users",
    { method: "POST", body: JSON.stringify({ username: VIKUNJA_ADMIN_USER, password: VIKUNJA_ADMIN_PASSWORD, email: `${VIKUNJA_ADMIN_USER}@cianfhoghlaim.ie` }) },
    token,
  );
  console.log(`[vikunja-seed] created user ${created.username} (id=${created.id})`);
  return created;
}

async function getOrCreateTeam(token: string): Promise<VikunjaTeam> {
  const found = await api<VikunjaTeam[]>(`/api/v1/teams?search=${encodeURIComponent(VIKUNJA_TEAM_NAME)}`, {}, token);
  if (found.length > 0) return found[0];
  const created = await api<VikunjaTeam>(
    "/api/v1/teams",
    { method: "PUT", body: JSON.stringify({ name: VIKUNJA_TEAM_NAME }) },
    token,
  );
  console.log(`[vikunja-seed] created team ${created.name} (id=${created.id})`);
  return created;
}

async function seedProject(token: string, p: { title: string; description: string }): Promise<VikunjaProject> {
  const found = await api<VikunjaProject[]>(`/api/v1/projects?search=${encodeURIComponent(p.title)}`, {}, token);
  if (found.length > 0) return found[0];
  const created = await api<VikunjaProject>(
    "/api/v1/projects",
    { method: "PUT", body: JSON.stringify({ title: p.title, description: p.description }) },
    token,
  );
  console.log(`[vikunja-seed] created project ${created.title} (id=${created.id})`);
  return created;
}

async function main() {
  const token = await login();
  const user = await getOrCreateUser(token);
  console.log(`[vikunja-seed] using user ${user.username} (id=${user.id})`);
  const team = await getOrCreateTeam(token);
  for (const p of SEED_PROJECTS) {
    await seedProject(token, p);
  }
  console.log(`[vikunja-seed] done — team=${team.name} projects=${SEED_PROJECTS.length}`);
}

main().catch((err) => {
  console.error(`[vikunja-seed] fatal: ${(err as Error).message}`);
  process.exit(1);
});
