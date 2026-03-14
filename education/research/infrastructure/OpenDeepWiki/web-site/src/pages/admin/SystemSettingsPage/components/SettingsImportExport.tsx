import React, { useState } from 'react'
import {
  Download,
  Upload,
  FileText,
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { systemSettingsService } from '@/services/admin.service'
import type {
  SystemSetting,
  SettingsExport,
  SettingGroupType
} from '@/types/systemSettings'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { useToast } from '@/hooks/useToast'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

interface SettingsImportExportProps {
  onClose: () => void
}

const SettingsImportExport: React.FC<SettingsImportExportProps> = ({
  onClose
}) => {
  const { t } = useTranslation('admin')
  const { toast } = useToast()
  const [activeTab, setActiveTab] = useState<'export' | 'import'>('export')
  const [exportLoading, setExportLoading] = useState(false)
  const [importLoading, setImportLoading] = useState(false)
  const [selectedGroups, setSelectedGroups] = useState<SettingGroupType[]>([])
  const [overwriteExisting, setOverwriteExisting] = useState(false)
  const [importFile, setImportFile] = useState<File | null>(null)
  const [importPreview, setImportPreview] = useState<SystemSetting[]>([])
  const [importProgress, setImportProgress] = useState(0)

  // 设置分组选项
  const settingGroups: { value: SettingGroupType; label: string }[] = [
    { value: 'Basic', label: t('settings.groups.basic') },
    { value: 'Email', label: t('settings.groups.email') },
    { value: 'OpenAI', label: t('settings.groups.ai') },
    { value: 'Storage', label: t('settings.groups.storage') },
    { value: 'Security', label: t('settings.groups.security') },
    { value: 'GitHub', label: t('settings.groups.github') },
    { value: 'Gitee', label: t('settings.groups.gitee') },
    { value: 'Document', label: t('settings.groups.document') },
    { value: 'JWT', label: t('settings.groups.jwt') },
    { value: 'Backup', label: t('settings.groups.backup') },
    { value: 'Logging', label: t('settings.groups.logging') }
  ]

  // 导出设置
  const handleExport = async () => {
    try {
      setExportLoading(true)

      const settings = await systemSettingsService.exportSettings()

      // 过滤选中的分组
      const filteredSettings = selectedGroups.length > 0
        ? settings.filter(setting => selectedGroups.includes(setting.group as SettingGroupType))
        : settings

      const exportData: SettingsExport = {
        version: '1.0',
        exportDate: new Date().toISOString(),
        settings: filteredSettings,
        groups: selectedGroups.length > 0 ? selectedGroups : [...new Set(settings.map(s => s.group))]
      }

      // 创建下载链接
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `koala-wiki-settings-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)

      toast({
        title: t('settings.importExport.exportSuccess'),
      })
    } catch (error) {
      console.error('Export failed:', error)
      toast({
        title: t('settings.importExport.exportFailed'),
        variant: 'destructive',
      })
    } finally {
      setExportLoading(false)
    }
  }

  // 处理文件上传
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setImportFile(file)

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target?.result as string) as SettingsExport

        if (!data.settings || !Array.isArray(data.settings)) {
          throw new Error('Invalid file format')
        }

        setImportPreview(data.settings)
        toast({
          title: t('settings.importExport.fileLoaded', { count: data.settings.length }),
        })
      } catch (error) {
        console.error('File parsing failed:', error)
        toast({
          title: t('settings.importExport.invalidFile'),
          variant: 'destructive',
        })
        setImportFile(null)
        setImportPreview([])
      }
    }
    reader.readAsText(file)
  }

  // 导入设置
  const handleImport = async () => {
    if (!importFile) {
      toast({
        title: t('settings.importExport.selectFileFirst'),
        variant: 'destructive',
      })
      return
    }

    try {
      setImportLoading(true)
      setImportProgress(0)

      // 模拟进度更新
      const progressInterval = setInterval(() => {
        setImportProgress(prev => Math.min(prev + 10, 90))
      }, 200)

      await systemSettingsService.exportSettings()

      clearInterval(progressInterval)
      setImportProgress(100)

      toast({
        title: t('settings.importExport.importSuccess'),
      })

      // 延迟关闭弹窗，让用户看到成功状态
      setTimeout(() => {
        onClose()
      }, 1500)
    } catch (error) {
      console.error('Import failed:', error)
      toast({
        title: t('settings.importExport.importFailed'),
        variant: 'destructive',
      })
      setImportProgress(0)
    } finally {
      setImportLoading(false)
    }
  }


  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex gap-4">
        <Button
          variant={activeTab === 'export' ? 'default' : 'outline'}
          onClick={() => setActiveTab('export')}
          className="flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          {t('settings.importExport.export')}
        </Button>
        <Button
          variant={activeTab === 'import' ? 'default' : 'outline'}
          onClick={() => setActiveTab('import')}
          className="flex items-center gap-2"
        >
          <Upload className="w-4 h-4" />
          {t('settings.importExport.import')}
        </Button>
      </div>

      {activeTab === 'export' && (
        <div className="space-y-6">
          <Alert>
            <Info className="h-4 w-4" />
            <AlertTitle>{t('settings.importExport.exportNote')}</AlertTitle>
            <AlertDescription>
              {t('settings.importExport.exportNoteDescription')}
            </AlertDescription>
          </Alert>

          <Card>
            <CardHeader>
              <CardTitle>{t('settings.importExport.exportSettings')}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>{t('settings.importExport.selectGroups')}</Label>
                <p className="text-sm text-muted-foreground">
                  {t('settings.importExport.selectGroupsDescription')}
                </p>
                <Select
                  value={selectedGroups.length > 0 ? selectedGroups[0] : ''}
                  onValueChange={(value) => {
                    if (value && !selectedGroups.includes(value as SettingGroupType)) {
                      setSelectedGroups([...selectedGroups, value as SettingGroupType])
                    }
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={t('settings.importExport.selectGroupsPlaceholder')} />
                  </SelectTrigger>
                  <SelectContent>
                    {settingGroups
                      .filter(group => !selectedGroups.includes(group.value))
                      .map(group => (
                        <SelectItem key={group.value} value={group.value}>
                          {group.label}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
                <div className="flex flex-wrap gap-1">
                  {selectedGroups.map(group => (
                    <Badge
                      key={group}
                      variant="secondary"
                      className="cursor-pointer"
                      onClick={() => setSelectedGroups(selectedGroups.filter(g => g !== group))}
                    >
                      {settingGroups.find(g => g.value === group)?.label} ×
                    </Badge>
                  ))}
                </div>
              </div>
              <Button
                onClick={handleExport}
                disabled={exportLoading}
                className="w-full"
              >
                {exportLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    {t('common.loading')}
                  </div>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    {t('settings.importExport.downloadSettings')}
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'import' && (
        <div className="space-y-6">
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>{t('settings.importExport.importNote')}</AlertTitle>
            <AlertDescription>
              {t('settings.importExport.importNoteDescription')}
            </AlertDescription>
          </Alert>

          <Card>
            <CardHeader>
              <CardTitle>{t('settings.importExport.uploadFile')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
                <FileText className="w-12 h-12 mx-auto mb-4 text-blue-500" />
                <div className="text-lg font-medium mb-2">
                  {importFile ? importFile.name : t('settings.importExport.dragFileHere')}
                </div>
                <div className="text-sm text-muted-foreground mb-4">
                  {t('settings.importExport.supportedFormats')}
                </div>
                <input
                  type="file"
                  accept=".json"
                  onChange={handleFileUpload}
                  disabled={importLoading}
                  className="block w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
                />
              </div>
            </CardContent>
          </Card>

          {importPreview.length > 0 && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>{t('settings.importExport.importOptions')}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label>{t('settings.importExport.selectImportGroups')}</Label>
                      <p className="text-sm text-muted-foreground">
                        {t('settings.importExport.selectImportGroupsDescription')}
                      </p>
                      <Select
                        value={selectedGroups.length > 0 ? selectedGroups[0] : ''}
                        onValueChange={(value) => {
                          if (value && !selectedGroups.includes(value as SettingGroupType)) {
                            setSelectedGroups([...selectedGroups, value as SettingGroupType])
                          }
                        }}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder={t('settings.importExport.selectGroupsPlaceholder')} />
                        </SelectTrigger>
                        <SelectContent>
                          {[...new Set(importPreview.map(s => s.group))]
                            .filter(group => !selectedGroups.includes(group as SettingGroupType))
                            .map(group => (
                              <SelectItem key={group} value={group}>
                                {settingGroups.find(g => g.value === group)?.label || group}
                              </SelectItem>
                            ))}
                        </SelectContent>
                      </Select>
                      <div className="flex flex-wrap gap-1">
                        {selectedGroups.map(group => (
                          <Badge
                            key={group}
                            variant="secondary"
                            className="cursor-pointer"
                            onClick={() => setSelectedGroups(selectedGroups.filter(g => g !== group))}
                          >
                            {settingGroups.find(g => g.value === group)?.label} ×
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label>{t('settings.importExport.overwriteExisting')}</Label>
                      <p className="text-sm text-muted-foreground">
                        {t('settings.importExport.overwriteExistingDescription')}
                      </p>
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="overwrite"
                          checked={overwriteExisting}
                          onCheckedChange={setOverwriteExisting}
                        />
                        <Label htmlFor="overwrite">
                          {overwriteExisting ? t('common.yes') : t('common.no')}
                        </Label>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>
                    {t('settings.importExport.previewSettings', { count: importPreview.length })}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="max-h-80 overflow-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-48">{t('settings.importExport.key')}</TableHead>
                          <TableHead className="w-32">{t('settings.importExport.group')}</TableHead>
                          <TableHead>{t('settings.importExport.description')}</TableHead>
                          <TableHead className="w-24">{t('settings.importExport.sensitive')}</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {importPreview.slice(0, 20).map((setting) => (
                          <TableRow key={setting.key}>
                            <TableCell className="font-mono text-sm">{setting.key}</TableCell>
                            <TableCell>
                              <Badge variant="outline">
                                {settingGroups.find(g => g.value === setting.group)?.label || setting.group}
                              </Badge>
                            </TableCell>
                            <TableCell className="truncate max-w-64">{setting.description}</TableCell>
                            <TableCell>
                              {setting.isSensitive ? (
                                <Badge variant="destructive" className="text-xs">
                                  <AlertTriangle className="w-3 h-3 mr-1" />
                                  {t('common.yes')}
                                </Badge>
                              ) : (
                                <Badge variant="secondary" className="text-xs">
                                  <CheckCircle className="w-3 h-3 mr-1" />
                                  {t('common.no')}
                                </Badge>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                    {importPreview.length > 20 && (
                      <div className="text-center text-sm text-muted-foreground mt-4">
                        {t('settings.importExport.showingFirst20', { total: importPreview.length })}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {importLoading && (
                <Card>
                  <CardContent className="py-8 text-center">
                    <div className="w-24 h-24 mx-auto mb-4">
                      <Progress value={importProgress} className="w-full" />
                      <div className="text-2xl font-bold mt-2">{importProgress}%</div>
                    </div>
                    <div className="font-medium">
                      {importProgress === 100
                        ? t('settings.importExport.importComplete')
                        : t('settings.importExport.importInProgress')
                      }
                    </div>
                  </CardContent>
                </Card>
              )}

              <Button
                onClick={handleImport}
                disabled={importLoading || importProgress === 100}
                className="w-full"
              >
                {importLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    {t('settings.importExport.importInProgress')}
                  </div>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    {t('settings.importExport.importSettings')}
                  </>
                )}
              </Button>
            </>
          )}
        </div>
      )}

      <Separator />

      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>{t('settings.importExport.securityWarning')}</AlertTitle>
        <AlertDescription>
          <ul className="list-disc list-inside space-y-1 text-sm">
            <li>{t('settings.importExport.securityTip1')}</li>
            <li>{t('settings.importExport.securityTip2')}</li>
            <li>{t('settings.importExport.securityTip3')}</li>
            <li>{t('settings.importExport.securityTip4')}</li>
          </ul>
        </AlertDescription>
      </Alert>
    </div>
  )
}

export default SettingsImportExport