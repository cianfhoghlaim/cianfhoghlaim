const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:4000/api/v1";

export interface SpotifyTrack {
  id: string; name: string; album_name: string; release_date: string;
  popularity: number; duration_ms: number; external_url: string;
  preview_url: string; album_cover_url: string;
  tempo: number; energy: number; danceability: number;
}

export interface GitHubRepo {
  id: number; name: string; full_name: string; description: string;
  language: string; stargazers_count: number; forks_count: number;
  html_url: string; topics: string; created_at: string; updated_at: string;
}

export interface CvEntry {
  filepath: string; category: string; filename: string;
  extracted_text: string; page_count: number;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json();
}

export const api = {
  spotify: {
    tracks: (limit = 20) => get<{ tracks: SpotifyTrack[] }>(`/spotify/tracks?limit=${limit}`),
    track: (id: string) => get<{ track: SpotifyTrack | null }>(`/spotify/tracks/${id}`),
  },
  github: {
    repos: (limit = 30) => get<{ repos: GitHubRepo[] }>(`/github/repos?limit=${limit}`),
  },
  cv: {
    entries: (category?: string) =>
      get<{ entries: CvEntry[] }>(`/cv/entries${category ? `?category=${category}` : ""}`),
    byCategory: (category: string) => get<{ entries: CvEntry[] }>(`/cv/entries/${category}`),
    search: (q: string) => get<{ entries: CvEntry[] }>(`/cv/search?q=${encodeURIComponent(q)}`),
  },
};
