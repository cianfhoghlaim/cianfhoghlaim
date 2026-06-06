import { useEffect, useState } from 'react'
import { Outlet, useParams, useNavigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { FumadocsSidebar } from '@/components/layout/FumadocsSidebar'
import { ThemeToggle } from '@/components/theme-toggle'
import { useRepositoryDetailStore } from '@/stores/repositoryDetail.store'
import { useChatStore } from '@/stores/chat.store'
import { warehouseService } from '@/services/warehouse.service'
import { toast } from 'sonner'
import { useAuth } from '@/hooks/useAuth'
import { FloatingChatButton } from '@/components/chat/FloatingChatButton'
import { ChatPanel } from '@/components/chat/ChatPanel'
import {
  Github,
  Home,
  Download,
  ChevronLeft,
  Menu,
  X,
  Search,
  PanelLeftOpen,
  ChevronRight,
  Hash,
  Book,
  AlertCircle
} from 'lucide-react'

interface RepositoryLayoutProps {
  children?: React.ReactNode
}

export const RepositoryLayout: React.FC<RepositoryLayoutProps> = ({ children }) => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const { owner, name } = useParams<{ owner: string; name: string }>()
  const [hasNavigatedToFirstDoc, setHasNavigatedToFirstDoc] = useState(false)

  // 使用store
  const {
    repository,
    branches,
    selectedBranch,
    loadingBranches,
    documentNodes,
    selectedNode,
    loadingDocuments,
    sidebarOpen,
    mobileMenuOpen,
    error,
    setRepository,
    fetchBranches,
    selectBranch,
    selectNode,
    setSidebarOpen,
    setMobileMenuOpen,
    clearError,
    reset
  } = useRepositoryDetailStore()

  const { isAuthenticated } = useAuth()
  const [isDownloading, setIsDownloading] = useState(false)

  // Chat state
  const { isOpen: isChatOpen, setOpen: setChatOpen, reset: resetChat } = useChatStore()

  // 处理节点选择
  const handleNodeSelect = (node: any) => {
    selectNode(node)
    // 导航到文档页面
    if (node.type === 'file' && owner && name) {
      const basePath = `/${owner}/${name}/${encodeURIComponent(node.path)}`
      const pathWithBranch = selectedBranch && selectedBranch !== 'main'
        ? `${basePath}?branch=${selectedBranch}`
        : basePath
      navigate(pathWithBranch)
    }
    // 移动端关闭菜单
    if (window.innerWidth < 1024) {
      setMobileMenuOpen(false)
    }
  }

  // 处理下载功能
  const handleDownload = async () => {
    if (!isAuthenticated) {
      toast.error(t('repository.layout.loginRequired'))
      navigate('/login')
      return
    }

    if (!repository?.id) {
      toast.error(t('repository.layout.downloadError'))
      return
    }

    setIsDownloading(true)
    try {
      await warehouseService.exportMarkdownZip(repository.id)
      toast.success(t('repository.layout.downloadSuccess'))
    } catch (error: any) {
      console.error('Download failed:', error)
      toast.error(error.message || t('repository.layout.downloadFailed'))
    } finally {
      setIsDownloading(false)
    }
  }

  // 检查是否为固定路由（不需要加载文档数据）
  const isFixedRoute = () => {
    const currentPath = location.pathname
    const basePath = `/${owner}/${name}`
    const subPath = currentPath.replace(basePath, '').replace(/^\//, '')

    // 固定路由列表
    const fixedRoutes = ['mindmap']
    return fixedRoutes.includes(subPath)
  }

  // 初始化
  useEffect(() => {
    if (owner && name) {
      // 清除之前的错误状态
      clearError()
      setRepository(owner, name)
      // 始终加载分支和文档数据（左侧菜单需要）
      fetchBranches()
    }

    return () => {
      // 组件卸载时重置store
      reset()
      // 重置聊天
      resetChat()
    }
  }, [owner, name])

  // 自动跳转到第一个文档
  useEffect(() => {
    // 只在仓库页面（不是具体文档页面）且有文档数据时执行自动跳转
    const isRepositoryRoot = location.pathname === `/${owner}/${name}` || location.pathname === `/${owner}/${name}/`
    if (
      isRepositoryRoot &&
      !isFixedRoute() &&
      !hasNavigatedToFirstDoc &&
      documentNodes.length > 0 &&
      !loadingDocuments &&
      selectedNode?.path
    ) {
      const basePath = `/${owner}/${name}/${encodeURIComponent(selectedNode.path)}`
      const pathWithBranch = selectedBranch && selectedBranch !== 'main'
        ? `${basePath}?branch=${selectedBranch}`
        : basePath

      setHasNavigatedToFirstDoc(true)
      navigate(pathWithBranch, { replace: true })
    }
  }, [owner, name, location.pathname, documentNodes, selectedNode, loadingDocuments, hasNavigatedToFirstDoc, selectedBranch, navigate])

  // 重置自动跳转状态当仓库或分支改变时
  useEffect(() => {
    setHasNavigatedToFirstDoc(false)
  }, [owner, name, selectedBranch])

  // 设置页面标题
  useEffect(() => {
    if (owner && name) {
      const baseTitle = `${owner}/${name}`
      const branchInfo = selectedBranch && selectedBranch !== 'main' ? ` (${selectedBranch})` : ''
      document.title = `${baseTitle}${branchInfo} | KoalaWiki`
    }
    
    return () => {
      // 恢复默认标题
      document.title = 'KoalaWiki'
    }
  }, [owner, name, selectedBranch])

  // 移动端关闭菜单
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setMobileMenuOpen(false)
      }
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return (
    <div className="min-h-screen bg-background">
      {/* 顶部导航栏 */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur-sm supports-[backdrop-filter]:bg-background/60">
        <div className="flex h-16 items-center px-4 lg:px-6">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            {/* 移动端菜单按钮 */}
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden h-8 w-8"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </Button>


            <nav className="flex items-center gap-1 min-w-0 flex-1">
              {error ? (
                <div className="flex items-center gap-2 text-destructive">
                  <AlertCircle className="h-4 w-4" />
                  <span className="text-sm font-medium">{t('repository.layout.repositoryNotFound')}</span>
                </div>
              ) : (
                <>
                  <span className="text-sm font-medium text-muted-foreground hover:text-foreground cursor-pointer">
                    {owner}
                  </span>
                  <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/60" />
                  <span className="text-sm font-semibold text-foreground truncate">
                    {name}
                  </span>
                </>
              )}
            </nav>
          </div>

          {/* 右侧操作按钮 */}
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="hidden lg:flex h-8 px-2"
              disabled
            >
              <Search className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-8 px-2"
              onClick={handleDownload}
              disabled={isDownloading || !repository}
              title={t('repository.layout.downloadTooltip')}
            >
              {isDownloading ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
              ) : (
                <Download className="h-4 w-4" />
              )}
            </Button>
            <ThemeToggle />
            <Button
              variant="ghost"
              size="sm"
              className="h-8 px-2"
              onClick={() => window.open(`https://github.com/${owner}/${name}`, '_blank')}
            >
              <Github className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      <div className="flex relative">
        <aside
          className={cn(
            "hidden lg:block min-h-[calc(100vh-4rem)] fixed left-0 z-10",
            "w-72 bg-background border-r border-border",
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          )}
          style={{
            transition: 'transform 300ms cubic-bezier(0.4, 0, 0.2, 1)',
            willChange: 'transform',
            backfaceVisibility: 'hidden',
            perspective: '1000px'
          }}
        >
          {owner && name && (
            <FumadocsSidebar
              owner={owner}
              name={name}
              branches={branches}
              selectedBranch={selectedBranch}
              onBranchChange={selectBranch}
              documentNodes={documentNodes}
              selectedPath={selectedNode?.path}
              onSelectNode={handleNodeSelect}
              loading={loadingBranches || loadingDocuments}
              className="h-[calc(100vh-4rem)]"
              sidebarOpen={sidebarOpen}
              onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}
            />
          )}
        </aside>

        {/* 侧边栏 - 移动端 */}
        {mobileMenuOpen && (
          <>
            <div
              className="fixed inset-0 z-40 bg-black/50 lg:hidden"
              onClick={() => setMobileMenuOpen(false)}
            />
            <aside className="fixed left-0 top-16 z-40 h-[calc(100vh-4rem)] w-72 bg-background lg:hidden">
              {owner && name && (
                <FumadocsSidebar
                  owner={owner}
                  name={name}
                  branches={branches}
                  selectedBranch={selectedBranch}
                  onBranchChange={selectBranch}
                  documentNodes={documentNodes}
                  selectedPath={selectedNode?.path}
                  onSelectNode={handleNodeSelect}
                  loading={loadingBranches || loadingDocuments}
                  className="h-full"
                  sidebarOpen={true}
                  onSidebarToggle={() => setMobileMenuOpen(false)}
                />
              )}
            </aside>
          </>
        )}

        {/* 主内容区 - 优化布局 */}
        <main
          className={cn(
            "h-[calc(100vh-4rem)] relative flex flex-col w-full",
            sidebarOpen ? "lg:ml-72" : "lg:ml-0"
          )}
          style={{
            transition: 'margin-left 300ms cubic-bezier(0.4, 0, 0.2, 1)',
            willChange: 'margin-left'
          }}
        >
          {/* 悬浮的侧边栏切换按钮 - 优化动画 */}
          <Button
            variant="outline"
            size="icon"
            onClick={() => setSidebarOpen(true)}
            className={cn(
              "fixed left-4 top-24 z-30 shadow-lg",
              "bg-background/95 backdrop-blur-sm border-border/50",
              "hover:bg-accent hover:text-accent-foreground",
              "hidden lg:flex h-8 w-8",
              sidebarOpen ? "opacity-0 pointer-events-none -translate-x-16" : "opacity-100 pointer-events-auto translate-x-0"
            )}
            style={{
              transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
              willChange: 'transform, opacity'
            }}
          >
            <PanelLeftOpen className="h-4 w-4" />
          </Button>

          <div className="flex-1 overflow-hidden">
            {error && !isFixedRoute() ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center space-y-3">
                  <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto" />
                  <div className="space-y-1">
                    <h3 className="text-lg font-semibold">{t('repository.layout.repositoryNotFound')}</h3>
                    <p className="text-sm text-muted-foreground">{t('repository.layout.checkRepositoryAddress')}</p>
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => navigate('/')}
                    className="mt-4"
                  >
                    <Home className="h-4 w-4 mr-2" />
                    {t('repository.layout.backToHome')}
                  </Button>
                </div>
              </div>
            ) : (
              children || <Outlet context={{ branch: selectedBranch, selectedNode }} />
            )}
          </div>
        </main>

        {/* Chat Components */}
        {owner && name && !error && (
          <>
            <FloatingChatButton
              onClick={() => setChatOpen(true)}
              className={cn(isChatOpen && 'pointer-events-none opacity-0')}
            />

            <ChatPanel
              isOpen={isChatOpen}
              onClose={() => setChatOpen(false)}
              organizationName={owner}
              repositoryName={name}
            />
          </>
        )}
      </div>
    </div>
  )
}

export default RepositoryLayout