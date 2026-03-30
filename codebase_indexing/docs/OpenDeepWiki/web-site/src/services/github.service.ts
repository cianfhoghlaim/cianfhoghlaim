// GitHub API服务

export interface GitHubRepository {
  id: number
  name: string
  full_name: string
  description: string
  stargazers_count: number
  forks_count: number
  watchers_count: number
  language: string
  html_url: string
  created_at: string
  updated_at: string
  pushed_at: string
}

export interface GitHubApiError {
  message: string
  documentation_url?: string
}

class GitHubService {
  private readonly baseURL = 'https://api.github.com'

  /**
   * 获取GitHub仓库信息
   * @param owner 仓库所有者
   * @param repo 仓库名称
   * @returns 仓库信息
   */
  async getRepository(owner: string, repo: string): Promise<GitHubRepository> {
    try {
      const response = await fetch(`${this.baseURL}/repos/${owner}/${repo}`, {
        headers: {
          'Accept': 'application/vnd.github.v3+json',
          'User-Agent': 'OpenDeepWiki-App'
        }
      })

      if (!response.ok) {
        const errorData: GitHubApiError = await response.json()
        throw new Error(errorData.message || `GitHub API error: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to fetch GitHub repository:', error)
      throw error
    }
  }

  /**
   * 获取仓库的star数量
   * @param owner 仓库所有者
   * @param repo 仓库名称
   * @returns star数量
   */
  async getStarCount(owner: string, repo: string): Promise<number> {
    try {
      const repository = await this.getRepository(owner, repo)
      return repository.stargazers_count
    } catch (error) {
      console.error('Failed to fetch star count:', error)
      // 返回默认值，避免UI崩溃
      return 0
    }
  }

  /**
   * 格式化star数量显示
   * @param count star数量
   * @returns 格式化后的字符串
   */
  formatStarCount(count: number): string {
    if (count >= 1000000) {
      return `${(count / 1000000).toFixed(1)}M`
    } else if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}k`
    }
    return count.toString()
  }
}

export const githubService = new GitHubService()
export default githubService