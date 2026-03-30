import React, { useState } from 'react'
import {
  Bot,
  Zap,
  AlertTriangle,
  Info,
  HelpCircle
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { systemSettingsService } from '@/services/admin.service'
import type { SystemSetting, ValidationErrors, APITestParams } from '@/types/systemSettings'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Slider } from '@/components/ui/slider'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { useToast } from '@/hooks/useToast'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

interface AISettingsTabProps {
  settings: SystemSetting[]
  onUpdate: (key: string, value: any) => void
  validationErrors: ValidationErrors
  loading?: boolean
}

const AISettingsTab: React.FC<AISettingsTabProps> = ({
  settings,
  onUpdate,
  validationErrors,
  loading = false
}) => {
  const { t } = useTranslation('admin')
  const { toast } = useToast()
  const [testModalVisible, setTestModalVisible] = useState(false)
  const [testing, setTesting] = useState(false)

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
    return value ? parseFloat(value) : undefined
  }

  // 获取整数值设置
  const getIntValue = (key: string) => {
    const value = getSettingValue(key)
    return value ? parseInt(value, 10) : undefined
  }

  // 测试AI API连接
  const testAIConnection = async () => {
    const endpoint = getSettingValue('Endpoint')
    const apiKey = getSettingValue('ChatApiKey')
    const model = getSettingValue('ChatModel')

    if (!endpoint || !apiKey) {
      toast({
        title: t('settings.ai.testRequiredFields'),
        variant: 'destructive',
      })
      return
    }

    try {
      setTesting(true)

      const params: APITestParams = {
        endpoint,
        apiKey,
        model
      }

      const result = await systemSettingsService.testAISettings(params) as any

      if (result.success) {
        toast({
          title: t('settings.ai.testSuccess'),
        })
        setTestModalVisible(false)
      } else {
        toast({
          title: result.message || t('settings.ai.testFailed'),
          variant: 'destructive',
        })
      }
    } catch (error) {
      console.error('AI API test failed:', error)
      toast({
        title: t('settings.ai.testFailed'),
        variant: 'destructive',
      })
    } finally {
      setTesting(false)
    }
  }

  // 模型提供商选项
  const modelProviders = [
    { value: 'OpenAI', label: 'OpenAI' },
    { value: 'Azure', label: 'Azure OpenAI' },
    { value: 'Custom', label: t('settings.ai.customProvider') }
  ]


  return (
    <TooltipProvider>
      <div className="max-w-4xl space-y-6">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold">{t('settings.groups.ai')}</h3>
            <p className="text-sm text-muted-foreground mt-2">
              {t('settings.aiDescription')}
            </p>
          </div>
          <Button
            onClick={() => setTestModalVisible(true)}
            disabled={loading}
          >
            <Zap className="w-4 h-4 mr-2" />
            {t('settings.ai.testConnection')}
          </Button>
        </div>

        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>{t('settings.ai.apiKeyNote')}</AlertTitle>
          <AlertDescription>
            {t('settings.ai.apiKeyNoteDescription')}
          </AlertDescription>
        </Alert>

        <div className="grid gap-6 md:grid-cols-2">
          {/* 模型提供商 */}
          <div className="space-y-2">
            <Label htmlFor="modelProvider">{t('settings.ai.modelProvider')} *</Label>
            <Select
              value={getSettingValue('ModelProvider')}
              onValueChange={(value) => onUpdate('ModelProvider', value)}
              disabled={loading}
            >
              <SelectTrigger className={validationErrors.ModelProvider ? 'border-destructive' : ''}>
                <SelectValue placeholder={t('settings.ai.modelProviderPlaceholder')} />
              </SelectTrigger>
              <SelectContent>
                {modelProviders.map(provider => (
                  <SelectItem key={provider.value} value={provider.value}>
                    {provider.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {validationErrors.ModelProvider && (
              <p className="text-sm text-destructive">{validationErrors.ModelProvider}</p>
            )}
          </div>

          {/* API端点 */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Label htmlFor="endpoint">{t('settings.ai.endpoint')} *</Label>
              <Tooltip>
                <TooltipTrigger>
                  <HelpCircle className="w-4 h-4 text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>{t('settings.ai.endpointHelp')}</p>
                </TooltipContent>
              </Tooltip>
            </div>
            <Input
              id="endpoint"
              value={getSettingValue('Endpoint')}
              onChange={(e) => onUpdate('Endpoint', e.target.value)}
              placeholder={t('settings.ai.endpointPlaceholder')}
              disabled={loading}
              className={validationErrors.Endpoint ? 'border-destructive' : ''}
            />
            {validationErrors.Endpoint && (
              <p className="text-sm text-destructive">{validationErrors.Endpoint}</p>
            )}
          </div>

          {/* API密钥 */}
          <div className="md:col-span-2 space-y-2">
            <Label htmlFor="apiKey">{t('settings.ai.apiKey')} *</Label>
            <Input
              id="apiKey"
              type="password"
              value={getSettingValue('ChatApiKey')}
              onChange={(e) => onUpdate('ChatApiKey', e.target.value)}
              placeholder={t('settings.ai.apiKeyPlaceholder')}
              disabled={loading}
              className={validationErrors.ChatApiKey ? 'border-destructive' : ''}
            />
            {validationErrors.ChatApiKey && (
              <p className="text-sm text-destructive">{validationErrors.ChatApiKey}</p>
            )}
          </div>

          {/* 模型配置 */}
          <div className="md:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">{t('settings.ai.modelConfiguration')}</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="chatModel">{t('settings.ai.chatModel')}</Label>
                  <Input
                    id="chatModel"
                    value={getSettingValue('ChatModel')}
                    onChange={(e) => onUpdate('ChatModel', e.target.value)}
                    placeholder={t('settings.ai.chatModelPlaceholder')}
                    disabled={loading}
                    className={validationErrors.ChatModel ? 'border-destructive' : ''}
                  />
                  {validationErrors.ChatModel && (
                    <p className="text-sm text-destructive">{validationErrors.ChatModel}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="analysisModel">{t('settings.ai.analysisModel')}</Label>
                  <Input
                    id="analysisModel"
                    value={getSettingValue('AnalysisModel')}
                    onChange={(e) => onUpdate('AnalysisModel', e.target.value)}
                    placeholder={t('settings.ai.analysisModelPlaceholder')}
                    disabled={loading}
                    className={validationErrors.AnalysisModel ? 'border-destructive' : ''}
                  />
                  {validationErrors.AnalysisModel && (
                    <p className="text-sm text-destructive">{validationErrors.AnalysisModel}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="deepResearchModel">{t('settings.ai.deepResearchModel')}</Label>
                  <Input
                    id="deepResearchModel"
                    value={getSettingValue('DeepResearchModel')}
                    onChange={(e) => onUpdate('DeepResearchModel', e.target.value)}
                    placeholder={t('settings.ai.deepResearchModelPlaceholder')}
                    disabled={loading}
                    className={validationErrors.DeepResearchModel ? 'border-destructive' : ''}
                  />
                  {validationErrors.DeepResearchModel && (
                    <p className="text-sm text-destructive">{validationErrors.DeepResearchModel}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="maxFileLimit">{t('settings.ai.maxFileLimit')}</Label>
                  <Input
                    id="maxFileLimit"
                    type="number"
                    value={getIntValue('MaxFileLimit') || ''}
                    onChange={(e) => onUpdate('MaxFileLimit', e.target.value)}
                    placeholder="10"
                    min={1}
                    max={100}
                    disabled={loading}
                    className={validationErrors.MaxFileLimit ? 'border-destructive' : ''}
                  />
                  {validationErrors.MaxFileLimit && (
                    <p className="text-sm text-destructive">{validationErrors.MaxFileLimit}</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 模型参数配置 */}
          <div className="md:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">{t('settings.ai.modelParameters')}</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-6 md:grid-cols-2">
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Label>{t('settings.ai.temperature')}</Label>
                    <Tooltip>
                      <TooltipTrigger>
                        <HelpCircle className="w-4 h-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{t('settings.ai.temperatureHelp')}</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <Slider
                    value={[getNumberValue('Temperature') || 0.7]}
                    onValueChange={(value) => onUpdate('Temperature', value[0].toString())}
                    min={0}
                    max={2}
                    step={0.1}
                    disabled={loading}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>0</span>
                    <span>0.7</span>
                    <span>1</span>
                    <span>2</span>
                  </div>
                  {validationErrors.Temperature && (
                    <p className="text-sm text-destructive">{validationErrors.Temperature}</p>
                  )}
                </div>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Label>{t('settings.ai.topP')}</Label>
                    <Tooltip>
                      <TooltipTrigger>
                        <HelpCircle className="w-4 h-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{t('settings.ai.topPHelp')}</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <Slider
                    value={[getNumberValue('TopP') || 1.0]}
                    onValueChange={(value) => onUpdate('TopP', value[0].toString())}
                    min={0}
                    max={1}
                    step={0.1}
                    disabled={loading}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>0</span>
                    <span>0.5</span>
                    <span>1</span>
                  </div>
                  {validationErrors.TopP && (
                    <p className="text-sm text-destructive">{validationErrors.TopP}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="maxTokens">{t('settings.ai.maxTokens')}</Label>
                  <Input
                    id="maxTokens"
                    type="number"
                    value={getIntValue('MaxTokens') || ''}
                    onChange={(e) => onUpdate('MaxTokens', e.target.value)}
                    placeholder="4000"
                    min={100}
                    max={100000}
                    disabled={loading}
                    className={validationErrors.MaxTokens ? 'border-destructive' : ''}
                  />
                  {validationErrors.MaxTokens && (
                    <p className="text-sm text-destructive">{validationErrors.MaxTokens}</p>
                  )}
                </div>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Label>{t('settings.ai.frequencyPenalty')}</Label>
                    <Tooltip>
                      <TooltipTrigger>
                        <HelpCircle className="w-4 h-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{t('settings.ai.frequencyPenaltyHelp')}</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <Slider
                    value={[getNumberValue('FrequencyPenalty') || 0.0]}
                    onValueChange={(value) => onUpdate('FrequencyPenalty', value[0].toString())}
                    min={-2}
                    max={2}
                    step={0.1}
                    disabled={loading}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>-2</span>
                    <span>0</span>
                    <span>2</span>
                  </div>
                  {validationErrors.FrequencyPenalty && (
                    <p className="text-sm text-destructive">{validationErrors.FrequencyPenalty}</p>
                  )}
                </div>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Label>{t('settings.ai.presencePenalty')}</Label>
                    <Tooltip>
                      <TooltipTrigger>
                        <HelpCircle className="w-4 h-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{t('settings.ai.presencePenaltyHelp')}</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <Slider
                    value={[getNumberValue('PresencePenalty') || 0.0]}
                    onValueChange={(value) => onUpdate('PresencePenalty', value[0].toString())}
                    min={-2}
                    max={2}
                    step={0.1}
                    disabled={loading}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>-2</span>
                    <span>0</span>
                    <span>2</span>
                  </div>
                  {validationErrors.PresencePenalty && (
                    <p className="text-sm text-destructive">{validationErrors.PresencePenalty}</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Mem0配置 */}
          <div className="md:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  {t('settings.ai.mem0Configuration')}
                  <Tooltip>
                    <TooltipTrigger>
                      <HelpCircle className="w-4 h-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{t('settings.ai.mem0Help')}</p>
                    </TooltipContent>
                  </Tooltip>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label>{t('settings.ai.enableMem0')}</Label>
                  <Switch
                    checked={getBooleanValue('EnableMem0')}
                    onCheckedChange={(checked) => onUpdate('EnableMem0', checked.toString())}
                    disabled={loading}
                  />
                </div>
                {getBooleanValue('EnableMem0') && (
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label htmlFor="mem0ApiKey">{t('settings.ai.mem0ApiKey')}</Label>
                      <Input
                        id="mem0ApiKey"
                        type="password"
                        value={getSettingValue('Mem0ApiKey')}
                        onChange={(e) => onUpdate('Mem0ApiKey', e.target.value)}
                        placeholder={t('settings.ai.mem0ApiKeyPlaceholder')}
                        disabled={loading}
                        className={validationErrors.Mem0ApiKey ? 'border-destructive' : ''}
                      />
                      {validationErrors.Mem0ApiKey && (
                        <p className="text-sm text-destructive">{validationErrors.Mem0ApiKey}</p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="mem0Endpoint">{t('settings.ai.mem0Endpoint')}</Label>
                      <Input
                        id="mem0Endpoint"
                        value={getSettingValue('Mem0Endpoint')}
                        onChange={(e) => onUpdate('Mem0Endpoint', e.target.value)}
                        placeholder={t('settings.ai.mem0EndpointPlaceholder')}
                        disabled={loading}
                        className={validationErrors.Mem0Endpoint ? 'border-destructive' : ''}
                      />
                      {validationErrors.Mem0Endpoint && (
                        <p className="text-sm text-destructive">{validationErrors.Mem0Endpoint}</p>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* 自定义Body参数配置 */}
          <div className="md:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  {t('settings.ai.customBodyParams')}
                  <Tooltip>
                    <TooltipTrigger>
                      <HelpCircle className="w-4 h-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{t('settings.ai.customBodyParamsHelp')}</p>
                    </TooltipContent>
                  </Tooltip>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="customBodyParams">{t('settings.ai.customBodyParamsLabel')}</Label>
                  <Input
                    id="customBodyParams"
                    value={getSettingValue('CustomBodyParams')}
                    onChange={(e) => onUpdate('CustomBodyParams', e.target.value)}
                    placeholder="stop=<|im_end|>,max_tokens=4096"
                    disabled={loading}
                    className={validationErrors.CustomBodyParams ? 'border-destructive' : ''}
                  />
                  <p className="text-xs text-muted-foreground">
                    {t('settings.ai.customBodyParamsDescription')}
                  </p>
                  {validationErrors.CustomBodyParams && (
                    <p className="text-sm text-destructive">{validationErrors.CustomBodyParams}</p>
                  )}
                </div>
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    {t('settings.ai.customBodyParamsNote')}
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* 测试API连接弹窗 */}
        <Dialog open={testModalVisible} onOpenChange={setTestModalVisible}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Bot className="w-5 h-5" />
                {t('settings.ai.testAPIConnection')}
              </DialogTitle>
            </DialogHeader>

            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                {t('settings.ai.testDescription')}
              </p>

              <div className="bg-muted p-4 rounded-lg space-y-2">
                <p className="font-medium">{t('settings.ai.currentConfiguration')}:</p>
                <div className="space-y-1 text-sm">
                  <div>
                    <span className="text-muted-foreground">{t('settings.ai.endpoint')}: </span>
                    <code className="bg-background px-1 py-0.5 rounded text-xs">
                      {getSettingValue('Endpoint') || t('common.notSet')}
                    </code>
                  </div>
                  <div>
                    <span className="text-muted-foreground">{t('settings.ai.model')}: </span>
                    <code className="bg-background px-1 py-0.5 rounded text-xs">
                      {getSettingValue('ChatModel') || t('common.notSet')}
                    </code>
                  </div>
                  <div>
                    <span className="text-muted-foreground">{t('settings.ai.apiKey')}: </span>
                    <code className="bg-background px-1 py-0.5 rounded text-xs">
                      {getSettingValue('ChatApiKey') ? '***' + getSettingValue('ChatApiKey').slice(-4) : t('common.notSet')}
                    </code>
                  </div>
                </div>
              </div>

              <Alert>
                <Info className="h-4 w-4" />
                <AlertTitle>{t('settings.ai.testNote')}</AlertTitle>
                <AlertDescription>
                  {t('settings.ai.testNoteDescription')}
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
                onClick={testAIConnection}
                disabled={testing}
              >
                {testing ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    {t('settings.ai.testing')}
                  </div>
                ) : (
                  <>
                    <Zap className="w-4 h-4 mr-2" />
                    {t('settings.ai.testConnection')}
                  </>
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </TooltipProvider>
  )
}

export default AISettingsTab