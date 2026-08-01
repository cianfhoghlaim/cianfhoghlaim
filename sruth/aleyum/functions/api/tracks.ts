/**
 * Tracks API - Cloudflare Pages Function
 *
 * Serves track metadata from static JSON files.
 * In production, this could connect to DuckDB via HTTP or read from R2.
 */

interface Env {
  ASSETS_BUCKET: R2Bucket;
  DATA_BUCKET: R2Bucket;
}

interface Track {
  id: string;
  title: string;
  artist: string;
  platform: "spotify" | "soundcloud";
  plays?: number;
  likes?: number;
  comments?: number;
  reposts?: number;
  duration_ms: number;
  artwork_url?: string;
  stream_url?: string;
  external_url?: string;
  audio_features?: {
    tempo: number;
    energy: number;
    danceability: number;
    valence: number;
    acousticness: number;
    instrumentalness: number;
    speechiness: number;
    liveness: number;
  };
}

// Static data for now - will be populated by DLT pipelines
const tracks: Track[] = [
  {
    id: "spotify-1",
    title: "Sample Track",
    artist: "Aleyum",
    platform: "spotify",
    plays: 50000,
    likes: 1200,
    duration_ms: 240000,
    external_url: "https://open.spotify.com/artist/2vLlk2CcC4NnN7yoNSTmX2",
    audio_features: {
      tempo: 174,
      energy: 0.75,
      danceability: 0.65,
      valence: 0.6,
      acousticness: 0.1,
      instrumentalness: 0.85,
      speechiness: 0.05,
      liveness: 0.15,
    },
  },
];

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const url = new URL(context.request.url);
  const platform = url.searchParams.get("platform");
  const limit = parseInt(url.searchParams.get("limit") || "50", 10);

  let filteredTracks = tracks;

  // Filter by platform if specified
  if (platform && (platform === "spotify" || platform === "soundcloud")) {
    filteredTracks = tracks.filter((t) => t.platform === platform);
  }

  // Apply limit
  filteredTracks = filteredTracks.slice(0, limit);

  return new Response(JSON.stringify({ tracks: filteredTracks }), {
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "public, max-age=300", // 5 minute cache
    },
  });
};

// Stream audio from R2
export const onRequestGetAudio: PagesFunction<Env> = async (context) => {
  const url = new URL(context.request.url);
  const trackId = url.searchParams.get("id");

  if (!trackId) {
    return new Response(JSON.stringify({ error: "Track ID required" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Try to get audio from R2
  const audioKey = `audio/${trackId}.mp3`;
  const object = await context.env.ASSETS_BUCKET.get(audioKey);

  if (!object) {
    return new Response(JSON.stringify({ error: "Track not found" }), {
      status: 404,
      headers: { "Content-Type": "application/json" },
    });
  }

  const headers = new Headers();
  object.writeHttpMetadata(headers);
  headers.set("Content-Type", "audio/mpeg");
  headers.set("Accept-Ranges", "bytes");
  headers.set("Cache-Control", "public, max-age=86400"); // 24 hour cache

  return new Response(object.body, { headers });
};
