import { fetchService } from './fetch'

export interface DocumentResponse {
  content: string
  title: string
  description: string
  fileSource: Array<{
    name: string
    address: string
    url: string
  }>
  address: string
  branch: string
  lastUpdate: string
  documentCatalogId: string
  currentLanguage: string
}

class DocumentService {
  // 获取文档内容 - 使用 GetDocumentByIdAsync (映射为 /DocumentById)
  async getDocument(
    owner: string,
    repo: string,
    path: string,
    branch?: string,
    languageCode?: string
  ): Promise<DocumentResponse> {
    try {
      const params = new URLSearchParams({
        owner,
        name: repo,
        path  // 不要再次编码，因为 URLSearchParams 会自动编码
      })

      if (branch) {
        params.append('branch', branch)
      }

      if (languageCode) {
        params.append('languageCode', languageCode)
      }

      const response = await fetchService.get<DocumentResponse>(
        `/api/DocumentCatalog/DocumentById?${params.toString()}`
      )
      return response
    } catch (error) {
      console.error('Failed to fetch document:', error)
      throw error
    }
  }

  // 获取文档树
  async getDocumentTree(owner: string, repo: string, branch?: string) {
    try {
      const params = branch ? { branch } : {}
      const response = await fetchService.get(
        `/api/repositories/${owner}/${repo}/tree`,
        { params }
      )
      return response
    } catch (error) {
      console.error('Failed to fetch document tree:', error)
      throw error
    }
  }
}

export const documentService = new DocumentService()