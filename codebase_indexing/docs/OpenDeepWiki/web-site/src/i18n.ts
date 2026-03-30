import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

// 导入翻译文件
import zhCN from './i18n/locales/zh-CN.json'
import enUS from './i18n/locales/en-US.json'
import jaJP from './i18n/locales/ja-JP.json'
import koKR from './i18n/locales/ko-KR.json'

// 导入 admin 翻译文件
import zhCNAdmin from './i18n/locales/admin/zh-CN.json'
import enUSAdmin from './i18n/locales/admin/en-US.json'
import jaJPAdmin from './i18n/locales/admin/ja-JP.json'
import koKRAdmin from './i18n/locales/admin/ko-KR.json'

// 翻译资源
const resources = {
  'zh-CN': {
    translation: zhCN,
    admin: zhCNAdmin.admin
  },
  'en-US': {
    translation: enUS,
    admin: enUSAdmin.admin
  },
  'ja-JP': {
    translation: jaJP,
    admin: jaJPAdmin.admin
  },
  'ko-KR': {
    translation: koKR,
    admin: koKRAdmin.admin
  }
}

// 初始化 i18n
i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: localStorage.getItem('language') || 'zh-CN', // 默认语言
    fallbackLng: 'en-US',
    ns: ['translation', 'admin'],
    defaultNS: 'translation',
    interpolation: {
      escapeValue: false // React 已经做了转义
    },
    debug: false
  })

export default i18n