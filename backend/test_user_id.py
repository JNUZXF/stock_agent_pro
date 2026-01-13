#!/usr/bin/env python3
"""
测试脚本：验证user_id功能
"""
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_guest_id_generation():
    """测试游客ID生成"""
    print("=== 测试1: 游客ID生成 ===")
    try:
        from app.agents.stock_agent import generate_guest_user_id
        
        # 生成多个游客ID，确保它们是唯一的
        ids = [generate_guest_user_id() for _ in range(5)]
        print(f"生成的游客ID示例:")
        for i, guest_id in enumerate(ids, 1):
            print(f"  {i}. {guest_id}")
        
        # 检查格式
        assert all(id.startswith("guest-") for id in ids), "所有ID应该以'guest-'开头"
        print("✓ 游客ID格式正确")
        
        # 检查唯一性
        assert len(set(ids)) == len(ids), "所有ID应该是唯一的"
        print("✓ 游客ID唯一性验证通过")
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_with_user_id():
    """测试Agent使用user_id"""
    print("\n=== 测试2: Agent使用user_id ===")
    try:
        from services.agent_service import agent_service
        
        # 测试1: 不提供user_id，应该自动生成
        agent1 = agent_service.get_or_create_agent()
        print(f"Agent 1 - 用户ID: {agent1.user_id}")
        print(f"Agent 1 - 会话ID: {agent1.conversation_id}")
        assert agent1.user_id.startswith("guest-"), "应该自动生成游客ID"
        print("✓ 自动生成游客ID成功")
        
        # 测试2: 提供自定义user_id
        custom_user_id = "custom-user-123"
        agent2 = agent_service.get_or_create_agent(user_id=custom_user_id)
        print(f"Agent 2 - 用户ID: {agent2.user_id}")
        assert agent2.user_id == custom_user_id, "应该使用提供的user_id"
        print("✓ 使用自定义user_id成功")
        
        # 测试3: 同一个conversation_id应该返回同一个Agent
        conv_id = agent1.conversation_id
        agent3 = agent_service.get_or_create_agent(conversation_id=conv_id)
        print(f"Agent 3 - 用户ID: {agent3.user_id}")
        print(f"Agent 3 - 会话ID: {agent3.conversation_id}")
        assert agent3.conversation_id == conv_id, "应该返回同一个会话"
        assert agent3.user_id == agent1.user_id, "应该保持相同的user_id"
        print("✓ 会话复用功能正常")
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试user_id功能...\n")
    
    success = True
    
    # 测试游客ID生成
    if not test_guest_id_generation():
        success = False
    
    # 测试Agent使用user_id
    if not test_agent_with_user_id():
        success = False
    
    if success:
        print("\n✓ 所有测试通过！")
    else:
        print("\n✗ 部分测试失败")
        sys.exit(1)
