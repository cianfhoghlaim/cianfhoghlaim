// 搜索栏组件

import { useState, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { Search, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface SearchBarProps {
  value?: string
  placeholder?: string
  onSearch?: (value: string) => void
  onChange?: (value: string) => void
  className?: string
  size?: 'default' | 'sm' | 'lg'
}

export const SearchBar: React.FC<SearchBarProps> = ({
  value: propValue = '',
  placeholder = '搜索仓库名称或地址',
  onSearch,
  onChange,
  className,
  size = 'default'
}) => {
  const { t } = useTranslation()
  const [internalValue, setInternalValue] = useState(propValue)
  const value = propValue || internalValue

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    setInternalValue(newValue)
    onChange?.(newValue)
  }, [onChange])

  const handleSearch = useCallback(() => {
    onSearch?.(value)
  }, [onSearch, value])

  const handleClear = useCallback(() => {
    setInternalValue('')
    onChange?.('')
    onSearch?.('')
  }, [onChange, onSearch])

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }, [handleSearch])

  const sizeClasses = {
    sm: 'h-9 text-sm',
    default: 'h-11',
    lg: 'h-14 text-lg'
  }

  return (
    <div className={cn(
      'relative flex items-center w-full max-w-2xl mx-auto',
      className
    )}>
      <div className="relative flex-1">
        <Search className={cn(
          'absolute left-3 text-muted-foreground pointer-events-none',
          size === 'sm' ? 'h-4 w-4 top-2.5' : size === 'lg' ? 'h-6 w-6 top-4' : 'h-5 w-5 top-3'
        )} />
        
        <input
          type="text"
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={cn(
            'w-full rounded-lg border border-input bg-background px-10 py-2 text-sm ring-offset-background',
            'placeholder:text-muted-foreground',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
            'disabled:cursor-not-allowed disabled:opacity-50',
            sizeClasses[size]
          )}
        />
        
        {value && (
          <button
            onClick={handleClear}
            className={cn(
              'absolute text-muted-foreground hover:text-foreground transition-colors',
              size === 'sm' ? 'right-2 top-2.5' : size === 'lg' ? 'right-3 top-4' : 'right-2.5 top-3'
            )}
          >
            <X className={size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-6 w-6' : 'h-5 w-5'} />
          </button>
        )}
      </div>
      
      <Button 
        onClick={handleSearch}
        size={size}
        className="ml-2"
      >
        {t('common.search')}
      </Button>
    </div>
  )
}

export default SearchBar