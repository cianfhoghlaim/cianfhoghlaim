@echo off
chcp 65001 >nul
echo 开始构建KoalaWiki项目...

REM 构建前端到wwwroot目录
echo 构建前端...
cd web-site
call npm install
call npm run build
cd ..

REM 构建后端
echo 构建后端...
dotnet publish KoalaWiki.sln -c Release -o output\backend

REM 复制启动脚本
copy ".\start-backend.bat" ".\output\" >nul

echo KoalaWiki项目构建完成！
echo 后端输出目录: %cd%\output\backend
echo 前端已构建到: %cd%\src\KoalaWiki\wwwroot

pause