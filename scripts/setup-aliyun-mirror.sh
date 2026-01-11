#!/bin/bash
# scripts/setup-aliyun-mirror.sh
# 配置阿里云容器镜像服务加速器

set -e

echo "=========================================="
echo "配置阿里云容器镜像服务加速器"
echo "=========================================="

# 提示用户输入加速器地址
echo ""
echo "请按照以下步骤获取您的专属镜像加速器地址："
echo ""
echo "1. 登录阿里云控制台：https://cr.console.aliyun.com/"
echo "2. 点击左侧菜单「镜像工具」->「镜像加速器」"
echo "3. 选择「Docker Hub 加速」标签页"
echo "4. 复制您的专属加速器地址（格式：https://xxxxx.mirror.aliyuncs.com）"
echo ""
read -p "请输入您的专属镜像加速器地址: " MIRROR_URL

if [ -z "$MIRROR_URL" ]; then
    echo "错误: 镜像加速器地址不能为空"
    exit 1
fi

# 验证地址格式
if [[ ! "$MIRROR_URL" =~ ^https?://.*\.mirror\.aliyuncs\.com$ ]]; then
    echo "警告: 地址格式可能不正确，但继续配置..."
fi

# 备份现有配置
if [ -f /etc/docker/daemon.json ]; then
    cp /etc/docker/daemon.json /etc/docker/daemon.json.bak.$(date +%Y%m%d_%H%M%S)
    echo "已备份现有配置"
fi

# 创建或更新配置
mkdir -p /etc/docker
cat > /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": ["${MIRROR_URL}"],
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF

echo ""
echo "配置已更新："
cat /etc/docker/daemon.json

# 重启 Docker 服务
echo ""
echo "正在重启 Docker 服务..."
systemctl daemon-reload
systemctl restart docker

# 等待 Docker 启动
sleep 3

# 验证配置
echo ""
echo "验证配置..."
if docker info 2>/dev/null | grep -q "Registry Mirrors"; then
    echo "✓ Docker 镜像加速器配置成功！"
    echo ""
    echo "当前配置的镜像加速器："
    docker info 2>/dev/null | grep -A 5 "Registry Mirrors"
    echo ""
    echo "测试镜像拉取..."
    if timeout 30 docker pull hello-world >/dev/null 2>&1; then
        echo "✓ 镜像拉取测试成功！"
        docker rmi hello-world >/dev/null 2>&1
    else
        echo "⚠ 镜像拉取测试失败，请检查网络连接"
    fi
else
    echo "✗ 配置可能未生效，请检查 Docker 服务状态"
    systemctl status docker | head -5
fi

echo ""
echo "=========================================="
echo "配置完成！"
echo "=========================================="
