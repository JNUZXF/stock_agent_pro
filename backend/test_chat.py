#!/usr/bin/env python3
"""
测试脚本：测试股票智能体的聊天功能
"""
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """测试导入"""
    try:
        from services.agent_service import agent_service
        print("✓ 导入成功")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_greeting():
    """测试问候消息"""
    print("\n=== 测试1: 问候消息 ===")
    try:
        from services.agent_service import agent_service
        
        # 创建新的Agent实例
        agent = agent_service.get_or_create_agent()
        print(f"会话ID: {agent.conversation_id}")
        
        # 发送问候消息
        print("用户: 你好")
        print("助手: ", end="", flush=True)
        
        response_chunks = []
        for chunk in agent.chat("你好"):
            response_chunks.append(chunk)
            print(chunk, end="", flush=True)
        
        print("\n✓ 问候消息测试完成")
        return True
    except Exception as e:
        print(f"\n✗ 问候消息测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stock_analysis():
    """测试股票分析"""
    print("\n=== 测试2: 股票分析 ===")
    try:
        from services.agent_service import agent_service
        
        # 创建新的Agent实例
        agent = agent_service.get_or_create_agent()
        print(f"会话ID: {agent.conversation_id}")
        
        # 发送股票分析请求
        print("用户: 分析一下SH600519这只股票")
        print("助手: ", end="", flush=True)
        
        response_chunks = []
        for chunk in agent.chat("分析一下SH600519这只股票"):
            response_chunks.append(chunk)
            print(chunk, end="", flush=True)
        
        print("\n✓ 股票分析测试完成")
        return True
    except Exception as e:
        print(f"\n✗ 股票分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试股票智能体...")
    
    # 测试导入
    if not test_import():
        print("\n导入失败，请检查依赖是否安装")
        sys.exit(1)
    
    # 测试问候消息
    test_greeting()
    
    # 测试股票分析
    test_stock_analysis()
    
    print("\n测试完成！")
