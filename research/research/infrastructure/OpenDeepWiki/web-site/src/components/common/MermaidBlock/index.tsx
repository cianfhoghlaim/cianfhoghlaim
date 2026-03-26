import { useEffect, useRef, useState, useCallback, useMemo } from 'react'
import mermaid from 'mermaid'
import * as Dialog from '@radix-ui/react-dialog'
import { X, Expand, ZoomIn, ZoomOut, RotateCcw, Download } from 'lucide-react'

// SVG 缓存管理器
class MermaidCache {
  private cache = new Map<string, { svg: string; timestamp: number }>()
  private readonly maxSize = 50 // 最大缓存数量
  private readonly maxAge = 30 * 60 * 1000 // 30分钟过期

  // 生成内容哈希
  private generateHash(content: string): string {
    let hash = 0
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // 转换为32位整数
    }
    return Math.abs(hash).toString(36)
  }

  // 获取缓存
  get(chart: string): string | null {
    const key = this.generateHash(chart.trim())
    const cached = this.cache.get(key)

    if (!cached) return null

    // 检查是否过期
    if (Date.now() - cached.timestamp > this.maxAge) {
      this.cache.delete(key)
      return null
    }

    // LRU: 重新设置以更新访问顺序
    this.cache.delete(key)
    this.cache.set(key, {
      ...cached,
      timestamp: Date.now() // 更新访问时间
    })

    return cached.svg
  }

  // 设置缓存
  set(chart: string, svg: string): void {
    const key = this.generateHash(chart.trim())

    // 如果缓存已满，删除最旧的项
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value
      this.cache.delete(oldestKey)
    }

    this.cache.set(key, {
      svg,
      timestamp: Date.now()
    })
  }

  // 清理过期缓存
  cleanup(): void {
    const now = Date.now()
    for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp > this.maxAge) {
        this.cache.delete(key)
      }
    }
  }

  // 清空所有缓存
  clear(): void {
    this.cache.clear()
  }

  // 获取缓存信息
  getStats(): { size: number; maxSize: number } {
    return {
      size: this.cache.size,
      maxSize: this.maxSize
    }
  }
}

// 全局缓存实例
const mermaidCache = new MermaidCache()

// 定期清理过期缓存
setInterval(() => {
  mermaidCache.cleanup()
}, 5 * 60 * 1000) // 每5分钟清理一次

// 导出缓存实例以便外部使用
export { mermaidCache }

interface MermaidBlockProps {
  chart: string
}

// 添加shimmer动画的CSS
const shimmerStyle = document.createElement('style')
if (!document.querySelector('#mermaid-shimmer-animation')) {
  shimmerStyle.id = 'mermaid-shimmer-animation'
  shimmerStyle.textContent = `
    @keyframes shimmer {
      0% {
        background-position: -200% 0;
      }
      100% {
        background-position: 200% 0;
      }
    }
  `
  document.head.appendChild(shimmerStyle)
}

export default function MermaidBlock({ chart }: MermaidBlockProps) {
  const ref = useRef<HTMLDivElement>(null)
  const modalRef = useRef<HTMLDivElement>(null)
  const [isError, setIsError] = useState(false)
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [scale, setScale] = useState(1)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [estimatedHeight, setEstimatedHeight] = useState(200)
  const [isExporting, setIsExporting] = useState(false)

  // 根据图表内容估算高度
  const estimateChartHeight = useCallback((chart: string): number => {
    const trimmedChart = chart.trim()
    const lines = trimmedChart.split('\n').length
    const hasSubgraphs = /subgraph/.test(trimmedChart)
    const hasSequence = /sequenceDiagram/.test(trimmedChart)
    const hasGantt = /gantt/.test(trimmedChart)
    const hasClass = /classDiagram/.test(trimmedChart)

    let baseHeight = 200

    // 基于图表类型调整高度
    if (hasSequence) {
      baseHeight = Math.max(300, lines * 25)
    } else if (hasGantt) {
      baseHeight = Math.max(250, lines * 20)
    } else if (hasClass) {
      baseHeight = Math.max(350, lines * 30)
    } else if (hasSubgraphs) {
      baseHeight = Math.max(400, lines * 35)
    } else {
      // 流程图或其他类型
      baseHeight = Math.max(200, lines * 15)
    }

    // 限制在合理范围内
    return Math.min(Math.max(baseHeight, 200), 600)
  }, [])

  // 缓存chart内容的哈希，避免重复计算
  const chartHash = useMemo(() => {
    let hash = 0
    const trimmedChart = chart.trim()
    for (let i = 0; i < trimmedChart.length; i++) {
      const char = trimmedChart.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash
    }
    return Math.abs(hash).toString(36)
  }, [chart])

  // 当图表内容变化时更新估算高度
  useEffect(() => {
    const newHeight = estimateChartHeight(chart)
    setEstimatedHeight(newHeight)
  }, [chart, estimateChartHeight])

  const configureMermaid = () => {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'base',
      themeVariables: {
        primaryColor: '#3b82f6',
        primaryTextColor: '#1f2937',
        primaryBorderColor: '#2563eb',
        lineColor: '#6b7280',
        secondaryColor: '#06b6d4',
        tertiaryColor: '#f3f4f6',
        background: '#ffffff',
        mainBkg: '#ffffff',
        secondBkg: '#f9fafb',
        tertiaryBkg: '#f3f4f6',
        fontFamily: 'ui-sans-serif, system-ui, sans-serif',
        fontSize: '14px',
        darkMode: false
      },
      securityLevel: 'loose',
      fontFamily: 'ui-sans-serif, system-ui, sans-serif',
      fontSize: 14,
      logLevel: 'error'
    })
  }

  // 缩放和拖拽处理函数
  const handleZoomIn = useCallback(() => {
    setScale(prev => Math.min(prev * 1.2, 3))
  }, [])

  const handleZoomOut = useCallback(() => {
    setScale(prev => Math.max(prev / 1.2, 0.3))
  }, [])

  const handleReset = useCallback(() => {
    setScale(1)
    setPosition({ x: 0, y: 0 })
  }, [])

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
    setScale(prev => Math.max(0.3, Math.min(3, prev * delta)))
  }, [])

  const handleDoubleClick = useCallback(() => {
    handleReset()
  }, [handleReset])

  // PNG导出功能
  const exportToPNG = useCallback(async (scale: number = 2) => {
    if (isExporting) return

    try {
      setIsExporting(true)

      const svgElement = modalRef.current?.querySelector('svg') || ref.current?.querySelector('svg')

      if (!svgElement) {
        console.error('No SVG element found for export')
        throw new Error('未找到图表内容')
      }

      // 创建一个新的 SVG 元素副本
      const svgClone = svgElement.cloneNode(true) as SVGElement

      // 获取 SVG 的尺寸
      const bbox = svgElement.getBBox()
      const width = bbox.width || svgElement.clientWidth || 800
      const height = bbox.height || svgElement.clientHeight || 600

      // 设置高分辨率尺寸
      const exportWidth = width * scale
      const exportHeight = height * scale

      // 确保 SVG 有正确的命名空间和属性
      svgClone.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
      svgClone.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink')
      svgClone.setAttribute('width', exportWidth.toString())
      svgClone.setAttribute('height', exportHeight.toString())
      svgClone.setAttribute('viewBox', `0 0 ${width} ${height}`)

      // 清理可能导致CORS问题的属性和元素
      const cleanSVG = (element: Element) => {
        // 移除可能导致CORS问题的属性
        const problematicAttrs = [
          'href', 'xlink:href', 'src', 'data-src',
          'style' // 移除可能包含外部资源的内联样式
        ]

        problematicAttrs.forEach(attr => {
          if (element.hasAttribute(attr)) {
            const value = element.getAttribute(attr)
            if (attr === 'style') {
              // 移除包含url()的样式
              if (value && value.includes('url(')) {
                element.removeAttribute(attr)
              }
            } else if (value && (value.startsWith('http') || value.startsWith('//') || value.startsWith('data:'))) {
              element.removeAttribute(attr)
            }
          }
        })

        // 移除可能有问题的元素
        const problematicTags = ['image', 'foreignObject', 'script', 'link']
        if (problematicTags.includes(element.tagName.toLowerCase())) {
          element.remove()
          return
        }

        // 递归清理子元素（需要先转换为数组以避免在迭代时修改DOM）
        Array.from(element.children).forEach(child => cleanSVG(child))
      }

      cleanSVG(svgClone)

      // 添加白色背景
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
      rect.setAttribute('width', '100%')
      rect.setAttribute('height', '100%')
      rect.setAttribute('fill', '#ffffff')
      svgClone.insertBefore(rect, svgClone.firstChild)

      // 内联所有样式以避免外部依赖
      const inlineStyles = (svgEl: SVGElement) => {
        const styleElement = document.createElementNS('http://www.w3.org/2000/svg', 'style')
        styleElement.setAttribute('type', 'text/css')
        styleElement.textContent = `
          <![CDATA[
          * {
            font-family: 'Arial', 'Helvetica', sans-serif !important;
          }
          text {
            font-family: 'Arial', 'Helvetica', sans-serif !important;
            font-size: 14px;
            fill: #000000;
          }
          path {
            fill: none;
            stroke: #000000;
            stroke-width: 1;
          }
          rect {
            fill: #ffffff;
            stroke: #000000;
            stroke-width: 1;
          }
          ]]>
        `
        svgEl.insertBefore(styleElement, svgEl.firstChild)
      }

      inlineStyles(svgClone)

      // 确保所有文本元素都有默认样式
      const textElements = svgClone.querySelectorAll('text')
      textElements.forEach(textEl => {
        if (!textEl.getAttribute('fill')) {
          textEl.setAttribute('fill', '#000000')
        }
        if (!textEl.getAttribute('font-family')) {
          textEl.setAttribute('font-family', 'Arial, Helvetica, sans-serif')
        }
      })

      // 将 SVG 转换为字符串并编码为 data URL
      const svgString = new XMLSerializer().serializeToString(svgClone)

      // 调试信息
      if (process.env.NODE_ENV === 'development') {
        console.log('SVG string length:', svgString.length)
        console.log('SVG preview:', svgString.substring(0, 500))
      }

      const encodedSvg = encodeURIComponent(svgString)
      const dataUrl = `data:image/svg+xml;charset=utf-8,${encodedSvg}`

      // 创建 Canvas 进行转换
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d', { willReadFrequently: true })

      if (!ctx) {
        throw new Error('Could not get canvas context')
      }

      canvas.width = exportWidth
      canvas.height = exportHeight

      // 创建 Image 对象
      const img = new Image()

      return new Promise<void>((resolve, reject) => {
        // 添加超时机制
        const timeout = setTimeout(() => {
          reject(new Error('Image load timeout'))
        }, 10000) // 10秒超时

        img.onload = () => {
          clearTimeout(timeout)
          try {
            // 设置高质量渲染
            ctx.imageSmoothingEnabled = true
            ctx.imageSmoothingQuality = 'high'

            // 绘制白色背景
            ctx.fillStyle = '#ffffff'
            ctx.fillRect(0, 0, exportWidth, exportHeight)

            // 绘制 SVG
            ctx.drawImage(img, 0, 0, exportWidth, exportHeight)

            // 转换为 PNG 并下载
            canvas.toBlob((blob) => {
              if (blob) {
                const url = URL.createObjectURL(blob)
                // 生成更有意义的文件名
                const chartType = chart.trim().split('\n')[0].replace(/[^a-zA-Z]/g, '') || 'chart'
                const timestamp = new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')
                const filename = `mermaid-${chartType}-${timestamp}.png`

                const a = document.createElement('a')
                a.href = url
                a.download = filename
                document.body.appendChild(a)
                a.click()
                document.body.removeChild(a)
                URL.revokeObjectURL(url)
                resolve()
              } else {
                reject(new Error('Failed to create PNG blob'))
              }
            }, 'image/png', 0.95)
          } catch (error) {
            console.error('Canvas error:', error)
            reject(error)
          }
        }

        img.onerror = (error) => {
          clearTimeout(timeout)
          console.error('Image load error:', error)
          reject(new Error('Failed to load SVG image'))
        }

        // 使用 data URL 而不是 blob URL
        img.src = dataUrl
      })

    } catch (error) {
      console.error('Export to PNG failed:', error)

      // 如果PNG导出失败，提供SVG下载作为替代方案
      try {
        console.log('PNG export failed, falling back to SVG export')
        await exportToSVG()
        // SVG导出成功，给用户一个提示
        console.log('已导出为SVG格式')

        // 可选：显示一个临时提示
        if (typeof window !== 'undefined') {
          const notification = document.createElement('div')
          notification.textContent = '已导出为SVG格式'
          notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 14px;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
          `
          document.body.appendChild(notification)
          setTimeout(() => {
            if (notification.parentNode) {
              document.body.removeChild(notification)
            }
          }, 3000)
        }
      } catch (svgError) {
        console.error('SVG export also failed:', svgError)
        throw new Error('导出失败，请重试')
      }
    } finally {
      setIsExporting(false)
    }
  }, [isExporting])

  // SVG导出的替代方法
  const exportToSVG = useCallback(async () => {
    const svgElement = modalRef.current?.querySelector('svg') || ref.current?.querySelector('svg')

    if (!svgElement) {
      throw new Error('未找到图表内容')
    }

    // 创建SVG副本
    const svgClone = svgElement.cloneNode(true) as SVGElement

    // 确保SVG有正确的命名空间
    svgClone.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
    svgClone.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink')

    // 添加白色背景
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
    rect.setAttribute('width', '100%')
    rect.setAttribute('height', '100%')
    rect.setAttribute('fill', '#ffffff')
    svgClone.insertBefore(rect, svgClone.firstChild)

    // 序列化SVG
    const svgString = new XMLSerializer().serializeToString(svgClone)
    const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' })

    // 下载SVG文件
    const url = URL.createObjectURL(blob)
    const chartType = chart.trim().split('\n')[0].replace(/[^a-zA-Z]/g, '') || 'chart'
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')
    const filename = `mermaid-${chartType}-${timestamp}.svg`

    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }, [chart])

  // 处理导出的包装函数
  const handleExport = useCallback(async () => {
    try {
      await exportToPNG()
    } catch (error) {
      // 这里可以替换为更好的错误提示组件
      const errorMessage = error instanceof Error ? error.message : '导出失败，请重试'
      console.error('Export failed:', errorMessage)

      // 临时使用alert，实际项目中应该使用toast组件
      // 如果是SVG导出成功，不显示错误信息
      if (!errorMessage.includes('SVG')) {
        alert(errorMessage)
      }
    }
  }, [exportToPNG])

  // 重置缩放和位置当弹窗打开时
  useEffect(() => {
    if (isOpen) {
      setScale(1)
      setPosition({ x: 0, y: 0 })
    }
  }, [isOpen])

  useEffect(() => {
    const renderMermaid = async () => {
      if (!ref.current) return

      try {
        setIsError(false)
        setIsLoading(true)

        // Clear previous content
        ref.current.innerHTML = ''

        // Clean and validate chart content
        const cleanChart = chart.trim()
        if (!cleanChart) {
          throw new Error('Empty chart content')
        }

        // 首先检查缓存
        const cachedSvg = mermaidCache.get(cleanChart)
        if (cachedSvg) {
          console.log('Using cached SVG for chart:', chartHash)

          if (ref.current) {
            ref.current.innerHTML = cachedSvg

            // Add responsive styling to SVG
            const svgElement = ref.current.querySelector('svg')
            if (svgElement) {
              svgElement.style.maxWidth = '100%'
              svgElement.style.height = 'auto'

              // 对于缓存的内容，也进行高度调整
              const actualHeight = svgElement.getBoundingClientRect().height
              if (actualHeight > 0 && Math.abs(actualHeight - estimatedHeight) > 50) {
                ref.current.style.transition = 'height 0.3s ease-out'
                setTimeout(() => {
                  if (ref.current) {
                    ref.current.style.height = 'auto'
                  }
                }, 50)
              } else {
                // 高度匹配良好，直接设置为auto
                ref.current.style.height = 'auto'
              }
            }
          }

          setIsLoading(false)
          return
        }

        // 缓存未命中，进行渲染
        console.log('Rendering new chart:', chartHash)
        configureMermaid()

        // Generate unique ID for this chart
        const id = `mermaid-${chartHash}-${Date.now()}`

        // Validate mermaid syntax first
        const isValid = await mermaid.parse(cleanChart)
        if (!isValid) {
          throw new Error('Invalid mermaid syntax')
        }

        // Render mermaid chart
        const { svg } = await mermaid.render(id, cleanChart)

        if (ref.current && svg) {
          ref.current.innerHTML = svg

          // Add responsive styling to SVG
          const svgElement = ref.current.querySelector('svg')
          if (svgElement) {
            svgElement.style.maxWidth = '100%'
            svgElement.style.height = 'auto'

            // 获取实际渲染的高度并平滑过渡
            const actualHeight = svgElement.getBoundingClientRect().height
            if (actualHeight > 0 && Math.abs(actualHeight - estimatedHeight) > 50) {
              // 如果实际高度与估算高度差异较大，使用过渡效果
              ref.current.style.transition = 'height 0.3s ease-out'
              setTimeout(() => {
                if (ref.current) {
                  ref.current.style.height = 'auto'
                }
              }, 50)
            }
          }

          // 缓存渲染结果
          mermaidCache.set(cleanChart, svg)
          console.log('Cached SVG for chart:', chartHash, 'Cache stats:', mermaidCache.getStats())
        }

        setIsLoading(false)
      } catch (error) {
        console.error('Mermaid rendering error:', error)
        setIsError(true)
        setIsLoading(false)

        // Clear content on error
        if (ref.current) {
          ref.current.innerHTML = ''
        }
      }
    }

    const timeoutId = setTimeout(renderMermaid, 100)
    return () => clearTimeout(timeoutId)
  }, [chart, chartHash])

  // Render modal content when modal opens
  useEffect(() => {
    const renderModalMermaid = async () => {
      if (!modalRef.current || !isOpen) return

      try {
        // Clear previous content
        modalRef.current.innerHTML = ''

        // Clean and validate chart content
        const cleanChart = chart.trim()
        if (!cleanChart) {
          throw new Error('Empty chart content')
        }

        // 首先检查缓存
        const cachedSvg = mermaidCache.get(cleanChart)
        if (cachedSvg) {
          console.log('Using cached SVG for modal chart:', chartHash)

          if (modalRef.current) {
            modalRef.current.innerHTML = cachedSvg

            // Add responsive styling to SVG
            const svgElement = modalRef.current.querySelector('svg')
            if (svgElement) {
              svgElement.style.maxWidth = '100%'
              svgElement.style.height = 'auto'
            }
          }
          return
        }

        // 缓存未命中，进行渲染
        console.log('Rendering new modal chart:', chartHash)
        configureMermaid()

        // Generate unique ID for modal chart
        const id = `mermaid-modal-${chartHash}-${Date.now()}`

        // Validate mermaid syntax first
        const isValid = await mermaid.parse(cleanChart)
        if (!isValid) {
          throw new Error('Invalid mermaid syntax')
        }

        // Render mermaid chart for modal
        const { svg } = await mermaid.render(id, cleanChart)

        if (modalRef.current && svg) {
          modalRef.current.innerHTML = svg

          // Add responsive styling to SVG
          const svgElement = modalRef.current.querySelector('svg')
          if (svgElement) {
            svgElement.style.maxWidth = '100%'
            svgElement.style.height = 'auto'
          }

          // 缓存渲染结果（如果还没有的话）
          if (!mermaidCache.get(cleanChart)) {
            mermaidCache.set(cleanChart, svg)
            console.log('Cached SVG for modal chart:', chartHash)
          }
        }
      } catch (error) {
        console.error('Mermaid modal rendering error:', error)
        // Clear content on error
        if (modalRef.current) {
          modalRef.current.innerHTML = ''
        }
      }
    }

    if (isOpen) {
      const timeoutId = setTimeout(renderModalMermaid, 100)
      return () => clearTimeout(timeoutId)
    }
  }, [isOpen, chart, chartHash])

  // 组件卸载时的清理（开发环境下的调试信息）
  useEffect(() => {
    return () => {
      if (process.env.NODE_ENV === 'development') {
        console.log('MermaidBlock unmounted, cache stats:', mermaidCache.getStats())
      }
    }
  }, [])

  // 快捷键支持 - Ctrl+S 保存PNG
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's' && isOpen) {
        e.preventDefault()
        handleExport()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      return () => document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isOpen, handleExport])

  if (isError) {
    return (
      <div className="my-6 rounded-lg border border-border bg-muted/30 p-4">
        <div className="mb-2 text-sm text-muted-foreground">Mermaid 渲染失败，显示原始代码：</div>
        <pre className="overflow-x-auto text-sm">
          <code className="language-mermaid">{chart}</code>
        </pre>
      </div>
    )
  }

  return (
    <>
      <div className="my-8 flex justify-center">
        <div className="group relative inline-block max-w-full min-w-[300px] overflow-x-auto rounded-xl border border-border/50 bg-gradient-to-br from-card to-card/80 p-6 shadow-lg backdrop-blur-sm">
          <div className="absolute right-3 top-3 z-10 flex gap-2 opacity-0 transition-all duration-200 group-hover:opacity-100">
            <button
              onClick={handleExport}
              disabled={isExporting}
              className={`rounded-lg bg-background/90 p-2 transition-all duration-200 hover:bg-background hover:scale-105 shadow-sm ${isExporting ? 'opacity-50 cursor-not-allowed' : ''}`}
              title={isExporting ? "正在导出..." : "下载PNG图片"}
            >
              {isExporting ? (
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="m12 2a10 10 0 0 1 10 10h-4a6 6 0 0 0-6-6v-4z"></path>
                </svg>
              ) : (
                <Download className="h-4 w-4" />
              )}
            </button>
            <button
              onClick={() => setIsOpen(true)}
              className="rounded-lg bg-background/90 p-2 transition-all duration-200 hover:bg-background hover:scale-105 shadow-sm"
              title="点击放大查看"
            >
              <Expand className="h-4 w-4" />
            </button>
          </div>
          <div
            ref={ref}
            className="mermaid cursor-pointer transition-all duration-300 hover:opacity-90 w-full flex justify-center items-center"
            onClick={() => setIsOpen(true)}
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              minHeight: `${estimatedHeight}px`,
              height: isLoading ? `${estimatedHeight}px` : 'auto'
            }}
          />
          {isLoading && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-card/50 backdrop-blur-sm rounded-xl">
              {/* 骨架屏效果 */}
              <div className="w-full max-w-md space-y-4">
                <div
                  className="h-4 rounded"
                  style={{
                    background: 'linear-gradient(90deg, hsl(var(--muted)) 25%, hsl(var(--muted)/0.5) 50%, hsl(var(--muted)) 75%)',
                    backgroundSize: '200% 100%',
                    animation: 'shimmer 2s infinite'
                  }}
                ></div>
                <div className="space-y-2">
                  <div
                    className="h-3 rounded w-3/4"
                    style={{
                      background: 'linear-gradient(90deg, hsl(var(--muted)) 25%, hsl(var(--muted)/0.5) 50%, hsl(var(--muted)) 75%)',
                      backgroundSize: '200% 100%',
                      animation: 'shimmer 2s infinite 0.5s'
                    }}
                  ></div>
                  <div
                    className="h-3 rounded w-1/2"
                    style={{
                      background: 'linear-gradient(90deg, hsl(var(--muted)) 25%, hsl(var(--muted)/0.5) 50%, hsl(var(--muted)) 75%)',
                      backgroundSize: '200% 100%',
                      animation: 'shimmer 2s infinite 1s'
                    }}
                  ></div>
                </div>
                <div
                  className="h-4 rounded w-2/3"
                  style={{
                    background: 'linear-gradient(90deg, hsl(var(--muted)) 25%, hsl(var(--muted)/0.5) 50%, hsl(var(--muted)) 75%)',
                    backgroundSize: '200% 100%',
                    animation: 'shimmer 2s infinite 1.5s'
                  }}
                ></div>
              </div>

              {/* 加载文字 */}
              <div className="flex items-center gap-2 text-sm text-muted-foreground mt-6">
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="m12 2a10 10 0 0 1 10 10h-4a6 6 0 0 0-6-6v-4z"></path>
                </svg>
                渲染图表中...
              </div>
            </div>
          )}
        </div>
      </div>

      <Dialog.Root open={isOpen} onOpenChange={setIsOpen}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
          <Dialog.Content className="fixed left-[50%] top-[50%] z-50 h-[95vh] w-[95vw] translate-x-[-50%] translate-y-[-50%] rounded-lg border border-border bg-background shadow-2xl data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%]">

            {/* 顶部工具栏 */}
            <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between p-4 bg-background/90 backdrop-blur-sm border-b border-border/50">
              <div className="flex items-center gap-2">
                <button
                  onClick={handleZoomOut}
                  className="p-2 rounded-lg bg-background/80 hover:bg-muted transition-colors border border-border/50"
                  title="缩小"
                >
                  <ZoomOut className="h-4 w-4" />
                </button>
                <button
                  onClick={handleZoomIn}
                  className="p-2 rounded-lg bg-background/80 hover:bg-muted transition-colors border border-border/50"
                  title="放大"
                >
                  <ZoomIn className="h-4 w-4" />
                </button>
                <button
                  onClick={handleReset}
                  className="p-2 rounded-lg bg-background/80 hover:bg-muted transition-colors border border-border/50"
                  title="重置"
                >
                  <RotateCcw className="h-4 w-4" />
                </button>
                <div className="w-px h-6 bg-border/50"></div>
                <button
                  onClick={handleExport}
                  disabled={isExporting}
                  className={`p-2 rounded-lg bg-background/80 hover:bg-muted transition-colors border border-border/50 ${isExporting ? 'opacity-50 cursor-not-allowed' : ''}`}
                  title={isExporting ? "正在导出..." : "下载PNG图片"}
                >
                  {isExporting ? (
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="m12 2a10 10 0 0 1 10 10h-4a6 6 0 0 0-6-6v-4z"></path>
                    </svg>
                  ) : (
                    <Download className="h-4 w-4" />
                  )}
                </button>
                <span className="text-sm text-muted-foreground px-2">
                  {Math.round(scale * 100)}%
                </span>
                {process.env.NODE_ENV === 'development' && (
                  <span className="text-xs text-muted-foreground/70 px-2 py-1 bg-muted/50 rounded">
                    Cache: {mermaidCache.getStats().size}/{mermaidCache.getStats().maxSize}
                  </span>
                )}
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
                  transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
                  transformOrigin: 'center center'
                }}
              >
                <div
                  ref={modalRef}
                  className="mermaid pointer-events-none"
                  style={{
                    minHeight: '200px',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center'
                  }}
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