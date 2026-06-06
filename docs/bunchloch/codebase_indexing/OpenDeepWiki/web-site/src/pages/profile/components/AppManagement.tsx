// 应用管理组件
import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
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
import { toast as sonnerToast } from 'sonner'
import { Badge } from '@/components/ui/badge'
import {
  Plus,
  Edit,
  Trash2,
  Copy,
  Settings,
  Globe,
  Key,
  Loader2
} from 'lucide-react'
import { appConfigService } from '@/services/appConfigService'
import type { AppConfigOutput, AppConfigInput } from '@/types'

export const AppManagement: React.FC = () => {
  const { t } = useTranslation()

  const toast = (opts: { title: string; description?: string; variant?: 'destructive' | string }) => {
    if (opts.variant === 'destructive') {
      sonnerToast.error(opts.title, { description: opts.description })
    } else {
      sonnerToast.success(opts.title, { description: opts.description })
    }
  }

  const [apps, setApps] = useState<AppConfigOutput[]>([])
  const [loading, setLoading] = useState(false)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [selectedApp, setSelectedApp] = useState<AppConfigOutput | null>(null)
  const [formData, setFormData] = useState<AppConfigInput>({
    appId: '',
    name: '',
    organizationName: '',
    repositoryName: '',
    description: '',
    allowedDomains: [],
    enableDomainValidation: false,
    prompt: '',
    introduction: '',
    model: 'gpt-3.5-turbo',
    recommendedQuestions: [],
    mcps: []
  })
  const [newDomain, setNewDomain] = useState('')
  const [newQuestion, setNewQuestion] = useState('')

  // 加载应用列表
  const loadApps = async () => {
    setLoading(true)
    try {
      const {data} = await appConfigService.getAppConfigs()
      setApps(data)
    } catch (error: any) {
      toast({
        title: t('profile.apps.loadFailed'),
        description: error.message || t('profile.apps.loadFailedDesc'),
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadApps()
  }, [])

  // 生成应用ID
  const generateAppId = () => {
    const id = `app_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    setFormData(prev => ({ ...prev, appId: id }))
  }

  // 处理表单输入
  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  // 添加域名
  const addDomain = () => {
    if (newDomain && !formData.allowedDomains.includes(newDomain)) {
      setFormData(prev => ({
        ...prev,
        allowedDomains: [...prev.allowedDomains, newDomain]
      }))
      setNewDomain('')
    }
  }

  // 移除域名
  const removeDomain = (domain: string) => {
    setFormData(prev => ({
      ...prev,
      allowedDomains: prev.allowedDomains.filter(d => d !== domain)
    }))
  }

  // 添加推荐问题
  const addQuestion = () => {
    if (newQuestion && !formData.recommendedQuestions?.includes(newQuestion)) {
      setFormData(prev => ({
        ...prev,
        recommendedQuestions: [...(prev.recommendedQuestions || []), newQuestion]
      }))
      setNewQuestion('')
    }
  }

  // 移除推荐问题
  const removeQuestion = (question: string) => {
    setFormData(prev => ({
      ...prev,
      recommendedQuestions: prev.recommendedQuestions?.filter(q => q !== question) || []
    }))
  }

  // 打开创建/编辑对话框
  const openDialog = (app?: AppConfigOutput) => {
    if (app) {
      setSelectedApp(app)
      setFormData({
        appId: app.appId,
        name: app.name,
        organizationName: app.organizationName,
        repositoryName: app.repositoryName,
        description: app.description || '',
        allowedDomains: app.allowedDomains || [],
        enableDomainValidation: app.enableDomainValidation || false,
        prompt: app.prompt || '',
        introduction: app.introduction || '',
        model: app.model || 'gpt-3.5-turbo',
        recommendedQuestions: app.recommendedQuestions || [],
        mcps: app.mcps || []
      })
    } else {
      setSelectedApp(null)
      setFormData({
        appId: '',
        name: '',
        organizationName: '',
        repositoryName: '',
        description: '',
        allowedDomains: [],
        enableDomainValidation: false,
        prompt: '',
        introduction: '',
        model: 'gpt-3.5-turbo',
        recommendedQuestions: [],
        mcps: []
      })
      generateAppId()
    }
    setDialogOpen(true)
  }

  // 保存应用
  const handleSave = async () => {
    try {
      if (selectedApp) {
        await appConfigService.updateAppConfig(selectedApp.appId, formData)
        toast({
          title: t('profile.apps.updateSuccess'),
          description: '',
        })
      } else {
        await appConfigService.createAppConfig(formData)
        toast({
          title: t('profile.apps.createSuccess'),
          description: '',
        })
      }
      setDialogOpen(false)
      loadApps()
    } catch (error: any) {
      toast({
        title: t('profile.apps.operationFailed'),
        description: error.message || '',
        variant: 'destructive',
      })
    }
  }

  // 删除应用
  const handleDelete = async () => {
    if (!selectedApp) return

    try {
      await appConfigService.deleteAppConfig(selectedApp.appId)
      toast({
        title: t('profile.apps.deleteSuccess'),
        description: '',
      })
      setDeleteDialogOpen(false)
      loadApps()
    } catch (error: any) {
      toast({
        title: t('profile.apps.deleteFailed'),
        description: error.message || '',
        variant: 'destructive',
      })
    }
  }

  // 切换应用启用状态
  const toggleAppStatus = async (appId: string) => {
    try {
      await appConfigService.toggleAppConfig(appId)
      loadApps()
      toast({
        title: t('profile.apps.toggleStatusSuccess'),
        description: '',
      })
    } catch (error: any) {
      toast({
        title: t('profile.apps.toggleStatusFailed'),
        description: error.message || '',
        variant: 'destructive',
      })
    }
  }

  // 复制应用ID
  const copyAppId = (appId: string) => {
    navigator.clipboard.writeText(appId)
    toast({
      title: t('profile.apps.copySuccess'),
      description: '',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 头部 */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">{t('profile.apps.title')}</h3>
          <p className="text-sm text-muted-foreground">
            {t('profile.apps.description')}
          </p>
        </div>
        <Button onClick={() => openDialog()}>
          <Plus className="h-4 w-4 mr-2" />
          {t('profile.apps.createApp')}
        </Button>
      </div>

      {/* 应用列表 */}
      {apps.length === 0 ? (
        <Card className="p-12 text-center">
          <div className="flex flex-col items-center space-y-4">
            <Settings className="h-12 w-12 text-muted-foreground" />
            <div>
              <h3 className="text-lg font-semibold">{t('profile.apps.noApps')}</h3>
              <p className="text-sm text-muted-foreground mt-1">
                {t('profile.apps.noAppsDesc')}
              </p>
            </div>
          </div>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {apps.map((app) => (
            <Card key={app.appId} className="relative">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <CardTitle className="text-base">{app.name}</CardTitle>
                    <CardDescription className="text-xs">
                      {app.organizationName}/{app.repositoryName}
                    </CardDescription>
                  </div>
                  <Badge variant={app.isEnabled ? 'default' : 'secondary'}>
                    {app.isEnabled ? t('profile.apps.enabled') : t('profile.apps.disabled')}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center space-x-2 text-sm">
                  <Key className="h-4 w-4 text-muted-foreground" />
                  <code className="flex-1 text-xs bg-muted px-2 py-1 rounded">
                    {app.appId}
                  </code>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => copyAppId(app.appId)}
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>

                {app.enableDomainValidation && (
                  <div className="flex items-center space-x-2 text-sm">
                    <Globe className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">
                      {t('profile.apps.allowedDomainsCount', { count: app.allowedDomains.length })}
                    </span>
                  </div>
                )}

                {app.description && (
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {app.description}
                  </p>
                )}

                {app.lastUsedAt && (
                  <p className="text-xs text-muted-foreground">
                    {t('profile.apps.lastUsed')}: {new Date(app.lastUsedAt).toLocaleDateString('zh-CN')}
                  </p>
                )}
              </CardContent>
              <CardFooter className="flex justify-between">
                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => openDialog(app)}
                  >
                    <Edit className="h-3 w-3 mr-1" />
                    {t('profile.apps.edit')}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setSelectedApp(app)
                      setDeleteDialogOpen(true)
                    }}
                  >
                    <Trash2 className="h-3 w-3 mr-1" />
                    {t('profile.apps.delete')}
                  </Button>
                </div>
                <Switch
                  checked={app.isEnabled}
                  onCheckedChange={() => toggleAppStatus(app.appId)}
                />
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {/* 创建/编辑对话框 */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {selectedApp ? t('profile.apps.createApplicationDialog.editTitle') : t('profile.apps.createApplicationDialog.title')}
            </DialogTitle>
            <DialogDescription>
              {selectedApp ? t('profile.apps.createApplicationDialog.editTitle') : ''}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* 基础信息 */}
            <div className="space-y-2">
              <Label htmlFor="appId">{t('profile.apps.appId')}</Label>
              <div className="flex space-x-2">
                <Input
                  id="appId"
                  value={formData.appId}
                  onChange={(e) => handleInputChange('appId', e.target.value)}
                  disabled={!!selectedApp}
                  placeholder={t('profile.apps.appId')}
                />
                {!selectedApp && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={generateAppId}
                  >
                    {t('profile.apps.generateId')}
                  </Button>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="name">{t('profile.apps.appName')}</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder={t('profile.apps.appName')}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="organization">{t('profile.apps.organization')}</Label>
                <Input
                  id="organization"
                  value={formData.organizationName}
                  onChange={(e) => handleInputChange('organizationName', e.target.value)}
                  placeholder={t('profile.apps.organization')}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="repository">{t('profile.apps.repository')}</Label>
                <Input
                  id="repository"
                  value={formData.repositoryName}
                  onChange={(e) => handleInputChange('repositoryName', e.target.value)}
                  placeholder={t('profile.apps.repository')}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">{t('profile.apps.description')}</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder={t('profile.apps.descriptionPlaceholder')}
                rows={3}
              />
            </div>

            {/* AI配置 */}
            <div className="space-y-2">
              <Label htmlFor="model">{t('profile.apps.model')}</Label>
              <Select
                value={formData.model}
                onValueChange={(value) => handleInputChange('model', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder={t('profile.apps.selectModel')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                  <SelectItem value="gpt-4">GPT-4</SelectItem>
                  <SelectItem value="gpt-4-turbo">GPT-4 Turbo</SelectItem>
                  <SelectItem value="claude-3">Claude 3</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="prompt">{t('profile.apps.prompt')}</Label>
              <Textarea
                id="prompt"
                value={formData.prompt}
                onChange={(e) => handleInputChange('prompt', e.target.value)}
                placeholder={t('profile.apps.promptPlaceholder')}
                rows={4}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="introduction">{t('profile.apps.introduction')}</Label>
              <Textarea
                id="introduction"
                value={formData.introduction}
                onChange={(e) => handleInputChange('introduction', e.target.value)}
                placeholder={t('profile.apps.introductionPlaceholder')}
                rows={3}
              />
            </div>

            {/* 推荐问题 */}
            <div className="space-y-2">
              <Label>{t('profile.apps.recommendedQuestions')}</Label>
              <div className="flex space-x-2">
                <Input
                  value={newQuestion}
                  onChange={(e) => setNewQuestion(e.target.value)}
                  placeholder={t('profile.apps.addQuestionPlaceholder')}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addQuestion())}
                />
                <Button type="button" variant="outline" onClick={addQuestion}>
                  {t('common.add')}
                </Button>
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                {formData.recommendedQuestions?.map((question, index) => (
                  <Badge key={index} variant="secondary">
                    {question}
                    <button
                      className="ml-2 text-xs"
                      onClick={() => removeQuestion(question)}
                    >
                      ×
                    </button>
                  </Badge>
                ))}
              </div>
            </div>

            {/* 域名验证 */}
            <div className="space-y-4 p-4 border rounded-lg">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>{t('profile.apps.domainValidation')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('profile.apps.domainValidationDesc')}
                  </p>
                </div>
                <Switch
                  checked={formData.enableDomainValidation}
                  onCheckedChange={(checked) => handleInputChange('enableDomainValidation', checked)}
                />
              </div>

              {formData.enableDomainValidation && (
                <div className="space-y-2">
                  <div className="flex space-x-2">
                    <Input
                      value={newDomain}
                      onChange={(e) => setNewDomain(e.target.value)}
                      placeholder={t('profile.apps.domainPlaceholder')}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addDomain())}
                    />
                    <Button type="button" variant="outline" onClick={addDomain}>
                      {t('profile.apps.addDomain')}
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {formData.allowedDomains.map((domain, index) => (
                      <Badge key={index} variant="secondary">
                        {domain}
                        <button
                          className="ml-2 text-xs"
                          onClick={() => removeDomain(domain)}
                        >
                          ×
                        </button>
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button onClick={handleSave}>
              {selectedApp ? t('common.save') : t('profile.apps.createApp')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 删除确认对话框 */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{t('profile.apps.deleteDialog.title')}</AlertDialogTitle>
            <AlertDialogDescription>
              {t('profile.apps.deleteDialog.desc', { name: selectedApp?.name || '' })}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t('common.cancel')}</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete}>
              {t('common.confirm')}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

export default AppManagement
