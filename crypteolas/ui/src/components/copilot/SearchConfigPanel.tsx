/**
 * SearchConfigPanel - Search configuration controls.
 *
 * Allows users to adjust search parameters:
 * - Similarity threshold
 * - Max chunks
 * - Source filters
 * - Protocol filters
 * - Search mode
 */

import { Filter, Settings2, SlidersHorizontal } from "lucide-react";
import { useState } from "react";
import type { SearchConfig } from "../../lib/types";

interface SearchConfigPanelProps {
  config: SearchConfig;
  onChange: (updates: Partial<SearchConfig>) => void;
  availableProtocols?: string[];
  availableLanguages?: string[];
  collapsed?: boolean;
}

const SOURCE_TYPES = [
  { id: "protocol_docs", label: "Protocol Docs" },
  { id: "user_url", label: "User URLs" },
  { id: "github", label: "GitHub" },
  { id: "local", label: "Local Files" },
];

const SEARCH_MODES = [
  { id: "hybrid", label: "Hybrid", description: "Vector + keyword search" },
  { id: "vector", label: "Vector", description: "Semantic similarity only" },
  { id: "fts", label: "Full-Text", description: "Keyword search only" },
];

export function SearchConfigPanel({
  config,
  onChange,
  availableProtocols = [],
  availableLanguages = [],
  collapsed = true,
}: SearchConfigPanelProps) {
  const [isExpanded, setIsExpanded] = useState(!collapsed);

  return (
    <div className="border rounded-lg bg-card">
      {/* Header */}
      <button
        className="w-full flex items-center justify-between p-3 hover:bg-muted/50"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <SlidersHorizontal size={16} className="text-muted-foreground" />
          <span className="font-medium text-sm">Search Settings</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>Threshold: {(config.similarity_threshold * 100).toFixed(0)}%</span>
          <span>Max: {config.max_chunks}</span>
          <Settings2
            size={14}
            className={`transform transition-transform ${isExpanded ? "rotate-90" : ""}`}
          />
        </div>
      </button>

      {/* Expanded content */}
      {isExpanded && (
        <div className="px-3 pb-3 border-t space-y-4">
          {/* Similarity threshold slider */}
          <div className="pt-3">
            <label className="flex items-center justify-between text-sm">
              <span>Similarity Threshold</span>
              <span className="text-muted-foreground">
                {(config.similarity_threshold * 100).toFixed(0)}%
              </span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={config.similarity_threshold * 100}
              onChange={(e) =>
                onChange({ similarity_threshold: Number(e.target.value) / 100 })
              }
              className="w-full h-2 mt-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
            />
            <div className="flex justify-between text-xs text-muted-foreground mt-1">
              <span>More results</span>
              <span>Higher relevance</span>
            </div>
          </div>

          {/* Max chunks */}
          <div>
            <label className="flex items-center justify-between text-sm">
              <span>Max Chunks</span>
              <span className="text-muted-foreground">{config.max_chunks}</span>
            </label>
            <input
              type="range"
              min="1"
              max="50"
              value={config.max_chunks}
              onChange={(e) => onChange({ max_chunks: Number(e.target.value) })}
              className="w-full h-2 mt-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
            />
          </div>

          {/* Search mode */}
          <div>
            <label className="text-sm mb-2 block">Search Mode</label>
            <div className="grid grid-cols-3 gap-2">
              {SEARCH_MODES.map((mode) => (
                <button
                  key={mode.id}
                  onClick={() =>
                    onChange({ search_mode: mode.id as SearchConfig["search_mode"] })
                  }
                  className={`p-2 text-center rounded border text-xs ${
                    config.search_mode === mode.id
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border hover:bg-muted"
                  }`}
                >
                  <div className="font-medium">{mode.label}</div>
                  <div className="text-muted-foreground text-[10px] mt-0.5">
                    {mode.description}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Include code toggle */}
          <div className="flex items-center justify-between">
            <label className="text-sm">Include Code Search</label>
            <button
              onClick={() => onChange({ include_code: !config.include_code })}
              className={`relative w-10 h-5 rounded-full transition-colors ${
                config.include_code ? "bg-primary" : "bg-muted"
              }`}
            >
              <span
                className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                  config.include_code ? "translate-x-5" : "translate-x-0.5"
                }`}
              />
            </button>
          </div>

          {/* Source filters */}
          <div>
            <label className="flex items-center gap-2 text-sm mb-2">
              <Filter size={14} />
              Source Types
            </label>
            <div className="flex flex-wrap gap-2">
              {SOURCE_TYPES.map((source) => {
                const isActive =
                  config.source_filter.length === 0 ||
                  config.source_filter.includes(source.id);
                return (
                  <button
                    key={source.id}
                    onClick={() => {
                      if (config.source_filter.includes(source.id)) {
                        onChange({
                          source_filter: config.source_filter.filter(
                            (s) => s !== source.id
                          ),
                        });
                      } else {
                        onChange({
                          source_filter: [...config.source_filter, source.id],
                        });
                      }
                    }}
                    className={`px-2 py-1 text-xs rounded border ${
                      isActive
                        ? "border-primary bg-primary/10 text-primary"
                        : "border-border text-muted-foreground hover:bg-muted"
                    }`}
                  >
                    {source.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Protocol filters */}
          {availableProtocols.length > 0 && (
            <div>
              <label className="text-sm mb-2 block">Protocol Filter</label>
              <div className="flex flex-wrap gap-2">
                {availableProtocols.map((protocol) => {
                  const isActive = config.protocol_filter.includes(protocol);
                  return (
                    <button
                      key={protocol}
                      onClick={() => {
                        if (isActive) {
                          onChange({
                            protocol_filter: config.protocol_filter.filter(
                              (p) => p !== protocol
                            ),
                          });
                        } else {
                          onChange({
                            protocol_filter: [...config.protocol_filter, protocol],
                          });
                        }
                      }}
                      className={`px-2 py-1 text-xs rounded border ${
                        isActive
                          ? "border-primary bg-primary/10 text-primary"
                          : "border-border text-muted-foreground hover:bg-muted"
                      }`}
                    >
                      {protocol}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Language filters */}
          {availableLanguages.length > 0 && (
            <div>
              <label className="text-sm mb-2 block">Language Filter</label>
              <div className="flex flex-wrap gap-2">
                {availableLanguages.map((lang) => {
                  const isActive = config.language_filter.includes(lang);
                  return (
                    <button
                      key={lang}
                      onClick={() => {
                        if (isActive) {
                          onChange({
                            language_filter: config.language_filter.filter(
                              (l) => l !== lang
                            ),
                          });
                        } else {
                          onChange({
                            language_filter: [...config.language_filter, lang],
                          });
                        }
                      }}
                      className={`px-2 py-1 text-xs rounded border ${
                        isActive
                          ? "border-primary bg-primary/10 text-primary"
                          : "border-border text-muted-foreground hover:bg-muted"
                      }`}
                    >
                      {lang}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Reset button */}
          <button
            onClick={() =>
              onChange({
                similarity_threshold: 0.7,
                max_chunks: 10,
                source_filter: [],
                protocol_filter: [],
                language_filter: [],
                search_mode: "hybrid",
                include_code: true,
              })
            }
            className="w-full py-1.5 text-xs text-muted-foreground hover:text-foreground border rounded"
          >
            Reset to Defaults
          </button>
        </div>
      )}
    </div>
  );
}
