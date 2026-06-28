import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AudioCard } from "@/components/music/AudioCard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Music, Headphones, Radio } from "lucide-react";
import { api } from "@croilar/db";
import { spotifyTrackToAudioCard } from "@/lib/data-mappers";

export const Route = createFileRoute("/music")({
  component: MusicPage,
});

function MusicPage() {
  const [tracks, setTracks] = useState<ReturnType<typeof spotifyTrackToAudioCard>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.spotify.tracks(20).then((res) => {
      setTracks(res.tracks.map(spotifyTrackToAudioCard));
    }).catch(() => setTracks([])).finally(() => setLoading(false));
  }, []);

  const spotifyTracks = tracks.filter((t) => t.platform === "spotify");

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Music</h1>
          <p className="text-muted-foreground text-lg">
            Productions, remixes, and collaborations across platforms.
          </p>
        </div>

        {loading ? (
          <div className="text-center py-20 text-muted-foreground">Loading...</div>
        ) : tracks.length === 0 ? (
          <div className="text-center py-20 text-muted-foreground">
            No data yet — run the DLT pipelines to populate the catalogue.
          </div>
        ) : (
          <>
            <Tabs defaultValue="all" className="mb-12">
              <TabsList className="grid w-full grid-cols-2 max-w-xs mx-auto">
                <TabsTrigger value="all" className="flex items-center gap-2">
                  <Music className="h-4 w-4" /> All
                </TabsTrigger>
                <TabsTrigger value="spotify" className="flex items-center gap-2">
                  <Headphones className="h-4 w-4" /> Spotify
                </TabsTrigger>
              </TabsList>
              <TabsContent value="all" className="mt-8">
                <div className="grid gap-6">
                  {tracks.map((track) => <AudioCard key={track.id} track={track} />)}
                </div>
              </TabsContent>
              <TabsContent value="spotify" className="mt-8">
                <div className="grid gap-6">
                  {spotifyTracks.map((track) => <AudioCard key={track.id} track={track} />)}
                </div>
              </TabsContent>
            </Tabs>

            <section className="mt-16">
              <h2 className="text-2xl font-bold mb-6">Listen Now</h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="rounded-xl bg-card border border-border p-4">
                  <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Headphones className="h-5 w-5 text-green-500" /> Spotify
                  </h3>
                  <iframe
                    src="https://open.spotify.com/embed/artist/2vLlk2CcC4NnN7yoNSTmX2"
                    className="w-full aspect-[3/4] rounded-lg"
                    allow="encrypted-media"
                    title="Spotify Player"
                  />
                </div>
                <div className="rounded-xl bg-card border border-border p-4">
                  <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Radio className="h-5 w-5 text-orange-500" /> SoundCloud
                  </h3>
                  <iframe
                    width="100%"
                    height="400"
                    scrolling="no"
                    allow="autoplay"
                    className="rounded-lg"
                    src="https://w.soundcloud.com/player/?url=https%3A//soundcloud.com/aleyummusic&color=%23ff5500&auto_play=false&hide_related=true&show_comments=false&show_user=true&show_reposts=false&show_teaser=false"
                    title="SoundCloud Player"
                  />
                </div>
              </div>
            </section>
          </>
        )}
      </div>
    </div>
  );
}
