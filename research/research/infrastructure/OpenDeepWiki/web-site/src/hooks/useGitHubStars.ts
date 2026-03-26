// GitHub Stars相关的自定义Hook

import { useState, useEffect, useCallback } from 'react'
import { githubService } from '@/services/github.service'

interface UseGitHubStarsOptions {
  owner: string
  repo: string
  refreshInterval?: number // 刷新间隔（毫秒）
  enableCache?: boolean // 是否启用缓存
  cacheExpiry?: number // 缓存过期时间（毫秒）
}

interface UseGitHubStarsReturn {
  starCount: number
  formattedStarCount: string
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
}

interface CacheItem {
  data: number
  timestamp: number
}

const CACHE_KEY_PREFIX = 'github_stars_'
const DEFAULT_CACHE_EXPIRY = 5 * 60 * 1000 // 5分钟

export const useGitHubStars = ({
  owner,
  repo,
  refreshInterval,
  enableCache = true,
  cacheExpiry = DEFAULT_CACHE_EXPIRY
}: UseGitHubStarsOptions): UseGitHubStarsReturn => {
  const [starCount, setStarCount] = useState<number>(0)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const cacheKey = `${CACHE_KEY_PREFIX}${owner}_${repo}`

  // 从缓存获取数据
  const getFromCache = useCallback((): number | null => {
    if (!enableCache) return null

    try {
      const cached = localStorage.getItem(cacheKey)
      if (!cached) return null

      const cacheItem: CacheItem = JSON.parse(cached)
      const now = Date.now()

      if (now - cacheItem.timestamp > cacheExpiry) {
        localStorage.removeItem(cacheKey)
        return null
      }

      return cacheItem.data
    } catch (error) {
      console.error('Failed to read from cache:', error)
      return null
    }
  }, [cacheKey, enableCache, cacheExpiry])

  // 保存到缓存
  const saveToCache = useCallback((data: number): void => {
    if (!enableCache) return

    try {
      const cacheItem: CacheItem = {
        data,
        timestamp: Date.now()
      }
      localStorage.setItem(cacheKey, JSON.stringify(cacheItem))
    } catch (error) {
      console.error('Failed to save to cache:', error)
    }
  }, [cacheKey, enableCache])

  // 获取star数据
  const fetchStarCount = useCallback(async (): Promise<void> => {
    try {
      setLoading(true)
      setError(null)

      // 先尝试从缓存获取
      const cachedData = getFromCache()
      if (cachedData !== null) {
        setStarCount(cachedData)
        setLoading(false)
        return
      }

      // 从API获取
      const count = await githubService.getStarCount(owner, repo)
      setStarCount(count)
      saveToCache(count)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch star count'
      setError(errorMessage)
      console.error('Error fetching GitHub stars:', err)
    } finally {
      setLoading(false)
    }
  }, [owner, repo, getFromCache, saveToCache])

  // 手动刷新
  const refresh = useCallback(async (): Promise<void> => {
    // 清除缓存并重新获取
    if (enableCache) {
      localStorage.removeItem(cacheKey)
    }
    await fetchStarCount()
  }, [fetchStarCount, enableCache, cacheKey])

  // 格式化star数量
  const formattedStarCount = githubService.formatStarCount(starCount)

  // 初始化和定时刷新
  useEffect(() => {
    fetchStarCount()

    // 设置定时刷新
    if (refreshInterval && refreshInterval > 0) {
      const interval = setInterval(() => {
        fetchStarCount()
      }, refreshInterval)

      return () => clearInterval(interval)
    }
  }, [fetchStarCount, refreshInterval])

  return {
    starCount,
    formattedStarCount,
    loading,
    error,
    refresh
  }
}

export default useGitHubStars