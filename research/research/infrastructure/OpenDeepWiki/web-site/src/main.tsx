import { createRoot } from 'react-dom/client'
import './index.css'
import './i18n/index' // 初始化 i18n
import App from './App.tsx'

// 全局清理 Mermaid 错误的函数
const cleanupMermaidErrors = () => {
  // 查找并移除可能的 Mermaid 错误显示元素
  const errorSelectors = [
    '.mermaidTooltip',
    '.mermaid-parse-error',
    '[id^="d-"][id$="-error"]',
    '.error',
    '[class*="mermaid"][class*="error"]',
    '.mermaid-error',
    '.error-message'
  ]

  errorSelectors.forEach(selector => {
    const elements = document.querySelectorAll(selector)
    elements.forEach(element => {
      const text = element.textContent || ''
      if (text.includes('Syntax error in text') ||
          text.includes('mermaid version') ||
          text.includes('Parse error') ||
          text.includes('Error:')) {
        element.remove()
      }
    })
  })

  // 清除可能的全局 Mermaid 错误状态 - 查找直接添加到body的错误元素
  const bodyChildren = document.querySelectorAll('body > *:not(#root):not(script):not(style):not(link):not(meta)')
  bodyChildren.forEach(element => {
    const text = element.textContent || ''
    if (text.includes('Syntax error in text') ||
        text.includes('mermaid version') ||
        text.includes('Parse error') ||
        (text.includes('Error:') && element.tagName !== 'SCRIPT')) {
      console.log('Removing Mermaid error element:', element)
      element.remove()
    }
  })

  // 更积极地清理任何包含 Mermaid 错误文本的元素
  const allElements = document.querySelectorAll('*')
  allElements.forEach(element => {
    const text = element.textContent || ''
    if (element.children.length === 0 && // 只处理叶子节点
        (text.trim() === 'Syntax error in text' ||
         text.trim().startsWith('mermaid version') ||
         (text.includes('Syntax error') && text.includes('mermaid')))) {
      element.remove()
    }
  })
}

// 立即清理一次
cleanupMermaidErrors()

// 设置定期清理
setInterval(cleanupMermaidErrors, 2000)

// 页面加载完成后再清理一次
window.addEventListener('load', cleanupMermaidErrors)

createRoot(document.getElementById('root')!).render(
    <App />
)
