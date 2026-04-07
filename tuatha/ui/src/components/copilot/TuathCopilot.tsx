/**
 * TuathCopilot - Main CopilotKit integration component
 *
 * Combines useCoAgent hook with A2UI components for the Celtic MMO
 */

import { FormEvent, useRef, useState } from 'react';
import {
  useCoAgent,
  useCoAgentStateRender,
  type AgentState,
} from '../../hooks/useCoAgent';
import {
  A2UIRenderer,
  XPIndicator,
  ToolCallIndicator,
} from './A2UIComponents';

interface TuathCopilotProps {
  sessionId?: string;
  paymentId?: string;
  language?: string;
  languageLevel?: string;
  currentQuest?: string;
  currentZone?: string;
  onPaymentRequired?: () => void;
}

export function TuathCopilot({
  sessionId,
  paymentId,
  language = 'ga',
  languageLevel = 'beginner',
  currentQuest,
  currentZone,
  onPaymentRequired,
}: TuathCopilotProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  const {
    isLoading,
    isStreaming,
    error,
    agentState,
    messages,
    streamingContent,
    sidebarComponents,
    mainComponents,
    overlayComponents,
    activeToolCalls,
    sendMessage,
    reset,
  } = useCoAgent({
    agentEndpoint: '/api/copilot/agent',
    sessionId,
    paymentId,
    language,
    languageLevel,
    context: {
      current_quest: currentQuest,
      current_zone: currentZone,
    },
  });

  // Handle payment required error
  if (error === 'Payment required' && onPaymentRequired) {
    onPaymentRequired();
  }

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const input = inputRef.current;
    if (!input || !input.value.trim()) return;

    sendMessage(input.value.trim());
    input.value = '';
  };

  // Render agent state with useCoAgentStateRender
  const stateIndicator = useCoAgentStateRender(agentState, (state: AgentState) => (
    <XPIndicator
      xp={state.xpEarned}
      vocabularyCount={state.vocabularyLearned.length}
    />
  ));

  // Scroll to bottom when new content arrives
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div
      className={`fixed bottom-4 right-4 flex flex-col transition-all duration-300 ${
        isExpanded ? 'w-[800px] h-[600px]' : 'w-80 h-[500px]'
      }`}
    >
      {/* Overlay Components (e.g., map markers) */}
      {overlayComponents.length > 0 && (
        <div className="absolute -top-20 right-0 left-0 z-10">
          <A2UIRenderer components={overlayComponents} slot="overlay" />
        </div>
      )}

      {/* Main Container */}
      <div className="bg-slate-900 border border-slate-700 rounded-xl shadow-2xl flex flex-col h-full overflow-hidden">
        {/* Header */}
        <div className="bg-slate-800 px-4 py-3 flex items-center justify-between border-b border-slate-700">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-emerald-600 rounded-full flex items-center justify-center">
              <CelticKnotIcon />
            </div>
            <div>
              <h3 className="font-bold text-white">Tuath Guide</h3>
              <p className="text-xs text-slate-400">
                {agentState?.agentType?.replace(/_/g, ' ') || 'Celtic Assistant'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {stateIndicator}

            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-700"
            >
              {isExpanded ? <CollapseIcon /> : <ExpandIcon />}
            </button>

            <button
              onClick={reset}
              className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-700"
              title="New conversation"
            >
              <ResetIcon />
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex flex-1 overflow-hidden">
          {/* Messages */}
          <div className={`flex-1 flex flex-col overflow-hidden ${isExpanded ? 'w-2/3' : 'w-full'}`}>
            {/* Tool Call Indicators */}
            {activeToolCalls.size > 0 && (
              <div className="px-4 py-2 border-b border-slate-700 space-y-1">
                {Array.from(activeToolCalls.values()).map((tool) => (
                  <ToolCallIndicator
                    key={tool.toolId}
                    toolName={tool.toolName}
                    status={tool.status}
                    parameters={tool.parameters}
                  />
                ))}
              </div>
            )}

            {/* Main Render Components */}
            {mainComponents.length > 0 && (
              <div className="px-4 py-2 border-b border-slate-700">
                <A2UIRenderer components={mainComponents} slot="main" />
              </div>
            )}

            {/* Messages List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 && !streamingContent && (
                <div className="text-center text-slate-500 py-8">
                  <p className="mb-2">Dia duit! Welcome to Tuath.</p>
                  <p className="text-sm">Ask me about:</p>
                  <div className="flex flex-wrap justify-center gap-2 mt-3">
                    <SuggestionButton
                      text="Learn Irish greetings"
                      onClick={() => sendMessage('Teach me basic Irish greetings')}
                    />
                    <SuggestionButton
                      text="Quest help"
                      onClick={() => sendMessage('Help me with my current quest')}
                    />
                    <SuggestionButton
                      text="Celtic mythology"
                      onClick={() => sendMessage('Tell me about the Tuatha Dé Danann')}
                    />
                  </div>
                </div>
              )}

              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-2 ${
                      msg.role === 'user'
                        ? 'bg-emerald-600 text-white'
                        : 'bg-slate-800 text-slate-200'
                    }`}
                  >
                    <MessageContent content={msg.content} />
                  </div>
                </div>
              ))}

              {/* Streaming Content */}
              {streamingContent && (
                <div className="flex justify-start">
                  <div className="max-w-[80%] rounded-lg px-4 py-2 bg-slate-800 text-slate-200">
                    <MessageContent content={streamingContent} />
                    <span className="inline-block w-2 h-4 bg-emerald-500 animate-pulse ml-1" />
                  </div>
                </div>
              )}

              {/* Error Display */}
              {error && error !== 'Payment required' && (
                <div className="bg-red-900/30 border border-red-700 rounded-lg p-3 text-red-300 text-sm">
                  {error}
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form
              onSubmit={handleSubmit}
              className="p-4 border-t border-slate-700"
            >
              <div className="flex gap-2">
                <input
                  ref={inputRef}
                  type="text"
                  placeholder="Ask about Irish, quests, or mythology..."
                  className="flex-1 bg-slate-800 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 text-white rounded-lg transition-colors"
                >
                  {isLoading ? (
                    <LoadingSpinner />
                  ) : (
                    <SendIcon />
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Sidebar (expanded mode only) */}
          {isExpanded && sidebarComponents.length > 0 && (
            <div className="w-1/3 border-l border-slate-700 p-4 overflow-y-auto space-y-4">
              <A2UIRenderer components={sidebarComponents} slot="sidebar" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Message content with basic markdown rendering
function MessageContent({ content }: { content: string }) {
  // Simple markdown rendering for bold, italic, and code
  const parts = content.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g);

  return (
    <div className="prose prose-invert prose-sm max-w-none">
      {parts.map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={i}>{part.slice(2, -2)}</strong>;
        }
        if (part.startsWith('*') && part.endsWith('*')) {
          return <em key={i}>{part.slice(1, -1)}</em>;
        }
        if (part.startsWith('`') && part.endsWith('`')) {
          return (
            <code key={i} className="bg-slate-700 px-1 rounded">
              {part.slice(1, -1)}
            </code>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </div>
  );
}

// Suggestion button
function SuggestionButton({
  text,
  onClick,
}: {
  text: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="px-3 py-1 text-sm bg-slate-800 border border-slate-600 rounded-full text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
    >
      {text}
    </button>
  );
}

// Icons
function CelticKnotIcon() {
  return (
    <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2a10 10 0 100 20 10 10 0 000-20zm0 18a8 8 0 110-16 8 8 0 010 16zm0-14a6 6 0 100 12 6 6 0 000-12zm0 10a4 4 0 110-8 4 4 0 010 8z" />
    </svg>
  );
}

function SendIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
    </svg>
  );
}

function LoadingSpinner() {
  return (
    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
  );
}

function ExpandIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
    </svg>
  );
}

function CollapseIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
    </svg>
  );
}

function ResetIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
    </svg>
  );
}

export default TuathCopilot;
