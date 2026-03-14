// Enhanced Message Content Component - Supports custom components
import { Alert, AlertCircle, Info, CheckCircle2, AlertTriangle, Lightbulb } from 'lucide-react'
import MarkdownRenderer from '@/components/common/MarkdownRenderer'
import { Alert as AlertUI, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { Button } from '@/components/ui/button'
import { ChevronDown } from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'

interface EnhancedMessageContentProps {
  content: string
  className?: string
}

// 检测并解析特殊块
const parseSpecialBlocks = (content: string) => {
  const blocks: Array<{ type: string; content: string; title?: string; data?: any }> = []

  // 匹配各种特殊块
  const patterns = {
    // :::warning 或 :::info 等
    admonition: /:::(\w+)(?:\s+(.+?))?[\n\r]+([\s\S]+?)[\n\r]+:::/g,
    // <details> HTML标签
    details: /<details>([\s\S]+?)<\/details>/g,
    // > [!NOTE] GitHub风格警告
    githubAlert: /^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\][\n\r]+((?:>.*[\n\r]*)+)/gm,
  }

  let lastIndex = 0
  const matches: Array<{ index: number; length: number; block: any }> = []

  // 查找所有匹配
  for (const [patternName, pattern] of Object.entries(patterns)) {
    const regex = new RegExp(pattern)
    let match

    while ((match = regex.exec(content)) !== null) {
      matches.push({
        index: match.index,
        length: match[0].length,
        block: {
          type: patternName,
          raw: match[0],
          groups: match.slice(1)
        }
      })
    }
  }

  // 按位置排序
  matches.sort((a, b) => a.index - b.index)

  // 构建blocks数组
  matches.forEach((match) => {
    const { index, length, block } = match

    // 添加之前的普通内容
    if (index > lastIndex) {
      blocks.push({
        type: 'markdown',
        content: content.substring(lastIndex, index)
      })
    }

    // 添加特殊块
    if (block.type === 'admonition') {
      blocks.push({
        type: 'admonition',
        content: block.groups[2],
        data: {
          variant: block.groups[0],
          title: block.groups[1]
        }
      })
    } else if (block.type === 'details') {
      const detailsContent = block.groups[0]
      const summaryMatch = detailsContent.match(/<summary>(.*?)<\/summary>/s)
      const summary = summaryMatch ? summaryMatch[1].trim() : 'Details'
      const innerContent = detailsContent.replace(/<summary>.*?<\/summary>/s, '').trim()

      blocks.push({
        type: 'collapsible',
        content: innerContent,
        title: summary
      })
    } else if (block.type === 'githubAlert') {
      const alertType = block.groups[0].toLowerCase()
      const alertContent = block.groups[1].replace(/^>\s*/gm, '').trim()

      blocks.push({
        type: 'admonition',
        content: alertContent,
        data: {
          variant: alertType,
          title: undefined
        }
      })
    }

    lastIndex = index + length
  })

  // 添加剩余内容
  if (lastIndex < content.length) {
    blocks.push({
      type: 'markdown',
      content: content.substring(lastIndex)
    })
  }

  return blocks.length > 0 ? blocks : [{ type: 'markdown', content }]
}

// 警告块组件
const AdmonitionBlock = ({ variant, title, content }: { variant: string; title?: string; content: string }) => {
  const variantConfig: Record<string, {
    icon: typeof AlertCircle
    title: string
    variant: 'default' | 'destructive'
    iconClass: string
  }> = {
    note: {
      icon: Info,
      title: 'Note',
      variant: 'default',
      iconClass: 'text-blue-500'
    },
    info: {
      icon: Info,
      title: 'Info',
      variant: 'default',
      iconClass: 'text-blue-500'
    },
    tip: {
      icon: Lightbulb,
      title: 'Tip',
      variant: 'default',
      iconClass: 'text-green-500'
    },
    important: {
      icon: CheckCircle2,
      title: 'Important',
      variant: 'default',
      iconClass: 'text-purple-500'
    },
    warning: {
      icon: AlertTriangle,
      title: 'Warning',
      variant: 'destructive',
      iconClass: 'text-yellow-500'
    },
    caution: {
      icon: AlertCircle,
      title: 'Caution',
      variant: 'destructive',
      iconClass: 'text-red-500'
    }
  }

  const config = variantConfig[variant?.toLowerCase()] || variantConfig.note
  const Icon = config.icon

  return (
    <AlertUI variant={config.variant === 'destructive' ? 'destructive' : 'default'} className="my-4">
      <Icon className={cn('h-4 w-4', config.iconClass)} />
      <AlertTitle>{title || config.title}</AlertTitle>
      <AlertDescription className="[&>*]:mb-0">
        <MarkdownRenderer content={content} />
      </AlertDescription>
    </AlertUI>
  )
}

// 折叠块组件
const CollapsibleBlock = ({ title, content }: { title: string; content: string }) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen} className="my-4">
      <Card>
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">{title}</CardTitle>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <ChevronDown className={cn(
                  'h-4 w-4 transition-transform',
                  isOpen && 'transform rotate-180'
                )} />
              </Button>
            </div>
          </CardHeader>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <CardContent className="pt-0">
            <MarkdownRenderer content={content} />
          </CardContent>
        </CollapsibleContent>
      </Card>
    </Collapsible>
  )
}

export const EnhancedMessageContent: React.FC<EnhancedMessageContentProps> = ({ content, className }) => {
  const blocks = parseSpecialBlocks(content)

  return (
    <div className={cn('space-y-2', className)}>
      {blocks.map((block, index) => {
        switch (block.type) {
          case 'admonition':
            return (
              <AdmonitionBlock
                key={index}
                variant={block.data?.variant || 'note'}
                title={block.data?.title}
                content={block.content}
              />
            )

          case 'collapsible':
            return (
              <CollapsibleBlock
                key={index}
                title={block.title || 'Details'}
                content={block.content}
              />
            )

          case 'markdown':
          default:
            // 只渲染非空内容
            if (block.content.trim()) {
              return (
                <div key={index}>
                  <MarkdownRenderer content={block.content} />
                </div>
              )
            }
            return null
        }
      })}
    </div>
  )
}
