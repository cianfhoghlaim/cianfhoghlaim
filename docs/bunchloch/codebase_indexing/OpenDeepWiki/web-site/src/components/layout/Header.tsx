// 页面头部组件

import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { LanguageSwitcher } from '@/components/LanguageSwitcher'
import { ThemeToggle } from '@/components/theme-toggle'
import { useAuth } from '@/hooks/useAuth'
import { usePermissions } from '@/hooks/usePermissions'
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Github,
  Star,
  Settings,
  LogOut,
  User,
  Menu,
  X,
  Shield
} from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'
import { useGitHubStars } from '@/hooks/useGitHubStars'
import { 
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

interface HeaderProps {
  className?: string
}

export const Header: React.FC<HeaderProps> = ({ className }) => {
  const { t } = useTranslation()
  const { user, isAuthenticated, logout } = useAuth()
  const { canAccessAdmin } = usePermissions()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  
  // 获取GitHub star数据
  const { formattedStarCount, loading: starLoading, error: starError } = useGitHubStars({
    owner: 'AIDotNet',
    repo: 'OpenDeepWiki',
    refreshInterval: 10 * 60 * 1000, // 10分钟刷新一次
    enableCache: true,
    cacheExpiry: 5 * 60 * 1000 // 缓存5分钟
  })

  return (
    <header className={cn('sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60', className)}>
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo and Brand */}
          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center space-x-2">
              <img 
                src="/favicon.png" 
                alt="OpenDeepWiki Logo" 
                className="h-8 w-8 rounded-full"
              />
              <span className="font-bold text-xl hidden sm:inline-block">OpenDeepWiki</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <Link to="/" className="text-sm font-medium hover:text-primary transition-colors">
              {t('nav.home')}
            </Link>
            <Link to="/repositories" className="text-sm font-medium hover:text-primary transition-colors">
              {t('nav.repositories')}
            </Link>
            <Link 
              target="_blank"
              rel="noopener noreferrer"
              to="https://token-ai.feishu.cn/wiki/space/7534927001112150018?ccm_open_type=lark_wiki_spaceLink&open_tab_from=wiki_home" className="text-sm font-medium hover:text-primary transition-colors">
              {t('nav.docs')}
            </Link>
            <Link to="/about" className="text-sm font-medium hover:text-primary transition-colors">
              {t('nav.about')}
            </Link>
          </nav>

          {/* Right Side Actions */}
          <div className="flex items-center gap-4">
            {/* GitHub Star Button */}
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="outline"
                    size="sm"
                    className="hidden sm:flex items-center gap-2"
                    asChild
                  >
                    <a href="https://github.com/AIDotNet/OpenDeepWiki" target="_blank" rel="noopener noreferrer">
                      <Github className="h-4 w-4" />
                      <span>Star</span>
                      <span className={cn(
                        "ml-1 rounded bg-muted px-1.5 py-0.5 text-xs",
                        starError && "text-muted-foreground"
                      )}>
                        {starLoading ? '...' : starError ? '2.1k' : formattedStarCount}
                      </span>
                    </a>
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>
                    {starError 
                      ? `无法获取最新star数据: ${starError}` 
                      : starLoading 
                        ? '正在获取star数据...' 
                        : `当前star数: ${formattedStarCount}`
                    }
                  </p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>

            {/* Language Selector */}
            <LanguageSwitcher variant="ghost" size="sm" className="hidden sm:flex" />

            {/* Theme Toggle */}
            <ThemeToggle />

            {/* User Menu */}
            {isAuthenticated ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback>{user?.username?.[0] || user?.email?.[0] || 'U'}</AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end">
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium">{user?.username || 'User'}</p>
                      <p className="text-xs text-muted-foreground">{user?.email || ''}</p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link to="/profile">
                      <User className="mr-2 h-4 w-4" />
                      <span>{t('nav.profile')}</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/settings">
                      <Settings className="mr-2 h-4 w-4" />
                      <span>{t('nav.settings')}</span>
                    </Link>
                  </DropdownMenuItem>
                  {canAccessAdmin() && (
                    <>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem asChild>
                        <div onClick={()=>{
                          window.location.href = '/admin'
                        }}>
                          <Shield className="mr-2 h-4 w-4" />
                          <span>{t('nav.admin_console')}</span>
                        </div>
                      </DropdownMenuItem>
                    </>
                  )}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="text-red-600" onClick={logout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>{t('nav.logout')}</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" asChild>
                  <Link to="/login">{t('nav.login')}</Link>
                </Button>
                <Button size="sm" asChild>
                  <Link to="/register">{t('nav.register')}</Link>
                </Button>
              </div>
            )}

            {/* Mobile Menu Toggle */}
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="md:hidden py-4 border-t">
            <div className="flex flex-col space-y-3">
              <Link to="/" className="text-sm font-medium hover:text-primary transition-colors">
                {t('nav.home')}
              </Link>
              <Link to="/repositories" className="text-sm font-medium hover:text-primary transition-colors">
                {t('nav.repositories')}
              </Link>
              <Link 
                target="_blank"
                rel="noopener noreferrer"
                to="https://token-ai.feishu.cn/wiki/space/7534927001112150018?ccm_open_type=lark_wiki_spaceLink&open_tab_from=wiki_home" className="text-sm font-medium hover:text-primary transition-colors">
                {t('nav.docs')}
              </Link>
              <Link to="/about" className="text-sm font-medium hover:text-primary transition-colors">
                {t('nav.about')}
              </Link>
            </div>
          </nav>
        )}
      </div>
    </header>
  )
}

export default Header