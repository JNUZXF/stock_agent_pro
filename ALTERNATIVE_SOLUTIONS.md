# 其他部署解决方案

由于 Docker 镜像拉取问题，以下是几个可行的替代方案：

## 方案1：使用阿里云 ECS 内网镜像仓库（推荐）

阿里云 ECS 服务器可以直接使用内网镜像仓库，无需登录：

```bash
# 配置使用阿里云内网镜像仓库
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://registry.cn-hangzhou.aliyuncs.com"
  ]
}
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker

# 尝试拉取镜像
chmod +x scripts/try-aliyun-mirrors.sh
./scripts/try-aliyun-mirrors.sh
```

## 方案2：不使用 Docker，直接部署（最简单）

如果 Docker 镜像一直无法拉取，可以直接使用系统服务部署：

```bash
chmod +x scripts/deploy-without-docker.sh
sudo ./scripts/deploy-without-docker.sh
```

这个方案会：
- 使用系统 Python 和 Node.js
- 创建 systemd 服务管理后端
- 使用系统 Nginx 作为反向代理
- 自动配置 SSL 证书

**优点**：
- 不需要 Docker
- 部署速度快
- 资源占用少
- 易于调试

**缺点**：
- 需要系统有 Python 3.8+ 和 Node.js
- 环境依赖系统包管理器

## 方案3：使用阿里云容器镜像服务的公共代理

如果您有阿里云账号，可以：

1. **登录阿里云控制台**
   - 访问：https://cr.console.aliyun.com/
   - 开通容器镜像服务（个人版免费）

2. **获取专属加速器地址**
   - 在控制台找到"镜像加速器"
   - 复制您的专属地址

3. **配置 Docker**
   ```bash
   sudo tee /etc/docker/daemon.json <<-'EOF'
   {
     "registry-mirrors": ["https://您的加速器地址.mirror.aliyuncs.com"]
   }
   EOF
   sudo systemctl daemon-reload
   sudo systemctl restart docker
   ```

## 方案4：手动导入镜像文件

如果有其他可以访问 Docker Hub 的服务器：

1. **在其他服务器上导出镜像**
   ```bash
   docker pull python:3.11-slim
   docker pull node:18-alpine
   docker pull nginx:alpine
   docker pull certbot/certbot
   
   docker save python:3.11-slim -o python.tar
   docker save node:18-alpine -o node.tar
   docker save nginx:alpine -o nginx.tar
   docker save certbot/certbot -o certbot.tar
   ```

2. **传输到当前服务器**
   ```bash
   scp *.tar user@47.113.101.218:/tmp/
   ```

3. **在当前服务器导入**
   ```bash
   docker load -i /tmp/python.tar
   docker load -i /tmp/node.tar
   docker load -i /tmp/nginx.tar
   docker load -i /tmp/certbot.tar
   ```

## 方案5：使用阿里云函数计算或容器服务

如果以上方案都不行，可以考虑：
- 使用阿里云函数计算（Serverless）
- 使用阿里云容器服务 ACK
- 使用阿里云 ECS 的容器镜像服务

## 推荐方案对比

| 方案 | 难度 | 速度 | 推荐度 |
|------|------|------|--------|
| 方案2：直接部署 | ⭐ 简单 | ⭐⭐⭐ 快 | ⭐⭐⭐⭐⭐ |
| 方案1：内网镜像 | ⭐⭐ 中等 | ⭐⭐⭐ 快 | ⭐⭐⭐⭐ |
| 方案3：专属加速器 | ⭐⭐ 中等 | ⭐⭐⭐ 快 | ⭐⭐⭐⭐ |
| 方案4：手动导入 | ⭐⭐⭐ 复杂 | ⭐⭐ 慢 | ⭐⭐ |
| 方案5：云服务 | ⭐⭐⭐⭐ 复杂 | ⭐⭐⭐ 快 | ⭐⭐⭐ |

## 快速开始

**推荐使用方案2（直接部署）**：

```bash
cd /home/stock_agent
chmod +x scripts/deploy-without-docker.sh
sudo ./scripts/deploy-without-docker.sh
```

这个方案会自动：
1. 检查并安装依赖
2. 部署后端服务（systemd）
3. 构建并部署前端
4. 配置 Nginx 反向代理
5. 获取 SSL 证书
6. 启动所有服务

## 注意事项

- 方案2需要系统有 Python 3.8+（当前是 3.6.8，可能需要升级）
- 确保 80 和 443 端口开放
- 确保域名已解析到服务器 IP
