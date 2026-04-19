import React from 'react'
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Database,
  Server,
  Clock,
  Wrench,
  AlertTriangleIcon
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import type { SystemStatus } from '@/types/systemSettings'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

interface SystemStatusCardProps {
  status: SystemStatus | null
  restartRequired: string[]
  className?: string
}

const SystemStatusCard: React.FC<SystemStatusCardProps> = ({ status, restartRequired, className }) => {
  const { t } = useTranslation('admin')

  // 如果没有状态数据，显示加载或错误状态
  if (!status) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="w-5 h-5" />
            {t('settings.systemStatus.title')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertTriangleIcon className="h-4 w-4" />
            <AlertDescription>
              {t('settings.systemStatus.noData')}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    )
  }

  // 格式化运行时间
  const formatUptime = (uptime: string) => {
    return uptime || t('common.unknown')
  }

  // 格式化最后重启时间
  const formatLastRestart = (lastRestart: string) => {
    if (!lastRestart) return t('common.unknown')
    return new Date(lastRestart).toLocaleString()
  }

  // 计算系统健康度评分
  const calculateHealthScore = (status: SystemStatus, restartRequired: string[]): number => {
    let score = 100

    // 性能指标扣分
    if (status.performance?.cpuUsage > 80) score -= 20
    else if (status.performance?.cpuUsage > 60) score -= 10

    if (status.performance?.memoryUsage > 90) score -= 20
    else if (status.performance?.memoryUsage > 70) score -= 10

    if (status.performance?.diskUsage > 85) score -= 15
    else if (status.performance?.diskUsage > 70) score -= 5

    // 功能模块配置扣分
    if (!status.features?.emailConfigured) score -= 10
    if (!status.features?.aiConfigured) score -= 15
    if (!status.features?.backupConfigured) score -= 10
    if (!status.features?.securityConfigured) score -= 15

    // 重启需求扣分
    if (restartRequired.length > 0) score -= Math.min(restartRequired.length * 5, 20)

    return Math.max(0, score)
  }

  // 获取健康度描述
  const getHealthDescription = (score: number): string => {
    if (score >= 90) return t('settings.systemStatus.healthExcellent')
    if (score >= 70) return t('settings.systemStatus.healthGood')
    if (score >= 50) return t('settings.systemStatus.healthFair')
    return t('settings.systemStatus.healthPoor')
  }

  const healthScore = calculateHealthScore(status, restartRequired)

  return (
    <TooltipProvider>
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="w-5 h-5" />
            {t('settings.systemStatus.title')}
            {restartRequired.length > 0 && (
              <Badge variant="destructive" className="ml-2">
                {restartRequired.length}
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* 系统信息 */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardContent className="p-4 text-center">
                <Wrench className="w-6 h-6 mx-auto mb-2 text-muted-foreground" />
                <div className="text-sm font-medium">{t('settings.systemStatus.version')}</div>
                <div className="text-lg font-bold">{status.systemInfo?.version || t('common.unknown')}</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <Server className="w-6 h-6 mx-auto mb-2 text-muted-foreground" />
                <div className="text-sm font-medium">{t('settings.systemStatus.environment')}</div>
                <div className={`text-lg font-bold ${
                  status.systemInfo?.environment === 'Production' ? 'text-destructive' : 'text-blue-600'
                }`}>
                  {status.systemInfo?.environment || t('common.unknown')}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="cursor-help">
                      <Clock className="w-6 h-6 mx-auto mb-2 text-muted-foreground" />
                      <div className="text-sm font-medium">{t('settings.systemStatus.uptime')}</div>
                      <div className="text-lg font-bold">{formatUptime(status.systemInfo?.uptime)}</div>
                    </div>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{formatLastRestart(status.systemInfo?.lastRestart)}</p>
                  </TooltipContent>
                </Tooltip>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <Server className="w-6 h-6 mx-auto mb-2 text-muted-foreground" />
                <div className="text-sm font-medium">{t('settings.systemStatus.activeConnections')}</div>
                <div className="text-lg font-bold">{status.performance?.activeConnections || 0}</div>
              </CardContent>
            </Card>
          </div>

          <Separator />
          {/* 功能状态 */}
          <div>
            <h4 className="text-sm font-medium mb-4">{t('settings.systemStatus.features')}</h4>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <span className="text-sm">{t('settings.systemStatus.emailService')}</span>
                {status.features?.emailConfigured ? (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-destructive" />
                )}
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <span className="text-sm">{t('settings.systemStatus.aiService')}</span>
                {status.features?.aiConfigured ? (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-destructive" />
                )}
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <span className="text-sm">{t('settings.systemStatus.backupService')}</span>
                {status.features?.backupConfigured ? (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-destructive" />
                )}
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <span className="text-sm">{t('settings.systemStatus.securityFeatures')}</span>
                {status.features?.securityConfigured ? (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-destructive" />
                )}
              </div>
            </div>
          </div>

          <Separator />

          {/* 系统健康度 */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium">{t('settings.systemStatus.systemHealth')}</h4>
              <span className={`text-sm font-medium ${
                healthScore >= 70 ? 'text-green-500' : healthScore >= 50 ? 'text-orange-500' : 'text-destructive'
              }`}>
                {getHealthDescription(healthScore)}
              </span>
            </div>
            <Progress
              value={healthScore}
              className="h-2"
            />
            <div className="flex justify-between mt-1">
              <span className="text-xs text-muted-foreground">0%</span>
              <span className="text-xs font-medium">{healthScore}%</span>
              <span className="text-xs text-muted-foreground">100%</span>
            </div>
          </div>

          {/* 警告信息 */}
          {restartRequired.length > 0 && (
            <>
              <Separator />
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  {t('settings.systemStatus.restartRequiredInfo', { count: restartRequired.length })}
                </AlertDescription>
              </Alert>
            </>
          )}
        </CardContent>
      </Card>
    </TooltipProvider>
  )
}

export default SystemStatusCard