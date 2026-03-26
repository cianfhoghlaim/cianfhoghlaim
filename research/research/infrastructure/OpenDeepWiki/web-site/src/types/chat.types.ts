// Chat Message Types based on ResponsesService.cs SSE events

export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system',
}

export enum ResponsesMessageContentType {
  TEXT = 'text',
  IMAGE = 'image',
}

export enum SSEEventType {
  REASONING_START = 'reasoning_start',
  REASONING_CONTENT = 'reasoning_content',
  REASONING_END = 'reasoning_end',
  MESSAGE_START = 'message_start',
  MESSAGE_CONTENT = 'message_content',
  MESSAGE_END = 'message_end',
  TOOL_CALL = 'tool_call',
  GIT_ISSUES = 'git_issues',
  DONE = 'done',
}

// SSE Event Types
export interface SSEReasoningStartEvent {
  type: SSEEventType.REASONING_START
}

export interface SSEReasoningContentEvent {
  type: SSEEventType.REASONING_CONTENT
  content: string
}

export interface SSEReasoningEndEvent {
  type: SSEEventType.REASONING_END
}

export interface SSEMessageStartEvent {
  type: SSEEventType.MESSAGE_START
}

export interface SSEMessageContentEvent {
  type: SSEEventType.MESSAGE_CONTENT
  content: string
}

export interface SSEMessageEndEvent {
  type: SSEEventType.MESSAGE_END
}

export interface SSEToolCallEvent {
  type: SSEEventType.TOOL_CALL
  tool_call_id: string
  function_name: string
  function_arguments: string
}

export interface GitIssue {
  id: number
  title: string
  state: string
  url: string
  created_at: string
  updated_at: string
  body?: string
}

export interface SSEGitIssuesEvent {
  type: SSEEventType.GIT_ISSUES
  content: GitIssue[]
}

export interface SSEDoneEvent {
  type: SSEEventType.DONE
}

export type SSEEvent =
  | SSEReasoningStartEvent
  | SSEReasoningContentEvent
  | SSEReasoningEndEvent
  | SSEMessageStartEvent
  | SSEMessageContentEvent
  | SSEMessageEndEvent
  | SSEToolCallEvent
  | SSEGitIssuesEvent
  | SSEDoneEvent

// Message Content Types
export interface TextContent {
  type: ResponsesMessageContentType.TEXT
  content: string
}

export interface ImageContent {
  type: ResponsesMessageContentType.IMAGE
  content: string
  imageContents?: {
    mimeType: string
    data: string
  }[]
}

export type MessageContent = TextContent | ImageContent

// Chat Message
export interface ChatMessage {
  id: string
  role: MessageRole
  content: MessageContent[]
  timestamp: number
  reasoning?: string // For displaying reasoning content
  toolCalls?: ToolCall[]
  gitIssues?: GitIssue[]
}

// Tool Call
export interface ToolCall {
  id: string
  functionName: string
  arguments: string
  timestamp: number
}

// Chat Session
export interface ChatSession {
  id: string
  organizationName?: string
  repositoryName?: string
  appId?: string
  messages: ChatMessage[]
  createdAt: number
  updatedAt: number
}

// API Request Types
export interface ResponsesMessageInput {
  role: string
  content: MessageContent[]
}

export interface ResponsesInput {
  organizationName?: string
  name?: string
  appId?: string
  messages: ResponsesMessageInput[]
  deepResearch?: boolean
}

// Chat UI State
export interface ChatUIState {
  isOpen: boolean
  isStreaming: boolean
  currentReasoning: string
  currentMessage: string
  error: string | null
}
