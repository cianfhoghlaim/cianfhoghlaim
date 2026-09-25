// /en/subjects/mathematics — Mathematics BIEP v1 per-subject landing page.
// Per openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/
// Renders the BIEP subject card + 5 visualizations + live marimo embed +
// 5×8 mastery matrix + the bilingual EN+GA mirror link.

import { createFileRoute } from "@tanstack/react-router";
import { BIEPSubjectPage } from "../../../components/BIEPSubjectPage";
import { getBIEPSubject, isBIEPSubject } from "../../../lib/bi-ep";

export const Route = createFileRoute("/en/subjects/mathematics")({
  component: MathematicsBIEPPage,
});

function MathematicsBIEPPage() {
  const subject = getBIEPSubject("mathematics");
  if (!subject || !isBIEPSubject("mathematics")) {
    return <div>Mathematics subject metadata not found.</div>;
  }
  return <BIEPSubjectPage subject={subject} language="en" />;
}
