// 通用类型定义

// 用户相关
export interface User {
  id: string
  username: string
  email: string
  avatar?: string
  bio?: string
  location?: string
  website?: string
  company?: string
  createdAt: string
  updatedAt?: string
  lastLoginAt?: string
}

// 仓库相关
export interface Warehouse {
  id: string
  name: string
  organizationName: string
  description?: string
  address?: string
  branch?: string
  status?: number
  createdAt: string
  updatedAt?: string
}

// 应用配置相关
export interface AppConfigMcp {
  url: string
  headers: Record<string, string>
}

export interface AppConfigInput {
  appId: string
  name: string
  organizationName: string
  repositoryName: string
  description?: string
  allowedDomains: string[]
  enableDomainValidation: boolean
  prompt?: string
  introduction?: string
  model?: string
  recommendedQuestions?: string[]
  mcps?: AppConfigMcp[]
}

export interface AppConfigOutput extends AppConfigInput {
  isEnabled: boolean
  createdAt: string
  updatedAt?: string
  lastUsedAt?: string
}

// 导出服务类型
export type { UserProfile, UpdateProfileData, ChangePasswordData } from '@/services/userService'
export type { DomainValidationRequest, DomainValidationResponse } from '@/services/appConfigService'