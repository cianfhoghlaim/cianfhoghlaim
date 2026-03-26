import React, { useState } from 'react'
import {
  Mail,
  Send,
  Info
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { systemSettingsService } from '@/services/admin.service'
import type { SystemSetting, ValidationErrors, EmailTestParams } from '@/types/systemSettings'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { useToast } from '@/hooks/useToast'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

interface EmailSettingsTabProps {
  settings: SystemSetting[]
  onUpdate: (key: string, value: any) => void
  validationErrors: ValidationErrors
  loading?: boolean
}

const EmailSettingsTab: React.FC<EmailSettingsTabProps> = ({
  settings,
  onUpdate,
  validationErrors,
  loading = false
}) => {
  const { t } = useTranslation('admin')
  const { toast } = useToast()
  const [testModalVisible, setTestModalVisible] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testEmail, setTestEmail] = useState('')
  const [testSubject, setTestSubject] = useState('')
  const [testBody, setTestBody] = useState('')

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

  // 测试邮件配置
  const testEmailSettings = async () => {
    if (!testEmail) {
      toast({
        title: t('settings.email.testEmailRequired'),
        variant: 'destructive',
      })
      return
    }

    try {
      setTesting(true)

      const params: EmailTestParams = {
        to: testEmail,
        subject: testSubject || t('settings.email.defaultTestSubject'),
        body: testBody || t('settings.email.defaultTestBody')
      }

      const result = await systemSettingsService.testEmailSettings(params) as any

      if (result.success) {
        toast({
          title: t('settings.email.testSuccess'),
        })
        setTestModalVisible(false)
      } else {
        toast({
          title: result.message || t('settings.email.testFailed'),
          variant: 'destructive',
        })
      }
    } catch (error) {
      console.error('Email test failed:', error)
      toast({
        title: t('settings.email.testFailed'),
        variant: 'destructive',
      })
    } finally {
      setTesting(false)
    }
  }

  return (
    <div className="max-w-4xl space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-lg font-semibold">{t('settings.groups.email')}</h3>
          <p className="text-sm text-muted-foreground mt-2">
            {t('settings.emailDescription')}
          </p>
        </div>
        <Button
          onClick={() => setTestModalVisible(true)}
          disabled={loading}
        >
          <Send className="w-4 h-4 mr-2" />
          {t('settings.email.testConnection')}
        </Button>
      </div>

      <Alert>
        <Info className="h-4 w-4" />
        <AlertTitle>{t('settings.email.securityNote')}</AlertTitle>
        <AlertDescription>
          {t('settings.email.securityNoteDescription')}
        </AlertDescription>
      </Alert>

      <div className="grid gap-6 md:grid-cols-2">
        {/* SMTP服务器 */}
        <div className="space-y-2">
          <Label htmlFor="smtpHost">{t('settings.email.smtpHost')} *</Label>
          <Input
            id="smtpHost"
            value={getSettingValue('smtpHost')}
            onChange={(e) => onUpdate('smtpHost', e.target.value)}
            placeholder={t('settings.email.smtpHostPlaceholder')}
            disabled={loading}
            className={validationErrors.smtpHost ? 'border-destructive' : ''}
          />
          {validationErrors.smtpHost && (
            <p className="text-sm text-destructive">{validationErrors.smtpHost}</p>
          )}
        </div>

        {/* SMTP端口 */}
        <div className="space-y-2">
          <Label htmlFor="smtpPort">{t('settings.email.smtpPort')} *</Label>
          <Input
            id="smtpPort"
            type="number"
            value={getNumberValue('smtpPort') || ''}
            onChange={(e) => onUpdate('smtpPort', e.target.value)}
            placeholder={t('settings.email.smtpPortPlaceholder')}
            min={1}
            max={65535}
            disabled={loading}
            className={validationErrors.smtpPort ? 'border-destructive' : ''}
          />
          {validationErrors.smtpPort && (
            <p className="text-sm text-destructive">{validationErrors.smtpPort}</p>
          )}
        </div>

        {/* SMTP用户名 */}
        <div className="space-y-2">
          <Label htmlFor="smtpUser">{t('settings.email.smtpUser')} *</Label>
          <Input
            id="smtpUser"
            value={getSettingValue('smtpUser')}
            onChange={(e) => onUpdate('smtpUser', e.target.value)}
            placeholder={t('settings.email.smtpUserPlaceholder')}
            disabled={loading}
            className={validationErrors.smtpUser ? 'border-destructive' : ''}
          />
          {validationErrors.smtpUser && (
            <p className="text-sm text-destructive">{validationErrors.smtpUser}</p>
          )}
        </div>

        {/* SMTP密码 */}
        <div className="space-y-2">
          <Label htmlFor="smtpPassword">{t('settings.email.smtpPassword')} *</Label>
          <Input
            id="smtpPassword"
            type="password"
            value={getSettingValue('smtpPassword')}
            onChange={(e) => onUpdate('smtpPassword', e.target.value)}
            placeholder={t('settings.email.smtpPasswordPlaceholder')}
            disabled={loading}
            className={validationErrors.smtpPassword ? 'border-destructive' : ''}
          />
          {validationErrors.smtpPassword && (
            <p className="text-sm text-destructive">{validationErrors.smtpPassword}</p>
          )}
        </div>

        {/* SSL/TLS设置 */}
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">{t('settings.email.securitySettings')}</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-6 md:grid-cols-2">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>{t('settings.email.enableSsl')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('settings.email.enableSslHelp')}
                  </p>
                </div>
                <Switch
                  checked={getBooleanValue('smtpEnableSsl')}
                  onCheckedChange={(checked) => onUpdate('smtpEnableSsl', checked.toString())}
                  disabled={loading}
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>{t('settings.email.enableTls')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('settings.email.enableTlsHelp')}
                  </p>
                </div>
                <Switch
                  checked={getBooleanValue('smtpEnableTls')}
                  onCheckedChange={(checked) => onUpdate('smtpEnableTls', checked.toString())}
                  disabled={loading}
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 发件人信息 */}
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">{t('settings.email.senderInfo')}</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="senderName">{t('settings.email.senderName')}</Label>
                <Input
                  id="senderName"
                  value={getSettingValue('senderName')}
                  onChange={(e) => onUpdate('senderName', e.target.value)}
                  placeholder={t('settings.email.senderNamePlaceholder')}
                  disabled={loading}
                  className={validationErrors.senderName ? 'border-destructive' : ''}
                />
                {validationErrors.senderName && (
                  <p className="text-sm text-destructive">{validationErrors.senderName}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="senderEmail">{t('settings.email.senderEmail')}</Label>
                <Input
                  id="senderEmail"
                  type="email"
                  value={getSettingValue('senderEmail')}
                  onChange={(e) => onUpdate('senderEmail', e.target.value)}
                  placeholder={t('settings.email.senderEmailPlaceholder')}
                  disabled={loading}
                  className={validationErrors.senderEmail ? 'border-destructive' : ''}
                />
                {validationErrors.senderEmail && (
                  <p className="text-sm text-destructive">{validationErrors.senderEmail}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="replyToEmail">{t('settings.email.replyToEmail')}</Label>
                <Input
                  id="replyToEmail"
                  type="email"
                  value={getSettingValue('replyToEmail')}
                  onChange={(e) => onUpdate('replyToEmail', e.target.value)}
                  placeholder={t('settings.email.replyToEmailPlaceholder')}
                  disabled={loading}
                  className={validationErrors.replyToEmail ? 'border-destructive' : ''}
                />
                {validationErrors.replyToEmail && (
                  <p className="text-sm text-destructive">{validationErrors.replyToEmail}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="maxEmailsPerHour">{t('settings.email.maxEmailsPerHour')}</Label>
                <Input
                  id="maxEmailsPerHour"
                  type="number"
                  value={getNumberValue('maxEmailsPerHour') || ''}
                  onChange={(e) => onUpdate('maxEmailsPerHour', e.target.value)}
                  placeholder="100"
                  min={1}
                  max={10000}
                  disabled={loading}
                  className={validationErrors.maxEmailsPerHour ? 'border-destructive' : ''}
                />
                {validationErrors.maxEmailsPerHour ? (
                  <p className="text-sm text-destructive">{validationErrors.maxEmailsPerHour}</p>
                ) : (
                  <p className="text-sm text-muted-foreground">{t('settings.email.maxEmailsPerHourHelp')}</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 邮件模板 */}
        <div className="md:col-span-2 space-y-2">
          <Label htmlFor="emailTemplate">{t('settings.email.emailTemplate')}</Label>
          <Textarea
            id="emailTemplate"
            rows={8}
            value={getSettingValue('emailTemplate')}
            onChange={(e) => onUpdate('emailTemplate', e.target.value)}
            placeholder={t('settings.email.emailTemplatePlaceholder')}
            disabled={loading}
            className={validationErrors.emailTemplate ? 'border-destructive' : ''}
          />
          {validationErrors.emailTemplate ? (
            <p className="text-sm text-destructive">{validationErrors.emailTemplate}</p>
          ) : (
            <p className="text-sm text-muted-foreground">{t('settings.email.emailTemplateHelp')}</p>
          )}
        </div>
      </div>

      {/* 测试邮件弹窗 */}
      <Dialog open={testModalVisible} onOpenChange={setTestModalVisible}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Mail className="w-5 h-5" />
              {t('settings.email.testEmailSettings')}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="testEmail">{t('settings.email.testEmailAddress')} *</Label>
              <Input
                id="testEmail"
                type="email"
                value={testEmail}
                onChange={(e) => setTestEmail(e.target.value)}
                placeholder={t('settings.email.testEmailPlaceholder')}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="testSubject">{t('settings.email.testSubject')}</Label>
              <Input
                id="testSubject"
                value={testSubject}
                onChange={(e) => setTestSubject(e.target.value)}
                placeholder={t('settings.email.defaultTestSubject')}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="testBody">{t('settings.email.testBody')}</Label>
              <Textarea
                id="testBody"
                rows={4}
                value={testBody}
                onChange={(e) => setTestBody(e.target.value)}
                placeholder={t('settings.email.defaultTestBody')}
              />
            </div>

            <Alert>
              <Info className="h-4 w-4" />
              <AlertTitle>{t('settings.email.testNote')}</AlertTitle>
              <AlertDescription>
                {t('settings.email.testNoteDescription')}
              </AlertDescription>
            </Alert>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setTestModalVisible(false)}
            >
              {t('common.cancel')}
            </Button>
            <Button
              onClick={testEmailSettings}
              disabled={testing}
            >
              {testing ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  {t('settings.email.sending')}
                </div>
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  {t('settings.email.sendTestEmail')}
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default EmailSettingsTab