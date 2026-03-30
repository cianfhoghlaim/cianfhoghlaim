// 请求工具封装，基于现有的 fetch service
import { fetchService } from '@/services/fetch'

// 获取认证token
const getAuthToken = () => {
  return localStorage.getItem('auth-token') || ''
}

// 请求拦截器 - 添加认证头
const requestInterceptor = (headers: HeadersInit = {}): HeadersInit => {
  const token = getAuthToken()
  return {
    ...headers,
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  }
}

// 封装请求方法
export const request = {
  get: async <T = any>(url: string, options?: { params?: Record<string, any>; [key: string]: any }): Promise<T> => {
    return fetchService.get<T>(url, {
      ...options,
      headers: requestInterceptor(options?.headers)
    })
  },

  post: async <T = any>(url: string, data?: any, options?: { params?: Record<string, any>; [key: string]: any }): Promise<T> => {
    return fetchService.post<T>(url, data, {
      ...options,
      headers: requestInterceptor(options?.headers)
    })
  },

  put: async <T = any>(url: string, data?: any, options?: { params?: Record<string, any>; [key: string]: any }): Promise<T> => {
    return fetchService.put<T>(url, data, {
      ...options,
      headers: requestInterceptor(options?.headers)
    })
  },

  delete: async <T = any>(url: string, options?: { params?: Record<string, any>; [key: string]: any }): Promise<T> => {
    return fetchService.delete<T>(url, {
      ...options,
      headers: requestInterceptor(options?.headers)
    })
  }
}

export default request