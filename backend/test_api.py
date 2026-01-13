#!/usr/bin/env python3
"""
API测试脚本：使用requests测试API接口
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def test_greeting():
    """测试问候消息"""
    print("\n=== 测试1: 问候消息 ===")
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "你好",
                "conversation_id": None,
                "user_id": None  # 不提供user_id，会自动生成游客ID
            },
            stream=True,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"✗ 请求失败: {response.status_code}")
            print(response.text)
            return False
        
        print("用户: 你好")
        print("助手: ", end="", flush=True)
        
        conversation_id = None
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # 去掉 'data: ' 前缀
                    try:
                        data = json.loads(data_str)
                        if data.get('type') == 'chunk':
                            print(data.get('content', ''), end='', flush=True)
                        elif data.get('type') == 'done':
                            conversation_id = data.get('conversation_id')
                            print("\n✓ 问候消息测试完成")
                            print(f"会话ID: {conversation_id}")
                            return True
                        elif data.get('type') == 'error':
                            print(f"\n✗ 错误: {data.get('error')}")
                            return False
                    except json.JSONDecodeError:
                        continue
        
        print("\n✓ 问候消息测试完成（未收到done信号）")
        return True
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"\n✗ 问候消息测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stock_analysis():
    """测试股票分析"""
    print("\n=== 测试2: 股票分析 ===")
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "分析一下SH600519这只股票",
                "conversation_id": None,
                "user_id": None  # 不提供user_id，会自动生成游客ID
            },
            stream=True,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"✗ 请求失败: {response.status_code}")
            print(response.text)
            return False
        
        print("用户: 分析一下SH600519这只股票")
        print("助手: ", end="", flush=True)
        
        conversation_id = None
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # 去掉 'data: ' 前缀
                    try:
                        data = json.loads(data_str)
                        if data.get('type') == 'chunk':
                            print(data.get('content', ''), end='', flush=True)
                        elif data.get('type') == 'done':
                            conversation_id = data.get('conversation_id')
                            print("\n✓ 股票分析测试完成")
                            print(f"会话ID: {conversation_id}")
                            return True
                        elif data.get('type') == 'error':
                            print(f"\n✗ 错误: {data.get('error')}")
                            return False
                    except json.JSONDecodeError:
                        continue
        
        print("\n✓ 股票分析测试完成（未收到done信号）")
        return True
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"\n✗ 股票分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试API接口...")
    print(f"API地址: {BASE_URL}")
    print("提示: 如果服务器未运行，请先启动服务器: python main.py")
    
    # 测试问候消息
    test_greeting()
    
    # 测试股票分析
    test_stock_analysis()
    
    print("\n测试完成！")
