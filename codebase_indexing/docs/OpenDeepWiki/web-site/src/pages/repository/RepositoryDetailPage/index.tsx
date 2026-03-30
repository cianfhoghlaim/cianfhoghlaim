// 仓库详情页面 - 概览

import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { useRepositoryDetailStore } from '@/stores/repositoryDetail.store'
import { warehouseService } from '@/services/warehouse.service'
import { request } from '@/utils/request'
import { WarehouseStatus } from '@/types/repository'
import { DocumentQualityEvaluation } from '@/components/DocumentQuality'
import WikiGenerationManagement from '@/components/WikiGeneration/WikiGenerationManagement'
import {
  GitBranch,
  AlertCircle,
  RefreshCw,
  ExternalLink,
  Loader2,
  Copy,
  CheckCircle2
} from 'lucide-react'

const RepositoryDetailPage = () => {
  const { t } = useTranslation()
  const { owner, name } = useParams<{ owner: string; name: string }>()
  const [copied, setCopied] = useState(false)

  // 使用store
  const {
    repository,
    error,
    setRepository,
    fetchDocumentCatalog,
  } = useRepositoryDetailStore()

  const [loading, setLoading] = useState(true)
  const [tokenStats, setTokenStats] = useState<{ inputToken: number; outputToken: number; totalToken: number }>({ inputToken: 0, outputToken: 0, totalToken: 0 })
  const [tokenRecords, setTokenRecords] = useState<Array<{ id: string; operation: string; inputToken: number; outputToken: number; totalToken: number; model?: string; createdAt: string }>>([])
  const [tokenDaily, setTokenDaily] = useState<Array<{date: string; operations: Array<{ operation: string; inputToken: number; outputToken: number; totalToken: number }>; totals: { inputToken: number; outputToken: number; totalToken: number }}>>([])

  // 初始化数据
  const initializeData = async () => {
    if (!owner || !name) return

    setLoading(true)

    try {
      // 设置仓库信息
      setRepository(owner, name)

      // 获取文档目录（这会同时获取分支列表）
      await fetchDocumentCatalog()

      // 获取仓库 Token 统计
      try {
        const res = await warehouseService.getTokenStatsByOwnerAndName(owner, name)
        if (res) {
          const { inputToken = 0, outputToken = 0, totalToken = 0 } = res || {}
          setTokenStats({ inputToken, outputToken, totalToken })
        }
        // 最近消费记录
        const rec = await request.get<any>(`/api/Repository/TokenConsumptionRecordsByOwnerAndName`, { params: { owner, name, page: 1, pageSize: 5 }})
        if (rec && rec.items) {
          setTokenRecords(rec.items || [])
        }
        // 按天×操作类型
        const daily = await request.get<any>(`/api/Repository/TokenDailyByOperationByOwnerAndName`, { params: { owner, name, days: 30 }})
        if (Array.isArray(daily)) setTokenDaily(daily)
      } catch {}
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    initializeData()
  }, [owner, name])

  // 复制Git地址
  const handleCopyAddress = () => {
    if (repository?.address) {
      navigator.clipboard.writeText(repository.address)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  // 获取状态颜色
  const getStatusVariant = (status: WarehouseStatus): "default" | "secondary" | "destructive" | "outline" => {
    switch (status) {
      case WarehouseStatus.Completed:
        return 'default'
      case WarehouseStatus.Processing:
        return 'secondary'
      case WarehouseStatus.Failed:
        return 'destructive'
      default:
        return 'outline'
    }
  }

  // 获取状态文本
  const getStatusText = (status: WarehouseStatus) => {
    switch (status) {
      case WarehouseStatus.Completed:
        return t('home.repository_card.status.completed')
      case WarehouseStatus.Processing:
        return t('home.repository_card.status.processing')
      case WarehouseStatus.Failed:
        return t('home.repository_card.status.failed')
      case WarehouseStatus.Pending:
        return t('home.repository_card.status.pending')
      default:
        return status
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-3 text-muted-foreground">{t('common.loading')}</span>
      </div>
    )
  }

  if (error || !repository) {
    return (
      <div className="space-y-4">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error || t('repository.detail.notFound')}
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {repository.name}
          </h1>
          {repository.description && (
            <p className="text-muted-foreground mt-2">
              {repository.description}
            </p>
          )}
          <div className="flex items-center gap-2 mt-3">
            {repository.isRecommended && (
              <Badge variant="secondary">
                {t('home.repository_card.recommended')}
              </Badge>
            )}
            <Badge variant={getStatusVariant(repository.status)}>
              {getStatusText(repository.status)}
            </Badge>
          </div>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={initializeData}
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          {t('common.refresh')}
        </Button>
      </div>

      {/* 仓库错误信息 */}
      {repository.error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {repository.error}
          </AlertDescription>
        </Alert>
      )}

      {/* 信息卡片 */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* 基本信息 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">{t('repository.detail.basicInfo')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">
                {t('repository.detail.organization')}
              </p>
              <p className="text-sm">{repository.organizationName}</p>
            </div>

            <Separator />

            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">
                {t('repository.detail.repositoryName')}
              </p>
              <p className="text-sm">{repository.name}</p>
            </div>

            <Separator />

            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">
                {t('repository.detail.createdAt')}
              </p>
              <p className="text-sm">
                {new Date(repository.createdAt).toLocaleString()}
              </p>
            </div>

            {repository.updatedAt && (
              <>
                <Separator />
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">
                    {t('repository.detail.updatedAt')}
                  </p>
                  <p className="text-sm">
                    {new Date(repository.updatedAt).toLocaleString()}
                  </p>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Git 信息 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">{t('repository.detail.gitInfo')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">
                {t('repository.detail.repositoryUrl')}
              </p>
              <div className="flex items-center gap-2">
                <a
                  href={repository.address}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-primary hover:underline flex-1 truncate"
                >
                  {repository.address}
                </a>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={handleCopyAddress}
                >
                  {copied ? (
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => window.open(repository.address, '_blank')}
                >
                  <ExternalLink className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <Separator />

            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">
                {t('repository.detail.branch')}
              </p>
              <div className="flex items-center gap-2">
                <GitBranch className="h-4 w-4 text-muted-foreground" />
                <p className="text-sm">{repository.branch}</p>
              </div>
            </div>

            <Separator />

            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">
                {t('repository.detail.cloneCommand')}
              </p>
              <div className="bg-muted rounded-md p-2 font-mono text-xs">
                git clone -b {repository.branch} {repository.address}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 统计信息 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">{t('repository.detail.statistics')}</CardTitle>
          <CardDescription>
            {t('repository.detail.statisticsDescription')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 rounded-lg bg-muted/50">
              <p className="text-2xl font-bold">0</p>
              <p className="text-sm text-muted-foreground">{t('repository.detail.documents')}</p>
            </div>
            <div className="text-center p-4 rounded-lg bg-muted/50">
              <p className="text-2xl font-bold">0</p>
              <p className="text-sm text-muted-foreground">{t('repository.detail.commits')}</p>
            </div>
            <div className="text-center p-4 rounded-lg bg-muted/50">
              <p className="text-2xl font-bold">0</p>
              <p className="text-sm text-muted-foreground">{t('repository.detail.contributors')}</p>
            </div>
            <div className="text-center p-4 rounded-lg bg-muted/50">
              <p className="text-2xl font-bold">0</p>
              <p className="text-sm text-muted-foreground">{t('repository.detail.stars')}</p>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="text-center p-4 rounded-lg bg-muted/50">
              <p className="text-2xl font-bold">{tokenStats.inputToken}</p>
              <p className="text-sm text-muted-foreground">{t('repository.detail.inputToken')}</p>
            </div>
            <div className="text-center p-4 rounded-lg bg-muted/50">
              <p className="text-2xl font-bold">{tokenStats.outputToken}</p>
              <p className="text-sm text-muted-foreground">{t('repository.detail.outputToken')}</p>
            </div>
            <div className="text-center p-4 rounded-lg bg-muted/50">
              <p className="text-2xl font-bold">{tokenStats.totalToken}</p>
              <p className="text-sm text-muted-foreground">{t('repository.detail.totalToken')}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Token消费记录 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">{t('repository.detail.tokenConsumption')}</CardTitle>
          <CardDescription>{t('repository.detail.tokenConsumptionDescription')}</CardDescription>
        </CardHeader>
        <CardContent>
          {tokenRecords.length === 0 ? (
            <div className="text-sm text-muted-foreground">{t('repository.detail.noRecords')}</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-muted-foreground">
                    <th className="py-2 pr-2">{t('repository.detail.time')}</th>
                    <th className="py-2 pr-2">{t('repository.detail.operation')}</th>
                    <th className="py-2 pr-2">{t('repository.detail.model')}</th>
                    <th className="py-2 pr-2">{t('repository.detail.inputToken')}</th>
                    <th className="py-2 pr-2">{t('repository.detail.outputToken')}</th>
                    <th className="py-2 pr-2">{t('repository.detail.totalToken')}</th>
                  </tr>
                </thead>
                <tbody>
                  {tokenRecords.map(r => (
                    <tr key={r.id} className="border-t">
                      <td className="py-2 pr-2">{new Date(r.createdAt).toLocaleString()}</td>
                      <td className="py-2 pr-2">{r.operation}</td>
                      <td className="py-2 pr-2">{r.model || '-'}</td>
                      <td className="py-2 pr-2">{r.inputToken}</td>
                      <td className="py-2 pr-2">{r.outputToken}</td>
                      <td className="py-2 pr-2 font-medium">{r.totalToken}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Token 按天 × 操作类型 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">{t('repository.detail.tokenDailyByOperation')}</CardTitle>
          <CardDescription>{t('repository.detail.tokenDailyDescription')}</CardDescription>
        </CardHeader>
        <CardContent>
          {tokenDaily.length === 0 ? (
            <div className="text-sm text-muted-foreground">{t('repository.detail.noData')}</div>
          ) : (
            <div className="space-y-2">
              {/* 简易堆叠条形图：使用 div 宽度比例模拟 */}
              {(() => {
                const max = Math.max(...tokenDaily.map(d => d.totals.totalToken || 0), 1)
                const opSet = Array.from(new Set(tokenDaily.flatMap(d => d.operations.map(o => o.operation))))
                const opColors: Record<string, string> = {}
                const palette = ['#2563eb', '#16a34a', '#f59e0b', '#ef4444', '#9333ea', '#0891b2']
                opSet.forEach((op, idx) => opColors[op] = palette[idx % palette.length])
                return (
                  <div className="space-y-1">
                    {tokenDaily.map(d => (
                      <div key={d.date} className="flex items-center gap-2">
                        <div className="w-24 text-xs text-muted-foreground">{d.date.slice(5)}</div>
                        <div className="flex-1 h-3 bg-muted rounded overflow-hidden flex">
                          {d.operations.map(op => (
                            <div key={op.operation}
                              title={`${op.operation}: ${op.totalToken}`}
                              style={{ width: `${(op.totalToken / max) * 100}%`, backgroundColor: opColors[op.operation] }}
                              className="h-full"></div>
                          ))}
                        </div>
                        <div className="w-16 text-right text-xs">{d.totals.totalToken}</div>
                      </div>
                    ))}
                    {/* 图例 */}
                    <div className="flex flex-wrap gap-3 pt-2">
                      {opSet.map(op => (
                        <div key={op} className="flex items-center gap-1 text-xs text-muted-foreground">
                          <span className="inline-block w-3 h-3 rounded" style={{ backgroundColor: opColors[op] }} />
                          <span>{op}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })()}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Wiki生成管理 */}
      {repository?.id && <WikiGenerationManagement warehouseId={repository.id} />}

      {/* 文档质量评估 */}
      {repository?.id && <DocumentQualityEvaluation warehouseId={repository.id} />}
    </div>
  )
}

export default RepositoryDetailPage
