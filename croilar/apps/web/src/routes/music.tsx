import { createFileRoute } from "@tanstack/react-router";
import { AudioCard } from "@/components/music/AudioCard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Music, Headphones, Radio } from "lucide-react";

export const Route = createFileRoute("/music")({
  component: MusicPage,
});

// Placeholder data - will be loaded from API/database
const spotifyTracks = [
  {
    id: "1",
    title: "Example Track 1",
    artist: "Aleyum",
    platform: "spotify" as const,
    artworkUrl: "",
    duration: 240000,
    plays: 125000,
    likes: 5400,
    audioFeatures: {
      tempo: 174,
      energy: 0.85,
      danceability: 0.72,
      valence: 0.65,
    },
  },
];

const soundcloudTracks = [
  {
    id: "2",
    title: "SoundCloud Track 1",
    artist: "Aleyum",
    platform: "soundcloud" as const,
    artworkUrl: "",
    duration: 320000,
    plays: 45000,
    likes: 2100,
    comments: 87,
    reposts: 340,
  },
];

function MusicPage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Music</h1>
          <p className="text-muted-foreground text-lg">
            Explore productions, remixes, and collaborations across platforms.
          </p>
        </div>

        {/* Platform Tabs */}
        <Tabs defaultValue="all" className="mb-12">
          <TabsList className="grid w-full grid-cols-3 max-w-md mx-auto">
            <TabsTrigger value="all" className="flex items-center gap-2">
              <Music className="h-4 w-4" />
              All
            </TabsTrigger>
            <TabsTrigger value="spotify" className="flex items-center gap-2">
              <Headphones className="h-4 w-4" />
              Spotify
            </TabsTrigger>
            <TabsTrigger value="soundcloud" className="flex items-center gap-2">
              <Radio className="h-4 w-4" />
              SoundCloud
            </TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-8">
            <div className="grid gap-6">
              {[...spotifyTracks, ...soundcloudTracks].map((track) => (
                <AudioCard key={track.id} track={track} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="spotify" className="mt-8">
            <div className="grid gap-6">
              {spotifyTracks.map((track) => (
                <AudioCard key={track.id} track={track} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="soundcloud" className="mt-8">
            <div className="grid gap-6">
              {soundcloudTracks.map((track) => (
                <AudioCard key={track.id} track={track} />
              ))}
            </div>
          </TabsContent>
        </Tabs>

        {/* Embedded Players Section */}
        <section className="mt-16">
          <h2 className="text-2xl font-bold mb-6">Listen Now</h2>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Spotify Embed Placeholder */}
            <div className="rounded-xl bg-card border border-border p-4">
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <Headphones className="h-5 w-5 text-green-500" />
                Spotify
              </h3>
              <div className="aspect-[3/4] bg-muted rounded-lg flex items-center justify-center">
                <p className="text-muted-foreground text-sm">
                  Spotify embed will load here
                </p>
              </div>
            </div>

            {/* SoundCloud Embed Placeholder */}
            <div className="rounded-xl bg-card border border-border p-4">
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <Radio className="h-5 w-5 text-orange-500" />
                SoundCloud
              </h3>
              <div className="aspect-[3/4] bg-muted rounded-lg flex items-center justify-center">
                <p className="text-muted-foreground text-sm">
                  SoundCloud embed will load here
                </p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
