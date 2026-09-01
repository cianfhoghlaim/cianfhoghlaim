/**
 * A2UI components barrel — re-exports the 11 canonical A2UI v0.9
 * components per the agentic-frontend-frameworks spec.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-a2ui-catalog-v1 change
 * (Phase 2 of the cianfhoghlaim-nua v6 era plan).
 *
 * The 11 components:
 *   - StudyPlanCard        (Phase 1, in oideachais/src/components/study-plan)
 *   - WeekTimeline         (Phase 2, this package)
 *   - MilestoneBadge       (Phase 2, this package)
 *   - ExamPaperCard        (Phase 2, this package)
 *   - MarksBreakdownTable  (Phase 2, this package)
 *   - KCWeightsBar         (Phase 2, this package)
 *   - StageOverview        (Phase 2, this package)
 *   - SubjectCard          (Phase 2, this package)
 *   - MarimoEmbed          (existing, oideachais)
 *   - CiPdfLibraryPanel    (existing, oideachais)
 *   - TranslationToggle    (existing, oideachais)
 *
 * Phase 2 ships the 7 NEW components in this package. The 3 existing
 * components (MarimoEmbed, CiPdfLibraryPanel, TranslationToggle) are
 * re-exported from the oideachais app for cross-package convenience;
 * a future openspec change will lift them into the a2ui package.
 */

export { WeekTimeline } from "./WeekTimeline";
export type { WeekTimelineWeek, WeekTimelineProps } from "./WeekTimeline";

export { MilestoneBadge } from "./MilestoneBadge";
export type {
  MilestoneAssessmentType,
  MilestoneBadgeItem,
  MilestoneBadgeProps,
} from "./MilestoneBadge";

export { ExamPaperCard, ExamPaperCardGrid } from "./ExamPaperCard";
export type { ExamPaperCardData, ExamPaperCardProps } from "./ExamPaperCard";

export { MarksBreakdownTable } from "./MarksBreakdownTable";
export type {
  MarksBreakdownTableRow,
  MarksBreakdownTableProps,
} from "./MarksBreakdownTable";

export { KCWeightsBar } from "./KCWeightsBar";
export type {
  KCCompetencySlug,
  KCWeightsBarItem,
  KCWeightsBarProps,
} from "./KCWeightsBar";

export { StageOverview, DEFAULT_BRITISH_ISLES_STAGES } from "./StageOverview";
export type {
  StageSlug,
  StageOverviewStage,
  StageOverviewProps,
} from "./StageOverview";

export { SubjectCard, SubjectCardGrid } from "./SubjectCard";
export type {
  SubjectStage,
  SubjectCardData,
  SubjectCardProps,
} from "./SubjectCard";
export { OralStudyPlayer } from "./OralStudyPlayer";
export type {
  OralStudySegmentData,
  OralStudyPlayerData,
  OralStudyPlayerProps,
} from "./OralStudyPlayer";
