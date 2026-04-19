import React, { useState, useEffect, useCallback } from 'react'
import {
  Settings,
  Save,
  RefreshCw,
  Import,
  AlertTriangle
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { systemSettingsService } from '@/services/admin.service'
import type {
  SystemSettingGroup,
  SystemSetting,
  SettingGroupType,
  ValidationErrors
} from '@/types/systemSettings'

import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/useToast'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

import BasicSettingsTab from './components/BasicSettingsTab'
import EmailSettingsTab from './components/EmailSettingsTab'
import AISettingsTab from './components/AISettingsTab'
import StorageSettingsTab from './components/StorageSettingsTab'
import SecuritySettingsTab from './components/SecuritySettingsTab'
import ThirdPartySettingsTab from './components/ThirdPartySettingsTab'
import DocumentSettingsTab from './components/DocumentSettingsTab'
import SettingsImportExport from './components/SettingsImportExport'

interface SystemSettingsPageProps {}

const SystemSettingsPage: React.FC<SystemSettingsPageProps> = () => {
  const { t } = useTranslation('admin')
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [activeTab, setActiveTab] = useState<string>('basic')
  const [settingGroups, setSettingGroups] = useState<SystemSettingGroup[]>([])
  const [settings, setSettings] = useState<Record<string, SystemSetting[]>>({})
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({})
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [restartRequired, setRestartRequired] = useState<string[]>([])
  const [importExportVisible, setImportExportVisible] = useState(false)
  const [resetDialogOpen, setResetDialogOpen] = useState(false)
  const [restartDialogOpen, setRestartDialogOpen] = useState(false)

  const loadSettingGroups = useCallback(async () => {
    try {
      setLoading(true)
      const response = await systemSettingsService.getSettingGroups()

      // 确保 response 是数组
      const groups = Array.isArray(response) ? response : []
      setSettingGroups(groups)
      setActiveTab(groups[0]?.group || '')

      const settingsMap: Record<string, SystemSetting[]> = {}
      groups.forEach(group => {
        if (group && group.group && Array.isArray(group.settings)) {
          settingsMap[group.group] = group.settings
        }
      })
      setSettings(settingsMap)
    } catch (error) {
      console.error('Failed to load setting groups:', error)
      toast({
        title: t('settings.loadFailed'),
        variant: 'destructive',
      })
      // 设置默认空数组以防止错误
      setSettingGroups([])
      setSettings({})
    } finally {
      setLoading(false)
    }
  }, [t, toast])

  const loadRestartRequired = useCallback(async () => {
    try {
      const response = await systemSettingsService.getRestartRequiredSettings()
      // 确保 response 是数组
      setRestartRequired(Array.isArray(response) ? response : [])
    } catch (error) {
      console.error('Failed to load restart required settings:', error)
      setRestartRequired([])
    }
  }, [])

  useEffect(() => {
    loadSettingGroups()
    loadRestartRequired()
  }, [loadSettingGroups, loadRestartRequired])

  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault()
        e.returnValue = ''
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [hasUnsavedChanges])

  const updateSetting = useCallback((group: string, key: string, value: any) => {
    setSettings(prev => {
      const newSettings = { ...prev }
      if (newSettings[group]) {
        newSettings[group] = newSettings[group].map(setting =>
          setting.key === key ? { ...setting, value: String(value) } : setting
        )
      }
      return newSettings
    })
    setHasUnsavedChanges(true)

    if (validationErrors[key]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[key]
        return newErrors
      })
    }
  }, [validationErrors])

  const saveAllSettings = useCallback(async () => {
    try {
      setSaving(true)

      const updateItems = Object.values(settings)
        .flat()
        .map(setting => ({
          key: setting.key,
          value: setting.value
        }))


      await systemSettingsService.batchUpdateSettings({ settings: updateItems })

      toast({
        title: t('settings.saveSuccess'),
      })
      setHasUnsavedChanges(false)
      setValidationErrors({})

      await loadRestartRequired()

      if (restartRequired.length > 0) {
        setRestartDialogOpen(true)
      }
    } catch (error) {
      console.error('Failed to save settings:', error)
      toast({
        title: t('settings.saveFailed'),
        variant: 'destructive',
      })
    } finally {
      setSaving(false)
    }
  }, [settings, t, toast, loadRestartRequired, restartRequired.length])

  const resetCurrentGroup = useCallback(async () => {
    const currentGroupSettings = settings[activeTab]
    if (!currentGroupSettings) return

    setResetDialogOpen(false)

    try {
      setLoading(true)

      for (const setting of currentGroupSettings) {
        await systemSettingsService.resetSetting(setting.key)
      }

      toast({
        title: t('settings.resetSuccess'),
      })
      await loadSettingGroups()
      setHasUnsavedChanges(false)
    } catch (error) {
      console.error('Failed to reset settings:', error)
      toast({
        title: t('settings.resetFailed'),
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }, [activeTab, settings, t, toast, loadSettingGroups])

  const clearCache = useCallback(async () => {
    try {
      await systemSettingsService.clearCache()
      toast({
        title: t('settings.cacheCleared'),
      })
    } catch (error) {
      console.error('Failed to clear cache:', error)
      toast({
        title: t('settings.cacheClearFailed'),
        variant: 'destructive',
      })
    }
  }, [t, toast])

  const handleRestart = async () => {
    try {
      await systemSettingsService.restartSystem()
      toast({
        title: t('settings.restartInitiated'),
      })
    } catch (error) {
      toast({
        title: t('settings.restartFailed'),
        variant: 'destructive',
      })
    }
    setRestartDialogOpen(false)
  }

  const renderTabContent = (group: SettingGroupType) => {
    const groupSettings = settings[group] || []
    const commonProps = {
      settings: groupSettings,
      onUpdate: (key: string, value: any) => updateSetting(group, key, value),
      validationErrors,
      loading: loading || saving
    }

    switch (group) {
      case 'Basic':
        return <BasicSettingsTab {...commonProps} />
      case 'Email':
        return <EmailSettingsTab {...commonProps} />
      case 'OpenAI':
        return <AISettingsTab {...commonProps} />
      case 'Storage':
        return <StorageSettingsTab {...commonProps} />
      case 'Security':
        return <SecuritySettingsTab {...commonProps} />
      case 'GitHub':
      case 'Gitee':
        return <ThirdPartySettingsTab {...commonProps} group={group} />
      case 'Document':
        return <DocumentSettingsTab {...commonProps} />
      default:
        return <div>Coming soon...</div>
    }
  }

  const getTabInfo = (group: SettingGroupType) => {
    const baseInfo = {
      Basic: { title: t('settings.groups.basic'), icon: <Settings className="w-4 h-4" /> },
      Email: { title: t('settings.groups.email'), icon: <Settings className="w-4 h-4" /> },
      OpenAI: { title: t('settings.groups.ai'), icon: <Settings className="w-4 h-4" /> },
      Storage: { title: t('settings.groups.storage'), icon: <Settings className="w-4 h-4" /> },
      Security: { title: t('settings.groups.security'), icon: <Settings className="w-4 h-4" /> },
      GitHub: { title: t('settings.groups.github'), icon: <Settings className="w-4 h-4" /> },
      Gitee: { title: t('settings.groups.gitee'), icon: <Settings className="w-4 h-4" /> },
      Document: { title: t('settings.groups.document'), icon: <Settings className="w-4 h-4" /> },
      JWT: { title: t('settings.groups.jwt'), icon: <Settings className="w-4 h-4" /> },
      Backup: { title: t('settings.groups.backup'), icon: <Settings className="w-4 h-4" /> },
      Logging: { title: t('settings.groups.logging'), icon: <Settings className="w-4 h-4" /> }
    }[group] || { title: group, icon: <Settings className="w-4 h-4" /> }

    const groupSettings = settings[group] || []
    const hasRestartRequired = groupSettings.some(setting =>
      setting.requiresRestart && restartRequired.includes(setting.key)
    )

    return {
      ...baseInfo,
      badge: hasRestartRequired
    }
  }

  return (
    <div className="p-6">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Settings className="w-8 h-8" />
            {t('settings.title')}
          </h2>
          <p className="text-muted-foreground mt-2">
            {t('settings.description')}
          </p>
        </div>

        <div className="flex items-center gap-4">
          {hasUnsavedChanges && (
            <Alert className="w-auto py-2 px-4">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{t('settings.unsavedChanges')}</AlertDescription>
            </Alert>
          )}

          <Button
            variant="outline"
            onClick={clearCache}
            disabled={loading}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            {t('settings.clearCache')}
          </Button>

          <Button
            variant="outline"
            onClick={() => setImportExportVisible(true)}
          >
            <Import className="w-4 h-4 mr-2" />
            {t('settings.importExport.title')}
          </Button>

          <Button
            variant="outline"
            onClick={() => setResetDialogOpen(true)}
            disabled={loading}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            {t('settings.resetGroup')}
          </Button>

          <Button
            onClick={saveAllSettings}
            disabled={!hasUnsavedChanges || loading}
          >
            <Save className="w-4 h-4 mr-2" />
            {t('settings.saveAll')}
          </Button>
        </div>
      </div>

      {restartRequired.length > 0 && (
        <Alert className="mb-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>{t('settings.restartRequired')}</AlertTitle>
          <AlertDescription className="flex items-center justify-between">
            <span>{t('settings.restartRequiredMessage')}</span>
            <Button
              size="sm"
              variant="destructive"
              onClick={() => setRestartDialogOpen(true)}
              className="ml-4"
            >
              {t('common.restart')}
            </Button>
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardContent className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              {settingGroups.length > 0 ? (
                <>
                  <TabsList className="grid w-full grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 mb-6">
                    {settingGroups.map(group => {
                      const tabInfo = getTabInfo(group.group as SettingGroupType)
                      return (
                        <TabsTrigger
                          key={group.group}
                          value={group.group}
                          className="relative flex items-center gap-2"
                        >
                          {tabInfo.icon}
                          <span>{tabInfo.title}</span>
                          {tabInfo.badge && (
                            <Badge variant="destructive" className="ml-2 h-2 w-2 p-0 rounded-full" />
                          )}
                        </TabsTrigger>
                      )
                    })}
                  </TabsList>

                  {settingGroups.map(group => (
                    <TabsContent key={group.group} value={group.group}>
                      {renderTabContent(group.group as SettingGroupType)}
                    </TabsContent>
                  ))}
                </>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  {t('settings.noSettingsAvailable')}
                </div>
              )}
            </Tabs>
          )}
        </CardContent>
      </Card>

      <AlertDialog open={resetDialogOpen} onOpenChange={setResetDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{t('settings.resetGroup')}</AlertDialogTitle>
            <AlertDialogDescription>
              {t('settings.resetGroupConfirm')}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t('common.cancel')}</AlertDialogCancel>
            <AlertDialogAction onClick={resetCurrentGroup} className="bg-destructive text-destructive-foreground">
              {t('common.reset')}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={restartDialogOpen} onOpenChange={setRestartDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{t('settings.restartRequired')}</AlertDialogTitle>
            <AlertDialogDescription>
              {t('settings.restartRequiredMessage')}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t('common.later')}</AlertDialogCancel>
            <AlertDialogAction onClick={handleRestart} className="bg-destructive text-destructive-foreground">
              {t('common.restart')}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <Dialog open={importExportVisible} onOpenChange={setImportExportVisible}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{t('settings.importExport.title')}</DialogTitle>
          </DialogHeader>
          <SettingsImportExport onClose={() => setImportExportVisible(false)} />
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default SystemSettingsPage