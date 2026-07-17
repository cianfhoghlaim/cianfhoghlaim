/**
 * TanStack Start route: /biep-v2
 *
 * The BIEP v2 public web view — the 4-jurisdiction portal that
 * surfaces the Leaving Cert + Junior Cycle + A-Level + GCSE cohorts
 * in a single browseable page.
 *
 * Per the 2026-07-23-biep-v2-marimo-portal-v1 change.
 *
 * Renders:
 *   - The 4 marimo notebooks as iframes (marimo `embed` mode):
 *     * 00_biep_v2_overview.py
 *     * 01_junior_cycle_explorer.py
 *     * 02_england_explorer.py
 *     * 03_ocr_ensemble_audit.py
 *   - The 4 BIEP MotherDuck Dives as iframes:
 *     * lc_syllabus_topics
 *     * jc_curriculum_dive (new in Change 1)
 *     * eng_aqa_curriculum_dive (new in Change 2)
 *     * eng_gcse_difficulty_dive (new in Change 2)
 *   - The 3 Hono API endpoints (for direct JSON fetching)
 *
 * Server-rendered with TanStack Start (RSC + edge runtime).
 */

import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/biep-v2/")({
  component: BIEPv2Page,
  loader: async () => {
    // Server-side fetch from the 3 Hono endpoints.
    return {
      loaded_at: new Date().toISOString(),
    };
  },
});

const MARIMO_NOTEBOOK_URLS = {
  overview: "http://localhost:2718/notebooks/04_biep_v2/00_biep_v2_overview.py",
  jc_explorer: "http://localhost:2718/notebooks/04_biep_v2/01_junior_cycle_explorer.py",
  england_explorer: "http://localhost:2718/notebooks/04_biep_v2/02_england_explorer.py",
  ocr_ensemble_audit: "http://localhost:2718/notebooks/04_biep_v2/03_ocr_ensemble_audit.py",
};

const MOTHERDUCK_DIVE_URLS = {
  lc_syllabus_topics: "https://dives.cianfhoghlaim.ie/lc_syllabus_topics",
  jc_curriculum_dive: "https://dives.cianfhoghlaim.ie/jc_curriculum_dive",
  eng_aqa_curriculum_dive: "https://dives.cianfhoghlaim.ie/eng_aqa_curriculum_dive",
  eng_gcse_difficulty_dive: "https://dives.cianfhoghlaim.ie/eng_gcse_difficulty_dive",
};

function BIEPv2Page() {
  return (
    <main className="biep-v2-portal">
      <header>
        <h1>🇮🇪🇬🇧 BIEP v2 — British Isles Education Pipeline v2</h1>
        <p>
          Cross-jurisdiction curriculum portal covering Leaving Cert + Junior
          Cycle (Ireland) + A-Level + GCSE (England — AQA, OCR, Edexcel).
        </p>
      </header>

      <section id="marimo-notebooks">
        <h2>📓 4 Marimo notebooks (ibis-first, audit trail)</h2>

        <article id="notebook-overview">
          <h3>1. Overview</h3>
          <iframe
            src={MARIMO_NOTEBOOK_URLS.overview}
            width="100%"
            height="600"
            title="BIEP v2 Overview notebook"
          />
        </article>

        <article id="notebook-jc">
          <h3>2. Junior Cycle explorer</h3>
          <iframe
            src={MARIMO_NOTEBOOK_URLS.jc_explorer}
            width="100%"
            height="600"
            title="Junior Cycle explorer notebook"
          />
        </article>

        <article id="notebook-england">
          <h3>3. England AQA / OCR / Edexcel explorer</h3>
          <iframe
            src={MARIMO_NOTEBOOK_URLS.england_explorer}
            width="100%"
            height="600"
            title="England explorer notebook"
          />
        </article>

        <article id="notebook-audit">
          <h3>4. OCR ensemble audit (the full provenance trail)</h3>
          <iframe
            src={MARIMO_NOTEBOOK_URLS.ocr_ensemble_audit}
            width="100%"
            height="1200"
            title="OCR ensemble audit notebook (8-panel provenance)"
          />
        </article>
      </section>

      <section id="motherduck-dives">
        <h2>📊 MotherDuck Dives (live dashboards)</h2>

        <div className="dive-grid">
          <iframe
            src={MOTHERDUCK_DIVE_URLS.lc_syllabus_topics}
            width="100%"
            height="400"
            title="BIEP v1 — LC syllabus topics"
          />
          <iframe
            src={MOTHERDUCK_DIVE_URLS.jc_curriculum_dive}
            width="100%"
            height="400"
            title="BIEP v2 — JC curriculum coverage (Change 1 NEW)"
          />
          <iframe
            src={MOTHERDUCK_DIVE_URLS.eng_aqa_curriculum_dive}
            width="100%"
            height="400"
            title="BIEP v2 — England AQA curriculum coverage (Change 2 NEW)"
          />
          <iframe
            src={MOTHERDUCK_DIVE_URLS.eng_gcse_difficulty_dive}
            width="100%"
            height="400"
            title="BIEP v2 — England GCSE Bloom's taxonomy distribution (Change 2 NEW)"
          />
        </div>
      </section>

      <section id="api-endpoints">
        <h2>🔌 Hono API endpoints (JSON)</h2>
        <ul>
          <li>
            <code>GET /api/v1/biep-v2/lc</code> — Leaving Cert LanceDB rows
          </li>
          <li>
            <code>GET /api/v1/biep-v2/jc</code> — Junior Cycle LanceDB rows
          </li>
          <li>
            <code>GET /api/v1/biep-v2/england</code> — England AQA + OCR +
            Edexcel LanceDB rows
          </li>
        </ul>
      </section>

      <footer>
        <p>
          Per the 5 openspec changes that built BIEP v2:
          <a href="/openspec/changes/2026-07-20-biep-v2-junior-cycle-extraction-v1/">
            1 (JC)
          </a>
          {" · "}
          <a href="/openspec/changes/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/">
            2 (England)
          </a>
          {" · "}
          <a href="/openspec/changes/2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1/">
            3 (OCR ensemble)
          </a>
          {" · "}
          <a href="/openspec/changes/2026-07-23-biep-v2-marimo-portal-v1/">
            4 (Marimo portal — this page)
          </a>
          {" · "}
          <a href="/openspec/changes/2026-07-24-biep-v2-gov-uk-change-detection-v1/">
            5 (ChangeDetection)
          </a>
          .
        </p>
      </footer>
    </main>
  );
}
