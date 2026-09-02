// /ga/subjects/ceimic — Ceimic BIEP v1 per-subject landing page (Irish mirror).
// Per openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/.

import { createFileRoute } from "@tanstack/react-router";
import { BIEPSubjectPage } from "../../../src/components/BIEPSubjectPage";
import { getBIEPSubject } from "../../../src/lib/bi-ep";

export const Route = createFileRoute("/lc/gaeilge/ga-ceimic")({
  component: CeimicBIEPPage,
});

function CeimicBIEPPage() {
  const subject = getBIEPSubject("chemistry");
  if (!subject) {
    return <div>Ní bhfuarthas sonraí Ceimic.</div>;
  }
  return <BIEPSubjectPage subject={subject} language="ga" />;
}
