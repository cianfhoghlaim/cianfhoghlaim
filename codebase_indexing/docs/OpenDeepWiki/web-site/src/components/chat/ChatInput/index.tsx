// Enhanced Chat Input Component with Image Upload - shadcn Style
import { useRef, useState, KeyboardEvent, ChangeEvent } from 'react'
import { Send, StopCircle, Image as ImageIcon, X, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

export interface ImageAttachment {
  id: string
  file: File
  preview: string
  mimeType: string
}

interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSend: (message: string, images: ImageAttachment[]) => void
  onCancel?: () => void
  isStreaming?: boolean
  deepResearch?: boolean
  onDeepResearchChange?: (enabled: boolean) => void
  disabled?: boolean
  placeholder?: string
  className?: string
}

export const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSend,
  onCancel,
  isStreaming = false,
  deepResearch = false,
  onDeepResearchChange,
  disabled = false,
  placeholder = 'Ask a question...',
  className
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [images, setImages] = useState<ImageAttachment[]>([])

  // Handle send message
  const handleSend = () => {
    if ((!value.trim() && images.length === 0) || isStreaming || disabled) return
    onSend(value, images)
    setImages([])

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  // Handle textarea keydown
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Auto-resize textarea
  const handleInputChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value)

    const textarea = e.target

    // 重置高度以获取正确的scrollHeight
    textarea.style.height = 'auto'

    // 限制最大高度为120px
    const maxHeight = 120
    const minHeight = 44
    const scrollHeight = textarea.scrollHeight

    // 确保高度在min和max之间
    const newHeight = Math.max(minHeight, Math.min(scrollHeight, maxHeight))

    // 设置高度和溢出处理
    textarea.style.height = `${newHeight}px`
    textarea.style.maxHeight = `${maxHeight}px`

    // 当内容超过最大高度时显示滚动条
    if (scrollHeight > maxHeight) {
      textarea.style.overflowY = 'auto'
    } else {
      textarea.style.overflowY = 'hidden'
    }
  }

  // Handle image selection
  const handleImageSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    const newImages: ImageAttachment[] = []

    Array.from(files).forEach((file) => {
      // Check if file is an image
      if (!file.type.startsWith('image/')) {
        return
      }

      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        return
      }

      const id = `img-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      const preview = URL.createObjectURL(file)

      newImages.push({
        id,
        file,
        preview,
        mimeType: file.type
      })
    })

    setImages(prev => [...prev, ...newImages])

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  // Remove image
  const handleRemoveImage = (id: string) => {
    setImages(prev => {
      const image = prev.find(img => img.id === id)
      if (image) {
        URL.revokeObjectURL(image.preview)
      }
      return prev.filter(img => img.id !== id)
    })
  }

  // Open file picker
  const handleImageButtonClick = () => {
    fileInputRef.current?.click()
  }

  // Toggle deep research
  const handleToggleDeepResearch = () => {
    if (onDeepResearchChange) {
      onDeepResearchChange(!deepResearch)
    }
  }

  return (
    <TooltipProvider>
      <div className={cn('space-y-2', className)}>
        {/* Top Action Bar */}
        <div className="flex items-center justify-between px-1">
          <div className="flex items-center gap-1">
            {/* Image upload button */}
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={handleImageButtonClick}
                  disabled={isStreaming || disabled}
                  className="h-8 w-8"
                >
                  <ImageIcon className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="top">
                <p>Upload image</p>
              </TooltipContent>
            </Tooltip>

            {/* Deep Research toggle */}
            {onDeepResearchChange && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    type="button"
                    variant={deepResearch ? "default" : "ghost"}
                    size="icon"
                    onClick={handleToggleDeepResearch}
                    disabled={isStreaming || disabled}
                    className={cn(
                      "h-8 w-8",
                      deepResearch && "bg-primary text-primary-foreground"
                    )}
                  >
                    <Sparkles className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="top">
                  <p>{deepResearch ? 'Deep Research: ON' : 'Deep Research: OFF'}</p>
                </TooltipContent>
              </Tooltip>
            )}
          </div>

          {/* Status indicator */}
          {deepResearch && !isStreaming && (
            <Badge variant="secondary" className="text-xs">
              <Sparkles className="h-3 w-3 mr-1" />
              Deep Research
            </Badge>
          )}
        </div>

        {/* Image Previews */}
        {images.length > 0 && (
          <div className="flex flex-wrap gap-2 px-1">
            {images.map((image) => (
              <div
                key={image.id}
                className="relative group rounded-lg overflow-hidden border bg-muted"
              >
                <img
                  src={image.preview}
                  alt="Upload preview"
                  className="h-20 w-20 object-cover"
                />
                <button
                  onClick={() => handleRemoveImage(image.id)}
                  className="absolute top-1 right-1 h-5 w-5 rounded-full bg-destructive text-destructive-foreground opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Input Area */}
        <div className="relative flex items-end gap-2">
          {/* Textarea */}
          <Textarea
            ref={textareaRef}
            value={value}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isStreaming || disabled}
            className="resize-none flex-1"
            rows={1}
            style={{
              minHeight: '44px',
              maxHeight: '120px',
              height: '44px',
              overflowY: 'hidden'
            }}
          />

          {/* Send/Cancel button */}
          {isStreaming ? (
            <Button
              onClick={onCancel}
              size="icon"
              variant="destructive"
              className="shrink-0"
            >
              <StopCircle className="h-4 w-4" />
            </Button>
          ) : (
            <Button
              onClick={handleSend}
              size="icon"
              disabled={(!value.trim() && images.length === 0) || disabled}
              className="shrink-0"
            >
              <Send className="h-4 w-4" />
            </Button>
          )}

          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            onChange={handleImageSelect}
            className="hidden"
          />
        </div>
      </div>
    </TooltipProvider>
  )
}
