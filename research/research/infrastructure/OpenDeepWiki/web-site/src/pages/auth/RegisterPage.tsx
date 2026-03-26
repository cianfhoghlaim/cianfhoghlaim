// 注册页面组件

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

export const RegisterPage = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { register, loading, error, clearError, isAuthenticated } = useAuth()
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
    const email = formData.get('email') as string
    const password = formData.get('password') as string
    const confirmPassword = formData.get('confirmPassword') as string
    const agreement = formData.get('agreement') === 'on'

    // 表单验证
    if (!username || username.trim().length < 4) {
      toast.error(t('register.validation.username_min_length'))
      return
    }

    if (!email || !/^\S+@\S+\.\S+$/.test(email)) {
      toast.error(t('register.validation.email_invalid'))
      return
    }

    if (!password || password.length < 8) {
      toast.error(t('register.validation.password_min_length'))
      return
    }

    if (!confirmPassword) {
      toast.error(t('register.validation.confirm_password_required'))
      return
    }

    if (password !== confirmPassword) {
      toast.error(t('register.validation.passwords_not_match'))
      return
    }

    if (!agreement) {
      toast.error(t('register.validation.agreement_required'))
      return
    }

    try {
      const success = await register({ username: username.trim(), email, password, confirmPassword })
      
      if (success) {
        toast.success(t('register.messages.success'))
        // useAuth hook会自动处理重定向
      } else {
        toast.error(error || t('register.messages.failed'))
      }
    } catch (err) {
      console.error('注册错误:', err)
      toast.error(t('register.messages.error'))
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
              {t('register.title')}
            </CardTitle>
            <CardDescription>
              {t('register.subtitle')}
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
                          {t('register.oauth.github')}
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
                          {t('register.oauth.google')}
                        </Button>
                      ) : null
                    ))}
                  </div>
                )}
                
                {/* 分隔线 */}
                {thirdPartyProviders.length > 0 && (
                  <div className="relative text-center text-sm before:absolute before:inset-0 before:top-1/2 before:z-0 before:flex before:items-center before:border-t before:border-border">
                    <span className="relative z-10 bg-card px-2 text-muted-foreground">
                      {t('register.or_use_email')}
                    </span>
                  </div>
                )}
                
                {/* 注册表单 */}
                <div className="grid gap-6">
                  <div className="grid gap-3">
                    <Label htmlFor="username">
                      {t('register.form.username')}
                    </Label>
                    <Input
                      id="username"
                      name="username"
                      placeholder={t('register.form.username_placeholder')}
                      autoComplete="username"
                      required
                      disabled={loading}
                    />
                  </div>
                  
                  <div className="grid gap-3">
                    <Label htmlFor="email">
                      {t('register.form.email')}
                    </Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      placeholder={t('register.form.email_placeholder')}
                      autoComplete="email"
                      required
                      disabled={loading}
                    />
                  </div>
                  
                  <div className="grid gap-3">
                    <Label htmlFor="password">
                      {t('register.form.password')}
                    </Label>
                    <Input 
                      id="password" 
                      name="password" 
                      type="password" 
                      placeholder={t('register.form.password_placeholder')}
                      autoComplete="new-password"
                      required
                      disabled={loading}
                    />
                  </div>
                  
                  <div className="grid gap-3">
                    <Label htmlFor="confirmPassword">
                      {t('register.form.confirm_password')}
                    </Label>
                    <Input 
                      id="confirmPassword" 
                      name="confirmPassword" 
                      type="password" 
                      placeholder={t('register.form.confirm_password_placeholder')}
                      autoComplete="new-password"
                      required
                      disabled={loading}
                    />
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id="agreement" 
                      name="agreement"
                      disabled={loading}
                    />
                    <Label htmlFor="agreement" className="text-sm font-normal">
                      {t('register.form.agreement')}{" "}
                      <Link 
                        to="/terms" 
                        className="text-primary hover:underline underline-offset-4"
                      >
                        {t('register.form.terms')}
                      </Link>
                      {" "}和{" "}
                      <Link 
                        to="/privacy" 
                        className="text-primary hover:underline underline-offset-4"
                      >
                        {t('register.form.privacy')}
                      </Link>
                    </Label>
                  </div>
                  
                  <Button 
                    type="submit" 
                    className="w-full" 
                    disabled={loading}
                  >
                    {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    {loading ? t('register.form.registering') : t('register.form.register')}
                  </Button>
                </div>
                
                {/* 登录链接 */}
                <div className="text-center text-sm">
                  {t('register.have_account')}{" "}
                  <Link 
                    to="/login" 
                    className="text-primary hover:underline underline-offset-4"
                  >
                    {t('register.login_now')}
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

export default RegisterPage