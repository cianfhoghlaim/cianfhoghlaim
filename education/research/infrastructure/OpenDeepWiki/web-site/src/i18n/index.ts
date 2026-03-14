// i18n 配置和初始化

import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

// 导入语言资源 - 主命名空间
import enUS from './locales/en-US.json'
import zhCN from './locales/zh-CN.json'
import jaJP from './locales/ja-JP.json'
import koKR from './locales/ko-KR.json'

// 导入语言资源 - admin 命名空间
import adminEnUS from './locales/admin/en-US.json'
import adminZhCN from './locales/admin/zh-CN.json'
import adminJaJP from './locales/admin/ja-JP.json'
import adminKoKR from './locales/admin/ko-KR.json'

const resources = {
  'en-US': {
    translation: enUS,
    admin: adminEnUS,
  },
  'zh-CN': {
    translation: zhCN,
    admin: adminZhCN,
  },
  'ja-JP': {
    translation: jaJP,
    admin: adminJaJP,
  },
  'ko-KR': {
    translation: koKR,
    admin: adminKoKR,
  },
}

i18n
  // 检测用户语言
  .use(LanguageDetector)
  // 传递 i18n 实例给 react-i18next
  .use(initReactI18next)
  // 初始化 i18next
  .init({
    resources,
    fallbackLng: 'zh-CN',
    debug: import.meta.env.DEV,

    // 语言检测选项
    detection: {
      // 检测顺序: 1. localStorage 中存储的语言 2. 浏览器语言 3. HTML lang 属性
      order: ['localStorage', 'navigator', 'htmlTag'],
      // 缓存用户选择的语言到 localStorage
      caches: ['localStorage'],
      // localStorage 中的键名
      lookupLocalStorage: 'i18nextLng',
      // 从 navigator 中检测语言
      lookupFromPathIndex: 0,
      lookupFromSubdomainIndex: 0,
      // 语言代码转换,确保格式统一
      convertDetectedLanguage: (lng: string) => {
        // 将浏览器语言代码转换为项目支持的语言代码
        const languageMap: Record<string, string> = {
          'zh': 'zh-CN',
          'zh-cn': 'zh-CN',
          'zh-Hans': 'zh-CN',
          'zh-Hans-CN': 'zh-CN',
          'en': 'en-US',
          'en-us': 'en-US',
          'ja': 'ja-JP',
          'ja-jp': 'ja-JP',
          'ko': 'ko-KR',
          'ko-kr': 'ko-KR',
        }
        
        const lowerLng = lng.toLowerCase()
        return languageMap[lowerLng] || lng
      },
    },

    interpolation: {
      escapeValue: false, // React 已经默认转义了
    },

    // 支持的语言
    supportedLngs: ['en-US', 'zh-CN', 'ja-JP', 'ko-KR'],

    // 命名空间
    ns: ['translation', 'admin'],
    defaultNS: 'translation',
  })

export default i18n

// 导出语言列表
export const languages = [
  {
    code: 'zh-CN',
    name: '中文(简体)',
    flag: '🇨🇳',
  },
  {
    code: 'en-US',
    name: 'English',
    flag: '🇺🇸',
  },
  {
    code: 'ja-JP',
    name: '日本語',
    flag: '🇯🇵',
  },
  {
    code: 'ko-KR',
    name: '한국어',
    flag: '🇰🇷',
  },
]

// 获取当前语言
export const getCurrentLanguage = () => i18n.language

// 切换语言
export const changeLanguage = (lng: string) => {
  return i18n.changeLanguage(lng)
}