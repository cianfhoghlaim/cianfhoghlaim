import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/admin/analytics/")({
  component: AnalyticsIndex,
});

const DIVE_URLS = {
  music: "https://app.motherduck.com/dives/music_md",
  teaching: "https://app.motherduck.com/dives/teaching_md",
  cv: "https://app.motherduck.com/dives/cv_md",
  research: "https://app.motherduck.com/dives/research_md",
};

function AnalyticsIndex() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Analytics & Notebooks</h1>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        {Object.entries(DIVE_URLS).map(([streamId, url]) => (
          <div key={streamId} className="rounded-xl bg-card border border-border p-6">
            <h2 className="text-lg font-semibold mb-2 capitalize">{streamId}</h2>
            <p className="text-muted-foreground text-sm mb-4">
              SQL-first analytics dashboard for the {streamId} stream. Explore music catalogues,
              GitHub repos, CV entries, and pipeline metrics.
            </p>
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity"
            >
              Open Dive
            </a>
          </div>
        ))}
      </div>

      <div className="rounded-xl bg-card border border-border p-6">
        <h2 className="text-lg font-semibold mb-2">Marimo Notebooks</h2>
        <p className="text-muted-foreground text-sm mb-4">
          Reactive Python notebooks for exploratory analysis. Run locally with:
        </p>
        <pre className="bg-muted p-3 rounded text-sm mb-4">
          {`marimo run notebooks/streams/music/music_analytics.py
marimo run notebooks/streams/teaching/teaching_analytics.py`}
        </pre>
        <p className="text-muted-foreground text-xs">
          The public{' '}
          <code className="bg-muted px-1 rounded">/data</code>{' '}
          route per stream renders WASM-exported static versions
          (built via{' '}
          <code className="bg-muted px-1 rounded">bun run notebook:wasm</code>).
        </p>
      </div>
    </div>
  );
}
