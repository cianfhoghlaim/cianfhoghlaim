/**
 * TeacherDashboard - Classroom Component.
 *
 * Dashboard for teachers to monitor classroom activity,
 * student progress, and manage lessons.
 */

import { useState, useMemo, useCallback } from "react";
import {
  Users,
  BookOpen,
  AlertTriangle,
  Trophy,
  MessageSquare,
  Play,
  Pause,
  Settings,
  Eye,
  EyeOff,
  Share2,
  BarChart3,
  Clock,
  Sparkles,
} from "lucide-react";
import {
  useTeacherDashboard,
  type Lesson,
  type Annotation,
} from "../../hooks/useClassroomState";
import { ClassProgress } from "./StudentProgress";

// ============================================================================
// Types
// ============================================================================

export interface TeacherDashboardProps {
  /** Classroom ID */
  classroomId?: string;
  /** Teacher's user ID */
  userId: string;
  /** Available lessons to select from */
  availableLessons?: Lesson[];
  /** Custom class name */
  className?: string;
}

interface QuickActionProps {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  onClick: () => void;
  variant?: "primary" | "secondary" | "danger";
  disabled?: boolean;
}

// ============================================================================
// TeacherDashboard Component
// ============================================================================

export function TeacherDashboard({
  classroomId = "default",
  userId,
  availableLessons = [],
  className = "",
}: TeacherDashboardProps) {
  const {
    state,
    isConnected,
    connectionError,
    activeStudents,
    classProgress,
    strugglingStudents,
    topPerformers,
    sharedAnnotations,
    setCurrentLesson,
    updateSharedContent,
    updateSettings,
  } = useTeacherDashboard({ classroomId, userId });

  const [showSettings, setShowSettings] = useState(false);
  const [selectedTab, setSelectedTab] = useState<
    "overview" | "students" | "annotations" | "settings"
  >("overview");

  // Handle lesson selection
  const handleLessonSelect = useCallback(
    (lessonId: string) => {
      const lesson = availableLessons.find((l) => l.id === lessonId);
      setCurrentLesson(lesson || null);
    },
    [availableLessons, setCurrentLesson]
  );

  // Handle pause/resume
  const handleTogglePause = useCallback(() => {
    updateSharedContent({
      teacherNotes: state.sharedContent.teacherNotes
        ? undefined
        : "Lesson paused",
    });
  }, [updateSharedContent, state.sharedContent]);

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">
                Teacher Dashboard
              </h1>
              <p className="text-sm text-gray-500">
                {state.currentLesson ? (
                  <>
                    <span className="text-green-600 font-medium">Active:</span>{" "}
                    {state.currentLesson.title}
                  </>
                ) : (
                  "No active lesson"
                )}
              </p>
            </div>
          </div>

          {/* Connection Status */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <span
                className={`w-2 h-2 rounded-full ${
                  isConnected ? "bg-green-500" : "bg-red-500"
                }`}
              />
              <span className="text-gray-600">
                {isConnected ? "Connected" : connectionError || "Disconnected"}
              </span>
            </div>

            {/* Lesson Selector */}
            {availableLessons.length > 0 && (
              <select
                value={state.currentLesson?.id || ""}
                onChange={(e) => handleLessonSelect(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select Lesson...</option>
                {availableLessons.map((lesson) => (
                  <option key={lesson.id} value={lesson.id}>
                    {lesson.title}
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mt-4">
          {(["overview", "students", "annotations", "settings"] as const).map(
            (tab) => (
              <button
                key={tab}
                onClick={() => setSelectedTab(tab)}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                  selectedTab === tab
                    ? "bg-blue-100 text-blue-700"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            )
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {selectedTab === "overview" && (
          <OverviewTab
            state={state}
            activeStudents={activeStudents}
            classProgress={classProgress}
            strugglingStudents={strugglingStudents}
            topPerformers={topPerformers}
            onTogglePause={handleTogglePause}
            onHighlightTopic={(topic) =>
              updateSharedContent({ highlightedTopic: topic })
            }
          />
        )}

        {selectedTab === "students" && (
          <StudentsTab
            state={state}
            activeStudents={activeStudents}
          />
        )}

        {selectedTab === "annotations" && (
          <AnnotationsTab
            annotations={sharedAnnotations}
            students={state.students}
          />
        )}

        {selectedTab === "settings" && (
          <SettingsTab
            settings={state.settings}
            onUpdateSettings={updateSettings}
          />
        )}
      </div>
    </div>
  );
}

// ============================================================================
// Tab Components
// ============================================================================

function OverviewTab({
  state,
  activeStudents,
  classProgress,
  strugglingStudents,
  topPerformers,
  onTogglePause,
  onHighlightTopic,
}: {
  state: ReturnType<typeof useTeacherDashboard>["state"];
  activeStudents: ReturnType<typeof useTeacherDashboard>["activeStudents"];
  classProgress: number;
  strugglingStudents: ReturnType<typeof useTeacherDashboard>["strugglingStudents"];
  topPerformers: ReturnType<typeof useTeacherDashboard>["topPerformers"];
  onTogglePause: () => void;
  onHighlightTopic: (topic: string) => void;
}) {
  const isPaused = !!state.sharedContent.teacherNotes;

  return (
    <div className="space-y-6">
      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={Users}
          label="Active Students"
          value={`${activeStudents.length}/${state.students.length}`}
          trend={activeStudents.length > 0 ? "up" : "neutral"}
        />
        <StatCard
          icon={BarChart3}
          label="Class Progress"
          value={`${Math.round(classProgress)}%`}
          trend={classProgress > 50 ? "up" : "down"}
        />
        <StatCard
          icon={AlertTriangle}
          label="Need Help"
          value={`${strugglingStudents.length}`}
          trend={strugglingStudents.length > 0 ? "down" : "up"}
          negative
        />
        <StatCard
          icon={Trophy}
          label="Top Performers"
          value={`${topPerformers.length}`}
          trend="up"
        />
      </div>

      {/* Quick Actions */}
      <div className="flex flex-wrap gap-2">
        <QuickAction
          icon={isPaused ? Play : Pause}
          label={isPaused ? "Resume Lesson" : "Pause Lesson"}
          onClick={onTogglePause}
          variant={isPaused ? "primary" : "secondary"}
        />
        <QuickAction
          icon={MessageSquare}
          label="Send Message"
          onClick={() => {}}
        />
        <QuickAction
          icon={Share2}
          label="Share Screen"
          onClick={() => {}}
        />
        <QuickAction
          icon={Sparkles}
          label="AI Assist"
          onClick={() => {}}
          variant="primary"
        />
      </div>

      {/* Current Lesson Topics */}
      {state.currentLesson && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            Lesson Topics
          </h3>
          <div className="flex flex-wrap gap-2">
            {state.currentLesson.topics.map((topic, index) => {
              const isHighlighted =
                state.sharedContent.highlightedTopic === topic;
              const completedCount = Object.values(state.studentProgress).filter(
                (p) => p.completedTopics.includes(topic)
              ).length;

              return (
                <button
                  key={topic}
                  onClick={() => onHighlightTopic(topic)}
                  className={`px-3 py-1.5 rounded-full text-sm transition-all ${
                    isHighlighted
                      ? "bg-blue-600 text-white ring-2 ring-blue-300"
                      : "bg-white border border-gray-200 text-gray-700 hover:border-blue-300"
                  }`}
                >
                  <span className="mr-1.5">{index + 1}.</span>
                  {topic}
                  <span
                    className={`ml-2 text-xs ${
                      isHighlighted ? "text-blue-200" : "text-gray-400"
                    }`}
                  >
                    {completedCount}/{state.students.length}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Alerts */}
      {strugglingStudents.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-yellow-800 mb-2 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" />
            Students Needing Attention
          </h3>
          <div className="space-y-2">
            {strugglingStudents.slice(0, 3).map(({ student, progress }) => (
              <div
                key={student!.id}
                className="flex items-center justify-between bg-white rounded-lg px-3 py-2"
              >
                <span className="text-sm text-gray-700">{student!.name}</span>
                <span className="text-sm text-yellow-600 font-medium">
                  Score: {progress.score}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Performers */}
      {topPerformers.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-green-800 mb-2 flex items-center gap-2">
            <Trophy className="h-4 w-4" />
            Top Performers
          </h3>
          <div className="flex flex-wrap gap-2">
            {topPerformers.slice(0, 5).map(({ student, progress }, index) => (
              <div
                key={student!.id}
                className="flex items-center gap-2 bg-white rounded-full px-3 py-1.5"
              >
                <span className="text-xs text-green-600 font-bold">
                  #{index + 1}
                </span>
                <span className="text-sm text-gray-700">{student!.name}</span>
                <span className="text-xs text-green-600 font-medium">
                  {progress.score}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StudentsTab({
  state,
  activeStudents,
}: {
  state: ReturnType<typeof useTeacherDashboard>["state"];
  activeStudents: ReturnType<typeof useTeacherDashboard>["activeStudents"];
}) {
  return (
    <ClassProgress
      students={state.students}
      studentProgress={state.studentProgress}
      lesson={state.currentLesson}
      showIndividual
      sortBy="score"
    />
  );
}

function AnnotationsTab({
  annotations,
  students,
}: {
  annotations: Annotation[];
  students: ReturnType<typeof useTeacherDashboard>["state"]["students"];
}) {
  if (annotations.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <MessageSquare className="h-12 w-12 mx-auto mb-3 text-gray-300" />
        <p>No shared annotations yet</p>
        <p className="text-sm mt-1">
          Student annotations will appear here when shared
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {annotations.map((annotation) => {
        const student = students.find((s) => s.id === annotation.studentId);
        return (
          <div
            key={annotation.id}
            className="bg-gray-50 rounded-lg p-4 border border-gray-200"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-sm font-medium text-gray-600">
                  {student?.name.charAt(0).toUpperCase() || "?"}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {student?.name || "Unknown"}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatTimeAgo(annotation.createdAt)}
                  </p>
                </div>
              </div>
              <span
                className={`px-2 py-0.5 text-xs rounded-full ${
                  annotation.type === "question"
                    ? "bg-blue-100 text-blue-700"
                    : annotation.type === "note"
                    ? "bg-green-100 text-green-700"
                    : "bg-gray-100 text-gray-700"
                }`}
              >
                {annotation.type}
              </span>
            </div>
            <p className="mt-2 text-sm text-gray-700">{annotation.content}</p>
          </div>
        );
      })}
    </div>
  );
}

function SettingsTab({
  settings,
  onUpdateSettings,
}: {
  settings: ReturnType<typeof useTeacherDashboard>["state"]["settings"];
  onUpdateSettings: (
    settings: Partial<ReturnType<typeof useTeacherDashboard>["state"]["settings"]>
  ) => void;
}) {
  return (
    <div className="space-y-4 max-w-md">
      <SettingToggle
        icon={MessageSquare}
        label="Allow Student Annotations"
        description="Students can add notes and questions"
        checked={settings.allowStudentAnnotations}
        onChange={(checked) =>
          onUpdateSettings({ allowStudentAnnotations: checked })
        }
      />
      <SettingToggle
        icon={Eye}
        label="Show Progress to Class"
        description="Display class progress publicly"
        checked={settings.showProgressToClass}
        onChange={(checked) =>
          onUpdateSettings({ showProgressToClass: checked })
        }
      />
      <SettingToggle
        icon={Share2}
        label="Sync Navigation"
        description="Students follow teacher's navigation"
        checked={settings.syncNavigation}
        onChange={(checked) => onUpdateSettings({ syncNavigation: checked })}
      />
    </div>
  );
}

// ============================================================================
// Helper Components
// ============================================================================

function StatCard({
  icon: Icon,
  label,
  value,
  trend,
  negative = false,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  trend?: "up" | "down" | "neutral";
  negative?: boolean;
}) {
  const trendColors = {
    up: negative ? "text-red-500" : "text-green-500",
    down: negative ? "text-green-500" : "text-red-500",
    neutral: "text-gray-400",
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <Icon className="h-5 w-5 text-gray-400" />
        {trend && (
          <span className={`text-xs ${trendColors[trend]}`}>
            {trend === "up" ? "+" : trend === "down" ? "-" : "~"}
          </span>
        )}
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  );
}

function QuickAction({
  icon: Icon,
  label,
  onClick,
  variant = "secondary",
  disabled = false,
}: QuickActionProps) {
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700",
    secondary: "bg-white border border-gray-200 text-gray-700 hover:bg-gray-50",
    danger: "bg-red-600 text-white hover:bg-red-700",
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
        variants[variant]
      } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
    >
      <Icon className="h-4 w-4" />
      {label}
    </button>
  );
}

function SettingToggle({
  icon: Icon,
  label,
  description,
  checked,
  onChange,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
      <div className="flex items-start gap-3">
        <Icon className="h-5 w-5 text-gray-400 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-gray-900">{label}</p>
          <p className="text-xs text-gray-500">{description}</p>
        </div>
      </div>
      <button
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative w-11 h-6 rounded-full transition-colors ${
          checked ? "bg-blue-600" : "bg-gray-200"
        }`}
      >
        <span
          className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${
            checked ? "translate-x-5" : ""
          }`}
        />
      </button>
    </div>
  );
}

// ============================================================================
// Helper Functions
// ============================================================================

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return date.toLocaleDateString();
}

export default TeacherDashboard;
