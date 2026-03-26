# OpenDeepWiki

[中文](README.zh-CN.md) | [English](README.md)

<div align="center">
  <img src="/img/favicon.png" alt="OpenDeepWiki Logo" width="220" />
  <h3>AI驱动的代码知识库</h3>
</div>

---

# 企业服务
[企业服务定价](https://docs.opendeep.wiki/pricing)

我们的企业服务为寻求专业人工智能解决方案的各类企业提供全面的支持和灵活性。

---

# 功能 Features

- **快速转换**：支持将所有GitHub、GitLab、Gitee、Gitea等代码仓库几分钟内转换为知识库。
- **多语言支持**：支持所有编程语言的代码分析和文档生成。
- **代码结构图**：自动生成Mermaid图，帮助理解代码结构。
- **自定义模型支持**：支持自定义模型和自定义API，灵活扩展。
- **AI智能分析**：基于AI进行代码分析和代码关系理解。
- **SEO友好**：基于Next.js生成SEO友好型文档和知识库，方便搜索引擎抓取。
- **对话式交互**：支持与AI对话，获取代码详细信息和使用方法，深入理解代码。

---

# 特性清单 Feature List

- [x] 支持多代码仓库（GitHub、GitLab、Gitee、Gitea等）
- [x] 支持多编程语言（Python、Java、C#、JavaScript等）
- [x] 支持仓库管理（增删改查仓库）
- [x] 支持多AI提供商（OpenAI、AzureOpenAI、Anthropic等）
- [x] 支持多数据库（SQLite、PostgreSQL、SqlServer、MySQL等）
- [x] 支持多语言（中文、英文、法文等）
- [x] 支持上传ZIP文件和本地文件
- [x] 提供数据微调平台，生成微调数据集
- [x] 支持目录级仓库管理，动态生成目录和文档
- [x] 支持仓库目录修改管理
- [x] 支持用户管理（增删改查用户）
- [x] 支持用户权限管理
- [x] 支持仓库级别生成不同微调框架数据集

---

# 项目介绍 Project Introduction

OpenDeepWiki是一个开源项目，灵感来源于[DeepWiki](https://deepwiki.com/)，基于.NET 9和Semantic Kernel开发。旨在帮助开发者更好地理解和利用代码库，提供代码分析、文档生成和知识图谱构建等功能。

主要功能：

- 分析代码结构
- 理解仓库核心概念
- 生成代码文档
- 自动生成代码的README.md
- 支持MCP（Model Context Protocol）协议

---

# MCP支持

OpenDeepWiki支持MCP协议：

- 可以作为单仓库的MCPServer，进行仓库分析。

示例配置：

```json
{
  "mcpServers": {
    "OpenDeepWiki":{
      "url": "http://Your OpenDeepWiki service IP:port/api/mcp?owner=AIDotNet&name=OpenDeepWiki"
    }
  }
}
```

如果不支持mcp streamable http则使用下面格式：

```json
{
  "mcpServers": {
    "OpenDeepWiki":{
      "url": "http://Your OpenDeepWiki service IP:port/api/mcp/sse?owner=AIDotNet&name=OpenDeepWiki",
      "supportsStreamableHttp": false
    }
  }
}
```

**MCP Streamable 配置**

您可以使用 `MCP_STREAMABLE` 环境变量为特定服务配置 MCP streamable 支持：

```yaml
environment:
  # 格式: 服务名称1=streamableUrl1,服务名称2=streamableUrl2
  - MCP_STREAMABLE=claude=http://localhost:8080/api/mcp,windsurf=http://localhost:8080/api/mcp
```

这允许您指定哪些服务应该使用 streamable HTTP 端点及其对应的 URL。

- owner：仓库所属组织或拥有者名称
- name：仓库名称

添加仓库后，可通过提问测试，如“什么是OpenDeepWiki？”，效果如下图所示：

![](img/mcp.png)

这样，OpenDeepWiki可作为MCPServer，供其他AI模型调用，方便分析和理解开源项目。

---

# 🚀 快速开始 Quick Start

1. 克隆仓库

```bash
git clone https://github.com/AIDotNet/OpenDeepWiki.git
cd OpenDeepWiki
```

2. 修改 `docker-compose.yml` 中环境变量配置：

- OpenAI示例：

```yaml
services:
  koalawiki:
    environment:
      - TASK_MAX_SIZE_PER_USER=2 # AI每用户最大并行文档生成任务数
      - CHAT_MODEL=DeepSeek-V3 # 模型需支持函数调用
      - ANALYSIS_MODEL= # 用于生成仓库目录结构的分析模型
      - CHAT_API_KEY= # 你的API Key
      - LANGUAGE= # 默认生成语言，如“Chinese”
      - ENDPOINT=https://api.token-ai.cn/v1
      - DB_TYPE=sqlite
      - MODEL_PROVIDER=OpenAI # 模型提供商，支持OpenAI、AzureOpenAI
      - DB_CONNECTION_STRING=Data Source=/data/KoalaWiki.db
      - EnableSmartFilter=true # 是否启用智能过滤，影响AI获取仓库文件目录能力
      - UPDATE_INTERVAL=5 # 仓库增量更新间隔，单位天
      - MAX_FILE_LIMIT=100 # 上传文件最大限制，单位MB
      - DEEP_RESEARCH_MODEL= # 深度研究模型，空则使用CHAT_MODEL
      - ENABLE_INCREMENTAL_UPDATE=true # 是否启用增量更新
      - ENABLE_CODED_DEPENDENCY_ANALYSIS=false # 是否启用代码依赖分析，可能影响代码质量
      - ENABLE_WAREHOUSE_COMMIT=true # 是否启用仓库提交
      - ENABLE_FILE_COMMIT=true # 是否启用文件提交
      - REFINE_AND_ENHANCE_QUALITY=false # 是否精炼并提高质量
      - CATALOGUE_FORMAT=compact # 目录结构格式 (compact, json, pathlist, unix)
      - CUSTOM_BODY_PARAMS= # 自定义请求body参数，格式: key1=value1,key2=value2 (例如: stop=<|im_end|>,max_tokens=4096)
      - READ_MAX_TOKENS=100000 # AI最大文件读取token数量限制，防止无限制读取文件，建议填写模型最大token的百分之七十
      - MCP_STREAMABLE= # MCP服务streamable配置，格式: 服务名=streamableUrl (例如: claude=http://localhost:8080/api/mcp,windsurf=http://localhost:8080/api/mcp)
      # 自动上下文压缩配置（可选）
      - AUTO_CONTEXT_COMPRESS_ENABLED=false # 是否启用AI智能上下文压缩
      - AUTO_CONTEXT_COMPRESS_TOKEN_LIMIT=100000 # 触发压缩的token上限（启用时必填）
      - AUTO_CONTEXT_COMPRESS_MAX_TOKEN_LIMIT=200000 # 允许的最大token上限（默认: 200000）
      # 飞书 Bot 配置（可选，如需接入飞书）
      - FeishuAppId=
      - FeishuAppSecret=
      - FeishuBotName=KoalaWiki
```

- AzureOpenAI和Anthropic配置类似，仅需调整 `ENDPOINT` 和 `MODEL_PROVIDER`。

## 数据库配置

### SQLite (默认)
```yaml
- DB_TYPE=sqlite
- DB_CONNECTION_STRING=Data Source=/data/KoalaWiki.db
```

### PostgreSQL
```yaml
- DB_TYPE=postgres
- DB_CONNECTION_STRING=Host=localhost;Database=KoalaWiki;Username=postgres;Password=password
```

### SQL Server
```yaml
- DB_TYPE=sqlserver
- DB_CONNECTION_STRING=Server=localhost;Database=KoalaWiki;Trusted_Connection=true;
```

### MySQL
```yaml
- DB_TYPE=mysql
- DB_CONNECTION_STRING=Server=localhost;Database=KoalaWiki;Uid=root;Pwd=password;
```

3. 启动服务

使用Makefile命令：

```bash
# 构建所有Docker镜像
make build

# 后台启动所有服务
make up

# 开发模式启动（可见日志）
make dev
```

访问 http://localhost:8090 进入知识库页面。

Windows用户无make环境，可直接使用Docker Compose：

```bash
docker-compose build
docker-compose up -d
docker-compose up
docker-compose down
docker-compose logs -f
```

---

# 部署建议

- 构建特定架构：

```bash
docker-compose build --build-arg ARCH=arm64
docker-compose build --build-arg ARCH=amd64
```

- 仅构建后端或前端：

```bash
docker-compose build koalawiki
docker-compose build koalawiki-web
```

- 一键部署到Sealos（支持公网访问）：

[![Deploy on Sealos](https://raw.githubusercontent.com/labring-actions/templates/main/Deploy-on-Sealos.svg)](https://bja.sealos.run/?openapp=system-template%3FtemplateName%3DOpenDeepWiki)

详细步骤请参考：[Sealos一键部署OpenDeepWiki](scripts/sealos/README.zh-CN.md)

---

# 🔍 工作原理 How It Works

OpenDeepWiki利用AI实现：

- 克隆代码仓库本地
- 读取.gitignore配置，忽略无关文件
- 递归扫描目录获取所有文件和目录
- 判断文件数量是否超过阈值，超过则调用AI模型智能过滤目录
- 解析AI返回的目录JSON数据
- 生成或更新README.md
- 调用AI模型生成仓库分类信息与项目总览
- 清理项目分析标签内容并保存项目总览到数据库
- 调用AI生成思考目录（任务列表）
- 递归处理目录任务，生成文档目录结构
- 保存目录结构到数据库
- 处理未完成的文档任务
- 若为Git仓库，清理旧提交记录，调用AI生成更新日志并保存

---

# OpenDeepWiki 仓库解析成文档详细流程图

```mermaid
graph TD
    A[克隆代码仓库] --> B[读取.gitignore配置忽略文件]
    B --> C[递归扫描目录获取所有文件和目录]
    C --> D{文件数量是否超过阈值}
    D -- 否 --> E[直接返回目录结构]
    D -- 是 --> F[调用AI模型进行目录结构智能过滤]
    F --> G[解析AI返回的目录JSON数据]
    E --> G
    G --> H[生成或更新README.md]
    H --> I[调用AI模型生成仓库分类信息]
    I --> J[调用AI模型生成项目总览信息]
    J --> K[清理项目分析标签内容]
    K --> L[保存项目总览到数据库]
    L --> M[调用AI生成思考目录任务列表]
    M --> N[递归处理目录任务，生成DocumentCatalog]
    N --> O[保存目录结构到数据库]
    O --> P[处理未完成的文档任务]
    P --> Q{仓库类型是否为Git}
    Q -- 是 --> R[清理旧的提交记录]
    R --> S[调用AI生成更新日志]
    S --> T[保存更新日志到数据库]
    Q -- 否 --> T
```

---

# 高级配置 Advanced Configuration

## 环境变量 Environment Variables

- `KOALAWIKI_REPOSITORIES`：仓库存储路径
- `TASK_MAX_SIZE_PER_USER`：AI每用户最大并行文档生成任务数
- `CHAT_MODEL`：聊天模型（需支持函数调用）
- `ENDPOINT`：API端点
- `ANALYSIS_MODEL`：用于生成仓库目录结构的分析模型
- `CHAT_API_KEY`：API密钥
- `LANGUAGE`：生成文档语言
- `DB_TYPE`：数据库类型，支持sqlite、postgres、sqlserver、mysql（默认：sqlite）
- `MODEL_PROVIDER`：模型提供商，默认OpenAI，支持AzureOpenAI、Anthropic
- `DB_CONNECTION_STRING`：数据库连接字符串
- `EnableSmartFilter`：是否启用智能过滤，影响AI获取仓库目录能力
- `UPDATE_INTERVAL`：仓库增量更新间隔（天）
- `MAX_FILE_LIMIT`：上传文件最大限制（MB）
- `DEEP_RESEARCH_MODEL`：深度研究模型，空则使用CHAT_MODEL
- `ENABLE_INCREMENTAL_UPDATE`：是否启用增量更新
- `ENABLE_CODED_DEPENDENCY_ANALYSIS`：是否启用代码依赖分析，可能影响代码质量
- `ENABLE_WAREHOUSE_COMMIT`：是否启用仓库提交
- `ENABLE_FILE_COMMIT`：是否启用文件提交
- `REFINE_AND_ENHANCE_QUALITY`：是否精炼并提高质量
- `ENABLE_WAREHOUSE_FUNCTION_PROMPT_TASK`：是否启用仓库功能提示任务
- `ENABLE_WAREHOUSE_DESCRIPTION_TASK`：是否启用仓库描述任务
- `CATALOGUE_FORMAT`：目录结构格式 (compact, json, pathlist, unix)
- `ENABLE_CODE_COMPRESSION`：是否启用代码压缩
- `CUSTOM_BODY_PARAMS`：自定义请求body参数，格式：`key1=value1,key2=value2`(例如：`stop=<|im_end|>,max_tokens=4096`)。这些参数将被添加到所有AI模型API请求中
- `READ_MAX_TOKENS`：AI最大文件读取token数量限制，防止无限制读取文件，建议填写模型最大token的百分之七十（默认：100000）
- `MAX_FILE_READ_COUNT`：AI最大文件读取数量限制，防止无限制读取文件，提高处理效率（默认：10，0表示不限制）
- `AUTO_CONTEXT_COMPRESS_ENABLED`：是否启用AI智能上下文压缩功能，用于处理长对话（默认：false）
- `AUTO_CONTEXT_COMPRESS_TOKEN_LIMIT`：触发上下文压缩的token阈值。启用压缩时必填（默认：100000）
- `AUTO_CONTEXT_COMPRESS_MAX_TOKEN_LIMIT`：允许的最大token上限，确保token限制不超过模型能力（默认：200000）

**智能上下文压缩功能特性：**
使用**提示词编码压缩** - 超高密度结构化格式，实现90%+压缩率，同时保留所有关键信息。

**压缩策略：**
```
100条消息 (50k tokens) → 1个编码快照 (3k tokens)
压缩率: 94% ✨
```

**完全保留的内容 (100%)：**
- **系统消息**：所有系统级指令
- **函数调用和结果**：完整的工具调用历史（完整保留核心行为）
- **最近对话**：最近30%的消息保持原始形式

**编码压缩的内容（较早的消息）：**
不是选择/删除消息，而是将较早的消息压缩为超密集的结构化快照：

```markdown
## CONTEXT_SNAPSHOT
### FILES
✓ src/File.cs:modified(L:25-48) → README.md:pending

### TASKS
✓ 实现功能X ✓ 修复bug Y → 添加测试（待办）

### TECH_STACK
IChatClient, Semantic Kernel, AutoContextCompress, TokenHelper

### DECISIONS
[D1] 使用消息筛选: 保留结构
[D2] 保留30%最近消息: 基于Google Gemini最佳实践

### CODE_PATTERNS
```cs
if (message.Contents.Any(c => c is FunctionCallContent)) { ... }
```

### USER_INTENT
通过环境变量实现可配置压缩。必须保留核心行为。

### NEXT_ACTIONS
1. 更新文档 2. 添加单元测试
```

**编码格式特性：**
- ✓ 超高密度：使用符号（✓=完成, →=待办, ✗=阻塞）
- ✓ 结构化：8个语义分区（FILES, TASKS, TECH_STACK等）
- ✓ 精确：保留文件路径、行号、函数名、决策
- ✓ 可操作：明确AI继续工作的下一步
- ✓ 无损：所有关键信息编码，零丢失

**核心优势：**
- ✅ 90-95%压缩率（vs 消息筛选的30-40%）
- ✅ 函数调用和结果零丢失
- ✅ 保持时间上下文（最近消息不变）
- ✅ AI可以从快照重构完整理解
- ✅ 一个快照替代数百条消息
- `FeishuAppId`：飞书应用 App ID（启用飞书 Bot 必填）
- `FeishuAppSecret`：飞书应用 App Secret（启用飞书 Bot 必填）
- `FeishuBotName`：飞书机器人显示名称（可选）

---

# 飞书 Bot 集成 Feishu Bot

- 功能：将当前代码仓库接入飞书群聊/私聊，作为知识机器人进行问答与内容推送。
- 回调地址：`/api/feishu-bot/{owner}/{name}`（在仓库页面右上角「飞书Bot」按钮内可复制完整 URL）。
- 要求：服务需公网可访问；暂不支持消息加密（Encrypt Key）。

## 一、在飞书开放平台创建应用

- 类型：企业自建应用（组织内部使用）。
- 能力：开启“机器人”能力；在“应用发布”中发布为企业可见并安装到企业。
- 权限（根据平台提示勾选，至少包含）：
  - 消息发送与相关权限（例如：im:message、im:message:send_as_bot 等）。
  - 事件订阅相关权限（用于接收消息事件）。

## 二、配置事件订阅（重要）

- 打开“事件订阅”，关闭“加密（Encrypt Key）”。
- 订阅事件：`im.message.receive_v1`。
- 请求网址（Request URL）：`https://你的域名/api/feishu-bot/{owner}/{name}`。
  - `{owner}` 为仓库所属组织或拥有者名称，如 `AIDotNet`。
  - `{name}` 为仓库名称，如 `OpenDeepWiki`。
- 保存后完成“URL 验证”（平台会下发 challenge，后端已内置处理）。

提示：也可在 Web 端仓库页面右上角点击「飞书Bot」，一键复制专属回调地址。

## 三、配置服务端环境变量

在后端服务中设置以下环境变量（docker-compose 可参考下方示例）：

- `FeishuAppId`：飞书应用 App ID
- `FeishuAppSecret`：飞书应用 App Secret
- `FeishuBotName`：机器人显示名称（可选）

## 四、将机器人拉入群聊并使用

- 安装应用到企业后，将机器人拉入目标群聊。
- 群聊：@机器人 + 提问（将使用对应仓库的知识进行回答）。
- 私聊：直接发送问题即可。
- 支持文本与图片回复（如思维导图等内容）。

## 常见问题 FAQ（飞书）

- 无响应/回调失败：确认 Request URL 可被公网访问，且 Nginx 将 `/api/` 代理到后端。
- “已开启加密”提示：关闭 Encrypt Key（当前版本不支持加密消息）。
- 403/权限不足：确认应用已安装到企业，并授予所需权限与事件订阅。

## 构建不同架构 Build for Different Architectures

Makefile命令：

```bash
make build-arm    # ARM架构
make build-amd    # AMD架构
make build-backend-arm   # 仅后端ARM
make build-frontend-amd  # 仅前端AMD
```

---

# 交流社区 Community

- Discord: [join us](https://discord.gg/Y3fvpnGVwt)
- 飞书交流群二维码：

![飞书交流群](/img/feishu.png)

![微信交流群](https://github.com/user-attachments/assets/cb346569-2635-4038-a5cd-1c14485da7b2)

---

# 📄 许可证 License

本项目采用 MIT 许可证，详情见 [LICENSE](./LICENSE)。

---

# ⭐ Star历史 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=AIDotNet/OpenDeepWiki&type=Date)](https://www.star-history.com/#AIDotNet/OpenDeepWiki&Date)
