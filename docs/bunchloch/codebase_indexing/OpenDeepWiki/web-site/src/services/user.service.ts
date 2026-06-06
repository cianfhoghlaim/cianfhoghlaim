// 用户相关API服务

import { fetchService } from './fetch'
import type { PageDto } from '@/types/repository'

// 用户信息接口
export interface UserInfo {
  id: string
  username: string
  name: string
  email: string
  avatar?: string
  roles?: string[]
  createdAt?: string
  updatedAt?: string
}

// 更新用户资料的请求参数
export interface UpdateProfileRequest {
  name: string
  email: string
  avatar?: string
}

// 修改密码的请求参数
export interface ChangePasswordRequest {
  currentPassword: string
  newPassword: string
}

// API响应通用格式
export interface ApiResponse<T> {
  code: number
  data: T
  message?: string
  success?: boolean
}

export interface AdminUserInfo {
  id: string
  name: string
  email: string
  role: string
  avatar?: string
  createdAt: string
  updatedAt?: string
  lastLoginAt?: string
  lastLoginIp?: string
}

export interface UserListParams {
  page?: number
  pageSize?: number
  keyword?: string
}

class UserService {
  private basePath = '/api/User'

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<ApiResponse<UserInfo>> {
    const response = await fetchService.get<ApiResponse<UserInfo>>(`${this.basePath}/profile`)
    return response
  }

  /**
   * 更新用户资料
   */
  async updateCurrentUserProfile(data: UpdateProfileRequest): Promise<ApiResponse<UserInfo>> {
    const response = await fetchService.put<ApiResponse<UserInfo>>(`${this.basePath}/profile`, data)
    return response
  }

  /**
   * 验证当前密码
   */
  async verifyPassword(password: string): Promise<ApiResponse<boolean>> {
    const response = await fetchService.post<ApiResponse<boolean>>(`${this.basePath}/verify-password`, {
      password
    })
    return response
  }

  /**
   * 修改密码
   */
  async changePassword(data: ChangePasswordRequest): Promise<ApiResponse<boolean>> {
    const response = await fetchService.put<ApiResponse<boolean>>(`${this.basePath}/change-password`, data)
    return response
  }

  /**
   * 获取用户列表（管理员）
   */
  async getUserList(params: UserListParams = {}): Promise<PageDto<AdminUserInfo>> {
    const { page = 1, pageSize = 20, keyword } = params
    const query: Record<string, string | number> = { page, pageSize }

    if (keyword && keyword.trim()) {
      query.keyword = keyword.trim()
    }

    return fetchService.get<PageDto<AdminUserInfo>>(`${this.basePath}/UserList`, {
      params: query,
    })
  }

  /**
   * 上传头像
   */
  async uploadAvatar(file: File): Promise<ApiResponse<string>> {
    const formData = new FormData()
    formData.append('avatar', file)
    
    const response = await fetchService.post<ApiResponse<string>>(`${this.basePath}/upload-avatar`, formData, {
      headers: {
        // 不设置 Content-Type，让浏览器自动设置
      }
    })
    return response
  }

  /**
   * 删除头像
   */
  async removeAvatar(): Promise<ApiResponse<boolean>> {
    const response = await fetchService.delete<ApiResponse<boolean>>(`${this.basePath}/avatar`)
    return response
  }

  /**
   * 获取用户设置
   */
  async getUserSettings(): Promise<ApiResponse<Record<string, any>>> {
    const response = await fetchService.get<ApiResponse<Record<string, any>>>(`${this.basePath}/settings`)
    return response
  }

  /**
   * 更新用户设置
   */
  async updateUserSettings(settings: Record<string, any>): Promise<ApiResponse<boolean>> {
    const response = await fetchService.put<ApiResponse<boolean>>(`${this.basePath}/settings`, settings)
    return response
  }

  /**
   * 获取账户统计信息
   */
  async getAccountStats(): Promise<ApiResponse<{
    repositoriesCount: number
    documentsCount: number
    lastLoginAt: string
    createdAt: string
  }>> {
    const response = await fetchService.get<ApiResponse<{
      repositoriesCount: number
      documentsCount: number
      lastLoginAt: string
      createdAt: string
    }>>(`${this.basePath}/stats`)
    return response
  }
}

// 导出单例实例
export const userService = new UserService()

// 导出便捷方法（保持与原版兼容）
export const getCurrentUser = userService.getCurrentUser.bind(userService)
export const updateCurrentUserProfile = userService.updateCurrentUserProfile.bind(userService)
export const verifyPassword = userService.verifyPassword.bind(userService)
export const changePassword = userService.changePassword.bind(userService)
export const uploadAvatar = userService.uploadAvatar.bind(userService)
export const getUserSettings = userService.getUserSettings.bind(userService)
export const updateUserSettings = userService.updateUserSettings.bind(userService)
export const getUserList = userService.getUserList.bind(userService)

// 添加 removeAvatar 方法
export const removeAvatar = async (): Promise<ApiResponse<boolean>> => {
  return userService.removeAvatar()
}

export default UserService