import { request } from '@/utils/request'
import type {
  SystemSetting,
  SystemSettingGroup,
  BatchUpdateSystemSettings,
  SystemSettingInput,
  ValidationErrors,
  SettingTestResult,
  EmailTestParams,
  APITestParams,
  SettingChangeHistory
} from '@/types/systemSettings'

// 用户管理相关接口
export interface UserInfo {
  id: string
  name: string
  email: string
  avatar?: string
  role?: string
  createdAt: string
  updatedAt?: string
}

export interface PageDto<T> {
  total: number
  items: T[]
}

export interface CreateUserDto {
  name: string
  email: string
  password: string
  avatar?: string
}

export interface UpdateUserDto {
  name: string
  email: string
  avatar?: string
  password?: string
}

export interface ResetPasswordDto {
  newPassword: string
}

export interface AssignUserRoleDto {
  roleIds: string[]
}

export interface BatchDeleteUserDto {
  userIds: string[]
}

// 同步记录相关接口
export interface WarehouseSyncRecord {
  id: string
  warehouseId: string
  status: 'InProgress' | 'Success' | 'Failed'
  startTime: string
  endTime?: string
  fromVersion?: string
  toVersion?: string
  errorMessage?: string
  fileCount: number
  updatedFileCount: number
  addedFileCount: number
  deletedFileCount: number
  trigger: 'Auto' | 'Manual'
  createdAt: string
}

export interface UpdateWarehouseSyncDto {
  enableSync: boolean
}

// 用户管理API
export const userService = {
  // 获取用户列表
  getUserList: async (page: number = 1, pageSize: number = 10, keyword?: string) => {
    const params = new URLSearchParams({
      page: page.toString(),
      pageSize: pageSize.toString()
    })
    if (keyword) {
      params.append('keyword', keyword)
    }
    return request.get<PageDto<UserInfo>>(`/api/user/UserList?${params}`)
  },

  // 获取用户详情
  getUser: async (id: string) => {
    return request.get<{ data: UserInfo }>(`/api/user/User?id=${id}`)
  },

  // 创建用户
  createUser: async (data: CreateUserDto) => {
    return request.post<{ data: UserInfo }>('/api/user/CreateUser', data)
  },

  // 更新用户
  updateUser: async (id: string, data: UpdateUserDto) => {
    return request.post<{ data: UserInfo }>(`/api/user/UpdateUser?id=${id}`, data)
  },

  // 删除用户
  deleteUser: async (id: string) => {
    return request.post(`/api/user/DeleteUser?id=${id}`)
  },

  // 重置用户密码
  resetUserPassword: async (id: string, newPassword: string) => {
    return request.post(`/api/user/ResetPassword?id=${id}`, { newPassword })
  },

  // 为用户分配角色
  assignUserRoles: async (id: string, roleIds: string[]) => {
    return request.post(`/api/user/AssignRoles?id=${id}`, { roleIds })
  },

  // 获取用户角色
  getUserRoles: async (id: string) => {
    return request.get<string[]>(`/api/user/UserRoles?id=${id}`)
  },

  // 批量删除用户
  batchDeleteUsers: async (userIds: string[]) => {
    return request.post('/api/user/BatchDelete', { userIds })
  }
}

// 角色管理相关接口
export interface RoleInfo {
  id: string
  name: string
  description?: string
  isActive: boolean
  isSystemRole: boolean
  userCount?: number
  warehousePermissionCount?: number
  createdAt: string
  updatedAt?: string
}

export interface CreateRoleDto {
  name: string
  description?: string
  isActive: boolean
}

export interface UpdateRoleDto {
  name: string
  description?: string
  isActive: boolean
}

export interface RoleDetailDto extends RoleInfo {
  users?: UserInfo[]
  warehousePermissions?: any[]
}

// 角色管理API
export const roleService = {
  // 获取角色列表
  getRoleList: async (page?: number, pageSize?: number, keyword?: string, isActive?: boolean) => {
    const params = new URLSearchParams()
    if (page) params.append('page', page.toString())
    if (pageSize) params.append('pageSize', pageSize.toString())
    if (keyword) params.append('keyword', keyword)
    if (isActive !== undefined) params.append('isActive', isActive.toString())

    return request.get<PageDto<RoleInfo>>(`/api/Role/RoleList?${params}`)
  },

  // 获取角色详情
  getRoleDetail: async (id: string) => {
    return request.get<RoleDetailDto>(`/api/Role/RoleDetail?id=${id}`)
  },

  // 获取所有角色(下拉选择)
  getAllRoles: async () => {
    return request.get<RoleInfo[]>('/api/Role/AllRoles')
  },

  // 创建角色
  createRole: async (data: CreateRoleDto) => {
    return request.post<RoleInfo>('/api/Role/CreateRole', data)
  },

  // 更新角色
  updateRole: async (id: string, data: UpdateRoleDto) => {
    return request.post<RoleInfo>(`/api/Role/UpdateRole?id=${id}`, data)
  },

  // 删除角色
  deleteRole: async (id: string) => {
    return request.post<boolean>(`/api/Role/DeleteRole?id=${id}`)
  },

  // 批量更新角色状态
  batchUpdateRoleStatus: async (ids: string[], isActive: boolean) => {
    return request.post<boolean>(`/api/Role/BatchUpdateRoleStatus?isActive=${isActive}`,ids)
  }
}

// 仓库管理相关接口
export interface WarehouseInfo {
  id: string
  name: string
  organizationName: string
  address: string
  branch: string
  description?: string
  status?: 'Pending' | 'Processing' | 'Completed' | 'Failed'
  createdAt: string
  updatedAt?: string
  optimizedDirectoryStructure?: string
  enableSync?: boolean
  documentCount?: number
  type?: string
  isRecommended?: boolean
  error?: string
  version?: string
  isEmbedded?: boolean
  stars?: number
  forks?: number
  language?: string
  license?: string
  avatarUrl?: string
  ownerUrl?: string
}

export interface CreateGitRepositoryDto {
  address: string
  branch: string
  gitUserName?: string
  gitPassword?: string
  email?: string
}

export interface UpdateRepositoryDto {
  description?: string
  isRecommended?: boolean
  prompt?: string
}

export interface RepositoryStatsDto {
  TotalDocuments: number
  CompletedDocuments: number
  PendingDocuments: number
  TotalFiles: number
  LastSyncTime?: string
  ProcessingStatus: string
}

export interface RepositoryPermissionDto {
  roleId: string
  roleName: string
  isRead: boolean
  isWrite: boolean
  isDelete: boolean
}

export interface BatchOperationDto {
  ids: string[]
  operation: 'enable' | 'disable' | 'delete' | 'refresh'
}

export interface RepositoryLogDto {
  id: string
  repositoryId: string
  operation: string
  description: string
  userId?: string
  userName?: string
  createdAt: string
  success: boolean
  error?: string
}

export interface BranchInfo {
  name: string
  isDefault: boolean
}

export interface GitBranchListDto {
  branches: string[]
  defaultBranch: string
}

export interface DocumentCatalogDto {
  id: string
  name: string
  url?: string
  prompt?: string
  parentId?: string
  order: number
  warehouseId: string
  isCompleted: boolean
  createdAt: string
}

export interface CreateCatalogInput {
  warehouseId: string
  name: string
  url: string
  prompt: string
  parentId?: string
  order: number
}

export interface TreeNode {
  title: string
  key: string
  isLeaf?: boolean
  children?: TreeNode[]
}

// 仓库管理API
export const repositoryService = {
  // 获取仓库列表
  getRepositoryList: async (
    page: number = 1,
    pageSize: number = 10,
    keyword?: string,
    status?: string,
    type?: string
  ) => {
    const params = new URLSearchParams({
      page: page.toString(),
      pageSize: pageSize.toString()
    })
    if (keyword) params.append('keyword', keyword)
    if (status) params.append('status', status)
    if (type) params.append('type', type)

    return request.get<PageDto<WarehouseInfo>>(`/api/Repository/RepositoryList?${params}`)
  },

  // 获取仓库详情
  getRepositoryDetail: async (id: string) => {
    const response = await request.get<{ data: WarehouseInfo }>(`/api/Repository/Repository?id=${id}`)
    return response.data
  },

  // 获取仓库统计信息
  getRepositoryStats: async () => {
    return request.get<RepositoryStatsDto>('/api/Warehouse/Stats')
  },

  // 获取仓库统计信息(按ID)
  getRepositoryStatsById: async (id: string) => {
    return request.get<RepositoryStatsDto>(`/api/Repository/RepositoryStats`, {
      params: { id }
    })
  },

  // 获取仓库文件目录结构
  getFiles: async (id: string) => {
    return request.get<TreeNode[]>(`/api/Repository/Files`, {
      params: { id }
    })
  },

  // 获取仓库文档目录
  getDocumentCatalogs: async (repositoryId: string) => {
    return request.get<DocumentCatalogDto[]>(`/api/Repository/DocumentCatalogs`, {
      params: { repositoryId }
    })
  },

  // 获取文件内容
  getFileContent: async (catalogId: string) => {
    return request.get<string>(`/api/Repository/FileContent`, {
      params: { id: catalogId }
    })
  },

  // 保存文件内容
  saveFileContent: async (catalogId: string, content: string) => {
    const data = { id: catalogId, content }
    return request.post<boolean>(`/api/Repository/FileContent`,data)
  },

  // 刷新/重置仓库
  refreshWarehouse: async (id: string) => {
    return request.post<boolean>(`/api/Repository/ResetRepository`, null, {
      params: { id }
    })
  },

  // 删除仓库
  deleteWarehouse: async (id: string) => {
    return request.delete<boolean>(`/api/Repository/Repository`, {
      params: { id }
    })
  },

  // 更新仓库信息
  updateRepository: async (id: string, data: Partial<WarehouseInfo>) => {
    return request.put<boolean>(`/api/Repository/UpdateWarehouse?id=${id}`, data)
  },

  // 导出仓库Markdown
  exportRepositoryMarkdown: async (id: string) => {
    // 这个需要根据实际后端API调整
    const response = await request.get(`/api/Repository/Export`, {
      params: { id },
      responseType: 'blob'
    })
    return response as Blob
  },

  // 创建Git仓库
  createGitRepository: async (data: CreateGitRepositoryDto) => {
    return request.post<string>('/api/Repository/GitRepository', data)
  },

  // 删除仓库
  deleteRepository: async (id: string) => {
    return request.delete<boolean>(`/api/Repository/Repository?id=${id}`)
  },

  // 批量操作仓库
  batchOperateRepositories: async (data: BatchOperationDto) => {
    return request.post<boolean>('/api/Warehouse/BatchOperate', data)
  },

  // 刷新仓库
  refreshRepository: async (id: string) => {
    return request.post<boolean>(`/api/Repository/ResetRepository?id=${id}`)
  },

  // 获取仓库权限
  getRepositoryPermissions: async (id: string) => {
    return request.get<RepositoryPermissionDto[]>(`/api/Warehouse/GetPermissions?id=${id}`)
  },

  // 更新仓库权限
  updateRepositoryPermissions: async (id: string, permissions: RepositoryPermissionDto[]) => {
    return request.post<boolean>(`/api/Warehouse/UpdatePermissions?id=${id}`, permissions)
  },

  // 获取仓库日志
  getRepositoryLogs: async (
    repositoryId: string,
    page: number = 1,
    pageSize: number = 10
  ) => {
    const params = new URLSearchParams({
      repositoryId,
      page: page.toString(),
      pageSize: pageSize.toString()
    })
    return request.get<PageDto<RepositoryLogDto>>(`/api/Repository/RepositoryLogs?${params}`)
  },

  // 获取Git分支列表
  getGitBranches: async (address: string) => {
    return request.get<GitBranchListDto>(`/api/Warehouse/GetGitBranches?address=${encodeURIComponent(address)}`)
  },

  // 获取文档目录树
  getDocumentTree: async (warehouseId: string) => {
    return request.get<TreeNode[]>(`/api/Warehouse/GetDocumentTree?warehouseId=${warehouseId}`)
  },

  // 获取文档目录列表
  getCatalogList: async (warehouseId: string) => {
    return request.get<DocumentCatalogDto[]>(`/api/Catalog/GetCatalogs?warehouseId=${warehouseId}`)
  },

  // 创建文档目录
  createCatalog: async (data: CreateCatalogInput) => {
    return request.post<string>('/api/Catalog/CreateCatalog', data)
  },

  // 更新文档目录
  updateCatalog: async (catalogId: string, data: Partial<CreateCatalogInput>) => {
    return request.post<boolean>(`/api/Catalog/UpdateCatalog?id=${catalogId}`, data)
  },

  // 删除文档目录
  deleteCatalog: async (catalogId: string) => {
    return request.post<boolean>(`/api/Catalog/DeleteCatalog?id=${catalogId}`)
  },

  // 排序文档目录
  sortCatalogs: async (warehouseId: string, catalogIds: string[]) => {
    return request.post<boolean>('/api/Catalog/SortCatalogs', {
      warehouseId,
      catalogIds
    })
  },

  // 更新仓库同步设置
  updateWarehouseSync: async (id: string, data: UpdateWarehouseSyncDto) => {
    return request.post<boolean>(`/api/Repository/UpdateSync?id=${id}`, data)
  },

  // 获取仓库同步记录
  getWarehouseSyncRecords: async (
    warehouseId: string,
    page: number = 1,
    pageSize: number = 10
  ) => {
    const params = new URLSearchParams({
      warehouseId,
      page: page.toString(),
      pageSize: pageSize.toString()
    })
    return request.get<PageDto<WarehouseSyncRecord>>(`/api/Repository/SyncRecords?${params}`)
  },

  // 手动触发同步
  triggerManualSync: async (id: string) => {
    return request.post<boolean>(`/api/Repository/ManualSync?id=${id}`)
  },

  // AI生成文档内容
  generateFileContent: async (id: string, prompt?: string) => {
    return request.post<boolean>('/api/Repository/GenerateFileContent', {
      id,
      prompt
    })
  }
}

// 保持向后兼容旧的仓库服务命名
export const warehouseService = repositoryService

// 系统设置管理API
export const systemSettingsService = {
  // 获取所有系统设置分组
  getSettingGroups: async (): Promise<SystemSettingGroup[]> => {
    try {
      const response = await request.get<any>('/api/SystemSetting/groups')

      return response.data.map((group: any) => ({
        group: group.group || '',
        settings: Array.isArray(group.settings) ? group.settings : []
      }))
    } catch (error) {
      console.error('Failed to load setting groups:', error)
      return []
    }
  },

  // 根据分组获取系统设置
  getSettingsByGroup: async (group: string): Promise<SystemSetting[]> => {
    try {
      const response = await request.get<SystemSetting[]>(`/api/SystemSetting/group/${group}`)
      return Array.isArray(response) ? response : []
    } catch (error) {
      console.error(`Failed to load settings for group ${group}:`, error)
      return []
    }
  },

  // 获取单个系统设置
  getSetting: async (key: string): Promise<SystemSetting | null> => {
    try {
      return await request.get<SystemSetting>(`/api/SystemSetting/${key}`)
    } catch (error) {
      console.error(`Failed to load setting ${key}:`, error)
      return null
    }
  },

  // 更新单个系统设置
  updateSetting: async (key: string, value?: string): Promise<boolean> => {
    try {
      // 直接发送字符串值，后端期望接收 string 类型的 body
      return await request.put<boolean>(`/api/SystemSetting/${key}`, value || '', {
        headers: { 'Content-Type': 'application/json' }
      })
    } catch (error) {
      console.error(`Failed to update setting ${key}:`, error)
      return false
    }
  },

  // 批量更新系统设置
  batchUpdateSettings: async (data: BatchUpdateSystemSettings): Promise<boolean> => {
    try {
      return await request.put<boolean>('/api/SystemSetting/batch', data)
    } catch (error) {
      console.error('Failed to batch update settings:', error)
      return false
    }
  },

  // 创建新的系统设置
  createSetting: async (data: SystemSettingInput): Promise<SystemSetting | null> => {
    try {
      return await request.post<SystemSetting>('/api/SystemSetting/', data)
    } catch (error) {
      console.error('Failed to create setting:', error)
      return null
    }
  },

  // 删除系统设置
  deleteSetting: async (key: string): Promise<boolean> => {
    try {
      return await request.delete<boolean>(`/api/SystemSetting/${key}`)
    } catch (error) {
      console.error(`Failed to delete setting ${key}:`, error)
      return false
    }
  },

  // 重置设置为默认值
  resetSetting: async (key: string): Promise<boolean> => {
    try {
      return await request.post<boolean>(`/api/SystemSetting/${key}/reset`)
    } catch (error) {
      console.error(`Failed to reset setting ${key}:`, error)
      return false
    }
  },

  // 清空配置缓存
  clearCache: async (): Promise<void> => {
    try {
      await request.post('/api/SystemSetting/cache/clear')
    } catch (error) {
      console.error('Failed to clear cache:', error)
    }
  },

  // 获取需要重启的设置项
  getRestartRequiredSettings: async (): Promise<string[]> => {
    try {
      const response = await request.get<string[]>('/api/SystemSetting/restart-required')
      return Array.isArray(response) ? response : []
    } catch (error) {
      console.error('Failed to load restart required settings:', error)
      return []
    }
  },

  // 导出系统设置
  exportSettings: async (): Promise<SystemSetting[]> => {
    try {
      const response = await request.get<SystemSetting[]>('/api/SystemSetting/export')
      return Array.isArray(response) ? response : []
    } catch (error) {
      console.error('Failed to export settings:', error)
      return []
    }
  },

  // 验证配置值的有效性
  validateSettings: async (data: BatchUpdateSystemSettings): Promise<ValidationErrors> => {
    try {
      const response = await request.post<ValidationErrors>('/api/SystemSetting/validate', data)
      return response || {}
    } catch (error) {
      console.error('Failed to validate settings:', error)
      return {}
    }
  },

  // 测试邮件配置
  testEmailSettings: async (params: EmailTestParams): Promise<SettingTestResult | null> => {
    try {
      return await request.post<SettingTestResult>('/api/SystemSetting/test/email', params)
    } catch (error) {
      console.error('Failed to test email settings:', error)
      return null
    }
  },

  // 测试AI API配置
  testAISettings: async (params: APITestParams): Promise<SettingTestResult | null> => {
    try {
      return await request.post<SettingTestResult>('/api/SystemSetting/test/ai', params)
    } catch (error) {
      console.error('Failed to test AI settings:', error)
      return null
    }
  },

  // 测试数据库连接
  testDatabaseConnection: async (): Promise<SettingTestResult | null> => {
    try {
      return await request.post<SettingTestResult>('/api/SystemSetting/test/database')
    } catch (error) {
      console.error('Failed to test database connection:', error)
      return null
    }
  },

  // 获取系统状态 - 移除此方法因为后端不提供
  // getSystemStatus 已被移除

  // 获取设置变更历史
  getChangeHistory: async (settingKey?: string, page: number = 1, pageSize: number = 20): Promise<PageDto<SettingChangeHistory>> => {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        pageSize: pageSize.toString()
      })
      if (settingKey) {
        params.append('settingKey', settingKey)
      }
      const response = await request.get<PageDto<SettingChangeHistory>>(`/api/SystemSetting/history?${params}`)
      return response || { total: 0, items: [] }
    } catch (error) {
      console.error('Failed to load change history:', error)
      return { total: 0, items: [] }
    }
  },

  // 回滚设置到指定版本
  rollbackSetting: async (historyId: string): Promise<boolean> => {
    try {
      return await request.post<boolean>(`/api/SystemSetting/rollback/${historyId}`)
    } catch (error) {
      console.error(`Failed to rollback setting ${historyId}:`, error)
      return false
    }
  },

  // 重启系统 - 后端不提供此功能
  restartSystem: async (): Promise<boolean> => {
    console.warn('System restart is not available')
    return false
  }
}

// 统计数据接口
export interface ComprehensiveDashboard {
  userStats: {
    totalUsers: number
    activeUsers: number
    newUsersToday: number
    userGrowth: number
  }
  repositoryStats: {
    totalRepositories: number
    activeRepositories: number
    newRepositoriesToday: number
    repositoryGrowth: number
  }
  documentStats: {
    totalDocuments: number
    processedDocuments: number
    newDocumentsToday: number
    documentGrowth: number
  }
  systemStats: {
    cpuUsage: number
    memoryUsage: number
    diskUsage: number
    uptime: string
  }
  recentActivities: Array<{
    id: string
    type: string
    description: string
    user: string
    timestamp: string
  }>
  topRepositories: Array<{
    id: string
    name: string
    documentCount: number
    lastActivity: string
  }>
}

// 统计数据管理API
export const statsService = {
  // 获取综合仪表板数据
  getComprehensiveDashboard: async (): Promise<ComprehensiveDashboard> => {
    try {
      const response = await request.get<ComprehensiveDashboard>('/api/stats/dashboard')
      return response || {
        userStats: {
          totalUsers: 0,
          activeUsers: 0,
          newUsersToday: 0,
          userGrowth: 0
        },
        repositoryStats: {
          totalRepositories: 0,
          activeRepositories: 0,
          newRepositoriesToday: 0,
          repositoryGrowth: 0
        },
        documentStats: {
          totalDocuments: 0,
          processedDocuments: 0,
          newDocumentsToday: 0,
          documentGrowth: 0
        },
        systemStats: {
          cpuUsage: 0,
          memoryUsage: 0,
          diskUsage: 0,
          uptime: '0d 0h 0m'
        },
        recentActivities: [],
        topRepositories: []
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      return {
        userStats: {
          totalUsers: 0,
          activeUsers: 0,
          newUsersToday: 0,
          userGrowth: 0
        },
        repositoryStats: {
          totalRepositories: 0,
          activeRepositories: 0,
          newRepositoriesToday: 0,
          repositoryGrowth: 0
        },
        documentStats: {
          totalDocuments: 0,
          processedDocuments: 0,
          newDocumentsToday: 0,
          documentGrowth: 0
        },
        systemStats: {
          cpuUsage: 0,
          memoryUsage: 0,
          diskUsage: 0,
          uptime: '0d 0h 0m'
        },
        recentActivities: [],
        topRepositories: []
      }
    }
  }
}

// 上传图片文件（仅管理员可用）
export const uploadImage = async (file: File): Promise<{ url: string; fileName: string; message: string }> => {
  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await request.post('/api/FileStorage/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data.data
  } catch (error) {
    console.error('Upload image failed:', error)
    throw error
  }
}

// 批量上传图片（仅管理员可用）
export const uploadImages = async (files: File[]): Promise<{
  images: Array<{ url: string; fileName: string; originalName: string; size: number }>
  errors: string[]
  successCount: number
  errorCount: number
  message: string
}> => {
  try {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })

    const response = await request.post('/api/FileStorage/images', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data.data
  } catch (error) {
    console.error('Upload images failed:', error)
    throw error
  }
}

// 删除图片（仅管理员可用）
export const deleteImage = async (imageUrl: string): Promise<void> => {
  try {
    await request.delete('/api/FileStorage/image', {
      params: { imageUrl },
    })
  } catch (error) {
    console.error('Delete image failed:', error)
    throw error
  }
}