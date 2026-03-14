// 系统设置相关类型定义

// 基础系统设置接口
export interface SystemSetting {
  id: string
  key: string
  value?: string
  group: string
  valueType: string
  description?: string
  isSensitive: boolean
  requiresRestart: boolean
  defaultValue?: string
  order: number
  isEnabled: boolean
  createdAt: string
  updatedAt: string
}

// 系统设置分组
export interface SystemSettingGroup {
  group: string
  settings: SystemSetting[]
}

// 系统设置更新项
export interface SystemSettingUpdateItem {
  key: string
  value?: string
}

// 批量更新系统设置输入
export interface BatchUpdateSystemSettings {
  settings: SystemSettingUpdateItem[]
}

// 系统设置输入DTO
export interface SystemSettingInput {
  key: string
  value?: string
  group: string
  valueType: string
  description?: string
  isSensitive: boolean
  requiresRestart: boolean
  defaultValue?: string
  order: number
}

// 配置验证错误
export interface ValidationErrors {
  [key: string]: string
}

// 设置组类型定义
export type SettingGroupType =
  | 'Basic'      // 基本设置
  | 'Email'      // 邮件配置
  | 'OpenAI'     // AI设置
  | 'Storage'    // 存储设置
  | 'Security'   // 安全设置
  | 'Backup'     // 备份恢复
  | 'Logging'    // 日志设置
  | 'GitHub'     // GitHub集成
  | 'Gitee'      // Gitee集成
  | 'JWT'        // JWT配置
  | 'Document'   // 文档配置

// 基本设置配置
export interface BasicSettings {
  siteName?: string
  siteLogo?: string
  siteDescription?: string
  copyRight?: string
  favicon?: string
  siteKeywords?: string
  analyticsCode?: string
  contactEmail?: string
  supportUrl?: string
  privacyPolicyUrl?: string
  termsOfServiceUrl?: string
}

// 邮件配置
export interface EmailSettings {
  smtpHost?: string
  smtpPort?: number
  smtpUser?: string
  smtpPassword?: string
  smtpEnableSsl?: boolean
  smtpEnableTls?: boolean
  senderName?: string
  senderEmail?: string
  replyToEmail?: string
  emailTemplate?: string
  maxEmailsPerHour?: number
}

// AI设置配置
export interface AISettings {
  chatModel?: string
  analysisModel?: string
  chatApiKey?: string
  endpoint?: string
  modelProvider?: string
  maxFileLimit?: number
  deepResearchModel?: string
  enableMem0?: boolean
  mem0ApiKey?: string
  mem0Endpoint?: string
  temperature?: string
  maxTokens?: number
  topP?: string
  frequencyPenalty?: string
  presencePenalty?: string
  customBodyParams?: string
}

// 存储设置
export interface StorageSettings {
  fileStoragePath?: string
  maxFileSize?: number
  allowedFileTypes?: string[]
  enableCompression?: boolean
  compressionQuality?: number
  storageTiers?: string
  backupStoragePath?: string
  enableCloudStorage?: boolean
  cloudStorageProvider?: string
  cloudStorageConfig?: string
}

// 安全设置
export interface SecuritySettings {
  passwordMinLength?: number
  passwordRequireNumbers?: boolean
  passwordRequireSymbols?: boolean
  passwordRequireUppercase?: boolean
  passwordRequireLowercase?: boolean
  sessionTimeoutMinutes?: number
  maxLoginAttempts?: number
  lockoutDurationMinutes?: number
  enableTwoFactorAuth?: boolean
  allowedIpAddresses?: string[]
  blockedIpAddresses?: string[]
  enableCaptcha?: boolean
  captchaProvider?: string
  captchaConfig?: string
}

// 备份恢复设置
export interface BackupSettings {
  enableAutoBackup?: boolean
  backupSchedule?: string
  backupRetentionDays?: number
  backupPath?: string
  backupFormat?: string
  includeFiles?: boolean
  includeDatabase?: boolean
  includeSettings?: boolean
  enableRemoteBackup?: boolean
  remoteBackupProvider?: string
  remoteBackupConfig?: string
  lastBackupTime?: string
  nextBackupTime?: string
}

// 日志设置
export interface LoggingSettings {
  logLevel?: string
  enableFileLogging?: boolean
  logFilePath?: string
  maxLogFileSize?: number
  logRetentionDays?: number
  enableDatabaseLogging?: boolean
  enableEmailNotifications?: boolean
  errorNotificationEmails?: string[]
  auditLogEnabled?: boolean
  performanceLogEnabled?: boolean
  logFormat?: string
}

// GitHub集成设置
export interface GitHubSettings {
  clientId?: string
  clientSecret?: string
  token?: string
  webhookSecret?: string
  enableOAuth?: boolean
  allowedOrganizations?: string[]
  defaultRepository?: string
  enableAutoSync?: boolean
  syncInterval?: number
}

// Gitee集成设置
export interface GiteeSettings {
  clientId?: string
  clientSecret?: string
  token?: string
  webhookSecret?: string
  enableOAuth?: boolean
  allowedOrganizations?: string[]
  defaultRepository?: string
  enableAutoSync?: boolean
  syncInterval?: number
}

// JWT配置
export interface JWTSettings {
  secret?: string
  issuer?: string
  audience?: string
  expireMinutes?: number
  refreshExpireMinutes?: number
  algorithm?: string
  enableRefreshToken?: boolean
  maxRefreshTokens?: number
}

// 文档配置
export interface DocumentSettings {
  enableIncrementalUpdate?: boolean
  excludedFiles?: string[]
  excludedFolders?: string[]
  enableSmartFilter?: boolean
  catalogueFormat?: string
  enableCodeDependencyAnalysis?: boolean
  enableWarehouseFunctionPromptTask?: boolean
  enableWarehouseDescriptionTask?: boolean
  enableFileCommit?: boolean
  refineAndEnhanceQuality?: boolean
  enableWarehouseCommit?: boolean
  enableCodeCompression?: boolean
  maxFileReadCount?: number
  supportedLanguages?: string[]
  defaultLanguage?: string
}

// 设置测试结果
export interface SettingTestResult {
  success: boolean
  message: string
  details?: any
}

// 邮件测试参数
export interface EmailTestParams {
  to: string
  subject?: string
  body?: string
}

// API连接测试参数
export interface APITestParams {
  endpoint: string
  apiKey: string
  model?: string
}

// 数据库连接测试结果
export interface DatabaseTestResult extends SettingTestResult {
  connectionTime?: number
  version?: string
}

// 系统状态信息
export interface SystemStatus {
  systemInfo: {
    version: string
    environment: string
    uptime: string
    lastRestart: string
  }
  performance: {
    cpuUsage: number
    memoryUsage: number
    diskUsage: number
    activeConnections: number
  }
  features: {
    emailConfigured: boolean
    aiConfigured: boolean
    backupConfigured: boolean
    securityConfigured: boolean
  }
}

// 设置导入导出
export interface SettingsExport {
  version: string
  exportDate: string
  settings: SystemSetting[]
  groups: string[]
}

export interface SettingsImport {
  file: File
  overwriteExisting: boolean
  selectedGroups: string[]
}

// 设置变更历史
export interface SettingChangeHistory {
  id: string
  settingKey: string
  oldValue?: string
  newValue?: string
  changedBy: string
  changedAt: string
  reason?: string
  rollbackAvailable: boolean
}

// 表单验证规则
export interface SettingValidationRule {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  min?: number
  max?: number
  validator?: (value: any) => string | null
}

// 设置字段配置
export interface SettingFieldConfig {
  key: string
  label: string
  type: 'text' | 'password' | 'number' | 'boolean' | 'select' | 'textarea' | 'array' | 'json'
  placeholder?: string
  description?: string
  helpText?: string
  validation?: SettingValidationRule
  options?: Array<{value: string, label: string}>
  sensitive?: boolean
  requiresRestart?: boolean
  dependsOn?: string[]
  conditionalDisplay?: (settings: any) => boolean
}

// 设置分组配置
export interface SettingGroupConfig {
  key: SettingGroupType
  label: string
  description?: string
  icon?: string
  order: number
  fields: SettingFieldConfig[]
}