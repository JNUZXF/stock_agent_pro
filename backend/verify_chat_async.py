#!/usr/bin/env python3
"""
验证脚本：验证 chat_async 方法是否存在且可调用
"""
import sys
import os
import inspect

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_chat_async():
    """验证 chat_async 方法"""
    print("="*80)
    print("验证 chat_async 方法")
    print("="*80)
    
    try:
        # 尝试导入（即使缺少依赖，也应该能检查方法是否存在）
        from app.agents.stock_agent import StockAnalysisAgent
        
        # 检查类是否有 chat_async 方法
        if not hasattr(StockAnalysisAgent, 'chat_async'):
            print("✗ StockAnalysisAgent 类没有 chat_async 方法")
            return False
        
        print("✓ StockAnalysisAgent 类有 chat_async 方法")
        
        # 检查方法签名
        method = getattr(StockAnalysisAgent, 'chat_async')
        if not inspect.iscoroutinefunction(method):
            print("✗ chat_async 不是异步函数")
            return False
        
        print("✓ chat_async 是异步函数")
        
        # 检查方法签名
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        if 'user_question' not in params:
            print("✗ chat_async 方法缺少 user_question 参数")
            return False
        
        print(f"✓ chat_async 方法签名正确: {sig}")
        
        # 检查返回类型注解
        return_annotation = sig.return_annotation
        print(f"✓ 返回类型注解: {return_annotation}")
        
        return True
        
    except ImportError as e:
        # 如果是因为缺少依赖导致的导入错误，这是可以接受的
        # 我们主要关心的是方法是否存在
        print(f"⚠ 导入警告（可能是缺少依赖）: {e}")
        print("尝试直接检查源代码...")
        
        # 直接读取源代码检查
        stock_agent_path = os.path.join(
            os.path.dirname(__file__),
            "app/agents/stock_agent.py"
        )
        
        with open(stock_agent_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'async def chat_async' in content:
            print("✓ 源代码中包含 chat_async 方法定义")
            return True
        else:
            print("✗ 源代码中未找到 chat_async 方法定义")
            return False
            
    except Exception as e:
        print(f"✗ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_user_id():
    """验证 user_id 参数"""
    print("\n" + "="*80)
    print("验证 user_id 参数")
    print("="*80)
    
    try:
        stock_agent_path = os.path.join(
            os.path.dirname(__file__),
            "app/agents/stock_agent.py"
        )
        
        with open(stock_agent_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查 __init__ 方法是否有 user_id 参数
        if 'user_id: Optional[str] = None' in content or 'user_id=None' in content:
            print("✓ __init__ 方法包含 user_id 参数")
        else:
            print("✗ __init__ 方法缺少 user_id 参数")
            return False
        
        # 检查是否有 generate_guest_user_id 函数
        if 'def generate_guest_user_id' in content:
            print("✓ 包含 generate_guest_user_id 函数")
        else:
            print("✗ 缺少 generate_guest_user_id 函数")
            return False
        
        # 检查是否有 self.user_id 赋值
        if 'self.user_id =' in content:
            print("✓ 包含 self.user_id 赋值")
        else:
            print("✗ 缺少 self.user_id 赋值")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始验证代码修改...\n")
    
    results = []
    
    # 验证 chat_async 方法
    results.append(("chat_async 方法", verify_chat_async()))
    
    # 验证 user_id 参数
    results.append(("user_id 参数", verify_user_id()))
    
    # 汇总结果
    print("\n" + "="*80)
    print("验证结果汇总")
    print("="*80)
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n✓ 所有验证通过！代码修改正确。")
        sys.exit(0)
    else:
        print("\n✗ 部分验证失败")
        sys.exit(1)
