#!/bin/bash

export URLS=http://localhost:5085
# 每个用户AI处理文档生成的最大并行数量
export TASK_MAX_SIZE_PER_USER=5
# 必须要支持function的模型
export CHAT_MODEL=DeepSeek-V3
# 分析模型，用于生成仓库目录结构
export ANALYSIS_MODEL=
# 您的APIkey
export CHAT_API_KEY=
# 设置生成语言默认为"中文"
export LANGUAGE=
export ENDPOINT=https://api.openai.com/v1
export DB_TYPE=sqlite
# 模型提供商，默认为OpenAI 支持AzureOpenAI和Anthropic
export MODEL_PROVIDER=OpenAI
export DB_CONNECTION_STRING="Data Source=./KoalaWiki.db"
# 是否启用智能过滤，这可能影响AI得到仓库的文件目录
export EnableSmartFilter=true
# 仓库增量更新间隔，单位天
export UPDATE_INTERVAL=5
# 上传文件的最大限制，单位MB
export MAX_FILE_LIMIT=100
# 深度研究模型，为空使用CHAT_MODEL
export DEEP_RESEARCH_MODEL=
# 是否启用增量更新
export ENABLE_INCREMENTAL_UPDATE=true

# 构建前端项目
echo "Building frontend..."
cd web-site
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi
echo "Building frontend project..."
npm run build
cd ..

./KoalaWiki