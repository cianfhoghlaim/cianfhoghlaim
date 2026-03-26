// Chat Panel Component with Slide Animation - shadcn Style
import { useEffect, useRef, useState } from 'react'
import { X, Trash2, Loader2, MessageSquare } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useChatStore } from '@/stores/chat.store'
import { MessageBubble } from '@/components/chat/MessageBubble'
import { ChatInput, ImageAttachment } from '@/components/chat/ChatInput'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { toast } from 'sonner'

interface ChatPanelProps {
  isOpen: boolean
  onClose: () => void
  organizationName?: string
  repositoryName?: string
  appId?: string
  className?: string
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  isOpen,
  onClose,
  organizationName,
  repositoryName,
  appId,
  className
}) => {
  const {
    messages,
    isStreaming,
    error,
    currentReasoning,
    currentMessageContent,
    initializeSession,
    sendMessage,
    cancelStream,
    clearMessages,
    deleteMessage
  } = useChatStore()

  const [inputValue, setInputValue] = useState('')
  const [deepResearch, setDeepResearch] = useState(false)
  const [showClearDialog, setShowClearDialog] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Initialize session when panel opens
  useEffect(() => {
    if (isOpen) {
      initializeSession(organizationName, repositoryName, appId)
    }
  }, [isOpen, organizationName, repositoryName, appId])

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, currentMessageContent, currentReasoning])

  // Show error toast
  useEffect(() => {
    if (error) {
      toast.error(error)
    }
  }, [error])

  // Handle send message
  const handleSend = (message: string, images: ImageAttachment[]) => {
    const imageData = images.map(img => ({
      file: img.file,
      mimeType: img.mimeType
    }))

    sendMessage(message, deepResearch, imageData)
    setInputValue('')
  }

  // Handle clear messages
  const handleClearConfirm = () => {
    clearMessages()
    setShowClearDialog(false)
    toast.success('Messages cleared')
  }

  // Handle delete message
  const handleDeleteMessage = async (messageId: string) => {
    await deleteMessage(messageId)
    toast.success('Message deleted')
  }

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Panel */}
      <div
        className={cn(
          'fixed top-0 right-0 h-full w-full lg:w-[480px] bg-card border-l shadow-xl z-50',
          'transition-transform duration-300 ease-in-out',
          isOpen ? 'translate-x-0' : 'translate-x-full',
          className
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
              <MessageSquare className="h-4 w-4 text-primary" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-foreground">AI Assistant</h2>
              {(repositoryName || appId) && (
                <p className="text-xs text-muted-foreground">
                  {appId ? `App: ${appId}` : `${organizationName}/${repositoryName}`}
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => messages.length > 0 && setShowClearDialog(true)}
              disabled={messages.length === 0 || isStreaming}
              className="h-8 w-8"
            >
              <Trash2 className="h-4 w-4" />
            </Button>

            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Messages Area */}
        <ScrollArea className="h-[calc(100vh-180px)]">
          <div className="p-4 space-y-4">
            {messages.length === 0 && !isStreaming && (
              <div className="flex flex-col items-center justify-center h-full text-center py-12">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <MessageSquare className="h-8 w-8 text-primary" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Start a conversation</h3>
                <p className="text-sm text-muted-foreground max-w-sm">
                  Ask questions about the repository, request code explanations, or get help with documentation.
                </p>
              </div>
            )}

            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                onDelete={handleDeleteMessage}
              />
            ))}

            {/* Streaming indicators */}
            {isStreaming && (
              <div className="flex gap-3">
                <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                  <MessageSquare className="h-4 w-4 text-primary" />
                </div>

                <div className="flex-1 space-y-2">
                  {currentReasoning && (
                    <div className="rounded-lg border bg-muted/50 p-3">
                      <div className="flex items-center gap-2 mb-2">
                        <Loader2 className="h-4 w-4 text-muted-foreground animate-spin" />
                        <span className="text-xs font-medium text-muted-foreground">
                          Reasoning...
                        </span>
                      </div>
                      <div className="text-xs text-muted-foreground font-mono whitespace-pre-wrap">
                        {currentReasoning}
                      </div>
                    </div>
                  )}

                  {currentMessageContent && (
                    <div className="rounded-lg bg-muted/50 border px-4 py-2.5">
                      <div className="text-sm whitespace-pre-wrap">
                        {currentMessageContent}
                        <span className="inline-block w-1 h-4 ml-1 bg-current animate-pulse" />
                      </div>
                    </div>
                  )}

                  {!currentReasoning && !currentMessageContent && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Thinking...</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        <Separator />

        {/* Input Area */}
        <div className="p-4 bg-muted/30">
          <ChatInput
            value={inputValue}
            onChange={setInputValue}
            onSend={handleSend}
            onCancel={cancelStream}
            isStreaming={isStreaming}
            deepResearch={deepResearch}
            onDeepResearchChange={setDeepResearch}
            placeholder="Ask a question..."
          />
        </div>
      </div>

      {/* Clear Messages Dialog */}
      <AlertDialog open={showClearDialog} onOpenChange={setShowClearDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Clear All Messages</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to clear all messages? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleClearConfirm} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Clear All
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
