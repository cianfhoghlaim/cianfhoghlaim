/**
 * Search Results Component
 *
 * Displays search results from curriculum or document queries.
 * Rendered by agents via AG-UI GenerativeUI events.
 */

import { Search, FileText, ExternalLink } from "lucide-react";
import { cn } from "../../../lib/utils";
import type { AgentComponentProps } from "../ComponentRegistry";

interface SearchResult {
  id: string;
  title: string;
  snippet: string;
  score?: number;
  source?: string;
  url?: string;
  metadata?: Record<string, string>;
}

interface SearchResultsProps extends AgentComponentProps {
  query: string;
  results: SearchResult[];
  totalCount?: number;
  searchTime?: number;
}

export default function SearchResults({
  query,
  results,
  totalCount,
  searchTime,
}: SearchResultsProps) {
  return (
    <div className="rounded-lg border bg-card shadow-sm">
      {/* Header */}
      <div className="p-4 border-b bg-muted/50">
        <div className="flex items-center gap-2">
          <Search className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium">
            Results for "{query}"
          </span>
        </div>
        <div className="flex gap-4 mt-1 text-xs text-muted-foreground">
          {totalCount !== undefined && (
            <span>{totalCount} results found</span>
          )}
          {searchTime !== undefined && (
            <span>{searchTime.toFixed(2)}ms</span>
          )}
        </div>
      </div>

      {/* Results */}
      <div className="divide-y">
        {results.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-sm text-muted-foreground">
              No results found for your query.
            </p>
          </div>
        ) : (
          results.map((result) => (
            <div
              key={result.id}
              className="p-4 hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-start gap-3">
                <FileText className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                <div className="flex-1 space-y-1">
                  <div className="flex items-start justify-between gap-4">
                    <h4 className="text-sm font-medium leading-tight">
                      {result.title}
                    </h4>
                    {result.score !== undefined && (
                      <span className="text-xs text-muted-foreground flex-shrink-0">
                        {Math.round(result.score * 100)}% match
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {result.snippet}
                  </p>
                  <div className="flex flex-wrap items-center gap-2 pt-1">
                    {result.source && (
                      <span className="text-xs bg-muted px-2 py-0.5 rounded">
                        {result.source}
                      </span>
                    )}
                    {result.metadata &&
                      Object.entries(result.metadata).map(([key, value]) => (
                        <span
                          key={key}
                          className="text-xs text-muted-foreground"
                        >
                          {key}: {value}
                        </span>
                      ))}
                    {result.url && (
                      <a
                        href={result.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
                      >
                        View <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
