import React, { useState } from 'react'
import {
  Shield,
  Lock,
  User,
  Globe,
  AlertTriangle,
  Info,
  HelpCircle,
  Plus,
  X
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import type { SystemSetting, ValidationErrors } from '@/types/systemSettings'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Badge } from '@/components/ui/badge'

interface SecuritySettingsTabProps {
  settings: SystemSetting[]
  onUpdate: (key: string, value: any) => void
  validationErrors: ValidationErrors
  loading?: boolean
}

const SecuritySettingsTab: React.FC<SecuritySettingsTabProps> = ({
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

  // 验证码提供商选项
  const captchaProviders = [
    { value: 'recaptcha', label: 'Google reCAPTCHA' },
    { value: 'hcaptcha', label: 'hCaptcha' },
    { value: 'turnstile', label: 'Cloudflare Turnstile' },
    { value: 'custom', label: t('settings.security.customCaptcha') }
  ]

  // IP地址输入组件
  const IPAddressList = ({
    value = [],
    onChange,
    placeholder
  }: {
    value?: string[]
    onChange?: (value: string[]) => void
    placeholder?: string
  }) => {
    const [inputValue, setInputValue] = useState('')

    const addIP = () => {
      if (inputValue && !value.includes(inputValue)) {
        onChange?.([...value, inputValue])
        setInputValue('')
      }
    }

    const removeIP = (ip: string) => {
      onChange?.(value.filter(item => item !== ip))
    }

    return (
      <div className="space-y-3">
        <div className="flex gap-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={placeholder}
            onKeyDown={(e) => e.key === 'Enter' && addIP()}
            className="flex-1"
          />
          <Button
            type="button"
            onClick={addIP}
            disabled={!inputValue || value.includes(inputValue)}
            size="sm"
          >
            <Plus className="w-4 h-4 mr-1" />
            {t('common.add')}
          </Button>
        </div>
        {value.length > 0 && (
          <div className="border rounded-md p-3 max-h-32 overflow-y-auto">
            <div className="flex flex-wrap gap-1">
              {value.map((ip, index) => (
                <Badge
                  key={index}
                  variant="secondary"
                  className="cursor-pointer"
                  onClick={() => removeIP(ip)}
                >
                  {ip}
                  <X className="w-3 h-3 ml-1" />
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <TooltipProvider>
      <div className="max-w-4xl space-y-6">
        <div>
          <h3 className="text-lg font-semibold">{t('settings.groups.security')}</h3>
          <p className="text-sm text-muted-foreground mt-2">
            {t('settings.securityDescription')}
          </p>
        </div>

        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>{t('settings.security.securityNote')}</AlertTitle>
          <AlertDescription>
            {t('settings.security.securityNoteDescription')}
          </AlertDescription>
        </Alert>

        <div className="space-y-6">
          {/* 密码策略 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Lock className="w-4 h-4" />
                {t('settings.security.passwordPolicy')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="passwordMinLength">{t('settings.security.passwordMinLength')}</Label>
                  <Input
                    id="passwordMinLength"
                    type="number"
                    value={getNumberValue('passwordMinLength') || ''}
                    onChange={(e) => onUpdate('passwordMinLength', e.target.value)}
                    placeholder="8"
                    min={6}
                    max={128}
                    disabled={loading}
                    className={validationErrors.passwordMinLength ? 'border-destructive' : ''}
                  />
                  {validationErrors.passwordMinLength && (
                    <p className="text-sm text-destructive">{validationErrors.passwordMinLength}</p>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center justify-between">
                    <Label>{t('settings.security.requireNumbers')}</Label>
                    <Switch
                      checked={getBooleanValue('passwordRequireNumbers')}
                      onCheckedChange={(checked) => onUpdate('passwordRequireNumbers', checked.toString())}
                      disabled={loading}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label>{t('settings.security.requireSymbols')}</Label>
                    <Switch
                      checked={getBooleanValue('passwordRequireSymbols')}
                      onCheckedChange={(checked) => onUpdate('passwordRequireSymbols', checked.toString())}
                      disabled={loading}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label>{t('settings.security.requireUppercase')}</Label>
                    <Switch
                      checked={getBooleanValue('passwordRequireUppercase')}
                      onCheckedChange={(checked) => onUpdate('passwordRequireUppercase', checked.toString())}
                      disabled={loading}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label>{t('settings.security.requireLowercase')}</Label>
                    <Switch
                      checked={getBooleanValue('passwordRequireLowercase')}
                      onCheckedChange={(checked) => onUpdate('passwordRequireLowercase', checked.toString())}
                      disabled={loading}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 会话管理 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <User className="w-4 h-4" />
                {t('settings.security.sessionManagement')}
              </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Label htmlFor="sessionTimeout">{t('settings.security.sessionTimeout')}</Label>
                  <Tooltip>
                    <TooltipTrigger>
                      <HelpCircle className="w-4 h-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{t('settings.security.sessionTimeoutHelp')}</p>
                    </TooltipContent>
                  </Tooltip>
                </div>
                <div className="flex">
                  <Input
                    id="sessionTimeout"
                    type="number"
                    value={getNumberValue('sessionTimeoutMinutes') || ''}
                    onChange={(e) => onUpdate('sessionTimeoutMinutes', e.target.value)}
                    placeholder="1440"
                    min={5}
                    max={43200}
                    disabled={loading}
                    className={`rounded-r-none ${validationErrors.sessionTimeoutMinutes ? 'border-destructive' : ''}`}
                  />
                  <span className="inline-flex items-center px-3 rounded-r-md border border-l-0 border-input bg-muted text-muted-foreground text-sm">
                    {t('common.minutes')}
                  </span>
                </div>
                {validationErrors.sessionTimeoutMinutes && (
                  <p className="text-sm text-destructive">{validationErrors.sessionTimeoutMinutes}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="maxLoginAttempts">{t('settings.security.maxLoginAttempts')}</Label>
                <Input
                  id="maxLoginAttempts"
                  type="number"
                  value={getNumberValue('maxLoginAttempts') || ''}
                  onChange={(e) => onUpdate('maxLoginAttempts', e.target.value)}
                  placeholder="5"
                  min={1}
                  max={20}
                  disabled={loading}
                  className={validationErrors.maxLoginAttempts ? 'border-destructive' : ''}
                />
                {validationErrors.maxLoginAttempts && (
                  <p className="text-sm text-destructive">{validationErrors.maxLoginAttempts}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="lockoutDuration">{t('settings.security.lockoutDuration')}</Label>
                <div className="flex">
                  <Input
                    id="lockoutDuration"
                    type="number"
                    value={getNumberValue('lockoutDurationMinutes') || ''}
                    onChange={(e) => onUpdate('lockoutDurationMinutes', e.target.value)}
                    placeholder="30"
                    min={1}
                    max={1440}
                    disabled={loading}
                    className={`rounded-r-none ${validationErrors.lockoutDurationMinutes ? 'border-destructive' : ''}`}
                  />
                  <span className="inline-flex items-center px-3 rounded-r-md border border-l-0 border-input bg-muted text-muted-foreground text-sm">
                    {t('common.minutes')}
                  </span>
                </div>
                {validationErrors.lockoutDurationMinutes && (
                  <p className="text-sm text-destructive">{validationErrors.lockoutDurationMinutes}</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* 双因素认证 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Shield className="w-4 h-4" />
                {t('settings.security.twoFactorAuth')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>{t('settings.security.enableTwoFactorAuth')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('settings.security.twoFactorAuthHelp')}
                  </p>
                </div>
                <Switch
                  checked={getBooleanValue('enableTwoFactorAuth')}
                  onCheckedChange={(checked) => onUpdate('enableTwoFactorAuth', checked.toString())}
                  disabled={loading}
                />
              </div>
              {getBooleanValue('enableTwoFactorAuth') && (
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertTitle>{t('settings.security.twoFactorAuthEnabled')}</AlertTitle>
                  <AlertDescription>
                    {t('settings.security.twoFactorAuthEnabledDescription')}
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* IP访问控制 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Globe className="w-4 h-4" />
                {t('settings.security.ipAccessControl')}
              </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-6 md:grid-cols-2">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Label>{t('settings.security.allowedIpAddresses')}</Label>
                  <Tooltip>
                    <TooltipTrigger>
                      <HelpCircle className="w-4 h-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{t('settings.security.allowedIpHelp')}</p>
                    </TooltipContent>
                  </Tooltip>
                </div>
                <IPAddressList
                  value={getArrayValue('allowedIpAddresses')}
                  onChange={(value) => updateArrayValue('allowedIpAddresses', value)}
                  placeholder={t('settings.security.ipAddressPlaceholder')}
                />
                <p className="text-sm text-muted-foreground">
                  {t('settings.security.allowedIpDescription')}
                </p>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Label>{t('settings.security.blockedIpAddresses')}</Label>
                  <Tooltip>
                    <TooltipTrigger>
                      <HelpCircle className="w-4 h-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{t('settings.security.blockedIpHelp')}</p>
                    </TooltipContent>
                  </Tooltip>
                </div>
                <IPAddressList
                  value={getArrayValue('blockedIpAddresses')}
                  onChange={(value) => updateArrayValue('blockedIpAddresses', value)}
                  placeholder={t('settings.security.ipAddressPlaceholder')}
                />
                <p className="text-sm text-muted-foreground">
                  {t('settings.security.blockedIpDescription')}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* 验证码设置 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Shield className="w-4 h-4" />
                {t('settings.security.captchaSettings')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label>{t('settings.security.enableCaptcha')}</Label>
                <Switch
                  checked={getBooleanValue('enableCaptcha')}
                  onCheckedChange={(checked) => onUpdate('enableCaptcha', checked.toString())}
                  disabled={loading}
                />
              </div>
              {getBooleanValue('enableCaptcha') && (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="captchaProvider">{t('settings.security.captchaProvider')}</Label>
                    <Select
                      value={getSettingValue('captchaProvider')}
                      onValueChange={(value) => onUpdate('captchaProvider', value)}
                      disabled={loading}
                    >
                      <SelectTrigger className={validationErrors.captchaProvider ? 'border-destructive' : ''}>
                        <SelectValue placeholder={t('settings.security.captchaProviderPlaceholder')} />
                      </SelectTrigger>
                      <SelectContent>
                        {captchaProviders.map(provider => (
                          <SelectItem key={provider.value} value={provider.value}>
                            {provider.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {validationErrors.captchaProvider && (
                      <p className="text-sm text-destructive">{validationErrors.captchaProvider}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label htmlFor="captchaConfig">{t('settings.security.captchaConfig')}</Label>
                      <Tooltip>
                        <TooltipTrigger>
                          <HelpCircle className="w-4 h-4 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>{t('settings.security.captchaConfigHelp')}</p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Textarea
                      id="captchaConfig"
                      rows={4}
                      value={getSettingValue('captchaConfig')}
                      onChange={(e) => onUpdate('captchaConfig', e.target.value)}
                      placeholder={t('settings.security.captchaConfigPlaceholder')}
                      disabled={loading}
                      className={validationErrors.captchaConfig ? 'border-destructive' : ''}
                    />
                    {validationErrors.captchaConfig && (
                      <p className="text-sm text-destructive">{validationErrors.captchaConfig}</p>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* 安全建议 */}
          <Alert>
            <Info className="h-4 w-4" />
            <AlertTitle>{t('settings.security.securityTips')}</AlertTitle>
            <AlertDescription>
              <ul className="space-y-1 text-sm mt-2">
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>{t('settings.security.tip1')}</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>{t('settings.security.tip2')}</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>{t('settings.security.tip3')}</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>{t('settings.security.tip4')}</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>{t('settings.security.tip5')}</span>
                </li>
              </ul>
            </AlertDescription>
          </Alert>
        </div>
      </div>
    </TooltipProvider>
  )
}

export default SecuritySettingsTab