#!/bin/bash
# 通过新加坡服务器克隆 GitHub 项目的自动化脚本

SINGAPORE_IP="47.237.167.77"
PROJECT_URL="https://github.com/JNUZXF/stock_agent.git"
PROJECT_NAME="stock_agent"
TARGET_DIR="/home"

echo "=== 通过新加坡服务器克隆 GitHub 项目 ==="
echo "新加坡服务器: ${SINGAPORE_IP}"
echo "项目: ${PROJECT_URL}"
echo ""

# 检查 SSH 连接
echo "[1/4] 检查新加坡服务器 SSH 连接..."
if ssh -o ConnectTimeout=5 -o BatchMode=yes root@${SINGAPORE_IP} "echo 'SSH连接成功'" 2>/dev/null; then
    echo "✓ SSH 连接正常"
else
    echo "✗ SSH 连接失败，请确保："
    echo "  1. 已配置 SSH 密钥认证，或"
    echo "  2. 可以使用密码登录"
    echo ""
    echo "请手动执行以下步骤："
    echo ""
    echo "【在新加坡服务器上执行】"
    echo "  ssh root@${SINGAPORE_IP}"
    echo "  cd /tmp"
    echo "  git clone ${PROJECT_URL}"
    echo "  tar -czf ${PROJECT_NAME}.tar.gz ${PROJECT_NAME}/"
    echo ""
    echo "【在当前服务器（阿里云）上执行】"
    echo "  scp root@${SINGAPORE_IP}:/tmp/${PROJECT_NAME}.tar.gz ${TARGET_DIR}/"
    echo "  cd ${TARGET_DIR} && tar -xzf ${PROJECT_NAME}.tar.gz"
    exit 1
fi

# 在新加坡服务器上克隆项目
echo ""
echo "[2/4] 在新加坡服务器上克隆项目..."
ssh root@${SINGAPORE_IP} << 'REMOTE_SCRIPT'
    cd /tmp
    rm -rf stock_agent stock_agent.tar.gz 2>/dev/null
    echo "正在克隆项目..."
    if git clone https://github.com/JNUZXF/stock_agent.git 2>&1; then
        echo "✓ 克隆成功"
        tar -czf stock_agent.tar.gz stock_agent/
        echo "✓ 打包完成: /tmp/stock_agent.tar.gz"
        ls -lh /tmp/stock_agent.tar.gz
    else
        echo "✗ 克隆失败"
        exit 1
    fi
REMOTE_SCRIPT

if [ $? -ne 0 ]; then
    echo "✗ 在新加坡服务器上克隆失败"
    exit 1
fi

# 从新加坡服务器下载到当前服务器
echo ""
echo "[3/4] 从新加坡服务器下载项目..."
if scp root@${SINGAPORE_IP}:/tmp/stock_agent.tar.gz ${TARGET_DIR}/ 2>&1; then
    echo "✓ 下载成功"
else
    echo "✗ 下载失败"
    exit 1
fi

# 解压项目
echo ""
echo "[4/4] 解压项目..."
cd ${TARGET_DIR}
if [ -d "${PROJECT_NAME}" ]; then
    echo "检测到已存在的 ${PROJECT_NAME} 目录，备份为 ${PROJECT_NAME}.backup"
    mv ${PROJECT_NAME} ${PROJECT_NAME}.backup
fi

if tar -xzf ${PROJECT_NAME}.tar.gz 2>&1; then
    echo "✓ 解压成功"
    rm -f ${PROJECT_NAME}.tar.gz
    echo "✓ 清理临时文件完成"
    echo ""
    echo "项目已成功克隆到: ${TARGET_DIR}/${PROJECT_NAME}"
    echo ""
    ls -la ${TARGET_DIR}/${PROJECT_NAME} | head -10
else
    echo "✗ 解压失败"
    exit 1
fi

echo ""
echo "=== 完成 ==="
