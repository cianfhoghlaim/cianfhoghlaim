// 仓库状态管理Store

import { create } from 'zustand'
import { warehouseService } from '@/services/warehouse.service'
import type { RepositoryInfo,  RepositoryListParams } from '@/types/repository'

interface RepositoryState {
  // 状态
  repositories: RepositoryInfo[]
  totalCount: number
  currentPage: number
  pageSize: number
  keyword: string
  loading: boolean
  error: string | null
  selectedRepository: RepositoryInfo | null
  
  // Actions
  fetchRepositories: (params?: Partial<RepositoryListParams>) => Promise<void>
  setSelectedRepository: (repository: RepositoryInfo | null) => void
  setKeyword: (keyword: string) => void
  setCurrentPage: (page: number) => void
  setPageSize: (size: number) => void
  resetState: () => void
}

const initialState = {
  repositories: [],
  totalCount: 0,
  currentPage: 1,
  pageSize: 12,
  keyword: '',
  loading: false,
  error: null,
  selectedRepository: null,
}

export const useRepositoryStore = create<RepositoryState>((set, get) => ({
  ...initialState,

  fetchRepositories: async (params?: Partial<RepositoryListParams>) => {
    const { currentPage, pageSize, keyword } = get()

    set({ loading: true, error: null })

    try {
      // 使用warehouse service获取数据
      const response = await warehouseService.getWarehouseList(
        params?.page ?? currentPage,
        params?.pageSize ?? pageSize,
        params?.keyword ?? keyword
      )

      // 兼容WarehouseListResponse结构
      set({
        repositories: response.items || [],
        totalCount: response.total || 0,
        currentPage: params?.page ?? currentPage,
        pageSize: params?.pageSize ?? pageSize,
        keyword: params?.keyword ?? keyword,
        loading: false,
      })
    } catch (error: any) {
      set({
        loading: false,
        error: error?.message || '获取仓库列表失败',
      })
    }
  },

  setSelectedRepository: (repository) => {
    set({ selectedRepository: repository })
  },

  setKeyword: (keyword) => {
    set({ keyword })
  },

  setCurrentPage: (page) => {
    set({ currentPage: page })
  },

  setPageSize: (size) => {
    set({ pageSize: size })
  },

  resetState: () => {
    set(initialState)
  },
}))

export default useRepositoryStore