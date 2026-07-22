import { Play, Pause, Heart, MessageCircle, Share2, Clock, Activity, Music } from "lucide-react";
import { useState } from "react";
import { cn, formatNumber, formatDuration } from "@/lib/utils";

interface AudioFeatures {
  tempo?: number;
  energy?: number;
  danceability?: number;
  valence?: number;
  acousticness?: number;
  instrumentalness?: number;
}

interface Track {
  id: string;
  title: string;
  artist: string;
  platform: "spotify" | "soundcloud";
  artworkUrl?: string;
  duration: number; // ms
  plays: number;
  likes: number;
  comments?: number;
  reposts?: number;
  followers?: number;
  audioFeatures?: AudioFeatures;
  previewUrl?: string;
  streamUrl?: string; // R2 URL for audio streaming
}

interface AudioCardProps {
  track: Track;
  className?: string;
}

export function AudioCard({ track, className }: AudioCardProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [showFeatures, setShowFeatures] = useState(false);

  const platformColors = {
    spotify: "text-green-500 bg-green-500/10",
    soundcloud: "text-orange-500 bg-orange-500/10",
  };

  return (
    <div
      className={cn(
        "group relative rounded-xl bg-card border border-border overflow-hidden hover:border-primary/50 transition-colors",
        className
      )}
    >
      <div className="flex flex-col sm:flex-row">
        {/* Artwork */}
        <div className="relative w-full sm:w-48 h-48 bg-muted flex-shrink-0">
          {track.artworkUrl ? (
            <img
              src={track.artworkUrl}
              alt={track.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Music className="h-12 w-12 text-muted-foreground" />
            </div>
          )}

          {/* Play overlay */}
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            {isPlaying ? (
              <Pause className="h-12 w-12 text-white" />
            ) : (
              <Play className="h-12 w-12 text-white" />
            )}
          </button>

          {/* Platform badge */}
          <span
            className={cn(
              "absolute top-2 left-2 px-2 py-1 text-xs font-medium rounded-full capitalize",
              platformColors[track.platform]
            )}
          >
            {track.platform}
          </span>
        </div>

        {/* Content */}
        <div className="flex-1 p-4 flex flex-col">
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="font-semibold text-lg">{track.title}</h3>
              <p className="text-muted-foreground">{track.artist}</p>
            </div>
            <span className="flex items-center gap-1 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" />
              {formatDuration(track.duration)}
            </span>
          </div>

          {/* Stats Row */}
          <div className="flex flex-wrap gap-4 mb-4">
            <div className="flex items-center gap-1.5 text-sm">
              <Play className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">{formatNumber(track.plays)}</span>
              <span className="text-muted-foreground">plays</span>
            </div>
            <div className="flex items-center gap-1.5 text-sm">
              <Heart className="h-4 w-4 text-red-500" />
              <span className="font-medium">{formatNumber(track.likes)}</span>
              <span className="text-muted-foreground">likes</span>
            </div>
            {track.comments !== undefined && (
              <div className="flex items-center gap-1.5 text-sm">
                <MessageCircle className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">{formatNumber(track.comments)}</span>
                <span className="text-muted-foreground">comments</span>
              </div>
            )}
            {track.reposts !== undefined && (
              <div className="flex items-center gap-1.5 text-sm">
                <Share2 className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">{formatNumber(track.reposts)}</span>
                <span className="text-muted-foreground">reposts</span>
              </div>
            )}
          </div>

          {/* Audio Features Toggle */}
          {track.audioFeatures && (
            <div className="mt-auto">
              <button
                onClick={() => setShowFeatures(!showFeatures)}
                className="flex items-center gap-2 text-sm text-primary hover:underline"
              >
                <Activity className="h-4 w-4" />
                {showFeatures ? "Hide" : "Show"} Audio Features
              </button>

              {showFeatures && (
                <div className="mt-3 p-3 rounded-lg bg-muted/50 grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {track.audioFeatures.tempo && (
                    <FeatureBar
                      label="Tempo"
                      value={track.audioFeatures.tempo}
                      max={200}
                      unit="BPM"
                      showPercentage={false}
                    />
                  )}
                  {track.audioFeatures.energy !== undefined && (
                    <FeatureBar
                      label="Energy"
                      value={track.audioFeatures.energy}
                      max={1}
                    />
                  )}
                  {track.audioFeatures.danceability !== undefined && (
                    <FeatureBar
                      label="Danceability"
                      value={track.audioFeatures.danceability}
                      max={1}
                    />
                  )}
                  {track.audioFeatures.valence !== undefined && (
                    <FeatureBar
                      label="Mood (Valence)"
                      value={track.audioFeatures.valence}
                      max={1}
                    />
                  )}
                  {track.audioFeatures.acousticness !== undefined && (
                    <FeatureBar
                      label="Acousticness"
                      value={track.audioFeatures.acousticness}
                      max={1}
                    />
                  )}
                  {track.audioFeatures.instrumentalness !== undefined && (
                    <FeatureBar
                      label="Instrumental"
                      value={track.audioFeatures.instrumentalness}
                      max={1}
                    />
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

interface FeatureBarProps {
  label: string;
  value: number;
  max: number;
  unit?: string;
  showPercentage?: boolean;
}

function FeatureBar({
  label,
  value,
  max,
  unit,
  showPercentage = true,
}: FeatureBarProps) {
  const percentage = (value / max) * 100;

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">
          {showPercentage
            ? `${Math.round(percentage)}%`
            : `${Math.round(value)}${unit ? ` ${unit}` : ""}`}
        </span>
      </div>
      <div className="h-1.5 rounded-full bg-muted overflow-hidden">
        <div
          className="h-full rounded-full bg-primary transition-all"
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    </div>
  );
}
