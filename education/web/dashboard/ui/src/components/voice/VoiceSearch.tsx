/**
 * VoiceSearch - Voice Component.
 *
 * Voice input for curriculum search using browser speech recognition
 * or ElevenLabs STT.
 */

import { useState, useCallback, useEffect, useRef } from "react";
import { Mic, MicOff, Loader2, X, Search } from "lucide-react";

// ============================================================================
// Types
// ============================================================================

export interface VoiceSearchProps {
  /** Callback when search is submitted */
  onSearch: (query: string) => void;
  /** Placeholder text */
  placeholder?: string;
  /** Initial value */
  value?: string;
  /** Language for speech recognition */
  language?: "en" | "ga";
  /** Enable continuous listening */
  continuous?: boolean;
  /** Show transcript preview */
  showTranscript?: boolean;
  /** Size variant */
  size?: "sm" | "md" | "lg";
  /** Disabled state */
  disabled?: boolean;
  /** Custom class name */
  className?: string;
}

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
// Component
// ============================================================================

export function VoiceSearch({
  onSearch,
  placeholder = "Search curriculum...",
  value = "",
  language = "en",
  continuous = false,
  showTranscript = true,
  size = "md",
  disabled = false,
  className = "",
}: VoiceSearchProps) {
  const [inputValue, setInputValue] = useState(value);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSupported, setIsSupported] = useState(true);

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Check browser support
  useEffect(() => {
    const SpeechRecognitionAPI =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    setIsSupported(!!SpeechRecognitionAPI);
  }, []);

  // Initialize speech recognition
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

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += result[0].transcript;
        } else {
          interimTranscript += result[0].transcript;
        }
      }

      if (finalTranscript) {
        setInputValue((prev) => (prev + " " + finalTranscript).trim());
        setTranscript("");
      } else {
        setTranscript(interimTranscript);
      }
    };

    recognition.onerror = (event: Event) => {
      const errorEvent = event as Event & { error?: string };
      setError(errorEvent.error || "Recognition error");
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
      if (transcript) {
        setInputValue((prev) => (prev + " " + transcript).trim());
        setTranscript("");
      }
    };

    recognition.start();
  }, [language, continuous, transcript]);

  // Stop listening
  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
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

  // Handle form submit
  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (inputValue.trim()) {
        onSearch(inputValue.trim());
      }
    },
    [inputValue, onSearch]
  );

  // Clear input
  const handleClear = useCallback(() => {
    setInputValue("");
    setTranscript("");
    inputRef.current?.focus();
  }, []);

  // Size configurations
  const sizeConfig = {
    sm: {
      input: "py-1.5 pl-8 pr-20 text-sm",
      icon: "h-4 w-4",
      button: "p-1.5",
    },
    md: {
      input: "py-2.5 pl-10 pr-24 text-base",
      icon: "h-5 w-5",
      button: "p-2",
    },
    lg: {
      input: "py-3 pl-12 pr-28 text-lg",
      icon: "h-6 w-6",
      button: "p-2.5",
    },
  };

  const config = sizeConfig[size];

  return (
    <form onSubmit={handleSubmit} className={`relative ${className}`}>
      {/* Search icon */}
      <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
        <Search className={config.icon} />
      </div>

      {/* Input */}
      <input
        ref={inputRef}
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className={`w-full rounded-lg border border-gray-300 bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors ${config.input} ${
          disabled ? "opacity-50 cursor-not-allowed" : ""
        }`}
      />

      {/* Interim transcript overlay */}
      {showTranscript && transcript && (
        <div className="absolute left-10 right-24 top-1/2 -translate-y-1/2 text-gray-400 italic truncate pointer-events-none">
          {transcript}
        </div>
      )}

      {/* Action buttons */}
      <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
        {/* Clear button */}
        {inputValue && (
          <button
            type="button"
            onClick={handleClear}
            className={`${config.button} rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors`}
            title="Clear"
          >
            <X className={config.icon} />
          </button>
        )}

        {/* Voice button */}
        {isSupported && (
          <button
            type="button"
            onClick={toggleListening}
            disabled={disabled}
            className={`${config.button} rounded-full transition-colors ${
              isListening
                ? "bg-red-100 text-red-600 animate-pulse"
                : "text-gray-400 hover:text-blue-600 hover:bg-blue-50"
            } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
            title={isListening ? "Stop listening" : "Start voice search"}
          >
            {isListening ? (
              <MicOff className={config.icon} />
            ) : (
              <Mic className={config.icon} />
            )}
          </button>
        )}

        {/* Submit button */}
        <button
          type="submit"
          disabled={disabled || !inputValue.trim()}
          className={`${config.button} rounded-full bg-blue-600 text-white hover:bg-blue-700 transition-colors ${
            disabled || !inputValue.trim() ? "opacity-50 cursor-not-allowed" : ""
          }`}
          title="Search"
        >
          <Search className={config.icon} />
        </button>
      </div>

      {/* Error message */}
      {error && (
        <p className="absolute left-0 -bottom-6 text-xs text-red-600">
          {error}
        </p>
      )}
    </form>
  );
}

export default VoiceSearch;
