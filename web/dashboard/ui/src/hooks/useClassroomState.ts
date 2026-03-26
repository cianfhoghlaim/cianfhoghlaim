/**
 * useClassroomState Hook.
 *
 * Shared state for classroom collaboration using CopilotKit CoAgents.
 * Enables real-time synchronization of learning progress across students and teachers.
 */

import { useState, useCallback, useEffect, useMemo } from "react";
import {
  useCoAgent,
  useCopilotReadable,
  useCopilotAction,
} from "@copilotkit/react-core";

// ============================================================================
// Types
// ============================================================================

export interface Student {
  id: string;
  name: string;
  avatarUrl?: string;
  isOnline: boolean;
  lastActive: string;
}

export interface LearningProgress {
  studentId: string;
  lessonId: string;
  completedTopics: string[];
  currentTopic: string | null;
  score: number;
  timeSpent: number; // in minutes
  lastUpdated: string;
}

export interface Annotation {
  id: string;
  studentId: string;
  lessonId: string;
  content: string;
  position?: { x: number; y: number };
  type: "note" | "question" | "highlight" | "bookmark";
  isShared: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Lesson {
  id: string;
  title: string;
  titleGa?: string; // Irish title
  subject: string;
  level: "primary" | "junior_cycle" | "senior_cycle";
  topics: string[];
  duration: number; // estimated minutes
}

export interface ClassroomState {
  classroomId: string;
  teacherId: string | null;
  students: Student[];
  currentLesson: Lesson | null;
  studentProgress: Record<string, LearningProgress>;
  annotations: Annotation[];
  sharedContent: {
    currentSlide?: number;
    highlightedTopic?: string;
    teacherNotes?: string;
  };
  settings: {
    allowStudentAnnotations: boolean;
    showProgressToClass: boolean;
    syncNavigation: boolean;
  };
}

export interface UseClassroomStateOptions {
  /** Classroom ID for multi-classroom support */
  classroomId?: string;
  /** Current user role */
  role?: "teacher" | "student";
  /** Current user ID */
  userId?: string;
  /** SSE endpoint for real-time sync */
  syncEndpoint?: string;
  /** Enable real-time synchronization */
  enableSync?: boolean;
}

export interface UseClassroomStateReturn {
  // State
  state: ClassroomState;
  isConnected: boolean;
  connectionError: string | null;
  role: "teacher" | "student";

  // Teacher actions
  setCurrentLesson: (lesson: Lesson | null) => void;
  updateSharedContent: (content: Partial<ClassroomState["sharedContent"]>) => void;
  updateSettings: (settings: Partial<ClassroomState["settings"]>) => void;

  // Student actions
  updateProgress: (progress: Partial<LearningProgress>) => void;
  addAnnotation: (annotation: Omit<Annotation, "id" | "createdAt" | "updatedAt">) => void;
  removeAnnotation: (annotationId: string) => void;
  toggleAnnotationSharing: (annotationId: string) => void;

  // Derived data
  classProgress: number;
  activeStudents: Student[];
  myProgress: LearningProgress | null;
  sharedAnnotations: Annotation[];
}

// ============================================================================
// Initial State
// ============================================================================

const createInitialState = (classroomId: string): ClassroomState => ({
  classroomId,
  teacherId: null,
  students: [],
  currentLesson: null,
  studentProgress: {},
  annotations: [],
  sharedContent: {},
  settings: {
    allowStudentAnnotations: true,
    showProgressToClass: false,
    syncNavigation: true,
  },
});

// ============================================================================
// Hook Implementation
// ============================================================================

export function useClassroomState(
  options: UseClassroomStateOptions = {}
): UseClassroomStateReturn {
  const {
    classroomId = "default",
    role = "student",
    userId = "anonymous",
    syncEndpoint = "/api/classroom/sync",
    enableSync = true,
  } = options;

  // Connect to the classroom agent with shared state
  const { state, setState } = useCoAgent<ClassroomState>({
    name: `classroom_${classroomId}`,
    initialState: createInitialState(classroomId),
  });

  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  // ============================================================================
  // CopilotKit Integration
  // ============================================================================

  // Expose classroom state to the AI assistant
  useCopilotReadable({
    description: "Current classroom learning state including students, lesson, progress, and annotations. Use this to understand classroom activity and provide contextual help.",
    value: {
      classroomId: state.classroomId,
      hasTeacher: !!state.teacherId,
      studentCount: state.students.length,
      activeStudentCount: state.students.filter((s) => s.isOnline).length,
      currentLesson: state.currentLesson
        ? {
            title: state.currentLesson.title,
            subject: state.currentLesson.subject,
            level: state.currentLesson.level,
            topicCount: state.currentLesson.topics.length,
          }
        : null,
      averageProgress: calculateAverageProgress(state.studentProgress),
      annotationCount: state.annotations.length,
      sharedAnnotationCount: state.annotations.filter((a) => a.isShared).length,
    },
  });

  // Register action to get student progress
  useCopilotAction({
    name: "getStudentProgress",
    description: "Get the learning progress for a specific student in the classroom",
    parameters: [
      {
        name: "studentId",
        type: "string",
        description: "The ID of the student (or 'all' for all students)",
        required: true,
      },
    ],
    handler: async ({ studentId }) => {
      if (studentId === "all") {
        return {
          students: Object.entries(state.studentProgress).map(([id, progress]) => ({
            studentId: id,
            studentName: state.students.find((s) => s.id === id)?.name ?? "Unknown",
            completedTopics: progress.completedTopics.length,
            currentTopic: progress.currentTopic,
            score: progress.score,
            timeSpent: progress.timeSpent,
          })),
          averageProgress: calculateAverageProgress(state.studentProgress),
        };
      }

      const progress = state.studentProgress[studentId];
      const student = state.students.find((s) => s.id === studentId);

      if (!progress) {
        return { found: false, message: `No progress found for student ${studentId}` };
      }

      return {
        found: true,
        studentId,
        studentName: student?.name ?? "Unknown",
        isOnline: student?.isOnline ?? false,
        ...progress,
      };
    },
  });

  // Register action to get lesson info
  useCopilotAction({
    name: "getClassroomLesson",
    description: "Get information about the current lesson in the classroom",
    parameters: [],
    handler: async () => {
      if (!state.currentLesson) {
        return { hasLesson: false, message: "No lesson is currently active" };
      }

      return {
        hasLesson: true,
        ...state.currentLesson,
        sharedContent: state.sharedContent,
      };
    },
  });

  // ============================================================================
  // Real-time Synchronization
  // ============================================================================

  useEffect(() => {
    if (!enableSync) return;

    let eventSource: EventSource | null = null;
    let reconnectTimeout: NodeJS.Timeout | null = null;

    const connect = () => {
      const url = `${syncEndpoint}?classroom=${classroomId}&role=${role}&user=${userId}`;
      eventSource = new EventSource(url);

      eventSource.onopen = () => {
        setIsConnected(true);
        setConnectionError(null);
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleSyncEvent(data);
        } catch (e) {
          console.error("Failed to parse sync event:", e);
        }
      };

      eventSource.onerror = () => {
        setIsConnected(false);
        setConnectionError("Connection lost. Reconnecting...");
        reconnectTimeout = setTimeout(() => {
          eventSource?.close();
          connect();
        }, 5000);
      };
    };

    connect();

    return () => {
      eventSource?.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, [enableSync, syncEndpoint, classroomId, role, userId]);

  // Handle sync events from server
  const handleSyncEvent = useCallback(
    (event: { type: string; payload: unknown }) => {
      switch (event.type) {
        case "student_joined":
          setState((prev) => ({
            ...prev,
            students: [...prev.students, event.payload as Student],
          }));
          break;

        case "student_left":
          setState((prev) => ({
            ...prev,
            students: prev.students.map((s) =>
              s.id === (event.payload as { studentId: string }).studentId
                ? { ...s, isOnline: false }
                : s
            ),
          }));
          break;

        case "progress_update":
          const progressUpdate = event.payload as {
            studentId: string;
            progress: LearningProgress;
          };
          setState((prev) => ({
            ...prev,
            studentProgress: {
              ...prev.studentProgress,
              [progressUpdate.studentId]: progressUpdate.progress,
            },
          }));
          break;

        case "lesson_changed":
          setState((prev) => ({
            ...prev,
            currentLesson: event.payload as Lesson,
          }));
          break;

        case "annotation_added":
          setState((prev) => ({
            ...prev,
            annotations: [...prev.annotations, event.payload as Annotation],
          }));
          break;

        case "shared_content_update":
          setState((prev) => ({
            ...prev,
            sharedContent: {
              ...prev.sharedContent,
              ...(event.payload as ClassroomState["sharedContent"]),
            },
          }));
          break;

        case "full_sync":
          setState(event.payload as ClassroomState);
          break;
      }
    },
    [setState]
  );

  // ============================================================================
  // Teacher Actions
  // ============================================================================

  const setCurrentLesson = useCallback(
    (lesson: Lesson | null) => {
      setState((prev) => ({
        ...prev,
        currentLesson: lesson,
        // Reset progress when lesson changes
        studentProgress: lesson
          ? Object.fromEntries(
              prev.students.map((s) => [
                s.id,
                {
                  studentId: s.id,
                  lessonId: lesson.id,
                  completedTopics: [],
                  currentTopic: lesson.topics[0] || null,
                  score: 0,
                  timeSpent: 0,
                  lastUpdated: new Date().toISOString(),
                },
              ])
            )
          : {},
      }));

      // Broadcast to server
      if (enableSync) {
        fetch(`${syncEndpoint}/lesson`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ classroomId, lesson }),
        }).catch(console.error);
      }
    },
    [setState, enableSync, syncEndpoint, classroomId]
  );

  const updateSharedContent = useCallback(
    (content: Partial<ClassroomState["sharedContent"]>) => {
      setState((prev) => ({
        ...prev,
        sharedContent: { ...prev.sharedContent, ...content },
      }));

      if (enableSync) {
        fetch(`${syncEndpoint}/shared-content`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ classroomId, content }),
        }).catch(console.error);
      }
    },
    [setState, enableSync, syncEndpoint, classroomId]
  );

  const updateSettings = useCallback(
    (settings: Partial<ClassroomState["settings"]>) => {
      setState((prev) => ({
        ...prev,
        settings: { ...prev.settings, ...settings },
      }));
    },
    [setState]
  );

  // ============================================================================
  // Student Actions
  // ============================================================================

  const updateProgress = useCallback(
    (progress: Partial<LearningProgress>) => {
      setState((prev) => {
        const currentProgress = prev.studentProgress[userId] || {
          studentId: userId,
          lessonId: prev.currentLesson?.id || "",
          completedTopics: [],
          currentTopic: null,
          score: 0,
          timeSpent: 0,
          lastUpdated: new Date().toISOString(),
        };

        const updatedProgress = {
          ...currentProgress,
          ...progress,
          lastUpdated: new Date().toISOString(),
        };

        return {
          ...prev,
          studentProgress: {
            ...prev.studentProgress,
            [userId]: updatedProgress,
          },
        };
      });

      if (enableSync) {
        fetch(`${syncEndpoint}/progress`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ classroomId, studentId: userId, progress }),
        }).catch(console.error);
      }
    },
    [setState, userId, enableSync, syncEndpoint, classroomId]
  );

  const addAnnotation = useCallback(
    (annotation: Omit<Annotation, "id" | "createdAt" | "updatedAt">) => {
      const newAnnotation: Annotation = {
        ...annotation,
        id: `ann_${Date.now()}_${Math.random().toString(36).slice(2)}`,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      setState((prev) => ({
        ...prev,
        annotations: [...prev.annotations, newAnnotation],
      }));

      if (enableSync && annotation.isShared) {
        fetch(`${syncEndpoint}/annotation`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ classroomId, annotation: newAnnotation }),
        }).catch(console.error);
      }
    },
    [setState, enableSync, syncEndpoint, classroomId]
  );

  const removeAnnotation = useCallback(
    (annotationId: string) => {
      setState((prev) => ({
        ...prev,
        annotations: prev.annotations.filter((a) => a.id !== annotationId),
      }));
    },
    [setState]
  );

  const toggleAnnotationSharing = useCallback(
    (annotationId: string) => {
      setState((prev) => ({
        ...prev,
        annotations: prev.annotations.map((a) =>
          a.id === annotationId
            ? { ...a, isShared: !a.isShared, updatedAt: new Date().toISOString() }
            : a
        ),
      }));
    },
    [setState]
  );

  // ============================================================================
  // Derived Data
  // ============================================================================

  const classProgress = useMemo(
    () => calculateAverageProgress(state.studentProgress),
    [state.studentProgress]
  );

  const activeStudents = useMemo(
    () => state.students.filter((s) => s.isOnline),
    [state.students]
  );

  const myProgress = useMemo(
    () => state.studentProgress[userId] || null,
    [state.studentProgress, userId]
  );

  const sharedAnnotations = useMemo(
    () => state.annotations.filter((a) => a.isShared),
    [state.annotations]
  );

  return {
    state,
    isConnected,
    connectionError,
    role,
    setCurrentLesson,
    updateSharedContent,
    updateSettings,
    updateProgress,
    addAnnotation,
    removeAnnotation,
    toggleAnnotationSharing,
    classProgress,
    activeStudents,
    myProgress,
    sharedAnnotations,
  };
}

// ============================================================================
// Helper Functions
// ============================================================================

function calculateAverageProgress(
  studentProgress: Record<string, LearningProgress>
): number {
  const progressValues = Object.values(studentProgress);
  if (progressValues.length === 0) return 0;

  const totalProgress = progressValues.reduce((sum, p) => {
    // Calculate individual progress as percentage of completed topics
    // Assuming score is out of 100 for simplicity
    return sum + p.score;
  }, 0);

  return totalProgress / progressValues.length;
}

/**
 * Simplified hook for students to track their own progress.
 */
export function useMyProgress(options: { classroomId?: string; userId: string }) {
  const { state, updateProgress, myProgress } = useClassroomState({
    ...options,
    role: "student",
  });

  return {
    progress: myProgress,
    currentLesson: state.currentLesson,
    updateProgress,
    completeTopic: (topicId: string) => {
      if (!myProgress) return;
      updateProgress({
        completedTopics: [...myProgress.completedTopics, topicId],
        currentTopic:
          state.currentLesson?.topics[
            state.currentLesson.topics.indexOf(topicId) + 1
          ] || null,
      });
    },
    updateScore: (score: number) => {
      updateProgress({ score });
    },
  };
}

/**
 * Simplified hook for teachers to monitor class progress.
 */
export function useTeacherDashboard(options: { classroomId?: string; userId: string }) {
  const classroom = useClassroomState({
    ...options,
    role: "teacher",
  });

  const strugglingStudents = useMemo(() => {
    return Object.entries(classroom.state.studentProgress)
      .filter(([, progress]) => progress.score < 50)
      .map(([studentId]) => ({
        student: classroom.state.students.find((s) => s.id === studentId),
        progress: classroom.state.studentProgress[studentId],
      }))
      .filter((s) => s.student);
  }, [classroom.state.studentProgress, classroom.state.students]);

  const topPerformers = useMemo(() => {
    return Object.entries(classroom.state.studentProgress)
      .filter(([, progress]) => progress.score >= 80)
      .map(([studentId]) => ({
        student: classroom.state.students.find((s) => s.id === studentId),
        progress: classroom.state.studentProgress[studentId],
      }))
      .filter((s) => s.student)
      .sort((a, b) => b.progress.score - a.progress.score);
  }, [classroom.state.studentProgress, classroom.state.students]);

  return {
    ...classroom,
    strugglingStudents,
    topPerformers,
  };
}

export default useClassroomState;
