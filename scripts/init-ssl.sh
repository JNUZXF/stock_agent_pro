#!/bin/bash
# scripts/init-ssl.sh
# 初始化 SSL 证书脚本，用于首次部署时获取 Let's Encrypt 证书

set -e

DOMAIN="stockagent.cc"
EMAIL="admin@stockagent.cc"  # 请修改为您的邮箱地址

echo "开始初始化 SSL 证书..."

# 创建必要的目录
mkdir -p nginx/ssl
mkdir -p certbot/www

# 临时启动 Nginx（仅 HTTP，用于验证）
echo "启动临时 Nginx 服务用于证书验证..."
docker compose -f docker-compose.prod.yml up -d nginx

# 等待 Nginx 启动
sleep 5

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
  -d "www.$DOMAIN"

# 复制证书到 nginx/ssl 目录（如果需要）
echo "证书获取完成！"

# 重启 Nginx 以加载 SSL 配置
echo "重启 Nginx 以加载 SSL 配置..."
docker compose -f docker-compose.prod.yml restart nginx

echo "SSL 证书初始化完成！"
echo "请确保域名 $DOMAIN 和 www.$DOMAIN 已正确解析到服务器 IP: 47.113.101.218"
