// Standalone Chat Page - shadcn Style
import { useEffect, useRef, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Trash2, Loader2, MessageSquare, Home, ArrowLeft } from 'lucide-react'
import { useChatStore } from '@/stores/chat.store'
import { MessageBubble } from '@/components/chat/MessageBubble'
import { ChatInput, ImageAttachment } from '@/components/chat/ChatInput'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { ThemeToggle } from '@/components/theme-toggle'
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

export default function ChatPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  // Get parameters from URL
  const appId = searchParams.get('appId')
  const organization = searchParams.get('organization')
  const name = searchParams.get('name')

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

  // Validate parameters
  useEffect(() => {
    if (!appId && (!organization || !name)) {
      toast.error('Missing required parameters: appId or (organization and name)')
      return
    }

    // Initialize session
    initializeSession(organization || undefined, name || undefined, appId || undefined)
  }, [appId, organization, name])

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
      <div className="flex flex-col h-screen bg-background">
        {/* Header */}
        <header className="sticky top-0 z-50 w-full border-b bg-card">
          <div className="flex h-16 items-center px-4 lg:px-6">
            <div className="flex items-center gap-3 flex-1">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate(-1)}
                className="h-8 w-8"
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>

              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
                  <MessageSquare className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold">AI Assistant</h1>
                  {(organization && name) && (
                    <p className="text-xs text-muted-foreground">
                      {organization}/{name}
                    </p>
                  )}
                  {appId && (
                    <p className="text-xs text-muted-foreground">
                      App: {appId}
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => messages.length > 0 && setShowClearDialog(true)}
                disabled={messages.length === 0 || isStreaming}
                className="h-8 w-8"
              >
                <Trash2 className="h-4 w-4" />
              </Button>

              <ThemeToggle />

              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate('/')}
                className="h-8 w-8"
              >
                <Home className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="max-w-4xl mx-auto p-4 space-y-4">
              {messages.length === 0 && !isStreaming && (
                <div className="flex flex-col items-center justify-center h-full text-center py-12">
                  <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                    <MessageSquare className="h-10 w-10 text-primary" />
                  </div>
                  <h3 className="text-2xl font-semibold mb-2">Start a conversation</h3>
                  <p className="text-muted-foreground max-w-md">
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
        </div>

        <Separator />

        {/* Input Area */}
        <div className="border-t bg-muted/30">
          <div className="max-w-4xl mx-auto p-4">
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
