import { useEffect, useState } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Loader2, List, X, Eye, EyeOff } from 'lucide-react'
import { documentService, type DocumentResponse } from '@/services/documentService'
import { useRepositoryDetailStore } from '@/stores/repositoryDetail.store'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import MarkdownRenderer from '@/components/common/MarkdownRenderer'
import TableOfContents from '@/components/common/TableOfContents'

interface DocumentPageProps {
  className?: string
  branch?: string
}

export default function DocumentPage({ className, branch }: DocumentPageProps) {
  const { owner, name, '*': path } = useParams<{ owner: string; name: string; '*': string }>()
  const [searchParams] = useSearchParams()
  const { t, i18n } = useTranslation()
  const { selectedBranch } = useRepositoryDetailStore()
  const [loading, setLoading] = useState(true)
  const [documentData, setDocumentData] = useState<DocumentResponse | null>(null)
  const [error, setError] = useState<string>('')
  const [isMobileTocOpen, setIsMobileTocOpen] = useState(false)
  const [showMobileTocButton, setShowMobileTocButton] = useState(true)
  const [hasTocContent, setHasTocContent] = useState(false)
  const [forceShowToc, setForceShowToc] = useState(false)

  useEffect(() => {
    if (!owner || !name || !path) return

    const fetchDocument = async () => {
      try {
        setLoading(true)
        setError('')

        // 获取分支参数（优先级：URL 参数 > store 中的 selectedBranch > props > 默认 main）
        const urlBranch = searchParams.get('branch')
        const currentBranch = urlBranch || selectedBranch || branch || 'main'

        // 调用文档服务获取内容 - 使用 GetDocumentByIdAsync
        const response = await documentService.getDocument(
          owner,
          name,
          path,
          currentBranch,
          i18n.language
        )

        if (response) {
          setDocumentData(response)
        } else {
          setError(t('repository.document.notFound'))
        }
      } catch (err) {
        console.error('Failed to fetch document:', err)
        setError(t('repository.document.loadFailed'))
      } finally {
        setLoading(false)
      }
    }

    fetchDocument()
  }, [owner, name, path, branch, selectedBranch, searchParams, i18n.language])

  // 检测页面是否有足够的标题来显示 TOC
  useEffect(() => {
    // 延迟检测，确保 markdown 已经渲染
    const checkTocContent = () => {
      const headings = document.querySelectorAll('.markdown-content h1, .markdown-content h2, .markdown-content h3, .markdown-content h4, .markdown-content h5, .markdown-content h6')
      setHasTocContent(headings.length >= 2)
    }

    if (documentData?.content) {
      // 延迟检测以确保 markdown 已经渲染
      setTimeout(checkTocContent, 500)
    }
  }, [documentData?.content])

  // 监听滚动以智能显示/隐藏 TOC 按钮
  useEffect(() => {
    let lastScrollY = 0
    let ticking = false

    const handleScroll = () => {
      const currentScrollY = window.scrollY

      if (!ticking) {
        requestAnimationFrame(() => {
          // 向下滚动隐藏，向上滚动显示
          if (currentScrollY > lastScrollY && currentScrollY > 100) {
            setShowMobileTocButton(false)
          } else if (currentScrollY < lastScrollY || currentScrollY <= 100) {
            setShowMobileTocButton(true)
          }

          lastScrollY = currentScrollY
          ticking = false
        })

        ticking = true
      }
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // 键盘支持（ESC 关闭抽屉）
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isMobileTocOpen) {
        setIsMobileTocOpen(false)
      }
    }

    if (isMobileTocOpen) {
      document.addEventListener('keydown', handleKeyDown)
      // 防止背景滚动
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'unset'
    }
  }, [isMobileTocOpen])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <p className="text-lg text-muted-foreground">{error}</p>
        <p className="text-sm text-muted-foreground">
          {owner}/{name}/{path}
        </p>
      </div>
    )
  }

  return (
    <div className={cn("flex-1 flex h-full relative", className)}>
      <div className="flex-1 overflow-auto h-full">
        <article className="max-w-4xl mx-auto px-6 py-8 min-h-full">
          {/* 显示文档标题 */}
          {documentData?.title && (
            <h1 className="text-3xl font-bold mb-4">{documentData.title}</h1>
          )}
          {/* 显示文档描述 */}
          {documentData?.description && (
            <p className="text-muted-foreground mb-6">{documentData.description}</p>
          )}

          {/* 显示源文件信息 - 移到顶部 */}
          {documentData?.fileSource && documentData.fileSource.length > 0 && (
            <div className="mb-6 p-4 bg-muted/30 rounded-lg border">
              <details className="group">
                <summary className="flex items-center gap-2 cursor-pointer font-medium text-sm">
                  <svg
                    className="w-4 h-4 transition-transform group-open:rotate-90"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  {t('repository.document.relevantSourceFiles')}
                </summary>
                <div className="mt-3 max-h-48 overflow-y-auto space-y-2 pl-6 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
                  {documentData.fileSource.map((source, index) => (
                    <a
                      key={index}
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-sm text-primary hover:underline hover:bg-muted/50 px-2 py-1 rounded transition-colors"
                    >
                      <svg className="w-4 h-4 text-muted-foreground flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <span className="truncate">{source.name}</span>
                    </a>
                  ))}
                  {documentData.fileSource.length > 8 && (
                    <div className="text-xs text-muted-foreground italic px-2 py-1">
                      {t('repository.document.showingSourceFiles', { count: documentData.fileSource.length })}
                    </div>
                  )}
                </div>
              </details>
            </div>
          )}

          {/* 渲染 Markdown 内容 */}
          <div className="markdown-content">
            <MarkdownRenderer content={documentData?.content || ''} />
          </div>
        </article>
      </div>

      {/* 桌面端 TOC - 自适应显示 */}
      {(hasTocContent || forceShowToc) && (
        <aside className="w-64 border-l border-border/40 px-4 py-8 overflow-y-auto hidden lg:block">
          {/* TOC 手动控制按钮 - 仅在内容不足时显示 */}
          {!hasTocContent && (
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-foreground tracking-tight">
                {t('repository.document.tableOfContents')}
              </h3>
              <Button
                onClick={() => setForceShowToc(false)}
                variant="ghost"
                size="icon"
                className="h-6 w-6 hover:bg-muted"
                title={t('repository.document.hideToc')}
              >
                <EyeOff className="h-4 w-4" />
              </Button>
            </div>
          )}
          <TableOfContents />
        </aside>
      )}

      {/* 桌面端 TOC 显示按钮 - 仅在内容不足且未强制显示时显示 */}
      {!hasTocContent && !forceShowToc && (
        <Button
          onClick={() => setForceShowToc(true)}
          className="fixed top-24 right-6 h-10 px-3 rounded-full shadow-lg hidden lg:flex items-center gap-2 z-40"
          variant="outline"
          title={t('repository.document.showToc')}
        >
          <Eye className="h-4 w-4" />
          <span className="text-sm">{t('repository.document.tableOfContents')}</span>
        </Button>
      )}

      {/* 移动端 TOC 按钮 - 自适应显示 */}
      {(hasTocContent || forceShowToc) && (
        <Button
          onClick={() => setIsMobileTocOpen(true)}
          className={cn(
            "fixed bottom-6 right-6 h-12 w-12 rounded-full shadow-lg lg:hidden z-40 p-0 transition-all duration-300",
            showMobileTocButton ? "translate-y-0 opacity-100" : "translate-y-16 opacity-0 pointer-events-none"
          )}
          size="icon"
          aria-label="Open Table of Contents"
        >
          <List className="h-5 w-5" />
        </Button>
      )}

      {/* 移动端 TOC 显示按钮 - 仅在内容不足且未强制显示时显示 */}
      {!hasTocContent && !forceShowToc && (
        <Button
          onClick={() => setForceShowToc(true)}
          className="fixed bottom-6 right-6 h-12 px-4 rounded-full shadow-lg lg:hidden z-40 flex items-center gap-2"
          variant="outline"
          aria-label="Show Table of Contents"
        >
          <Eye className="h-4 w-4" />
          <span className="text-sm">TOC</span>
        </Button>
      )}

      {/* 移动端 TOC 抽屉 - 自适应显示 */}
      {(hasTocContent || forceShowToc) && isMobileTocOpen && (
        <>
          {/* 遮罩层 */}
          <div
            className="fixed inset-0 bg-black/50 z-50 lg:hidden animate-in fade-in duration-300"
            onClick={() => setIsMobileTocOpen(false)}
          />

          {/* TOC 抽屉 */}
          <div className="fixed inset-y-0 right-0 w-80 max-w-[85vw] bg-background border-l border-border z-50 lg:hidden animate-in slide-in-from-right duration-300 shadow-2xl">
            <div className="flex flex-col h-full">
              {/* 头部 */}
              <div className="flex items-center justify-between p-4 border-b border-border">
                <h3 className="text-lg font-semibold">{t('repository.document.tableOfContents')}</h3>
                <Button
                  onClick={() => setIsMobileTocOpen(false)}
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 hover:bg-muted"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {/* TOC 内容 */}
              <div className="flex-1 overflow-y-auto p-4">
                {/* 手动显示提示 - 仅在内容不足时显示 */}
                {!hasTocContent && (
                  <div className="mb-4 p-3 bg-muted/30 rounded-lg border text-sm text-muted-foreground">
                    <div className="flex items-center gap-2 mb-2">
                      <Eye className="h-4 w-4" />
                      <span className="font-medium">{t('repository.document.manualTocMode')}</span>
                    </div>
                    <p>{t('repository.document.manualTocDescription')}</p>
                  </div>
                )}
                <TableOfContents
                  className="max-h-none"
                  onItemClick={() => setIsMobileTocOpen(false)}
                />
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}