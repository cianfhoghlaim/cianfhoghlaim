#!/bin/bash

echo "==========================================="
echo "Building KoalaWiki Docker Image with BuildKit Multi-platform"
echo "==========================================="

# Enable Docker Buildx with a new builder that supports multi-platform builds
docker buildx create --name multiplatform-builder --use

# Build frontend first
echo "Building frontend..."
pushd web-site > /dev/null
npm install
npm run build
popd > /dev/null

# Build and push backend images for multiple platforms at once (includes frontend static files)
echo "Building and pushing backend image with frontend for multiple platforms..."
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -t crpi-j9ha7sxwhatgtvj4.cn-shenzhen.personal.cr.aliyuncs.com/koala-ai/koala-wiki:latest \
    -t crpi-j9ha7sxwhatgtvj4.cn-shenzhen.personal.cr.aliyuncs.com/koala-ai/koala-wiki:amd64 \
    -f src/KoalaWiki/Dockerfile \
    --push .

if [ $? -ne 0 ]; then
    echo "Error building and pushing backend image!"
    exit 1
fi

# Clean up the builder
docker buildx rm multiplatform-builder

echo "==========================================="
echo "Image built and pushed successfully!"
echo "==========================================="
