import React, { useState } from 'react'
import {
  FileText,
  Filter,
  Code,
  Settings,
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
import { Switch } from '@/components/ui/switch'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Badge } from '@/components/ui/badge'

interface DocumentSettingsTabProps {
  settings: SystemSetting[]
  onUpdate: (key: string, value: any) => void
  validationErrors: ValidationErrors
  loading?: boolean
}

const DocumentSettingsTab: React.FC<DocumentSettingsTabProps> = ({
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

  // 目录格式选项
  const catalogueFormatOptions = [
    { value: 'compact', label: t('settings.document.formatCompact') },
    { value: 'detailed', label: t('settings.document.formatDetailed') },
    { value: 'tree', label: t('settings.document.formatTree') },
    { value: 'flat', label: t('settings.document.formatFlat') }
  ]

  // 支持的编程语言
  const supportedLanguages = [
    'javascript', 'typescript', 'python', 'java', 'csharp', 'cpp', 'c',
    'go', 'rust', 'php', 'ruby', 'swift', 'kotlin', 'scala', 'r',
    'matlab', 'shell', 'bash', 'powershell', 'sql', 'html', 'css',
    'json', 'xml', 'yaml', 'markdown', 'dockerfile', 'terraform'
  ]

  // 文件扩展名输入组件
  const FileExtensionList = ({
    value = [],
    onChange,
    placeholder
  }: {
    value?: string[]
    onChange?: (value: string[]) => void
    placeholder?: string
  }) => {
    const [inputValue, setInputValue] = useState('')

    const addExtension = () => {
      if (inputValue && !value.includes(inputValue)) {
        onChange?.([...value, inputValue])
        setInputValue('')
      }
    }

    const removeExtension = (ext: string) => {
      onChange?.(value.filter(item => item !== ext))
    }

    return (
      <div className="space-y-3">
        <div className="flex gap-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={placeholder}
            onKeyDown={(e) => e.key === 'Enter' && addExtension()}
            className="flex-1"
          />
          <Button
            type="button"
            onClick={addExtension}
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
              {value.map((ext, index) => (
                <Badge
                  key={index}
                  variant="secondary"
                  className="cursor-pointer"
                  onClick={() => removeExtension(ext)}
                >
                  {ext}
                  <X className="w-3 h-3 ml-1" />
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  const selectedSupportedLanguages = getArrayValue('supportedLanguages')

  return (
    <TooltipProvider>
      <div className="max-w-4xl space-y-6">
        <div>
          <h3 className="text-lg font-semibold">{t('settings.groups.document')}</h3>
          <p className="text-sm text-muted-foreground mt-2">
            {t('settings.documentDescription')}
          </p>
        </div>

        <div className="space-y-6">
          {/* 基本文档设置 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <FileText className="w-4 h-4" />
                {t('settings.document.basicSettings')}
              </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>{t('settings.document.enableIncrementalUpdate')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('settings.document.enableIncrementalUpdateHelp')}
                  </p>
                </div>
                <Switch
                  checked={getBooleanValue('EnableIncrementalUpdate')}
                  onCheckedChange={(checked) => onUpdate('EnableIncrementalUpdate', checked.toString())}
                  disabled={loading}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="catalogueFormat">{t('settings.document.catalogueFormat')}</Label>
                <Select
                  value={getSettingValue('CatalogueFormat')}
                  onValueChange={(value) => onUpdate('CatalogueFormat', value)}
                  disabled={loading}
                >
                  <SelectTrigger className={validationErrors.CatalogueFormat ? 'border-destructive' : ''}>
                    <SelectValue placeholder={t('settings.document.catalogueFormatPlaceholder')} />
                  </SelectTrigger>
                  <SelectContent>
                    {catalogueFormatOptions.map(option => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {validationErrors.CatalogueFormat && (
                  <p className="text-sm text-destructive">{validationErrors.CatalogueFormat}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="readMaxTokens">{t('settings.document.readMaxTokens')}</Label>
                <Input
                  id="readMaxTokens"
                  type="number"
                  value={getNumberValue('ReadMaxTokens') || ''}
                  onChange={(e) => onUpdate('ReadMaxTokens', e.target.value)}
                  placeholder="80000"
                  min={1000}
                  max={200000}
                  disabled={loading}
                  className={validationErrors.ReadMaxTokens ? 'border-destructive' : ''}
                />
                {validationErrors.ReadMaxTokens ? (
                  <p className="text-sm text-destructive">{validationErrors.ReadMaxTokens}</p>
                ) : (
                  <p className="text-sm text-muted-foreground">{t('settings.document.readMaxTokensHelp')}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="defaultLanguage">{t('settings.document.defaultLanguage')}</Label>
                <Input
                  id="defaultLanguage"
                  value={getSettingValue('defaultLanguage')}
                  onChange={(e) => onUpdate('defaultLanguage', e.target.value)}
                  placeholder={t('settings.document.defaultLanguagePlaceholder')}
                  disabled={loading}
                  className={validationErrors.defaultLanguage ? 'border-destructive' : ''}
                />
                {validationErrors.defaultLanguage ? (
                  <p className="text-sm text-destructive">{validationErrors.defaultLanguage}</p>
                ) : (
                  <p className="text-sm text-muted-foreground">设置生成文档时使用的默认语言，而非编程语言</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="proxy">{t('settings.document.proxy')}</Label>
                <Input
                  id="proxy"
                  value={getSettingValue('Proxy')}
                  onChange={(e) => onUpdate('Proxy', e.target.value)}
                  placeholder={t('settings.document.proxyPlaceholder')}
                  disabled={loading}
                  className={validationErrors.Proxy ? 'border-destructive' : ''}
                />
                {validationErrors.Proxy ? (
                  <p className="text-sm text-destructive">{validationErrors.Proxy}</p>
                ) : (
                  <p className="text-sm text-muted-foreground">{t('settings.document.proxyHelp')}</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* 文件过滤设置 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Filter className="w-4 h-4" />
                {t('settings.document.fileFiltering')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Label>{t('settings.document.excludedFiles')}</Label>
                    <Tooltip>
                      <TooltipTrigger>
                        <HelpCircle className="w-4 h-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{t('settings.document.excludedFilesHelp')}</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <FileExtensionList
                    value={getArrayValue('ExcludedFiles')}
                    onChange={(value) => updateArrayValue('ExcludedFiles', value)}
                    placeholder={t('settings.document.excludedFilesPlaceholder')}
                  />
                  <p className="text-sm text-muted-foreground">
                    {t('settings.document.excludedFilesDescription')}
                  </p>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Label>{t('settings.document.excludedFolders')}</Label>
                    <Tooltip>
                      <TooltipTrigger>
                        <HelpCircle className="w-4 h-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{t('settings.document.excludedFoldersHelp')}</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <FileExtensionList
                    value={getArrayValue('ExcludedFolders')}
                    onChange={(value) => updateArrayValue('ExcludedFolders', value)}
                    placeholder={t('settings.document.excludedFoldersPlaceholder')}
                  />
                  <p className="text-sm text-muted-foreground">
                    {t('settings.document.excludedFoldersDescription')}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 代码分析设置 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Code className="w-4 h-4" />
                {t('settings.document.codeAnalysis')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>{t('settings.document.enableCodeDependencyAnalysis')}</Label>
                    <p className="text-sm text-muted-foreground">
                      {t('settings.document.enableCodeDependencyAnalysisHelp')}
                    </p>
                  </div>
                  <Switch
                    checked={getBooleanValue('EnableCodeDependencyAnalysis')}
                    onCheckedChange={(checked) => onUpdate('EnableCodeDependencyAnalysis', checked.toString())}
                    disabled={loading}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>{t('settings.document.enableCodeCompression')}</Label>
                    <p className="text-sm text-muted-foreground">
                      {t('settings.document.enableCodeCompressionHelp')}
                    </p>
                  </div>
                  <Switch
                    checked={getBooleanValue('EnableCodeCompression')}
                    onCheckedChange={(checked) => onUpdate('EnableCodeCompression', checked.toString())}
                    disabled={loading}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label>{t('settings.document.supportedLanguages')}</Label>
                <Select
                  value={selectedSupportedLanguages.length > 0 ? selectedSupportedLanguages[0] : ''}
                  onValueChange={(value) => {
                    const currentLanguages = selectedSupportedLanguages
                    if (value && !currentLanguages.includes(value)) {
                      updateArrayValue('supportedLanguages', [...currentLanguages, value])
                    }
                  }}
                  disabled={loading}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={t('settings.document.supportedLanguagesPlaceholder')} />
                  </SelectTrigger>
                  <SelectContent>
                    {supportedLanguages
                      .filter(lang => !selectedSupportedLanguages.includes(lang))
                      .map(lang => (
                        <SelectItem key={lang} value={lang}>
                          {lang}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
                <div className="flex flex-wrap gap-1">
                  {selectedSupportedLanguages.map((lang: string) => (
                    <Badge
                      key={lang}
                      variant="secondary"
                      className="cursor-pointer"
                      onClick={() => {
                        const newLanguages = selectedSupportedLanguages.filter((l: string) => l !== lang)
                        updateArrayValue('supportedLanguages', newLanguages)
                      }}
                    >
                      {lang} ×
                    </Badge>
                  ))}
                </div>
                <p className="text-sm text-muted-foreground">{t('settings.document.supportedLanguagesHelp')}</p>
              </div>
            </CardContent>
          </Card>

          {/* 仓库处理任务 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Settings className="w-4 h-4" />
                {t('settings.document.warehouseTasks')}
              </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>{t('settings.document.enableWarehouseFunctionPromptTask')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('settings.document.enableWarehouseFunctionPromptTaskHelp')}
                  </p>
                </div>
                <Switch
                  checked={getBooleanValue('EnableWarehouseFunctionPromptTask')}
                  onCheckedChange={(checked) => onUpdate('EnableWarehouseFunctionPromptTask', checked.toString())}
                  disabled={loading}
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>{t('settings.document.enableFileCommit')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('settings.document.enableFileCommitHelp')}
                  </p>
                </div>
                <Switch
                  checked={getBooleanValue('EnableFileCommit')}
                  onCheckedChange={(checked) => onUpdate('EnableFileCommit', checked.toString())}
                  disabled={loading}
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>{t('settings.document.enableWarehouseCommit')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('settings.document.enableWarehouseCommitHelp')}
                  </p>
                </div>
                <Switch
                  checked={getBooleanValue('EnableWarehouseCommit')}
                  onCheckedChange={(checked) => onUpdate('EnableWarehouseCommit', checked.toString())}
                  disabled={loading}
                />
              </div>
              <div className="md:col-span-2 flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>{t('settings.document.refineAndEnhanceQuality')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('settings.document.refineAndEnhanceQualityHelp')}
                  </p>
                </div>
                <Switch
                  checked={getBooleanValue('RefineAndEnhanceQuality')}
                  onCheckedChange={(checked) => onUpdate('RefineAndEnhanceQuality', checked.toString())}
                  disabled={loading}
                />
              </div>
            </CardContent>
          </Card>

          {/* 文档处理优化建议 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">{t('settings.document.optimizationTips')}</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>{t('settings.document.tip1')}</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>{t('settings.document.tip2')}</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>{t('settings.document.tip3')}</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>{t('settings.document.tip4')}</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>{t('settings.document.tip5')}</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </TooltipProvider>
  )
}

export default DocumentSettingsTab