// Git Issues Display Component - shadcn Style
import { GitBranch, ExternalLink, Calendar } from 'lucide-react'
import { cn } from '@/lib/utils'
import { GitIssue } from '@/types/chat.types'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface GitIssuesDisplayProps {
  issues: GitIssue[]
  className?: string
}

export const GitIssuesDisplay: React.FC<GitIssuesDisplayProps> = ({ issues, className }) => {
  if (!issues || issues.length === 0) return null

  return (
    <div className={cn('space-y-2', className)}>
      <div className="flex items-center gap-2 mb-2">
        <GitBranch className="h-4 w-4 text-primary" />
        <span className="text-sm font-medium">Related Issues</span>
      </div>

      <div className="space-y-2">
        {issues.map((issue) => (
          <Card key={issue.id} className="overflow-hidden hover:border-primary/50 transition-colors">
            <CardHeader className="pb-3 pt-3">
              <div className="flex items-start justify-between gap-2">
                <CardTitle className="text-sm font-medium line-clamp-2 flex-1">
                  {issue.title}
                </CardTitle>
                <Badge
                  variant={issue.state === 'open' ? 'default' : 'secondary'}
                  className="shrink-0"
                >
                  {issue.state}
                </Badge>
              </div>
            </CardHeader>

            {issue.body && (
              <CardContent className="pb-3 pt-0">
                <p className="text-xs text-muted-foreground line-clamp-2">
                  {issue.body}
                </p>
              </CardContent>
            )}

            <CardContent className="pt-0 pb-3">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  <span>
                    {new Date(issue.created_at).toLocaleDateString()}
                  </span>
                </div>

                {issue.url && (
                  <a
                    href={issue.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-primary hover:underline"
                  >
                    View
                    <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
