// 应用配置服务
import { fetchService } from './fetch'

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

export interface DomainValidationRequest {
  appId: string
  domain: string
}

export interface DomainValidationResponse {
  isValid: boolean
  reason?: string
  appConfig?: AppConfigOutput
}

class AppConfigService {
  /**
   * 创建应用配置
   */
  async createAppConfig(data: AppConfigInput): Promise<AppConfigOutput> {
    return fetchService.post<AppConfigOutput>('/api/AppConfig', data)
  }

  /**
   * 获取应用配置列表
   */
  async getAppConfigs(): Promise<AppConfigOutput[]> {
    return fetchService.get<AppConfigOutput[]>('/api/AppConfig')
  }

  /**
   * 根据AppId获取应用配置
   */
  async getAppConfigByAppId(appId: string): Promise<AppConfigOutput> {
    return fetchService.get<AppConfigOutput>(`/api/AppConfig/${appId}`)
  }

  /**
   * 更新应用配置
   */
  async updateAppConfig(appId: string, data: AppConfigInput): Promise<AppConfigOutput> {
    return fetchService.put<AppConfigOutput>(`/api/AppConfig/${appId}`, data)
  }

  /**
   * 删除应用配置
   */
  async deleteAppConfig(appId: string): Promise<void> {
    await fetchService.delete(`/api/AppConfig/${appId}`)
  }

  /**
   * 切换应用启用状态
   */
  async toggleAppConfig(appId: string): Promise<AppConfigOutput> {
    return fetchService.post<AppConfigOutput>(`/api/AppConfig/${appId}/toggle`)
  }

  /**
   * 验证域名
   */
  async validateDomain(data: DomainValidationRequest): Promise<DomainValidationResponse> {
    return fetchService.post<DomainValidationResponse>('/api/AppConfig/validatedomain', data)
  }

  /**
   * 获取公开应用配置
   */
  async getPublicAppConfig(appId: string): Promise<AppConfigOutput | null> {
    return fetchService.get<AppConfigOutput | null>(`/api/AppConfig/public/${appId}`)
  }
}

export const appConfigService = new AppConfigService()