// /ga/subjects/riomheolaiocht — Ríomheolaíocht BIEP v1 per-subject landing page (Irish mirror).
// Per openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/.

import { createFileRoute } from "@tanstack/react-router";
import { BIEPSubjectPage } from "../../../src/components/BIEPSubjectPage";
import { getBIEPSubject } from "../../../src/lib/bi-ep";

export const Route = createFileRoute("/lc/gaeilge/ga-riomheolaiocht")({
  component: RiomheolaiochtBIEPPage,
});

function RiomheolaiochtBIEPPage() {
  const subject = getBIEPSubject("computer_science");
  if (!subject) {
    return <div>Ní bhfuarthas sonraí Ríomheolaíochta.</div>;
  }
  return <BIEPSubjectPage subject={subject} language="ga" />;
}
