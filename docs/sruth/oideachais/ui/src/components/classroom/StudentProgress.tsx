/**
 * StudentProgress - Classroom Component.
 *
 * Displays student learning progress in the classroom.
 * Shows individual and class-wide progress visualization.
 */

import { useMemo } from "react";
import {
  BookOpen,
  CheckCircle,
  Clock,
  TrendingUp,
  Users,
  Award,
  Target,
} from "lucide-react";
import type { LearningProgress, Student, Lesson } from "../../hooks/useClassroomState";

// ============================================================================
// Types
// ============================================================================

export interface StudentProgressProps {
  /** Student information */
  student: Student;
  /** Learning progress data */
  progress: LearningProgress;
  /** Current lesson */
  lesson?: Lesson | null;
  /** Show detailed breakdown */
  detailed?: boolean;
  /** Compact display mode */
  compact?: boolean;
  /** Size variant */
  size?: "sm" | "md" | "lg";
  /** Click handler */
  onClick?: () => void;
  /** Custom class name */
  className?: string;
}

export interface ClassProgressProps {
  /** All student progress records */
  studentProgress: Record<string, LearningProgress>;
  /** Student list */
  students: Student[];
  /** Current lesson */
  lesson?: Lesson | null;
  /** Show individual breakdown */
  showIndividual?: boolean;
  /** Sort order */
  sortBy?: "name" | "score" | "progress" | "time";
  /** Custom class name */
  className?: string;
}

// ============================================================================
// StudentProgress Component
// ============================================================================

export function StudentProgress({
  student,
  progress,
  lesson,
  detailed = false,
  compact = false,
  size = "md",
  onClick,
  className = "",
}: StudentProgressProps) {
  // Calculate progress percentage
  const progressPercent = useMemo(() => {
    if (!lesson || lesson.topics.length === 0) return 0;
    return Math.round(
      (progress.completedTopics.length / lesson.topics.length) * 100
    );
  }, [progress.completedTopics, lesson]);

  // Size configurations
  const sizeConfig = {
    sm: {
      container: "p-2",
      avatar: "w-8 h-8 text-sm",
      text: "text-xs",
      badge: "text-xs px-1.5 py-0.5",
    },
    md: {
      container: "p-3",
      avatar: "w-10 h-10 text-base",
      text: "text-sm",
      badge: "text-sm px-2 py-1",
    },
    lg: {
      container: "p-4",
      avatar: "w-12 h-12 text-lg",
      text: "text-base",
      badge: "text-base px-2.5 py-1",
    },
  };

  const config = sizeConfig[size];

  // Get score color
  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600 bg-green-100";
    if (score >= 60) return "text-blue-600 bg-blue-100";
    if (score >= 40) return "text-yellow-600 bg-yellow-100";
    return "text-red-600 bg-red-100";
  };

  // Get status indicator
  const getStatusIndicator = () => {
    if (!student.isOnline) {
      return <span className="w-2 h-2 bg-gray-300 rounded-full" />;
    }
    if (progress.currentTopic) {
      return <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />;
    }
    return <span className="w-2 h-2 bg-green-500 rounded-full" />;
  };

  if (compact) {
    return (
      <div
        className={`flex items-center gap-2 ${onClick ? "cursor-pointer hover:bg-gray-50" : ""} ${className}`}
        onClick={onClick}
      >
        {/* Avatar */}
        <div className="relative">
          {student.avatarUrl ? (
            <img
              src={student.avatarUrl}
              alt={student.name}
              className={`${config.avatar} rounded-full`}
            />
          ) : (
            <div
              className={`${config.avatar} rounded-full bg-gray-200 flex items-center justify-center font-medium text-gray-600`}
            >
              {student.name.charAt(0).toUpperCase()}
            </div>
          )}
          <span className="absolute -bottom-0.5 -right-0.5">
            {getStatusIndicator()}
          </span>
        </div>

        {/* Name and progress */}
        <div className="flex-1 min-w-0">
          <p className={`${config.text} font-medium text-gray-900 truncate`}>
            {student.name}
          </p>
          <div className="flex items-center gap-1">
            <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 rounded-full transition-all duration-300"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            <span className={`${config.text} text-gray-500`}>
              {progressPercent}%
            </span>
          </div>
        </div>

        {/* Score badge */}
        <span
          className={`${config.badge} rounded-full font-medium ${getScoreColor(progress.score)}`}
        >
          {progress.score}
        </span>
      </div>
    );
  }

  return (
    <div
      className={`bg-white rounded-lg border border-gray-200 shadow-sm ${config.container} ${onClick ? "cursor-pointer hover:shadow-md transition-shadow" : ""} ${className}`}
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-3">
        {/* Avatar */}
        <div className="relative">
          {student.avatarUrl ? (
            <img
              src={student.avatarUrl}
              alt={student.name}
              className={`${config.avatar} rounded-full`}
            />
          ) : (
            <div
              className={`${config.avatar} rounded-full bg-gray-200 flex items-center justify-center font-medium text-gray-600`}
            >
              {student.name.charAt(0).toUpperCase()}
            </div>
          )}
          <span className="absolute -bottom-0.5 -right-0.5">
            {getStatusIndicator()}
          </span>
        </div>

        <div className="flex-1 min-w-0">
          <h3 className={`${config.text} font-semibold text-gray-900 truncate`}>
            {student.name}
          </h3>
          <p className={`${config.text} text-gray-500`}>
            {student.isOnline ? (
              progress.currentTopic ? (
                <span className="text-green-600">Learning: {progress.currentTopic}</span>
              ) : (
                "Online"
              )
            ) : (
              `Last active: ${formatTimeAgo(student.lastActive)}`
            )}
          </p>
        </div>

        {/* Score badge */}
        <span
          className={`${config.badge} rounded-full font-semibold ${getScoreColor(progress.score)}`}
        >
          {progress.score}%
        </span>
      </div>

      {/* Progress bar */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className={`${config.text} text-gray-600`}>Lesson Progress</span>
          <span className={`${config.text} text-gray-900 font-medium`}>
            {progress.completedTopics.length} / {lesson?.topics.length ?? 0} topics
          </span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full transition-all duration-300"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Stats */}
      {detailed && (
        <div className="grid grid-cols-3 gap-2">
          <div className="flex items-center gap-1.5 text-gray-600">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span className={config.text}>
              {progress.completedTopics.length} done
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-gray-600">
            <Clock className="h-4 w-4 text-blue-500" />
            <span className={config.text}>{progress.timeSpent}m</span>
          </div>
          <div className="flex items-center gap-1.5 text-gray-600">
            <TrendingUp className="h-4 w-4 text-purple-500" />
            <span className={config.text}>{progress.score}%</span>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// ClassProgress Component
// ============================================================================

export function ClassProgress({
  studentProgress,
  students,
  lesson,
  showIndividual = true,
  sortBy = "name",
  className = "",
}: ClassProgressProps) {
  // Calculate class statistics
  const stats = useMemo(() => {
    const progressValues = Object.values(studentProgress);
    if (progressValues.length === 0) {
      return { averageScore: 0, averageProgress: 0, totalTime: 0, completing: 0 };
    }

    const scores = progressValues.map((p) => p.score);
    const progressPercents = progressValues.map((p) => {
      if (!lesson || lesson.topics.length === 0) return 0;
      return (p.completedTopics.length / lesson.topics.length) * 100;
    });

    return {
      averageScore: Math.round(scores.reduce((a, b) => a + b, 0) / scores.length),
      averageProgress: Math.round(
        progressPercents.reduce((a, b) => a + b, 0) / progressPercents.length
      ),
      totalTime: progressValues.reduce((sum, p) => sum + p.timeSpent, 0),
      completing: progressValues.filter((p) => {
        if (!lesson) return false;
        return p.completedTopics.length === lesson.topics.length;
      }).length,
    };
  }, [studentProgress, lesson]);

  // Sort students
  const sortedStudents = useMemo(() => {
    const list = students
      .map((student) => ({
        student,
        progress: studentProgress[student.id],
      }))
      .filter((s) => s.progress);

    switch (sortBy) {
      case "score":
        return list.sort((a, b) => b.progress.score - a.progress.score);
      case "progress":
        return list.sort(
          (a, b) =>
            b.progress.completedTopics.length - a.progress.completedTopics.length
        );
      case "time":
        return list.sort((a, b) => b.progress.timeSpent - a.progress.timeSpent);
      default:
        return list.sort((a, b) => a.student.name.localeCompare(b.student.name));
    }
  }, [students, studentProgress, sortBy]);

  const activeCount = students.filter((s) => s.isOnline).length;

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Class Overview */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Users className="h-5 w-5 text-blue-500" />
          Class Progress
          {lesson && (
            <span className="text-sm font-normal text-gray-500">
              - {lesson.title}
            </span>
          )}
        </h2>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            icon={Users}
            label="Active Students"
            value={`${activeCount}/${students.length}`}
            color="blue"
          />
          <StatCard
            icon={Target}
            label="Avg. Progress"
            value={`${stats.averageProgress}%`}
            color="green"
          />
          <StatCard
            icon={Award}
            label="Avg. Score"
            value={`${stats.averageScore}%`}
            color="purple"
          />
          <StatCard
            icon={CheckCircle}
            label="Completed"
            value={`${stats.completing}`}
            color="orange"
          />
        </div>

        {/* Overall Progress Bar */}
        <div className="mt-4">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-gray-600">Class Completion</span>
            <span className="text-sm font-medium text-gray-900">
              {stats.averageProgress}%
            </span>
          </div>
          <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-green-400 to-green-600 rounded-full transition-all duration-500"
              style={{ width: `${stats.averageProgress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Individual Progress */}
      {showIndividual && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-700 flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            Individual Progress
            <span className="text-gray-400">({sortedStudents.length} students)</span>
          </h3>

          <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
            {sortedStudents.map(({ student, progress }) => (
              <StudentProgress
                key={student.id}
                student={student}
                progress={progress}
                lesson={lesson}
                compact
                size="sm"
              />
            ))}
          </div>
        </div>
      )}
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
  color,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  color: "blue" | "green" | "purple" | "orange";
}) {
  const colorConfig = {
    blue: "bg-blue-50 text-blue-600",
    green: "bg-green-50 text-green-600",
    purple: "bg-purple-50 text-purple-600",
    orange: "bg-orange-50 text-orange-600",
  };

  return (
    <div className="bg-gray-50 rounded-lg p-3">
      <div className="flex items-center gap-2 mb-1">
        <div className={`p-1.5 rounded-md ${colorConfig[color]}`}>
          <Icon className="h-4 w-4" />
        </div>
        <span className="text-xs text-gray-500">{label}</span>
      </div>
      <p className="text-xl font-semibold text-gray-900">{value}</p>
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
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

export default StudentProgress;
