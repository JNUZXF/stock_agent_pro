# 阿里云服务器部署说明

## 问题说明

当前服务器位于阿里云大陆境内，无法直接访问 Docker Hub。需要配置镜像加速器或使用阿里云容器镜像服务。

## 解决方案

### 方案1：使用阿里云容器镜像服务（推荐）

1. **登录阿里云控制台**
   - 访问：https://cr.console.aliyun.com/
   - 开通容器镜像服务（个人版免费）

2. **获取镜像加速器地址**
   - 在控制台找到"镜像加速器"
   - 复制您的专属加速器地址（格式：`https://xxxxx.mirror.aliyuncs.com`）

3. **配置 Docker 镜像加速器**
   ```bash
   sudo mkdir -p /etc/docker
   sudo tee /etc/docker/daemon.json <<-'EOF'
   {
     "registry-mirrors": ["https://您的加速器地址.mirror.aliyuncs.com"]
   }
   EOF
   sudo systemctl daemon-reload
   sudo systemctl restart docker
   ```

4. **验证配置**
   ```bash
   docker info | grep -A 5 "Registry Mirrors"
   ```

### 方案2：使用其他国内镜像加速器

如果无法使用阿里云容器镜像服务，可以尝试以下镜像加速器：

```bash
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 方案3：手动拉取镜像并重新标记

如果镜像加速器配置后仍然无法拉取，可以尝试手动从国内镜像源拉取：

```bash
# 拉取 Python 镜像
docker pull docker.mirrors.ustc.edu.cn/library/python:3.11-slim
docker tag docker.mirrors.ustc.edu.cn/library/python:3.11-slim python:3.11-slim

# 拉取 Node 镜像
docker pull docker.mirrors.ustc.edu.cn/library/node:18-alpine
docker tag docker.mirrors.ustc.edu.cn/library/node:18-alpine node:18-alpine

# 拉取 Nginx 镜像
docker pull docker.mirrors.ustc.edu.cn/library/nginx:alpine
docker tag docker.mirrors.ustc.edu.cn/library/nginx:alpine nginx:alpine

# 拉取 Certbot 镜像
docker pull docker.mirrors.ustc.edu.cn/library/certbot/certbot
docker tag docker.mirrors.ustc.edu.cn/library/certbot/certbot certbot/certbot
```

### 方案4：使用本地环境运行（临时测试）

如果 Docker 镜像拉取一直失败，可以先用本地环境运行服务进行测试：

```bash
# 后端
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
python main.py

# 前端（新终端）
cd frontend
npm config set registry https://registry.npmmirror.com
npm install
npm run build
# 然后配置 Nginx 指向构建产物
```

## 当前配置状态

- ✅ Docker 镜像加速器已配置（但可能未生效）
- ✅ Dockerfile 已配置使用国内 pip 和 npm 镜像源
- ⚠️ 需要配置有效的 Docker 镜像加速器才能拉取基础镜像

## 下一步操作

1. **配置阿里云容器镜像服务**（推荐）
   - 登录阿里云控制台获取专属加速器地址
   - 更新 `/etc/docker/daemon.json`
   - 重启 Docker 服务

2. **验证镜像拉取**
   ```bash
   docker pull python:3.11-slim
   docker pull nginx:alpine
   docker pull certbot/certbot
   ```

3. **执行部署**
   ```bash
   ./scripts/deploy.sh
   ```

## 注意事项

- 确保服务器防火墙开放 80 和 443 端口
- 确保域名已正确解析到服务器 IP
- SSL 证书获取需要域名可以正常访问（HTTP 80 端口）
