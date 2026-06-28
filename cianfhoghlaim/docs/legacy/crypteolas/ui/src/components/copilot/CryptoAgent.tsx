/**
 * CryptoAgent - Main CopilotKit integration component for Crypteolas
 *
 * AI-powered assistant for DeFi protocol analysis and GitHub intelligence
 */

import { FormEvent, useRef, useState } from 'react';
import {
  useCoAgent,
  useCoAgentStateRender,
  type AgentState,
} from '../../hooks/useCoAgent';

interface CryptoAgentProps {
  sessionId?: string;
  currentProtocol?: string;
  currentRepo?: string;
  onPaymentRequired?: () => void;
}

export function CryptoAgent({
  sessionId,
  currentProtocol,
  currentRepo,
  onPaymentRequired,
}: CryptoAgentProps) {
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
    activeToolCalls,
    sendMessage,
    reset,
  } = useCoAgent({
    agentEndpoint: '/api/agent',
    sessionId,
    context: {
      current_protocol: currentProtocol,
      current_repo: currentRepo,
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

  // Render agent state
  const stateIndicator = useCoAgentStateRender(agentState, (state: AgentState) => (
    <AnalysisIndicator
      protocolCount={state.analyzedProtocols.length}
      repoCount={state.analyzedRepos.length}
      alertCount={state.riskAlerts.length}
    />
  ));

  return (
    <div
      className={`fixed bottom-4 right-4 flex flex-col transition-all duration-300 ${
        isExpanded ? 'w-[800px] h-[600px]' : 'w-96 h-[500px]'
      }`}
    >
      {/* Main Container */}
      <div className="bg-slate-900 border border-slate-700 rounded-xl shadow-2xl flex flex-col h-full overflow-hidden">
        {/* Header */}
        <div className="bg-slate-800 px-4 py-3 flex items-center justify-between border-b border-slate-700">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center">
              <CryptoIcon />
            </div>
            <div>
              <h3 className="font-bold text-white">Crypto Agent</h3>
              <p className="text-xs text-slate-400">
                {agentState?.agentType?.replace(/_/g, ' ') || 'DeFi Analyst'}
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
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Tool Call Indicators */}
            {activeToolCalls.size > 0 && (
              <div className="px-4 py-2 border-b border-slate-700 space-y-1">
                {Array.from(activeToolCalls.values()).map((tool) => (
                  <ToolCallIndicator
                    key={tool.toolId}
                    toolName={tool.toolName}
                    status={tool.status}
                  />
                ))}
              </div>
            )}

            {/* Messages List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 && !streamingContent && (
                <div className="text-center text-slate-500 py-8">
                  <p className="mb-2">Welcome to Crypto Agent</p>
                  <p className="text-sm">Ask me about:</p>
                  <div className="flex flex-wrap justify-center gap-2 mt-3">
                    <SuggestionButton
                      text="Analyze Aave V3"
                      onClick={() => sendMessage('Analyze the Aave V3 protocol: TVL, yields, and risks')}
                    />
                    <SuggestionButton
                      text="GitHub security"
                      onClick={() => sendMessage('Scan Uniswap v3-core for security issues')}
                    />
                    <SuggestionButton
                      text="Compare yields"
                      onClick={() => sendMessage('Compare lending yields between Aave, Compound, and Morpho')}
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
                        ? 'bg-indigo-600 text-white'
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
                    <span className="inline-block w-2 h-4 bg-indigo-500 animate-pulse ml-1" />
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
                  placeholder="Ask about protocols, yields, or smart contracts..."
                  className="flex-1 bg-slate-800 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 text-white rounded-lg transition-colors"
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
          {isExpanded && agentState && (
            <div className="w-1/3 border-l border-slate-700 p-4 overflow-y-auto space-y-4">
              {/* Insights */}
              {agentState.insights.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-indigo-300 mb-2">Insights</h4>
                  <ul className="space-y-2">
                    {agentState.insights.map((insight, i) => (
                      <li key={i} className="text-sm text-slate-400 flex gap-2">
                        <span className="text-emerald-400">•</span>
                        {insight}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Risk Alerts */}
              {agentState.riskAlerts.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-red-300 mb-2">Risk Alerts</h4>
                  <ul className="space-y-2">
                    {agentState.riskAlerts.map((alert, i) => (
                      <li key={i} className="text-sm text-red-400 flex gap-2">
                        <span>⚠️</span>
                        {alert}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Analyzed */}
              {(agentState.analyzedProtocols.length > 0 || agentState.analyzedRepos.length > 0) && (
                <div>
                  <h4 className="text-sm font-semibold text-slate-300 mb-2">Analyzed</h4>
                  <div className="flex flex-wrap gap-1">
                    {agentState.analyzedProtocols.map((p) => (
                      <span key={p} className="px-2 py-1 bg-indigo-900/50 text-indigo-300 rounded text-xs">
                        {p}
                      </span>
                    ))}
                    {agentState.analyzedRepos.map((r) => (
                      <span key={r} className="px-2 py-1 bg-violet-900/50 text-violet-300 rounded text-xs">
                        {r}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Analysis indicator
function AnalysisIndicator({
  protocolCount,
  repoCount,
  alertCount,
}: {
  protocolCount: number;
  repoCount: number;
  alertCount: number;
}) {
  if (protocolCount === 0 && repoCount === 0) return null;

  return (
    <div className="flex items-center gap-2 text-xs">
      {protocolCount > 0 && (
        <span className="px-2 py-1 bg-indigo-900/50 text-indigo-300 rounded">
          {protocolCount} protocols
        </span>
      )}
      {repoCount > 0 && (
        <span className="px-2 py-1 bg-violet-900/50 text-violet-300 rounded">
          {repoCount} repos
        </span>
      )}
      {alertCount > 0 && (
        <span className="px-2 py-1 bg-red-900/50 text-red-400 rounded">
          {alertCount} alerts
        </span>
      )}
    </div>
  );
}

// Tool call indicator
function ToolCallIndicator({
  toolName,
  status,
}: {
  toolName: string;
  status: string;
}) {
  const toolIcons: Record<string, string> = {
    protocol_search: '📊',
    github_analyze: '💻',
    tvl_query: '💰',
    risk_assess: '⚠️',
    contract_scan: '🔍',
  };

  return (
    <div className="flex items-center gap-2 text-xs text-slate-400">
      <span>{toolIcons[toolName] || '🔧'}</span>
      <span className="capitalize">{toolName.replace(/_/g, ' ')}</span>
      {status === 'running' && (
        <span className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      )}
      {status === 'complete' && <span className="text-emerald-400">✓</span>}
    </div>
  );
}

// Message content with markdown
function MessageContent({ content }: { content: string }) {
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
            <code key={i} className="bg-slate-700 px-1 rounded text-indigo-300">
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
function CryptoIcon() {
  return (
    <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93s3.05-7.44 7-7.93v15.86zm2-15.86c1.03.13 2 .45 2.87.93H13v-.93zM13 7h5.24c.25.31.48.65.68 1H13V7zm0 3h6.74c.08.33.15.66.19 1H13v-1zm0 9.93V19h2.87c-.87.48-1.84.8-2.87.93zM18.24 17H13v-1h5.92c-.2.35-.43.69-.68 1zm1.5-3H13v-1h6.93c-.04.34-.11.67-.19 1z" />
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

export default CryptoAgent;
