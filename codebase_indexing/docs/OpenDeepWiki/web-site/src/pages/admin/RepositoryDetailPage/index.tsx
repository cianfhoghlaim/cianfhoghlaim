// 仓库详情管理页面

import React, { useState, useEffect, useCallback, useMemo, lazy, Suspense } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog'
import { Progress } from '@/components/ui/progress'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'

import {
  ChevronLeft,
  ChevronDown,
  ChevronRight,
  File,
  Save,
  RefreshCw,
  FileText,
  Code,
  Image,
  Database,
  Search,
  Edit3,
  Trash2,
  Clock,
  Activity,
  AlertCircle,
  CheckCircle,
  Download,
  Shield,
  Cog,
  Eye,
  ExternalLink,
  Copy,
  Sparkles,
  Loader2
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { type WarehouseInfo, type RepositoryLogDto, type WarehouseSyncRecord, repositoryService } from '@/services/admin.service'
import { toast } from 'sonner'
import { DocumentQualityEvaluation } from '@/components/DocumentQuality'
import WikiGenerationManagement from '@/components/WikiGeneration/WikiGenerationManagement'

// 延迟加载 MarkdownEditor 组件
const MarkdownEditor = lazy(() => import('@/components/MarkdownEditor'))

interface TreeNode {
  id: string
  name: string
  title?: string
  key?: string
  isLeaf?: boolean
  type?: 'file' | 'folder'
  path?: string
  children?: TreeNode[]
  size?: number
  lastModified?: string
  content?: string // 明确定义为字符串类型
  catalog?: DocumentCatalog
}

interface DocumentCatalog {
  id: string
  name: string
  url: string
  prompt?: string
  parentId?: string
  order: number
  warehouseId: string
  isDeleted: boolean
  isCompleted: boolean
  createdAt: string
}

interface RepositoryStats {
  totalDocuments: number
  totalFiles: number
  lastSyncTime?: string
  processingStatus: string
  completedDocuments: number
  pendingDocuments: number
  fileTypes: { [key: string]: number }
  syncHistory: SyncRecord[]
}

interface SyncRecord {
  id: string
  timestamp: string
  status: 'success' | 'failed' | 'processing'
  message: string
  filesChanged: number
}


const RepositoryDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const { t } = useTranslation('admin')
  const navigate = useNavigate()

  // 状态管理
  const [repository, setRepository] = useState<WarehouseInfo | null>(null)
  const [treeData, setTreeData] = useState<TreeNode[]>([])
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null)
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [stats, setStats] = useState<RepositoryStats | null>(null)
  const [logs, setLogs] = useState<RepositoryLogDto[]>([])
  const [activeTab, setActiveTab] = useState('documents')
  const [editMode, setEditMode] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [syncDialogOpen, setSyncDialogOpen] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [syncRecords, setSyncRecords] = useState<WarehouseSyncRecord[]>([])
  const [updatingSyncSetting, setUpdatingSyncSetting] = useState(false)
  const [aiGenerateDialog, setAiGenerateDialog] = useState(false)
  const [aiGeneratePrompt, setAiGeneratePrompt] = useState('')
  const [aiGenerating, setAiGenerating] = useState(false)
  const [editDialog, setEditDialog] = useState(false)
  const [editForm, setEditForm] = useState({
    name: '',
    description: '',
    enableSync: false
  })

  // 收集所有可展开的节点ID
  const collectExpandableNodes = useCallback((nodes: any[]): string[] => {
    const nodeIds: string[] = []

    const traverse = (nodeList: any[]) => {
      nodeList.forEach(node => {
        const nodeId = node.key || node.id || ''
        const isFolder = !node.isLeaf
        const hasChildren = isFolder && node.children && Array.isArray(node.children) && node.children.length > 0

        if (hasChildren) {
          nodeIds.push(nodeId)
          traverse(node.children)
        }
      })
    }

    traverse(nodes)
    return nodeIds
  }, [])

  // 加载仓库数据
  useEffect(() => {
    const loadRepositoryData = async () => {
      if (!id) return

      try {
        setLoading(true)

        // 获取仓库详情
        const repoResponse = await repositoryService.getRepositoryDetail(id)
        setRepository(repoResponse)

        // 获取文档目录树 - 使用DocumentCatalogs接口
        const { data } = await repositoryService.getDocumentCatalogs(id) as any
        if (data && Array.isArray(data)) {
          // 后端已经返回TreeNode格式的树形结构，直接使用
          setTreeData(data)

          // 自动展开所有可展开的节点
          const expandableNodeIds = collectExpandableNodes(data)
          setExpandedNodes(new Set(expandableNodeIds))
        } else {
          setTreeData([])
        }

        // 获取仓库统计信息
        await loadRepositoryStats(id)

        // 获取操作日志
        await loadRepositoryLogs(id)

        // 获取同步记录
        await loadSyncRecords(id)

      } catch (error) {
        console.error('Failed to load repository data:', error)
        toast.error(t('admin.repositories.detail.load_repository_data_failed'))
      } finally {
        setLoading(false)
      }
    }

    loadRepositoryData()
  }, [id])

  const loadRepositoryStats = async (repoId: string) => {
    try {
      // 从API获取统计数据
      const statsResponse = await repositoryService.getRepositoryStatsById(repoId)
      const stats: RepositoryStats = {
        totalDocuments: statsResponse.TotalDocuments || 0,
        totalFiles: statsResponse.TotalFiles || 0,
        lastSyncTime: statsResponse.LastSyncTime ? new Date(statsResponse.LastSyncTime).toISOString() : undefined,
        processingStatus: statsResponse.ProcessingStatus || 'Pending',
        completedDocuments: statsResponse.CompletedDocuments || 0,
        pendingDocuments: statsResponse.PendingDocuments || 0,
        fileTypes: {},
        syncHistory: []
      }
      setStats(stats)
    } catch (error) {
      console.error('Failed to load repository stats:', error)
      // 设置默认值
      setStats({
        totalDocuments: 0,
        totalFiles: 0,
        processingStatus: 'Pending',
        completedDocuments: 0,
        pendingDocuments: 0,
        fileTypes: {},
        syncHistory: []
      })
    }
  }

  const loadRepositoryLogs = async (repoId: string) => {
    try {
      const response = await repositoryService.getRepositoryLogs(repoId, 1, 20)
      setLogs(response.items || [])
    } catch (error) {
      console.error('Failed to load repository logs:', error)
    }
  }

  const loadSyncRecords = async (warehouseId: string) => {
    try {
      const response = await repositoryService.getWarehouseSyncRecords(warehouseId, 1, 10)
      setSyncRecords(response.items || [])
    } catch (error) {
      console.error('Failed to load sync records:', error)
    }
  }

  const handleNodeClick = useCallback((node: any, isExpandToggle: boolean = false) => {
    const nodeId = node.key || node.id || ''
    const isFolder = !node.isLeaf

    // 总是设置选中的节点（无论是文件夹还是文件）
    setSelectedNode(node)

    if (isFolder) {
      // 只有在点击展开按钮时才切换展开状态
      if (isExpandToggle) {
        setExpandedNodes(prev => {
          const newSet = new Set(prev)
          if (newSet.has(nodeId)) {
            newSet.delete(nodeId)
          } else {
            newSet.add(nodeId)
          }
          return newSet
        })
      }

      // 如果文件夹有内容可以加载，也加载内容
      if (node.catalog?.id) {
        loadFileContent(node.catalog.id)
      }
    } else {
      // 如果是文档目录，加载文件内容
      if (node.catalog?.id) {
        loadFileContent(node.catalog.id)
      }
    }
  }, [])

  const loadFileContent = async (catalogId: string) => {
    try {
      const { data } = await repositoryService.getFileContent(catalogId) as any
      // 确保content是字符串类型
      const contentStr = typeof data === 'string' ? data : String(data || '')
      setSelectedNode(prev => prev ? { ...prev, content: contentStr } : null)
    } catch (error) {
      console.error('Failed to load file content:', error)
    }
  }

  const handleContentChange = (content: string) => {
    if (selectedNode) {
      // 确保content是字符串类型
      const contentStr = typeof content === 'string' ? content : String(content || '')
      setSelectedNode({ ...selectedNode, content: contentStr })
    }
  }

  const handleSave = async () => {
    if (!selectedNode || !selectedNode.content || !id) return

    setSaving(true)
    try {
      // 确保content是字符串类型
      const contentStr = typeof selectedNode.content === 'string' ? selectedNode.content : String(selectedNode.content || '')
      // 调用API保存内容，传递仓库ID
      await repositoryService.saveFileContent(selectedNode.catalog!.id, contentStr)
      toast.success(t('admin.repositories.detail.file_save_success'))
    } catch (error) {
      toast.error(t('admin.repositories.detail.file_save_failed'))
    } finally {
      setSaving(false)
    }
  }

  const handleRefresh = async () => {
    if (!id) return

    setRefreshing(true)
    try {
      await repositoryService.refreshWarehouse(id)
      toast.success(t('admin.repositories.detail.repository_refresh_success'))

      // 重新加载数据
      setTimeout(() => {
        window.location.reload()
      }, 1000)
    } catch (error) {
      toast.error(t('admin.repositories.detail.repository_refresh_failed'))
    } finally {
      setRefreshing(false)
    }
  }

  const handleDelete = async () => {
    if (!id) return

    try {
      await repositoryService.deleteWarehouse(id)
      toast.success(t('admin.repositories.detail.repository_delete_success'))
      navigate('/admin/repositories')
    } catch (error) {
      toast.error(t('admin.repositories.detail.repository_delete_failed'))
    }
  }

  const handleSync = async () => {
    if (!id) return

    try {
      await repositoryService.triggerManualSync(id)
      toast.success(t('admin.repositories.detail.sync_task_started'))
      setSyncDialogOpen(false)

      // 刷新统计信息和同步记录
      await loadRepositoryStats(id)
      await loadSyncRecords(id)
    } catch (error) {
      toast.error(t('admin.repositories.detail.sync_start_failed'))
    }
  }

  const handleSyncToggle = async (enabled: boolean) => {
    if (!id) return

    setUpdatingSyncSetting(true)
    try {
      await repositoryService.updateWarehouseSync(id, { enableSync: enabled })
      setRepository(prev => prev ? { ...prev, enableSync: enabled } : null)
      toast.success(enabled ? '已启用自动同步' : '已禁用自动同步')
    } catch (error) {
      toast.error('更新同步设置失败')
    } finally {
      setUpdatingSyncSetting(false)
    }
  }

  const handleExport = async () => {
    if (!id) return

    try {
      const blob = await repositoryService.exportRepositoryMarkdown(id)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.style.display = 'none'
      a.href = url
      a.download = `${repository?.name || 'repository'}.zip`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      toast.success(t('admin.repositories.detail.export_success'))
    } catch (error) {
      toast.error(t('admin.repositories.detail.export_failed'))
    }
  }

  const handleEdit = () => {
    if (repository) {
      setEditForm({
        name: repository.name || '',
        description: repository.description || '',
        enableSync: repository.enableSync || false
      })
      setEditDialog(true)
    }
  }

  const handleSaveEdit = async () => {
    if (!id || !repository) return

    try {
      // 更新仓库信息
      await repositoryService.updateRepository(id, {
        name: editForm.name,
        description: editForm.description
      })

      // 如果同步设置有变化，单独更新
      if (editForm.enableSync !== repository.enableSync) {
        await repositoryService.updateWarehouseSync(id, { enableSync: editForm.enableSync })
      }

      toast.success('仓库信息更新成功')
      setEditDialog(false)

      // 重新加载仓库信息
      const repoResponse = await repositoryService.getRepositoryDetail(id)
      setRepository(repoResponse)
    } catch (error) {
      toast.error('更新失败，请稍后重试')
    }
  }

  const handleAiGenerate = async () => {
    if (!selectedNode?.catalog?.id) {
      toast.error('请先选择一个文档目录')
      return
    }

    setAiGenerating(true)
    try {
      // 调用AI生成API，提示词可为空，为空时使用原有提示词
      await repositoryService.generateFileContent(
        selectedNode.catalog.id,
        aiGeneratePrompt || undefined
      )

      toast.success('AI生成任务已启动，请稍后刷新查看结果')
      setAiGenerateDialog(false)
      setAiGeneratePrompt('')

      // 5秒后自动刷新内容
      setTimeout(async () => {
        if (selectedNode?.catalog?.id) {
          await loadFileContent(selectedNode.catalog.id)
          toast.info('文档内容已刷新')
        }
      }, 5000)
    } catch (error) {
      console.error('AI生成失败:', error)
      toast.error('AI生成失败，请稍后重试')
    } finally {
      setAiGenerating(false)
    }
  }


  // 获取文件图标
  const getFileIcon = (fileName: string) => {
    if (!fileName || typeof fileName !== 'string') return <File className="h-4 w-4 text-gray-600" />
    const extension = fileName.split('.').pop()?.toLowerCase()

    switch (extension) {
      case 'md':
        return <FileText className="h-4 w-4 text-blue-600" />
      case 'js':
      case 'ts':
      case 'jsx':
      case 'tsx':
      case 'cs':
      case 'py':
      case 'java':
        return <Code className="h-4 w-4 text-green-600" />
      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'gif':
      case 'svg':
        return <Image className="h-4 w-4 text-purple-600" />
      case 'json':
      case 'xml':
      case 'yml':
      case 'yaml':
        return <Database className="h-4 w-4 text-orange-600" />
      default:
        return <File className="h-4 w-4 text-muted-foreground" />
    }
  }

  // 渲染文件树节点 - 完全参考 FumadocsSidebar 的实现
  const renderTreeNode = useCallback((node: any, level: number = 0) => {
    const nodeId = node.key || node.id || ''
    const nodeName = node.title || node.name || ''
    const isFolder = !node.isLeaf
    const isExpanded = expandedNodes.has(nodeId)
    const isSelected = selectedNode?.key === nodeId || selectedNode?.id === nodeId
    const hasChildren = isFolder && node.children && Array.isArray(node.children) && node.children.length > 0
    const hasProgress = typeof node.progress === 'number'
    const isDisabled = node.disabled || false

    // Fumadocs 风格的缩进，增大字体和间距
    const indent = level * 16 + 16 // 基础16px + 每级16px

    if (hasChildren) {
      return (
        <div key={nodeId} className="group">
          <div className="flex items-center">
            {/* 展开/折叠按钮 */}
            <button
              className={cn(
                "flex items-center justify-center w-5 h-5 hover:bg-accent/50 rounded transition-all duration-150 flex-shrink-0",
                !isDisabled && "hover:bg-accent/50",
                isDisabled && "opacity-50 cursor-not-allowed"
              )}
              style={{ marginLeft: `${indent - 20}px` }}
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                if (isDisabled) return
                handleNodeClick(node, true) // 传递 isExpandToggle = true
              }}
              disabled={isDisabled}
            >
              {isExpanded ? (
                <ChevronDown className="h-3 w-3 text-muted-foreground" />
              ) : (
                <ChevronRight className="h-3 w-3 text-muted-foreground" />
              )}
            </button>

            {/* 主要内容按钮 */}
            <button
              className={cn(
                "flex items-center flex-1 py-2 px-3 text-sm transition-all duration-150 rounded-md relative ml-1",
                !isDisabled && "hover:bg-accent/50 hover:text-accent-foreground",
                isSelected && !isDisabled && "bg-accent text-accent-foreground font-medium",
                isDisabled && "opacity-50 cursor-not-allowed"
              )}
              onClick={(e) => {
                if (isDisabled) {
                  e.preventDefault()
                  e.stopPropagation()
                  return
                }
                handleNodeClick(node, false) // 传递 isExpandToggle = false
              }}
              disabled={isDisabled}
            >
              <span className="truncate flex-1 text-left font-normal">{nodeName}</span>
              {node.catalog?.isCompleted && (
                <span className="ml-2 text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded-full font-medium flex-shrink-0">
                  {t('admin.repositories.detail.completed')}
                </span>
              )}
            </button>
          </div>
          {hasProgress && (
            <div className="px-4 mt-1 mb-1">
              <div className="flex items-center gap-2">
                <Progress value={node.progress || 0} className="h-2 flex-1" />
                <span className="text-[10px] text-muted-foreground font-mono min-w-[30px]">
                  {Math.round(node.progress || 0)}%
                </span>
              </div>
              {isDisabled && (
                <span className="text-[10px] text-muted-foreground">{t('admin.repositories.detail.processing')}</span>
              )}
            </div>
          )}
          {isExpanded && (
            <div className="pb-1">
              {node.children.map((child: any) => renderTreeNode(child, level + 1))}
            </div>
          )}
        </div>
      )
    }

    return (
      <div key={nodeId} className="relative">
        <button
          className={cn(
            "flex items-center w-full py-2 px-3 text-sm transition-all duration-150 rounded-md group relative",
            !isDisabled && "hover:bg-accent/50 hover:text-accent-foreground",
            isSelected && !isDisabled ? "bg-accent text-accent-foreground font-medium" : "text-muted-foreground",
            isDisabled && "opacity-50 cursor-not-allowed"
          )}
          style={{ paddingLeft: `${indent + 16}px` }} // 叶节点额外缩进
          onClick={(e) => {
            if (isDisabled) {
              e.preventDefault()
              e.stopPropagation()
              return
            }
            handleNodeClick(node)
          }}
          disabled={isDisabled}
        >
          <span className="truncate flex-1 text-left font-normal">{nodeName}</span>
          {node.catalog?.isCompleted && (
            <span className="ml-2 text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded-full font-medium flex-shrink-0">
              {t('admin.repositories.detail.completed')}
            </span>
          )}
        </button>
        {hasProgress && (
          <div className="px-4 mt-1 mb-1" style={{ paddingLeft: `${indent + 32}px` }}>
            <div className="flex items-center gap-2">
              <Progress value={node.progress || 0} className="h-2 flex-1" />
              <span className="text-[10px] text-muted-foreground font-mono min-w-[30px]">
                {Math.round(node.progress || 0)}%
              </span>
            </div>
            {isDisabled && (
              <span className="text-[10px] text-muted-foreground">{t('admin.repositories.detail.processing')}</span>
            )}
          </div>
        )}
      </div>
    )
  }, [handleNodeClick, expandedNodes, selectedNode])

  // 过滤文件树数据
  const filteredTreeData = useMemo(() => {
    const filterNodes = (nodes: any[]): any[] => {
      if (!nodes || !Array.isArray(nodes)) return []
      if (!searchQuery) return nodes

      return nodes.filter(node => {
        const nodeName = node.title || node.name || ''
        if (nodeName.toLowerCase().includes(searchQuery.toLowerCase())) {
          return true
        }
        if (node.children && Array.isArray(node.children)) {
          const filteredChildren = filterNodes(node.children)
          if (filteredChildren.length > 0) {
            return true
          }
        }
        return false
      })
    }

    return filterNodes
  }, [searchQuery])

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      'Completed': { label: t('admin.common.completed'), variant: 'default' as const, icon: CheckCircle },
      'Processing': { label: t('admin.common.processing'), variant: 'secondary' as const, icon: Activity },
      'Pending': { label: t('admin.common.pending'), variant: 'outline' as const, icon: Clock },
      'Failed': { label: t('admin.common.failed'), variant: 'destructive' as const, icon: AlertCircle }
    }

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.Pending
    const Icon = config.icon

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {config.label}
      </Badge>
    )
  }

  const renderDocumentsTab = () => (
    <div className="grid grid-cols-12 gap-6 h-[calc(100vh-16rem)]">
      {/* 文档目录树 */}
      {sidebarCollapsed ? (
        <div className="col-span-1 flex items-start justify-center pt-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="h-8 w-8 p-0 hover:bg-accent/50 bg-background border border-border/50 shadow-sm"
          >
            <ChevronRight className="h-3.5 w-3.5" />
          </Button>
        </div>
      ) : (
        <div className="col-span-4 transition-all duration-300 ease-in-out">
          <Card className="h-full">
            <CardContent className="p-0">
              <div className="px-3 py-2">
                <div className="flex items-center gap-2">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
                    <Input
                      type="text"
                      placeholder={t('admin.repositories.detail.search_documents')}
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9 pr-14 h-8 text-sm bg-accent/30 border-0 focus:bg-accent/50 transition-colors placeholder:text-muted-foreground/60"
                    />
                    <kbd className="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none inline-flex h-4 select-none items-center gap-0.5 rounded border border-border/50 bg-background px-1 font-mono text-[10px] font-medium text-muted-foreground">
                      <span className="text-[10px]">⌘</span>K
                    </kbd>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                    className="h-8 w-8 p-0 hover:bg-accent/50"
                  >
                    <ChevronLeft className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>
              <ScrollArea className="flex-1">
                <div className="px-2 py-1 space-y-1">
                  {/* 分隔线 */}
                  <div className="h-px bg-border/30 mx-2 my-3" />

                  {/* 文档树 */}
                  {treeData && treeData.length > 0 ? (
                    <div className="space-y-0.5">
                      {filteredTreeData(treeData).map(node => renderTreeNode(node))}
                    </div>
                  ) : (
                    <p className="text-xs text-muted-foreground/60 text-center py-4 px-6">
                      {t('admin.repositories.detail.no_documents')}
                    </p>
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 文档内容 */}
      <div className={cn(
        "transition-all duration-300 ease-in-out",
        sidebarCollapsed ? "col-span-11" : "col-span-8"
      )}>
        <Card className="h-full flex flex-col">
          {selectedNode ? (
            <>
              {/* 文档内容区域 */}
              <CardContent className="flex-1 p-0 overflow-hidden">
                <div className="h-full flex flex-col">
                  {/* 工具栏 */}
                  <div className="flex-shrink-0 px-4 py-2 border-b bg-muted/30">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 text-sm text-muted-foreground"><div className="flex items-center space-x-2">
                        {selectedNode.catalog?.isCompleted && (
                          <Badge variant="default" className="text-xs">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            {t('admin.repositories.detail.completed_badge')}
                          </Badge>
                        )}
                        <Button
                          size="sm"
                          variant="default"
                          onClick={() => setAiGenerateDialog(true)}
                          disabled={!selectedNode.catalog?.id}
                          className="flex items-center gap-2"
                        >
                          <Sparkles className="h-4 w-4" />
                          {t('admin.repositories.detail.ai_generate')}
                        </Button>
                        <Button
                          size="sm"
                          onClick={handleSave}
                          disabled={saving || !selectedNode.content}
                          className="flex items-center gap-2"
                        >
                          <Save className="h-4 w-4" />
                          {saving ? t('admin.repositories.detail.saving') : t('admin.repositories.detail.save')}
                        </Button>
                      </div>
                        {selectedNode.lastModified && (
                          <>
                            <Separator orientation="vertical" className="h-4" />
                            <span>{t('admin.repositories.detail.last_modified')}: {new Date(selectedNode.lastModified).toLocaleString()}</span>
                          </>
                        )}
                      </div>
                      <div className="flex items-center space-x-1">
                        <Button variant="ghost" size="sm" className="h-7 px-2">
                          <Eye className="h-3 w-3" />
                        </Button>
                        <Button variant="ghost" size="sm" className="h-7 px-2">
                          <Copy className="h-3 w-3" />
                        </Button>
                        <Button variant="ghost" size="sm" className="h-7 px-2">
                          <ExternalLink className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* 编辑器区域 */}
                  <div className="flex-1 relative">
                    <Suspense fallback={
                      <div className="flex items-center justify-center h-full">
                        <div className="text-center">
                          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                          <p>{t('admin.repositories.detail.loading_editor')}</p>
                        </div>
                      </div>
                    }>
                      <MarkdownEditor
                        value={selectedNode.content || ''}
                        onChange={handleContentChange}
                        placeholder={selectedNode.isLeaf ? t('admin.repositories.detail.file_placeholder') : t('admin.repositories.detail.document_placeholder')}
                        height="100%"
                        theme="light"
                        language="zh-CN"
                        onSave={(value, html) => {
                          handleSave()
                          toast.success(t('admin.repositories.detail.document_save_success'))
                        }}
                        onError={(error) => {
                          console.error('Editor error:', error)
                        }}
                      />
                    </Suspense>
                  </div>
                </div>
              </CardContent>
            </>
          ) : (
            <CardContent className="flex-1 flex items-center justify-center">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 mx-auto rounded-full bg-muted flex items-center justify-center">
                  <FileText className="h-8 w-8 text-muted-foreground" />
                </div>
                <div>
                  <h3 className="font-medium text-foreground">{t('admin.repositories.detail.select_document')}</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {t('admin.repositories.detail.select_document_description')}
                  </p>
                </div>
              </div>
            </CardContent>
          )}
        </Card>
      </div>
    </div>
  )

  const renderSyncTab = () => (
    <div className="space-y-6">
      {/* 同步操作 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>{t('admin.repositories.detail.sync_management')}</CardTitle>
              <CardDescription>{t('admin.repositories.detail.manage_sync_settings_history')}</CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Dialog open={syncDialogOpen} onOpenChange={setSyncDialogOpen}>
                <DialogTrigger asChild>
                  <Button>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    {t('admin.repositories.detail.manual_sync')}
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>{t('admin.repositories.detail.manual_sync_repository')}</DialogTitle>
                    <DialogDescription>
                      {t('admin.repositories.detail.sync_description')}
                    </DialogDescription>
                  </DialogHeader>
                  <div className="flex justify-end space-x-2">
                    <Button variant="outline" onClick={() => setSyncDialogOpen(false)}>
                      {t('admin.repositories.detail.cancel')}
                    </Button>
                    <Button onClick={handleSync}>
                      {t('admin.repositories.detail.start_sync')}
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>{t('admin.repositories.detail.last_sync_label')}</Label>
              <p className="text-sm text-muted-foreground">
                {stats?.lastSyncTime
                  ? new Date(stats.lastSyncTime).toLocaleString()
                  : t('admin.repositories.detail.never_synced_label')
                }
              </p>
            </div>
            <div className="space-y-2">
              <Label>{t('admin.repositories.detail.sync_status_label')}</Label>
              {getStatusBadge(stats?.processingStatus || 'Pending')}
            </div>
            <div className="space-y-2">
              <Label>{t('admin.repositories.detail.auto_sync_label')}</Label>
              <div className="flex items-center space-x-2">
                <Switch
                  checked={repository?.enableSync || false}
                  onCheckedChange={handleSyncToggle}
                  disabled={updatingSyncSetting}
                />
                <span className="text-sm text-muted-foreground">
                  {updatingSyncSetting ? t('admin.repositories.detail.sync_updating') : (repository?.enableSync ? t('admin.repositories.detail.enabled') : t('admin.repositories.detail.disabled'))}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 同步历史 */}
      <Card>
        <CardHeader>
          <CardTitle>{t('admin.repositories.detail.sync_history')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {syncRecords.length > 0 ? (
              syncRecords.map((sync) => (
                <div key={sync.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={cn(
                      "w-3 h-3 rounded-full",
                      sync.status === 'Success' ? 'bg-green-500' :
                        sync.status === 'Failed' ? 'bg-red-500' : 'bg-yellow-500'
                    )} />
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium">
                          {sync.status === 'Success' ? t('admin.repositories.detail.sync_success') :
                            sync.status === 'Failed' ? t('admin.repositories.detail.sync_failed') : t('admin.repositories.detail.syncing')}
                        </p>
                        <Badge variant={sync.trigger === 'Manual' ? 'default' : 'outline'} className="text-xs">
                          {sync.trigger === 'Manual' ? t('admin.repositories.detail.manual_trigger') : t('admin.repositories.detail.auto_trigger')}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {t('admin.repositories.detail.start_time')}: {new Date(sync.startTime).toLocaleString()}
                        {sync.endTime && ` • ${t('admin.repositories.detail.end_time')}: ${new Date(sync.endTime).toLocaleString()}`}
                      </p>
                      {sync.errorMessage && (
                        <p className="text-xs text-red-500 mt-1">{sync.errorMessage}</p>
                      )}
                      {sync.fromVersion && sync.toVersion && (
                        <p className="text-xs text-muted-foreground">
                          {sync.fromVersion.slice(0, 7)} → {sync.toVersion.slice(0, 7)}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge variant="outline" className="mb-1">
                      {sync.fileCount} {t('admin.repositories.detail.files')}
                    </Badge>
                    {sync.status === 'Success' && (
                      <div className="text-xs text-muted-foreground">
                        <div>{t('admin.repositories.detail.added_files')}: {sync.addedFileCount}</div>
                        <div>{t('admin.repositories.detail.updated_files')}: {sync.updatedFileCount}</div>
                        <div>{t('admin.repositories.detail.deleted_files')}: {sync.deletedFileCount}</div>
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">
                {t('admin.repositories.detail.no_sync_history')}
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderPermissionsTab = () => (
    <Card>
      <CardHeader>
        <CardTitle>权限管理</CardTitle>
        <CardDescription>管理用户和角色对此仓库的访问权限</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-center py-8">
          <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p className="text-muted-foreground">权限管理功能开发中...</p>
        </div>
      </CardContent>
    </Card>
  )

  const renderConfigTab = () => (
    <Card>
      <CardHeader>
        <CardTitle>配置管理</CardTitle>
        <CardDescription>管理仓库的各种配置选项</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-center py-8">
          <Cog className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p className="text-muted-foreground">配置管理功能开发中...</p>
        </div>
      </CardContent>
    </Card>
  )

  const renderTasksTab = () => (
    <Card>
      <CardHeader>
        <CardTitle>任务管理</CardTitle>
        <CardDescription>查看和管理仓库相关的处理任务</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-center py-8">
          <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p className="text-muted-foreground">任务管理功能开发中...</p>
        </div>
      </CardContent>
    </Card>
  )

  // 加载状态处理
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>{t('admin.messages.loading')}</p>
        </div>
      </div>
    )
  }

  if (!repository) {
    return (
      <div className="text-center py-8">
        <p>{t('admin.repositories.detail.repository_not_found')}</p>
        <Button asChild className="mt-4">
          <Link to="/admin/repositories">
            <ChevronLeft className="mr-2 h-4 w-4" />
            {t('admin.repositories.detail.return_to_repository_list')}
          </Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={cn("mr-2 h-4 w-4", refreshing && "animate-spin")} />
            {refreshing ? t('admin.repositories.detail.refreshing') : t('admin.repositories.detail.refresh')}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleExport}
          >
            <Download className="mr-2 h-4 w-4" />
            {t('admin.repositories.detail.export')}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleEdit}
          >
            <Edit3 className="mr-2 h-4 w-4" />
            {t('admin.repositories.detail.edit')}
          </Button>
          <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Trash2 className="mr-2 h-4 w-4" />
                {t('admin.repositories.detail.delete')}
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{t('admin.repositories.detail.confirm_delete_repository')}</DialogTitle>
                <DialogDescription>
                  {t('admin.repositories.detail.delete_repository_warning')}
                </DialogDescription>
              </DialogHeader>
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
                  {t('admin.repositories.detail.cancel')}
                </Button>
                <Button variant="destructive" onClick={handleDelete}>
                  {t('admin.repositories.detail.confirm_delete')}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* 主要内容区域 */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-5">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="documents">{t('admin.repositories.detail.documents')}</TabsTrigger>
          <TabsTrigger value="sync">{t('admin.repositories.detail.sync')}</TabsTrigger>
          <TabsTrigger value="generation">Wiki生成</TabsTrigger>
          <TabsTrigger value="quality">{t('admin.repositories.detail.quality') || '质量评估'}</TabsTrigger>
        </TabsList>

        {/* 文档管理标签页 */}
        <TabsContent value="documents" className="space-y-6">
          {renderDocumentsTab()}
        </TabsContent>

        {/* 同步管理标签页 */}
        <TabsContent value="sync" className="space-y-6">
          {renderSyncTab()}
        </TabsContent>

        {/* Wiki生成管理标签页 */}
        <TabsContent value="generation" className="space-y-6">
          {id && <WikiGenerationManagement warehouseId={id} />}
        </TabsContent>

        {/* 文档质量评估标签页 */}
        <TabsContent value="quality" className="space-y-6">
          {id && <DocumentQualityEvaluation warehouseId={id} />}
        </TabsContent>

      </Tabs>

      {/* 编辑仓库对话框 */}
      <Dialog open={editDialog} onOpenChange={setEditDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>编辑仓库信息</DialogTitle>
            <DialogDescription>
              修改仓库的基本信息和同步设置
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">仓库名称</Label>
              <Input
                id="name"
                value={editForm.name}
                onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                placeholder="输入仓库名称"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">仓库描述</Label>
              <Textarea
                id="description"
                value={editForm.description}
                onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                placeholder="输入仓库描述"
                className="min-h-[80px]"
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="enableSync">自动同步</Label>
                <p className="text-sm text-muted-foreground">
                  启用后系统将自动同步仓库更新
                </p>
              </div>
              <Switch
                id="enableSync"
                checked={editForm.enableSync}
                onCheckedChange={(checked) => setEditForm({ ...editForm, enableSync: checked })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialog(false)}>
              取消
            </Button>
            <Button onClick={handleSaveEdit}>
              保存
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* AI生成对话框 */}
      <Dialog open={aiGenerateDialog} onOpenChange={setAiGenerateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              AI智能生成文档内容
            </DialogTitle>
            <DialogDescription>
              为当前选中的文档目录生成内容。您可以输入自定义提示词来引导AI生成，留空则使用默认提示词。
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="prompt">提示词（可选）</Label>
              <Textarea
                id="prompt"
                placeholder="例如：请生成详细的技术文档，包含代码示例和架构说明..."
                value={aiGeneratePrompt}
                onChange={(e) => setAiGeneratePrompt(e.target.value)}
                className="min-h-[100px]"
                disabled={aiGenerating}
              />
              <p className="text-sm text-muted-foreground">
                提示：留空将使用系统默认提示词或之前保存的提示词
              </p>
            </div>
            {selectedNode?.catalog && (
              <div className="rounded-lg bg-muted p-3">
                <p className="text-sm">
                  <strong>目标文档：</strong>{selectedNode.title || selectedNode.name}
                </p>
                {selectedNode.catalog.prompt && (
                  <p className="text-sm mt-1">
                    <strong>当前提示词：</strong>{selectedNode.catalog.prompt}
                  </p>
                )}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setAiGenerateDialog(false)
                setAiGeneratePrompt('')
              }}
              disabled={aiGenerating}
            >
              取消
            </Button>
            <Button
              onClick={handleAiGenerate}
              disabled={aiGenerating || !selectedNode?.catalog?.id}
            >
              {aiGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  生成中...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  开始生成
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default RepositoryDetailPage