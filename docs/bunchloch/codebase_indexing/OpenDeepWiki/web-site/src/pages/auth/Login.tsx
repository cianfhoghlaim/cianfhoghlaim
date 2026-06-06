// 登录页面组件

import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { toast } from 'sonner'
import { Github, Loader2 } from 'lucide-react'
import { GoogleIcon } from '@/components/icons/GoogleIcon'

import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'

import { useAuth, useThirdPartyAuth } from '@/hooks/useAuth'
import { getSupportedThirdPartyLogins } from '@/services/auth.service'
import type { ThirdPartyLoginProvider } from '@/services/auth.service'

export const Login = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { login, loading, error, clearError, isAuthenticated } = useAuth()
  const { handleThirdPartyLogin } = useThirdPartyAuth()
  
  const [thirdPartyProviders, setThirdPartyProviders] = useState<ThirdPartyLoginProvider[]>([])

  // 如果已登录，重定向到首页
  useEffect(() => {
    if (isAuthenticated) {
      const redirectPath = localStorage.getItem('redirectPath') || '/'
      localStorage.removeItem('redirectPath')
      navigate(redirectPath)
    }
  }, [isAuthenticated, navigate])

  // 获取支持的第三方登录方式
  useEffect(() => {
    const fetchThirdPartyProviders = async () => {
      try {
        const response = await getSupportedThirdPartyLogins()
        if (response.code === 200 && response.data) {
          setThirdPartyProviders(response.data)
        }
      } catch (error) {
        console.error('获取第三方登录方式失败:', error)
      }
    }

    fetchThirdPartyProviders()
  }, [])

  // 处理表单提交
  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    clearError()
    
    const formData = new FormData(event.currentTarget)
    const username = formData.get('username') as string
    const password = formData.get('password') as string

    if (!username || !password) {
      toast.error(t('login.validation.required_fields'))
      return
    }

    try {
      const success = await login(username, password)
      
      if (success) {
        toast.success(t('login.messages.success'))
        // useAuth hook会自动处理重定向
      } else {
        toast.error(error || t('login.messages.failed'))
      }
    } catch (err) {
      console.error('登录错误:', err)
      toast.error(t('login.messages.error'))
    }
  }

  // 处理第三方登录
  const handleOAuthLogin = (providerName: string) => {
    const provider = thirdPartyProviders.find(p => 
      p.name.toLowerCase() === providerName.toLowerCase()
    )
    
    if (provider) {
      handleThirdPartyLogin(providerName, provider.clientId)
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-xl">
              {t('login.title')}
            </CardTitle>
            <CardDescription>
              {t('login.subtitle')}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit}>
              <div className="grid gap-6">
                {/* 第三方登录 */}
                {thirdPartyProviders.length > 0 && (
                  <div className="flex flex-col gap-4">
                    {thirdPartyProviders.map((provider) => (
                      provider.name.toLowerCase() === 'github' ? (
                        <Button
                          key={provider.name}
                          variant="outline"
                          className="w-full"
                          type="button"
                          onClick={() => handleOAuthLogin('github')}
                          disabled={loading}
                        >
                          <Github className="mr-2 h-4 w-4" />
                          {t('login.oauth.github')}
                        </Button>
                      ) : provider.name.toLowerCase() === 'google' ? (
                        <Button
                          key={provider.name}
                          variant="outline"
                          className="w-full"
                          type="button"
                          onClick={() => handleOAuthLogin('google')}
                          disabled={loading}
                        >
                          <GoogleIcon className="mr-2 h-4 w-4" />
                          {t('login.oauth.google')}
                        </Button>
                      ) : null
                    ))}
                  </div>
                )}
                
                {/* 分隔线 */}
                {thirdPartyProviders.length > 0 && (
                  <div className="relative text-center text-sm before:absolute before:inset-0 before:top-1/2 before:z-0 before:flex before:items-center before:border-t before:border-border">
                    <span className="relative z-10 bg-card px-2 text-muted-foreground">
                      {t('login.or_use_credentials')}
                    </span>
                  </div>
                )}
                
                {/* 登录表单 */}
                <div className="grid gap-6">
                  <div className="grid gap-3">
                    <Label htmlFor="username">
                      {t('login.form.username')}
                    </Label>
                    <Input
                      id="username"
                      name="username"
                      placeholder={t('login.form.username_placeholder')}
                      autoComplete="username"
                      required
                      disabled={loading}
                    />
                  </div>
                  
                  <div className="grid gap-3">
                    <div className="flex items-center">
                      <Label htmlFor="password">
                        {t('login.form.password')}
                      </Label>
                      <Link
                        to="/forgot-password"
                        className="ml-auto text-sm text-primary hover:underline underline-offset-4"
                      >
                        {t('login.form.forgot_password')}
                      </Link>
                    </div>
                    <Input 
                      id="password" 
                      name="password" 
                      type="password" 
                      placeholder={t('login.form.password_placeholder')}
                      autoComplete="current-password"
                      required
                      disabled={loading}
                    />
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id="remember" 
                      name="remember"
                      disabled={loading}
                    />
                    <Label htmlFor="remember" className="text-sm font-normal">
                      {t('login.form.remember_me')}
                    </Label>
                  </div>
                  
                  <Button 
                    type="submit" 
                    className="w-full" 
                    disabled={loading}
                  >
                    {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    {loading ? t('login.form.logging_in') : t('login.form.login')}
                  </Button>
                </div>
                
                {/* 注册链接 */}
                <div className="text-center text-sm">
                  {t('login.no_account')}{" "}
                  <Link 
                    to="/register" 
                    className="text-primary hover:underline underline-offset-4"
                  >
                    {t('login.register_now')}
                  </Link>
                </div>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Login