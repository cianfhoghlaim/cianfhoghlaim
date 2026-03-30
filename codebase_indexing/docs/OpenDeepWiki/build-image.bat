@echo off
echo ===========================================
echo Building KoalaWiki Docker Image
echo ===========================================

REM Enable Docker Buildx
echo Enabling Docker Buildx...
docker buildx create --use

REM Build frontend first
echo Building frontend...
pushd web-site
call npm install
call npm run build
popd

REM Build backend image (includes frontend static files)
echo Building backend image with frontend...
docker buildx build ^
    --platform linux/amd64,linux/arm64 ^
    -t crpi-j9ha7sxwhatgtvj4.cn-shenzhen.personal.cr.aliyuncs.com/koala-ai/koala-wiki ^
    -f src/KoalaWiki/Dockerfile ^
    --push .
if %ERRORLEVEL% NEQ 0 (
    echo Error building backend image!
    exit /b %ERRORLEVEL%
)

echo ===========================================
echo Image built and pushed successfully!
echo ===========================================

