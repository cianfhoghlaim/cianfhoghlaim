/**
 * useIrishTTS Hook.
 *
 * Provides Irish pronunciation via Chatterbox TTS backend.
 * Supports dialect selection and audio caching.
 */

import { useState, useCallback, useRef, useMemo } from "react";

// ============================================================================
// Types
// ============================================================================

export type IrishDialect = "connacht" | "munster" | "ulster" | "standard";

export interface DialectInfo {
  id: IrishDialect;
  name: string;
  region: string;
  description: string;
}

export interface UseIrishTTSOptions {
  /** API endpoint for TTS */
  endpoint?: string;
  /** Default dialect */
  defaultDialect?: IrishDialect;
  /** Enable audio caching */
  enableCache?: boolean;
  /** Cache size limit */
  maxCacheSize?: number;
  /** Callback when playback starts */
  onPlay?: () => void;
  /** Callback when playback ends */
  onEnd?: () => void;
  /** Callback on error */
  onError?: (error: string) => void;
}

export interface UseIrishTTSReturn {
  /** Pronounce text */
  pronounce: (text: string, dialect?: IrishDialect) => Promise<void>;
  /** Stop current playback */
  stop: () => void;
  /** Whether currently playing */
  isPlaying: boolean;
  /** Whether loading audio */
  isLoading: boolean;
  /** Current error */
  error: string | null;
  /** Current dialect */
  dialect: IrishDialect;
  /** Set dialect */
  setDialect: (dialect: IrishDialect) => void;
  /** Available dialects */
  dialects: DialectInfo[];
  /** Clear audio cache */
  clearCache: () => void;
  /** Prefetch audio for text */
  prefetch: (text: string, dialect?: IrishDialect) => Promise<void>;
}

// ============================================================================
// Constants
// ============================================================================

export const DIALECTS: DialectInfo[] = [
  {
    id: "connacht",
    name: "Connacht",
    region: "West (Galway, Mayo)",
    description: "Western Irish dialect",
  },
  {
    id: "munster",
    name: "Munster",
    region: "South (Cork, Kerry)",
    description: "Southern Irish dialect",
  },
  {
    id: "ulster",
    name: "Ulster",
    region: "North (Donegal)",
    description: "Northern Irish dialect",
  },
  {
    id: "standard",
    name: "Standard",
    region: "Official",
    description: "An Caighdeán Oifigiúil",
  },
];

// ============================================================================
// Hook Implementation
// ============================================================================

export function useIrishTTS(options: UseIrishTTSOptions = {}): UseIrishTTSReturn {
  const {
    endpoint = "/api/tts",
    defaultDialect = "standard",
    enableCache = true,
    maxCacheSize = 50,
    onPlay,
    onEnd,
    onError,
  } = options;

  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dialect, setDialect] = useState<IrishDialect>(defaultDialect);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const cacheRef = useRef<Map<string, string>>(new Map());

  // Generate cache key
  const getCacheKey = useCallback((text: string, d: IrishDialect) => {
    return `${d}:${text.toLowerCase().trim()}`;
  }, []);

  // Fetch audio from API
  const fetchAudio = useCallback(
    async (text: string, d: IrishDialect): Promise<string> => {
      const cacheKey = getCacheKey(text, d);

      // Check cache
      if (enableCache && cacheRef.current.has(cacheKey)) {
        return cacheRef.current.get(cacheKey)!;
      }

      // Fetch from API
      const response = await fetch(`${endpoint}/pronounce`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          word: text,
          dialect: d,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to generate pronunciation");
      }

      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);

      // Cache the result
      if (enableCache) {
        // Evict old entries if cache is full
        if (cacheRef.current.size >= maxCacheSize) {
          const firstKey = cacheRef.current.keys().next().value;
          const oldUrl = cacheRef.current.get(firstKey);
          if (oldUrl) URL.revokeObjectURL(oldUrl);
          cacheRef.current.delete(firstKey);
        }
        cacheRef.current.set(cacheKey, audioUrl);
      }

      return audioUrl;
    },
    [endpoint, enableCache, maxCacheSize, getCacheKey]
  );

  // Pronounce text
  const pronounce = useCallback(
    async (text: string, d?: IrishDialect) => {
      const targetDialect = d ?? dialect;

      // Stop any current playback
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }

      setIsLoading(true);
      setError(null);

      try {
        const audioUrl = await fetchAudio(text, targetDialect);

        const audio = new Audio(audioUrl);
        audioRef.current = audio;

        audio.onplay = () => {
          setIsPlaying(true);
          onPlay?.();
        };

        audio.onended = () => {
          setIsPlaying(false);
          onEnd?.();
        };

        audio.onerror = () => {
          setIsPlaying(false);
          setError("Playback failed");
          onError?.("Playback failed");
        };

        await audio.play();
      } catch (err) {
        const message = err instanceof Error ? err.message : "Pronunciation failed";
        setError(message);
        onError?.(message);
      } finally {
        setIsLoading(false);
      }
    },
    [dialect, fetchAudio, onPlay, onEnd, onError]
  );

  // Stop playback
  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  }, []);

  // Clear cache
  const clearCache = useCallback(() => {
    cacheRef.current.forEach((url) => URL.revokeObjectURL(url));
    cacheRef.current.clear();
  }, []);

  // Prefetch audio
  const prefetch = useCallback(
    async (text: string, d?: IrishDialect) => {
      try {
        await fetchAudio(text, d ?? dialect);
      } catch {
        // Silently ignore prefetch errors
      }
    },
    [dialect, fetchAudio]
  );

  // Memoized dialects list
  const dialects = useMemo(() => DIALECTS, []);

  return {
    pronounce,
    stop,
    isPlaying,
    isLoading,
    error,
    dialect,
    setDialect,
    dialects,
    clearCache,
    prefetch,
  };
}

/**
 * Simplified hook for single-word pronunciation.
 */
export function usePronunciation(word: string, options?: UseIrishTTSOptions) {
  const { pronounce, isPlaying, isLoading, error, dialect, setDialect, dialects } =
    useIrishTTS(options);

  const play = useCallback(() => {
    pronounce(word);
  }, [pronounce, word]);

  return {
    play,
    isPlaying,
    isLoading,
    error,
    dialect,
    setDialect,
    dialects,
  };
}

export default useIrishTTS;
