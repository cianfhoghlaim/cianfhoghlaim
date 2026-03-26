import { useEffect, useState, useCallback, useRef, useMemo } from 'react'
import { cn } from '@/lib/utils'

interface TocItem {
  id: string
  text: string
  level: number
  element: HTMLElement
}

interface TableOfContentsProps {
  className?: string
  onItemClick?: () => void
}

export default function TableOfContents({ className, onItemClick }: TableOfContentsProps) {
  const [headings, setHeadings] = useState<TocItem[]>([])
  const [activeId, setActiveId] = useState<string>('')
  const [indicatorStyle, setIndicatorStyle] = useState({ top: 0, height: 0, opacity: 0 })
  const tocRef = useRef<HTMLDivElement>(null)

  // 获取滚动容器
  const getScrollContainer = useCallback(() => {
    return document.querySelector('.flex-1.overflow-auto') as HTMLElement ||
           document.querySelector('main') as HTMLElement ||
           document.documentElement
  }, [])

  // 更精确的滚动位置计算
  const getScrollPosition = useCallback((container: HTMLElement) => {
    if (container === document.documentElement) {
      return window.scrollY
    }
    return container.scrollTop
  }, [])

  // 获取元素相对于容器的位置
  const getElementTop = useCallback((element: HTMLElement, container: HTMLElement) => {
    if (container === document.documentElement) {
      return element.offsetTop
    }

    const containerRect = container.getBoundingClientRect()
    const elementRect = element.getBoundingClientRect()
    return elementRect.top - containerRect.top + container.scrollTop
  }, [])

  // 使用 useMemo 优化标题选择器
  const headingSelectors = useMemo(() => [
    '.markdown-content h1, .markdown-content h2, .markdown-content h3, .markdown-content h4, .markdown-content h5, .markdown-content h6',
    'article h1, article h2, article h3, article h4, article h5, article h6',
    'main h1, main h2, main h3, main h4, main h5, main h6',
    '.prose h1, .prose h2, .prose h3, .prose h4, .prose h5, .prose h6',
    'h1, h2, h3, h4, h5, h6'
  ], [])

  useEffect(() => {
    // 定时检查DOM变化并更新标题
    const updateHeadings = () => {
      // 使用预定义的选择器

      let elements: HTMLElement[] = []

      // 按优先级尝试选择器
      for (const selector of headingSelectors) {
        elements = Array.from(document.querySelectorAll(selector)) as HTMLElement[]
        if (elements.length > 0) break
      }

      // 过滤掉导航和侧边栏中的标题
      elements = elements.filter(elem => {
        const closest = elem.closest('nav, aside, .sidebar, .navigation, header, footer')
        return !closest
      })

      // console.log('TOC: Found elements', elements.length, elements.map(el => ({ tag: el.tagName, text: el.textContent, id: el.id })))

      const tocItems: TocItem[] = elements
        .map((elem) => {
          const rawText = elem.textContent || ''
          const cleanText = rawText.trim()

          // 清理显示文本：移除前缀的 # 符号和其他标记
          const displayText = cleanText
            .replace(/^#{1,6}\s*/, '') // 移除 markdown 标记
            .replace(/^\d+\.\s*/, '') // 移除数字列表标记
            .replace(/^[\u2022\u25CF\u25E6]\s*/, '') // 移除项目符号
            .trim()

          // 生成更robust的ID
          let elementId = elem.id
          if (!elementId && displayText) {
            elementId = displayText
              .toLowerCase()
              .replace(/[^\w\s\u4e00-\u9fff-]/g, '') // 保留中文字符
              .replace(/\s+/g, '-')
              .replace(/^-+|-+$/g, '') // 移除开头和结尾的连字符
              .substring(0, 50) // 限制长度

            if (elementId) {
              // 确保ID唯一
              let uniqueId = elementId
              let counter = 1
              while (document.getElementById(uniqueId) && document.getElementById(uniqueId) !== elem) {
                uniqueId = `${elementId}-${counter}`
                counter++
              }
              elem.id = uniqueId
              elementId = uniqueId
            }
          }

          return {
            id: elementId,
            text: displayText,
            level: parseInt(elem.tagName.substring(1)),
            element: elem
          }
        })
        .filter((item) => {
          const isValid = (
            item.text &&
            item.text.length > 0 &&
            item.id &&
            item.level >= 1 &&
            item.level <= 6 &&
            item.text.length < 200 // 过滤掉过长的文本（可能不是真正的标题）
          )

          if (!isValid) {
            // console.log('TOC: Filtered out item', item)
          }

          return isValid
        })

      // console.log('TOC: Final headings', tocItems)
      setHeadings(tocItems)
    }

    // 初始化
    updateHeadings()

    // 使用 MutationObserver 监听DOM变化
    const observer = new MutationObserver(() => {
      setTimeout(updateHeadings, 100) // 延迟更新，确保DOM完全渲染
    })

    const markdownContent = document.querySelector('.markdown-content')
    if (markdownContent) {
      observer.observe(markdownContent, {
        childList: true,
        subtree: true,
        characterData: true
      })
    }

    return () => {
      observer.disconnect()
    }
  }, [headingSelectors])

  // 防抖函数
  const debounce = useCallback((func: Function, wait: number) => {
    let timeout: NodeJS.Timeout
    return (...args: any[]) => {
      clearTimeout(timeout)
      timeout = setTimeout(() => func.apply(null, args), wait)
    }
  }, [])

  // 更新指示器位置
  const updateIndicatorPosition = useCallback((targetId: string, immediate = false) => {
    if (!tocRef.current || !targetId) {
      setIndicatorStyle(prev => ({ ...prev, opacity: 0 }))
      return
    }

    const performUpdate = () => {
      if (!tocRef.current) return

      const activeLink = tocRef.current.querySelector(`[href="#${targetId}"]`) as HTMLElement
      if (!activeLink) {
        setIndicatorStyle(prev => ({ ...prev, opacity: 0 }))
        return
      }

      const tocRect = tocRef.current.getBoundingClientRect()
      const linkRect = activeLink.getBoundingClientRect()

      const top = linkRect.top - tocRect.top + tocRef.current.scrollTop
      const height = linkRect.height

      setIndicatorStyle({
        top: Math.max(0, top),
        height: Math.max(0, height),
        opacity: 1
      })
    }

    if (immediate) {
      performUpdate()
    } else {
      // 添加小延迟确保DOM更新完成
      requestAnimationFrame(performUpdate)
    }
  }, [])

  // 防抖的指示器更新
  const debouncedUpdateIndicator = useCallback(
    debounce((targetId: string) => updateIndicatorPosition(targetId), 50),
    [updateIndicatorPosition, debounce]
  )

  // 节流函数 - 优化性能
  const throttle = useCallback((func: Function, limit: number) => {
    let inThrottle: boolean
    let lastResult: any
    return (...args: any[]) => {
      if (!inThrottle) {
        lastResult = func.apply(null, args)
        inThrottle = true
        setTimeout(() => inThrottle = false, limit)
      }
      return lastResult
    }
  }, [])

  // 滚动监听和活跃标题更新
  useEffect(() => {
    if (headings.length === 0) return

    const handleScroll = throttle(() => {
      const container = getScrollContainer()
      const scrollTop = getScrollPosition(container)
      const offset = 80 // 偏移量

      let activeIndex = -1

      // 优化：使用二分查找提高性能
      let left = 0
      let right = headings.length - 1

      while (left <= right) {
        const mid = Math.floor((left + right) / 2)
        const heading = headings[mid]
        const elementTop = getElementTop(heading.element, container)

        if (elementTop - offset <= scrollTop + 10) {
          activeIndex = mid
          left = mid + 1
        } else {
          right = mid - 1
        }
      }

      // 如果没有找到合适的标题，选择第一个
      if (activeIndex === -1 && headings.length > 0) {
        activeIndex = 0
      }

      const newActiveId = activeIndex >= 0 ? headings[activeIndex].id : ''

      if (newActiveId !== activeId) {
        setActiveId(newActiveId)
      }
    }, 32) // 减少到约30fps，降低CPU使用

    const container = getScrollContainer()

    // 添加事件监听
    if (container === document.documentElement) {
      window.addEventListener('scroll', handleScroll, { passive: true })
    } else {
      container.addEventListener('scroll', handleScroll, { passive: true })
    }

    // 初始调用
    handleScroll()

    return () => {
      if (container === document.documentElement) {
        window.removeEventListener('scroll', handleScroll)
      } else {
        container.removeEventListener('scroll', handleScroll)
      }
    }
  }, [headings, activeId, getScrollContainer, getScrollPosition, getElementTop, throttle])

  // 监听activeId变化，更新指示器位置并滚动到可见区域
  useEffect(() => {
    if (activeId && tocRef.current) {
      // 首次设置立即更新，后续使用防抖
      updateIndicatorPosition(activeId, true)

      // 自动滚动 TOC 到当前激活项
      const activeLink = tocRef.current.querySelector(`[href="#${activeId}"]`) as HTMLElement
      if (activeLink) {
        const tocContainer = tocRef.current
        const containerRect = tocContainer.getBoundingClientRect()
        const linkRect = activeLink.getBoundingClientRect()

        // 计算元素相对于容器的位置
        const relativeTop = linkRect.top - containerRect.top
        const relativeBottom = linkRect.bottom - containerRect.top

        // 检查元素是否在可见区域内
        const isAboveViewport = relativeTop < 0
        const isBelowViewport = relativeBottom > containerRect.height

        if (isAboveViewport || isBelowViewport) {
          // 滚动到元素位置，居中显示
          const scrollTop = tocContainer.scrollTop + relativeTop - containerRect.height / 2 + linkRect.height / 2
          tocContainer.scrollTo({
            top: Math.max(0, scrollTop),
            behavior: 'smooth'
          })
        }
      }
    }
  }, [activeId, updateIndicatorPosition])

  // 监听headings变化，重新计算指示器位置
  useEffect(() => {
    if (activeId && headings.length > 0) {
      // headings变化后，延迟更新指示器位置，确保DOM渲染完成
      setTimeout(() => updateIndicatorPosition(activeId, true), 100)
    }
  }, [headings, activeId, updateIndicatorPosition])

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault()

    const heading = headings.find(h => h.id === id)
    if (!heading) return

    const container = getScrollContainer()
    const elementTop = getElementTop(heading.element, container)
    const offset = 80

    if (container === document.documentElement) {
      window.scrollTo({
        top: elementTop - offset,
        behavior: 'smooth'
      })
    } else {
      container.scrollTo({
        top: elementTop - offset,
        behavior: 'smooth'
      })
    }

    // 调用回调函数（用于移动端关闭抽屉）
    onItemClick?.()
  }

  // 获取基础级别（最小的标题级别）
  const baseLevel = headings.length > 0 ? Math.min(...headings.map(h => h.level)) : 1

  // 如果标题数量太少（少于2个），不显示TOC
  if (headings.length < 2) {
    return null
  }

  return (
    <nav className={cn("sticky top-20 max-h-[calc(100vh-5rem)]", className)}>
      <div className="relative">
        {/* 标题 */}
        <div className="mb-6 px-3">
          <h3 className="text-sm font-semibold text-foreground tracking-tight">
            On This Page
          </h3>
        </div>

        {/* 目录列表容器 */}
        <div
          ref={tocRef}
          className="relative overflow-y-auto max-h-[calc(100vh-8rem)] scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent"
        >
          {/* 背景轨道线 */}
          <div className="absolute left-3 top-0 bottom-0 w-px bg-border/60" />

          {/* 动画指示器 */}
          <div
            className="absolute left-3 w-0.5 bg-primary rounded-full transition-all duration-500 ease-in-out will-change-transform"
            style={{
              top: `${indicatorStyle.top}px`,
              height: `${indicatorStyle.height}px`,
              opacity: indicatorStyle.opacity,
              transform: 'translateX(-1px) translateZ(0)', // 使用GPU加速
              boxShadow: '0 0 6px rgba(var(--primary), 0.3)' // 添加微妙的阴影
            }}
          />

          <ul className="relative space-y-0.5 pb-4">
            {headings.map((heading, index) => {
              const isActive = activeId === heading.id
              const relativeLevel = heading.level - baseLevel
              const paddingLeft = 12 + relativeLevel * 16 // 基础12px + 每级16px

              return (
                <li
                  key={`${heading.id}-${index}`}
                  className="relative group"
                >
                  <a
                    href={`#${heading.id}`}
                    onClick={(e) => handleClick(e, heading.id)}
                    className={cn(
                      "block py-2.5 pr-3 text-sm leading-6 transition-all duration-200 relative",
                      "hover:text-foreground rounded-lg mr-2",
                      isActive
                        ? "text-foreground font-medium bg-primary/10"
                        : "text-muted-foreground hover:bg-muted/30",
                      // 根据级别调整样式
                      relativeLevel === 0 && "font-semibold text-[13px]",
                      relativeLevel === 1 && "text-[13px]",
                      relativeLevel >= 2 && "text-xs font-normal",
                      relativeLevel >= 3 && "opacity-75"
                    )}
                    style={{
                      paddingLeft: `${paddingLeft}px`,
                    }}
                    title={heading.text}
                  >
                    <span className="block truncate transition-colors">
                      {heading.text}
                    </span>

                    {/* 悬停指示器 */}
                    {!isActive && (
                      <div className="absolute left-3 top-1/2 -translate-y-1/2 w-px h-0 bg-muted-foreground/40 group-hover:h-4 transition-all duration-200" />
                    )}
                  </a>
                </li>
              )
            })}
          </ul>
        </div>
      </div>
    </nav>
  )
}