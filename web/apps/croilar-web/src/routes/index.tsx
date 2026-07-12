import { createFileRoute } from "@tanstack/react-router";
import { HeroSection, SubprojectGrid } from "@/pages/home/hero";

export const Route = createFileRoute("/")({
  component: HomePage,
});

const SUBPROJECTS = [
  { to: "/cv", icon: "📄", title: "Curriculum Vitae", description: "Education, awards, publications, references — extracted from source PDFs via BAML." },
  { to: "/music", icon: "🎵", title: "Music", description: "Spotify · SoundCloud · YouTube playlist + audio analytics (tempo, energy, danceability)." },
  { to: "/code", icon: "💻", title: "Code", description: "Open source repositories for @Yedya — sorted by stars + last-updated." },
  { to: "/research", icon: "🔬", title: "Research", description: "Cross-linked outputs from the oideachais and meaisínfhoghlaim subprojects." },
  { to: "/teaching", icon: "🏫", title: "Teaching", description: "BCS PGC scholarship, school placements, and student feedback." },
  { to: "/data", icon: "📊", title: "Data Engineering", description: "Live Dagster pipeline status — 13 assets, 3 schedules, materialisation history." },
  { to: "/identity", icon: "🛡️", title: "Identity", description: "Verification metadata (GPG-encrypted PII, Pocket ID-gated)." },
  { to: "/contact", icon: "✉️", title: "Contact", description: "End-to-end encrypted form (HMAC-signed → Hono Worker on Cloudflare)." },
];

function HomePage() {
  return (
    <div className="flex flex-col">
      <HeroSection />
      <SubprojectGrid cards={SUBPROJECTS} />
    </div>
  );
}
