#!/usr/bin/env python3
"""
测试脚本：测试 /api/chat 接口
"""
import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000/api"

def test_greeting():
    """测试1: 问候消息"""
    print("\n" + "="*80)
    print("测试1: 问候消息")
    print("="*80)
    
    try:
        print(f"发送请求到: {BASE_URL}/chat")
        print("请求内容: {'message': '你好', 'conversation_id': None, 'user_id': None}")
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "你好",
                "conversation_id": None,
                "user_id": None
            },
            stream=True,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"✗ 请求失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
        
        print(f"✓ 请求成功: HTTP {response.status_code}")
        print("\n响应内容:")
        print("-" * 80)
        
        conversation_id = None
        chunks_received = 0
        full_content = ""
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # 去掉 'data: ' 前缀
                    try:
                        data = json.loads(data_str)
                        if data.get('type') == 'chunk':
                            content = data.get('content', '')
                            full_content += content
                            print(content, end='', flush=True)
                            chunks_received += 1
                        elif data.get('type') == 'done':
                            conversation_id = data.get('conversation_id')
                            print("\n" + "-" * 80)
                            print(f"✓ 收到完成信号")
                            print(f"会话ID: {conversation_id}")
                            print(f"收到chunk数量: {chunks_received}")
                            print(f"总内容长度: {len(full_content)} 字符")
                            return True
                        elif data.get('type') == 'error':
                            error_msg = data.get('error', '未知错误')
                            print(f"\n✗ 错误: {error_msg}")
                            return False
                    except json.JSONDecodeError as e:
                        print(f"\n✗ JSON解析错误: {e}")
                        print(f"原始数据: {data_str}")
                        return False
        
        print("\n" + "-" * 80)
        if conversation_id:
            print(f"✓ 测试完成（未收到done信号，但收到了响应）")
            print(f"会话ID: {conversation_id}")
            return True
        else:
            print("✗ 未收到有效响应")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器")
        print("提示: 请确保服务器正在运行: python3 main.py")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stock_analysis():
    """测试2: 股票分析"""
    print("\n" + "="*80)
    print("测试2: 股票分析")
    print("="*80)
    
    try:
        print(f"发送请求到: {BASE_URL}/chat")
        print("请求内容: {'message': '分析一下SH600519这只股票', 'conversation_id': None, 'user_id': None}")
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "分析一下SH600519这只股票",
                "conversation_id": None,
                "user_id": None
            },
            stream=True,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"✗ 请求失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
        
        print(f"✓ 请求成功: HTTP {response.status_code}")
        print("\n响应内容:")
        print("-" * 80)
        
        conversation_id = None
        chunks_received = 0
        full_content = ""
        first_chunk_time = None
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # 去掉 'data: ' 前缀
                    try:
                        data = json.loads(data_str)
                        if data.get('type') == 'chunk':
                            if first_chunk_time is None:
                                first_chunk_time = time.time()
                                time_to_first_chunk = (first_chunk_time - start_time) * 1000
                                print(f"[首Token耗时: {time_to_first_chunk:.2f}ms]")
                            
                            content = data.get('content', '')
                            full_content += content
                            print(content, end='', flush=True)
                            chunks_received += 1
                        elif data.get('type') == 'done':
                            conversation_id = data.get('conversation_id')
                            end_time = time.time()
                            total_time = (end_time - start_time) * 1000
                            print("\n" + "-" * 80)
                            print(f"✓ 收到完成信号")
                            print(f"会话ID: {conversation_id}")
                            print(f"收到chunk数量: {chunks_received}")
                            print(f"总内容长度: {len(full_content)} 字符")
                            print(f"总耗时: {total_time:.2f}ms")
                            if first_chunk_time:
                                print(f"首Token耗时: {(first_chunk_time - start_time) * 1000:.2f}ms")
                            return True
                        elif data.get('type') == 'error':
                            error_msg = data.get('error', '未知错误')
                            print(f"\n✗ 错误: {error_msg}")
                            return False
                    except json.JSONDecodeError as e:
                        print(f"\n✗ JSON解析错误: {e}")
                        print(f"原始数据: {data_str}")
                        return False
        
        print("\n" + "-" * 80)
        if conversation_id:
            print(f"✓ 测试完成（未收到done信号，但收到了响应）")
            print(f"会话ID: {conversation_id}")
            return True
        else:
            print("✗ 未收到有效响应")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器")
        print("提示: 请确保服务器正在运行: python3 main.py")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_custom_user_id():
    """测试3: 使用自定义user_id"""
    print("\n" + "="*80)
    print("测试3: 使用自定义user_id")
    print("="*80)
    
    try:
        custom_user_id = "test-user-12345"
        print(f"发送请求到: {BASE_URL}/chat")
        print(f"请求内容: {{'message': '你好', 'conversation_id': None, 'user_id': '{custom_user_id}'}}")
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "你好",
                "conversation_id": None,
                "user_id": custom_user_id
            },
            stream=True,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"✗ 请求失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
        
        print(f"✓ 请求成功: HTTP {response.status_code}")
        print("\n响应内容:")
        print("-" * 80)
        
        conversation_id = None
        chunks_received = 0
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    try:
                        data = json.loads(data_str)
                        if data.get('type') == 'chunk':
                            content = data.get('content', '')
                            print(content, end='', flush=True)
                            chunks_received += 1
                        elif data.get('type') == 'done':
                            conversation_id = data.get('conversation_id')
                            print("\n" + "-" * 80)
                            print(f"✓ 收到完成信号")
                            print(f"会话ID: {conversation_id}")
                            print(f"收到chunk数量: {chunks_received}")
                            return True
                        elif data.get('type') == 'error':
                            error_msg = data.get('error', '未知错误')
                            print(f"\n✗ 错误: {error_msg}")
                            return False
                    except json.JSONDecodeError:
                        continue
        
        print("\n" + "-" * 80)
        if conversation_id:
            print(f"✓ 测试完成")
            return True
        else:
            print("✗ 未收到有效响应")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*80)
    print("开始测试 /api/chat 接口")
    print("="*80)
    print(f"API地址: {BASE_URL}")
    print("提示: 如果服务器未运行，请先启动服务器: python3 main.py")
    print()
    
    results = []
    
    # 测试1: 问候消息
    results.append(("问候消息", test_greeting()))
    
    # 测试2: 股票分析
    results.append(("股票分析", test_stock_analysis()))
    
    # 测试3: 自定义user_id
    results.append(("自定义user_id", test_with_custom_user_id()))
    
    # 汇总结果
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n✓ 所有测试通过！")
        sys.exit(0)
    else:
        print("\n✗ 部分测试失败")
        sys.exit(1)
