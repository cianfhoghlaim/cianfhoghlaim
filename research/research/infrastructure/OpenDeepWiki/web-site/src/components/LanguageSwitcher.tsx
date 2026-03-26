// 语言切换组件

import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Globe, Check } from 'lucide-react'
import { languages, changeLanguage } from '@/i18n/index'
import { cn } from '@/lib/utils'

interface LanguageSwitcherProps {
  variant?: 'default' | 'ghost' | 'outline'
  size?: 'default' | 'sm' | 'lg'
  className?: string
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({
  variant = 'ghost',
  size = 'sm',
  className
}) => {
  const { i18n } = useTranslation()
  
  const currentLanguage = languages.find((lang:any) => lang.code === i18n.language) || languages[0]

  const handleLanguageChange = async (languageCode: string) => {
    try {
      await changeLanguage(languageCode)
      // 显式保存语言选择到 localStorage（i18next-browser-languagedetector 会自动处理）
      localStorage.setItem('i18nextLng', languageCode)
      console.log('语言已切换至:', languageCode)
    } catch (error) {
      console.error('切换语言失败:', error)
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant={variant} 
          size={size} 
          className={cn('flex items-center gap-2', className)}
        >
          <Globe className="h-4 w-4" />
          <span className="hidden sm:inline-block">
            {currentLanguage.name}
          </span>
        </Button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent align="end" className="w-48">
        {languages.map((language) => {
          const isActive = i18n.language === language.code
          
          return (
            <DropdownMenuItem
              key={language.code}
              className={cn(
                'flex items-center justify-between cursor-pointer',
                isActive && 'bg-accent'
              )}
              onClick={() => handleLanguageChange(language.code)}
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">{language.flag}</span>
                <span>{language.name}</span>
              </div>
              {isActive && (
                <Check className="h-4 w-4 text-primary" />
              )}
            </DropdownMenuItem>
          )
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export default LanguageSwitcher