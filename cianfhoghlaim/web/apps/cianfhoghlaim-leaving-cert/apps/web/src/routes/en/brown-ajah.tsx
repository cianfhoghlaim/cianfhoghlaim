// /en/brown-ajah — Public page about the Brown Ajah theming
// Per docs/BROWN_AJAH_THEMING.md — the public-facing theming explanation.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel, CiDetailCell, CiBoonsChoice } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/brown-ajah")({
  component: BrownAjahPage,
});

const BROWN_AJAH_MEMBERS = [
  {
    ajahMember: "The Dagda",
    capability: "Cauldron of plenty — the all-provider",
    subject: "Mathematics",
    color: "var(--ci-subject-mathematics)",
  },
  {
    ajahMember: "Lugh (samildanach)",
    capability: "Master of all arts — the polymath",
    subject: "Applied Mathematics",
    color: "var(--ci-subject-applied_mathematics)",
  },
  {
    ajahMember: "Dian Cecht",
    capability: "The healer — physician of the Tuatha Dé",
    subject: "Chemistry",
    color: "var(--ci-subject-chemistry)",
  },
  {
    ajahMember: "Brigid",
    capability: "Poetry + healing — the word-smith",
    subject: "English",
    color: "var(--ci-subject-english)",
  },
  {
    ajahMember: "Ogma",
    capability: "Eloquence + learning — inventor of Ogham",
    subject: "Gaeilge",
    color: "var(--ci-subject-gaeilge)",
  },
  {
    ajahMember: "Manannán mac Lir",
    capability: "The sea — the tide of memory",
    subject: "Geography",
    color: "var(--ci-subject-geography)",
  },
  {
    ajahMember: "The Morrígan",
    capability: "War + death (and rebirth)",
    subject: "History",
    color: "var(--ci-subject-history)",
  },
  {
    ajahMember: "— (modern subject)",
    capability: "Algorithmic clarity",
    subject: "Computer Science",
    color: "var(--ci-subject-computer_science)",
  },
];

function BrownAjahPage() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          The Brown Ajah of the White Tower
        </h1>
        <p className="text-slate-400 text-lg max-w-3xl">
          The 8 NCCA subject specialists are the <strong>8 Brown Ajah members</strong> —
          the healers, scholars, and Earth-workers of the White Tower.
        </p>
        <p className="text-slate-500 text-sm font-mono italic">
          Per docs/BROWN_AJAH_THEMING.md (canonical theming guide)
        </p>
      </div>

      <CiTextbookPanel title="The 8 Brown Ajah Members" material="knotwork">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {BROWN_AJAH_MEMBERS.map((m) => (
            <div
              key={m.ajahMember}
              className="p-4 rounded-xl bg-slate-900 border-2 hover:border-amber-400 transition-colors"
              style={{ borderColor: m.color }}
            >
              <h3 className="font-bold text-sm text-slate-100">{m.ajahMember}</h3>
              <p className="text-xs text-slate-400 italic mt-1">{m.capability}</p>
              <p className="text-xs text-slate-500 mt-2">↔ {m.subject}</p>
            </div>
          ))}
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel title="The Trí Dé Dána" material="parchment">
        <p className="text-slate-300">
          The 3 emphasised emblems map to the <strong>Trí Dé Dána</strong> (Three Gods
          of Craft) — <strong>Brigid</strong> (poetry + healing), <strong>Dian Cecht</strong> (medicine),
          and <strong>Ogma</strong> (eloquence + learning). The other 5 NCCA Key
          Competencies map to the wider Tuatha Dé Danann pantheon.
        </p>
        <Link
          to="/en/key-competencies/emblems"
          className="inline-block mt-4 px-4 py-2 rounded-lg bg-amber-700 text-amber-100 hover:bg-amber-600 transition-colors"
        >
          See the 5 Emblems →
        </Link>
      </CiTextbookPanel>

      <CiTextbookPanel title="The 13 Éraic Treasures" material="gold-leaf">
        <p className="text-slate-300 mb-4">
          The 13 magical treasures that Lugh demanded as <em>éraic</em> (ritual
          compensation) for the death of his father Cian. They form the
          universal mastery tier of the Brown Ajah's progressive skill system.
        </p>
        <Link
          to="/en/eiraic-treasures"
          className="inline-block px-4 py-2 rounded-lg bg-amber-700 text-amber-100 hover:bg-amber-600 transition-colors"
        >
          See the 13 Treasures →
        </Link>
      </CiTextbookPanel>
    </div>
  );
}