import { Hono } from "hono";
import { query } from "./duckdb";

interface SpotifyTrack {
  id: string; name: string; album_name: string; release_date: string;
  popularity: number; duration_ms: number; external_url: string;
  preview_url: string; album_cover_url: string;
  tempo: number; energy: number; danceability: number;
}

const spotifyRoutes = new Hono();

spotifyRoutes.get("/tracks", (c) => {
  const limit = parseInt(c.req.query("limit") ?? "20", 10);
  try {
    const tracks = query<SpotifyTrack>(
      `SELECT id, name, album_name, release_date, popularity,
              duration_ms, external_url, preview_url, album_cover_url,
              tempo, energy, danceability
       FROM spotify_data.tracks
       ORDER BY popularity DESC
       LIMIT ?`, limit,
    );
    return c.json({ tracks });
  } catch {
    return c.json({ tracks: [] });
  }
});

spotifyRoutes.get("/tracks/:id", (c) => {
  const id = c.req.param("id");
  try {
    const tracks = query<SpotifyTrack>(
      `SELECT * FROM spotify_data.tracks WHERE id = ?`, id,
    );
    return c.json({ track: tracks[0] ?? null });
  } catch {
    return c.json({ track: null });
  }
});

export default spotifyRoutes;
