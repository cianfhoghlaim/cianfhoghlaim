// /ga/subjects/mata — Mata BIEP v1 per-subject landing page (Irish mirror).
// Per openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/.

import { createFileRoute } from "@tanstack/react-router";
import { BIEPSubjectPage } from "../../../components/BIEPSubjectPage";
import { getBIEPSubject } from "../../../lib/bi-ep";

export const Route = createFileRoute("/ga/subjects/mata")({
  component: MataBIEPPage,
});

function MataBIEPPage() {
  const subject = getBIEPSubject("mathematics");
  if (!subject) {
    return <div>Ní bhfuarthas sonraí Mata.</div>;
  }
  return <BIEPSubjectPage subject={subject} language="ga" />;
}
