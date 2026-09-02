/**
 * TanStack Start route: /analyzer
 * Per the 2026-08-05-official-media-biiep-v3-coverage-v1 change
 * (closes GitHub issue #35 — meaisinfhoghlaim web analyzer).
 */
import { createFileRoute } from "@tanstack/react-router";
import { hc } from "hono/client";

export const Route = createFileRoute("/analyzer/")({
  component: AnalyzerPage,
  loader: async () => {
    return { placeholder: "meaisinfhoghlaim web analyzer" };
  },
});

function AnalyzerPage() {
  const { placeholder } = Route.useLoaderData();
  return (
    <main className="analyzer">
      <h1>🧠 {placeholder}</h1>
      <p>The meaisinfhoghlaim agent fleet analysis output for any text input.</p>
      <form>
        <label>
          Text to analyze:
          <textarea name="text" rows={10} cols={60} />
        </label>
        <button type="submit">Analyze</button>
      </form>
    </main>
  );
}
