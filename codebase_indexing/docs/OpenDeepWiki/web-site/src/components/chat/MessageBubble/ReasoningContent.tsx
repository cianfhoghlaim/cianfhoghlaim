// Reasoning Content Component - shadcn Style
import { useState } from 'react'
import { ChevronDown, ChevronUp, Brain } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { Button } from '@/components/ui/button'

interface ReasoningContentProps {
  content: string
  className?: string
}

export const ReasoningContent: React.FC<ReasoningContentProps> = ({ content, className }) => {
  const [expanded, setExpanded] = useState(false)

  if (!content) return null

  return (
    <Collapsible open={expanded} onOpenChange={setExpanded}>
      <div className={cn('rounded-lg border bg-muted/50 overflow-hidden', className)}>
        <CollapsibleTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="w-full flex items-center justify-between px-3 py-2.5 hover:bg-muted"
          >
            <div className="flex items-center gap-2">
              <Brain className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium">
                Reasoning Process
              </span>
            </div>
            {expanded ? (
              <ChevronUp className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            )}
          </Button>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <div className="px-3 py-2.5 border-t">
            <div className="text-sm text-muted-foreground whitespace-pre-wrap font-mono">
              {content}
            </div>
          </div>
        </CollapsibleContent>
      </div>
    </Collapsible>
  )
}
