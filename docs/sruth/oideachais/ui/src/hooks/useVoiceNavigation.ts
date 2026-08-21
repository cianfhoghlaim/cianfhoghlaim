/**
 * useVoiceNavigation Hook.
 *
 * Voice command recognition for curriculum navigation.
 * Uses browser Speech Recognition API with ElevenLabs fallback potential.
 */

import { useState, useCallback, useEffect, useRef } from "react";

// ============================================================================
// Types
// ============================================================================

export type VoiceCommand =
  | "search"
  | "navigate"
  | "read"
  | "pronounce"
  | "help"
  | "stop"
  | "unknown";

export interface ParsedCommand {
  command: VoiceCommand;
  args: string[];
  rawText: string;
  confidence: number;
}

export interface VoiceNavigationOptions {
  /** Language for recognition */
  language?: "en" | "ga";
  /** Enable continuous listening */
  continuous?: boolean;
  /** Custom command patterns */
  commands?: Record<string, RegExp[]>;
  /** Callback when command is recognized */
  onCommand?: (command: ParsedCommand) => void;
  /** Callback for search commands */
  onSearch?: (query: string) => void;
  /** Callback for navigation commands */
  onNavigate?: (destination: string) => void;
  /** Callback for read commands */
  onRead?: () => void;
  /** Callback for pronunciation commands */
  onPronounce?: (word: string) => void;
  /** Callback for help commands */
  onHelp?: () => void;
}

export interface UseVoiceNavigationReturn {
  /** Start listening */
  startListening: () => void;
  /** Stop listening */
  stopListening: () => void;
  /** Toggle listening */
  toggleListening: () => void;
  /** Whether currently listening */
  isListening: boolean;
  /** Whether speech recognition is supported */
  isSupported: boolean;
  /** Current transcript (interim) */
  transcript: string;
  /** Last recognized command */
  lastCommand: ParsedCommand | null;
  /** Error message */
  error: string | null;
}

// ============================================================================
// Default Command Patterns
// ============================================================================

const DEFAULT_COMMANDS: Record<VoiceCommand, RegExp[]> = {
  search: [
    /^search(?:\s+for)?\s+(.+)$/i,
    /^find\s+(.+)$/i,
    /^look(?:\s+for)?\s+(.+)$/i,
    /^show\s+me\s+(.+)$/i,
  ],
  navigate: [
    /^go\s+to\s+(.+)$/i,
    /^open\s+(.+)$/i,
    /^navigate\s+to\s+(.+)$/i,
  ],
  read: [
    /^read(?:\s+this)?(?:\s+aloud)?$/i,
    /^read\s+(?:the\s+)?content$/i,
    /^speak$/i,
  ],
  pronounce: [
    /^pronounce\s+(.+)$/i,
    /^how\s+do\s+(?:you\s+)?say\s+(.+)$/i,
    /^say\s+(.+)$/i,
  ],
  help: [
    /^help$/i,
    /^what\s+can\s+(?:you|I)\s+(?:do|say)$/i,
    /^commands$/i,
  ],
  stop: [
    /^stop$/i,
    /^cancel$/i,
    /^never\s*mind$/i,
  ],
  unknown: [],
};

// ============================================================================
// Speech Recognition Types
// ============================================================================

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  isFinal: boolean;
  length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: Event) => void) | null;
  onend: (() => void) | null;
  onstart: (() => void) | null;
}

declare global {
  interface Window {
    SpeechRecognition?: new () => SpeechRecognition;
    webkitSpeechRecognition?: new () => SpeechRecognition;
  }
}

// ============================================================================
// Hook Implementation
// ============================================================================

export function useVoiceNavigation(
  options: VoiceNavigationOptions = {}
): UseVoiceNavigationReturn {
  const {
    language = "en",
    continuous = false,
    commands = DEFAULT_COMMANDS,
    onCommand,
    onSearch,
    onNavigate,
    onRead,
    onPronounce,
    onHelp,
  } = options;

  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const [transcript, setTranscript] = useState("");
  const [lastCommand, setLastCommand] = useState<ParsedCommand | null>(null);
  const [error, setError] = useState<string | null>(null);

  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // Check browser support
  useEffect(() => {
    const SpeechRecognitionAPI =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    setIsSupported(!!SpeechRecognitionAPI);
  }, []);

  // Parse command from text
  const parseCommand = useCallback(
    (text: string, confidence: number): ParsedCommand => {
      const normalizedText = text.trim().toLowerCase();

      for (const [commandType, patterns] of Object.entries(commands)) {
        for (const pattern of patterns) {
          const match = normalizedText.match(pattern);
          if (match) {
            return {
              command: commandType as VoiceCommand,
              args: match.slice(1).filter(Boolean),
              rawText: text,
              confidence,
            };
          }
        }
      }

      return {
        command: "unknown",
        args: [text],
        rawText: text,
        confidence,
      };
    },
    [commands]
  );

  // Handle recognized command
  const handleCommand = useCallback(
    (parsed: ParsedCommand) => {
      setLastCommand(parsed);
      onCommand?.(parsed);

      switch (parsed.command) {
        case "search":
          onSearch?.(parsed.args[0] || "");
          break;
        case "navigate":
          onNavigate?.(parsed.args[0] || "");
          break;
        case "read":
          onRead?.();
          break;
        case "pronounce":
          onPronounce?.(parsed.args[0] || "");
          break;
        case "help":
          onHelp?.();
          break;
        case "stop":
          stopListening();
          break;
        default:
          // Unknown command - could trigger a search as fallback
          if (parsed.rawText && onSearch) {
            onSearch(parsed.rawText);
          }
      }
    },
    [onCommand, onSearch, onNavigate, onRead, onPronounce, onHelp]
  );

  // Start listening
  const startListening = useCallback(() => {
    const SpeechRecognitionAPI =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognitionAPI) {
      setError("Speech recognition not supported");
      return;
    }

    const recognition = new SpeechRecognitionAPI();
    recognitionRef.current = recognition;

    recognition.continuous = continuous;
    recognition.interimResults = true;
    recognition.lang = language === "ga" ? "ga-IE" : "en-US";

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
      setTranscript("");
    };

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let finalTranscript = "";
      let interimTranscript = "";
      let confidence = 0;

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += result[0].transcript;
          confidence = result[0].confidence;
        } else {
          interimTranscript += result[0].transcript;
        }
      }

      setTranscript(interimTranscript || finalTranscript);

      if (finalTranscript) {
        const parsed = parseCommand(finalTranscript, confidence);
        handleCommand(parsed);
      }
    };

    recognition.onerror = (event: Event) => {
      const errorEvent = event as Event & { error?: string };
      setError(errorEvent.error || "Recognition error");
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
      if (continuous && recognitionRef.current === recognition) {
        // Restart if continuous mode
        setTimeout(() => {
          try {
            recognition.start();
          } catch {
            // Ignore if already started
          }
        }, 100);
      }
    };

    recognition.start();
  }, [language, continuous, parseCommand, handleCommand]);

  // Stop listening
  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsListening(false);
  }, []);

  // Toggle listening
  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  return {
    startListening,
    stopListening,
    toggleListening,
    isListening,
    isSupported,
    transcript,
    lastCommand,
    error,
  };
}

/**
 * Available voice commands for help display.
 */
export const VOICE_COMMANDS_HELP = [
  { command: "Search for [topic]", description: "Search curriculum documents" },
  { command: "Go to [page]", description: "Navigate to a section" },
  { command: "Read this", description: "Read current content aloud" },
  { command: "Pronounce [word]", description: "Hear Irish pronunciation" },
  { command: "Help", description: "Show available commands" },
  { command: "Stop", description: "Stop listening" },
];

export default useVoiceNavigation;
