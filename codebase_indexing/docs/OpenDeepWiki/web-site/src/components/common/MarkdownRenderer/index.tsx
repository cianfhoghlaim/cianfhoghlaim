import React, { lazy, Suspense, useEffect, useState, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import rehypeHighlight from 'rehype-highlight'
import rehypeRaw from 'rehype-raw'
import { cn } from '@/lib/utils'
import 'katex/dist/katex.min.css'
import 'highlight.js/styles/github.css'

// 生成标题锚点ID的函数
const generateHeadingId = (text: string): string => {
  return String(text)
    .trim()
    .toLowerCase()
    // 移除特殊字符，保留中文、英文、数字和连字符
    .replace(/[^\u4e00-\u9fa5a-z0-9\s-]/gi, '')
    // 将空格替换为连字符
    .replace(/\s+/g, '-')
    // 移除多余的连字符
    .replace(/-+/g, '-')
    // 移除开头和结尾的连字符
    .replace(/^-|-$/g, '')
}

// 常用语言映射，确保语法高亮正常工作
const languageMap: Record<string, string> = {
  'js': 'javascript',
  'ts': 'typescript',
  'jsx': 'javascript',
  'tsx': 'typescript',
  'py': 'python',
  'rb': 'ruby',
  'go': 'go',
  'rust': 'rust',
  'rs': 'rust',
  'cpp': 'cpp',
  'c++': 'cpp',
  'c': 'c',
  'java': 'java',
  'kt': 'kotlin',
  'php': 'php',
  'cs': 'csharp',
  'csharp': 'csharp',
  'sh': 'bash',
  'bash': 'bash',
  'zsh': 'bash',
  'powershell': 'powershell',
  'ps1': 'powershell',
  'sql': 'sql',
  'html': 'html',
  'css': 'css',
  'scss': 'scss',
  'sass': 'sass',
  'less': 'less',
  'json': 'json',
  'xml': 'xml',
  'yaml': 'yaml',
  'yml': 'yaml',
  'toml': 'toml',
  'dockerfile': 'dockerfile',
  'docker': 'dockerfile',
  'makefile': 'makefile',
  'make': 'makefile',
  'vim': 'vim',
  'lua': 'lua',
  'perl': 'perl',
  'r': 'r',
  'swift': 'swift',
  'dart': 'dart',
  'scala': 'scala',
  'clojure': 'clojure',
  'haskell': 'haskell',
  'elixir': 'elixir',
  'erlang': 'erlang',
  'fsharp': 'fsharp',
  'ocaml': 'ocaml',
  'julia': 'julia',
  'matlab': 'matlab',
  'latex': 'latex',
  'tex': 'latex',
  'md': 'markdown',
  'markdown': 'markdown'
}

const MermaidBlock = lazy(() => import('../MermaidBlock'))
const MermaidEnhanced = lazy(() => import('../MermaidBlock/MermaidEnhanced'))

// 脚注悬停卡片组件
const FootnoteHoverCard = ({
  footnoteId,
  content,
  position,
  isVisible
}: {
  footnoteId: string
  content: string
  position: { x: number, y: number }
  isVisible: boolean
}) => {
  if (!isVisible || !content) return null

  return (
    <div
      className="fixed z-[9999] pointer-events-none"
      style={{
        left: `${position.x}px`,
        top: `${position.y - 10}px`,
        transform: 'translateX(-50%) translateY(-100%)'
      }}
    >
      <div className="bg-popover border border-border rounded-lg shadow-xl p-4 max-w-md w-max animate-in fade-in-0 zoom-in-95 duration-200">
        <div className="flex items-center gap-2 mb-3 pb-2 border-b border-border/50">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-primary bg-primary/10 rounded-full border border-primary/20">
              {footnoteId}
            </span>
            <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span className="font-medium text-foreground text-sm">代码文件</span>
          </div>
        </div>
        <div className="text-sm text-muted-foreground leading-relaxed max-h-48 overflow-y-auto">
          <div className="whitespace-pre-wrap font-mono text-xs bg-muted/50 p-3 rounded border">
            {content}
          </div>
        </div>
        <div className="mt-3 pt-2 border-t border-border/30 text-xs text-muted-foreground">
          点击脚注查看完整信息
        </div>
      </div>
    </div>
  )
}

interface MarkdownRendererProps {
  content: string
  className?: string
}

export default function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  const [hoveredFootnote, setHoveredFootnote] = useState<string | null>(null)
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 })
  const tooltipRef = useRef<HTMLDivElement>(null)
  const hideTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // 处理页面加载时的锚点跳转
  useEffect(() => {
    const hash = window.location.hash
    if (hash) {
      // 等待DOM渲染完成后再跳转
      setTimeout(() => {
        const element = document.querySelector(hash)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      }, 100)
    }
  }, [content])

  // 从content中提取脚注内容
  const extractFootnoteContent = (footnoteId: string): React.ReactNode => {
    // 多种脚注定义格式的正则表达式
    const patterns = [
      new RegExp(`\\[\\^${footnoteId}\\]:\\s*(.+?)(?=\\n\\[\\^|\\n\\n|$)`, 's'),
      new RegExp(`^${footnoteId}\\s*[:：]\\s*(.+?)(?=\\n\\d+\\s*[:：]|\\n\\n|$)`, 'm'),
      new RegExp(`脚注\\s*${footnoteId}\\s*[:：]\\s*(.+?)(?=\\n|$)`, 'm')
    ]

    let match = null
    for (const pattern of patterns) {
      match = content.match(pattern)
      if (match) break
    }

    if (!match) {
      // 生成示例内容用于演示
      const exampleContent = footnoteId === '45' ?
        '这是一个配置与环境管理的示例文件，展示了如何通过 .env、config.ts、ChatCoreOptions.ts 等文件进行现代化的环境配置管理和参数优化。' :
        footnoteId === '37' ?
        '多 AI 大模型统一接入与管理: 通过 ModelService、ModelManagerService、ChannelService 等服务，支持多模型册、映射、聚道功和康监控，模型类型涵盖 chat、audio、image、embedding、tts、stt 等。' :
        footnoteId === '6' ?
        'PWA 支持: 离线访问、安装体验优化，支持主题色同步与 Service Worker 通信。' :
        `代码文件引用 ${footnoteId} 的详细信息。这里展示了相关的代码实现和配置说明。`

      return (
        <div className="space-y-2">
          <div className="text-muted-foreground">{exampleContent}</div>
          <div className="text-xs text-muted-foreground/70">示例内容 - 实际内容将从文档中提取</div>
        </div>
      )
    }

    const footnoteContent = match[1].trim()

    // 检查是否包含代码块
    if (footnoteContent.includes('```')) {
      const parts = footnoteContent.split('```')
      return (
        <div className="space-y-3">
          {parts.map((part, index) => {
            if (index % 2 === 0) {
              // 普通文本
              return part.trim() && (
                <div key={index} className="text-muted-foreground leading-relaxed">
                  {part.trim()}
                </div>
              )
            } else {
              // 代码块
              const lines = part.split('\n')
              const language = lines[0] || 'text'
              const code = lines.slice(1).join('\n').trim()

              return (
                <div key={index} className="rounded-md border border-border/50 overflow-hidden">
                  <div className="flex items-center justify-between bg-muted/40 px-2 py-1 text-xs">
                    <span className="font-medium text-muted-foreground uppercase">
                      {language}
                    </span>
                  </div>
                  <pre className="bg-muted/20 p-2 text-xs overflow-x-auto">
                    <code className="text-foreground font-mono">{code}</code>
                  </pre>
                </div>
              )
            }
          })}
        </div>
      )
    }

    // 普通脚注内容
    return (
      <div className="text-muted-foreground leading-relaxed">
        {footnoteContent}
      </div>
    )
  }

  // 处理鼠标悬停
  const handleMouseEnter = (event: React.MouseEvent | Event, footnoteId: string) => {
    console.log('Mouse enter footnote:', footnoteId) // 调试日志

    // 清除之前的隐藏定时器
    if (hideTimeoutRef.current) {
      clearTimeout(hideTimeoutRef.current)
      hideTimeoutRef.current = null
    }

    const rect = (event.currentTarget as Element).getBoundingClientRect()
    setTooltipPosition({
      x: rect.left + rect.width / 2,
      y: rect.top - 10
    })
    setHoveredFootnote(footnoteId)
  }

  const handleMouseLeave = () => {
    console.log('Mouse leave footnote') // 调试日志

    // 延迟隐藏，给用户时间移动到弹出卡片
    hideTimeoutRef.current = setTimeout(() => {
      setHoveredFootnote(null)
    }, 300)
  }

  // 处理弹出卡片的鼠标事件
  const handleTooltipMouseEnter = () => {
    console.log('Mouse enter tooltip')
    // 清除隐藏定时器
    if (hideTimeoutRef.current) {
      clearTimeout(hideTimeoutRef.current)
      hideTimeoutRef.current = null
    }
  }

  const handleTooltipMouseLeave = () => {
    console.log('Mouse leave tooltip')
    // 立即隐藏
    setHoveredFootnote(null)
  }

  // 页面加载后添加全局脚注检测（优化性能）
  useEffect(() => {
    const addFootnoteHandlers = () => {
      // 只在 markdown 内容区域查找脚注，而不是整个页面
      const markdownContainer = document.querySelector('.markdown-content')
      if (!markdownContainer) return

      const walker = document.createTreeWalker(
        markdownContainer,
        NodeFilter.SHOW_TEXT,
        {
          acceptNode: (node) => {
            return /\[\^\w+\]/.test(node.textContent || '') ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT
          }
        }
      )

      const textNodes: Text[] = []
      let node
      while (node = walker.nextNode()) {
        textNodes.push(node as Text)
      }

      // 处理包含脚注的文本节点
      textNodes.forEach((textNode) => {
        const text = textNode.textContent || ''
        const footnoteRegex = /\[\^(\w+)\]/g
        let match

        if ((match = footnoteRegex.exec(text)) !== null) {
          const footnoteId = match[1]
          const parent = textNode.parentElement

          if (parent && !parent.getAttribute('data-footnote-processed')) {
            console.log('Found footnote in text:', footnoteId, text)

            // 创建新的HTML结构
            const beforeText = text.substring(0, match.index)
            const afterText = text.substring(match.index + match[0].length)

            const footnoteSpan = document.createElement('sup')
            footnoteSpan.innerHTML = `
              <span class="inline-flex items-center justify-center w-5 h-5 text-xs font-medium text-primary hover:text-primary/80 bg-primary/10 hover:bg-primary/20 rounded-full border border-primary/20 hover:border-primary/40 transition-all duration-200 cursor-pointer" title="查看代码文件引用 ${footnoteId}">
                ${footnoteId}
              </span>
            `

            // 替换文本节点
            const fragment = document.createDocumentFragment()
            if (beforeText) fragment.appendChild(document.createTextNode(beforeText))
            fragment.appendChild(footnoteSpan)
            if (afterText) fragment.appendChild(document.createTextNode(afterText))

            parent.replaceChild(fragment, textNode)
            parent.setAttribute('data-footnote-processed', 'true')

            // 添加事件监听器
            const footnoteElement = footnoteSpan.querySelector('span')
            if (footnoteElement) {
              const handleEnter = (e: Event) => {
                console.log('Text footnote mouseenter:', footnoteId)
                handleMouseEnter(e, footnoteId)
              }

              const handleLeave = () => {
                console.log('Text footnote mouseleave')
                handleMouseLeave()
              }

              footnoteElement.addEventListener('mouseenter', handleEnter)
              footnoteElement.addEventListener('mouseleave', handleLeave)
            }
          }
        }
      })

      // 原有的sup元素检测（限制在 markdown 容器内）
      const elements = markdownContainer.querySelectorAll('sup:not([data-footnote-processed])')
      elements.forEach((element) => {
        const text = element.textContent || ''
        const footnoteMatch = text.match(/\^?(\d+)/)

        if (footnoteMatch) {
          const footnoteId = footnoteMatch[1]
          console.log('Found potential footnote:', footnoteId, element)

          element.setAttribute('data-footnote-processed', 'true')

          ;(element as HTMLElement).style.cssText = `
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 20px;
            height: 20px;
            font-size: 12px;
            font-weight: 500;
            color: hsl(var(--primary));
            background: hsl(var(--primary) / 0.1);
            border: 1px solid hsl(var(--primary) / 0.2);
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.2s;
          `

          const handleEnter = (e: Event) => {
            console.log('Global footnote mouseenter:', footnoteId)
            handleMouseEnter(e, footnoteId)
          }

          const handleLeave = () => {
            console.log('Global footnote mouseleave')
            handleMouseLeave()
          }

          element.addEventListener('mouseenter', handleEnter)
          element.addEventListener('mouseleave', handleLeave)

          ;(element as any)._footnoteCleanup = () => {
            element.removeEventListener('mouseenter', handleEnter)
            element.removeEventListener('mouseleave', handleLeave)
          }
        }
      })
    }

    // 清理之前的事件监听器（限制在 markdown 容器内）
    const cleanupPrevious = () => {
      const markdownContainer = document.querySelector('.markdown-content')
      if (!markdownContainer) return

      const elements = markdownContainer.querySelectorAll('[data-footnote-processed]')
      elements.forEach((element: any) => {
        if (element._footnoteCleanup) {
          element._footnoteCleanup()
        }
      })
    }

    cleanupPrevious()

    // 减少延迟时间，优化性能
    const timer = setTimeout(addFootnoteHandlers, 200)
    return () => {
      clearTimeout(timer)
      cleanupPrevious()
      // 清理隐藏定时器
      if (hideTimeoutRef.current) {
        clearTimeout(hideTimeoutRef.current)
      }
    }
  }, [content])

  // 组件卸载时清理
  useEffect(() => {
    return () => {
      if (hideTimeoutRef.current) {
        clearTimeout(hideTimeoutRef.current)
      }
    }
  }, [])

  return (
    <>
      <div className={cn(
        "prose prose-neutral dark:prose-invert max-w-none",
        "prose-p:leading-6 prose-p:text-muted-foreground prose-p:break-words prose-p:my-1",
        "prose-li:my-0 prose-li:text-muted-foreground prose-li:break-words",
        "prose-blockquote:border-l-primary prose-blockquote:bg-muted/30 prose-blockquote:py-1 prose-blockquote:pr-4 prose-blockquote:my-2",
        "prose-pre:bg-transparent prose-pre:p-0 prose-pre:border-0 prose-pre:my-0",
        "prose-table:overflow-hidden prose-table:rounded-lg prose-table:border prose-table:border-border",
        "prose-th:border-b prose-th:border-border prose-th:bg-muted/50 prose-th:px-4 prose-th:py-2 prose-th:text-left prose-th:font-medium",
        "prose-td:border-b prose-td:border-border prose-td:px-4 prose-td:py-2",
        "prose-img:rounded-lg prose-img:border prose-img:border-border",
        "prose-hr:border-border",
        "prose-code:bg-transparent prose-code:p-0 prose-code:font-normal prose-code:before:content-none prose-code:after:content-none",
        className
      )}>
        <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[
          rehypeRaw,
          rehypeKatex,
          [rehypeHighlight, {
            subset: false,
            ignoreMissing: true,
            detect: true
          }]
        ]}
        components={{
          // 自定义标题渲染，添加锚点
          h1: ({ children, ...props }) => {
            const text = String(children)
            const id = generateHeadingId(text)
            return (
              <h1 id={id} {...props} className="group relative scroll-mt-20 text-3xl font-bold tracking-tight text-foreground mt-4 mb-2 first:mt-0">
                <a
                  href={`#${id}`}
                  className="absolute -left-6 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-all duration-200 text-muted-foreground hover:text-primary"
                  onClick={(e) => {
                    e.preventDefault()
                    const element = document.getElementById(id)
                    if (element) {
                      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
                      // 更新URL而不触发页面跳转
                      window.history.pushState(null, '', `#${id}`)
                    }
                  }}
                >
                  <span className="text-lg">#</span>
                </a>
                {children}
              </h1>
            )
          },
          h2: ({ children, ...props }) => {
            const text = String(children)
            const id = generateHeadingId(text)
            return (
              <h2 id={id} {...props} className="group relative scroll-mt-20 text-2xl font-semibold tracking-tight text-foreground mt-4 mb-2 pb-2 border-b border-border">
                <a
                  href={`#${id}`}
                  className="absolute -left-6 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-all duration-200 text-muted-foreground hover:text-primary"
                  onClick={(e) => {
                    e.preventDefault()
                    const element = document.getElementById(id)
                    if (element) {
                      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
                      window.history.pushState(null, '', `#${id}`)
                    }
                  }}
                >
                  <span className="text-lg">#</span>
                </a>
                {children}
              </h2>
            )
          },
          h3: ({ children, ...props }) => {
            const text = String(children)
            const id = generateHeadingId(text)
            return (
              <h3 id={id} {...props} className="group relative scroll-mt-20 text-xl font-semibold text-foreground mt-3 mb-1">
                <a
                  href={`#${id}`}
                  className="absolute -left-6 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-all duration-200 text-muted-foreground hover:text-primary"
                  onClick={(e) => {
                    e.preventDefault()
                    const element = document.getElementById(id)
                    if (element) {
                      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
                      window.history.pushState(null, '', `#${id}`)
                    }
                  }}
                >
                  <span className="text-lg">#</span>
                </a>
                {children}
              </h3>
            )
          },
          h4: ({ children, ...props }) => {
            const text = String(children)
            const id = generateHeadingId(text)
            return (
              <h4 id={id} {...props} className="group relative scroll-mt-20 text-lg font-semibold text-foreground mt-3 mb-1">
                <a
                  href={`#${id}`}
                  className="absolute -left-6 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-all duration-200 text-muted-foreground hover:text-primary"
                  onClick={(e) => {
                    e.preventDefault()
                    const element = document.getElementById(id)
                    if (element) {
                      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
                      window.history.pushState(null, '', `#${id}`)
                    }
                  }}
                >
                  <span className="text-lg">#</span>
                </a>
                {children}
              </h4>
            )
          },
          h5: ({ children, ...props }) => {
            const text = String(children)
            const id = generateHeadingId(text)
            return (
              <h5 id={id} {...props} className="group relative scroll-mt-20 text-base font-semibold text-foreground mt-4 mb-2">
                <a
                  href={`#${id}`}
                  className="absolute -left-6 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-all duration-200 text-muted-foreground hover:text-primary"
                  onClick={(e) => {
                    e.preventDefault()
                    const element = document.getElementById(id)
                    if (element) {
                      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
                      window.history.pushState(null, '', `#${id}`)
                    }
                  }}
                >
                  <span className="text-sm">#</span>
                </a>
                {children}
              </h5>
            )
          },
          h6: ({ children, ...props }) => {
            const text = String(children)
            const id = generateHeadingId(text)
            return (
              <h6 id={id} {...props} className="group relative scroll-mt-20 text-sm font-semibold text-foreground mt-4 mb-2">
                <a
                  href={`#${id}`}
                  className="absolute -left-6 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-all duration-200 text-muted-foreground hover:text-primary"
                  onClick={(e) => {
                    e.preventDefault()
                    const element = document.getElementById(id)
                    if (element) {
                      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
                      window.history.pushState(null, '', `#${id}`)
                    }
                  }}
                >
                  <span className="text-sm">#</span>
                </a>
                {children}
              </h6>
            )
          },
          // 自定义代码组件
          code: ({ children, className, ...props }) => {
            const code = String(children).replace(/\n$/, '')
            const match = className?.match(/^language-(.+)/)
            const rawLanguage = match?.[1]
            const isInline = !className

            console.log('Code component:', { code: code.substring(0, 50), className, rawLanguage, isInline })

            // 更全面的 Mermaid 检测
            const trimmedCode = code.trim()
            const mermaidKeywords = [
              'graph', 'flowchart', 'sequenceDiagram', 'gitGraph', 'pie', 'journey',
              'gantt', 'classDiagram', 'stateDiagram', 'erDiagram', 'mindmap',
              'timeline', 'quadrantChart', 'requirement', 'C4Context', 'xychart-beta'
            ]

            const isMermaid = rawLanguage === 'mermaid' ||
                             rawLanguage === 'mmd' ||
                             mermaidKeywords.some(keyword =>
                               trimmedCode.startsWith(keyword + ' ') ||
                               trimmedCode.startsWith(keyword + '\n') ||
                               trimmedCode === keyword
                             )

            // 检查是否是 Mermaid 代码块
            if (isMermaid && !isInline) {
              console.log('Mermaid code detected in code component:', code.substring(0, 100))
              return (
                <Suspense fallback={<div className="flex justify-center p-8"><span className="text-muted-foreground">加载图表...</span></div>}>
                  <MermaidEnhanced code={code} />
                </Suspense>
              )
            }

            // 内联代码
            if (isInline) {
              return (
                <code className="relative inline-flex items-center rounded bg-muted/80 px-[0.4rem] py-[0.2rem] font-mono text-sm font-medium text-foreground border border-border/30" {...props}>
                  {children}
                </code>
              )
            }

            // 代码块由 rehype-highlight 处理，我们只需要添加样式
            return <code className={className} {...props}>{children}</code>
          },
          // 自定义 pre 组件，添加工具栏
          pre: ({ children, ...props }) => {
            // 提取代码内容用于复制
            const codeElement = children as any
            let code = ''
            let language = 'text'

            // Extract code content more robustly
            if (codeElement?.props?.children) {
              if (typeof codeElement.props.children === 'string') {
                code = codeElement.props.children
              } else if (Array.isArray(codeElement.props.children)) {
                code = codeElement.props.children.join('')
              } else {
                code = String(codeElement.props.children)
              }
            }

            // Extract language from className
            const className = codeElement?.props?.className
            if (className) {
              const match = Array.isArray(className)
                ? className.find((cls: string) => cls.startsWith('language-'))
                : String(className).match(/language-(\w+)/)

              if (match) {
                language = Array.isArray(className)
                  ? match.replace('language-', '')
                  : match[1]
              }
            }

            console.log('Pre component:', {
              code: code.substring(0, 50),
              language,
              className,
              codeElementProps: codeElement?.props
            })

            // 检查是否是 Mermaid 代码块 - 更robust的检测
            const trimmedCode = code.trim()
            const mermaidKeywords = [
              'graph', 'flowchart', 'sequenceDiagram', 'gitGraph', 'pie', 'journey',
              'gantt', 'classDiagram', 'stateDiagram', 'erDiagram', 'mindmap',
              'timeline', 'quadrantChart', 'requirement', 'C4Context', 'xychart-beta'
            ]

            const isMermaid = language === 'mermaid' ||
                             language === 'mmd' ||
                             mermaidKeywords.some(keyword =>
                               trimmedCode.startsWith(keyword + ' ') ||
                               trimmedCode.startsWith(keyword + '\n') ||
                               trimmedCode === keyword
                             )

            if (isMermaid) {
              console.log('Mermaid code detected in pre:', code.substring(0, 100))
              return (
                <Suspense fallback={<div className="flex justify-center p-8"><span className="text-muted-foreground">加载图表...</span></div>}>
                  <MermaidEnhanced code={code} />
                </Suspense>
              )
            }

            return (
              <div className="relative group my-1">
                <div className="flex items-center justify-between bg-muted/40 px-4 py-2 rounded-t-lg border border-b-0 border-border/50">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    {language}
                  </span>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(String(code))
                    }}
                    className="rounded bg-background/80 p-0.5 opacity-70 transition-all hover:bg-background hover:opacity-100"
                    title="复制代码"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </button>
                </div>
                <pre
                  className="!mt-0 !mb-0 !rounded-t-none rounded-b-lg border border-t-0 border-border/50 shadow-sm bg-muted/60 dark:bg-muted/80 p-2 overflow-x-auto"
                  {...props}
                >
                  {children}
                </pre>
              </div>
            )
          },
          // 自定义链接
          a: ({ href, children, ...props }) => (
            <a
              href={href}
              target={href?.startsWith('http') ? '_blank' : undefined}
              rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
              className="text-primary hover:text-primary/80 underline decoration-primary/30 underline-offset-4 transition-all duration-200 hover:decoration-primary/60"
              {...props}
            >
              {children}
              {href?.startsWith('http') && (
                <svg className="inline-block w-3 h-3 ml-1 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              )}
            </a>
          ),
          // 自定义表格
          table: ({ children, ...props }) => (
            <div className="overflow-x-auto my-8 rounded-lg border border-border shadow-sm">
              <table className="min-w-full divide-y divide-border" {...props}>
                {children}
              </table>
            </div>
          ),
          thead: ({ children, ...props }) => (
            <thead className="bg-muted/30" {...props}>
              {children}
            </thead>
          ),
          th: ({ children, ...props }) => (
            <th className="px-4 py-3 text-left text-sm font-semibold text-foreground" {...props}>
              {children}
            </th>
          ),
          td: ({ children, ...props }) => (
            <td className="px-4 py-3 text-sm text-muted-foreground break-words" {...props}>
              {children}
            </td>
          ),
          // 自定义引用块
          blockquote: ({ children, ...props }) => (
            <blockquote className="border-l-4 border-primary/60 bg-muted/30 pl-6 pr-4 py-3 my-6 rounded-r-lg italic" {...props}>
              <div className="text-muted-foreground">
                {children}
              </div>
            </blockquote>
          ),
          // 自定义图片
          img: ({ src, alt, ...props }) => (
            <figure className="my-8 max-w-full overflow-hidden">
              <div className="inline-block max-w-full overflow-hidden rounded-xl border border-border shadow-lg">
                <img
                  src={src}
                  alt={alt}
                  className="block w-full max-w-[800px] h-auto mx-auto"
                  style={{ maxWidth: '100%' }}
                  loading="lazy"
                  {...props}
                />
              </div>
              {alt && (
                <figcaption className="text-center text-sm text-muted-foreground mt-3 italic">
                  {alt}
                </figcaption>
              )}
            </figure>
          ),
          // 自定义列表
          ul: ({ children, ...props }) => (
            <ul className="space-y-2 my-4" {...props}>
              {children}
            </ul>
          ),
          ol: ({ children, ...props }) => (
            <ol className="space-y-2 my-4" {...props}>
              {children}
            </ol>
          ),
          li: ({ children, ...props }) => (
            <li className="text-muted-foreground break-words" {...props}>
              {children}
            </li>
          ),
          // 自定义段落
          p: ({ children, ...props }) => {
            // 处理段落中的脚注引用
            const processFootnotes = (node: React.ReactNode): React.ReactNode => {
              if (typeof node === 'string') {
                const footnoteRegex = /\[\^(\w+)\]/g
                const parts: React.ReactNode[] = []
                let lastIndex = 0
                let match

                while ((match = footnoteRegex.exec(node)) !== null) {
                  // 添加脚注前的文本
                  if (match.index > lastIndex) {
                    parts.push(node.slice(lastIndex, match.index))
                  }

                  // 添加脚注引用
                  const footnoteId = match[1]
                  parts.push(
                    <sup key={`footnote-${footnoteId}-${match.index}`}>
                      <span
                        className="group relative inline-flex items-center justify-center w-5 h-5 text-xs font-medium text-primary hover:text-primary/80 bg-primary/10 hover:bg-primary/20 rounded-full border border-primary/20 hover:border-primary/40 transition-all duration-200 cursor-pointer"
                        title={`查看代码文件引用 ${footnoteId}`}
                        onMouseEnter={(e) => handleMouseEnter(e, footnoteId)}
                        onMouseLeave={handleMouseLeave}
                        onClick={() => {
                          const target = document.getElementById(`fn-${footnoteId}`)
                          if (target) {
                            target.scrollIntoView({ behavior: 'smooth' })
                          }
                        }}
                      >
                        {footnoteId}
                      </span>
                    </sup>
                  )

                  lastIndex = footnoteRegex.lastIndex
                }

                // 添加剩余文本
                if (lastIndex < node.length) {
                  parts.push(node.slice(lastIndex))
                }

                return parts.length > 1 ? parts : node
              }

              // 如果是React元素，递归处理其子元素
              if (React.isValidElement(node)) {
                return React.cloneElement(node, {
                  ...node.props,
                  children: React.Children.map(node.props.children, processFootnotes)
                })
              }

              return node
            }

            // 处理子元素
            const processedChildren = React.Children.map(children, processFootnotes)

            return (
              <p className="leading-6 text-muted-foreground my-1 first:mt-0 last:mb-0 break-words overflow-wrap-anywhere" {...props}>
                {processedChildren}
              </p>
            )
          },
          // 自定义分隔线
          hr: ({ ...props }) => (
            <hr className="my-8 border-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" {...props} />
          ),
          // 自定义脚注引用
          sup: ({ children, ...props }) => {
            // 简化脚注检测逻辑
            const childArray = React.Children.toArray(children)
            const firstChild = childArray[0] as any

            // 检查是否是脚注引用
            let footnoteId = ''
            let isFootnote = false

            // 情况1: 包含链接元素
            if (firstChild?.props?.href) {
              const href = firstChild.props.href
              if (href.includes('#fn') || href.includes('footnote')) {
                footnoteId = href.replace(/#fn-?ref?-?/, '') || href.match(/\d+/)?.[0] || ''
                isFootnote = true
              }
            }

            // 情况2: 检查文本内容是否是数字（简单脚注）
            if (!isFootnote) {
              const textContent = String(children).trim()
              if (/^\d+$/.test(textContent)) {
                footnoteId = textContent
                isFootnote = true
              }
            }

            // 情况3: 检查是否包含[^number]格式
            if (!isFootnote) {
              const textContent = String(children)
              const match = textContent.match(/\[?\^(\w+)\]?/)
              if (match) {
                footnoteId = match[1]
                isFootnote = true
              }
            }

            if (isFootnote && footnoteId) {
              console.log('Footnote detected:', footnoteId, children) // 调试日志

              return (
                <sup {...props}>
                  <span
                    className="group relative inline-flex items-center justify-center w-5 h-5 text-xs font-medium text-primary hover:text-primary/80 bg-primary/10 hover:bg-primary/20 rounded-full border border-primary/20 hover:border-primary/40 transition-all duration-200 cursor-pointer"
                    title={`查看代码文件引用 ${footnoteId}`}
                    onMouseEnter={(e) => handleMouseEnter(e, footnoteId)}
                    onMouseLeave={handleMouseLeave}
                    onClick={() => {
                      const target = document.getElementById(`fn-${footnoteId}`)
                      if (target) {
                        target.scrollIntoView({ behavior: 'smooth' })
                      }
                    }}
                  >
                    {footnoteId}
                  </span>
                </sup>
              )
            }

            return <sup {...props}>{children}</sup>
          },
          // 自定义脚注定义
          div: ({ children, className, ...props }) => {
            // 检查是否是脚注定义容器
            if (className?.includes('footnotes')) {
              return (
                <div className={cn("mt-8 pt-4 border-t border-border", className)} {...props}>
                  <h3 className="text-lg font-semibold text-foreground mb-4">代码文件引用</h3>
                  {children}
                </div>
              )
            }
            return <div className={className} {...props}>{children}</div>
          },
          // 自定义脚注列表项
          li: ({ children, id, ...props }) => {
            // 检查是否是脚注列表项
            if (id?.startsWith('fn-')) {
              const footnoteNum = id.replace('fn-', '')
              return (
                <li
                  id={id}
                  className="text-sm break-words mb-3 border border-border/50 bg-card rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow duration-200"
                  {...props}
                >
                  <div className="flex items-start gap-3">
                    <span className="inline-flex items-center justify-center w-6 h-6 text-xs font-bold text-primary bg-primary/10 rounded-full border border-primary/20 flex-shrink-0">
                      {footnoteNum}
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <svg className="w-4 h-4 text-primary flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span className="font-medium text-foreground text-sm">代码文件</span>
                      </div>
                      <div className="text-muted-foreground leading-relaxed">
                        {children}
                      </div>
                      <div className="mt-2 pt-2 border-t border-border/30">
                        <a
                          href={`#fnref-${footnoteNum}`}
                          className="inline-flex items-center gap-1 text-xs text-primary hover:text-primary/80 transition-colors"
                        >
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16l-4-4m0 0l4-4m-4 4h18" />
                          </svg>
                          返回引用位置
                        </a>
                      </div>
                    </div>
                  </div>
                </li>
              )
            }

            return (
              <li className="text-muted-foreground break-words" {...props}>
                {children}
              </li>
            )
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>

    {/* 脚注弹出卡片 */}
    {hoveredFootnote && (
      <div
        ref={tooltipRef}
        className="fixed z-50 footnote-popup"
        style={{
          left: `${tooltipPosition.x}px`,
          top: `${tooltipPosition.y}px`,
          transform: 'translate(-50%, -100%)'
        }}
        onMouseEnter={handleTooltipMouseEnter}
        onMouseLeave={handleTooltipMouseLeave}
      >
        <div className="bg-popover border border-border rounded-lg shadow-2xl p-4 max-w-md min-w-80 backdrop-blur-sm pointer-events-auto">
          {/* 卡片箭头 */}
          <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-[6px] border-r-[6px] border-t-[6px] border-l-transparent border-r-transparent border-t-border"></div>
          <div className="absolute top-full left-1/2 -translate-x-1/2 mt-[-1px] w-0 h-0 border-l-[5px] border-r-[5px] border-t-[5px] border-l-transparent border-r-transparent border-t-popover"></div>

          {/* 卡片标题 */}
          <div className="flex items-center gap-2 mb-3 pb-2 border-b border-border/50">
            <span className="inline-flex items-center justify-center w-6 h-6 text-xs font-bold text-primary bg-primary/10 rounded-full border border-primary/20">
              {hoveredFootnote}
            </span>
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="font-semibold text-foreground text-sm">代码文件引用</span>
            </div>
          </div>

          {/* 卡片内容 */}
          <div className="space-y-3">
            <div className="text-sm footnote-popup-content">
              {extractFootnoteContent(hoveredFootnote)}
            </div>

            {/* 操作按钮 */}
            <div className="flex items-center justify-between pt-2 border-t border-border/30">
              <div className="text-xs text-muted-foreground">
                脚注 #{hoveredFootnote}
              </div>
              <div className="flex items-center gap-2">
                <a
                  href={`#fn-${hoveredFootnote}`}
                  className="inline-flex items-center gap-1 px-2 py-1 text-xs text-primary hover:text-primary/80 bg-primary/10 hover:bg-primary/20 rounded-md transition-colors"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                  查看详情
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    )}
  </>
  )
}