#!/bin/bash

echo "开始构建KoalaWiki项目..."

# 构建前端到wwwroot目录
echo "构建前端..."
cd web-site
npm install
npm run build
cd ..

# 创建输出目录
mkdir -p output/backend

echo "构建后端..."
dotnet publish KoalaWiki.sln -c Release -o output/backend

# 复制启动脚本
cp "./start-backend.sh" "./output/" 2>/dev/null || true

echo "KoalaWiki项目构建完成！"
echo "后端输出目录: $(pwd)/output/backend"
echo "前端已构建到: $(pwd)/src/KoalaWiki/wwwroot"