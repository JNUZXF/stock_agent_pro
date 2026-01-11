# 快速部署指南

## 一键部署到 stockagent.cc

### 前置检查

1. **域名解析**：确保 `stockagent.cc` 和 `www.stockagent.cc` 都解析到 `47.113.101.218`
   ```bash
   dig stockagent.cc
   dig www.stockagent.cc
   ```

2. **端口检查**：确保 80 和 443 端口开放
   ```bash
   sudo netstat -tulpn | grep -E ':(80|443)'
   ```

3. **环境变量**：创建 `.env` 文件
   ```bash
   cat > .env << EOF
   DOUBAO_API_KEY=your_doubao_api_key
   xq_a_token=your_xueqiu_token
   EOF
   ```

4. **修改邮箱**：编辑 `scripts/deploy.sh`，修改邮箱地址
   ```bash
   EMAIL="your-email@example.com"
   ```

### 执行部署

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 验证部署

部署完成后访问：
- https://stockagent.cc
- https://stockagent.cc/api/docs

### 常用命令

```bash
# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 重启服务
docker compose -f docker-compose.prod.yml restart

# 停止服务
docker compose -f docker-compose.prod.yml down

# 更新服务
git pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

### 故障排查

如果部署失败，检查：
1. 域名是否正确解析
2. 80/443 端口是否开放
3. 防火墙设置
4. Docker 服务是否运行

详细故障排查请参考 [DEPLOY.md](./DEPLOY.md)。
