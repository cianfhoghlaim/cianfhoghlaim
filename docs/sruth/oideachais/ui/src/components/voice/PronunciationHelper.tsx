/**
 * PronunciationHelper - Voice Component.
 *
 * Hover/click to hear Irish word pronunciation.
 * Integrates with useIrishTTS hook for Chatterbox TTS.
 */

import { useState, useCallback } from "react";
import { Volume2, VolumeX, Loader2 } from "lucide-react";
import { useIrishTTS, type IrishDialect } from "../../hooks/useIrishTTS";

// ============================================================================
// Types
// ============================================================================

export interface PronunciationHelperProps {
  /** Irish text to pronounce */
  textGa: string;
  /** English translation (optional) */
  textEn?: string;
  /** Phonetic transcription (optional) */
  phonetic?: string;
  /** Trigger mode: click or hover */
  trigger?: "click" | "hover";
  /** Show dialect selector */
  showDialect?: boolean;
  /** Default dialect */
  defaultDialect?: IrishDialect;
  /** Visual style variant */
  variant?: "inline" | "button" | "card";
  /** Size */
  size?: "sm" | "md" | "lg";
  /** Custom class name */
  className?: string;
}

// ============================================================================
// Component
// ============================================================================

export function PronunciationHelper({
  textGa,
  textEn,
  phonetic,
  trigger = "click",
  showDialect = false,
  defaultDialect = "standard",
  variant = "inline",
  size = "md",
  className = "",
}: PronunciationHelperProps) {
  const {
    pronounce,
    stop,
    isPlaying,
    isLoading,
    error,
    dialect,
    setDialect,
    dialects,
  } = useIrishTTS({
    defaultDialect,
  });

  const [isHovered, setIsHovered] = useState(false);

  const handlePronounce = useCallback(() => {
    if (isPlaying) {
      stop();
    } else {
      pronounce(textGa);
    }
  }, [isPlaying, stop, pronounce, textGa]);

  const handleMouseEnter = useCallback(() => {
    setIsHovered(true);
    if (trigger === "hover" && !isPlaying && !isLoading) {
      pronounce(textGa);
    }
  }, [trigger, isPlaying, isLoading, pronounce, textGa]);

  const handleMouseLeave = useCallback(() => {
    setIsHovered(false);
  }, []);

  // Size configurations
  const sizeConfig = {
    sm: { icon: "h-3 w-3", text: "text-xs", padding: "p-1" },
    md: { icon: "h-4 w-4", text: "text-sm", padding: "p-1.5" },
    lg: { icon: "h-5 w-5", text: "text-base", padding: "p-2" },
  };

  const config = sizeConfig[size];

  // Render based on variant
  if (variant === "inline") {
    return (
      <span
        className={`inline-flex items-center gap-1 cursor-pointer group ${className}`}
        onClick={trigger === "click" ? handlePronounce : undefined}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        title={`Click to pronounce: ${textGa}`}
      >
        <span className={`text-gray-900 ${config.text}`}>{textGa}</span>
        <button
          onClick={(e) => {
            e.stopPropagation();
            handlePronounce();
          }}
          className={`${config.padding} rounded-full transition-colors ${
            isPlaying
              ? "text-blue-600 bg-blue-100"
              : "text-gray-400 group-hover:text-blue-500 group-hover:bg-blue-50"
          }`}
          disabled={isLoading}
        >
          {isLoading ? (
            <Loader2 className={`${config.icon} animate-spin`} />
          ) : isPlaying ? (
            <VolumeX className={config.icon} />
          ) : (
            <Volume2 className={config.icon} />
          )}
        </button>
      </span>
    );
  }

  if (variant === "button") {
    return (
      <button
        onClick={handlePronounce}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        disabled={isLoading}
        className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors ${
          isPlaying
            ? "border-blue-500 bg-blue-50 text-blue-700"
            : "border-gray-200 bg-white text-gray-700 hover:border-blue-300 hover:bg-blue-50"
        } ${isLoading ? "opacity-50 cursor-not-allowed" : ""} ${className}`}
      >
        {isLoading ? (
          <Loader2 className={`${config.icon} animate-spin`} />
        ) : isPlaying ? (
          <VolumeX className={config.icon} />
        ) : (
          <Volume2 className={config.icon} />
        )}
        <span className={config.text}>{textGa}</span>
      </button>
    );
  }

  // Card variant
  return (
    <div
      className={`bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden ${className}`}
    >
      {/* Main content */}
      <div
        className="flex items-center gap-3 p-3 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={trigger === "click" ? handlePronounce : undefined}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        <button
          onClick={(e) => {
            e.stopPropagation();
            handlePronounce();
          }}
          disabled={isLoading}
          className={`flex items-center justify-center rounded-full transition-colors ${
            isPlaying
              ? "bg-blue-100 text-blue-600"
              : "bg-gray-100 text-gray-500 hover:bg-blue-50 hover:text-blue-600"
          } ${config.padding} ${isLoading ? "opacity-50" : ""}`}
        >
          {isLoading ? (
            <Loader2 className={`${config.icon} animate-spin`} />
          ) : isPlaying ? (
            <VolumeX className={config.icon} />
          ) : (
            <Volume2 className={config.icon} />
          )}
        </button>

        <div className="flex-1 min-w-0">
          <p className={`font-medium text-gray-900 ${config.text}`}>{textGa}</p>
          {textEn && (
            <p className="text-xs text-gray-500 mt-0.5">{textEn}</p>
          )}
          {phonetic && (
            <p className="text-xs text-gray-400 font-mono mt-0.5">/{phonetic}/</p>
          )}
        </div>
      </div>

      {/* Dialect selector */}
      {showDialect && (
        <div className="border-t border-gray-100 px-3 py-2 bg-gray-50">
          <div className="flex items-center gap-1 flex-wrap">
            <span className="text-xs text-gray-500 mr-1">Dialect:</span>
            {dialects.map((d) => (
              <button
                key={d.id}
                onClick={() => setDialect(d.id)}
                className={`px-2 py-0.5 text-xs rounded transition-colors ${
                  dialect === d.id
                    ? "bg-green-100 text-green-700 font-medium"
                    : "bg-white border border-gray-200 text-gray-600 hover:border-green-300"
                }`}
                title={d.description}
              >
                {d.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="border-t border-red-100 px-3 py-2 bg-red-50">
          <p className="text-xs text-red-600">{error}</p>
        </div>
      )}
    </div>
  );
}

export default PronunciationHelper;
