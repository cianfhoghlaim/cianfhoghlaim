/**
 * Generative UI Component for Curriculum Visualization.
 *
 * Agent-rendered components for:
 * - Learning outcome hierarchies (Subject → Strand → Unit → LO)
 * - Subject navigation trees
 * - Examiner insight summaries
 * - Document relationship graphs
 */

import { useState, useCallback, useMemo } from "react";
import {
  ChevronRight,
  ChevronDown,
  BookOpen,
  FileText,
  Target,
  Layers,
  GraduationCap,
  Search,
  ExternalLink,
  Info,
  TrendingUp,
  AlertCircle,
  Check,
  Lightbulb,
} from "lucide-react";

// ============================================================================
// Types
// ============================================================================

export interface LearningOutcome {
  code: string;
  descriptionEn: string;
  descriptionGa?: string;
  difficultyLevel?: "foundation" | "ordinary" | "higher";
  curriculumYear?: number;
  keySkills?: string[];
}

export interface StrandUnit {
  id: string;
  nameEn: string;
  nameGa?: string;
  sequence: number;
  outcomes: LearningOutcome[];
}

export interface Strand {
  id: string;
  nameEn: string;
  nameGa?: string;
  sequence: number;
  units: StrandUnit[];
}

export interface Subject {
  code: string;
  nameEn: string;
  nameGa?: string;
  educationLevel: "primary" | "junior_cycle" | "senior_cycle";
  strands: Strand[];
}

export interface ExaminerInsight {
  id: string;
  year: number;
  outcomeCode?: string;
  insightType: "strength" | "weakness" | "recommendation" | "common_error";
  content: string;
  frequency?: "common" | "occasional" | "rare";
}

export interface DocumentRelation {
  documentId: string;
  documentTitle: string;
  documentType: string;
  relevanceScore: number;
  section?: string;
}

// ============================================================================
// Curriculum Hierarchy Tree
// ============================================================================

export interface CurriculumTreeProps {
  subject: Subject;
  selectedOutcome?: string;
  onSelectOutcome?: (code: string) => void;
  showIrish?: boolean;
  expandedByDefault?: boolean;
}

export function CurriculumTree({
  subject,
  selectedOutcome,
  onSelectOutcome,
  showIrish = false,
  expandedByDefault = false,
}: CurriculumTreeProps) {
  const [expandedStrands, setExpandedStrands] = useState<Set<string>>(
    expandedByDefault ? new Set(subject.strands.map((s) => s.id)) : new Set()
  );
  const [expandedUnits, setExpandedUnits] = useState<Set<string>>(
    expandedByDefault
      ? new Set(subject.strands.flatMap((s) => s.units.map((u) => u.id)))
      : new Set()
  );

  const toggleStrand = useCallback((strandId: string) => {
    setExpandedStrands((prev) => {
      const next = new Set(prev);
      if (next.has(strandId)) {
        next.delete(strandId);
      } else {
        next.add(strandId);
      }
      return next;
    });
  }, []);

  const toggleUnit = useCallback((unitId: string) => {
    setExpandedUnits((prev) => {
      const next = new Set(prev);
      if (next.has(unitId)) {
        next.delete(unitId);
      } else {
        next.add(unitId);
      }
      return next;
    });
  }, []);

  const levelLabels: Record<string, { label: string; color: string }> = {
    primary: { label: "Primary", color: "bg-yellow-100 text-yellow-800" },
    junior_cycle: { label: "Junior Cycle", color: "bg-blue-100 text-blue-800" },
    senior_cycle: { label: "Senior Cycle", color: "bg-purple-100 text-purple-800" },
  };

  const levelInfo = levelLabels[subject.educationLevel] || levelLabels.primary;

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200">
      {/* Subject Header */}
      <div className="px-4 py-3 border-b bg-gray-50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <GraduationCap className="h-5 w-5 text-blue-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-medium text-gray-900">
              {showIrish && subject.nameGa ? subject.nameGa : subject.nameEn}
            </h3>
            {showIrish && subject.nameGa && (
              <p className="text-sm text-gray-500">{subject.nameEn}</p>
            )}
          </div>
          <span className={`text-xs px-2 py-1 rounded-full ${levelInfo.color}`}>
            {levelInfo.label}
          </span>
        </div>
      </div>

      {/* Strands */}
      <div className="divide-y">
        {subject.strands
          .sort((a, b) => a.sequence - b.sequence)
          .map((strand) => (
            <div key={strand.id}>
              {/* Strand Row */}
              <button
                onClick={() => toggleStrand(strand.id)}
                className="w-full px-4 py-3 flex items-center gap-3 hover:bg-gray-50 transition-colors text-left"
              >
                {expandedStrands.has(strand.id) ? (
                  <ChevronDown className="h-4 w-4 text-gray-400 flex-shrink-0" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-gray-400 flex-shrink-0" />
                )}
                <Layers className="h-4 w-4 text-orange-500 flex-shrink-0" />
                <span className="font-medium text-gray-800">
                  {showIrish && strand.nameGa ? strand.nameGa : strand.nameEn}
                </span>
                <span className="text-xs text-gray-400 ml-auto">
                  {strand.units.reduce((acc, u) => acc + u.outcomes.length, 0)} outcomes
                </span>
              </button>

              {/* Strand Units */}
              {expandedStrands.has(strand.id) && (
                <div className="pl-8 border-l-2 border-orange-100 ml-6">
                  {strand.units
                    .sort((a, b) => a.sequence - b.sequence)
                    .map((unit) => (
                      <div key={unit.id}>
                        {/* Unit Row */}
                        <button
                          onClick={() => toggleUnit(unit.id)}
                          className="w-full px-4 py-2 flex items-center gap-3 hover:bg-gray-50 transition-colors text-left"
                        >
                          {expandedUnits.has(unit.id) ? (
                            <ChevronDown className="h-3 w-3 text-gray-400 flex-shrink-0" />
                          ) : (
                            <ChevronRight className="h-3 w-3 text-gray-400 flex-shrink-0" />
                          )}
                          <BookOpen className="h-4 w-4 text-green-500 flex-shrink-0" />
                          <span className="text-sm text-gray-700">
                            {showIrish && unit.nameGa ? unit.nameGa : unit.nameEn}
                          </span>
                          <span className="text-xs text-gray-400 ml-auto">
                            {unit.outcomes.length} LOs
                          </span>
                        </button>

                        {/* Learning Outcomes */}
                        {expandedUnits.has(unit.id) && (
                          <div className="pl-8 py-1">
                            {unit.outcomes.map((outcome) => (
                              <button
                                key={outcome.code}
                                onClick={() => onSelectOutcome?.(outcome.code)}
                                className={`w-full px-3 py-2 flex items-start gap-2 rounded-lg transition-colors text-left ${
                                  selectedOutcome === outcome.code
                                    ? "bg-blue-50 border border-blue-200"
                                    : "hover:bg-gray-50"
                                }`}
                              >
                                <Target className="h-4 w-4 text-blue-500 flex-shrink-0 mt-0.5" />
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2">
                                    <span className="text-xs font-mono text-gray-500">
                                      {outcome.code}
                                    </span>
                                    {outcome.difficultyLevel && (
                                      <DifficultyBadge level={outcome.difficultyLevel} />
                                    )}
                                  </div>
                                  <p className="text-sm text-gray-700 mt-0.5 line-clamp-2">
                                    {showIrish && outcome.descriptionGa
                                      ? outcome.descriptionGa
                                      : outcome.descriptionEn}
                                  </p>
                                </div>
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                </div>
              )}
            </div>
          ))}
      </div>
    </div>
  );
}

// ============================================================================
// Learning Outcome Detail Card
// ============================================================================

export interface LearningOutcomeDetailProps {
  outcome: LearningOutcome;
  insights?: ExaminerInsight[];
  relatedDocuments?: DocumentRelation[];
  showIrish?: boolean;
  onViewDocument?: (documentId: string) => void;
}

export function LearningOutcomeDetail({
  outcome,
  insights = [],
  relatedDocuments = [],
  showIrish = false,
  onViewDocument,
}: LearningOutcomeDetailProps) {
  const [activeTab, setActiveTab] = useState<"overview" | "insights" | "documents">(
    "overview"
  );

  const insightsByType = useMemo(() => {
    return insights.reduce((acc, insight) => {
      if (!acc[insight.insightType]) {
        acc[insight.insightType] = [];
      }
      acc[insight.insightType].push(insight);
      return acc;
    }, {} as Record<string, ExaminerInsight[]>);
  }, [insights]);

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <Target className="h-5 w-5 text-blue-600" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm text-gray-600">{outcome.code}</span>
              {outcome.difficultyLevel && (
                <DifficultyBadge level={outcome.difficultyLevel} />
              )}
              {outcome.curriculumYear && (
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                  Year {outcome.curriculumYear}
                </span>
              )}
            </div>
            <p className="mt-1 text-gray-800">
              {showIrish && outcome.descriptionGa
                ? outcome.descriptionGa
                : outcome.descriptionEn}
            </p>
            {showIrish && outcome.descriptionGa && (
              <p className="mt-1 text-sm text-gray-500">{outcome.descriptionEn}</p>
            )}
          </div>
        </div>

        {outcome.keySkills && outcome.keySkills.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {outcome.keySkills.map((skill) => (
              <span
                key={skill}
                className="text-xs bg-white border border-gray-200 text-gray-600 px-2 py-0.5 rounded"
              >
                {skill}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b">
        <div className="flex">
          {[
            { id: "overview" as const, label: "Overview", icon: Info },
            { id: "insights" as const, label: `Insights (${insights.length})`, icon: Lightbulb },
            { id: "documents" as const, label: `Documents (${relatedDocuments.length})`, icon: FileText },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-4">
        {activeTab === "overview" && (
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Description</h4>
              <p className="text-gray-600">{outcome.descriptionEn}</p>
            </div>

            {outcome.keySkills && outcome.keySkills.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Key Skills</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                  {outcome.keySkills.map((skill) => (
                    <li key={skill}>{skill}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {activeTab === "insights" && (
          <div className="space-y-4">
            {insights.length === 0 ? (
              <p className="text-gray-500 text-sm text-center py-4">
                No examiner insights available for this outcome.
              </p>
            ) : (
              <>
                {insightsByType.strength && (
                  <InsightSection
                    type="strength"
                    insights={insightsByType.strength}
                  />
                )}
                {insightsByType.weakness && (
                  <InsightSection
                    type="weakness"
                    insights={insightsByType.weakness}
                  />
                )}
                {insightsByType.common_error && (
                  <InsightSection
                    type="common_error"
                    insights={insightsByType.common_error}
                  />
                )}
                {insightsByType.recommendation && (
                  <InsightSection
                    type="recommendation"
                    insights={insightsByType.recommendation}
                  />
                )}
              </>
            )}
          </div>
        )}

        {activeTab === "documents" && (
          <div className="space-y-2">
            {relatedDocuments.length === 0 ? (
              <p className="text-gray-500 text-sm text-center py-4">
                No related documents found.
              </p>
            ) : (
              relatedDocuments
                .sort((a, b) => b.relevanceScore - a.relevanceScore)
                .map((doc) => (
                  <button
                    key={doc.documentId}
                    onClick={() => onViewDocument?.(doc.documentId)}
                    className="w-full p-3 flex items-start gap-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors text-left"
                  >
                    <FileText className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-800 truncate">
                          {doc.documentTitle}
                        </span>
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                          {doc.documentType.replace(/_/g, " ")}
                        </span>
                      </div>
                      {doc.section && (
                        <p className="text-xs text-gray-500 mt-0.5">{doc.section}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500">
                        {(doc.relevanceScore * 100).toFixed(0)}%
                      </span>
                      <ExternalLink className="h-4 w-4 text-gray-400" />
                    </div>
                  </button>
                ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// Helper Components
// ============================================================================

function DifficultyBadge({ level }: { level: "foundation" | "ordinary" | "higher" }) {
  const config = {
    foundation: { label: "Foundation", color: "bg-green-100 text-green-800" },
    ordinary: { label: "Ordinary", color: "bg-blue-100 text-blue-800" },
    higher: { label: "Higher", color: "bg-purple-100 text-purple-800" },
  };

  const info = config[level];
  return (
    <span className={`text-xs px-2 py-0.5 rounded ${info.color}`}>{info.label}</span>
  );
}

function InsightSection({
  type,
  insights,
}: {
  type: ExaminerInsight["insightType"];
  insights: ExaminerInsight[];
}) {
  const config = {
    strength: {
      label: "Strengths",
      icon: TrendingUp,
      color: "text-green-600",
      bgColor: "bg-green-50",
      borderColor: "border-green-200",
    },
    weakness: {
      label: "Areas for Improvement",
      icon: AlertCircle,
      color: "text-orange-600",
      bgColor: "bg-orange-50",
      borderColor: "border-orange-200",
    },
    common_error: {
      label: "Common Errors",
      icon: AlertCircle,
      color: "text-red-600",
      bgColor: "bg-red-50",
      borderColor: "border-red-200",
    },
    recommendation: {
      label: "Recommendations",
      icon: Lightbulb,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
      borderColor: "border-blue-200",
    },
  };

  const info = config[type];
  const IconComponent = info.icon;

  return (
    <div className={`rounded-lg p-3 ${info.bgColor} border ${info.borderColor}`}>
      <div className={`flex items-center gap-2 mb-2 ${info.color}`}>
        <IconComponent className="h-4 w-4" />
        <span className="font-medium text-sm">{info.label}</span>
      </div>
      <ul className="space-y-2">
        {insights.map((insight) => (
          <li key={insight.id} className="text-sm text-gray-700 flex items-start gap-2">
            <Check className="h-3 w-3 mt-1 flex-shrink-0 text-gray-400" />
            <span>{insight.content}</span>
            {insight.year && (
              <span className="text-xs text-gray-400 ml-auto">({insight.year})</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

// ============================================================================
// Compact Subject Navigation
// ============================================================================

export interface SubjectNavigationProps {
  subjects: Pick<Subject, "code" | "nameEn" | "nameGa" | "educationLevel">[];
  selectedSubject?: string;
  onSelectSubject: (code: string) => void;
  showIrish?: boolean;
}

export function SubjectNavigation({
  subjects,
  selectedSubject,
  onSelectSubject,
  showIrish = false,
}: SubjectNavigationProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredSubjects = useMemo(() => {
    if (!searchQuery) return subjects;
    const query = searchQuery.toLowerCase();
    return subjects.filter(
      (s) =>
        s.nameEn.toLowerCase().includes(query) ||
        s.nameGa?.toLowerCase().includes(query) ||
        s.code.toLowerCase().includes(query)
    );
  }, [subjects, searchQuery]);

  const groupedSubjects = useMemo(() => {
    return filteredSubjects.reduce((acc, subject) => {
      const level = subject.educationLevel;
      if (!acc[level]) acc[level] = [];
      acc[level].push(subject);
      return acc;
    }, {} as Record<string, typeof subjects>);
  }, [filteredSubjects]);

  const levelOrder = ["primary", "junior_cycle", "senior_cycle"];
  const levelLabels: Record<string, string> = {
    primary: "Primary",
    junior_cycle: "Junior Cycle",
    senior_cycle: "Senior Cycle",
  };

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
      {/* Search */}
      <div className="p-3 border-b">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search subjects..."
            className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Subject List */}
      <div className="max-h-96 overflow-y-auto">
        {levelOrder.map((level) => {
          const levelSubjects = groupedSubjects[level];
          if (!levelSubjects || levelSubjects.length === 0) return null;

          return (
            <div key={level}>
              <div className="px-3 py-2 bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wider sticky top-0">
                {levelLabels[level]}
              </div>
              <div className="divide-y">
                {levelSubjects.map((subject) => (
                  <button
                    key={subject.code}
                    onClick={() => onSelectSubject(subject.code)}
                    className={`w-full px-3 py-2 flex items-center gap-3 text-left transition-colors ${
                      selectedSubject === subject.code
                        ? "bg-blue-50 border-l-2 border-blue-500"
                        : "hover:bg-gray-50"
                    }`}
                  >
                    <BookOpen className="h-4 w-4 text-gray-400 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <span className="text-sm font-medium text-gray-800 block truncate">
                        {showIrish && subject.nameGa ? subject.nameGa : subject.nameEn}
                      </span>
                      {showIrish && subject.nameGa && (
                        <span className="text-xs text-gray-500 block truncate">
                          {subject.nameEn}
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-gray-400 font-mono">{subject.code}</span>
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default CurriculumTree;
