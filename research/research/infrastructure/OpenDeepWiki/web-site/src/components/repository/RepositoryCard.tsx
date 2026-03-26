// 仓库卡片组件

import React, { useCallback, useMemo } from 'react'
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Star, GitBranch, Calendar, AlertCircle, ChevronRight } from 'lucide-react'
import { WarehouseStatus, type RepositoryInfo } from '@/types/repository'
import { formatDistanceToNow } from '@/utils/date'
import { useTranslation } from 'react-i18next'

const getStatusVariant = (status: WarehouseStatus): 'default' | 'secondary' | 'success' | 'destructive' => {
  switch (status) {
    case WarehouseStatus.Pending:
      return 'secondary'
    case WarehouseStatus.Processing:
      return 'default'
    case WarehouseStatus.Completed:
      return 'success'
    case WarehouseStatus.Failed:
    case WarehouseStatus.Canceled:
    case WarehouseStatus.Unauthorized:
      return 'destructive'
    default:
      return 'secondary'
  }
}

interface RepositoryCardProps {
  repository: RepositoryInfo
  onClick?: (repository: RepositoryInfo) => void
}

export const RepositoryCard: React.FC<RepositoryCardProps> = React.memo(({ repository, onClick }) => {
  const { t } = useTranslation()

  // 缓存状态信息
  const statusInfo = useMemo(() => ({
    label: t(`home.repository_card.status.${repository.status}`),
    variant: getStatusVariant(repository.status)
  }), [repository.status, t])

  // 缓存头像显示文本
  const avatarText = useMemo(() =>
    repository.organizationName.substring(0, 2).toUpperCase(),
    [repository.organizationName]
  )

  // 缓存时间格式化
  const formattedTime = useMemo(() =>
    formatDistanceToNow(repository.createdAt),
    [repository.createdAt]
  )

  // 缓存点击处理器
  const handleClick = useCallback(() => {
    onClick?.(repository)
  }, [onClick, repository])

  return (
    <Card
      className="hover:shadow-md transition-shadow cursor-pointer h-full flex flex-col p-2 gap-2"
      onClick={handleClick}
    >
      <CardHeader className="pb-1 pt-1 px-2">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-base line-clamp-1">
            <span className="mr-1">{repository.name}</span>/
            <span className="ml-1 text-muted-foreground">{repository.organizationName}</span>
          </h3>
        </div>
      </CardHeader>

      <CardContent className="flex-1 pb-2 pt-1 px-2">
        <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
          {repository.description || t('repository.layout.no_description')}
        </p>
        {repository.error && (
          <div className="mt-1 flex items-start text-xs text-destructive">
            <AlertCircle className="h-3 w-3 mr-1 mt-0.5 flex-shrink-0" />
            <span className="line-clamp-2">{repository.error}</span>
          </div>
        )}
      </CardContent>

      <CardFooter className="pt-2 border-t px-2 pb-1">
        <div className="flex items-center justify-between w-full text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            {repository.branch && (
              <div className="flex items-center text-xs text-muted-foreground">
                <GitBranch className="h-3 w-3 mr-1" />
                {repository.branch}
              </div>
            )}
            <div className="flex items-center">
              <Star className="h-3 w-3 mr-1" />
              <span>{repository?.stars}</span>
            </div>
            <div className="flex items-center">
              <GitBranch className="h-3 w-3 mr-1" />
              <span>{repository?.forks}</span>
            </div>
            <div className="flex items-center gap-1 flex-wrap">
              <Badge className="px-1 py-0 text-xs h-5">{statusInfo.label}</Badge>
            </div>
          </div>
          <div className="flex items-center">
            <ChevronRight className="h-3 w-3 ml-1" />
          </div>
        </div>
      </CardFooter>
    </Card>
  )
})

RepositoryCard.displayName = 'RepositoryCard'

export default RepositoryCard