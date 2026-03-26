// 管理员控制台布局组件

import React, { useState } from 'react'
import { Outlet, Link, useLocation, Navigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { cn } from '@/lib/utils'
import { useAuth } from '@/hooks/useAuth'
import { usePermissions } from '@/hooks/usePermissions'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { ThemeToggle } from '@/components/theme-toggle'
import { LanguageSwitcher } from '@/components/LanguageSwitcher'
import {
  BarChart3,
  Users,
  Shield,
  Database,
  Settings,
  Menu,
  X,
  ChevronLeft,
  Home
} from 'lucide-react'

interface AdminLayoutProps {
  children?: React.ReactNode
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const { t } = useTranslation('admin')
  const location = useLocation()
  const { isAuthenticated } = useAuth()
  const { canAccessAdmin } = usePermissions()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  // 如果未登录或不是管理员，重定向
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (!canAccessAdmin()) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center space-y-4">
          <Shield className="h-16 w-16 text-muted-foreground mx-auto" />
          <h1 className="text-2xl font-bold">{t('messages.no_permission')}</h1>
          <Button asChild>
            <Link to="/">
              <Home className="mr-2 h-4 w-4" />
              {t('nav.back_to_home')}
            </Link>
          </Button>
        </div>
      </div>
    )
  }

  const navigation = [
    {
      name: t('nav.dashboard'),
      href: '/admin',
      icon: BarChart3,
      current: location.pathname === '/admin' || location.pathname === '/admin/'
    },
    {
      name: t('nav.users'),
      href: '/admin/users',
      icon: Users,
      current: location.pathname.startsWith('/admin/users')
    },
    {
      name: t('nav.roles'),
      href: '/admin/roles',
      icon: Shield,
      current: location.pathname.startsWith('/admin/roles')
    },
    {
      name: t('nav.repositories'),
      href: '/admin/repositories',
      icon: Database,
      current: location.pathname.startsWith('/admin/repositories')
    },
    {
      name: t('nav.settings'),
      href: '/admin/settings',
      icon: Settings,
      current: location.pathname.startsWith('/admin/settings')
    }
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* 顶部导航栏 */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex h-16 items-center px-4 lg:px-6">
          <div className="flex items-center gap-4">
            {/* 侧边栏切换按钮 */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="h-8 w-8"
            >
              {sidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </Button>

            {/* 标题 */}
            <div className="flex items-center gap-2">
              <Shield className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-semibold">{t('title')}</h1>
            </div>
          </div>

          <div className="flex-1" />

          {/* 右侧操作区 */}
          <div className="flex items-center gap-2">
            <LanguageSwitcher variant="ghost" size="sm" />
            <ThemeToggle />
            <Button variant="ghost" size="sm" asChild>
              <Link to="/">
                <ChevronLeft className="mr-2 h-4 w-4" />
                {t('nav.back_to_website')}
              </Link>
            </Button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* 侧边栏 */}
        <aside
          className={cn(
            "border-r bg-muted/10 transition-all duration-300 ease-in-out",
            sidebarOpen ? "w-64" : "w-0 overflow-hidden"
          )}
        >
          <div className="h-[calc(100vh-4rem)]">
            <ScrollArea className="h-full py-6">
              <nav className="space-y-2 px-4">
                {navigation.map((item) => {
                  const Icon = item.icon
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={cn(
                        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                        item.current
                          ? "bg-primary text-primary-foreground"
                          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      {item.name}
                    </Link>
                  )
                })}
              </nav>
            </ScrollArea>
          </div>
        </aside>

        {/* 主内容区 */}
        <main className="flex-1 overflow-hidden">
          <div className="h-[calc(100vh-4rem)] overflow-auto">
            <div className="container mx-auto p-6">
              {children || <Outlet />}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default AdminLayout