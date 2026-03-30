import React, { useState } from 'react'
import {
  Github,
  GitBranch,
  User,
  Link,
  RotateCw,
  Info,
  HelpCircle,
  Key,
  Globe,
  Plus,
  X
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import type { SystemSetting, ValidationErrors, SettingGroupType } from '@/types/systemSettings'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Badge } from '@/components/ui/badge'

interface ThirdPartySettingsTabProps {
  settings: SystemSetting[]
  onUpdate: (key: string, value: any) => void
  validationErrors: ValidationErrors
  loading?: boolean
  group: SettingGroupType
}

const ThirdPartySettingsTab: React.FC<ThirdPartySettingsTabProps> = ({
  settings,
  onUpdate,
  validationErrors,
  loading = false,
  group
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

  // 根据group获取配置
  const getGroupConfig = () => {
    switch (group) {
      case 'GitHub':
        return {
          title: t('settings.groups.github'),
          icon: <Github className="w-4 h-4" />,
          color: 'text-gray-900',
          keyPrefix: 'GitHub.',
          fields: [
            { key: 'ClientId', label: t('settings.github.clientId'), required: true, sensitive: false },
            { key: 'ClientSecret', label: t('settings.github.clientSecret'), required: true, sensitive: true },
            { key: 'Token', label: t('settings.github.token'), required: false, sensitive: true },
            { key: 'webhookSecret', label: t('settings.github.webhookSecret'), required: false, sensitive: true },
          ],
          oauthUrl: 'https://github.com/settings/developers',
          docsUrl: 'https://docs.github.com/en/developers/apps/building-oauth-apps/creating-an-oauth-app'
        }
      case 'Gitee':
        return {
          title: t('settings.groups.gitee'),
          icon: <GitBranch className="w-4 h-4" />,
          color: 'text-red-600',
          keyPrefix: 'Gitee.',
          fields: [
            { key: 'ClientId', label: t('settings.gitee.clientId'), required: true, sensitive: false },
            { key: 'ClientSecret', label: t('settings.gitee.clientSecret'), required: true, sensitive: true },
            { key: 'Token', label: t('settings.gitee.token'), required: false, sensitive: true },
            { key: 'webhookSecret', label: t('settings.gitee.webhookSecret'), required: false, sensitive: true },
          ],
          oauthUrl: 'https://gitee.com/oauth/applications',
          docsUrl: 'https://gitee.com/api/v5/oauth_doc'
        }
      default:
        return null
    }
  }

  const config = getGroupConfig()
  if (!config) return null

  // 同步间隔选项
  const syncIntervalOptions = [
    { value: 5, label: t('settings.thirdParty.every5Minutes') },
    { value: 15, label: t('settings.thirdParty.every15Minutes') },
    { value: 30, label: t('settings.thirdParty.every30Minutes') },
    { value: 60, label: t('settings.thirdParty.everyHour') },
    { value: 360, label: t('settings.thirdParty.every6Hours') },
    { value: 720, label: t('settings.thirdParty.every12Hours') },
    { value: 1440, label: t('settings.thirdParty.everyDay') }
  ]

  // 组织标签列表组件
  const OrganizationsList = ({
    value = [],
    onChange
  }: {
    value?: string[]
    onChange?: (value: string[]) => void
  }) => {
    const [inputValue, setInputValue] = useState('')

    const addOrganization = () => {
      if (inputValue && !value.includes(inputValue)) {
        onChange?.([...value, inputValue])
        setInputValue('')
      }
    }

    const removeOrganization = (org: string) => {
      onChange?.(value.filter(item => item !== org))
    }

    return (
      <div className="space-y-3">
        <div className="flex gap-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={t('settings.thirdParty.allowedOrganizationsPlaceholder')}
            onKeyDown={(e) => e.key === 'Enter' && addOrganization()}
            className="flex-1"
          />
          <Button
            type="button"
            onClick={addOrganization}
            disabled={!inputValue || value.includes(inputValue)}
            size="sm"
          >
            <Plus className="w-4 h-4 mr-1" />
            {t('common.add')}
          </Button>
        </div>
        {value.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {value.map((org, index) => (
              <Badge
                key={index}
                variant="secondary"
                className="cursor-pointer"
                onClick={() => removeOrganization(org)}
              >
                {org}
                <X className="w-3 h-3 ml-1" />
              </Badge>
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <TooltipProvider>
      <div className="max-w-4xl space-y-6">
        <div>
          <h3 className={`text-lg font-semibold flex items-center gap-2 ${config.color}`}>
            {config.icon}
            {config.title}
          </h3>
          <p className="text-sm text-muted-foreground mt-2">
            {t('settings.thirdPartyDescription', { platform: config.title })}
          </p>
        </div>

        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>{t('settings.thirdParty.setupNote')}</AlertTitle>
          <AlertDescription>
            <div className="space-y-3">
              <p>{t('settings.thirdParty.setupNoteDescription', { platform: config.title })}</p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  asChild
                >
                  <a href={config.oauthUrl} target="_blank" rel="noopener noreferrer">
                    <Link className="w-4 h-4 mr-2" />
                    {t('settings.thirdParty.createApp')}
                  </a>
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  asChild
                >
                  <a href={config.docsUrl} target="_blank" rel="noopener noreferrer">
                    <Info className="w-4 h-4 mr-2" />
                    {t('settings.thirdParty.viewDocs')}
                  </a>
                </Button>
              </div>
            </div>
          </AlertDescription>
        </Alert>

        <div className="space-y-6">
          {/* OAuth 配置 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <User className="w-4 h-4" />
                {t('settings.thirdParty.oauthConfiguration')}
              </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              {config.fields.map(field => (
                <div key={field.key} className="space-y-2">
                  <div className="flex items-center gap-2">
                    {field.sensitive && <Key className="w-4 h-4 text-muted-foreground" />}
                    <Label htmlFor={field.key}>
                      {field.label}
                      {field.required && <span className="text-destructive ml-1">*</span>}
                    </Label>
                  </div>
                  <Input
                    id={field.key}
                    type={field.sensitive ? 'password' : 'text'}
                    value={getSettingValue(config.keyPrefix + field.key)}
                    onChange={(e) => onUpdate(config.keyPrefix + field.key, e.target.value)}
                    placeholder={t('settings.thirdParty.inputPlaceholder', { field: field.label })}
                    disabled={loading}
                    className={validationErrors[config.keyPrefix + field.key] ? 'border-destructive' : ''}
                  />
                  {validationErrors[config.keyPrefix + field.key] && (
                    <p className="text-sm text-destructive">{validationErrors[config.keyPrefix + field.key]}</p>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>

          {/* OAuth 设置 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Globe className="w-4 h-4" />
                {t('settings.thirdParty.oauthSettings')}
              </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>{t('settings.thirdParty.enableOAuth')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('settings.thirdParty.enableOAuthHelp', { platform: config.title })}
                  </p>
                </div>
                <Switch
                  checked={getBooleanValue('enableOAuth')}
                  onCheckedChange={(checked) => onUpdate('enableOAuth', checked.toString())}
                  disabled={loading}
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Label>{t('settings.thirdParty.allowedOrganizations')}</Label>
                  <Tooltip>
                    <TooltipTrigger>
                      <HelpCircle className="w-4 h-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{t('settings.thirdParty.allowedOrganizationsHelp')}</p>
                    </TooltipContent>
                  </Tooltip>
                </div>
                <OrganizationsList
                  value={getArrayValue('allowedOrganizations')}
                  onChange={(value) => updateArrayValue('allowedOrganizations', value)}
                />
                <p className="text-sm text-muted-foreground">
                  {t('settings.thirdParty.allowedOrganizationsDescription')}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* 仓库同步设置 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <RotateCw className="w-4 h-4" />
                {t('settings.thirdParty.repositorySync')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>{t('settings.thirdParty.enableAutoSync')}</Label>
                    <p className="text-sm text-muted-foreground">
                      {t('settings.thirdParty.enableAutoSyncHelp')}
                    </p>
                  </div>
                  <Switch
                    checked={getBooleanValue('enableAutoSync')}
                    onCheckedChange={(checked) => onUpdate('enableAutoSync', checked.toString())}
                    disabled={loading}
                  />
                </div>
                {getBooleanValue('enableAutoSync') && (
                  <div className="md:col-span-2 space-y-2">
                    <Label htmlFor="syncInterval">{t('settings.thirdParty.syncInterval')}</Label>
                    <Select
                      value={getNumberValue('syncInterval')?.toString()}
                      onValueChange={(value) => onUpdate('syncInterval', value)}
                      disabled={loading}
                    >
                      <SelectTrigger className={validationErrors.syncInterval ? 'border-destructive' : ''}>
                        <SelectValue placeholder={t('settings.thirdParty.syncIntervalPlaceholder')} />
                      </SelectTrigger>
                      <SelectContent>
                        {syncIntervalOptions.map(option => (
                          <SelectItem key={option.value} value={option.value.toString()}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {validationErrors.syncInterval && (
                      <p className="text-sm text-destructive">{validationErrors.syncInterval}</p>
                    )}
                  </div>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="defaultRepository">{t('settings.thirdParty.defaultRepository')}</Label>
                <div className="flex">
                  <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-input bg-muted text-muted-foreground text-sm">
                    {group === 'GitHub' ? 'github.com/' : 'gitee.com/'}
                  </span>
                  <Input
                    id="defaultRepository"
                    value={getSettingValue('defaultRepository')}
                    onChange={(e) => onUpdate('defaultRepository', e.target.value)}
                    placeholder={t('settings.thirdParty.defaultRepositoryPlaceholder')}
                    disabled={loading}
                    className={`rounded-l-none ${validationErrors.defaultRepository ? 'border-destructive' : ''}`}
                  />
                </div>
                {validationErrors.defaultRepository ? (
                  <p className="text-sm text-destructive">{validationErrors.defaultRepository}</p>
                ) : (
                  <p className="text-sm text-muted-foreground">{t('settings.thirdParty.defaultRepositoryHelp')}</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* 回调URL信息 */}
          <Alert>
            <Info className="h-4 w-4" />
            <AlertTitle>{t('settings.thirdParty.callbackUrls')}</AlertTitle>
            <AlertDescription>
              <div className="space-y-3">
                <p>{t('settings.thirdParty.callbackUrlsDescription')}</p>
                <div className="bg-muted p-3 rounded-md font-mono text-sm">
                  <div className="font-semibold">OAuth Callback URL:</div>
                  <div className="text-muted-foreground">https://yourdomain.com/api/auth/{group.toLowerCase()}/callback</div>
                  <div className="font-semibold mt-2">Webhook URL:</div>
                  <div className="text-muted-foreground">https://yourdomain.com/api/webhooks/{group.toLowerCase()}</div>
                </div>
              </div>
            </AlertDescription>
          </Alert>

          {/* 连接状态 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">{t('settings.thirdParty.connectionStatus')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="text-center space-y-2">
                  <Badge
                    variant={getSettingValue(config.keyPrefix + 'ClientId') ? 'default' : 'destructive'}
                    className={getSettingValue(config.keyPrefix + 'ClientId') ? 'bg-green-100 text-green-800 border-green-200' : ''}
                  >
                    {getSettingValue(config.keyPrefix + 'ClientId') ? t('common.configured') : t('common.notConfigured')}
                  </Badge>
                  <p className="text-xs text-muted-foreground">
                    {t('settings.thirdParty.oauthStatus')}
                  </p>
                </div>
                <div className="text-center space-y-2">
                  <Badge
                    variant={getSettingValue(config.keyPrefix + 'Token') ? 'default' : 'secondary'}
                    className={getSettingValue(config.keyPrefix + 'Token') ? 'bg-green-100 text-green-800 border-green-200' : 'bg-orange-100 text-orange-800 border-orange-200'}
                  >
                    {getSettingValue(config.keyPrefix + 'Token') ? t('common.configured') : t('common.optional')}
                  </Badge>
                  <p className="text-xs text-muted-foreground">
                    {t('settings.thirdParty.apiTokenStatus')}
                  </p>
                </div>
                <div className="text-center space-y-2">
                  <Badge
                    variant={getBooleanValue('enableAutoSync') ? 'default' : 'secondary'}
                    className={getBooleanValue('enableAutoSync') ? 'bg-blue-100 text-blue-800 border-blue-200' : ''}
                  >
                    {getBooleanValue('enableAutoSync') ? t('common.enabled') : t('common.disabled')}
                  </Badge>
                  <p className="text-xs text-muted-foreground">
                    {t('settings.thirdParty.autoSyncStatus')}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 配置指南 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">{t('settings.thirdParty.configurationGuide')}</CardTitle>
            </CardHeader>
            <CardContent>
              <ol className="space-y-2 text-sm text-muted-foreground list-decimal list-inside">
                <li>{t('settings.thirdParty.step1', { platform: config.title })}</li>
                <li>{t('settings.thirdParty.step2')}</li>
                <li>{t('settings.thirdParty.step3')}</li>
                <li>{t('settings.thirdParty.step4')}</li>
                <li>{t('settings.thirdParty.step5')}</li>
              </ol>
            </CardContent>
          </Card>
        </div>
      </div>
    </TooltipProvider>
  )
}

export default ThirdPartySettingsTab