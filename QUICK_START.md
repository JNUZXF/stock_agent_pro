# 快速开始 - 推荐方案

由于 Docker 镜像拉取问题，**强烈推荐使用方案2：直接部署（不使用 Docker）**

## 🚀 方案2：直接部署（推荐，最简单）

### 前置要求
- Python 3.8+（当前系统是 3.6.8，脚本会自动尝试安装）
- Node.js（已安装 v20.19.2 ✓）
- Nginx（脚本会自动安装）

### 一键部署

```bash
cd /home/stock_agent
chmod +x scripts/deploy-without-docker.sh
sudo ./scripts/deploy-without-docker.sh
```

### 这个方案会做什么？

1. ✅ 检查并安装 Python 3.8+（如果需要）
2. ✅ 创建 Python 虚拟环境
3. ✅ 安装后端依赖（使用清华镜像源）
4. ✅ 创建 systemd 服务管理后端
5. ✅ 构建前端（使用 npm 淘宝镜像源）
6. ✅ 配置 Nginx 反向代理
7. ✅ 自动获取 SSL 证书
8. ✅ 启动所有服务

### 服务管理

```bash
# 查看后端状态
sudo systemctl status stock-agent-backend

# 查看后端日志
sudo journalctl -u stock-agent-backend -f

# 重启后端
sudo systemctl restart stock-agent-backend

# 重启 Nginx
sudo systemctl restart nginx

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/error.log
```

---

## 🔄 其他方案（如果方案2不行）

### 方案A：配置阿里云容器镜像服务

1. 登录：https://cr.console.aliyun.com/
2. 开通容器镜像服务（免费）
3. 获取专属加速器地址
4. 更新 `/etc/docker/daemon.json`
5. 重启 Docker
6. 运行 `./scripts/deploy.sh`

### 方案B：手动导入镜像

如果有其他可以访问 Docker Hub 的服务器：

```bash
# 在其他服务器上
docker pull python:3.11-slim
docker pull node:18-alpine
docker pull nginx:alpine
docker pull certbot/certbot

docker save python:3.11-slim -o python.tar
docker save node:18-alpine -o node.tar
docker save nginx:alpine -o nginx.tar
docker save certbot/certbot -o certbot.tar

# 传输到当前服务器
scp *.tar root@47.113.101.218:/tmp/

# 在当前服务器上
docker load -i /tmp/python.tar
docker load -i /tmp/node.tar
docker load -i /tmp/nginx.tar
docker load -i /tmp/certbot.tar

# 然后运行部署脚本
./scripts/deploy.sh
```

---

## 📋 当前环境检查

```bash
# 检查 Python
python3 --version  # 当前: 3.6.8（需要升级到 3.8+）

# 检查 Node.js
node --version  # ✓ v20.19.2

# 检查 Nginx
nginx -v  # 脚本会自动安装

# 检查端口
netstat -tuln | grep -E ':(80|443)'
```

---

## ⚠️ 注意事项

1. **Python 版本**：脚本会自动尝试安装 Python 3.8+，如果失败需要手动安装
2. **端口占用**：确保 80 和 443 端口未被占用
3. **域名解析**：确保 `stockagent.cc` 已解析到 `47.113.101.218`
4. **防火墙**：确保防火墙开放 80 和 443 端口

---

## 🎯 推荐执行顺序

1. **首选**：运行 `sudo ./scripts/deploy-without-docker.sh`
2. **如果失败**：检查错误信息，可能需要手动安装 Python 3.8+
3. **如果 Docker 可用**：配置阿里云容器镜像服务后运行 `./scripts/deploy.sh`
