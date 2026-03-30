// SSE Streaming Service for Chat API
import {
  ResponsesInput,
  SSEEvent,
  SSEEventType,
  SSEToolCallEvent,
  SSEGitIssuesEvent,
  SSEReasoningContentEvent,
  SSEMessageContentEvent
} from '@/types/chat.types'

export type SSEEventHandler = (event: SSEEvent) => void

export interface StreamOptions {
  onEvent: SSEEventHandler
  onError?: (error: Error) => void
  onComplete?: () => void
  signal?: AbortSignal
}

class ChatStreamService {
  private readonly apiEndpoint = '/api/Responses'

  /**
   * Stream chat responses from the API
   */
  async streamChat(input: ResponsesInput, options: StreamOptions): Promise<void> {
    const { onEvent, onError, onComplete, signal } = options

    try {
      const response = await fetch(this.apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(input),
        signal,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      if (!response.body) {
        throw new Error('Response body is null')
      }

      // Read the stream
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      try {
        while (true) {
          const { done, value } = await reader.read()

          if (done) {
            break
          }

          // Decode the chunk and add to buffer
          buffer += decoder.decode(value, { stream: true })

          // Process complete lines
          const lines = buffer.split('\n')
          buffer = lines.pop() || '' // Keep the last incomplete line in buffer

          for (const line of lines) {
            if (!line.trim()) continue

            // SSE format: "data: {...}"
            if (line.startsWith('data: ')) {
              const data = line.slice(6) // Remove "data: " prefix

              try {
                const event = this.parseSSEEvent(data)
                if (event) {
                  onEvent(event)
                }
              } catch (parseError) {
                if (import.meta.env.DEV) {
                  console.error('Failed to parse SSE event:', parseError, data)
                }
              }
            }
          }
        }

        // Call completion callback
        onComplete?.()
      } finally {
        // Ensure reader is always released
        reader.releaseLock()
      }
    } catch (error) {
      if (error instanceof Error) {
        // Don't report abort errors
        if (error.name !== 'AbortError') {
          onError?.(error)
        }
      } else {
        onError?.(new Error('Unknown error occurred'))
      }
    }
  }

  /**
   * Parse SSE event data
   */
  private parseSSEEvent(data: string): SSEEvent | null {
    try {
      const parsed = JSON.parse(data)
      const type = parsed.type as SSEEventType

      switch (type) {
        case SSEEventType.REASONING_START:
          return { type: SSEEventType.REASONING_START }

        case SSEEventType.REASONING_CONTENT:
          return {
            type: SSEEventType.REASONING_CONTENT,
            content: parsed.content
          } as SSEReasoningContentEvent

        case SSEEventType.REASONING_END:
          return { type: SSEEventType.REASONING_END }

        case SSEEventType.MESSAGE_START:
          return { type: SSEEventType.MESSAGE_START }

        case SSEEventType.MESSAGE_CONTENT:
          return {
            type: SSEEventType.MESSAGE_CONTENT,
            content: parsed.content
          } as SSEMessageContentEvent

        case SSEEventType.MESSAGE_END:
          return { type: SSEEventType.MESSAGE_END }

        case SSEEventType.TOOL_CALL:
          return {
            type: SSEEventType.TOOL_CALL,
            tool_call_id: parsed.tool_call_id,
            function_name: parsed.function_name,
            function_arguments: parsed.function_arguments
          } as SSEToolCallEvent

        case SSEEventType.GIT_ISSUES:
          return {
            type: SSEEventType.GIT_ISSUES,
            content: parsed.content
          } as SSEGitIssuesEvent

        case SSEEventType.DONE:
          return { type: SSEEventType.DONE }

        default:
          console.warn('Unknown SSE event type:', type)
          return null
      }
    } catch (error) {
      console.error('Failed to parse SSE event:', error, data)
      return null
    }
  }

  /**
   * Create abort controller for cancelling stream
   */
  createAbortController(): AbortController {
    return new AbortController()
  }
}

// Create singleton instance
export const chatStreamService = new ChatStreamService()

// Export class for testing
export default ChatStreamService
