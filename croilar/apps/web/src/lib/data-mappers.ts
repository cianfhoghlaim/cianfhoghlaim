import type { SpotifyTrack, GitHubRepo } from "@croilar/db";

export function spotifyTrackToAudioCard(t: SpotifyTrack) {
  return {
    id: t.id,
    title: t.name,
    artist: "Aleyum",
    platform: "spotify" as const,
    artworkUrl: t.album_cover_url ?? undefined,
    duration: t.duration_ms,
    plays: t.popularity * 1000,
    likes: Math.round(t.popularity * 40),
    audioFeatures: {
      tempo: t.tempo,
      energy: t.energy,
      danceability: t.danceability,
    },
    previewUrl: t.preview_url ?? undefined,
  };
}

export function githubRepoToCard(r: GitHubRepo) {
  return {
    id: r.id,
    name: r.name,
    description: r.description ?? null,
    language: r.language ?? null,
    stargazers_count: r.stargazers_count,
    forks_count: r.forks_count,
    html_url: r.html_url,
    homepage: null,
    updated_at: r.updated_at,
    topics: r.topics ? r.topics.split(",").map((s: string) => s.trim()) : [],
  };
}
