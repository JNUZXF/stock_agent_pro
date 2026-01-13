#!/bin/bash
# 前端快速部署脚本
# 使用: ./scripts/deploy-frontend-quick.sh
# 作用: 快速清理缓存并重新部署前端

set -e  # 遇到错误立即退出

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}前端快速部署脚本${NC}"
echo -e "${BLUE}================================${NC}"

# 步骤1: 检查Docker是否运行
echo -e "\n${YELLOW}[1/5]${NC} 检查Docker状态..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker未安装${NC}"
    exit 1
fi

if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker daemon未运行${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker状态正常${NC}"

# 步骤2: 停止服务
echo -e "\n${YELLOW}[2/5]${NC} 停止现有服务..."
cd "$PROJECT_ROOT"
docker-compose down 2>/dev/null || true
echo -e "${GREEN}✅ 服务已停止${NC}"

# 步骤3: 删除旧镜像
echo -e "\n${YELLOW}[3/5]${NC} 删除旧镜像..."
docker rmi stock_analysis_frontend 2>/dev/null || true
echo -e "${GREEN}✅ 旧镜像已删除${NC}"

# 步骤4: 重新构建
echo -e "\n${YELLOW}[4/5]${NC} 重新构建前端镜像..."
echo -e "${BLUE}这可能需要几分钟，请耐心等待...${NC}"
docker-compose build --no-cache frontend
echo -e "${GREEN}✅ 镜像构建完成${NC}"

# 步骤5: 启动服务
echo -e "\n${YELLOW}[5/5]${NC} 启动服务..."
docker-compose up -d
echo -e "${GREEN}✅ 服务已启动${NC}"

# 等待服务启动
echo -e "\n${BLUE}等待前端服务启动...${NC}"
sleep 3

# 验证
echo -e "\n${BLUE}================================${NC}"
echo -e "${GREEN}✅ 前端部署完成！${NC}"
echo -e "${BLUE}================================${NC}"

# 输出信息
echo -e "\n${YELLOW}服务状态:${NC}"
docker-compose ps | grep frontend || echo "未找到前端容器"

echo -e "\n${YELLOW}访问地址:${NC}"
echo -e "  ${GREEN}http://localhost${NC}"

echo -e "\n${YELLOW}查看日志:${NC}"
echo -e "  ${GREEN}docker-compose logs -f frontend${NC}"

echo -e "\n${YELLOW}进入容器:${NC}"
echo -e "  ${GREEN}docker exec -it stock_analysis_frontend sh${NC}"

echo ""
