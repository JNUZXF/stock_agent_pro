#!/bin/bash
# scripts/deploy-without-docker.sh
# 不使用 Docker 的生产环境部署脚本（直接使用系统服务）

set -e

DOMAIN="stockagent.cc"
EMAIL="admin@stockagent.cc"

echo "=========================================="
echo "开始部署 Stock Agent（非 Docker 方式）"
echo "域名: $DOMAIN"
echo "=========================================="

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $PYTHON_VERSION"

# 检查是否需要安装 Python 3.8+
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "✓ Python 版本满足要求"
    PYTHON_CMD=python3
else
    echo "⚠ Python 版本过低，尝试安装 Python 3.8+..."
    
    # 尝试使用 pyenv 或从源码安装
    if command -v yum &> /dev/null; then
        # CentOS/RHEL
        echo "尝试安装 Python 3.8..."
        yum install -y python38 python38-pip python38-devel || {
            echo "无法自动安装 Python 3.8，请手动安装"
            echo "参考: https://www.python.org/downloads/"
            exit 1
        }
        PYTHON_CMD=python3.8
    elif command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        echo "尝试安装 Python 3.8..."
        apt-get update
        apt-get install -y python3.8 python3.8-venv python3.8-dev || {
            echo "无法自动安装 Python 3.8，请手动安装"
            exit 1
        }
        PYTHON_CMD=python3.8
    else
        echo "错误: 无法确定包管理器，请手动安装 Python 3.8+"
        exit 1
    fi
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "错误: Node.js 未安装"
    exit 1
fi
echo "Node.js 版本: $(node --version)"

# 检查 Nginx
if ! command -v nginx &> /dev/null; then
    echo "安装 Nginx..."
    yum install -y nginx || apt-get update && apt-get install -y nginx
fi
echo "Nginx 版本: $(nginx -v 2>&1)"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "错误: .env 文件不存在"
    exit 1
fi

# 部署后端
echo ""
echo "部署后端服务..."
cd backend

# 创建虚拟环境
if [ ! -d ".venv" ]; then
    $PYTHON_CMD -m venv .venv
fi

source .venv/bin/activate

# 安装依赖
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 创建 systemd 服务文件
sudo tee /etc/systemd/system/stock-agent-backend.service > /dev/null <<EOF
[Unit]
Description=Stock Agent Backend Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/.venv/bin"
ExecStart=$(pwd)/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable stock-agent-backend
sudo systemctl restart stock-agent-backend

echo "✓ 后端服务已启动"

# 部署前端
echo ""
echo "部署前端服务..."
cd ../frontend

# 配置 npm 镜像源
npm config set registry https://registry.npmmirror.com

# 安装依赖并构建
if [ ! -d "node_modules" ]; then
    npm install
fi

npm run build

# 复制构建产物到 Nginx 目录
sudo rm -rf /usr/share/nginx/html/stock-agent
sudo mkdir -p /usr/share/nginx/html/stock-agent
sudo cp -r dist/* /usr/share/nginx/html/stock-agent/

echo "✓ 前端已构建并部署"

# 配置 Nginx
echo ""
echo "配置 Nginx..."
cd ..

sudo tee /etc/nginx/conf.d/stock-agent.conf > /dev/null <<EOF
# HTTP 服务器 - 重定向到 HTTPS
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Let's Encrypt 验证路径
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # 其他所有请求重定向到 HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS 服务器
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL 证书配置（稍后配置）
    # ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    root /usr/share/nginx/html/stock-agent;
    index index.html;

    # 前端路由支持（SPA）
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # API 代理到后端
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # SSE 流式响应支持
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding on;
    }
}
EOF

# 测试 Nginx 配置
sudo nginx -t

# 启动 Nginx
sudo systemctl enable nginx
sudo systemctl restart nginx

echo "✓ Nginx 已配置并启动"

# 获取 SSL 证书
echo ""
echo "获取 SSL 证书..."
if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    # 安装 certbot
    if ! command -v certbot &> /dev/null; then
        yum install -y certbot python3-certbot-nginx || \
        apt-get update && apt-get install -y certbot python3-certbot-nginx
    fi

    # 获取证书
    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $EMAIL
else
    echo "SSL 证书已存在"
fi

# 重启 Nginx 加载 SSL
sudo systemctl restart nginx

echo ""
echo "=========================================="
echo "部署完成！"
echo "访问地址: https://$DOMAIN"
echo "=========================================="
echo ""
echo "服务管理命令："
echo "  查看后端状态: sudo systemctl status stock-agent-backend"
echo "  查看后端日志: sudo journalctl -u stock-agent-backend -f"
echo "  重启后端: sudo systemctl restart stock-agent-backend"
echo "  重启 Nginx: sudo systemctl restart nginx"
