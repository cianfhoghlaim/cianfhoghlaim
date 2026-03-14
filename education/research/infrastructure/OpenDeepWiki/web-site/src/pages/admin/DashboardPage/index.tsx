// 管理员仪表板页面

import React, { useEffect, useState, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'
import {
  Users,
  Database,
  Shield,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Eye,
  FileText,
  Settings,
  UserPlus,
  FolderPlus,
  Plus,
  BarChart3,
  Globe
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { statsService } from '@/services/admin.service'

const DashboardPage: React.FC = () => {
  const { t } = useTranslation('admin')
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [error, setError] = useState<string | null>(null)

  // 获取仪表板数据
  const fetchDashboardData = useCallback(async (isRefresh = false) => {
    try {
      setError(null)
      if (isRefresh) {
        setRefreshing(true)
      } else {
        setLoading(true)
      }

      const data = await statsService.getComprehensiveDashboard()
      setDashboardData(data)
      setLastUpdated(new Date())
    } catch (error: any) {
      console.error('Failed to fetch dashboard data:', error)
      setError(error.message || '获取仪表板数据失败')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  // 组件挂载时获取数据
  useEffect(() => {
    fetchDashboardData()
  }, [fetchDashboardData])

  // 自动刷新功能（每30秒）
  useEffect(() => {
    const interval = setInterval(() => {
      if (dashboardData) {
        fetchDashboardData(true)
      }
    }, 30000)

    return () => clearInterval(interval)
  }, [fetchDashboardData, dashboardData])

  const refreshData = () => {
    fetchDashboardData(true)
  }

  // 格式化数字显示
  const formatNumber = (num?: number | null) => {
    const value = typeof num === 'number' && !Number.isNaN(num) ? num : 0

    if (value >= 1000000) {
      return (value / 1000000).toFixed(1) + 'M'
    }
    if (value >= 1000) {
      return (value / 1000).toFixed(1) + 'K'
    }
    return value.toString()
  }

  // 格式化百分比显示
  const formatPercentage = (value: number) => {
    const sign = value >= 0 ? '+' : ''
    return `${sign}${value.toFixed(1)}%`
  }


  // 获取趋势图标
  const getTrendIcon = (value: number) => {
    if (value > 0) return <TrendingUp className="h-4 w-4 text-green-600" />
    if (value < 0) return <TrendingDown className="h-4 w-4 text-red-600" />
    return <div className="h-4 w-4" />
  }

  // 加载状态
  if (loading && !dashboardData) {
    return (
      <div className="space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-4 w-24" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-16 mb-2" />
                <Skeleton className="h-3 w-20" />
              </CardContent>
            </Card>
          ))}
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      </div>
    )
  }

  // 错误状态
  if (error && !dashboardData) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('dashboard.title')}</h1>
          <p className="text-muted-foreground">{t('dashboard.overview')}</p>
        </div>
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            {error}
            <Button
              variant="outline"
              size="sm"
              onClick={refreshData}
              className="ml-2"
            >
              重试
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  if (!dashboardData) return null

  // 安全的默认值
  const safeData = {
    systemStats: {
      totalUsers: 0,
      userGrowthRate: 0,
      monthlyNewUsers: 0,
      totalRepositories: 0,
      repositoryGrowthRate: 0,
      monthlyNewRepositories: 0,
      totalDocuments: 0,
      documentGrowthRate: 0,
      monthlyNewDocuments: 0,
      totalViews: 0,
      ...(dashboardData?.systemStats ?? {})
    },
    userActivity: {
      onlineUsers: 0,
      dailyActiveUsers: 0,
      weeklyActiveUsers: 0,
      monthlyActiveUsers: 0,
      activeUserGrowthRate: 0,
      ...(dashboardData?.userActivity ?? {})
    },
    recentUsers: dashboardData?.recentUsers ?? [],
    recentRepositories: dashboardData?.recentRepositories ?? [],
    recentErrors: dashboardData?.recentErrors ?? []
  }


  return (
    <div className="space-y-6">
      {/* 页面标题和操作栏 */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('dashboard.title')}</h1>
          <div className="flex items-center space-x-2 mt-1">
            <p className="text-muted-foreground">{t('dashboard.overview')}</p>
            {lastUpdated && (
              <>
                <Separator orientation="vertical" className="h-4" />
                <p className="text-xs text-muted-foreground">
                  {t('dashboard.lastUpdated')}: {lastUpdated.toLocaleTimeString()}
                </p>
              </>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="text-green-600">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></div>
            {t('dashboard.autoRefresh')}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={refreshData}
            disabled={refreshing}
          >
            <RefreshCw className={cn("h-4 w-4 mr-2", refreshing && "animate-spin")} />
            {t('dashboard.refresh')}
          </Button>
        </div>
      </div>


      {/* 核心统计卡片 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('dashboard.stats.total_users')}</CardTitle>
            <Users className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(safeData.systemStats.totalUsers)}</div>
            <div className="flex items-center space-x-1 mt-1">
              {getTrendIcon(safeData.systemStats.userGrowthRate)}
              <p className="text-xs text-muted-foreground">
                {formatPercentage(safeData.systemStats.userGrowthRate)} {t('dashboard.comparedToLastMonth')}
              </p>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {t('dashboard.monthlyNew')}: {safeData.systemStats.monthlyNewUsers}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('dashboard.stats.total_repositories')}</CardTitle>
            <Database className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(safeData.systemStats.totalRepositories)}</div>
            <div className="flex items-center space-x-1 mt-1">
              {getTrendIcon(safeData.systemStats.repositoryGrowthRate)}
              <p className="text-xs text-muted-foreground">
                {formatPercentage(safeData.systemStats.repositoryGrowthRate)} {t('dashboard.comparedToLastMonth')}
              </p>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {t('dashboard.monthlyNew')}: {safeData.systemStats.monthlyNewRepositories}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('dashboard.stats.total_documents')}</CardTitle>
            <FileText className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(safeData.systemStats.totalDocuments)}</div>
            <div className="flex items-center space-x-1 mt-1">
              {getTrendIcon(safeData.systemStats.documentGrowthRate)}
              <p className="text-xs text-muted-foreground">
                {formatPercentage(safeData.systemStats.documentGrowthRate)} {t('dashboard.comparedToLastMonth')}
              </p>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {t('dashboard.monthlyNew')}: {formatNumber(safeData.systemStats.monthlyNewDocuments)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('dashboard.stats.online_users')}</CardTitle>
            <Globe className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{safeData.userActivity.onlineUsers}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {t('dashboard.todayActive')}: {safeData.userActivity.dailyActiveUsers}
            </p>
            <p className="text-xs text-muted-foreground">
              {t('dashboard.totalViews')}: {formatNumber(safeData.systemStats.totalViews)}
            </p>
          </CardContent>
        </Card>
      </div>


      {/* 用户活跃度和最近活动 */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-blue-600" />
              <span>{t('dashboard.userActivityStats')}</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-muted-foreground">{t('dashboard.todayActive')}</p>
                <p className="text-2xl font-bold text-blue-600">{safeData.userActivity.dailyActiveUsers}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{t('dashboard.weekActive')}</p>
                <p className="text-2xl font-bold text-green-600">{safeData.userActivity.weeklyActiveUsers}</p>
              </div>
            </div>
            <div className="space-y-1 text-sm text-muted-foreground">
              <p>{t('dashboard.monthlyActiveUsers')}: {safeData.userActivity.monthlyActiveUsers}</p>
              <div className="flex items-center space-x-1">
                <span>{t('dashboard.increaseRate')}:</span>
                {getTrendIcon(safeData.userActivity.activeUserGrowthRate)}
                <span>{formatPercentage(safeData.userActivity.activeUserGrowthRate)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Eye className="h-5 w-5 text-purple-600" />
              <span>{t('dashboard.recentUsers')}</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {safeData.recentUsers.slice(0, 4).map((user) => (
                <div key={user.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={user.avatar} />
                      <AvatarFallback>{user.name[0]}</AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="text-sm font-medium">{user.name}</p>
                      <p className="text-xs text-muted-foreground">{user.email}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge variant={user.isOnline ? "default" : "secondary"} className="text-xs">
                      {user.isOnline ? t('dashboard.online') : t('dashboard.offline')}
                    </Badge>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(user.createdAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 最近创建的仓库 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Database className="h-5 w-5 text-green-600" />
            <span>{t('dashboard.recentRepositories')}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {safeData.recentRepositories.map((repo) => (
              <div key={repo.id} className="border rounded-lg p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-sm">{repo.organizationName}/{repo.name}</h4>
                  <Badge variant="outline" className={cn(
                    "text-xs",
                    repo.status === 'Completed' ? 'text-green-600 border-green-200' :
                    repo.status === 'Processing' ? 'text-blue-600 border-blue-200' :
                    repo.status === 'Pending' ? 'text-yellow-600 border-yellow-200' :
                    'text-red-600 border-red-200'
                  )}>
                    {t(`dashboard.${repo.status.toLowerCase()}`)}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2">
                  {repo.description || t('dashboard.noDescription')}
                </p>
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>{t('dashboard.documentation')}: {repo.documentCount}</span>
                  <span>{new Date(repo.createdAt).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 错误日志 */}
      {safeData.recentErrors.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <span>{t('dashboard.recentErrorLogs')}</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {safeData.recentErrors.slice(0, 5).map((error) => (
                <div key={error.id} className="flex items-center justify-between p-2 border rounded">
                  <div className="flex items-center space-x-2">
                    <Badge variant={error.level === 'Error' ? 'destructive' : 'secondary'} className="text-xs">
                      {error.level}
                    </Badge>
                    <span className="text-sm">{error.message}</span>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {new Date(error.createdAt).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 快速操作 */}
      <Card>
        <CardHeader>
          <CardTitle>{t('dashboard.quickActions')}</CardTitle>
          <CardDescription>{t('dashboard.quickActionsDescription')}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm">
              <UserPlus className="h-4 w-4 mr-2" />
              {t('dashboard.addUser')}
            </Button>
            <Button variant="outline" size="sm">
              <FolderPlus className="h-4 w-4 mr-2" />
              {t('dashboard.addRepository')}
            </Button>
            <Button variant="outline" size="sm">
              <Shield className="h-4 w-4 mr-2" />
              {t('dashboard.manageRoles')}
            </Button>
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              {t('dashboard.systemSettings')}
            </Button>
            <Button variant="outline" size="sm">
              <BarChart3 className="h-4 w-4 mr-2" />
              {t('dashboard.viewReports')}
            </Button>
            <Button variant="outline" size="sm">
              <AlertTriangle className="h-4 w-4 mr-2" />
              {t('dashboard.viewLogs')}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default DashboardPage