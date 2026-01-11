#!/bin/bash
# 配置 SSH 并克隆项目的完整方案

SINGAPORE_IP="47.237.167.77"
PROJECT_NAME="stock_agent"
TARGET_DIR="/home"

echo "=== 利用新加坡服务器克隆 GitHub 项目 ==="
echo ""

# 方案选择
echo "请选择认证方式："
echo "1. 使用 SSH 密钥（推荐，更安全）"
echo "2. 使用密码（需要手动输入）"
echo "3. 查看手动操作步骤"
read -p "请输入选项 (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "【配置 SSH 密钥】"
        echo "步骤 1: 生成 SSH 密钥（如果还没有）"
        if [ ! -f ~/.ssh/id_rsa ]; then
            echo "正在生成 SSH 密钥..."
            ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" -q
            echo "✓ SSH 密钥已生成"
        else
            echo "✓ 已存在 SSH 密钥"
        fi
        
        echo ""
        echo "步骤 2: 将公钥复制到新加坡服务器"
        echo "请在新加坡服务器上执行以下命令（或使用 ssh-copy-id）："
        echo ""
        echo "  ssh-copy-id root@${SINGAPORE_IP}"
        echo ""
        echo "或者手动复制公钥："
        echo "  cat ~/.ssh/id_rsa.pub"
        echo "  然后登录新加坡服务器，将公钥添加到 ~/.ssh/authorized_keys"
        echo ""
        read -p "按回车键继续（确保已配置好 SSH 密钥）..."
        
        echo ""
        echo "步骤 3: 测试连接并克隆项目"
        if ssh -o ConnectTimeout=5 root@${SINGAPORE_IP} "echo '连接成功'" 2>/dev/null; then
            echo "✓ SSH 连接成功，开始克隆..."
            ./clone_via_singapore.sh
        else
            echo "✗ SSH 连接失败，请检查密钥配置"
        fi
        ;;
    2)
        echo ""
        echo "【使用密码方式】"
        echo "由于需要交互式输入密码，请手动执行以下步骤："
        echo ""
        echo "步骤 1: 在新加坡服务器上克隆项目"
        echo "  ssh root@${SINGAPORE_IP}"
        echo "  cd /tmp"
        echo "  git clone https://github.com/JNUZXF/stock_agent.git"
        echo "  tar -czf stock_agent.tar.gz stock_agent/"
        echo ""
        echo "步骤 2: 从新加坡服务器下载到当前服务器"
        echo "  scp root@${SINGAPORE_IP}:/tmp/stock_agent.tar.gz ${TARGET_DIR}/"
        echo ""
        echo "步骤 3: 解压项目"
        echo "  cd ${TARGET_DIR}"
        echo "  tar -xzf stock_agent.tar.gz"
        ;;
    3)
        echo ""
        echo "=== 手动操作步骤 ==="
        echo ""
        echo "【方法 A：在新加坡服务器克隆后传输】"
        echo ""
        echo "1. 登录新加坡服务器："
        echo "   ssh root@${SINGAPORE_IP}"
        echo ""
        echo "2. 在新加坡服务器上执行："
        echo "   cd /tmp"
        echo "   git clone https://github.com/JNUZXF/stock_agent.git"
        echo "   tar -czf stock_agent.tar.gz stock_agent/"
        echo ""
        echo "3. 在阿里云服务器（当前服务器）上执行："
        echo "   scp root@${SINGAPORE_IP}:/tmp/stock_agent.tar.gz ${TARGET_DIR}/"
        echo "   cd ${TARGET_DIR}"
        echo "   tar -xzf stock_agent.tar.gz"
        echo ""
        echo "【方法 B：在新加坡服务器搭建代理】"
        echo ""
        echo "1. 在新加坡服务器上安装 tinyproxy："
        echo "   ssh root@${SINGAPORE_IP}"
        echo "   yum install -y tinyproxy  # CentOS/RHEL"
        echo "   # 或 apt-get install -y tinyproxy  # Ubuntu/Debian"
        echo ""
        echo "2. 配置 tinyproxy 允许当前服务器访问："
        CURRENT_IP=$(hostname -I | awk '{print $1}')
        echo "   echo 'Allow ${CURRENT_IP}' >> /etc/tinyproxy/tinyproxy.conf"
        echo "   systemctl start tinyproxy"
        echo "   systemctl enable tinyproxy"
        echo ""
        echo "3. 在阿里云服务器上配置 Git 使用代理："
        echo "   git config --global http.proxy http://${SINGAPORE_IP}:8888"
        echo "   git config --global https.proxy http://${SINGAPORE_IP}:8888"
        echo ""
        echo "4. 克隆项目："
        echo "   git clone https://github.com/JNUZXF/stock_agent.git"
        echo ""
        echo "5. 使用完后取消代理："
        echo "   git config --global --unset http.proxy"
        echo "   git config --global --unset https.proxy"
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac
