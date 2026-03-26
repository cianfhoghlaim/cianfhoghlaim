/**
 * Orb - Voice Component.
 *
 * Animated voice indicator orb.
 * Visual feedback for voice activity state.
 */

import { useState, useEffect } from "react";
import { Mic, Volume2, VolumeX, Loader2 } from "lucide-react";

// ============================================================================
// Types
// ============================================================================

export type OrbState = "idle" | "listening" | "speaking" | "processing" | "error";

export interface OrbProps {
  /** Current state */
  state?: OrbState;
  /** Audio level (0-1) for amplitude visualization */
  level?: number;
  /** Size variant */
  size?: "sm" | "md" | "lg" | "xl";
  /** Color theme */
  color?: "blue" | "green" | "purple" | "red";
  /** Show icon in center */
  showIcon?: boolean;
  /** Click handler */
  onClick?: () => void;
  /** Custom class name */
  className?: string;
}

// ============================================================================
// Component
// ============================================================================

export function Orb({
  state = "idle",
  level = 0,
  size = "md",
  color = "blue",
  showIcon = true,
  onClick,
  className = "",
}: OrbProps) {
  const [pulseScale, setPulseScale] = useState(1);

  // Animate based on level
  useEffect(() => {
    if (state === "listening" || state === "speaking") {
      setPulseScale(1 + level * 0.3);
    } else {
      setPulseScale(1);
    }
  }, [level, state]);

  // Size configurations
  const sizeConfig = {
    sm: { container: "w-10 h-10", icon: "h-4 w-4", ring: "ring-4" },
    md: { container: "w-14 h-14", icon: "h-5 w-5", ring: "ring-4" },
    lg: { container: "w-20 h-20", icon: "h-6 w-6", ring: "ring-6" },
    xl: { container: "w-28 h-28", icon: "h-8 w-8", ring: "ring-8" },
  };

  // Color configurations
  const colorConfig = {
    blue: {
      bg: "bg-blue-500",
      ring: "ring-blue-200",
      pulse: "bg-blue-400",
      icon: "text-white",
    },
    green: {
      bg: "bg-green-500",
      ring: "ring-green-200",
      pulse: "bg-green-400",
      icon: "text-white",
    },
    purple: {
      bg: "bg-purple-500",
      ring: "ring-purple-200",
      pulse: "bg-purple-400",
      icon: "text-white",
    },
    red: {
      bg: "bg-red-500",
      ring: "ring-red-200",
      pulse: "bg-red-400",
      icon: "text-white",
    },
  };

  // State configurations
  const stateConfig: Record<OrbState, { animation: string; opacity: number }> = {
    idle: { animation: "", opacity: 0.7 },
    listening: { animation: "animate-pulse", opacity: 1 },
    speaking: { animation: "animate-ping", opacity: 1 },
    processing: { animation: "animate-spin", opacity: 0.9 },
    error: { animation: "animate-bounce", opacity: 1 },
  };

  const sizes = sizeConfig[size];
  const colors = colorConfig[state === "error" ? "red" : color];
  const stateStyle = stateConfig[state];

  // Get appropriate icon
  const getIcon = () => {
    switch (state) {
      case "listening":
        return <Mic className={sizes.icon} />;
      case "speaking":
        return <Volume2 className={sizes.icon} />;
      case "error":
        return <VolumeX className={sizes.icon} />;
      case "processing":
        return <Loader2 className={`${sizes.icon} animate-spin`} />;
      default:
        return <Mic className={sizes.icon} />;
    }
  };

  return (
    <button
      onClick={onClick}
      disabled={state === "processing"}
      className={`relative flex items-center justify-center rounded-full transition-all duration-300 ${
        onClick ? "cursor-pointer hover:scale-105" : "cursor-default"
      } ${sizes.container} ${className}`}
      style={{
        transform: `scale(${pulseScale})`,
        opacity: stateStyle.opacity,
      }}
    >
      {/* Pulse rings for active states */}
      {(state === "listening" || state === "speaking") && (
        <>
          <span
            className={`absolute inset-0 rounded-full ${colors.pulse} opacity-30 ${stateStyle.animation}`}
            style={{
              transform: `scale(${1 + level * 0.5})`,
            }}
          />
          <span
            className={`absolute inset-0 rounded-full ${colors.pulse} opacity-20 ${stateStyle.animation}`}
            style={{
              transform: `scale(${1 + level * 0.8})`,
              animationDelay: "0.2s",
            }}
          />
        </>
      )}

      {/* Main orb */}
      <span
        className={`relative flex items-center justify-center rounded-full ${sizes.container} ${colors.bg} ${sizes.ring} ${colors.ring} shadow-lg`}
      >
        {showIcon && (
          <span className={colors.icon}>{getIcon()}</span>
        )}
      </span>

      {/* Level indicator ring */}
      {(state === "listening" || state === "speaking") && level > 0 && (
        <svg
          className="absolute inset-0 w-full h-full -rotate-90"
          viewBox="0 0 100 100"
        >
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="currentColor"
            strokeWidth="4"
            strokeDasharray={`${level * 283} 283`}
            className={`${colors.icon} opacity-50 transition-all duration-100`}
          />
        </svg>
      )}
    </button>
  );
}

/**
 * Minimal orb for compact displays.
 */
export function OrbMini({
  isActive,
  color = "blue",
  className = "",
}: {
  isActive: boolean;
  color?: OrbProps["color"];
  className?: string;
}) {
  return (
    <span
      className={`inline-flex w-3 h-3 rounded-full transition-all duration-300 ${
        isActive ? `bg-${color}-500 animate-pulse` : `bg-${color}-300`
      } ${className}`}
    />
  );
}

export default Orb;
