import { createFileRoute } from "@tanstack/react-router";
import { Download, Mail, MapPin, Briefcase, GraduationCap } from "lucide-react";

export const Route = createFileRoute("/about")({
  component: AboutPage,
});

function AboutPage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="w-32 h-32 rounded-full bg-muted mx-auto mb-6 flex items-center justify-center">
            {/* Profile image placeholder */}
            <span className="text-4xl font-bold text-muted-foreground">CH</span>
          </div>
          <h1 className="text-4xl font-bold mb-2">Conor Hynes</h1>
          <p className="text-xl text-primary mb-4">Aleyum</p>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Music producer and software developer combining technical precision
            with creative expression. Building data pipelines by day, crafting
            electronic soundscapes by night.
          </p>

          <div className="flex items-center justify-center gap-4 mt-6">
            <span className="flex items-center gap-2 text-muted-foreground">
              <MapPin className="h-4 w-4" />
              Ireland
            </span>
            <a
              href="mailto:contact@aleyum.com"
              className="flex items-center gap-2 text-primary hover:underline"
            >
              <Mail className="h-4 w-4" />
              Contact
            </a>
            <a
              href="https://github.com/Yedya/Portfolio/blob/master/Conor_Hynes_Resume_.pdf"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              <Download className="h-4 w-4" />
              Resume
            </a>
          </div>
        </div>

        {/* Skills Matrix */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Skills</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {/* Music Production Skills */}
            <div className="rounded-xl bg-card border border-border p-6">
              <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <span className="text-primary">🎵</span>
                Music Production
              </h3>
              <div className="space-y-3">
                <SkillBar label="DAW (Ableton, Logic)" level={90} />
                <SkillBar label="Sound Design" level={85} />
                <SkillBar label="Mixing & Mastering" level={80} />
                <SkillBar label="Music Theory" level={75} />
                <SkillBar label="Synthesis" level={85} />
              </div>
            </div>

            {/* Software Development Skills */}
            <div className="rounded-xl bg-card border border-border p-6">
              <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <span className="text-primary">💻</span>
                Software Development
              </h3>
              <div className="space-y-3">
                <SkillBar label="Python" level={90} />
                <SkillBar label="TypeScript / JavaScript" level={85} />
                <SkillBar label="React / TanStack" level={80} />
                <SkillBar label="Data Engineering (DLT, Dagster)" level={85} />
                <SkillBar label="Cloud (Cloudflare, AWS)" level={75} />
              </div>
            </div>
          </div>
        </section>

        {/* Experience */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Briefcase className="h-6 w-6" />
            Experience
          </h2>
          <div className="space-y-6">
            <ExperienceCard
              title="Music Producer"
              company="Independent / Various Labels"
              period="2015 - Present"
              description="Released music on Monstercat, Lemongrass Music, Fokuz Recordings, and other labels. Specializing in Drum & Bass, Liquid Funk, and ambient electronic music."
            />
            <ExperienceCard
              title="Software Developer"
              company="Various Projects"
              period="2018 - Present"
              description="Full-stack development with focus on data engineering, building pipelines with DLT, Dagster, and modern web applications with React and TanStack."
            />
          </div>
        </section>

        {/* Education */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <GraduationCap className="h-6 w-6" />
            Education
          </h2>
          <div className="rounded-xl bg-card border border-border p-6">
            <h3 className="font-semibold text-lg">Computer Science</h3>
            <p className="text-muted-foreground">University</p>
            <p className="text-sm text-muted-foreground mt-2">
              Focus on software engineering, data structures, and algorithms.
            </p>
          </div>
        </section>

        {/* Music Labels */}
        <section>
          <h2 className="text-2xl font-bold mb-6">Labels & Releases</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {[
              { name: "Monstercat", url: "https://www.monstercat.com/artist/aleyum" },
              { name: "Lemongrass Music", url: "https://lemongrassmusic.de/artists/Aleyum/" },
              { name: "Fokuz Recordings", url: "#" },
              { name: "Immersed Records", url: "#" },
              { name: "Offworld Recordings", url: "#" },
              { name: "Soul Deep Recordings", url: "#" },
            ].map((label) => (
              <a
                key={label.name}
                href={label.url}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-lg bg-card border border-border p-4 hover:border-primary/50 transition-colors text-center"
              >
                <span className="font-medium">{label.name}</span>
              </a>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

interface SkillBarProps {
  label: string;
  level: number;
}

function SkillBar({ label, level }: SkillBarProps) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span>{label}</span>
        <span className="text-muted-foreground">{level}%</span>
      </div>
      <div className="h-2 rounded-full bg-muted overflow-hidden">
        <div
          className="h-full rounded-full bg-primary transition-all"
          style={{ width: `${level}%` }}
        />
      </div>
    </div>
  );
}

interface ExperienceCardProps {
  title: string;
  company: string;
  period: string;
  description: string;
}

function ExperienceCard({ title, company, period, description }: ExperienceCardProps) {
  return (
    <div className="rounded-xl bg-card border border-border p-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-2">
        <h3 className="font-semibold text-lg">{title}</h3>
        <span className="text-sm text-muted-foreground">{period}</span>
      </div>
      <p className="text-primary mb-2">{company}</p>
      <p className="text-muted-foreground text-sm">{description}</p>
    </div>
  );
}
