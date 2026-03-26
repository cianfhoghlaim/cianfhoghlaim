// 赞助商配置数据

export interface Sponsor {
  name: string
  logo: string
  url: string
  description: string
}

export const sponsors: Sponsor[] = [
  {
    name: 'AntSK',
    logo: 'https://antsk.cn/logo.ico',
    url: 'https://antsk.cn/',
    description: 'AI知识库和智能助手平台'
  },
  {
    name: '痴者工良',
    logo: 'https://www.whuanle.cn/wp-content/uploads/2020/04/image-1586681324216.png',
    url: 'https://www.whuanle.cn/',
    description: '技术博客和开发者社区'
  }
]