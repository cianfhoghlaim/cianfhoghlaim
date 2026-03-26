set URLS=http://localhost:5085
REM 每个用户AI处理文档生成的最大并行数量
SET TASK_MAX_SIZE_PER_USER=5
REM 必须要支持function的模型
SET CHAT_MODEL=DeepSeek-V3
REM 分析模型，用于生成仓库目录结构
SET ANALYSIS_MODEL=
REM 您的APIkey
SET CHAT_API_KEY=
REM 设置生成语言默认为"中文"
SET LANGUAGE=
SET ENDPOINT=https://api.openai.com/v1
SET DB_TYPE=sqlite
REM 模型提供商，默认为OpenAI 支持AzureOpenAI和Anthropic
SET MODEL_PROVIDER=OpenAI
SET DB_CONNECTION_STRING=Data Source=./KoalaWiki.db
REM 是否启用智能过滤，这可能影响AI得到仓库的文件目录
SET EnableSmartFilter=true
REM 仓库增量更新间隔，单位天
SET UPDATE_INTERVAL=5
REM 上传文件的最大限制，单位MB
SET MAX_FILE_LIMIT=100
REM 深度研究模型，为空使用CHAT_MODEL
SET DEEP_RESEARCH_MODEL=
REM 是否启用增量更新
SET ENABLE_INCREMENTAL_UPDATE=true

REM 构建前端项目
echo Building frontend...
cd web-site
if not exist node_modules (
    echo Installing frontend dependencies...
    npm install
)
echo Building frontend project...
npm run build
cd ..

"KoalaWiki.exe"