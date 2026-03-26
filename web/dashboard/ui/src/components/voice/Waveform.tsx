/**
 * Waveform - Voice Component.
 *
 * Audio visualization for voice activity.
 * Animated waveform based on audio levels.
 */

import { useState, useEffect, useRef, useMemo } from "react";

// ============================================================================
// Types
// ============================================================================

export interface WaveformProps {
  /** Whether audio is active */
  isActive?: boolean;
  /** Audio level (0-1) for manual control */
  level?: number;
  /** Number of bars */
  bars?: number;
  /** Animation style */
  variant?: "bars" | "wave" | "dots";
  /** Color theme */
  color?: "blue" | "green" | "purple" | "gray";
  /** Size */
  size?: "sm" | "md" | "lg";
  /** Custom class name */
  className?: string;
}

// ============================================================================
// Component
// ============================================================================

export function Waveform({
  isActive = false,
  level,
  bars = 5,
  variant = "bars",
  color = "blue",
  size = "md",
  className = "",
}: WaveformProps) {
  const [levels, setLevels] = useState<number[]>(Array(bars).fill(0.2));
  const animationRef = useRef<number | null>(null);

  // Color configurations
  const colorConfig = {
    blue: { active: "bg-blue-500", inactive: "bg-blue-200" },
    green: { active: "bg-green-500", inactive: "bg-green-200" },
    purple: { active: "bg-purple-500", inactive: "bg-purple-200" },
    gray: { active: "bg-gray-500", inactive: "bg-gray-200" },
  };

  // Size configurations
  const sizeConfig = {
    sm: { height: "h-4", width: "w-0.5", gap: "gap-0.5", dot: "w-1 h-1" },
    md: { height: "h-6", width: "w-1", gap: "gap-1", dot: "w-1.5 h-1.5" },
    lg: { height: "h-8", width: "w-1.5", gap: "gap-1.5", dot: "w-2 h-2" },
  };

  const colors = colorConfig[color];
  const sizes = sizeConfig[size];

  // Animate levels when active
  useEffect(() => {
    if (!isActive) {
      setLevels(Array(bars).fill(0.2));
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      return;
    }

    const animate = () => {
      setLevels((prev) =>
        prev.map(() => {
          if (level !== undefined) {
            // Use provided level with some variation
            return 0.2 + level * 0.8 * (0.5 + Math.random() * 0.5);
          }
          // Random animation when no level provided
          return 0.2 + Math.random() * 0.8;
        })
      );
      animationRef.current = requestAnimationFrame(animate);
    };

    // Start animation with interval for natural look
    const intervalId = setInterval(animate, 100);

    return () => {
      clearInterval(intervalId);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive, bars, level]);

  // Memoize bar rendering
  const barsContent = useMemo(() => {
    if (variant === "bars") {
      return levels.map((l, i) => (
        <div
          key={i}
          className={`${sizes.width} rounded-full transition-all duration-100 ${
            isActive ? colors.active : colors.inactive
          }`}
          style={{
            height: `${l * 100}%`,
            transform: `scaleY(${l})`,
          }}
        />
      ));
    }

    if (variant === "wave") {
      return levels.map((l, i) => (
        <div
          key={i}
          className={`${sizes.width} rounded-full transition-all duration-150 ${
            isActive ? colors.active : colors.inactive
          }`}
          style={{
            height: `${l * 100}%`,
            transform: `translateY(${(1 - l) * 50}%)`,
          }}
        />
      ));
    }

    // Dots variant
    return levels.map((l, i) => (
      <div
        key={i}
        className={`${sizes.dot} rounded-full transition-all duration-100 ${
          isActive ? colors.active : colors.inactive
        }`}
        style={{
          transform: `scale(${0.5 + l * 0.5})`,
          opacity: 0.3 + l * 0.7,
        }}
      />
    ));
  }, [levels, variant, sizes, colors, isActive]);

  return (
    <div
      className={`flex items-center justify-center ${sizes.gap} ${sizes.height} ${className}`}
      role="img"
      aria-label={isActive ? "Audio active" : "Audio inactive"}
    >
      {barsContent}
    </div>
  );
}

/**
 * Compact waveform indicator for inline use.
 */
export function WaveformIndicator({
  isActive,
  color = "blue",
  className = "",
}: {
  isActive: boolean;
  color?: WaveformProps["color"];
  className?: string;
}) {
  return (
    <Waveform
      isActive={isActive}
      bars={3}
      variant="bars"
      color={color}
      size="sm"
      className={className}
    />
  );
}

export default Waveform;
