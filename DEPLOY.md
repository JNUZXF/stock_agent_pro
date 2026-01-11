# 生产环境部署指南

本文档说明如何将 Stock Agent 部署到生产环境，配置 HTTPS 和 SSL 自动续期。

## 前置要求

1. **服务器要求**
   - Linux 服务器（推荐 Ubuntu 20.04+ 或 CentOS 8+）
   - Docker 20.10+ 和 Docker Compose 2.0+
   - 域名已解析到服务器 IP（47.113.101.218）

2. **域名配置**
   - 主域名：`stockagent.cc`
   - 子域名：`www.stockagent.cc`（可选）
   - 确保两个域名都解析到服务器 IP：`47.113.101.218`

3. **端口要求**
   - 80 端口（HTTP，用于 Let's Encrypt 验证）
   - 443 端口（HTTPS）
   - 确保防火墙开放这两个端口

## 部署步骤

### 1. 准备环境变量

在项目根目录创建 `.env` 文件：

```env
DOUBAO_API_KEY=your_doubao_api_key
xq_a_token=your_xueqiu_token
```

### 2. 配置域名 DNS

确保域名正确解析到服务器：

```bash
# 检查域名解析
dig stockagent.cc
dig www.stockagent.cc

# 应该返回：47.113.101.218
```

### 3. 修改部署脚本中的邮箱

编辑 `scripts/deploy.sh`，将邮箱地址修改为您的邮箱：

```bash
EMAIL="your-email@example.com"  # 修改为您的邮箱
```

Let's Encrypt 会在证书到期前发送提醒邮件到此邮箱。

### 4. 执行部署

运行部署脚本：

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

部署脚本会自动：
1. 检查环境配置
2. 验证域名解析
3. 获取 SSL 证书（如果不存在）
4. 构建并启动所有服务

### 5. 验证部署

部署完成后，访问以下地址验证：

- HTTPS 主站：https://stockagent.cc
- HTTPS 子域名：https://www.stockagent.cc（如果配置了）
- API 文档：https://stockagent.cc/api/docs

## 手动部署（如果自动脚本失败）

如果自动部署脚本失败，可以手动执行以下步骤：

### 步骤 1：创建必要的目录

```bash
mkdir -p certbot/etc certbot/var certbot/www
mkdir -p nginx/ssl
```

### 步骤 2：启动临时 Nginx（仅 HTTP）

```bash
docker compose -f docker-compose.prod.yml up -d nginx
```

等待 Nginx 启动完成（约 10 秒）。

### 步骤 3：获取 SSL 证书

```bash
docker run --rm \
  -v "$(pwd)/certbot/etc:/etc/letsencrypt" \
  -v "$(pwd)/certbot/var:/var/lib/letsencrypt" \
  -v "$(pwd)/certbot/www:/var/www/certbot" \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d stockagent.cc \
  -d www.stockagent.cc
```

### 步骤 4：启动所有服务

```bash
docker compose -f docker-compose.prod.yml up -d
```

### 步骤 5：验证服务状态

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

## SSL 证书自动续期

SSL 证书已配置自动续期，Certbot 容器会每 12 小时检查一次证书是否需要续期。

证书有效期：90 天
自动续期检查：每 12 小时
续期阈值：证书剩余有效期少于 30 天时自动续期

### 手动续期（测试）

如果需要手动测试证书续期：

```bash
docker compose -f docker-compose.prod.yml exec certbot certbot renew --dry-run
```

### 查看证书信息

```bash
docker compose -f docker-compose.prod.yml exec certbot certbot certificates
```

## 服务管理

### 查看服务状态

```bash
docker compose -f docker-compose.prod.yml ps
```

### 查看日志

```bash
# 查看所有服务日志
docker compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml logs -f certbot
```

### 重启服务

```bash
# 重启所有服务
docker compose -f docker-compose.prod.yml restart

# 重启特定服务
docker compose -f docker-compose.prod.yml restart nginx
```

### 停止服务

```bash
docker compose -f docker-compose.prod.yml down
```

### 更新服务

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

## 故障排查

### 问题 1：SSL 证书获取失败

**症状**：部署时提示证书获取失败

**可能原因**：
1. 域名未正确解析到服务器 IP
2. 80 端口未开放或被占用
3. 防火墙阻止了 Let's Encrypt 的验证请求

**解决方法**：
```bash
# 检查域名解析
dig stockagent.cc

# 检查端口占用
sudo netstat -tulpn | grep :80

# 检查防火墙
sudo ufw status
sudo firewall-cmd --list-all  # CentOS/RHEL
```

### 问题 2：HTTPS 无法访问

**症状**：HTTP 可以访问，但 HTTPS 无法访问

**可能原因**：
1. 443 端口未开放
2. SSL 证书配置错误
3. Nginx 配置错误

**解决方法**：
```bash
# 检查端口
sudo netstat -tulpn | grep :443

# 检查 Nginx 配置
docker compose -f docker-compose.prod.yml exec nginx nginx -t

# 查看 Nginx 错误日志
docker compose -f docker-compose.prod.yml logs nginx | grep error
```

### 问题 3：API 请求失败

**症状**：前端可以访问，但 API 请求返回 502 或 504

**可能原因**：
1. 后端服务未启动
2. 网络配置问题
3. 后端服务崩溃

**解决方法**：
```bash
# 检查后端服务状态
docker compose -f docker-compose.prod.yml ps backend

# 查看后端日志
docker compose -f docker-compose.prod.yml logs backend

# 检查后端健康状态
curl http://localhost:8000/health
```

### 问题 4：证书续期失败

**症状**：证书到期但未自动续期

**解决方法**：
```bash
# 手动续期
docker compose -f docker-compose.prod.yml exec certbot certbot renew

# 重启 Nginx 加载新证书
docker compose -f docker-compose.prod.yml restart nginx
```

## 安全建议

1. **定期更新**：定期更新 Docker 镜像和系统补丁
2. **防火墙配置**：只开放必要的端口（80, 443）
3. **环境变量安全**：不要将 `.env` 文件提交到版本控制
4. **日志监控**：定期检查日志，发现异常及时处理
5. **备份**：定期备份重要数据和配置文件

## 架构说明

生产环境架构：

```
Internet
    |
    v
[Nginx 反向代理] (HTTPS:443, HTTP:80)
    |
    +---> [前端容器] (静态文件)
    |
    +---> [后端容器] (FastAPI:8000)
    |
    +---> [Certbot 容器] (SSL 证书管理)
```

- **Nginx**：处理 HTTPS、SSL 终止、反向代理
- **前端容器**：提供 React 静态文件
- **后端容器**：提供 FastAPI 服务
- **Certbot 容器**：自动管理 SSL 证书续期

## 联系支持

如遇到问题，请检查：
1. 项目 README.md
2. Docker 日志
3. Nginx 日志
4. 后端服务日志
