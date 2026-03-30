// 认证相关API服务

import { fetchService } from './fetch'

// 登录接口参数
export interface LoginRequest {
  username: string
  password: string
}

// 登录响应（匹配后端 LoginDto 结构）
export interface LoginResponse {
  success: boolean
  token?: string
  refreshToken?: string
  user?: {
    id: string
    username: string  // 后端返回的是 name 而不是 username
    email: string
    roleName: string  // 后端返回的是单个 role 字符串
    avatar?: string
  }
  errorMessage?: string
}

// 第三方登录提供商
export interface ThirdPartyLoginProvider {
  name: string
  icon: string
  clientId: string
  redirectUri: string
}

// 第三方登录响应
export interface ThirdPartyLoginResponse {
  code: number
  data?: ThirdPartyLoginProvider[]
  message?: string
}

// 注册接口参数
export interface RegisterRequest {
  username: string
  email: string
  password: string
  confirmPassword: string
}

class AuthService {
  private basePath = '/api/Auth'

  /**
   * 用户登录
   */
  async login(username: string, password: string): Promise<{ data: LoginResponse }> {
    const response = await fetchService.post<any>(`${this.basePath}/Login`, {
      username,
      password,
    })

    // 处理后端返回的嵌套数据结构并转换字段名
    if (response.code === 200 && response.data) {
      const loginData = response.data
      return {
        data: {
          success: loginData.success || loginData.Success,
          token: loginData.token || loginData.Token,
          refreshToken: loginData.refreshToken || loginData.RefreshToken,
          user: loginData.user || loginData.User,
          errorMessage: loginData.errorMessage || loginData.ErrorMessage
        }
      }
    }

    // 兼容直接返回的格式
    return { data: response }
  }

  /**
   * 用户注册
   */
  async register(data: RegisterRequest): Promise<{ data: LoginResponse }> {
    const response = await fetchService.post<any>(`${this.basePath}/Register`, {
      userName: data.username,
      email: data.email,
      password: data.password
    })

    // 处理后端返回的嵌套数据结构并转换字段名
    if (response.code === 200 && response.data) {
      const loginData = response.data
      return {
        data: {
          success: loginData.success || loginData.Success,
          token: loginData.token || loginData.Token,
          refreshToken: loginData.refreshToken || loginData.RefreshToken,
          user: loginData.user || loginData.User,
          errorMessage: loginData.errorMessage || loginData.ErrorMessage
        }
      }
    }

    // 兼容直接返回的格式
    return { data: response }
  }

  /**
   * 获取支持的第三方登录方式
   */
  async getSupportedThirdPartyLogins(): Promise<ThirdPartyLoginResponse> {
    const response = await fetchService.get<any>(`${this.basePath}/GetSupportedThirdPartyLogins`)

    // 如果响应被包装，则解包
    if (response.code !== undefined && response.data !== undefined) {
      return response
    }

    // 否则构造标准响应格式
    return { code: 200, data: response }
  }

  /**
   * 刷新Token
   */
  async refreshToken(refreshToken: string): Promise<LoginResponse> {
    return fetchService.post<LoginResponse>(`${this.basePath}/refresh-token`, {
      refreshToken,
    })
  }

  /**
   * 用户登出
   */
  async logout(): Promise<void> {
    return fetchService.post<void>(`${this.basePath}/logout`)
  }

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<LoginResponse['user']> {
    return fetchService.get<LoginResponse['user']>(`${this.basePath}/me`)
  }

  /**
   * OAuth回调处理
   */
  async oauthCallback(code: string, state?: string): Promise<LoginResponse> {
    return fetchService.post<LoginResponse>(`${this.basePath}/oauth/callback`, {
      code,
      state,
    })
  }

  /**
   * 忘记密码
   */
  async forgotPassword(email: string): Promise<{ success: boolean; message?: string }> {
    return fetchService.post<{ success: boolean; message?: string }>(`${this.basePath}/forgot-password`, {
      email,
    })
  }

  /**
   * 重置密码
   */
  async resetPassword(token: string, password: string): Promise<{ success: boolean; message?: string }> {
    return fetchService.post<{ success: boolean; message?: string }>(`${this.basePath}/reset-password`, {
      token,
      password,
    })
  }
}

// 导出单例实例
export const authService = new AuthService()

// 导出便捷方法（保持与原版兼容）
export const login = authService.login.bind(authService)
export const getSupportedThirdPartyLogins = authService.getSupportedThirdPartyLogins.bind(authService)

export default AuthService