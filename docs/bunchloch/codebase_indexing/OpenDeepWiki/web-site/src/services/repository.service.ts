// 仓库相关API服务

import { fetchService } from './fetch'
import type {
  RepositoryInfo,
  PageDto,
  RepositoryListParams,
  CreateGitRepositoryDto,
  UpdateRepositoryDto,
  ApiResponse
} from '@/types/repository'

class RepositoryService {
  private basePath = '/api/Repository'

  /**
   * 获取仓库列表
   */
  async getRepositoryList(params: RepositoryListParams): Promise<PageDto<RepositoryInfo>> {
    return fetchService.get<PageDto<RepositoryInfo>>(
      `${this.basePath}/RepositoryList`,
      { params }
    )
  }

  /**
   * 获取仓库详情
   */
  async getRepository(id: string): Promise<ApiResponse<RepositoryInfo>> {
    return fetchService.get<ApiResponse<RepositoryInfo>>(
      `${this.basePath}/Repository`,
      { params: { id } }
    )
  }

  /**
   * 根据组织名称和仓库名称获取仓库详情
   */
  async getRepositoryByOwnerAndName(
    owner: string,
    name: string,
    branch?: string
  ): Promise<RepositoryInfo> {
    return fetchService.get<RepositoryInfo>(
      `${this.basePath}/RepositoryByOwnerAndName`,
      { params: { owner, name, branch } }
    )
  }

  /**
   * 获取仓库文件目录结构
   */
  async getFiles(id: string): Promise<any[]> {
    return fetchService.get<any[]>(
      `${this.basePath}/Files`,
      { params: { id } }
    )
  }

  /**
   * 创建Git仓库
   */
  async createGitRepository(data: CreateGitRepositoryDto): Promise<RepositoryInfo> {
    return fetchService.post<RepositoryInfo>(
      `${this.basePath}/GitRepository`,
      data
    )
  }

  /**
   * 更新仓库信息
   */
  async updateRepository(id: string, data: UpdateRepositoryDto): Promise<RepositoryInfo> {
    return fetchService.put<RepositoryInfo>(
      `${this.basePath}/Repository`,
      data,
      { params: { id } }
    )
  }

  /**
   * 删除仓库
   */
  async deleteRepository(id: string): Promise<boolean> {
    return fetchService.delete<boolean>(
      `${this.basePath}/Repository`,
      { params: { id } }
    )
  }

  /**
   * 重新处理仓库
   */
  async resetRepository(id: string): Promise<boolean> {
    return fetchService.post<boolean>(
      `${this.basePath}/ResetRepository`,
      null,
      { params: { id } }
    )
  }
}

// 导出单例实例
export const repositoryService = new RepositoryService()

export default RepositoryService