// Chat State Management with Zustand
import { create } from 'zustand'
import {
  ChatMessage,
  ChatSession,
  MessageRole,
  ResponsesMessageContentType,
  SSEEvent,
  SSEEventType,
  ToolCall,
  GitIssue,
  ResponsesInput
} from '@/types/chat.types'
import { chatStorageService } from '@/services/chatStorage.service'
import { chatStreamService } from '@/services/chatStream.service'

// Helper function to convert File to base64
const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const base64 = reader.result as string
      // Remove data URL prefix (e.g., "data:image/png;base64,")
      const base64Data = base64.split(',')[1]
      resolve(base64Data)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

interface ChatState {
  // UI State
  isOpen: boolean
  isStreaming: boolean
  error: string | null
  isInitializing: boolean

  // Current Session
  currentSession: ChatSession | null
  messages: ChatMessage[]

  // Streaming State
  currentReasoning: string
  currentMessageContent: string
  currentToolCalls: ToolCall[]
  currentGitIssues: GitIssue[]

  // Abort Controller
  abortController: AbortController | null

  // Actions
  setOpen: (open: boolean) => void
  initializeSession: (organizationName?: string, repositoryName?: string, appId?: string) => Promise<void>
  sendMessage: (content: string, deepResearch?: boolean, images?: Array<{ file: File, mimeType: string }>) => Promise<void>
  cancelStream: () => void
  clearMessages: () => void
  deleteMessage: (messageId: string) => Promise<void>
  deleteSession: () => Promise<void>
  reset: () => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  // Initial State
  isOpen: false,
  isStreaming: false,
  error: null,
  isInitializing: false,
  currentSession: null,
  messages: [],
  currentReasoning: '',
  currentMessageContent: '',
  currentToolCalls: [],
  currentGitIssues: [],
  abortController: null,

  // Set panel open state
  setOpen: (open: boolean) => {
    set({ isOpen: open })
  },

  // Initialize session
  initializeSession: async (organizationName?: string, repositoryName?: string, appId?: string) => {
    const { isInitializing } = get()

    // Prevent concurrent initialization
    if (isInitializing) {
      return
    }

    set({ isInitializing: true, error: null })

    try {
      // Initialize storage if needed
      await chatStorageService.init()

      // Get or create session
      const session = await chatStorageService.getOrCreateSession(organizationName, repositoryName, appId)

      set({
        currentSession: session,
        messages: session.messages,
        isInitializing: false
      })
    } catch (error) {
      console.error('Failed to initialize session:', error)
      set({
        error: 'Failed to initialize chat session',
        isInitializing: false
      })
    }
  },

  // Send message
  sendMessage: async (content: string, deepResearch = false, images?: Array<{ file: File, mimeType: string }>) => {
    const { currentSession, messages } = get()

    if (!currentSession) {
      set({ error: 'No active session' })
      return
    }

    if (!content.trim() && (!images || images.length === 0)) {
      return
    }

    // Convert images to base64
    const imageContents = []
    if (images && images.length > 0) {
      for (const image of images) {
        try {
          const base64 = await fileToBase64(image.file)
          imageContents.push({
            mimeType: image.mimeType,
            data: base64
          })
        } catch (error) {
          console.error('Failed to convert image to base64:', error)
        }
      }
    }

    // Create user message content
    const messageContent = []

    // Add text content if present
    if (content.trim()) {
      messageContent.push({
        type: ResponsesMessageContentType.TEXT,
        content: content.trim()
      })
    }

    // Add image content if present
    if (imageContents.length > 0) {
      messageContent.push({
        type: ResponsesMessageContentType.IMAGE,
        content: '', // Empty string for image type
        imageContents
      })
    }

    // Create user message
    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      role: MessageRole.USER,
      content: messageContent,
      timestamp: Date.now()
    }

    // Add user message to state
    const updatedMessages = [...messages, userMessage]
    set({ messages: updatedMessages, error: null })

    // Save user message to storage
    try {
      await chatStorageService.addMessage(currentSession.id, userMessage)
    } catch (error) {
      console.error('Failed to save user message:', error)
    }

    // Prepare API input
    const apiInput: ResponsesInput = {
      organizationName: currentSession.organizationName,
      name: currentSession.repositoryName,
      appId: currentSession.appId,
      deepResearch,
      messages: updatedMessages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))
    }

    // Start streaming
    const abortController = chatStreamService.createAbortController()

    set({
      isStreaming: true,
      abortController,
      currentReasoning: '',
      currentMessageContent: '',
      currentToolCalls: [],
      currentGitIssues: []
    })

    // Track assistant message data immutably
    const assistantMessageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    const assistantTimestamp = Date.now()
    let completedReasoning: string | undefined
    let completedContent: string | undefined
    let completedGitIssues: GitIssue[] | undefined

    try {
      await chatStreamService.streamChat(apiInput, {
        signal: abortController.signal,
        onEvent: (event: SSEEvent) => {
          const state = get()

          switch (event.type) {
            case SSEEventType.REASONING_START:
              set({ currentReasoning: '' })
              break

            case SSEEventType.REASONING_CONTENT:
              set({ currentReasoning: state.currentReasoning + event.content })
              break

            case SSEEventType.REASONING_END:
              completedReasoning = state.currentReasoning
              set({ currentReasoning: '' })
              break

            case SSEEventType.MESSAGE_START:
              set({ currentMessageContent: '' })
              break

            case SSEEventType.MESSAGE_CONTENT:
              set({ currentMessageContent: state.currentMessageContent + event.content })
              break

            case SSEEventType.MESSAGE_END:
              if (state.currentMessageContent) {
                completedContent = state.currentMessageContent
              }
              set({ currentMessageContent: '' })
              break

            case SSEEventType.TOOL_CALL:
              const toolCall: ToolCall = {
                id: event.tool_call_id,
                functionName: event.function_name,
                arguments: event.function_arguments,
                timestamp: Date.now()
              }
              set({ currentToolCalls: [...state.currentToolCalls, toolCall] })
              break

            case SSEEventType.GIT_ISSUES:
              completedGitIssues = event.content
              set({ currentGitIssues: event.content })
              break

            case SSEEventType.DONE:
              // Build final assistant message immutably
              const assistantMessage: ChatMessage = {
                id: assistantMessageId,
                role: MessageRole.ASSISTANT,
                content: completedContent ? [{
                  type: ResponsesMessageContentType.TEXT,
                  content: completedContent
                }] : [],
                timestamp: assistantTimestamp,
                ...(completedReasoning && { reasoning: completedReasoning }),
                ...(state.currentToolCalls.length > 0 && { toolCalls: state.currentToolCalls }),
                ...(completedGitIssues && { gitIssues: completedGitIssues })
              }

              // Add to messages
              const finalMessages = [...state.messages, assistantMessage]
              set({
                messages: finalMessages,
                isStreaming: false,
                currentToolCalls: [],
                currentGitIssues: [],
                abortController: null
              })

              // Save to storage
              chatStorageService.addMessage(currentSession.id, assistantMessage).catch(error => {
                console.error('Failed to save assistant message:', error)
                set({ error: 'Failed to save message to storage' })
              })
              break
          }
        },
        onError: (error) => {
          console.error('Stream error:', error)
          set({
            error: error.message,
            isStreaming: false,
            abortController: null
          })
        },
        onComplete: () => {
          set({
            isStreaming: false,
            abortController: null
          })
        }
      })
    } catch (error) {
      console.error('Failed to send message:', error)
      set({
        error: error instanceof Error ? error.message : 'Failed to send message',
        isStreaming: false,
        abortController: null
      })
    }
  },

  // Cancel streaming
  cancelStream: () => {
    const { abortController } = get()
    if (abortController) {
      abortController.abort()
      set({
        isStreaming: false,
        abortController: null,
        currentReasoning: '',
        currentMessageContent: '',
        currentToolCalls: [],
        currentGitIssues: []
      })
    }
  },

  // Clear messages
  clearMessages: () => {
    const { currentSession } = get()
    if (currentSession) {
      const updatedSession = { ...currentSession, messages: [], updatedAt: Date.now() }
      chatStorageService.saveSession(updatedSession).catch(error => {
        console.error('Failed to clear messages:', error)
        set({ error: 'Failed to clear messages from storage' })
      })
    }
    set({ messages: [] })
  },

  // Delete single message
  deleteMessage: async (messageId: string) => {
    const { currentSession, messages } = get()

    if (!currentSession) {
      set({ error: 'No active session' })
      return
    }

    // Filter out the message
    const updatedMessages = messages.filter(msg => msg.id !== messageId)

    // Update state immediately
    set({ messages: updatedMessages })

    // Update storage
    try {
      const updatedSession = {
        ...currentSession,
        messages: updatedMessages,
        updatedAt: Date.now()
      }
      await chatStorageService.saveSession(updatedSession)
    } catch (error) {
      console.error('Failed to delete message:', error)
      set({ error: 'Failed to delete message from storage' })
      // Revert on error
      set({ messages })
    }
  },

  // Delete session
  deleteSession: async () => {
    const { currentSession } = get()
    if (currentSession) {
      try {
        await chatStorageService.deleteSession(currentSession.id)
        set({
          currentSession: null,
          messages: [],
          error: null
        })
      } catch (error) {
        console.error('Failed to delete session:', error)
        set({ error: 'Failed to delete session' })
      }
    }
  },

  // Reset state
  reset: () => {
    const { abortController } = get()
    if (abortController) {
      abortController.abort()
    }
    set({
      isOpen: false,
      isStreaming: false,
      error: null,
      isInitializing: false,
      currentSession: null,
      messages: [],
      currentReasoning: '',
      currentMessageContent: '',
      currentToolCalls: [],
      currentGitIssues: [],
      abortController: null
    })
  }
}))
