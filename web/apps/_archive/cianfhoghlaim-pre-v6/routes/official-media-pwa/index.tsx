/**
 * TanStack Start route: /official-media-pwa
 * Per the 2026-08-05-official-media-biiep-v3-coverage-v1 change
 * (closes GitHub issue #48 — side-loadable PWA / iOS / Android app).
 */
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/official-media-pwa/")({
  component: OfficialMediaPwaPage,
  loader: async () => {
    return { manifest_url: "/manifest.webmanifest" };
  },
});

function OfficialMediaPwaPage() {
  const { manifest_url } = Route.useLoaderData();
  return (
    <main className="official-media-pwa">
      <h1>📱 Official Media PWA</h1>
      <p>Side-loadable PWA + iOS + Android app for the official-media pipeline.</p>
      <link rel="manifest" href={manifest_url} />
      <p>
        <a href="/manifest.webmanifest" download>Download manifest</a>
        {" · "}
        <a href="/official-media-pwa/install">Install instructions</a>
      </p>
    </main>
  );
}
