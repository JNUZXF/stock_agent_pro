# frontend/Dockerfile
# 前端应用Docker镜像构建文件（多阶段构建）

# 阶段1: 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 配置 npm 使用国内镜像源
RUN npm config set registry https://registry.npmmirror.com

# 复制package文件
COPY package*.json ./

# 清理缓存，确保干净安装
RUN npm cache clean --force

# 安装依赖：使用 --force 和 --legacy-peer-deps 解决嵌套依赖和 peer dependency 冲突问题
# 删除可能损坏的嵌套依赖，强制重新安装
RUN rm -rf node_modules && \
    npm install --force --legacy-peer-deps && \
    # 修复 hast-util-to-parse5 中 property-information 嵌套依赖问题
    # 删除有问题的嵌套依赖，让它使用顶层的依赖
    rm -rf node_modules/hast-util-to-parse5/node_modules/property-information 2>/dev/null || true

# 复制源代码（.dockerignore 会排除 node_modules）
COPY . .

# 构建生产版本
RUN npm run build

# 阶段2: 生产阶段
FROM nginx:alpine

# 复制构建产物到nginx目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]

