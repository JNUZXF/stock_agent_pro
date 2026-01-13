# 测试说明

## 已完成的修改

1. **修复了 `agent_service.py` 的导入路径**
   - 从 `from stock_agent import StockAnalysisAgent` 
   - 改为 `from app.agents.stock_agent import StockAnalysisAgent`
   - 这样可以正确导入修改后的 `StockAnalysisAgent` 类

2. **检查了 `routes.py` 的逻辑**
   - `routes.py` 的逻辑与新的 `stock_agent.py` 实现兼容
   - `chat` 方法返回的 `Generator[str, None, None]` 与路由期望的格式一致
   - 流式响应处理逻辑正确

## 测试方法

### 方法1: 使用测试脚本（需要安装依赖）

```bash
cd /home/stock_agent/backend
python3 test_chat.py
```

### 方法2: 使用API测试脚本（需要服务器运行）

1. 启动服务器：
```bash
cd /home/stock_agent/backend
python3 main.py
```

2. 在另一个终端运行测试：
```bash
cd /home/stock_agent/backend
python3 test_api.py
```

### 方法3: 使用curl测试

1. 启动服务器后，测试问候消息：
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "conversation_id": null}' \
  --no-buffer
```

2. 测试股票分析：
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "分析一下SH600519这只股票", "conversation_id": null}' \
  --no-buffer
```

## 测试用例

### 测试1: 问候消息
- **请求**: `{"message": "你好", "conversation_id": null}`
- **预期**: 返回友好的问候回复

### 测试2: 股票分析
- **请求**: `{"message": "分析一下SH600519这只股票", "conversation_id": null}`
- **预期**: 调用 `get_stock_info` 工具获取股票信息，并返回详细分析

## 注意事项

1. 确保环境变量已正确设置（`DOUBAO_API_KEY` 和 `xq_a_token`）
2. 确保所有依赖已安装（见 `requirements.txt`）
3. 服务器默认运行在 `http://localhost:8000`
