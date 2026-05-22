import React from "react";
import { LessonNode, LessonStatus, LessonType } from "./LessonNode";
import { StreakCounter } from "./StreakCounter";
import { MasteryPill, MasteryLevel } from "./MasteryPill";

export interface Lesson {
  id: string;
  title: string;
  status: LessonStatus;
  type: LessonType;
  progress?: number;
  mastery?: MasteryLevel;
}

interface LearningPathProps {
  lessons?: Lesson[];
  streakDays?: number;
  streakActive?: boolean;
  onLessonSelect?: (lessonId: string) => void;
  className?: string;
}

const DEFAULT_LESSONS: Lesson[] = [
  {
    id: "1",
    title: "Intro to Phrases",
    status: "completed",
    type: "book",
    mastery: "mastered",
  },
  {
    id: "2",
    title: "Common Greetings",
    status: "completed",
    type: "star",
    mastery: "proficient",
  },
  {
    id: "3",
    title: "Numbers & Counting",
    status: "completed",
    type: "star",
    mastery: "familiar",
  },
  {
    id: "4",
    title: "Food & Drink",
    status: "active",
    type: "trophy",
    progress: 65,
    mastery: "attempted",
  },
  {
    id: "5",
    title: "Family Members",
    status: "locked",
    type: "book",
    mastery: "attempted",
  },
  {
    id: "6",
    title: "Animals",
    status: "locked",
    type: "star",
    mastery: "attempted",
  },
  {
    id: "7",
    title: "Colors",
    status: "locked",
    type: "star",
    mastery: "attempted",
  },
  {
    id: "8",
    title: "Travel Basics",
    status: "locked",
    type: "trophy",
    mastery: "attempted",
  },
];

export function LearningPath({
  lessons = DEFAULT_LESSONS,
  streakDays = 12,
  streakActive = false,
  onLessonSelect,
  className = "",
}: LearningPathProps) {
  return (
    <div
      className={`flex flex-col items-center w-full max-w-md mx-auto p-6 ${className}`}
    >
      <div className="w-full flex justify-between items-center mb-12 px-4 sticky top-4 z-20">
        <StreakCounter days={streakDays} isActive={streakActive} />
        <div className="flex gap-2">
          <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center border border-slate-200">
            <span className="text-sm font-bold text-slate-600">ga</span>
          </div>
        </div>
      </div>

      <div className="relative w-full flex flex-col items-center gap-4 pb-20">
        <PathSvg lessons={lessons} />

        {lessons.map((lesson, index) => {
          const cycleIndex = index % 8;
          const indent = Math.sin((cycleIndex / 8) * Math.PI * 2) * 80;

          return (
            <div
              key={lesson.id}
              className="relative z-10 flex flex-col items-center"
              style={{ transform: `translateX(${indent}px)` }}
            >
              <div className="group relative">
                <LessonNode
                  id={lesson.id}
                  status={lesson.status}
                  type={lesson.type}
                  progress={lesson.progress}
                  isActive={lesson.status === "active"}
                  onClick={() => onLessonSelect?.(lesson.id)}
                />

                <div className="absolute top-1/2 left-full ml-4 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 text-white text-xs px-2 py-1 rounded pointer-events-none whitespace-nowrap z-20">
                  {lesson.title}
                </div>
              </div>

              {lesson.status !== "locked" && lesson.mastery && (
                <div className="mt-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 absolute top-full pt-1">
                  <MasteryPill level={lesson.mastery} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function PathSvg({ lessons }: { lessons: Lesson[] }) {
  const NODE_HEIGHT = 80 + 16;
  const totalHeight = lessons.length * NODE_HEIGHT;

  const points = lessons
    .map((_, index) => {
      const cycleIndex = index % 8;
      const x = Math.sin((cycleIndex / 8) * Math.PI * 2) * 80;
      const y = index * NODE_HEIGHT + 32;
      return `${x + 200},${y}`;
    })
    .join(" ");

  return (
    <svg
      className="absolute top-0 left-0 w-full h-full pointer-events-none z-0 overflow-visible"
      viewBox={`0 0 400 ${totalHeight}`}
      preserveAspectRatio="xMidYMin slice"
    >
      <path
        d={`M ${points}`}
        fill="none"
        stroke="#e2e8f0"
        strokeWidth="10"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="opacity-50"
      />
      <path
        d={`M ${points}`}
        fill="none"
        stroke="#e2e8f0"
        strokeWidth="6"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeDasharray="12 12"
      />
    </svg>
  );
}
