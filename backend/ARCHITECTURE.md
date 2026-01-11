# Stock Agent Pro - 后端架构说明

## 版本信息
- **版本**: 2.0.0
- **架构类型**: 生产级分层架构
- **设计模式**: MVC + 依赖注入 + 仓储模式

## 架构概览

Stock Agent Pro 2.0 采用现代化的分层架构设计，实现了高内聚、低耦合、易扩展的生产级系统。

### 核心特性

✅ **用户隔离**: 完整的用户认证和授权系统，支持多用户独立使用
✅ **API版本控制**: 支持/api/v1、/api/v2等多版本API
✅ **高度可扩展**: 工具注册表系统，轻松添加新工具
✅ **低耦合**: 清晰的分层架构，各层职责明确
✅ **高可用**: 数据库持久化，智能体生命周期管理
✅ **代码高质量**: 完整类型提示，异常处理，日志系统

## 目录结构

```
backend/
├── app/                         # 应用主目录
│   ├── __init__.py
│   ├── main.py                  # 应用入口
│   ├── config.py                # 配置管理
│   │
│   ├── core/                    # 核心模块
│   │   ├── exceptions.py        # 自定义异常
│   │   ├── security.py          # 认证和安全
│   │   ├── middleware.py        # 中间件
│   │   └── logging.py           # 日志配置
│   │
│   ├── db/                      # 数据库
│   │   └── session.py           # 数据库会话
│   │
│   ├── models/                  # 数据模型（SQLAlchemy）
│   │   ├── base.py              # 基础模型
│   │   ├── user.py              # 用户模型
│   │   ├── conversation.py      # 对话模型
│   │   └── message.py           # 消息模型
│   │
│   ├── schemas/                 # Pydantic模式
│   │   ├── auth.py              # 认证Schema
│   │   ├── user.py              # 用户Schema
│   │   ├── conversation.py      # 对话Schema
│   │   └── chat.py              # 聊天Schema
│   │
│   ├── repositories/            # 数据访问层
│   │   ├── base.py              # 基础Repository
│   │   ├── user_repository.py
│   │   ├── conversation_repository.py
│   │   └── message_repository.py
│   │
│   ├── services/                # 业务逻辑层
│   │   ├── user_service.py
│   │   ├── auth_service.py
│   │   ├── conversation_service.py
│   │   └── chat_service.py
│   │
│   ├── agents/                  # 智能体框架
│   │   ├── base.py              # 智能体抽象基类
│   │   ├── stock_agent.py       # 股票分析智能体
│   │   ├── manager.py           # 智能体管理器
│   │   └── tools/               # 工具系统
│   │       ├── base.py          # 工具抽象基类
│   │       ├── registry.py      # 工具注册表
│   │       └── stock_tool.py    # 股票工具
│   │
│   └── api/                     # API层
│       └── v1/                  # v1版本API
│           ├── router.py        # 路由聚合
│           └── endpoints/       # API端点
│               ├── auth.py
│               ├── chat.py
│               └── conversations.py
│
├── requirements.txt
├── .env.example
└── Dockerfile
```

## 分层架构详解

### 1. API层（Controller）

**职责**: 处理HTTP请求和响应

```python
# 示例: app/api/v1/endpoints/chat.py
@router.post("/chat")
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    chat_service = ChatService(db)
    return chat_service.chat_stream(...)
```

**特点**:
- 依赖注入（Depends）
- 请求验证（Pydantic Schema）
- 异常转换为HTTP错误

### 2. Service层（业务逻辑）

**职责**: 实现业务逻辑，协调各个组件

```python
# 示例: app/services/chat_service.py
class ChatService:
    def chat_stream(self, user_id, message, conversation_id):
        # 1. 创建或获取对话
        # 2. 保存用户消息
        # 3. 调用智能体
        # 4. 保存助手回复
        # 5. 返回流式响应
```

**特点**:
- 不直接操作数据库，通过Repository
- 不直接处理HTTP，返回业务对象
- 包含业务逻辑和事务管理

### 3. Repository层（数据访问）

**职责**: 封装数据库操作

```python
# 示例: app/repositories/conversation_repository.py
class ConversationRepository(BaseRepository[Conversation]):
    def get_by_user_id(self, user_id: int):
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).all()
```

**特点**:
- 继承BaseRepository获得通用CRUD
- 提供领域特定查询方法
- 隔离SQL细节

### 4. Models层（数据模型）

**职责**: 定义数据库表结构

```python
# 示例: app/models/conversation.py
class Conversation(Base, BaseModel):
    __tablename__ = "conversations"

    conversation_id = Column(String(50), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    messages = relationship("Message", ...)
```

**特点**:
- SQLAlchemy ORM模型
- 关系定义（外键、关联）
- 索引优化

### 5. Agents层（智能体框架）

**职责**: AI智能体的抽象和实现

```python
# 智能体基类
class BaseAgent(ABC):
    @abstractmethod
    def chat(self, message: str) -> Generator:
        pass

# 具体实现
class StockAnalysisAgent(BaseAgent):
    def chat(self, message: str):
        # 调用AI API
        # 执行工具
        # 返回结果
```

**特点**:
- 抽象基类定义接口
- 工具注册表系统
- 支持用户隔离

## 核心设计模式

### 1. 依赖注入

```python
# 数据库依赖
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 用户认证依赖
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = credentials.credentials
    payload = verify_token(token)
    return payload.get("sub")
```

### 2. 工具注册表模式

```python
# 定义工具
@register_tool
class StockInfoTool(BaseTool):
    @property
    def name(self) -> str:
        return "get_stock_info"

    def execute(self, **kwargs) -> str:
        # 实现
        pass

# 使用工具
tool = tool_registry.get_tool("get_stock_info")
result = tool.execute(symbol="SH600519")
```

### 3. 仓储模式

```python
# 通用基础仓储
class BaseRepository(Generic[ModelType]):
    def get(self, id: int) -> Optional[ModelType]:
        ...
    def create(self, obj_in: Dict) -> ModelType:
        ...

# 特定领域仓储
class UserRepository(BaseRepository[User]):
    def get_by_username(self, username: str):
        ...
```

## 用户隔离实现

### 认证流程

```
1. 用户注册/登录
   └─> AuthService.register/login()
       └─> 生成JWT Token (包含user_id)

2. API请求
   └─> Header: Authorization: Bearer <token>
       └─> get_current_user_id() 解析token
           └─> 返回user_id

3. 业务逻辑
   └─> Service层接收user_id
       └─> Repository层过滤数据 (WHERE user_id = ?)
```

### 数据隔离

```python
# 所有涉及用户数据的操作都带user_id过滤
def get_user_conversations(user_id: int):
    return db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).all()
```

### 智能体隔离

```python
# 智能体管理器按用户ID存储实例
class AgentManager:
    _agents: Dict[str, Dict[str, Agent]] = {}
    # {user_id: {conversation_id: agent}}

    def get_agent(self, user_id, conversation_id):
        if user_id not in self._agents:
            self._agents[user_id] = {}
        ...
```

## API版本控制

### 路由组织

```python
# app/main.py
app.include_router(
    api_v1_router,
    prefix="/api/v1"
)

# 未来可添加
app.include_router(
    api_v2_router,
    prefix="/api/v2"
)
```

### 版本兼容

- **向后兼容**: v1继续提供服务
- **渐进迁移**: 新功能在v2实现
- **废弃通知**: 响应头标注版本信息

## 配置管理

### 环境变量

```python
# app/config.py
class Settings(BaseSettings):
    # 从环境变量或.env文件加载
    DATABASE_URL: str
    SECRET_KEY: str
    AI_API_KEY: str

    class Config:
        env_file = ".env"
```

### 多环境支持

```bash
# 开发环境
ENVIRONMENT=development
DEBUG=true

# 生产环境
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<strong-random-key>
```

## 异常处理

### 异常层次

```
StockAgentException (基类)
├── AuthenticationError
│   ├── TokenExpiredError
│   └── InvalidTokenError
├── AuthorizationError
├── ResourceNotFoundError
├── AgentError
│   ├── ToolExecutionError
│   └── AgentExecutionError
└── ...
```

### 统一处理

```python
# 中间件自动捕获并转换
class ExceptionHandlerMiddleware:
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except StockAgentException as e:
            return JSONResponse(
                status_code=get_status_code(e),
                content=e.to_dict()
            )
```

## 日志系统

### 日志配置

```python
# app/core/logging.py
def setup_logging():
    # 控制台输出
    console_handler = logging.StreamHandler()

    # 文件输出（可选）
    if settings.LOG_FILE:
        file_handler = logging.FileHandler(settings.LOG_FILE)
```

### 日志记录

```python
logger.info(f"用户登录: {username}")
logger.error(f"智能体执行失败: {str(e)}", exc_info=True)
```

## 数据库设计

### 表结构

```sql
-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 对话表
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    conversation_id VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 消息表
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT,
    tool_calls JSON,
    created_at TIMESTAMP
);
```

### 索引优化

```python
# 用户名和邮箱索引（唯一）
username = Column(String(50), unique=True, index=True)

# 外键索引
user_id = Column(Integer, ForeignKey("users.id"), index=True)

# 复合查询优化
Index('idx_user_updated', 'user_id', 'updated_at')
```

## 扩展指南

### 添加新工具

```python
# 1. 创建工具类
@register_tool
class NewTool(BaseTool):
    @property
    def name(self) -> str:
        return "new_tool"

    def execute(self, **kwargs) -> str:
        # 实现
        pass

# 2. 自动注册（通过装饰器）
# 3. 智能体自动可用
```

### 添加新智能体

```python
# 1. 继承BaseAgent
class NewsAnalysisAgent(BaseAgent):
    @property
    def agent_type(self) -> str:
        return "news_analysis"

    def chat(self, message: str):
        # 实现
        pass

# 2. 注册到AgentManager
AgentManager.AGENT_TYPES["news_analysis"] = NewsAnalysisAgent
```

### 添加新API版本

```bash
# 1. 创建目录
mkdir -p app/api/v2/endpoints

# 2. 创建路由
# app/api/v2/router.py

# 3. 注册到main.py
app.include_router(api_v2_router, prefix="/api/v2")
```

## 性能优化

### 数据库

- 连接池管理
- 查询索引优化
- 延迟加载（lazy loading）

### 智能体

- 实例复用（AgentManager）
- 过期清理机制
- 上下文窗口限制

### API

- 流式响应（SSE）
- 异步处理（async/await）
- 响应压缩

## 安全考虑

### 认证

- JWT Token（有效期限制）
- 密码哈希（bcrypt）
- HTTPS强制（生产环境）

### 授权

- 用户数据隔离
- API权限验证
- SQL注入防护（ORM）

### 限流

```python
# 配置限流
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10
```

## 监控和运维

### 健康检查

```bash
GET /health
{
    "status": "healthy",
    "database": "connected",
    "active_agents": 5
}
```

### 日志监控

- 错误日志
- 性能日志
- 业务日志

### 指标收集

```python
# 配置Prometheus/Sentry
METRICS_ENABLED=true
SENTRY_DSN=your-sentry-dsn
```

## 部署建议

### 开发环境

```bash
# 使用SQLite
DATABASE_URL=sqlite:///./stock_agent.db
DEBUG=true
```

### 生产环境

```bash
# 使用PostgreSQL
DATABASE_URL=postgresql://user:pass@host:5432/db
DEBUG=false
SECRET_KEY=<strong-random-key>
WORKERS=4
```

### Docker部署

```bash
docker-compose up -d
```

### 环境变量

所有敏感配置通过环境变量注入，不硬编码在代码中。

## 总结

Stock Agent Pro 2.0 采用生产级分层架构，实现了：

- ✅ 用户隔离和多用户支持
- ✅ API版本控制
- ✅ 高度可扩展的工具系统
- ✅ 清晰的职责分离
- ✅ 完善的错误处理
- ✅ 生产级的安全性

这是一个可持续发展、易于维护、方便扩展的现代化后端系统。
