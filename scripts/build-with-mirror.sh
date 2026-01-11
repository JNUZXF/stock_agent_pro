#!/bin/bash
# scripts/build-with-mirror.sh
# 使用国内镜像源构建 Docker 镜像

set -e

echo "开始使用国内镜像源构建 Docker 镜像..."

# 方法1: 直接使用镜像加速器（如果配置正确）
echo "方法1: 尝试使用镜像加速器..."
docker compose -f docker-compose.prod.yml build --progress=plain backend frontend 2>&1 | tee /tmp/build.log || {
    echo "方法1失败，尝试方法2..."
    
    # 方法2: 手动拉取基础镜像
    echo "方法2: 手动拉取基础镜像..."
    
    # 尝试多个镜像源
    for mirror in "hub-mirror.c.163.com" "mirror.baidubce.com"; do
        echo "尝试从 $mirror 拉取镜像..."
        docker pull ${mirror}/library/python:3.11-slim && docker tag ${mirror}/library/python:3.11-slim python:3.11-slim && break || continue
    done
    
    for mirror in "hub-mirror.c.163.com" "mirror.baidubce.com"; do
        echo "尝试从 $mirror 拉取镜像..."
        docker pull ${mirror}/library/node:18-alpine && docker tag ${mirror}/library/node:18-alpine node:18-alpine && break || continue
    done
    
    for mirror in "hub-mirror.c.163.com" "mirror.baidubce.com"; do
        echo "尝试从 $mirror 拉取镜像..."
        docker pull ${mirror}/library/nginx:alpine && docker tag ${mirror}/library/nginx:alpine nginx:alpine && break || continue
    done
    
    # 重新构建
    docker compose -f docker-compose.prod.yml build --progress=plain backend frontend
}

echo "构建完成！"
