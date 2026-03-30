// Main Message Bubble Component
import { useState } from 'react'
import { User, Bot, Copy, Trash2, Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { ChatMessage, MessageRole, ResponsesMessageContentType } from '@/types/chat.types'
import { ReasoningContent } from './ReasoningContent'
import { GitIssuesDisplay } from './GitIssuesDisplay'
import { ToolCallDisplay } from './ToolCallDisplay'
import { EnhancedMessageContent } from './EnhancedMessageContent'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
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

interface MessageBubbleProps {
  message: ChatMessage
  onDelete?: (messageId: string) => void
  className?: string
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onDelete, className }) => {
  const isUser = message.role === MessageRole.USER
  const isAssistant = message.role === MessageRole.ASSISTANT
  const [copied, setCopied] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  // Extract text content
  const textContent = message.content
    .filter(c => c.type === ResponsesMessageContentType.TEXT)
    .map(c => c.content)
    .join('\n')

  // Extract image content
  const imageContent = message.content.filter(c => c.type === ResponsesMessageContentType.IMAGE)

  // Handle copy
  const handleCopy = async () => {
    if (!textContent) return

    try {
      await navigator.clipboard.writeText(textContent)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  // Handle delete
  const handleDelete = () => {
    onDelete?.(message.id)
    setShowDeleteDialog(false)
  }

  return (
    <>
      <div className={cn('flex gap-3 group', isUser ? 'justify-end' : 'justify-start', className)}>
        {/* Avatar - Show for assistant only */}
        {isAssistant && (
          <Avatar className="h-8 w-8 shrink-0">
            <AvatarFallback className="bg-primary/10">
              <Bot className="h-4 w-4 text-primary" />
            </AvatarFallback>
          </Avatar>
        )}

        {/* Message Content */}
        <div className={cn('flex flex-col gap-2 max-w-[80%] relative', isUser && 'items-end')}>
          {/* Reasoning (Assistant only) */}
          {isAssistant && message.reasoning && (
            <ReasoningContent content={message.reasoning} />
          )}

          {/* Images */}
          {imageContent.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {imageContent.map((imgContent, idx) => {
                if ('imageContents' in imgContent && imgContent.imageContents) {
                  return imgContent.imageContents.map((img, imgIdx) => (
                    <div key={`${idx}-${imgIdx}`} className="rounded-lg overflow-hidden border bg-muted max-w-sm">
                      <img
                        src={`data:${img.mimeType};base64,${img.data}`}
                        alt="Uploaded image"
                        className="w-full h-auto"
                      />
                    </div>
                  ))
                }
                return null
              })}
            </div>
          )}

          {/* Main message bubble */}
          {textContent && (
            <div
              className={cn(
                'rounded-lg px-4 py-2.5 relative group/message',
                isUser
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted/50 text-foreground border'
              )}
            >
              {isUser ? (
                <div className="text-sm whitespace-pre-wrap break-words">
                  {textContent}
                </div>
              ) : (
                <div className="prose prose-sm dark:prose-invert max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
                  <EnhancedMessageContent content={textContent} />
                </div>
              )}

              {/* Action buttons */}
              <div className={cn(
                'absolute -top-2 flex items-center gap-1 opacity-0 group-hover/message:opacity-100 transition-opacity',
                isUser ? '-left-2' : '-right-2'
              )}>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        size="icon"
                        variant="secondary"
                        className="h-6 w-6 shadow-sm"
                        onClick={handleCopy}
                      >
                        {copied ? (
                          <Check className="h-3 w-3" />
                        ) : (
                          <Copy className="h-3 w-3" />
                        )}
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{copied ? 'Copied!' : 'Copy'}</p>
                    </TooltipContent>
                  </Tooltip>

                  {onDelete && (
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          size="icon"
                          variant="secondary"
                          className="h-6 w-6 shadow-sm hover:bg-destructive hover:text-destructive-foreground"
                          onClick={() => setShowDeleteDialog(true)}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Delete</p>
                      </TooltipContent>
                    </Tooltip>
                  )}
                </TooltipProvider>
              </div>
            </div>
          )}

          {/* Tool Calls (Assistant only) */}
          {isAssistant && message.toolCalls && message.toolCalls.length > 0 && (
            <div className="space-y-2 w-full">
              {message.toolCalls.map((toolCall) => (
                <ToolCallDisplay key={toolCall.id} toolCall={toolCall} />
              ))}
            </div>
          )}

          {/* Git Issues (Assistant only) */}
          {isAssistant && message.gitIssues && message.gitIssues.length > 0 && (
            <GitIssuesDisplay issues={message.gitIssues} />
          )}

          {/* Timestamp */}
          <span className="text-xs text-muted-foreground px-1">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>

        {/* Avatar - Show for user only */}
        {isUser && (
          <Avatar className="h-8 w-8 shrink-0">
            <AvatarFallback className="bg-primary">
              <User className="h-4 w-4 text-primary-foreground" />
            </AvatarFallback>
          </Avatar>
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Message</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this message? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
