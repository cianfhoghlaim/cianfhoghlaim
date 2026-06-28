/**
 * MotherDuck Dive embed for Leaving Certificate per-subject analysis.
 *
 * Embeds an interactive MotherDuck Dive iframe that shows the topic frequency
 * analysis for the given subject. The Dive is a pre-built SQL component that
 * queries the `leaving_cert.{subject}_topic_frequency` table.
 *
 * In dev mode (MOTHERDUCK_ENABLED=false), shows a placeholder with the
 * subject's seeded data instead.
 */

"use client";

interface MotherDuckDiveProps {
  subject: string;
  height?: number;
}

export function MotherDuckDive({ subject, height = 500 }: MotherDuckDiveProps) {
  const motherduckEnabled = typeof window !== "undefined"
    ? new URLSearchParams(window.location.search).get("md") !== "false"
    : true;

  if (!motherduckEnabled) {
    return (
      <div className="border border-slate-800 rounded-lg p-4 text-center text-slate-400">
        <p>MotherDuck Dive disabled (dev mode).</p>
        <p className="text-xs mt-1">
          Add <code>?md=true</code> to enable.
        </p>
      </div>
    );
  }

  // MotherDuck Dive embed URL — the Dive ID is per-subject,
  // e.g. leaving_cert_mathematics_topic_frequency
  const diveUrl = `https://app.motherduck.com/dive/${subject}_topic_frequency?token=${encodeURIComponent(import.meta.env?.VITE_MOTHERDUCK_TOKEN ?? "")}`;

  return (
    <div className="border border-slate-800 rounded-lg overflow-hidden">
      <iframe
        src={diveUrl}
        width="100%"
        height={height}
        title={`${subject} topic frequency — MotherDuck Dive`}
        className="bg-white"
        loading="lazy"
      />
    </div>
  );
}
