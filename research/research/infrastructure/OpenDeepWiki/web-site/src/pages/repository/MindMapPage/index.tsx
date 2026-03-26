
import { useEffect, useState, useRef } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Loader2, AlertCircle, RefreshCw, Maximize, Minimize, Download } from 'lucide-react'
import { useRepositoryDetailStore } from '@/stores/repositoryDetail.store'
import { fetchService } from '@/services/fetch'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardContent } from '@/components/ui/card'
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from '@/components/ui/tooltip'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import 'mind-elixir/style'

interface MiniMapResult {
  title: string
  url: string
  nodes: MiniMapResult[]
}

interface MindMapResponse {
  code: number
  message: string
  data: MiniMapResult
}

interface MindElixirNode {
  topic: string
  id: string
  root?: boolean
  expanded?: boolean
  hyperLink?: string
  children?: MindElixirNode[]
}

class MindMapService {
  async getMindMap(
    owner: string,
    repo: string,
    branch?: string,
    languageCode?: string
  ): Promise<MindMapResponse> {
    try {
      const params = new URLSearchParams({
        owner,
        name: repo
      })

      if (branch) {
        params.append('branch', branch)
      }

      if (languageCode) {
        params.append('languageCode', languageCode)
      }

      const response = await fetchService.get<MindMapResponse>(
        `/api/Warehouse/MiniMap?${params.toString()}`
      )
      return response
    } catch (error) {
      console.error('Failed to fetch mind map:', error)
      throw error
    }
  }
}

const mindMapService = new MindMapService()

// 转换为 mind-elixir 数据格式
const convertToMindElixirData = (miniMapData: MiniMapResult): MindElixirNode => {
  let nodeIdCounter = 0

  const buildMindNode = (node: MiniMapResult, isRoot = false): MindElixirNode => {
    const mindNode: MindElixirNode = {
      topic: node.title,
      id: isRoot ? 'root' : `node_${nodeIdCounter++}`,
      hyperLink: node.url
    }

    if (isRoot) {
      mindNode.root = true
    }

    if (node.nodes && node.nodes.length > 0) {
      mindNode.expanded = true
      mindNode.children = node.nodes.map(child => buildMindNode(child))
    }

    return mindNode
  }

  return buildMindNode(miniMapData, true)
}



export default function MindMapPage({ className }: { className?: string }) {
  const { owner, name } = useParams<{ owner: string; name: string }>()
  const [searchParams] = useSearchParams()
  const { t, i18n } = useTranslation()
  const { selectedBranch } = useRepositoryDetailStore()
  const [loading, setLoading] = useState(true)
  const [mindMapData, setMindMapData] = useState<MiniMapResult | null>(null)
  const [error, setError] = useState<string>('')
  const [isFullscreen, setIsFullscreen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const mindRef = useRef<any>(null)
  const panCleanupRef = useRef<(() => void) | null>(null)

  const branch = searchParams.get('branch') || selectedBranch || 'main'

  const fetchMindMap = async () => {
    if (!owner || !name) return

    setLoading(true)
    try {
      const response = await mindMapService.getMindMap(
        owner,
        name,
        branch,
        i18n.language
      )

      if (response.code === 200 && response.data) {
        setMindMapData(response.data)
        const mindData = convertToMindElixirData(response.data)
        setTimeout(() => initMindElixir(mindData), 100)
      } else {
        setError(response.message || t('repository.mindMap.loadFailed'))
      }
    } catch (err: any) {
      console.error('Failed to fetch mind map:', err)
      setError(err?.message || t('repository.mindMap.loadFailed'))
    } finally {
      setLoading(false)
    }
  }


  // 初始化 Mind Elixir
  const initMindElixir = async (mindData: MindElixirNode) => {
    if (!containerRef.current) return

    // 动态导入 mind-elixir
    const MindElixir = (await import('mind-elixir')).default

    // 销毁旧实例
    if (panCleanupRef.current) {
      panCleanupRef.current()
      panCleanupRef.current = null
    }

    if (mindRef.current) {
      mindRef.current.destroy?.()
    }

    const options = {
      el: containerRef.current,
      direction: MindElixir.SIDE,
      draggable: true,
      contextMenu: true,
      toolBar: false,
      nodeMenu: true,
      keypress: true,
      locale: 'en' as const,
      overflowHidden: false,
      mainLinkStyle: 2,
      mouseSelectionButton: 0 as const,
      allowFreeTransform: true,
      mouseMoveThreshold: 5,
      primaryLinkStyle: 1,
      primaryNodeHorizontalGap: 65,
      primaryNodeVerticalGap: 25,
      theme: {
        name: 'Minimal',
        palette: [
          '#0f172a', '#475569', '#64748b', '#94a3b8',
          '#cbd5e1', '#e2e8f0', '#f1f5f9', '#f8fafc',
          '#0ea5e9', '#06b6d4'
        ],
        cssVar: {
          '--main-color': '#0f172a',
          '--main-bgcolor': '#2f2020',
          '--color': '#1e293b',
          '--bgcolor': '#f8fafc',
          '--panel-color': '255, 255, 255',
          '--panel-bgcolor': '248, 250, 252',
        },
      },
    }

    const mind = new MindElixir(options)

    const mindElixirData = {
      nodeData: mindData,
      linkData: {}
    }

    mind.init(mindElixirData)

    const ensureFit = () => {
      mind.scaleFit()
      mind.toCenter()
    }

    if (typeof window !== 'undefined') {
      requestAnimationFrame(ensureFit)
      setTimeout(ensureFit, 150)
    } else {
      ensureFit()
    }

    const panState = {
      isPanning: false,
      lastX: 0,
      lastY: 0
    }

    const isNodeElement = (target: EventTarget | null) => {
      if (!(target instanceof HTMLElement)) return false
      return Boolean(
        target.closest('me-root') ||
          target.closest('me-parent') ||
          target.closest('me-tpc') ||
          target.closest('#input-box')
      )
    }

    const handleMouseDown = (event: MouseEvent) => {
      if (event.button !== 0) return
      if (isNodeElement(event.target)) return

      panState.isPanning = true
      panState.lastX = event.clientX
      panState.lastY = event.clientY
      if (mind.container) {
        mind.container.style.cursor = 'grabbing'
        mind.container.classList.add('grabbing')
      }
      event.preventDefault()
    }

    const handleMouseMove = (event: MouseEvent) => {
      if (!panState.isPanning) return

      const dx = event.clientX - panState.lastX
      const dy = event.clientY - panState.lastY

      if (dx !== 0 || dy !== 0) {
        mind.move(dx, dy)
        panState.lastX = event.clientX
        panState.lastY = event.clientY
      }
    }

    const stopPanning = () => {
      if (!panState.isPanning) return
      panState.isPanning = false
      if (mind.container) {
        mind.container.style.cursor = 'grab'
        mind.container.classList.remove('grabbing')
      }
    }

    mind.container?.addEventListener('mousedown', handleMouseDown)
    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseup', stopPanning)
    mind.container?.addEventListener('mouseleave', stopPanning)

    panCleanupRef.current = () => {
      mind.container?.removeEventListener('mousedown', handleMouseDown)
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', stopPanning)
      mind.container?.removeEventListener('mouseleave', stopPanning)
      if (mind.container) {
        mind.container.style.cursor = ''
        mind.container.classList.remove('grabbing')
      }
    }

    if (mind.container) {
      mind.container.style.cursor = 'grab'
      mind.container.classList.remove('grabbing')
    }

    mind.bus.addListener('selectNode', (node: any) => {
      if (node.hyperLink) {
        window.open(node.hyperLink, '_blank')
      }
    })

    mind.bus.addListener('operation', (operation: any) => {
      console.log('Mind map operation:', operation)
    })

    mindRef.current = mind

    const resizeObserver = new ResizeObserver(() => {
      if (mind && containerRef.current) {
        mind.refresh()
      }
    })

    resizeObserver.observe(containerRef.current)

    return () => {
      resizeObserver.disconnect()
      if (panCleanupRef.current) {
        panCleanupRef.current()
        panCleanupRef.current = null
      }
      if (mind) {
        mind.destroy?.()
      }
    }
  }

  // 全屏切换
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
    setTimeout(() => {
      if (mindRef.current && containerRef.current) {
        mindRef.current.refresh()
      }
    }, 100)
  }

  // 导出为图片
  const exportImage = async () => {
    if (!mindRef.current) {
      console.error('思维导图未初始化')
      return
    }

    try {
      const blob = await mindRef.current.exportPng()
      if (blob) {
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${owner}-${name}-mindmap.png`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Export error:', error)
    }
  }

  useEffect(() => {
    fetchMindMap()
  }, [owner, name, branch, i18n.language])

  useEffect(() => {
    return () => {
      if (panCleanupRef.current) {
        panCleanupRef.current()
        panCleanupRef.current = null
      }
      if (mindRef.current) {
        mindRef.current.destroy?.()
      }
    }
  }, [])

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[60vh]">
        <Skeleton className="w-32 h-32" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <AlertCircle className="h-12 w-12 text-destructive" />
        <div className="text-center space-y-2">
          <p className="text-lg font-medium">{t('repository.mindMap.error')}</p>
          <p className="text-sm text-muted-foreground">{error}</p>
          <p className="text-xs text-muted-foreground">
            {owner}/{name} - {branch}
          </p>
        </div>
        <Button onClick={fetchMindMap} variant="outline" className="gap-2">
          <RefreshCw className="h-4 w-4" />
          {t('common.retry')}
        </Button>
      </div>
    )
  }

  return (
    <TooltipProvider>
      <div className="h-full">
        <Card className={`
          relative flex flex-col
          ${isFullscreen ? 'h-screen fixed top-0 left-0 w-screen z-[9999]' : 'h-[85vh]'}
          transition-all duration-300 border-border/50 shadow-sm
        `}>
        <CardHeader>
          <div className="flex justify-between  sm:flex-nowrap">
            <div className="flex justify-end">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={fetchMindMap}
                    className="h-8 w-8"
                  >
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{t('repository.mindMap.refresh')}</p>
                </TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={exportImage}
                    className="h-8 w-8"
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{t('repository.mindMap.exportImage')}</p>
                </TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={toggleFullscreen}
                    className="h-8 w-8"
                  >
                    {isFullscreen ? <Minimize className="h-4 w-4" /> : <Maximize className="h-4 w-4" />}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{isFullscreen ? t('repository.mindMap.fullscreenExit') : t('repository.mindMap.fullscreenEnter')}</p>
                </TooltipContent>
              </Tooltip>
            </div>
          </div>
        </CardHeader>
        <CardContent className={`
          ${isFullscreen ? 'h-[calc(100vh-80px)]' : 'h-[calc(85vh-80px)]'}
          p-0 relative
          w-full
        `}>
          <div
            ref={containerRef}
            className={`
              w-full h-full relative select-none
              bg-gradient-to-br from-slate-50 to-slate-200
              ${isFullscreen ? 'rounded-none' : 'rounded-lg'}
            `}
            style={{
              touchAction: 'none',
              WebkitUserSelect: 'none',
            }}
            onContextMenu={(e) => {
              e.preventDefault()
            }}
            onMouseDown={(e) => {
              if (e.button === 2) {
                e.preventDefault()
              }
            }}
            onTouchStart={(e) => {
              if (e.touches.length > 1) {
                e.preventDefault()
              }
            }}
            onTouchMove={(e) => {
              e.preventDefault()
            }}
            onDragStart={(e) => {
              e.preventDefault()
            }}
          />

          <div className="absolute bottom-4 right-4 bg-black/70 text-white px-3 py-2 rounded text-xs z-[1000]">
            {t('repository.mindMap.helpText')}
          </div>
        </CardContent>
      </Card>

      <style jsx global>{`
        .mind-elixir {
          width: 100%;
          height: 100%;
          touch-action: none !important;
          user-select: none !important;
          WebkitUserSelect: none !important;
          MozUserSelect: none !important;
          MsUserSelect: none !important;
        }

        .mind-elixir .map-container {
          background: transparent !important;
          touch-action: none !important;
          -ms-touch-action: none !important;
          -webkit-touch-callout: none !important;
          cursor: grab;
        }

        .mind-elixir .map-container.is-panning,
        .mind-elixir .map-container.grabbing {
          cursor: grabbing !important;
        }

        .mind-elixir .node-container {
          cursor: pointer;
          touch-action: none !important;
        }

        .mind-elixir .node-container:hover {
          opacity: 0.9;
          transform: scale(1.02);
          transition: all 0.2s ease-in-out;
        }

        .mind-elixir .line {
          stroke: #475569;
          stroke-width: 1.5;
        }

        .mind-elixir .node {
          border-radius: 8px;
          border: 1px solid #e2e8f0;
          background: #ffffff;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          touch-action: none !important;
          font-family: inherit;
        }

        .mind-elixir .root {
          background: linear-gradient(135deg, #0f172a, #1e293b) !important;
          color: white !important;
          font-weight: 600;
          font-size: 16px;
          border: none !important;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        }

        .mind-elixir .primary {
          background: #f8fafc !important;
          border-color: #cbd5e1 !important;
          color: #334155 !important;
          font-weight: 500;
        }

        .mind-elixir .context-menu {
          border-radius: 8px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
          border: 1px solid #e2e8f0;
          z-index: 9999 !important;
          background: white;
        }

        html {
          -ms-touch-action: none !important;
          touch-action: none !important;
        }

        body {
          -ms-touch-action: manipulation !important;
          touch-action: manipulation !important;
        }

        * {
          -webkit-touch-callout: none !important;
          -webkit-user-select: none !important;
          -khtml-user-select: none !important;
          -moz-user-select: none !important;
          -ms-user-select: none !important;
        }

        input, textarea, [contenteditable] {
          -webkit-user-select: text !important;
          -moz-user-select: text !important;
          -ms-user-select: text !important;
          user-select: text !important;
        }

        .mind-elixir ::-webkit-scrollbar {
          width: 6px;
          height: 6px;
        }

        .mind-elixir ::-webkit-scrollbar-track {
          background: #f1f5f9;
          border-radius: 3px;
        }

        .mind-elixir ::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 3px;
        }

        .mind-elixir ::-webkit-scrollbar-thumb:hover {
          background: #94a3b8;
        }
      `}</style>
      </div>
    </TooltipProvider>
  )
}