#!/bin/bash
# scripts/deploy.sh
# 生产环境部署脚本

set -e

DOMAIN="finagent.asia"
EMAIL="admin@finagent.asia"  # Let's Encrypt 通知邮箱

echo "=========================================="
echo "开始部署 Stock Agent 到生产环境"
echo "域名: $DOMAIN"
echo "=========================================="

# 检查 Docker 镜像加速器配置
echo "检查 Docker 镜像加速器配置..."
if docker info 2>/dev/null | grep -q "Registry Mirrors"; then
    echo "✓ Docker 镜像加速器已配置"
    docker info 2>/dev/null | grep -A 5 "Registry Mirrors"
else
    echo "⚠ 警告: 未检测到 Docker 镜像加速器配置"
    echo "建议配置阿里云容器镜像服务，参考 ALIYUN_DEPLOY.md"
fi

# 测试镜像拉取
echo ""
echo "测试基础镜像拉取..."
if timeout 30 docker pull python:3.11-slim >/dev/null 2>&1; then
    echo "✓ Python 镜像拉取成功"
elif timeout 30 docker pull nginx:alpine >/dev/null 2>&1; then
    echo "✓ Nginx 镜像拉取成功"
else
    echo "⚠ 警告: 无法拉取 Docker 镜像"
    echo "请检查："
    echo "1. 网络连接是否正常"
    echo "2. Docker 镜像加速器是否配置正确"
    echo "3. 参考 ALIYUN_DEPLOY.md 配置阿里云容器镜像服务"
    echo ""
    read -p "是否继续部署？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "部署已取消"
        exit 1
    fi
fi

# 检查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "错误: .env 文件不存在，请先创建 .env 文件并配置必要的环境变量"
    exit 1
fi

# 检查域名解析
echo "检查域名解析..."
SERVER_IP=$(dig +short $DOMAIN | tail -n1)
if [ -z "$SERVER_IP" ]; then
    echo "警告: 无法解析域名 $DOMAIN，请确保域名已正确配置 DNS"
else
    echo "域名 $DOMAIN 解析到: $SERVER_IP"
fi

# 创建必要的目录
mkdir -p certbot/etc certbot/var certbot/www
mkdir -p nginx/ssl

# 检查 SSL 证书是否存在
if [ ! -d "certbot/etc/live/$DOMAIN" ]; then
    echo "SSL 证书不存在，开始初始化..."
    
    # 先启动 Nginx（仅 HTTP，用于 Let's Encrypt 验证）
    echo "启动临时 Nginx 服务用于证书验证..."
    docker compose -f docker-compose.prod.yml up -d nginx
    
    # 等待 Nginx 启动
    echo "等待 Nginx 启动..."
    sleep 10
    
    # 检查 Nginx 是否正常运行
    if ! docker compose -f docker-compose.prod.yml ps nginx | grep -q "Up"; then
        echo "错误: Nginx 启动失败，请检查日志"
        docker compose -f docker-compose.prod.yml logs nginx
        exit 1
    fi
    
    # 获取 SSL 证书
    echo "正在从 Let's Encrypt 获取 SSL 证书..."
    docker run --rm \
      -v "$(pwd)/certbot/etc:/etc/letsencrypt" \
      -v "$(pwd)/certbot/var:/var/lib/letsencrypt" \
      -v "$(pwd)/certbot/www:/var/www/certbot" \
      certbot/certbot certonly \
      --webroot \
      --webroot-path=/var/www/certbot \
      --email "$EMAIL" \
      --agree-tos \
      --no-eff-email \
      -d "$DOMAIN" \
      -d "www.$DOMAIN" || {
        echo "证书获取失败，请检查："
        echo "1. 域名是否正确解析到服务器 IP: 47.113.101.218"
        echo "2. 80 端口是否开放"
        echo "3. 防火墙设置是否正确"
        echo "4. Nginx 是否正常运行"
        docker compose -f docker-compose.prod.yml logs nginx
        exit 1
      }
    
    echo "SSL 证书获取成功！"
    
    # 重启 Nginx 以加载 SSL 配置
    echo "重启 Nginx 以加载 SSL 配置..."
    docker compose -f docker-compose.prod.yml restart nginx
else
    echo "SSL 证书已存在，跳过初始化步骤"
fi

# 构建并启动所有服务
echo "构建并启动所有服务..."
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker compose -f docker-compose.prod.yml ps

echo "=========================================="
echo "部署完成！"
echo "访问地址: https://$DOMAIN"
echo "=========================================="
