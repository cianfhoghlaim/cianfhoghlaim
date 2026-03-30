import React, { useState, useCallback, useEffect } from 'react'
import { MdEditor, config, } from 'md-editor-rt'
import 'md-editor-rt/lib/style.css'
import { toast } from 'sonner'
import { uploadImage } from '@/services/admin.service'
import { useTheme } from '@/components/theme-provider'

// 配置中文语言包
config({
  editorConfig: {
    languageUserDefined: {
      'zh-CN': {
        toolbarTips: {
          bold: '加粗',
          underline: '下划线',
          italic: '斜体',
          strikeThrough: '删除线',
          title: '标题',
          sub: '下标',
          sup: '上标',
          quote: '引用',
          unorderedList: '无序列表',
          orderedList: '有序列表',
          task: '任务列表',
          codeRow: '行内代码',
          code: '代码块',
          link: '链接',
          image: '图片',
          table: '表格',
          mermaid: 'Mermaid图',
          katex: 'KaTeX公式',
          revoke: '后退',
          next: '前进',
          save: '保存',
          prettier: '美化',
          pageFullscreen: '浏览器全屏',
          fullscreen: '屏幕全屏',
          preview: '预览',
          previewOnly: '仅预览',
          htmlPreview: 'HTML预览',
          catalog: '目录',
          github: '源码地址'
        },
        titleItem: {
          h1: '一级标题',
          h2: '二级标题',
          h3: '三级标题',
          h4: '四级标题',
          h5: '五级标题',
          h6: '六级标题'
        },
        imgTitleItem: {
          link: '添加链接',
          upload: '上传图片',
          clip2upload: '裁剪上传'
        },
        linkModalTips: {
          linkTitle: '添加链接',
          imageTitle: '添加图片',
          descLabel: '链接描述',
          descLabelPlaceHolder: '请输入描述...',
          urlLabel: '链接地址',
          urlLabelPlaceHolder: '请输入链接...',
          buttonOK: '确定'
        },
        clipModalTips: {
          title: '裁剪图片上传',
          buttonUpload: '上传'
        },
        copyCode: {
          text: '复制代码',
          successTips: '已复制！',
          failTips: '复制失败！'
        },
        mermaid: {
          flow: '流程图',
          sequence: '时序图',
          gantt: '甘特图',
          class: '类图',
          state: '状态图',
          pie: '饼图',
          relationship: '关系图',
          journey: '旅程图'
        },
        katex: {
          inline: '行内公式',
          block: '块级公式'
        },
        footer: {
          markdownTotal: '字数',
          scrollAuto: '同步滚动'
        }
      }
    }
  }
})

interface MarkdownEditorProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  height?: string
  readOnly?: boolean
  theme?: 'light' | 'dark' | 'auto'
  language?: string
  toolbarsExclude?: string[]
  onSave?: (value: string, html: string) => void
  onError?: (error: Error) => void
  autoFocus?: boolean
  maxLength?: number
  showCodeRowNumber?: boolean
  previewTheme?: 'default' | 'github' | 'vuepress' | 'mk-cute' | 'smart-blue' | 'cyanosis'
  codeTheme?: 'atom' | 'a11y' | 'github' | 'gradient' | 'kimbie' | 'paraiso' | 'qtcreator' | 'stackoverflow'
}

const MarkdownEditor: React.FC<MarkdownEditorProps> = ({
  value,
  onChange,
  placeholder = '请输入内容...',
  height = '600px',
  readOnly = false,
  theme = 'auto',
  language = 'zh-CN',
  toolbarsExclude = [],
  onSave,
  onError,
  autoFocus = false,
  maxLength,
  showCodeRowNumber = true,
  previewTheme = 'github',
  codeTheme = 'github'
}) => {
  const [editorId] = useState(() => `md-editor-${Date.now()}`)
  const [uploading, setUploading] = useState(false)

  const { theme: globalTheme } = useTheme()

  // 根据全局主题和组件props计算实际主题
  const actualTheme = React.useMemo(() => {
    // 如果组件props指定了具体主题，使用props主题
    if (globalTheme === 'light' || globalTheme === 'dark') {
      return globalTheme
    }

    // 如果组件props是auto或未指定，使用全局主题
    if (globalTheme === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }

    return globalTheme === 'light' || globalTheme === 'dark' ? globalTheme : 'light'
  }, [globalTheme])


  // 处理图片上传
  const handleUploadImg = useCallback(async (
    files: File[],
    callback: (urls: string[]) => void
  ) => {
    if (files.length === 0) return

    setUploading(true)
    const uploadedUrls: string[] = []

    try {
      // 逐个上传图片
      for (const file of files) {
        try {
          const result = await uploadImage(file)
          if (result.url) {
            uploadedUrls.push(result.url)
          } else {
            throw new Error('上传失败：未返回图片URL')
          }
        } catch (error) {
          console.error('Upload image error:', error)
          toast.error(`上传图片 ${file.name} 失败`)
          if (onError) {
            onError(error as Error)
          }
        }
      }

      // 回调返回所有上传成功的图片URL
      if (uploadedUrls.length > 0) {
        callback(uploadedUrls)
        toast.success(`成功上传 ${uploadedUrls.length} 张图片`)
      }
    } catch (error) {
      console.error('Upload images error:', error)
      toast.error('图片上传失败')
      if (onError) {
        onError(error as Error)
      }
    } finally {
      setUploading(false)
    }
  }, [onError])

  // 处理保存
  const handleSave = useCallback((value: string, html: Promise<string>) => {
    if (onSave) {
      html.then(htmlContent => {
        onSave(value, htmlContent)
      })
    }
  }, [onSave])

  // 处理错误
  const handleError = useCallback((err: { name: string; message: string }) => {
    const error = new Error(err.message)
    error.name = err.name
    if (onError) {
      onError(error)
    }
  }, [maxLength, onError])

  // 自定义工具栏配置
  const toolbars = [
    'bold',
    'underline',
    'italic',
    '-',
    'title',
    'strikeThrough',
    'sub',
    'sup',
    'quote',
    'unorderedList',
    'orderedList',
    'task',
    '-',
    'codeRow',
    'code',
    'link',
    'image',
    'table',
    'mermaid',
    'katex',
    '-',
    'revoke',
    'next',
    'save',
    '=',
    'pageFullscreen',
    'fullscreen',
    'preview',
    'previewOnly',
    'htmlPreview',
    'catalog'
  ].filter(item => !toolbarsExclude.includes(item))

  console.log('MarkdownEditor theme:', actualTheme)

  return (
    <div className="markdown-editor-container">
      <MdEditor
        editorId={editorId}
        modelValue={value}
        onChange={onChange}
        language={language}
        theme={actualTheme}
        previewTheme={previewTheme}
        codeTheme={codeTheme}
        placeholder={placeholder}
        readOnly={readOnly}
        autoFocus={autoFocus}
        disabled={uploading}
        maxLength={maxLength}
        showCodeRowNumber={showCodeRowNumber}
        toolbars={toolbars as any}
        onUploadImg={handleUploadImg}
        onSave={handleSave}
        onError={handleError}
        style={{ height }}
        footers={['markdownTotal', '=', 'scrollSwitch']}
      />
    </div>
  )
}

export default MarkdownEditor