// Repository types based on backend DTOs

export enum WarehouseStatus {
  Pending = 0,
  Processing = 1,
  Completed = 2,
  Canceled = 3,
  Unauthorized = 4,
  Failed = 99
}
export interface RepositoryInfo {
  id: string
  organizationName: string
  name: string
  description: string
  address: string
  type?: string
  branch?: string
  status: WarehouseStatus
  error?: string
  prompt?: string
  version?: string
  isEmbedded: boolean
  isRecommended: boolean
  createdAt: string
  stars:number
  forks:number
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

export interface PageDto<T> {
  total: number
  items: T[]
}

export interface RepositoryListParams {
  page: number
  pageSize: number
  keyword?: string
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}

export interface WarehouseListResponse {
  total: number
  items: RepositoryInfo[]
}