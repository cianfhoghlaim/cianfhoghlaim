import React from 'react'
import {
  Upload,
  Trash2,
  Eye
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import type { SystemSetting, ValidationErrors } from '@/types/systemSettings'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent } from '@/components/ui/card'
import { useToast } from '@/hooks/useToast'

interface BasicSettingsTabProps {
  settings: SystemSetting[]
  onUpdate: (key: string, value: any) => void
  validationErrors: ValidationErrors
  loading?: boolean
}

const BasicSettingsTab: React.FC<BasicSettingsTabProps> = ({
  settings,
  onUpdate,
  validationErrors,
  loading = false
}) => {
  const { t } = useTranslation('admin')
  const { toast } = useToast()

  const getSettingValue = (key: string) => {
    const setting = settings.find(s => s.key === key)
    return setting?.value || setting?.defaultValue || ''
  }

  const handleFileUpload = async (key: string, file: File) => {
    const isImage = file.type.startsWith('image/')
    if (!isImage) {
      toast({
        title: t('settings.onlyImageAllowed'),
        variant: 'destructive',
      })
      return
    }

    const isLt2M = file.size / 1024 / 1024 < 2
    if (!isLt2M) {
      toast({
        title: t('settings.imageTooLarge'),
        variant: 'destructive',
      })
      return
    }

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('/api/upload/image', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        const fileUrl = data?.url || data?.data?.url
        if (fileUrl) {
          onUpdate(key, fileUrl)
          toast({
            title: t('settings.uploadSuccess'),
          })
        }
      } else {
        throw new Error('Upload failed')
      }
    } catch (error) {
      toast({
        title: t('settings.uploadFailed'),
        variant: 'destructive',
      })
    }
  }

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h3 className="text-lg font-semibold">{t('settings.groups.basic')}</h3>
        <p className="text-sm text-muted-foreground mt-2">
          {t('settings.basicDescription')}
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="siteName">{t('settings.basic.siteName')}</Label>
          <Input
            id="siteName"
            value={getSettingValue('siteName')}
            onChange={(e) => onUpdate('siteName', e.target.value)}
            placeholder={t('settings.basic.siteNamePlaceholder')}
            disabled={loading}
            className={validationErrors.siteName ? 'border-destructive' : ''}
          />
          {validationErrors.siteName && (
            <p className="text-sm text-destructive">{validationErrors.siteName}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="siteDescription">{t('settings.basic.siteDescription')}</Label>
          <Input
            id="siteDescription"
            value={getSettingValue('siteDescription')}
            onChange={(e) => onUpdate('siteDescription', e.target.value)}
            placeholder={t('settings.basic.siteDescriptionPlaceholder')}
            disabled={loading}
            className={validationErrors.siteDescription ? 'border-destructive' : ''}
          />
          {validationErrors.siteDescription && (
            <p className="text-sm text-destructive">{validationErrors.siteDescription}</p>
          )}
        </div>

        <div className="space-y-2 md:col-span-2">
          <Label htmlFor="siteLogo">{t('settings.basic.siteLogo')}</Label>
          <Card>
            <CardContent className="p-4">
              <div className="flex gap-4">
                <div className="flex-1">
                  <Input
                    id="siteLogo"
                    value={getSettingValue('siteLogo')}
                    onChange={(e) => onUpdate('siteLogo', e.target.value)}
                    placeholder={t('settings.basic.siteLogoPlaceholder')}
                    disabled={loading}
                    className={validationErrors.siteLogo ? 'border-destructive' : ''}
                  />
                </div>
                <div className="flex gap-2">
                  <Label htmlFor="logo-upload" className="cursor-pointer">
                    <Button
                      variant="outline"
                      size="sm"
                      asChild
                      disabled={loading}
                    >
                      <span>
                        <Upload className="w-4 h-4 mr-2" />
                        {t('common.upload')}
                      </span>
                    </Button>
                    <input
                      id="logo-upload"
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => {
                        const file = e.target.files?.[0]
                        if (file) handleFileUpload('siteLogo', file)
                      }}
                    />
                  </Label>
                  {getSettingValue('siteLogo') && (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(getSettingValue('siteLogo'), '_blank')}
                        disabled={loading}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => onUpdate('siteLogo', '')}
                        disabled={loading}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </>
                  )}
                </div>
              </div>
              {getSettingValue('siteLogo') && (
                <div className="mt-4">
                  <img
                    src={getSettingValue('siteLogo')}
                    alt="Site Logo"
                    className="max-h-20 max-w-[200px] object-contain"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement
                      target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjgwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iODAiIGZpbGw9IiNmMGYwZjAiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iIGZvbnQtZmFtaWx5PSJzYW5zLXNlcmlmIiBmb250LXNpemU9IjE0IiBmaWxsPSIjOTk5Ij5Mb2dvPC90ZXh0Pjwvc3ZnPg=='
                    }}
                  />
                </div>
              )}
              {validationErrors.siteLogo && (
                <p className="text-sm text-destructive mt-2">{validationErrors.siteLogo}</p>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-2">
          <Label htmlFor="favicon">{t('settings.basic.favicon')}</Label>
          <div className="flex gap-2">
            <Input
              id="favicon"
              value={getSettingValue('favicon')}
              onChange={(e) => onUpdate('favicon', e.target.value)}
              placeholder={t('settings.basic.faviconPlaceholder')}
              disabled={loading}
              className={validationErrors.favicon ? 'border-destructive' : ''}
            />
            <Label htmlFor="favicon-upload" className="cursor-pointer">
              <Button
                variant="outline"
                size="icon"
                asChild
                disabled={loading}
              >
                <span>
                  <Upload className="w-4 h-4" />
                </span>
              </Button>
              <input
                id="favicon-upload"
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) handleFileUpload('favicon', file)
                }}
              />
            </Label>
          </div>
          {validationErrors.favicon && (
            <p className="text-sm text-destructive">{validationErrors.favicon}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="copyRight">{t('settings.basic.copyright')}</Label>
          <Input
            id="copyRight"
            value={getSettingValue('copyRight')}
            onChange={(e) => onUpdate('copyRight', e.target.value)}
            placeholder={t('settings.basic.copyrightPlaceholder')}
            disabled={loading}
            className={validationErrors.copyRight ? 'border-destructive' : ''}
          />
          {validationErrors.copyRight && (
            <p className="text-sm text-destructive">{validationErrors.copyRight}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="siteKeywords">{t('settings.basic.keywords')}</Label>
          <Input
            id="siteKeywords"
            value={getSettingValue('siteKeywords')}
            onChange={(e) => onUpdate('siteKeywords', e.target.value)}
            placeholder={t('settings.basic.keywordsPlaceholder')}
            disabled={loading}
            className={validationErrors.siteKeywords ? 'border-destructive' : ''}
          />
          {validationErrors.siteKeywords && (
            <p className="text-sm text-destructive">{validationErrors.siteKeywords}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="contactEmail">{t('settings.basic.contactEmail')}</Label>
          <Input
            id="contactEmail"
            type="email"
            value={getSettingValue('contactEmail')}
            onChange={(e) => onUpdate('contactEmail', e.target.value)}
            placeholder={t('settings.basic.contactEmailPlaceholder')}
            disabled={loading}
            className={validationErrors.contactEmail ? 'border-destructive' : ''}
          />
          {validationErrors.contactEmail && (
            <p className="text-sm text-destructive">{validationErrors.contactEmail}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="supportUrl">{t('settings.basic.supportUrl')}</Label>
          <Input
            id="supportUrl"
            type="url"
            value={getSettingValue('supportUrl')}
            onChange={(e) => onUpdate('supportUrl', e.target.value)}
            placeholder={t('settings.basic.supportUrlPlaceholder')}
            disabled={loading}
            className={validationErrors.supportUrl ? 'border-destructive' : ''}
          />
          {validationErrors.supportUrl && (
            <p className="text-sm text-destructive">{validationErrors.supportUrl}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="privacyPolicyUrl">{t('settings.basic.privacyPolicyUrl')}</Label>
          <Input
            id="privacyPolicyUrl"
            type="url"
            value={getSettingValue('privacyPolicyUrl')}
            onChange={(e) => onUpdate('privacyPolicyUrl', e.target.value)}
            placeholder={t('settings.basic.privacyPolicyUrlPlaceholder')}
            disabled={loading}
            className={validationErrors.privacyPolicyUrl ? 'border-destructive' : ''}
          />
          {validationErrors.privacyPolicyUrl && (
            <p className="text-sm text-destructive">{validationErrors.privacyPolicyUrl}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="termsOfServiceUrl">{t('settings.basic.termsOfServiceUrl')}</Label>
          <Input
            id="termsOfServiceUrl"
            type="url"
            value={getSettingValue('termsOfServiceUrl')}
            onChange={(e) => onUpdate('termsOfServiceUrl', e.target.value)}
            placeholder={t('settings.basic.termsOfServiceUrlPlaceholder')}
            disabled={loading}
            className={validationErrors.termsOfServiceUrl ? 'border-destructive' : ''}
          />
          {validationErrors.termsOfServiceUrl && (
            <p className="text-sm text-destructive">{validationErrors.termsOfServiceUrl}</p>
          )}
        </div>

        <div className="space-y-2 md:col-span-2">
          <Label htmlFor="analyticsCode">{t('settings.basic.analyticsCode')}</Label>
          <Textarea
            id="analyticsCode"
            rows={6}
            value={getSettingValue('analyticsCode')}
            onChange={(e) => onUpdate('analyticsCode', e.target.value)}
            placeholder={t('settings.basic.analyticsCodePlaceholder')}
            disabled={loading}
            className={validationErrors.analyticsCode ? 'border-destructive' : ''}
          />
          <p className="text-sm text-muted-foreground">
            {t('settings.basic.analyticsCodeHelp')}
          </p>
          {validationErrors.analyticsCode && (
            <p className="text-sm text-destructive">{validationErrors.analyticsCode}</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default BasicSettingsTab