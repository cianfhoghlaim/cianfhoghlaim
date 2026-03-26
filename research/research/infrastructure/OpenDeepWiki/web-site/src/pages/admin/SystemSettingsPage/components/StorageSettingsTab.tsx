import React from 'react'
import {
  Folder,
  Cloud,
  Shield,
  Info,
  HelpCircle
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import type { SystemSetting, ValidationErrors } from '@/types/systemSettings'

import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Badge } from '@/components/ui/badge'
interface StorageSettingsTabProps {
  settings: SystemSetting[]
  onUpdate: (key: string, value: any) => void
  validationErrors: ValidationErrors
  loading?: boolean
}

const StorageSettingsTab: React.FC<StorageSettingsTabProps> = ({
  settings,
  onUpdate,
  validationErrors,
  loading = false
}) => {
  const { t } = useTranslation('admin')

  // 获取设置值的辅助函数
  const getSettingValue = (key: string) => {
    const setting = settings.find(s => s.key === key)
    return setting?.value || setting?.defaultValue || ''
  }

  // 获取布尔值设置
  const getBooleanValue = (key: string) => {
    const value = getSettingValue(key) as any
    return value === 'true' || value === true
  }

  // 获取数字值设置
  const getNumberValue = (key: string) => {
    const value = getSettingValue(key)
    return value ? parseInt(value, 10) : undefined
  }

  // 获取数组设置
  const getArrayValue = (key: string) => {
    const value = getSettingValue(key)
    try {
      return value ? JSON.parse(value) : []
    } catch {
      return []
    }
  }

  // 更新数组设置
  const updateArrayValue = (key: string, value: string[]) => {
    onUpdate(key, JSON.stringify(value))
  }

  // 文件类型选项
  const fileTypeOptions = [
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg',
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'txt', 'md', 'json', 'xml', 'csv',
    'zip', 'rar', '7z', 'tar', 'gz',
    'mp3', 'mp4', 'avi', 'mov', 'wmv'
  ]

  // 存储提供商选项
  const storageProviders = [
    { value: 'local', label: t('settings.storage.local') },
    { value: 'aws-s3', label: 'AWS S3' },
    { value: 'azure-blob', label: 'Azure Blob Storage' },
    { value: 'google-cloud', label: 'Google Cloud Storage' },
    { value: 'aliyun-oss', label: t('settings.storage.aliyunOSS') },
    { value: 'tencent-cos', label: t('settings.storage.tencentCOS') },
    { value: 'custom', label: t('settings.storage.custom') }
  ]

  // 存储层级选项
  const storageTierOptions = [
    { value: 'standard', label: t('settings.storage.standard') },
    { value: 'cold', label: t('settings.storage.cold') },
    { value: 'archive', label: t('settings.storage.archive') }
  ]

  const selectedFileTypes = getArrayValue('allowedFileTypes')

  return (
    <TooltipProvider>
      <div className="max-w-4xl space-y-6">
        <div>
          <h3 className="text-lg font-semibold">{t('settings.groups.storage')}</h3>
          <p className="text-sm text-muted-foreground mt-2">
            {t('settings.storageDescription')}
          </p>
        </div>

        <div className="space-y-6">
          {/* 本地存储配置 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Folder className="w-4 h-4" />
                {t('settings.storage.localStorage')}
              </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="fileStoragePath">{t('settings.storage.fileStoragePath')} *</Label>
                <div className="relative">
                  <Folder className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    id="fileStoragePath"
                    value={getSettingValue('fileStoragePath')}
                    onChange={(e) => onUpdate('fileStoragePath', e.target.value)}
                    placeholder={t('settings.storage.fileStoragePathPlaceholder')}
                    disabled={loading}
                    className={`pl-10 ${validationErrors.fileStoragePath ? 'border-destructive' : ''}`}
                  />
                </div>
                {validationErrors.fileStoragePath ? (
                  <p className="text-sm text-destructive">{validationErrors.fileStoragePath}</p>
                ) : (
                  <p className="text-sm text-muted-foreground">{t('settings.storage.fileStoragePathHelp')}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="backupStoragePath">{t('settings.storage.backupStoragePath')}</Label>
                <div className="relative">
                  <Shield className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    id="backupStoragePath"
                    value={getSettingValue('backupStoragePath')}
                    onChange={(e) => onUpdate('backupStoragePath', e.target.value)}
                    placeholder={t('settings.storage.backupStoragePathPlaceholder')}
                    disabled={loading}
                    className={`pl-10 ${validationErrors.backupStoragePath ? 'border-destructive' : ''}`}
                  />
                </div>
                {validationErrors.backupStoragePath && (
                  <p className="text-sm text-destructive">{validationErrors.backupStoragePath}</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* 文件上传限制 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">{t('settings.storage.uploadLimits')}</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Label htmlFor="maxFileSize">{t('settings.storage.maxFileSize')}</Label>
                  <Tooltip>
                    <TooltipTrigger>
                      <HelpCircle className="w-4 h-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{t('settings.storage.maxFileSizeHelp')}</p>
                    </TooltipContent>
                  </Tooltip>
                </div>
                <div className="flex">
                  <Input
                    id="maxFileSize"
                    type="number"
                    value={getNumberValue('maxFileSize') || ''}
                    onChange={(e) => onUpdate('maxFileSize', e.target.value)}
                    placeholder="10"
                    min={1}
                    max={1024}
                    disabled={loading}
                    className={`rounded-r-none ${validationErrors.maxFileSize ? 'border-destructive' : ''}`}
                  />
                  <span className="inline-flex items-center px-3 rounded-r-md border border-l-0 border-input bg-muted text-muted-foreground text-sm">
                    MB
                  </span>
                </div>
                {validationErrors.maxFileSize && (
                  <p className="text-sm text-destructive">{validationErrors.maxFileSize}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label>{t('settings.storage.allowedFileTypes')}</Label>
                <Select
                  value={selectedFileTypes.length > 0 ? selectedFileTypes[0] : ''}
                  onValueChange={(value) => {
                    const currentTypes = selectedFileTypes
                    if (value && !currentTypes.includes(value)) {
                      updateArrayValue('allowedFileTypes', [...currentTypes, value])
                    }
                  }}
                  disabled={loading}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={t('settings.storage.allowedFileTypesPlaceholder')} />
                  </SelectTrigger>
                  <SelectContent>
                    {fileTypeOptions
                      .filter(type => !selectedFileTypes.includes(type))
                      .map(type => (
                        <SelectItem key={type} value={type}>
                          {type}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
                <div className="flex flex-wrap gap-1">
                  {selectedFileTypes.map((type: string) => (
                    <Badge
                      key={type}
                      variant="secondary"
                      className="cursor-pointer"
                      onClick={() => {
                        const newTypes = selectedFileTypes.filter((t: string) => t !== type)
                        updateArrayValue('allowedFileTypes', newTypes)
                      }}
                    >
                      {type} ×
                    </Badge>
                  ))}
                </div>
                <p className="text-sm text-muted-foreground">{t('settings.storage.allowedFileTypesHelp')}</p>
              </div>
            </CardContent>
          </Card>

          {/* 文件压缩设置 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">{t('settings.storage.compression')}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label>{t('settings.storage.enableCompression')}</Label>
                <Switch
                  checked={getBooleanValue('enableCompression')}
                  onCheckedChange={(checked) => onUpdate('enableCompression', checked.toString())}
                  disabled={loading}
                />
              </div>
              {getBooleanValue('enableCompression') && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Label htmlFor="compressionQuality">{t('settings.storage.compressionQuality')}</Label>
                    <Tooltip>
                      <TooltipTrigger>
                        <HelpCircle className="w-4 h-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{t('settings.storage.compressionQualityHelp')}</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <div className="flex">
                    <Input
                      id="compressionQuality"
                      type="number"
                      value={getNumberValue('compressionQuality') || ''}
                      onChange={(e) => onUpdate('compressionQuality', e.target.value)}
                      placeholder="85"
                      min={1}
                      max={100}
                      disabled={loading}
                      className={`rounded-r-none ${validationErrors.compressionQuality ? 'border-destructive' : ''}`}
                    />
                    <span className="inline-flex items-center px-3 rounded-r-md border border-l-0 border-input bg-muted text-muted-foreground text-sm">
                      %
                    </span>
                  </div>
                  {validationErrors.compressionQuality && (
                    <p className="text-sm text-destructive">{validationErrors.compressionQuality}</p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* 存储层级设置 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">{t('settings.storage.storageTiers')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Label htmlFor="storageTiers">{t('settings.storage.defaultStorageTier')}</Label>
                  <Tooltip>
                    <TooltipTrigger>
                      <HelpCircle className="w-4 h-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{t('settings.storage.storageTiersHelp')}</p>
                    </TooltipContent>
                  </Tooltip>
                </div>
                <Select
                  value={getSettingValue('storageTiers')}
                  onValueChange={(value) => onUpdate('storageTiers', value)}
                  disabled={loading}
                >
                  <SelectTrigger className={validationErrors.storageTiers ? 'border-destructive' : ''}>
                    <SelectValue placeholder={t('settings.storage.storageTiersPlaceholder')} />
                  </SelectTrigger>
                  <SelectContent>
                    {storageTierOptions.map(tier => (
                      <SelectItem key={tier.value} value={tier.value}>
                        {tier.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {validationErrors.storageTiers && (
                  <p className="text-sm text-destructive">{validationErrors.storageTiers}</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* 云存储配置 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Cloud className="w-4 h-4" />
                {t('settings.storage.cloudStorage')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label>{t('settings.storage.enableCloudStorage')}</Label>
                <Switch
                  checked={getBooleanValue('enableCloudStorage')}
                  onCheckedChange={(checked) => onUpdate('enableCloudStorage', checked.toString())}
                  disabled={loading}
                />
              </div>
              {getBooleanValue('enableCloudStorage') && (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="cloudStorageProvider">{t('settings.storage.cloudStorageProvider')}</Label>
                    <Select
                      value={getSettingValue('cloudStorageProvider')}
                      onValueChange={(value) => onUpdate('cloudStorageProvider', value)}
                      disabled={loading}
                    >
                      <SelectTrigger className={validationErrors.cloudStorageProvider ? 'border-destructive' : ''}>
                        <SelectValue placeholder={t('settings.storage.cloudStorageProviderPlaceholder')} />
                      </SelectTrigger>
                      <SelectContent>
                        {storageProviders.map(provider => (
                          <SelectItem key={provider.value} value={provider.value}>
                            {provider.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {validationErrors.cloudStorageProvider && (
                      <p className="text-sm text-destructive">{validationErrors.cloudStorageProvider}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label htmlFor="cloudStorageConfig">{t('settings.storage.cloudStorageConfig')}</Label>
                      <Tooltip>
                        <TooltipTrigger>
                          <HelpCircle className="w-4 h-4 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>{t('settings.storage.cloudStorageConfigHelp')}</p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Textarea
                      id="cloudStorageConfig"
                      rows={6}
                      value={getSettingValue('cloudStorageConfig')}
                      onChange={(e) => onUpdate('cloudStorageConfig', e.target.value)}
                      placeholder={t('settings.storage.cloudStorageConfigPlaceholder')}
                      disabled={loading}
                      className={validationErrors.cloudStorageConfig ? 'border-destructive' : ''}
                    />
                    {validationErrors.cloudStorageConfig && (
                      <p className="text-sm text-destructive">{validationErrors.cloudStorageConfig}</p>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* 存储使用情况显示 */}
          <Alert>
            <Info className="h-4 w-4" />
            <AlertTitle>{t('settings.storage.storageUsage')}</AlertTitle>
            <AlertDescription>
              <p className="mb-3">{t('settings.storage.storageUsageDescription')}</p>
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                  {t('settings.storage.totalSpace')}: 100 GB
                </Badge>
                <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                  {t('settings.storage.usedSpace')}: 25 GB
                </Badge>
                <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200">
                  {t('settings.storage.freeSpace')}: 75 GB
                </Badge>
              </div>
            </AlertDescription>
          </Alert>

          {/* 存储优化建议 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">{t('settings.storage.optimizationTips')}</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>{t('settings.storage.tip1')}</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>{t('settings.storage.tip2')}</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>{t('settings.storage.tip3')}</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>{t('settings.storage.tip4')}</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </TooltipProvider>
  )
}

export default StorageSettingsTab