#!/bin/bash
# scripts/try-aliyun-mirrors.sh
# 尝试使用阿里云各种镜像源拉取 Docker 镜像

set -e

echo "尝试使用阿里云各种镜像源..."

# 阿里云 ECS 内网镜像仓库（不需要登录）
ALIYUN_MIRRORS=(
    "registry.cn-hangzhou.aliyuncs.com/acs/python:3.11-slim"
    "registry.cn-hangzhou.aliyuncs.com/acs/node:18-alpine"
    "registry.cn-hangzhou.aliyuncs.com/acs/nginx:alpine"
)

# 阿里云公共代理（如果可用）
PUBLIC_MIRRORS=(
    "registry.cn-hangzhou.aliyuncs.com/google_containers/python:3.11-slim"
    "registry.cn-hangzhou.aliyuncs.com/google_containers/node:18-alpine"
    "registry.cn-hangzhou.aliyuncs.com/google_containers/nginx:alpine"
)

# 尝试拉取镜像
pull_image() {
    local image=$1
    local target=$2
    
    echo "尝试拉取: $image"
    if timeout 60 docker pull "$image" 2>/dev/null; then
        echo "✓ 成功拉取: $image"
        docker tag "$image" "$target"
        echo "✓ 已标记为: $target"
        return 0
    else
        echo "✗ 失败: $image"
        return 1
    fi
}

# 尝试拉取 Python 镜像
echo ""
echo "=== 拉取 Python 镜像 ==="
for mirror in "${ALIYUN_MIRRORS[@]}" "${PUBLIC_MIRRORS[@]}"; do
    if [[ "$mirror" == *"python"* ]]; then
        pull_image "$mirror" "python:3.11-slim" && break
    fi
done

# 尝试拉取 Node 镜像
echo ""
echo "=== 拉取 Node 镜像 ==="
for mirror in "${ALIYUN_MIRRORS[@]}" "${PUBLIC_MIRRORS[@]}"; do
    if [[ "$mirror" == *"node"* ]]; then
        pull_image "$mirror" "node:18-alpine" && break
    fi
done

# 尝试拉取 Nginx 镜像
echo ""
echo "=== 拉取 Nginx 镜像 ==="
for mirror in "${ALIYUN_MIRRORS[@]}" "${PUBLIC_MIRRORS[@]}"; do
    if [[ "$mirror" == *"nginx"* ]]; then
        pull_image "$mirror" "nginx:alpine" && break
    fi
done

# 尝试拉取 Certbot
echo ""
echo "=== 拉取 Certbot 镜像 ==="
pull_image "registry.cn-hangzhou.aliyuncs.com/acs/certbot:latest" "certbot/certbot" || \
pull_image "registry.cn-hangzhou.aliyuncs.com/google_containers/certbot:latest" "certbot/certbot" || \
echo "Certbot 镜像拉取失败，将使用其他方式获取 SSL 证书"

echo ""
echo "=== 镜像拉取完成 ==="
docker images | grep -E "(python|node|nginx|certbot)" | head -10
