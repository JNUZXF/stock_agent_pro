#!/bin/bash
# 一键修复并部署脚本
# 用途: 修复Docker编译错误并重新部署前端
# 使用: chmod +x deploy-and-fix.sh && ./deploy-and-fix.sh

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  前端修复和部署脚本 v1.0         ║${NC}"
echo -e "${BLUE}║  修复项目: 修复TS错误+优化样式    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════╝${NC}"

# 步骤1: 本地构建测试
echo -e "\n${YELLOW}[1/6]${NC} 本地构建测试..."
cd "$PROJECT_ROOT/frontend"

if npm run build > /tmp/build.log 2>&1; then
    echo -e "${GREEN}✅ 本地构建成功${NC}"
else
    echo -e "${RED}❌ 本地构建失败${NC}"
    echo -e "${RED}错误日志:${NC}"
    tail -20 /tmp/build.log
    exit 1
fi

# 步骤2: 停止运行的容器
echo -e "\n${YELLOW}[2/6]${NC} 停止运行的容器..."
cd "$PROJECT_ROOT"
docker compose down 2>/dev/null || true
sleep 2
echo -e "${GREEN}✅ 容器已停止${NC}"

# 步骤3: 删除旧镜像
echo -e "\n${YELLOW}[3/6]${NC} 清理旧镜像..."
docker rmi stock_analysis_frontend 2>/dev/null || true
sleep 1
echo -e "${GREEN}✅ 旧镜像已删除${NC}"

# 步骤4: 重新构建
echo -e "\n${YELLOW}[4/6]${NC} 使用Docker重新构建前端..."
echo -e "${BLUE}这可能需要2-3分钟，请稍候...${NC}"

if docker compose build --no-cache frontend > /tmp/docker-build.log 2>&1; then
    echo -e "${GREEN}✅ Docker构建成功${NC}"
else
    echo -e "${RED}❌ Docker构建失败${NC}"
    echo -e "${RED}错误日志:${NC}"
    tail -30 /tmp/docker-build.log
    exit 1
fi

# 步骤5: 启动服务
echo -e "\n${YELLOW}[5/6]${NC} 启动服务..."
docker compose up -d

# 等待服务启动
echo -e "${BLUE}等待服务完全启动...${NC}"
sleep 5

# 步骤6: 验证
echo -e "\n${YELLOW}[6/6]${NC} 验证部署..."
if docker compose ps | grep -q "stock_analysis_frontend.*Up"; then
    echo -e "${GREEN}✅ 前端容器运行正常${NC}"
else
    echo -e "${RED}❌ 前端容器启动失败${NC}"
    docker compose logs frontend | tail -20
    exit 1
fi

# 输出总结
echo -e "\n${BLUE}╔════════════════════════════════════╗${NC}"
echo -e "${GREEN}✅ 修复和部署完成！${NC}"
echo -e "${BLUE}╚════════════════════════════════════╝${NC}"

echo -e "\n${YELLOW}📋 修复项目:${NC}"
echo -e "  ✓ TypeScript类型错误修复"
echo -e "  ✓ ParticleBackground canvas类型推断"
echo -e "  ✓ Markdown列表项颜色优化"

echo -e "\n${YELLOW}🌐 访问信息:${NC}"
echo -e "  ${GREEN}前端地址: http://localhost${NC}"
echo -e "  ${GREEN}API地址: http://localhost:8000${NC}"

echo -e "\n${YELLOW}📝 日志查看:${NC}"
echo -e "  ${GREEN}docker compose logs -f frontend${NC}"

echo -e "\n${YELLOW}🧪 验证清单:${NC}"
echo -e "  [ ] 前端页面能正常打开"
echo -e "  [ ] 列表项文字清晰可读"
echo -e "  [ ] Markdown样式正确显示"
echo -e "  [ ] DevTools Console无错误"

echo ""
