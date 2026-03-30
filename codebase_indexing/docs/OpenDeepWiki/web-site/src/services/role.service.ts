// 角色相关API服务

import { fetchService } from './fetch'
import type { PageDto } from '@/types/repository'

export interface RoleInfo {
  id: string
  name: string
  description?: string
  isActive: boolean
  isSystemRole: boolean
  createdAt: string
  updatedAt: string
  userCount: number
  warehousePermissionCount: number
}

export interface RoleListParams {
  page?: number
  pageSize?: number
  keyword?: string
  isActive?: boolean
}

export interface CreateRoleDto {
  name: string
  description?: string
  isActive: boolean
}

export interface UpdateRoleDto {
  name: string
  description?: string
  isActive: boolean
}

export interface UserInfo {
  id: string
  name: string
  email: string
  avatar?: string
  role?: string
  createdAt: string
  updatedAt?: string
}

export interface RoleDetailDto extends RoleInfo {
  users?: UserInfo[]
  warehousePermissions?: WarehousePermissionDetailDto[]
}

export interface WarehousePermissionDetailDto {
  warehouseId: string
  isReadOnly: boolean
  isWrite: boolean
  isDelete: boolean
  organizationName: string
  warehouseName: string
  warehouseDescription: string
}

class RoleService {
  private basePath = '/api/Role'

  /**
   * 获取角色列表
   */
  async getRoleList(params: RoleListParams = {}): Promise<PageDto<RoleInfo>> {
    const { page = 1, pageSize = 20, keyword, isActive } = params
    const query: Record<string, string | number | boolean> = { page, pageSize }

    if (keyword && keyword.trim()) {
      query.keyword = keyword.trim()
    }

    if (typeof isActive === 'boolean') {
      query.isActive = isActive
    }

    return fetchService.get<PageDto<RoleInfo>>(`${this.basePath}/RoleList`, {
      params: query,
    })
  }

  /**
   * 获取角色详情
   */
  async getRoleDetail(id: string): Promise<RoleDetailDto> {
    return fetchService.get<RoleDetailDto>(`${this.basePath}/RoleDetail`, {
      params: { id }
    })
  }

  /**
   * 获取全部角色（用于下拉选择）
   */
  async getAllRoles(): Promise<RoleInfo[]> {
    return fetchService.get<RoleInfo[]>(`${this.basePath}/AllRoles`)
  }

  /**
   * 创建角色
   */
  async createRole(data: CreateRoleDto): Promise<RoleInfo> {
    return fetchService.post<RoleInfo>(`${this.basePath}/CreateRole`, data)
  }

  /**
   * 更新角色
   */
  async updateRole(id: string, data: UpdateRoleDto): Promise<RoleInfo> {
    return fetchService.post<RoleInfo>(`${this.basePath}/UpdateRole`, data, {
      params: { id }
    })
  }

  /**
   * 删除角色
   */
  async deleteRole(id: string): Promise<boolean> {
    return fetchService.post<boolean>(`${this.basePath}/DeleteRole`, {}, {
      params: { id }
    })
  }

  /**
   * 批量更新角色状态
   */
  async batchUpdateRoleStatus(ids: string[], isActive: boolean): Promise<boolean> {
    return fetchService.post<boolean>(`${this.basePath}/BatchUpdateRoleStatus?isActive=${isActive}`, ids)
  }
}

export const roleService = new RoleService()
export const getRoleList = roleService.getRoleList.bind(roleService)
export default RoleService
