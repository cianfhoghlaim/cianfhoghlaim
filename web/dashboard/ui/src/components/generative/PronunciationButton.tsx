/**
 * PronunciationButton - Generative UI Component.
 *
 * Click-to-hear button for Irish words and phrases.
 * Supports dialect selection (Connacht, Munster, Ulster).
 */

import { useState, useCallback } from "react";
import { Volume2, VolumeX, Loader2, X } from "lucide-react";

// ============================================================================
// Types
// ============================================================================

export type IrishDialect = "connacht" | "munster" | "ulster" | "standard";

export interface PronunciationButtonProps {
  /** Unique ID from AG-UI event */
  componentId?: string;
  /** Callback to dismiss the component */
  onDismiss?: () => void;

  /** Text to pronounce */
  text: string;
  /** Irish translation (if text is English) */
  textGa?: string;
  /** English translation (if text is Irish) */
  textEn?: string;
  /** Current dialect preference */
  dialect?: IrishDialect;
  /** Whether text is Irish */
  isIrish?: boolean;
  /** Phonetic transcription */
  phonetic?: string;
  /** Size variant */
  size?: "sm" | "md" | "lg";
  /** Custom pronunciation endpoint */
  ttsEndpoint?: string;
  /** Callback when pronunciation starts */
  onPlay?: () => void;
  /** Callback when pronunciation ends */
  onEnd?: () => void;
  /** Callback for dialect change */
  onDialectChange?: (dialect: IrishDialect) => void;
}

// ============================================================================
// Component
// ============================================================================

export function PronunciationButton({
  componentId,
  onDismiss,
  text,
  textGa,
  textEn,
  dialect = "standard",
  isIrish = true,
  phonetic,
  size = "md",
  ttsEndpoint = "/api/tts",
  onPlay,
  onEnd,
  onDialectChange,
}: PronunciationButtonProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentDialect, setCurrentDialect] = useState<IrishDialect>(dialect);
  const [audioRef, setAudioRef] = useState<HTMLAudioElement | null>(null);

  const dialectLabels: Record<IrishDialect, { label: string; region: string }> = {
    connacht: { label: "Connacht", region: "West" },
    munster: { label: "Munster", region: "South" },
    ulster: { label: "Ulster", region: "North" },
    standard: { label: "Standard", region: "Official" },
  };

  const sizeConfig = {
    sm: {
      button: "px-2 py-1 text-xs",
      icon: "h-3 w-3",
      text: "text-xs",
    },
    md: {
      button: "px-3 py-2 text-sm",
      icon: "h-4 w-4",
      text: "text-sm",
    },
    lg: {
      button: "px-4 py-3 text-base",
      icon: "h-5 w-5",
      text: "text-base",
    },
  };

  const config = sizeConfig[size];

  const handlePlay = useCallback(async () => {
    if (isPlaying && audioRef) {
      audioRef.pause();
      audioRef.currentTime = 0;
      setIsPlaying(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Request pronunciation from TTS endpoint
      const response = await fetch(ttsEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: textGa || text,
          dialect: currentDialect,
          language: "ga",
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate pronunciation");
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      audio.onplay = () => {
        setIsPlaying(true);
        onPlay?.();
      };

      audio.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
        onEnd?.();
      };

      audio.onerror = () => {
        setError("Playback failed");
        setIsPlaying(false);
      };

      setAudioRef(audio);
      await audio.play();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Pronunciation failed");
    } finally {
      setIsLoading(false);
    }
  }, [text, textGa, currentDialect, ttsEndpoint, isPlaying, audioRef, onPlay, onEnd]);

  const handleDialectChange = useCallback(
    (newDialect: IrishDialect) => {
      setCurrentDialect(newDialect);
      onDialectChange?.(newDialect);
    },
    [onDialectChange]
  );

  return (
    <div
      className="inline-flex flex-col bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden"
      data-component-id={componentId}
    >
      {/* Main content */}
      <div className="flex items-center gap-3 p-3">
        {/* Play button */}
        <button
          onClick={handlePlay}
          disabled={isLoading}
          className={`flex items-center justify-center rounded-full transition-colors ${
            isPlaying
              ? "bg-blue-100 text-blue-600"
              : "bg-gray-100 text-gray-600 hover:bg-blue-50 hover:text-blue-600"
          } ${isLoading ? "opacity-50 cursor-not-allowed" : ""} p-2`}
          title={isPlaying ? "Stop" : "Play pronunciation"}
        >
          {isLoading ? (
            <Loader2 className={`${config.icon} animate-spin`} />
          ) : isPlaying ? (
            <VolumeX className={config.icon} />
          ) : (
            <Volume2 className={config.icon} />
          )}
        </button>

        {/* Text content */}
        <div className="flex-1 min-w-0">
          <p className={`font-medium text-gray-900 ${config.text}`}>
            {textGa || text}
          </p>
          {textEn && (
            <p className="text-xs text-gray-500 mt-0.5">{textEn}</p>
          )}
          {phonetic && (
            <p className="text-xs text-gray-400 font-mono mt-0.5">
              /{phonetic}/
            </p>
          )}
        </div>

        {/* Dismiss button */}
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
            title="Dismiss"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Dialect selector */}
      {isIrish && (
        <div className="border-t border-gray-100 px-3 py-2 bg-gray-50">
          <div className="flex items-center gap-1">
            <span className="text-xs text-gray-500 mr-2">Dialect:</span>
            {(Object.keys(dialectLabels) as IrishDialect[]).map((d) => (
              <button
                key={d}
                onClick={() => handleDialectChange(d)}
                className={`px-2 py-0.5 text-xs rounded transition-colors ${
                  currentDialect === d
                    ? "bg-green-100 text-green-700 font-medium"
                    : "bg-white border border-gray-200 text-gray-600 hover:border-green-300"
                }`}
                title={dialectLabels[d].region}
              >
                {dialectLabels[d].label}
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

export default PronunciationButton;
