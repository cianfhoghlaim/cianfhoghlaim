
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import {
  Github,
  Globe,
  BookOpen,
  Zap,
  Code2,
  Database,
  Languages,
  Shield,
  ArrowRight,
  Users,
  ExternalLink
} from 'lucide-react'

export const AboutPage = () => {
  const features = [
    {
      icon: <Zap className="h-5 w-5" />,
      title: '快速转换',
      description: '几分钟内将代码仓库转换为知识库'
    },
    {
      icon: <Languages className="h-5 w-5" />,
      title: '多语言支持',
      description: '支持所有编程语言的代码分析'
    },
    {
      icon: <Code2 className="h-5 w-5" />,
      title: '代码结构图',
      description: '自动生成 Mermaid 图表'
    },
    {
      icon: <Database className="h-5 w-5" />,
      title: '灵活存储',
      description: '支持多种数据库系统'
    },
    {
      icon: <Globe className="h-5 w-5" />,
      title: 'SEO 友好',
      description: '基于 Next.js 的文档生成'
    },
    {
      icon: <Shield className="h-5 w-5" />,
      title: 'MCP 协议',
      description: '可作为 AI 模型的知识源'
    }
  ]

  const techStack = [
    '.NET 9',
    'Semantic Kernel',
    'React',
    'TypeScript',
    'Tailwind CSS',
    'Docker'
  ]

  const stats = [
    { label: '代码仓库', value: '5+' },
    { label: '编程语言', value: '20+' },
    { label: '数据库', value: '4+' },
    { label: 'AI 提供商', value: '3+' }
  ]

  const workflowSteps = [
    '克隆代码仓库到本地',
    '读取配置文件并过滤',
    '扫描文件和目录结构',
    'AI 智能分析和过滤',
    '生成文档和知识图谱',
    '保存至数据库',
    '持续更新和优化'
  ]

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section - 极简设计 */}
      <section className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center">
          {/* Logo - 简洁呈现 */}
          <div className="mb-8">
            <img
              src="/favicon.png"
              alt="OpenDeepWiki"
              className="h-20 w-20 mx-auto"
            />
          </div>

          {/* 标题和描述 - 简洁明了 */}
          <h1 className="text-4xl font-semibold mb-4 text-foreground">
            OpenDeepWiki
          </h1>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            AI 驱动的代码知识库系统，将代码仓库转换为智能化的知识库
          </p>

          {/* 行动按钮 - 扁平设计 */}
          <div className="flex gap-4 justify-center">
            <Button
              variant="default"
              className="rounded-full"
              onClick={() => window.open('https://github.com/AIDotNet/OpenDeepWiki', '_blank')}
            >
              <Github className="mr-2 h-4 w-4" />
              GitHub
            </Button>
            <Button
              variant="outline"
              className="rounded-full"
              onClick={() => window.open('https://docs.opendeep.wiki', '_blank')}
            >
              <BookOpen className="mr-2 h-4 w-4" />
              文档
            </Button>
          </div>
        </div>
      </section>

      {/* 统计数据 - 极简网格 */}
      <section className="container mx-auto px-4 pb-20">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl font-semibold text-foreground mb-1">
                  {stat.value}
                </div>
                <div className="text-sm text-muted-foreground">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Separator className="container mx-auto" />

      {/* 项目介绍 - 简洁段落 */}
      <section className="container mx-auto px-4 py-20">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-semibold mb-6">关于项目</h2>
          <div className="space-y-4 text-muted-foreground leading-relaxed">
            <p>
              OpenDeepWiki 是一个开源项目，灵感来自 DeepWiki，基于 .NET 9 和 Semantic Kernel 开发。
            </p>
            <p>
              它旨在帮助开发者更好地理解和利用代码仓库，提供代码分析、文档生成和知识图谱构建等功能。
              通过 AI 技术，OpenDeepWiki 能够自动分析代码结构、理解仓库核心概念、生成代码文档。
            </p>
            <p>
              支持 MCP (Model Context Protocol) 协议，可以作为其他 AI 模型的知识源。
            </p>
          </div>
        </div>
      </section>

      <Separator className="container mx-auto" />

      {/* 核心功能 - 简约列表 */}
      <section className="container mx-auto px-4 py-20">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-semibold mb-8">核心功能</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature, index) => (
              <div key={index} className="flex gap-4">
                <div className="text-muted-foreground mt-1">
                  {feature.icon}
                </div>
                <div>
                  <h3 className="font-medium mb-1">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">
                    {feature.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Separator className="container mx-auto" />

      {/* 工作流程 - 简洁步骤 */}
      <section className="container mx-auto px-4 py-20">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-semibold mb-8">工作流程</h2>
          <div className="space-y-3">
            {workflowSteps.map((step, index) => (
              <div key={index} className="flex items-center gap-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-muted flex items-center justify-center text-xs text-muted-foreground">
                  {index + 1}
                </span>
                <span className="text-muted-foreground">{step}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Separator className="container mx-auto" />

      {/* 技术栈 - 简约标签 */}
      <section className="container mx-auto px-4 py-20">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-semibold mb-8">技术栈</h2>
          <div className="flex flex-wrap gap-2">
            {techStack.map((tech, index) => (
              <span
                key={index}
                className="px-3 py-1 text-sm border rounded-full text-muted-foreground"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      </section>

      <Separator className="container mx-auto" />

      {/* 社区 - 简洁链接 */}
      <section className="container mx-auto px-4 py-20">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-semibold mb-8">社区与支持</h2>

          <div className="space-y-8">
            {/* 社区链接 */}
            <div>
              <h3 className="font-medium mb-4">加入社区</h3>
              <div className="flex flex-wrap gap-3">
                <Button
                  variant="outline"
                  size="sm"
                  className="rounded-full"
                  onClick={() => window.open('https://discord.gg/Y3fvpnGVwt', '_blank')}
                >
                  <Users className="mr-2 h-4 w-4" />
                  Discord
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="rounded-full"
                  onClick={() => window.open('https://github.com/AIDotNet/OpenDeepWiki/issues', '_blank')}
                >
                  <Github className="mr-2 h-4 w-4" />
                  Issues
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="rounded-full"
                  onClick={() => window.open('https://github.com/AIDotNet/OpenDeepWiki/discussions', '_blank')}
                >
                  <ExternalLink className="mr-2 h-4 w-4" />
                  讨论区
                </Button>
              </div>
            </div>

            {/* 企业服务 */}
            <div>
              <h3 className="font-medium mb-4">企业服务</h3>
              <p className="text-sm text-muted-foreground mb-4">
                我们为企业提供专业的 AI 解决方案支持和服务。
              </p>
              <Button
                variant="outline"
                size="sm"
                className="rounded-full"
                onClick={() => window.open('https://docs.opendeep.wiki/pricing', '_blank')}
              >
                了解更多
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>

            {/* 开源协议 */}
            <div>
              <h3 className="font-medium mb-4">开源协议</h3>
              <p className="text-sm text-muted-foreground">
                本项目基于 MIT 协议开源，详情请查看{' '}
                <a
                  href="https://github.com/AIDotNet/OpenDeepWiki/blob/main/LICENSE"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline underline-offset-4 hover:text-foreground"
                >
                  LICENSE
                </a>
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 页脚 - 极简设计 */}
      <footer className="border-t">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-3xl mx-auto flex flex-col md:flex-row items-center justify-between text-sm text-muted-foreground">
            <p>© {new Date().getFullYear()} OpenDeepWiki</p>
            <div className="flex items-center gap-6 mt-4 md:mt-0">
              <a
                href="https://github.com/AIDotNet/OpenDeepWiki"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-foreground transition-colors"
              >
                GitHub
              </a>
              <a
                href="https://docs.opendeep.wiki"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-foreground transition-colors"
              >
                文档
              </a>
              <a
                href="https://discord.gg/Y3fvpnGVwt"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-foreground transition-colors"
              >
                Discord
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default AboutPage