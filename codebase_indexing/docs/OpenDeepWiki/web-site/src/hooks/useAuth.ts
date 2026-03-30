// 认证相关的自定义Hook

import { useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth.store'

export const useAuth = () => {
  const {
    user,
    token,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    refreshToken,
    getCurrentUser,
    clearError,
    initializeAuth,
  } = useAuthStore()

  const navigate = useNavigate()

  // 登录处理
  const handleLogin = useCallback(async (username: string, password: string) => {
    const success = await login(username, password)
    
    if (success) {
      // 检查是否有重定向路径
      const redirectPath = localStorage.getItem('redirectPath') || '/'
      localStorage.removeItem('redirectPath')
      navigate(redirectPath)
    }
    
    return success
  }, [login, navigate])

  // 注册处理
  const handleRegister = useCallback(async (data: { username: string; email: string; password: string; confirmPassword: string }) => {
    const success = await register(data)
    
    if (success) {
      // 注册成功后自动跳转
      const redirectPath = localStorage.getItem('redirectPath') || '/'
      localStorage.removeItem('redirectPath')
      navigate(redirectPath)
    }
    
    return success
  }, [register, navigate])

  // 登出处理
  const handleLogout = useCallback(() => {
    logout()
    navigate('/login')
  }, [logout, navigate])

  // 检查用户权限
  const hasRole = useCallback((role: string): boolean => {
    // 后端返回的是单个 role 字符串，可能包含多个角色用逗号分隔
    const userRoles = user?.role?.split(',').map(r => r.trim()) ?? []
    return userRoles.includes(role)
  }, [user])

  // 检查是否为管理员
  const isAdmin = useCallback((): boolean => {
    return hasRole('Admin') || hasRole('admin')
  }, [hasRole])

  // 自动刷新Token
  const autoRefreshToken = useCallback(async () => {
    if (isAuthenticated && token) {
      try {
        // 检查Token是否快要过期（这里简化处理，实际可以解析JWT）
        // const success = await refreshTokenHandle()
        // if (!success) {
        //   handleLogout()
        // }
      } catch (error) {
        console.error('Token refresh failed:', error)
        handleLogout()
      }
    }
  }, [isAuthenticated, token, refreshToken, handleLogout])

  // 初始化认证状态
  useEffect(() => {
    initializeAuth()
  }, [initializeAuth])

  // 定期刷新Token (每30分钟)
  useEffect(() => {
    if (isAuthenticated) {
      const interval = setInterval(autoRefreshToken, 30 * 60 * 1000)
      return () => clearInterval(interval)
    }
  }, [isAuthenticated, autoRefreshToken])

  return {
    // 状态
    user,
    token,
    isAuthenticated,
    loading,
    error,
    
    // 方法
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    refreshToken,
    getCurrentUser,
    clearError,
    hasRole,
    isAdmin,
  }
}

// 用于保护需要认证的路由的Hook
export const useRequireAuth = (redirectTo: string = '/login') => {
  const { isAuthenticated, loading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      // 保存当前路径以便登录后重定向
      localStorage.setItem('redirectPath', window.location.pathname)
      navigate(redirectTo)
    }
  }, [isAuthenticated, loading, navigate, redirectTo])

  return { isAuthenticated, loading }
}

// 第三方登录Hook
export const useThirdPartyAuth = () => {
  const navigate = useNavigate()

  const handleThirdPartyLogin = useCallback((providerName: string, clientId: string) => {
    // 记录登录类型
    localStorage.setItem('oauthProvider', providerName.toLowerCase())
    
    // 根据提供商名称构建OAuth URL
    if (providerName.toLowerCase() === 'github') {
      const redirectUri = `${window.location.origin}/auth/callback`
      window.location.href = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}`
    } else if (providerName.toLowerCase() === 'google') {
      const redirectUri = `${window.location.origin}/auth/callback`
      const scope = 'openid email profile'
      window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}&response_type=code`
    }
  }, [])

  const handleOAuthCallback = useCallback(async (code: string, state?: string) => {
    try {
      // 这里应该调用后端的OAuth回调处理
      // const result = await authService.oauthCallback(code, state)
      // 处理登录结果...
      
      // 暂时跳转到首页
      navigate('/')
    } catch (error) {
      console.error('OAuth callback failed:', error)
      navigate('/login?error=oauth_failed')
    }
  }, [navigate])

  return {
    handleThirdPartyLogin,
    handleOAuthCallback,
  }
}

export default useAuth