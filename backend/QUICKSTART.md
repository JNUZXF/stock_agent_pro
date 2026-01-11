# Stock Agent Pro 2.0 - 快速开始

## 前置要求

- Python 3.11+
- pip

## 本地开发

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑.env文件，至少需要配置：
# - AI_API_KEY: 你的AI服务API密钥
# - SECRET_KEY: 修改为随机字符串（生产环境）
```

### 3. 初始化数据库

数据库会在首次启动时自动创建，默认使用SQLite。

### 4. 启动服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用Python启动
python -m app.main
```

### 5. 访问API文档

打开浏览器访问：http://localhost:8000/docs

## Docker部署

### 1. 配置环境变量

在项目根目录创建`.env`文件：

```bash
# AI服务配置
AI_API_KEY=your-api-key-here

# JWT密钥（生产环境必须修改）
SECRET_KEY=your-secret-key-here

# 其他配置...
```

### 2. 启动服务

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f backend
```

### 3. 停止服务

```bash
docker-compose down
```

## API使用示例

### 1. 用户注册

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

响应：
```json
{
  "access_token": "eyJ0eXAiOiJKV1...",
  "refresh_token": "eyJ0eXAiOiJKV1...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 2. 用户登录

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### 3. 发送聊天消息

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "请分析贵州茅台的股票",
    "agent_type": "stock_analysis"
  }'
```

响应（Server-Sent Events流）：
```
data: {"type":"chunk","content":"好的","conversation_id":"20240115-143052-12345"}
data: {"type":"chunk","content":"，让我","conversation_id":"20240115-143052-12345"}
data: {"type":"chunk","content":"为您查询","conversation_id":"20240115-143052-12345"}
...
data: {"type":"done","conversation_id":"20240115-143052-12345"}
```

### 4. 获取对话历史

```bash
curl -X GET "http://localhost:8000/api/v1/conversations" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. 获取对话详情

```bash
curl -X GET "http://localhost:8000/api/v1/conversations/20240115-143052-12345" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ENVIRONMENT` | 运行环境 | `development` |
| `DEBUG` | 调试模式 | `false` |
| `DATABASE_URL` | 数据库连接URL | `sqlite:///./stock_agent.db` |
| `SECRET_KEY` | JWT密钥 | ⚠️ 生产环境必须修改 |
| `AI_API_KEY` | AI服务API密钥 | 必填 |
| `AI_BASE_URL` | AI服务地址 | 豆包API地址 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token过期时间 | `30` |
| `MAX_ACTIVE_AGENTS_PER_USER` | 每用户最大活跃智能体数 | `5` |

完整配置参考：`backend/.env.example`

### 数据库选择

#### SQLite（开发）

```bash
DATABASE_URL=sqlite:///./stock_agent.db
```

#### PostgreSQL（生产推荐）

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/stock_agent
```

#### MySQL

```bash
DATABASE_URL=mysql://user:password@localhost:3306/stock_agent
```

## 开发指南

### 添加新工具

1. 在`app/agents/tools/`创建新文件
2. 继承`BaseTool`并使用`@register_tool`装饰器
3. 实现必需的方法

示例：

```python
from app.agents.tools.base import BaseTool
from app.agents.tools.registry import register_tool

@register_tool
class WeatherTool(BaseTool):
    @property
    def name(self) -> str:
        return "get_weather"

    @property
    def description(self) -> str:
        return "获取天气信息"

    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名称"}
            },
            "required": ["city"]
        }

    def execute(self, **kwargs) -> str:
        city = kwargs.get("city")
        # 实现天气查询逻辑
        return f"{city}的天气是..."
```

### 添加新API端点

1. 在`app/api/v1/endpoints/`创建新文件
2. 定义路由和处理函数
3. 在`app/api/v1/router.py`注册

示例：

```python
# app/api/v1/endpoints/weather.py
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/weather/{city}")
def get_weather(city: str):
    return {"city": city, "weather": "sunny"}
```

```python
# app/api/v1/router.py
from app.api.v1.endpoints import weather

api_router.include_router(
    weather.router,
    prefix="/weather",
    tags=["天气"]
)
```

## 故障排查

### 数据库连接失败

检查`DATABASE_URL`配置是否正确，确保数据库服务已启动。

### Token验证失败

1. 检查`SECRET_KEY`是否一致
2. Token是否过期
3. Header格式：`Authorization: Bearer <token>`

### 工具执行失败

1. 检查AI_API_KEY是否正确
2. 查看日志了解具体错误
3. 验证工具参数是否正确

### 智能体超出限制

每个用户最多5个活跃智能体，30分钟未使用自动清理。可通过环境变量调整：

```bash
MAX_ACTIVE_AGENTS_PER_USER=10
CONVERSATION_TIMEOUT_MINUTES=60
```

## 日志查看

### 开发环境

日志输出到控制台，级别：INFO

### Docker环境

```bash
# 实时查看
docker-compose logs -f backend

# 查看最近100行
docker-compose logs --tail=100 backend
```

### 日志文件

配置`LOG_FILE`环境变量启用文件日志：

```bash
LOG_FILE=./logs/app.log
```

## 性能调优

### 数据库连接池

```bash
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

### 会话管理

```bash
# 最大历史消息数
MAX_CONVERSATION_HISTORY=50

# 会话超时时间（分钟）
CONVERSATION_TIMEOUT_MINUTES=30
```

### Worker进程

```bash
# 生产环境建议
WORKERS=4  # CPU核心数 * 2 + 1
```

## 下一步

- 阅读 [架构文档](ARCHITECTURE.md) 了解系统设计
- 查看 [API文档](http://localhost:8000/docs) 了解所有接口
- 访问 [GitHub](https://github.com/your-repo) 查看源代码

## 获取帮助

- 提交Issue: GitHub Issues
- 查看日志: `docker-compose logs -f backend`
- 联系开发者: your-email@example.com
