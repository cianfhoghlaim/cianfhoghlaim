import React from "react";
import { Check, Lock, Star, BookOpen, Trophy } from "lucide-react";

export type LessonStatus = "locked" | "active" | "completed";
export type LessonType = "star" | "book" | "trophy";

interface LessonNodeProps {
  id: string;
  status: LessonStatus;
  type?: LessonType;
  progress?: number;
  isActive?: boolean;
  onClick?: () => void;
  className?: string;
}

export function LessonNode({
  status,
  type = "star",
  progress = 0,
  isActive = false,
  onClick,
  className = "",
}: LessonNodeProps) {
  const isLocked = status === "locked";
  const isCompleted = status === "completed";

  const Icon = {
    star: Star,
    book: BookOpen,
    trophy: Trophy,
  }[type];

  const colors = {
    locked: "bg-slate-200 text-slate-400 border-slate-300",
    active: "bg-indigo-500 text-white border-indigo-700",
    completed: "bg-emerald-500 text-white border-emerald-700",
  };

  const baseColor = colors[status] || colors.locked;

  return (
    <div
      className={`relative flex flex-col items-center justify-center ${className}`}
    >
      {status === "active" && (
        <div className="absolute inset-[-8px] pointer-events-none">
          <CircularProgress progress={progress} />
        </div>
      )}

      {isActive && (
        <div className="absolute -top-12 animate-bounce bg-white px-3 py-1 rounded-xl shadow-lg border border-indigo-100 text-indigo-600 font-bold text-sm whitespace-nowrap z-10">
          START
          <div className="absolute bottom-[-6px] left-1/2 -translate-x-1/2 w-3 h-3 bg-white border-b border-r border-indigo-100 rotate-45" />
        </div>
      )}

      <button
        onClick={!isLocked ? onClick : undefined}
        disabled={isLocked}
        className={`
          relative w-16 h-16 rounded-full flex items-center justify-center
          transition-all duration-200 transform
          border-b-4 active:border-b-0 active:translate-y-1
          ${baseColor}
          ${isLocked ? "cursor-not-allowed opacity-80" : "cursor-pointer hover:brightness-110"}
          shadow-sm z-0
        `}
      >
        {isCompleted ? (
          <Check className="w-8 h-8 stroke-[3]" />
        ) : isLocked ? (
          <Lock className="w-6 h-6 opacity-50" />
        ) : (
          <Icon className="w-7 h-7 fill-current" />
        )}

        {!isLocked && (
          <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-white/20 to-transparent pointer-events-none" />
        )}
      </button>
    </div>
  );
}

function CircularProgress({ progress }: { progress: number }) {
  const radius = 38;
  const stroke = 5;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <svg
      height={radius * 2}
      width={radius * 2}
      className="rotate-[-90deg] drop-shadow-sm"
    >
      <circle
        stroke="#e2e8f0"
        strokeWidth={stroke}
        fill="transparent"
        r={normalizedRadius}
        cx={radius}
        cy={radius}
        strokeLinecap="round"
      />
      <circle
        stroke="#6366f1"
        strokeWidth={stroke}
        strokeDasharray={circumference + " " + circumference}
        style={{
          strokeDashoffset,
          transition: "stroke-dashoffset 0.5s ease-in-out",
        }}
        fill="transparent"
        r={normalizedRadius}
        cx={radius}
        cy={radius}
        strokeLinecap="round"
      />
    </svg>
  );
}
