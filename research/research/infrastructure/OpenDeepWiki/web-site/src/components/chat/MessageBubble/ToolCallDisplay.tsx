// Tool Call Display Component - shadcn Style
import { Wrench, Code, FileCode } from 'lucide-react'
import { cn } from '@/lib/utils'
import { ToolCall } from '@/types/chat.types'
import { Badge } from '@/components/ui/badge'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { Button } from '@/components/ui/button'
import { useState } from 'react'

interface ToolCallDisplayProps {
  toolCall: ToolCall
  className?: string
}

export const ToolCallDisplay: React.FC<ToolCallDisplayProps> = ({ toolCall, className }) => {
  const [isOpen, setIsOpen] = useState(false)

  // Parse arguments safely
  let parsedArgs: any = null
  try {
    parsedArgs = toolCall.arguments ? JSON.parse(toolCall.arguments) : null
  } catch {
    // If parsing fails, display as string
  }

  // Get icon based on function name
  const getIcon = () => {
    if (toolCall.functionName.toLowerCase().includes('code')) {
      return <Code className="h-4 w-4" />
    }
    if (toolCall.functionName.toLowerCase().includes('file')) {
      return <FileCode className="h-4 w-4" />
    }
    return <Wrench className="h-4 w-4" />
  }

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <div className={cn('rounded-lg border bg-muted/50 overflow-hidden', className)}>
        <CollapsibleTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="w-full flex items-center justify-between px-3 py-2.5 hover:bg-muted"
          >
            <div className="flex items-center gap-2">
              <div className="text-primary">
                {getIcon()}
              </div>
              <span className="text-sm font-medium">
                Tool Call: {toolCall.functionName}
              </span>
            </div>
            <Badge variant="outline" className="text-xs">
              {isOpen ? 'Hide' : 'Show'} Details
            </Badge>
          </Button>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <div className="px-3 py-2.5 border-t">
            <div className="space-y-2">
              <div>
                <span className="text-xs font-semibold">
                  Function:
                </span>
                <code className="ml-2 text-xs font-mono text-foreground">
                  {toolCall.functionName}
                </code>
              </div>

              {parsedArgs && (
                <div>
                  <span className="text-xs font-semibold">
                    Arguments:
                  </span>
                  <pre className="mt-1 text-xs font-mono text-muted-foreground bg-muted p-2 rounded-md overflow-x-auto">
                    {JSON.stringify(parsedArgs, null, 2)}
                  </pre>
                </div>
              )}

              {!parsedArgs && toolCall.arguments && (
                <div>
                  <span className="text-xs font-semibold">
                    Arguments:
                  </span>
                  <pre className="mt-1 text-xs font-mono text-muted-foreground bg-muted p-2 rounded-md overflow-x-auto">
                    {toolCall.arguments}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </CollapsibleContent>
      </div>
    </Collapsible>
  )
}
