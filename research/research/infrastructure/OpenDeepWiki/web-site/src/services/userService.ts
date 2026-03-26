// 用户服务
import { fetchService } from './fetch'

export interface UserProfile {
  id: string
  username: string
  email: string
  avatar: string
  bio?: string
  location?: string
  website?: string
  company?: string
  createdAt: string
  updatedAt?: string
  lastLoginAt?: string
}

export interface UpdateProfileData {
  username?: string
  email?: string
  bio?: string
  location?: string
  website?: string
  company?: string
}

export interface ChangePasswordData {
  oldPassword: string
  newPassword: string
}

class UserService {
  /**
   * 获取当前用户个人资料
   */
  async getProfile(): Promise<UserProfile> {
    return fetchService.get<UserProfile>('/api/UserProfile')
  }

  /**
   * 更新用户个人资料
   */
  async updateProfile(data: UpdateProfileData): Promise<UserProfile> {
    return fetchService.put<UserProfile>('/api/UserProfile', data)
  }

  /**
   * 上传头像
   */
  async uploadAvatar(formData: FormData): Promise<{ avatarUrl: string; message: string }> {
    return fetchService.post<{ avatarUrl: string; message: string }>(
      '/api/UserProfile/avatar',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
  }

  /**
   * 删除头像
   */
  async deleteAvatar(): Promise<void> {
    await fetchService.delete('/api/UserProfile/avatar')
  }

  /**
   * 修改密码
   */
  async changePassword(data: ChangePasswordData): Promise<void> {
    await fetchService.post('/api/UserProfile/password', data)
  }
}

export const userService = new UserService()