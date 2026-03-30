/**
 * i18n 翻译合并脚本
 * 用途：将基础翻译和 admin 翻译文件合并为完整的翻译文件
 * 运行：node src/i18n/mergeBundles.js
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

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
function readBaseTranslation(languageCode) {
  try {
    const filePath = path.join(localesDir, `${languageCode}.json`)
    const content = fs.readFileSync(filePath, 'utf-8')
    return JSON.parse(content)
  } catch (error) {
    console.warn(`⚠️  无法读取 ${languageCode} 基础翻译文件:`, error.message)
    return {}
  }
}

/**
 * 从 admin 目录读取翻译文件
 */
function readAdminTranslation(languageCode) {
  try {
    const filePath = path.join(localesDir, 'admin', `${languageCode}.json`)
    const content = fs.readFileSync(filePath, 'utf-8')
    return JSON.parse(content)
  } catch (error) {
    console.warn(`⚠️  无法读取 ${languageCode} admin 翻译文件:`, error.message)
    return { admin: {} }
  }
}

/**
 * 生成完整的翻译文件
 */
function generateCompleteTranslationFile(languageCode) {
  const baseData = readBaseTranslation(languageCode)
  const adminData = readAdminTranslation(languageCode)

  const completeBundle = {
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
    console.error(`❌ 更新 ${outputFileName} 失败:`, error.message)
  }
}

/**
 * 主函数
 */
function main() {
  console.log('📦 开始合并 i18n 翻译文件...\n')

  languages.forEach(lang => {
    generateCompleteTranslationFile(lang.code)
  })

  console.log('\n✨ 翻译文件合并完成！')
  console.log(`📁 输出位置: ${outputDir}`)
}

// 执行
main()
