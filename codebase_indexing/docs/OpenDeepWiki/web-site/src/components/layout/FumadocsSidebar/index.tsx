// Fumadocs风格的侧边栏组件

import React, { useState, useMemo, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { cn } from '@/lib/utils'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger
} from '@/components/ui/tooltip'
import {
  Search,
  GitBranch,
  Github,
  PanelLeftClose,
  PanelLeftOpen,
  Hash,
  Loader2,
  Lock
} from 'lucide-react'
import { Progress } from '@/components/ui/progress'
import type { DocumentNode } from '@/components/repository/DocumentTree'

interface MenuItem {
  id: string
  label: string
  icon?: React.ReactNode
  path?: string
  children?: MenuItem[]
  badge?: string
  disabled?: boolean  // 是否禁用
  progress?: number   // 生成进度
}

interface FumadocsSidebarProps {
  owner: string
  name: string
  branches: string[]
  selectedBranch: string
  onBranchChange: (branch: string) => void
  documentNodes: DocumentNode[]
  selectedPath?: string
  onSelectNode?: (node: DocumentNode) => void
  loading?: boolean
  className?: string
  sidebarOpen?: boolean
  onSidebarToggle?: () => void
}

export const FumadocsSidebar: React.FC<FumadocsSidebarProps> = React.memo(({
  owner,
  name,
  branches,
  selectedBranch,
  onBranchChange,
  documentNodes,
  selectedPath,
  onSelectNode,
  loading,
  className,
  sidebarOpen = true,
  onSidebarToggle
}) => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [loadingItemId, setLoadingItemId] = useState<string | null>(null)


  // 将DocumentNode转换为MenuItem - 使用 useMemo 优化性能
  const menuItems = useMemo(() => {
    const convertToMenuItem = (node: DocumentNode): MenuItem => {
      // 构建包含分支参数的路径
      const basePath = `/${owner}/${name}/${encodeURIComponent(node.path)}`
      const pathWithBranch = selectedBranch && selectedBranch !== 'main'
        ? `${basePath}?branch=${selectedBranch}`
        : basePath

      return {
        id: node.id,
        label: node.name || 'Untitled',  // Fallback to 'Untitled' if name is null/undefined
        // 所有节点都可以点击，并包含分支信息
        path: pathWithBranch,
        disabled: node.disabled,  // 传递禁用状态
        progress: node.progress,  // 传递进度
        children: node.children?.map(convertToMenuItem)
      }
    }

    return documentNodes.map(convertToMenuItem)
  }, [documentNodes, owner, name, selectedBranch])


  // 处理菜单点击 - 使用 useCallback 优化性能
  const handleMenuClick = useCallback(async (item: MenuItem, event?: React.MouseEvent) => {
    // 如果菜单项被禁用，不处理点击
    if (item.disabled) {
      console.log('Menu item is disabled:', item.label, item)
      event?.preventDefault()
      event?.stopPropagation()
      return
    }

    if (item.path) {
      // 设置加载状态
      setLoadingItemId(item.id)

      try {
        // 先导航到页面
        navigate(item.path)

        // 查找并选择节点
        const findNode = (nodes: DocumentNode[], id: string): DocumentNode | null => {
          for (const node of nodes) {
            if (node.id === id) return node
            if (node.children) {
              const found = findNode(node.children, id)
              if (found) return found
            }
          }
          return null
        }

        const node = findNode(documentNodes, item.id)
        if (node && onSelectNode) {
          onSelectNode(node)
        }
      } catch (error) {
        console.error('Navigation error:', error)
      } finally {
        // 延迟清除加载状态，给页面加载一些时间
        setTimeout(() => {
          setLoadingItemId(null)
        }, 500)
      }
    }
  }, [navigate, documentNodes, onSelectNode])

  // 渲染菜单项 - 使用 useCallback 优化性能
  const renderMenuItem = useCallback((item: MenuItem, level: number = 0): React.ReactNode => {
    const hasChildren = item.children && item.children.length > 0
    const isSelected = item.path === selectedPath ||
      item.path === window.location.pathname ||
      window.location.pathname.includes(item.path + '/')
    const isLoading = loadingItemId === item.id
    const isDisabled = item.disabled || false
    const hasProgress = typeof item.progress === 'number'

    // Fumadocs 风格的缩进，增大字体和间距
    const indent = level * 16 + 16 // 基础16px + 每级16px

    if (hasChildren) {
      return (
        <div key={item.id} className="group">
          <button
            className={cn(
              "flex items-center w-full py-2 px-3 text-sm transition-all duration-150 rounded-md relative",
              !isDisabled && "hover:bg-accent/50 hover:text-accent-foreground",
              isSelected && !isDisabled && "bg-accent text-accent-foreground font-medium",
              isLoading && "opacity-70",
              isDisabled && "opacity-50 cursor-not-allowed"
            )}
            style={{ paddingLeft: `${indent}px` }}
            onClick={(e) => {
              if (isDisabled || isLoading) {
                e.preventDefault()
                e.stopPropagation()
                console.log('Button click prevented - disabled:', isDisabled, 'loading:', isLoading)
                return
              }
              handleMenuClick(item, e)
            }}
            disabled={isDisabled || isLoading}
          >
            {isLoading && (
              <Loader2 className="mr-2 h-3 w-3 animate-spin flex-shrink-0" />
            )}
            {isDisabled && !isLoading && (
              <Lock className="mr-2 h-3 w-3 flex-shrink-0 text-muted-foreground" />
            )}
            <span className="truncate flex-1 text-left font-normal">{item.label}</span>
            {item.badge && (
              <span className="ml-2 text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded-full font-medium flex-shrink-0">
                {item.badge}
              </span>
            )}
          </button>
          {hasProgress && (
            <div className="px-4 mt-1 mb-1">
              <div className="flex items-center gap-2">
                <Progress value={item.progress || 0} className="h-2 flex-1" />
                <span className="text-[10px] text-muted-foreground font-mono min-w-[30px]">
                  {Math.round(item.progress || 0)}%
                </span>
              </div>
              {isDisabled && (
                <span className="text-[10px] text-muted-foreground">生成中...</span>
              )}
            </div>
          )}
          <div className="pb-1">
            {item.children?.map(child => renderMenuItem(child, level + 1))}
          </div>
        </div>
      )
    }

    return (
      <div key={item.id} className="relative">
        <button
          className={cn(
            "flex items-center w-full py-2 px-3 text-sm transition-all duration-150 rounded-md group relative",
            !isDisabled && "hover:bg-accent/50 hover:text-accent-foreground",
            isSelected && !isDisabled ? "bg-accent text-accent-foreground font-medium" : "text-muted-foreground",
            isLoading && "opacity-70",
            isDisabled && "opacity-50 cursor-not-allowed"
          )}
          style={{ paddingLeft: `${indent + 16}px` }} // 叶节点额外缩进
          onClick={(e) => {
            if (isDisabled || isLoading) {
              e.preventDefault()
              e.stopPropagation()
              console.log('Leaf button click prevented - disabled:', isDisabled, 'loading:', isLoading, 'item:', item)
              return
            }
            handleMenuClick(item, e)
          }}
          disabled={isDisabled || isLoading}
        >
          {isLoading && (
            <Loader2 className="mr-2 h-3 w-3 animate-spin flex-shrink-0" />
          )}
          {isDisabled && !isLoading && (
            <Lock className="mr-2 h-3 w-3 flex-shrink-0 text-muted-foreground" />
          )}
          <span className="truncate flex-1 text-left font-normal">{item.label}</span>
          {item.badge && (
            <span className="ml-2 text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded-full font-medium flex-shrink-0">
              {item.badge}
            </span>
          )}
        </button>
        {hasProgress && (
          <div className="px-4 mt-1 mb-1" style={{ paddingLeft: `${indent + 32}px` }}>
            <div className="flex items-center gap-2">
              <Progress value={item.progress || 0} className="h-2 flex-1" />
              <span className="text-[10px] text-muted-foreground font-mono min-w-[30px]">
                {Math.round(item.progress || 0)}%
              </span>
            </div>
            {isDisabled && (
              <span className="text-[10px] text-muted-foreground">生成中...</span>
            )}
          </div>
        )}
      </div>
    )
  }, [handleMenuClick, selectedPath, loadingItemId])



  return (
    <div
      className={cn(
        "flex flex-col h-full bg-background border-r border-border",
        className
      )}
      style={{
        transform: 'translateZ(0)', // 
        backfaceVisibility: 'hidden'
      }}
    >
      {/* 搜索框 */}
      <div className="px-3 py-2 border-b border-border/50">
        <div className="relative flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="搜索文档..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 pr-14 h-8 text-sm bg-accent/30 border-0 focus:bg-accent/50 transition-colors placeholder:text-muted-foreground/60"
            />
            <kbd className="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none inline-flex h-4 select-none items-center gap-0.5 rounded border border-border/50 bg-background px-1 font-mono text-[10px] font-medium text-muted-foreground">
              <span className="text-[10px]">⌘</span>K
            </kbd>
          </div>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 hover:bg-accent/50 flex-shrink-0"
                  onClick={onSidebarToggle}
                  disabled={!onSidebarToggle}
                >
                  {sidebarOpen ? (
                    <PanelLeftClose className="h-3.5 w-3.5" />
                  ) : (
                    <PanelLeftOpen className="h-3.5 w-3.5" />
                  )}
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p className="text-xs">
                  {sidebarOpen
                    ? t('repository.layout.collapseSidebar')
                    : t('repository.layout.expandSidebar')}
                </p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>

      {/* 导航内容 */}
      <ScrollArea className="flex-1">
        <div className="px-2 py-1 space-y-1">
          <button
            className={cn(
              "w-full flex items-center px-3 py-1.5 text-sm rounded-md transition-all duration-150",
              window.location.pathname.includes('/mindmap')
                ? "bg-accent text-accent-foreground font-medium"
                : "text-muted-foreground hover:text-accent-foreground hover:bg-accent/50"
            )}
            onClick={() => navigate(`/${owner}/${name}/mindmap`)}
          >
            <Hash className="mr-2 h-3.5 w-3.5 flex-shrink-0" />
            {t('repository.layout.mindMap')}
          </button>

          {/* 分支选择器 */}
          <div className="px-3 py-2">
            <div className="flex items-center gap-2">
              <GitBranch className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
              <Select value={selectedBranch} onValueChange={onBranchChange} disabled={loading || branches.length === 0}>
                <SelectTrigger className="h-7 text-sm bg-accent/30 border-0 hover:bg-accent/50 transition-colors">
                  <SelectValue placeholder={t('repository.layout.selectBranch')} />
                </SelectTrigger>
                <SelectContent>
                  {branches.map(branch => (
                    <SelectItem key={branch} value={branch} className="text-sm">{branch}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* 分隔线 */}
          <div className="h-px bg-border/30 mx-2 my-3" />

          {/* 文档部分 */}
          <div className="space-y-0.5">
            {menuItems.length > 0 ? (
              menuItems
                .filter(item => !searchQuery ||
                  (item.label && item.label.toLowerCase().includes(searchQuery.toLowerCase())))
                .map(item => renderMenuItem(item))
            ) : (
              <p className="text-xs text-muted-foreground/60 text-center py-4 px-6">
                {t('repository.layout.noDocuments')}
              </p>
            )}
          </div>
        </div>
      </ScrollArea>

      {/* 底部信息 */}
      <div className="px-3 py-2 border-t border-border/50">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground/70 font-mono">
            {owner}/{name}
          </span>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 hover:bg-accent/50"
                  onClick={() => window.open(`https://github.com/${owner}/${name}`, '_blank')}
                >
                  <Github className="h-3 w-3" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p className="text-xs">{t('common.viewOnGithub')}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>
    </div>
  )
})

FumadocsSidebar.displayName = 'FumadocsSidebar'

export default FumadocsSidebar