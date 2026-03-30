/**
 * i18n 翻译合并脚本
 * 用途：将基础翻译和 admin 翻译文件合并为完整的翻译文件
 * 运行：npm run merge-i18n 或 node src/i18n/mergeBundles.ts
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

interface BaseTranslation {
  common?: Record<string, any>
  nav?: Record<string, any>
  home?: Record<string, any>
  login?: Record<string, any>
  register?: Record<string, any>
  repository?: Record<string, any>
  messages?: Record<string, any>
  settings?: Record<string, any>
  [key: string]: any
}

interface AdminTranslation {
  admin?: Record<string, any>
  [key: string]: any
}

interface CompleteBundle extends BaseTranslation {
  admin?: Record<string, any>
}

const localesDir = path.join(__dirname, 'locales')
const outputDir = path.join(__dirname, 'locales')

// 支持的语言列表
const languages = [
  { code: 'zh-CN', name: '中文' },
  { code: 'en-US', name: 'English' },
  { code: 'ja-JP', name: '日本語' },
  { code: 'ko-KR', name: '한국어' }
]

/**
 * 从主目录读取基础翻译文件
 */
function readBaseTranslation(languageCode: string): BaseTranslation {
  try {
    const filePath = path.join(localesDir, `${languageCode}.json`)
    const content = fs.readFileSync(filePath, 'utf-8')
    return JSON.parse(content)
  } catch (error) {
    console.warn(`⚠️  无法读取 ${languageCode} 基础翻译文件:`, error)
    return {}
  }
}

/**
 * 从 admin 目录读取翻译文件
 */
function readAdminTranslation(languageCode: string): AdminTranslation {
  try {
    const filePath = path.join(localesDir, 'admin', `${languageCode}.json`)
    const content = fs.readFileSync(filePath, 'utf-8')
    return JSON.parse(content)
  } catch (error) {
    console.warn(`⚠️  无法读取 ${languageCode} admin 翻译文件:`, error)
    return { admin: {} }
  }
}

/**
 * 生成完整的翻译文件
 */
function generateCompleteTranslationFile(languageCode: string): void {
  const baseData = readBaseTranslation(languageCode)
  const adminData = readAdminTranslation(languageCode)

  const completeBundle: CompleteBundle = {
    ...baseData,
    admin: adminData.admin || {}
  }

  const outputFileName = `${languageCode}.json`
  const outputPath = path.join(outputDir, outputFileName)

  try {
    fs.writeFileSync(
      outputPath,
      JSON.stringify(completeBundle, null, 2),
      'utf-8'
    )
    console.log(`✅ 已更新: ${outputFileName}`)
  } catch (error) {
    console.error(`❌ 更新 ${outputFileName} 失败:`, error)
  }
}

/**
 * 主函数
 */
function main(): void {
  console.log('📦 开始合并 i18n 翻译文件...\n')

  languages.forEach(lang => {
    generateCompleteTranslationFile(lang.code)
  })

  console.log('\n✨ 翻译文件合并完成！')
  console.log(`📁 输出位置: ${outputDir}`)
}

// 执行
main()
