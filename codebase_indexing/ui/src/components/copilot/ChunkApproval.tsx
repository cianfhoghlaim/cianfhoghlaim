/**
 * ChunkApproval - Human-in-the-Loop chunk approval UI.
 *
 * Displays retrieved RAG chunks with approve/reject controls.
 * Supports bulk actions and individual chunk feedback.
 */

import {
  Check,
  CheckCheck,
  ChevronDown,
  ChevronUp,
  Code,
  ExternalLink,
  FileText,
  Github,
  Globe,
  X,
} from "lucide-react";
import { useState } from "react";
import type { RAGChunk } from "../../lib/types";

interface ChunkApprovalProps {
  chunks: RAGChunk[];
  approvedChunks: string[];
  rejectedChunks: string[];
  awaitingApproval: boolean;
  onApprove: (chunkId: string) => void;
  onReject: (chunkId: string, feedback?: string) => void;
  onApproveAll: () => void;
  onClear: () => void;
}

export function ChunkApproval({
  chunks,
  approvedChunks,
  rejectedChunks,
  awaitingApproval,
  onApprove,
  onReject,
  onApproveAll,
  onClear,
}: ChunkApprovalProps) {
  const [expandedChunks, setExpandedChunks] = useState<Set<string>>(new Set());

  const pendingCount = chunks.filter(
    (c) => !approvedChunks.includes(c.id) && !rejectedChunks.includes(c.id)
  ).length;

  const toggleExpand = (id: string) => {
    setExpandedChunks((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  if (chunks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-8">
        <FileText size={48} className="mb-4 opacity-50" />
        <p>No chunks retrieved yet</p>
        <p className="text-sm">Search results will appear here</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header with bulk actions */}
      <div className="flex items-center justify-between p-4 border-b bg-card">
        <div>
          <h2 className="font-semibold">Retrieved Chunks</h2>
          <p className="text-sm text-muted-foreground">
            {chunks.length} chunks found
            {pendingCount > 0 && ` (${pendingCount} pending)`}
          </p>
        </div>
        <div className="flex gap-2">
          {pendingCount > 0 && (
            <button
              onClick={onApproveAll}
              className="flex items-center gap-1 px-3 py-1.5 text-sm bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
            >
              <CheckCheck size={16} />
              Approve All
            </button>
          )}
          <button
            onClick={onClear}
            className="flex items-center gap-1 px-3 py-1.5 text-sm bg-secondary rounded-lg hover:bg-secondary/80"
          >
            Clear
          </button>
        </div>
      </div>

      {/* HITL status indicator */}
      {awaitingApproval && (
        <div className="px-4 py-2 bg-amber-500/10 border-b border-amber-500/20 text-amber-700 dark:text-amber-400 text-sm">
          Waiting for your approval to continue...
        </div>
      )}

      {/* Chunk list */}
      <div className="flex-1 overflow-auto p-4 space-y-3">
        {chunks.map((chunk) => (
          <ChunkCard
            key={chunk.id}
            chunk={chunk}
            isApproved={approvedChunks.includes(chunk.id)}
            isRejected={rejectedChunks.includes(chunk.id)}
            isExpanded={expandedChunks.has(chunk.id)}
            onToggleExpand={() => toggleExpand(chunk.id)}
            onApprove={() => onApprove(chunk.id)}
            onReject={(feedback) => onReject(chunk.id, feedback)}
          />
        ))}
      </div>
    </div>
  );
}

interface ChunkCardProps {
  chunk: RAGChunk;
  isApproved: boolean;
  isRejected: boolean;
  isExpanded: boolean;
  onToggleExpand: () => void;
  onApprove: () => void;
  onReject: (feedback?: string) => void;
}

function ChunkCard({
  chunk,
  isApproved,
  isRejected,
  isExpanded,
  onToggleExpand,
  onApprove,
  onReject,
}: ChunkCardProps) {
  const [showFeedbackInput, setShowFeedbackInput] = useState(false);
  const [feedback, setFeedback] = useState("");

  const handleReject = () => {
    if (showFeedbackInput && feedback.trim()) {
      onReject(feedback);
      setFeedback("");
      setShowFeedbackInput(false);
    } else if (!showFeedbackInput) {
      setShowFeedbackInput(true);
    } else {
      onReject();
      setShowFeedbackInput(false);
    }
  };

  const getSourceIcon = () => {
    switch (chunk.source_type) {
      case "github":
        return <Github size={14} />;
      case "user_url":
        return <Globe size={14} />;
      case "local":
        return chunk.language ? <Code size={14} /> : <FileText size={14} />;
      default:
        return <FileText size={14} />;
    }
  };

  const getStatusClasses = () => {
    if (isApproved) return "border-green-500/50 bg-green-500/5";
    if (isRejected) return "border-red-500/50 bg-red-500/5";
    return "border-border";
  };

  return (
    <div className={`border rounded-lg ${getStatusClasses()}`}>
      {/* Header */}
      <div
        className="flex items-start gap-3 p-3 cursor-pointer hover:bg-muted/50"
        onClick={onToggleExpand}
      >
        {/* Expand/collapse */}
        <button className="mt-0.5 text-muted-foreground">
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>

        {/* Source icon and info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 text-sm">
            {getSourceIcon()}
            <span className="font-medium truncate">
              {chunk.title || chunk.source}
            </span>
            {chunk.protocol && (
              <span className="px-1.5 py-0.5 text-xs bg-primary/10 text-primary rounded">
                {chunk.protocol}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
            <span className="capitalize">{chunk.source_type.replace("_", " ")}</span>
            <span>Score: {(chunk.score * 100).toFixed(0)}%</span>
            {chunk.language && <span>{chunk.language}</span>}
            {chunk.start_line && chunk.end_line && (
              <span>
                L{chunk.start_line}-{chunk.end_line}
              </span>
            )}
          </div>
        </div>

        {/* Status/Actions */}
        <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
          {isApproved ? (
            <span className="flex items-center gap-1 px-2 py-1 text-xs text-green-600 bg-green-500/10 rounded">
              <Check size={12} />
              Approved
            </span>
          ) : isRejected ? (
            <span className="flex items-center gap-1 px-2 py-1 text-xs text-red-600 bg-red-500/10 rounded">
              <X size={12} />
              Rejected
            </span>
          ) : (
            <>
              <button
                onClick={onApprove}
                className="p-1.5 text-green-600 hover:bg-green-500/10 rounded"
                title="Approve"
              >
                <Check size={16} />
              </button>
              <button
                onClick={handleReject}
                className="p-1.5 text-red-600 hover:bg-red-500/10 rounded"
                title="Reject"
              >
                <X size={16} />
              </button>
            </>
          )}
        </div>
      </div>

      {/* Expanded content */}
      {isExpanded && (
        <div className="px-3 pb-3 border-t">
          {/* Text preview */}
          <div className="mt-3">
            {chunk.language ? (
              <pre className="p-3 bg-muted/50 rounded text-xs overflow-x-auto font-mono">
                <code>{chunk.text}</code>
              </pre>
            ) : (
              <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                {chunk.text}
              </p>
            )}
          </div>

          {/* Source link */}
          {chunk.source.startsWith("http") && (
            <a
              href={chunk.source}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 mt-2 text-xs text-primary hover:underline"
            >
              Open source
              <ExternalLink size={12} />
            </a>
          )}
        </div>
      )}

      {/* Feedback input for rejection */}
      {showFeedbackInput && !isRejected && (
        <div className="px-3 pb-3 border-t" onClick={(e) => e.stopPropagation()}>
          <div className="flex gap-2 mt-2">
            <input
              type="text"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Why is this irrelevant? (optional)"
              className="flex-1 px-2 py-1 text-sm bg-muted rounded border focus:outline-none focus:ring-1 focus:ring-primary"
              autoFocus
            />
            <button
              onClick={handleReject}
              className="px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600"
            >
              Reject
            </button>
            <button
              onClick={() => setShowFeedbackInput(false)}
              className="px-2 py-1 text-xs bg-muted rounded hover:bg-muted/80"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Show rejection feedback if present */}
      {isRejected && chunk.feedback && (
        <div className="px-3 pb-3 text-xs text-muted-foreground italic">
          Feedback: {chunk.feedback}
        </div>
      )}
    </div>
  );
}
