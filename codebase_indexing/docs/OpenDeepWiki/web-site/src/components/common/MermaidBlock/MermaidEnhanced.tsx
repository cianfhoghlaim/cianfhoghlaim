import { useEffect, useRef, useState, useCallback } from 'react'
import mermaid from 'mermaid'
import * as Dialog from '@radix-ui/react-dialog'
import { cn } from '@/lib/utils'
import {
  Copy,
  Check,
  Maximize2,
  Download,
  RefreshCw,
  ZoomIn,
  ZoomOut,
  Move,
  X,
  RotateCcw
} from 'lucide-react'

interface MermaidEnhancedProps {
  code: string
  title?: string
  className?: string
}

// 根据代码内容推断图表类型和标题
const inferDiagramType = (code: string): string => {
  const trimmedCode = code.trim().toLowerCase()

  if (trimmedCode.includes('sequencediagram')) return 'Sequence Diagram'
  if (trimmedCode.includes('classDiagram')) return 'Class Diagram'
  if (trimmedCode.includes('gitgraph')) return 'Git Graph'
  if (trimmedCode.includes('gantt')) return 'Gantt Chart'
  if (trimmedCode.includes('pie')) return 'Pie Chart'
  if (trimmedCode.includes('journey')) return 'User Journey'
  if (trimmedCode.includes('statediagram')) return 'State Diagram'
  if (trimmedCode.includes('erdiagram')) return 'ER Diagram'
  if (trimmedCode.includes('mindmap')) return 'Mind Map'
  if (trimmedCode.includes('timeline')) return 'Timeline'
  if (trimmedCode.includes('quadrantchart')) return 'Quadrant Chart'
  if (trimmedCode.includes('flowchart')) return 'Flowchart'
  if (trimmedCode.includes('graph')) return 'Graph'

  return 'Diagram'
}

// Mermaid 主题配置
const getMermaidTheme = (isDark: boolean) => ({
  startOnLoad: false,
  theme: isDark ? 'dark' : 'default',
  themeVariables: isDark ? {
    // 暗色主题
    primaryColor: '#60a5fa',
    primaryTextColor: '#e5e7eb',
    primaryBorderColor: '#3b82f6',
    lineColor: '#6b7280',
    secondaryColor: '#34d399',
    tertiaryColor: '#1f2937',
    background: '#111827',
    mainBkg: '#1f2937',
    secondBkg: '#374151',
    tertiaryBkg: '#111827',
    textColor: '#e5e7eb',
    labelColor: '#e5e7eb',
    errorBkgColor: '#991b1b',
    errorTextColor: '#fef2f2',
    fontFamily: 'ui-sans-serif, system-ui, sans-serif',
    fontSize: '14px',
    darkMode: true
  } : {
    // 亮色主题
    primaryColor: '#3b82f6',
    primaryTextColor: '#1f2937',
    primaryBorderColor: '#2563eb',
    lineColor: '#9ca3af',
    secondaryColor: '#10b981',
    tertiaryColor: '#f3f4f6',
    background: '#ffffff',
    mainBkg: '#ffffff',
    secondBkg: '#f9fafb',
    tertiaryBkg: '#f3f4f6',
    textColor: '#1f2937',
    labelColor: '#1f2937',
    errorBkgColor: '#fef2f2',
    errorTextColor: '#991b1b',
    fontFamily: 'ui-sans-serif, system-ui, sans-serif',
    fontSize: '14px',
    darkMode: false
  },
  securityLevel: 'loose',
  fontFamily: 'ui-sans-serif, system-ui, sans-serif'
})

export default function MermaidEnhanced({
  code,
  title,
  className
}: MermaidEnhancedProps) {
  // 使用传入的标题或根据代码推断标题
  const diagramTitle = title || inferDiagramType(code)
  const containerRef = useRef<HTMLDivElement>(null)
  const svgRef = useRef<SVGElement | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isCopied, setIsCopied] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [scale, setScale] = useState(1)
  const [modalScale, setModalScale] = useState(1)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [isExporting, setIsExporting] = useState(false)

  // 检测系统主题
  useEffect(() => {
    const checkDarkMode = () => {
      const isDark = document.documentElement.classList.contains('dark')
      setIsDarkMode(isDark)
    }

    checkDarkMode()

    // 监听主题变化
    const observer = new MutationObserver(checkDarkMode)
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class']
    })

    return () => observer.disconnect()
  }, [])

  // 复制代码功能
  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(code)
      setIsCopied(true)
      setTimeout(() => setIsCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }, [code])

  // 导出为 SVG
  const exportSVG = useCallback(() => {
    if (!svgRef.current) return

    const svgClone = svgRef.current.cloneNode(true) as SVGElement
    svgClone.setAttribute('xmlns', 'http://www.w3.org/2000/svg')

    const svgString = new XMLSerializer().serializeToString(svgClone)
    const blob = new Blob([svgString], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)

    const a = document.createElement('a')
    a.href = url
    a.download = `${diagramTitle.replace(/\s+/g, '-')}.svg`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }, [diagramTitle])

  // 导出为 PNG
  const exportPNG = useCallback(async () => {
    if (isExporting || !svgRef.current) return

    try {
      setIsExporting(true)

      const svgElement = svgRef.current
      const bbox = svgElement.getBBox()
      const svgClone = svgElement.cloneNode(true) as SVGElement

      svgClone.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
      svgClone.setAttribute('width', String(bbox.width * 2))
      svgClone.setAttribute('height', String(bbox.height * 2))

      // 添加白色背景
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
      rect.setAttribute('width', '100%')
      rect.setAttribute('height', '100%')
      rect.setAttribute('fill', '#ffffff')
      svgClone.insertBefore(rect, svgClone.firstChild)

      const svgString = new XMLSerializer().serializeToString(svgClone)
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')

      if (!ctx) return

      canvas.width = bbox.width * 2
      canvas.height = bbox.height * 2

      const img = new Image()

      img.onload = () => {
        ctx.fillStyle = '#ffffff'
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.drawImage(img, 0, 0)

        canvas.toBlob(blob => {
          if (!blob) return

          const url = URL.createObjectURL(blob)
          const timestamp = new Date().toISOString().slice(0, 10)
          const filename = `${diagramTitle.replace(/\s+/g, '-')}-${timestamp}.png`

          const a = document.createElement('a')
          a.href = url
          a.download = filename
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          URL.revokeObjectURL(url)
          setIsExporting(false)
        }, 'image/png', 0.95)
      }

      img.onerror = () => {
        setIsExporting(false)
        console.error('Failed to export PNG')
      }

      img.src = `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgString)))}`
    } catch (error) {
      console.error('Export failed:', error)
      setIsExporting(false)
    }
  }, [isExporting, diagramTitle])

  // 渲染 Mermaid 图表
  useEffect(() => {
    const renderDiagram = async () => {
      if (!containerRef.current) return

      try {
        setIsLoading(true)
        setError(null)

        // 清空容器
        containerRef.current.innerHTML = ''

        // 配置 Mermaid
        mermaid.initialize(getMermaidTheme(isDarkMode))

        // 验证语法
        const cleanCode = code.trim()
        if (!cleanCode) {
          throw new Error('Empty diagram code')
        }

        await mermaid.parse(cleanCode)

        // 渲染图表
        const id = `mermaid-${Date.now()}`
        const { svg } = await mermaid.render(id, cleanCode)

        if (containerRef.current) {
          containerRef.current.innerHTML = svg

          // 保存 SVG 引用
          const svgElement = containerRef.current.querySelector('svg')
          if (svgElement) {
            svgRef.current = svgElement
            svgElement.style.maxWidth = '100%'
            svgElement.style.height = 'auto'
          }
        }

        setIsLoading(false)
      } catch (err) {
        console.error('Mermaid render error:', err)
        setError(err instanceof Error ? err.message : 'Failed to render diagram')
        setIsLoading(false)
      }
    }

    renderDiagram()
  }, [code, isDarkMode])

  // 全屏模式
  const toggleFullscreen = useCallback(() => {
    setIsFullscreen(prev => !prev)
  }, [])

  // 缩放控制（用于主图）
  const handleZoomIn = useCallback(() => {
    setScale(prev => Math.min(prev * 1.2, 3))
  }, [])

  const handleZoomOut = useCallback(() => {
    setScale(prev => Math.max(prev / 1.2, 0.5))
  }, [])

  const handleResetZoom = useCallback(() => {
    setScale(1)
  }, [])

  // 模态框缩放控制
  const handleModalZoomIn = useCallback(() => {
    setModalScale(prev => Math.min(prev * 1.2, 3))
  }, [])

  const handleModalZoomOut = useCallback(() => {
    setModalScale(prev => Math.max(prev / 1.2, 0.3))
  }, [])

  const handleModalReset = useCallback(() => {
    setModalScale(1)
    setPosition({ x: 0, y: 0 })
  }, [])

  // 拖动控制
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button === 0) { // 只处理左键
      setIsDragging(true)
      setDragStart({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      })
    }
  }, [position])

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      })
    }
  }, [isDragging, dragStart])

  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault()
    const delta = e.deltaY > 0 ? 0.9 : 1.1
    setModalScale(prev => Math.max(0.3, Math.min(3, prev * delta)))
  }, [])

  const handleDoubleClick = useCallback(() => {
    handleModalReset()
  }, [handleModalReset])

  return (
    <>
      <div className="my-8 flex justify-center">
        <div className="group relative inline-block max-w-full min-w-[300px] overflow-x-auto rounded-xl border border-border/50 bg-gradient-to-br from-card to-card/80 p-6 shadow-lg backdrop-blur-sm">
          <div className="absolute right-3 top-3 z-10 flex gap-2 opacity-0 transition-all duration-200 group-hover:opacity-100">
            {/* 复制按钮 */}
            <button
              onClick={handleCopy}
              className="rounded-lg bg-background/90 p-2 transition-all duration-200 hover:bg-background hover:scale-105 shadow-sm"
              title={isCopied ? "已复制" : "复制代码"}
            >
              {isCopied ? (
                <Check className="h-4 w-4" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </button>

            {/* 缩放控制 */}
            <div className="flex items-center gap-1 bg-background/90 rounded-lg shadow-sm">
              <button
                onClick={handleZoomOut}
                className="rounded-lg p-2 transition-all duration-200 hover:bg-muted"
                title="缩小"
              >
                <ZoomOut className="h-4 w-4" />
              </button>
              <span className="text-xs px-2 text-muted-foreground min-w-[3rem] text-center">
                {Math.round(scale * 100)}%
              </span>
              <button
                onClick={handleZoomIn}
                className="rounded-lg p-2 transition-all duration-200 hover:bg-muted"
                title="放大"
              >
                <ZoomIn className="h-4 w-4" />
              </button>
              {scale !== 1 && (
                <button
                  onClick={handleResetZoom}
                  className="rounded-lg p-2 transition-all duration-200 hover:bg-muted"
                  title="重置缩放"
                >
                  <RefreshCw className="h-4 w-4" />
                </button>
              )}
            </div>

            {/* 导出按钮 */}
            <button
              onClick={exportPNG}
              disabled={isExporting}
              className={`rounded-lg bg-background/90 p-2 transition-all duration-200 hover:bg-background hover:scale-105 shadow-sm ${isExporting ? 'opacity-50 cursor-not-allowed' : ''}`}
              title={isExporting ? "正在导出..." : "导出PNG"}
            >
              {isExporting ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
              ) : (
                <Download className="h-4 w-4" />
              )}
            </button>

            {/* 全屏按钮 */}
            <button
              onClick={toggleFullscreen}
              className="rounded-lg bg-background/90 p-2 transition-all duration-200 hover:bg-background hover:scale-105 shadow-sm"
              title="全屏查看"
            >
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>

          {/* 标题显示 */}
          <div className="absolute left-6 top-6 text-sm font-medium text-muted-foreground">
            {diagramTitle}
          </div>

          {/* 图表内容区 */}
          <div className="mt-8 relative">
            {/* 加载状态 */}
            {isLoading && (
              <div className="absolute inset-0 flex items-center justify-center min-h-[200px]">
                <div className="flex flex-col items-center gap-3">
                  <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                  <span className="text-sm text-muted-foreground">
                    渲染图表中...
                  </span>
                </div>
              </div>
            )}

            {/* 错误状态 */}
            {error && (
              <div className="p-6 text-destructive">
                <div className="mb-2 font-medium">图表渲染失败</div>
                <div className="text-sm text-muted-foreground">
                  {error}
                </div>
                <pre className="mt-4 overflow-auto rounded p-3 text-xs bg-muted">
                  <code>{code}</code>
                </pre>
              </div>
            )}

            {/* Mermaid 图表容器 */}
            {!error && (
              <div
                ref={containerRef}
                className="cursor-pointer transition-all duration-300 hover:opacity-90 w-full flex justify-center items-center"
                onClick={toggleFullscreen}
                style={{
                  transform: `scale(${scale})`,
                  transformOrigin: 'center top',
                  transition: 'transform 0.2s',
                  minHeight: isLoading ? '200px' : 'auto'
                }}
              />
            )}
          </div>
        </div>
      </div>

      {/* 全屏模态框 */}
      <Dialog.Root open={isFullscreen} onOpenChange={setIsFullscreen}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
          <Dialog.Content className="fixed left-[50%] top-[50%] z-50 h-[95vh] w-[95vw] translate-x-[-50%] translate-y-[-50%] rounded-lg border border-border bg-background shadow-2xl data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%]">

            {/* 顶部工具栏 */}
            <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between p-4 bg-background/90 backdrop-blur-sm border-b border-border/50">
              <div className="flex items-center gap-2">
                <button
                  onClick={handleModalZoomOut}
                  className="p-2 rounded-lg bg-background/80 hover:bg-muted transition-colors border border-border/50"
                  title="缩小"
                >
                  <ZoomOut className="h-4 w-4" />
                </button>
                <button
                  onClick={handleModalZoomIn}
                  className="p-2 rounded-lg bg-background/80 hover:bg-muted transition-colors border border-border/50"
                  title="放大"
                >
                  <ZoomIn className="h-4 w-4" />
                </button>
                <button
                  onClick={handleModalReset}
                  className="p-2 rounded-lg bg-background/80 hover:bg-muted transition-colors border border-border/50"
                  title="重置"
                >
                  <RotateCcw className="h-4 w-4" />
                </button>
                <div className="w-px h-6 bg-border/50"></div>
                <button
                  onClick={exportPNG}
                  disabled={isExporting}
                  className={`p-2 rounded-lg bg-background/80 hover:bg-muted transition-colors border border-border/50 ${isExporting ? 'opacity-50 cursor-not-allowed' : ''}`}
                  title={isExporting ? "正在导出..." : "导出PNG"}
                >
                  {isExporting ? (
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                  ) : (
                    <Download className="h-4 w-4" />
                  )}
                </button>
                <span className="text-sm text-muted-foreground px-2">
                  {Math.round(modalScale * 100)}%
                </span>
              </div>

              <Dialog.Close asChild>
                <button className="p-2 rounded-lg bg-background/80 hover:bg-muted transition-colors border border-border/50">
                  <X className="h-4 w-4" />
                  <span className="sr-only">关闭</span>
                </button>
              </Dialog.Close>
            </div>

            {/* 图表容器 */}
            <div
              className="w-full h-full pt-16 overflow-hidden select-none"
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              onWheel={handleWheel}
              onDoubleClick={handleDoubleClick}
              style={{
                cursor: isDragging ? 'grabbing' : 'grab'
              }}
            >
              <div
                className="w-full h-full flex items-center justify-center transition-transform duration-100"
                style={{
                  transform: `translate(${position.x}px, ${position.y}px) scale(${modalScale})`,
                  transformOrigin: 'center center'
                }}
              >
                <div
                  dangerouslySetInnerHTML={{ __html: svgRef.current?.outerHTML || '' }}
                  className="pointer-events-none"
                />
              </div>
            </div>

            {/* 提示文字 */}
            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-xs text-muted-foreground bg-background/80 backdrop-blur-sm px-3 py-1 rounded-full border border-border/50">
              拖拽移动 • 滚轮缩放 • 双击重置 • Ctrl+S 保存
            </div>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </>
  )
}