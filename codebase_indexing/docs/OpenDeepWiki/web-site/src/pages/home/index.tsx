// 首页组件

import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Header } from '@/components/layout/Header'
import { SearchBar } from '@/components/SearchBar'
import { RepositoryCard } from '@/components/repository/RepositoryCard'
import { RepositoryForm, type RepositoryFormValues } from '@/components/repository/RepositoryForm/index'
import { Pagination } from '@/components/Pagination'
import { SponsorsSection } from '@/components/SponsorsSection'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useRepositories } from '@/hooks/useRepositories'
import { warehouseService } from '@/services/warehouse.service'
import { Loader2, RefreshCw, AlertCircle, Plus } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'

export const HomePage = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const {
    repositories,
    totalCount,
    currentPage,
    totalPages,
    loading,
    error,
    handleSearch,
    handlePageChange,
    refresh,
  } = useRepositories()

  const [searchValue, setSearchValue] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)

  const handleRepositoryClick = (repo: any) => {
    navigate(`/${repo.organizationName}/${repo.name}`)
  }

  const handleAddRepository = async (values: RepositoryFormValues) => {
    try {
      let response

      if (values.submitType === 'custom') {
        // 自定义仓库提交
        response = await warehouseService.customSubmitWarehouse({
          organization: values.organizationName!,
          repositoryName: values.repositoryName!,
          address: values.address!,
          branch: values.branch,
          gitUserName: values.enableGitAuth ? values.gitUserName : undefined,
          gitPassword: values.enableGitAuth ? values.gitPassword : undefined,
          email: values.enableGitAuth ? values.email : undefined
        })
      } else if (values.submitType === 'file') {
        // 文件上传
        if (values.uploadMethod === 'file' && values.fileUpload) {
          const formData = new FormData()
          formData.append('organization', values.organizationName || '')
          formData.append('repositoryName', values.repositoryName || '')
          formData.append('file', values.fileUpload)
          // 为文件上传添加Git认证参数
          if (values.enableGitAuth) {
            if (values.gitUserName) formData.append('gitUserName', values.gitUserName)
            if (values.gitPassword) formData.append('gitPassword', values.gitPassword)
            if (values.email) formData.append('email', values.email)
          }
          response = await warehouseService.uploadAndSubmitWarehouse(formData)
        } else {
          throw new Error('文件上传失败')
        }
      } else {
        // URL上传
        response = await warehouseService.submitWarehouse({
          address: values.address,
          branch: values.branch,
          gitUserName: values.enableGitAuth ? values.gitUserName : null,
          gitPassword: values.enableGitAuth ? values.gitPassword : null,
          email: values.enableGitAuth && values.email ? values.email : null
        })
      }

      if (response && response.code === 200) {
        toast.success(response.message)
        refresh()
        setShowAddModal(false)
      } else {
        toast.error(response?.message || t('repository.form.submitFailed'))
      }
    } catch (error: any) {
      toast.error(error.message || t('repository.form.submitFailed'))
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <section className="relative bg-gradient-to-b from-background via-background/95 to-background py-20 px-4">
        <div className="container mx-auto text-center">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
            {t('home.title')}
          </h1>
          <p className="text-xl text-muted-foreground mb-12 max-w-2xl mx-auto">
            {t('home.subtitle')}
          </p>

          {/* Search Bar */}
          <SearchBar
            value={searchValue}
            onChange={setSearchValue}
            onSearch={handleSearch}
            placeholder={t('home.search_placeholder')}
            size="lg"
            className="max-w-3xl"
          />

          {/* Quick Filters */}
          <div className="flex items-center justify-center gap-2 mt-6 flex-wrap">
            <Badge variant="secondary" className="cursor-pointer hover:bg-secondary/80">
              {t('common.search')}
            </Badge>
            <Badge variant="outline" className="cursor-pointer hover:bg-secondary/80">
              {t('home.repository_card.recommended')}
            </Badge>
            <Badge variant="outline" className="cursor-pointer hover:bg-secondary/80">
              {t('home.repository_card.recently_updated')}
            </Badge>
            <Badge variant="outline" className="cursor-pointer hover:bg-secondary/80">
              {t('home.repository_card.status.1')}
            </Badge>
            <Badge variant="outline" className="cursor-pointer hover:bg-secondary/80">
              {t('home.repository_card.status.2')}
            </Badge>
          </div>
        </div>
      </section>

      {/* Repository List Section */}
      <section className="container mx-auto px-4 py-12">
        {/* Section Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold mb-2">{t('home.repository_list.title')}</h2>
            <p className="text-muted-foreground">
              {t('common.total', { count: totalCount })}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              size="sm"
              onClick={() => setShowAddModal(true)}
              className="bg-primary hover:bg-primary/90"
            >
              <Plus className="h-4 w-4" />
              <span className="ml-2">{t('repository.form.addRepository')}</span>
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={refresh}
              disabled={loading}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
              <span className="ml-2">{t('common.refresh')}</span>
            </Button>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 mb-6 flex items-start">
            <AlertCircle className="h-5 w-5 text-destructive mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <p className="font-medium text-destructive">{t('common.failed')}</p>
              <p className="text-sm text-muted-foreground mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && repositories.length === 0 ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <span className="ml-3 text-muted-foreground">{t('common.loading')}</span>
          </div>
        ) : (
          <>
            {/* Repository Grid */}
            {repositories.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2 mb-12">
                {repositories.map((repo) => (
                  <RepositoryCard
                    key={repo.id}
                    repository={repo}
                    onClick={handleRepositoryClick}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-20">
                <p className="text-muted-foreground text-lg">{t('home.repository_list.empty')}</p>
                <p className="text-sm text-muted-foreground mt-2">
                  {t('home.repository_list.empty_description')}
                </p>
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={handlePageChange}
                className="mt-8"
              />
            )}
          </>
        )}
      </section>

      {/* Sponsors Section */}
      <SponsorsSection
        className="bg-muted/30"
      />

      {/* Footer */}
      <footer className="border-t">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between text-sm text-muted-foreground">
            <p>{t('footer.copyright', { year: new Date().getFullYear() })}</p>
            <div className="flex items-center gap-6 mt-4 md:mt-0">
              <a href="/privacy" className="hover:text-foreground transition-colors">
                {t('footer.privacy')}
              </a>
              <a href="/terms" className="hover:text-foreground transition-colors">
                {t('footer.terms')}
              </a>
              <a href="https://github.com/AIDotNet/OpenDeepWiki" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">
                {t('footer.github')}
              </a>
            </div>
          </div>
        </div>
      </footer>

      {/* Repository Form Modal */}
      <RepositoryForm
        open={showAddModal}
        onCancel={() => setShowAddModal(false)}
        onSubmit={handleAddRepository}
      />
    </div>
  )
}

export default HomePage
