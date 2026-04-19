// 用户认证状态管理Store

import { create } from 'zustand'
import { authService } from '@/services/auth.service'
import type { LoginResponse, RegisterRequest } from '@/services/auth.service'

interface User {
  id: string
  username: string  // 后端返回的是 name
  email: string
  role?: string  // 后端返回的是单个 role 字符串
  avatar?: string
}

interface AuthState {
  // 状态
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
  
  // Actions
  login: (username: string, password: string) => Promise<boolean>
  register: (data: RegisterRequest) => Promise<boolean>
  logout: () => void
  refreshTokenHandle: () => Promise<boolean>
  getCurrentUser: () => Promise<void>
  setUser: (user: User | null) => void
  clearError: () => void
  initializeAuth: () => void
}

const getStoredToken = (): string | null => {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('userToken')
}

const getStoredRefreshToken = (): string | null => {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('refreshToken')
}

const getStoredUser = (): User | null => {
  if (typeof window === 'undefined') return null
  try {
    const userInfo = localStorage.getItem('userInfo')
    return userInfo ? JSON.parse(userInfo) : null
  } catch {
    return null
  }
}

const storeAuthData = (data: LoginResponse) => {
  if (typeof window === 'undefined') return
  
  if (data.token) {
    localStorage.setItem('userToken', data.token)
  }
  if (data.refreshToken) {
    localStorage.setItem('refreshToken', data.refreshToken)
  }
  if (data.user) {
    localStorage.setItem('userInfo', JSON.stringify(data.user))
  }
}

const clearAuthData = () => {
  if (typeof window === 'undefined') return
  
  localStorage.removeItem('userToken')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('userInfo')
  localStorage.removeItem('redirectPath')
}

export const useAuthStore = create<AuthState>((set, get) => ({
  // 初始状态
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  loading: false,
  error: null,

  // 登录
  login: async (username: string, password: string) => {
    set({ loading: true, error: null })
    
    try {
      const response = await authService.login(username, password)
      
      if (response.data.success) {
        storeAuthData(response.data)
        
        set({
          user: response.data.user || null,
          token: response.data.token || null,
          refreshToken: response.data.refreshToken || null,
          isAuthenticated: true,
          loading: false,
        })
        
        return true
      } else {
        set({
          error: response.data.errorMessage || '登录失败',
          loading: false,
        })
        return false
      }
    } catch (error: any) {
      set({
        error: error?.message || '登录过程中发生错误',
        loading: false,
      })
      return false
    }
  },

  // 注册
  register: async (data: RegisterRequest) => {
    set({ loading: true, error: null })
    
    try {
      const response = await authService.register(data)
      
      if (response.data.success) {
        storeAuthData(response.data)
        
        set({
          user: response.data.user || null,
          token: response.data.token || null,
          refreshToken: response.data.refreshToken || null,
          isAuthenticated: true,
          loading: false,
        })
        
        return true
      } else {
        set({
          error: response.data.errorMessage || '注册失败',
          loading: false,
        })
        return false
      }
    } catch (error: any) {
      set({
        error: error?.message || '注册过程中发生错误',
        loading: false,
      })
      return false
    }
  },

  // 登出
  logout: () => {
    clearAuthData()
    
    // 调用后端登出接口（可选，不影响前端状态）
    authService.logout().catch(console.error)
    
    set({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      error: null,
    })
  },

  // 刷新Token
  refreshTokenHandle: async () => {
    const { refreshToken } = get()
    if (!refreshToken) return false
    
    try {
      const response = await authService.refreshToken(refreshToken)
      
      if (response.success) {
        storeAuthData(response)
        
        set({
          user: response.user || null,
          token: response.token || null,
          refreshToken: response.refreshToken || refreshToken,
          isAuthenticated: true,
        })
        
        return true
      } else {
        get().logout()
        return false
      }
    } catch (error) {
      get().logout()
      return false
    }
  },

  // 获取当前用户信息
  getCurrentUser: async () => {
    if (!get().isAuthenticated) return
    
    try {
      const user = await authService.getCurrentUser()
      if (user) {
        localStorage.setItem('userInfo', JSON.stringify(user))
        set({ user })
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  },

  // 设置用户信息
  setUser: (user) => {
    set({ user })
    if (user) {
      localStorage.setItem('userInfo', JSON.stringify(user))
    }
  },

  // 清除错误
  clearError: () => {
    set({ error: null })
  },

  // 初始化认证状态
  initializeAuth: () => {
    const token = getStoredToken()
    const refreshToken = getStoredRefreshToken()
    const user = getStoredUser()
    
    if (token && user) {
      set({
        user,
        token,
        refreshToken,
        isAuthenticated: true,
      })
    }
  },
}))

// 自动初始化认证状态
if (typeof window !== 'undefined') {
  useAuthStore.getState().initializeAuth()
}

export default useAuthStore