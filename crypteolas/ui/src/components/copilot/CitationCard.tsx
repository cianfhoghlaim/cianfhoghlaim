/**
 * CitationCard - Source attribution display.
 *
 * Shows citations from approved chunks used in the response.
 * Supports linking to source documents and code locations.
 */

import {
  Code,
  ExternalLink,
  FileText,
  Github,
  Globe,
  Quote,
} from "lucide-react";
import type { Citation, RAGChunk } from "../../lib/types";

interface CitationCardProps {
  citation: Citation;
  index: number;
  onClick?: () => void;
}

export function CitationCard({ citation, index, onClick }: CitationCardProps) {
  const getSourceIcon = () => {
    if (citation.source.includes("github.com")) {
      return <Github size={14} />;
    }
    if (citation.source.startsWith("http")) {
      return <Globe size={14} />;
    }
    return <FileText size={14} />;
  };

  const isUrl = citation.source.startsWith("http");

  return (
    <div
      className={`border rounded-lg p-3 ${
        onClick ? "cursor-pointer hover:bg-muted/50" : ""
      }`}
      onClick={onClick}
    >
      {/* Header with citation number */}
      <div className="flex items-start gap-2">
        <span className="flex items-center justify-center w-5 h-5 text-xs font-bold bg-primary/10 text-primary rounded-full shrink-0">
          {index + 1}
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            {getSourceIcon()}
            <span className="font-medium text-sm truncate">
              {citation.title || extractDomain(citation.source)}
            </span>
          </div>
          <div className="text-xs text-muted-foreground mt-0.5 truncate">
            {citation.source}
          </div>
        </div>
        {isUrl && (
          <a
            href={citation.source}
            target="_blank"
            rel="noopener noreferrer"
            className="p-1 text-muted-foreground hover:text-primary"
            onClick={(e) => e.stopPropagation()}
          >
            <ExternalLink size={14} />
          </a>
        )}
      </div>

      {/* Text preview */}
      <div className="mt-2 flex items-start gap-2">
        <Quote size={12} className="text-muted-foreground mt-1 shrink-0" />
        <p className="text-xs text-muted-foreground line-clamp-2">
          {citation.text_preview}
        </p>
      </div>

      {/* Score indicator */}
      <div className="mt-2 flex items-center gap-2">
        <div className="flex-1 h-1 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-primary/50"
            style={{ width: `${citation.score * 100}%` }}
          />
        </div>
        <span className="text-[10px] text-muted-foreground">
          {(citation.score * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  );
}

interface CitationListProps {
  citations: Citation[];
  onCitationClick?: (citation: Citation) => void;
}

export function CitationList({ citations, onCitationClick }: CitationListProps) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
        <FileText size={14} />
        Sources ({citations.length})
      </h3>
      <div className="grid gap-2">
        {citations.map((citation, index) => (
          <CitationCard
            key={citation.chunk_id}
            citation={citation}
            index={index}
            onClick={onCitationClick ? () => onCitationClick(citation) : undefined}
          />
        ))}
      </div>
    </div>
  );
}

/**
 * Inline citation reference for use within text.
 */
interface CitationRefProps {
  index: number;
  onClick?: () => void;
}

export function CitationRef({ index, onClick }: CitationRefProps) {
  return (
    <button
      onClick={onClick}
      className="inline-flex items-center justify-center w-4 h-4 text-[10px] font-bold bg-primary/10 text-primary rounded-full hover:bg-primary/20"
    >
      {index + 1}
    </button>
  );
}

/**
 * Compact citation display for chat messages.
 */
interface InlineCitationsProps {
  citations: Citation[];
  onCitationClick?: (citation: Citation) => void;
}

export function InlineCitations({
  citations,
  onCitationClick,
}: InlineCitationsProps) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-wrap gap-1 mt-2">
      {citations.map((citation, index) => (
        <button
          key={citation.chunk_id}
          onClick={() => onCitationClick?.(citation)}
          className="flex items-center gap-1 px-2 py-0.5 text-xs bg-muted rounded hover:bg-muted/80"
          title={citation.source}
        >
          <span className="font-bold text-primary">[{index + 1}]</span>
          <span className="truncate max-w-24">
            {citation.title || extractDomain(citation.source)}
          </span>
        </button>
      ))}
    </div>
  );
}

// Helper to extract domain from URL
function extractDomain(url: string): string {
  try {
    if (url.startsWith("http")) {
      return new URL(url).hostname;
    }
    // For file paths, return the filename
    return url.split("/").pop() || url;
  } catch {
    return url;
  }
}

/**
 * Code citation card with syntax highlighting info.
 */
interface CodeCitationCardProps {
  chunk: RAGChunk;
  index: number;
  onClick?: () => void;
}

export function CodeCitationCard({
  chunk,
  index,
  onClick,
}: CodeCitationCardProps) {
  return (
    <div
      className={`border rounded-lg p-3 ${
        onClick ? "cursor-pointer hover:bg-muted/50" : ""
      }`}
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-start gap-2">
        <span className="flex items-center justify-center w-5 h-5 text-xs font-bold bg-primary/10 text-primary rounded-full shrink-0">
          {index + 1}
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <Code size={14} />
            <span className="font-medium text-sm truncate">{chunk.source}</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
            {chunk.language && (
              <span className="px-1.5 py-0.5 bg-muted rounded">
                {chunk.language}
              </span>
            )}
            {chunk.chunk_type && <span>{chunk.chunk_type}</span>}
            {chunk.start_line && chunk.end_line && (
              <span>
                Lines {chunk.start_line}-{chunk.end_line}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Code preview */}
      <pre className="mt-2 p-2 bg-muted/50 rounded text-xs overflow-x-auto font-mono">
        <code className="line-clamp-4">{chunk.text}</code>
      </pre>
    </div>
  );
}
