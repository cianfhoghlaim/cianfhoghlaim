/**
 * Generative UI Components Index.
 *
 * AG-UI components for dynamic rendering from agent events.
 */

// Registry and renderer
export {
  componentRegistry,
  isRegisteredComponent,
  getComponent,
  useGenerativeUI,
  SlotRenderer,
  GenerativeUILayout,
  type SlotType,
  type GenerativeUIEvent,
  type RenderedComponent,
  type UseGenerativeUIOptions,
  type UseGenerativeUIReturn,
  type SlotRendererProps,
  type GenerativeUILayoutProps,
} from "./ComponentRegistry";

// Individual components
export { CurriculumCard, type CurriculumCardProps } from "./CurriculumCard";
export { PronunciationButton, type PronunciationButtonProps, type IrishDialect } from "./PronunciationButton";
export { AssessmentWidget, type AssessmentWidgetProps, type Question, type QuestionOption, type QuestionType } from "./AssessmentWidget";
export { ProgressChart, type ProgressChartProps, type ProgressItem } from "./ProgressChart";
