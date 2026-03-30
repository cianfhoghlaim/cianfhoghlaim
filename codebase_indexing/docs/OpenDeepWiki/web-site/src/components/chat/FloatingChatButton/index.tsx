// Floating Chat Button Component - Minimalist shadcn Style
import { MessageSquare } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

interface FloatingChatButtonProps {
  onClick: () => void
  unreadCount?: number
  className?: string
}

export const FloatingChatButton: React.FC<FloatingChatButtonProps> = ({
  onClick,
  unreadCount = 0,
  className
}) => {
  return (
    <div className={cn('fixed bottom-6 right-6 z-40', className)}>
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              onClick={onClick}
              size="icon"
              className={cn(
                'h-12 w-12 rounded-full shadow-md',
                'hover:shadow-lg transition-all duration-200',
                'relative group'
              )}
            >
              <MessageSquare className="h-5 w-5" />

              {unreadCount > 0 && (
                <Badge
                  variant="destructive"
                  className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 rounded-full text-[10px] font-semibold"
                >
                  {unreadCount > 99 ? '99+' : unreadCount}
                </Badge>
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent side="left">
            <p>Open AI Assistant</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
  )
}
