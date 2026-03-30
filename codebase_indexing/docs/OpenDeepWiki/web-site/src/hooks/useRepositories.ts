// 仓库相关的自定义Hook

import { useEffect, useCallback } from 'react'
import { useRepositoryStore } from '@/stores/repository.store'

export const useRepositories = (autoFetch = true) => {
  const {
    repositories,
    totalCount,
    currentPage,
    pageSize,
    keyword,
    loading,
    error,
    fetchRepositories,
    setKeyword,
    setCurrentPage,
    setPageSize,
  } = useRepositoryStore()

  // 初始加载
  useEffect(() => {
    if (autoFetch) {
      fetchRepositories()
    }
  }, [])

  // 搜索处理
  const handleSearch = useCallback((searchKeyword: string) => {
    setKeyword(searchKeyword)
    fetchRepositories({ keyword: searchKeyword, page: 1 })
  }, [setKeyword, fetchRepositories])

  // 分页处理
  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page)
    fetchRepositories({ page })
  }, [setCurrentPage, fetchRepositories])

  // 每页数量变化处理
  const handlePageSizeChange = useCallback((size: number) => {
    setPageSize(size)
    fetchRepositories({ pageSize: size, page: 1 })
  }, [setPageSize, fetchRepositories])

  // 刷新数据
  const refresh = useCallback(() => {
    fetchRepositories()
  }, [fetchRepositories])

  // 计算分页信息
  const totalPages = Math.ceil(totalCount / pageSize)
  const hasNextPage = currentPage < totalPages
  const hasPrevPage = currentPage > 1

  return {
    // 数据
    repositories,
    totalCount,
    currentPage,
    pageSize,
    keyword,
    loading,
    error,
    
    // 分页信息
    totalPages,
    hasNextPage,
    hasPrevPage,
    
    // 操作方法
    handleSearch,
    handlePageChange,
    handlePageSizeChange,
    refresh,
  }
}

export default useRepositories