import { createFileRoute, Link } from "@tanstack/react-router";
import { Music, Code, ArrowRight, Play, Github, Disc } from "lucide-react";

export const Route = createFileRoute("/")({
  component: HomePage,
});

function HomePage() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative min-h-[80vh] flex items-center justify-center overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-background to-background" />

        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="text-primary">Aleyum</span>
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground mb-4">
              Music Producer & Software Developer
            </p>
            <p className="text-lg text-muted-foreground/80 max-w-2xl mx-auto mb-8">
              Crafting sonic landscapes and digital experiences. Where algorithmic
              precision meets creative expression.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/music"
                className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
              >
                <Music className="h-5 w-5" />
                Explore Music
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/code"
                className="inline-flex items-center justify-center gap-2 px-6 py-3 border border-border rounded-lg hover:bg-accent transition-colors"
              >
                <Code className="h-5 w-5" />
                View Projects
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Dual Identity Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-8">
            {/* Music Side */}
            <div className="group relative p-8 rounded-2xl bg-card border border-border hover:border-primary/50 transition-colors">
              <div className="flex items-center gap-4 mb-6">
                <div className="p-3 rounded-full bg-primary/10">
                  <Disc className="h-8 w-8 text-primary" />
                </div>
                <h2 className="text-2xl font-bold">Music Production</h2>
              </div>
              <p className="text-muted-foreground mb-6">
                Electronic music producer with releases on Monstercat, Lemongrass Music,
                Fokuz Recordings, and more. Specializing in Drum & Bass, Liquid Funk,
                and ambient electronic soundscapes.
              </p>
              <div className="flex flex-wrap gap-2 mb-6">
                {["Drum & Bass", "Liquid Funk", "Electronic", "Ambient"].map((genre) => (
                  <span
                    key={genre}
                    className="px-3 py-1 text-sm rounded-full bg-primary/10 text-primary"
                  >
                    {genre}
                  </span>
                ))}
              </div>
              <Link
                to="/music"
                className="inline-flex items-center gap-2 text-primary hover:underline"
              >
                <Play className="h-4 w-4" />
                Listen to tracks
              </Link>
            </div>

            {/* Code Side */}
            <div className="group relative p-8 rounded-2xl bg-card border border-border hover:border-primary/50 transition-colors">
              <div className="flex items-center gap-4 mb-6">
                <div className="p-3 rounded-full bg-primary/10">
                  <Code className="h-8 w-8 text-primary" />
                </div>
                <h2 className="text-2xl font-bold">Software Development</h2>
              </div>
              <p className="text-muted-foreground mb-6">
                Full-stack developer with expertise in data engineering, web applications,
                and AI systems. Building robust pipelines and elegant interfaces.
              </p>
              <div className="flex flex-wrap gap-2 mb-6">
                {["Python", "TypeScript", "React", "Data Engineering"].map((tech) => (
                  <span
                    key={tech}
                    className="px-3 py-1 text-sm rounded-full bg-primary/10 text-primary"
                  >
                    {tech}
                  </span>
                ))}
              </div>
              <Link
                to="/code"
                className="inline-flex items-center gap-2 text-primary hover:underline"
              >
                <Github className="h-4 w-4" />
                View repositories
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Section */}
      <section className="py-20 bg-card/50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Featured Work</h2>

          <div className="grid md:grid-cols-3 gap-6">
            {/* Placeholder cards - will be populated from data */}
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="relative aspect-square rounded-xl bg-card border border-border overflow-hidden group"
              >
                <div className="absolute inset-0 bg-gradient-to-t from-background/90 to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 p-4">
                  <p className="font-semibold">Featured Work {i}</p>
                  <p className="text-sm text-muted-foreground">Coming soon</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Labels Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-2xl font-bold text-center mb-8">Released On</h2>
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
            {["Monstercat", "Lemongrass", "Fokuz", "Immersed", "Offworld", "Soul Deep"].map(
              (label) => (
                <span key={label} className="text-lg font-medium">
                  {label}
                </span>
              )
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
