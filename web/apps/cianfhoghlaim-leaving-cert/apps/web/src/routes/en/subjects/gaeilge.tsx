// /en/subjects/gaeilge — Gaeilge BIEP v1 per-subject landing page.
// Per openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/

import { createFileRoute } from "@tanstack/react-router";
import { BIEPSubjectPage } from "../../../components/BIEPSubjectPage";
import { getBIEPSubject } from "../../../lib/bi-ep";

export const Route = createFileRoute("/en/subjects/gaeilge")({
  component: GaeilgeBIEPPage,
});

function GaeilgeBIEPPage() {
  const subject = getBIEPSubject("gaeilge");
  if (!subject) {
    return <div>Gaeilge subject metadata not found.</div>;
  }
  return <BIEPSubjectPage subject={subject} language="en" />;
}
