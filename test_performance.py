"""
性能测试脚本
测试异步优化后的智能体响应速度
"""
import time
import requests
import json

# 测试配置
API_URL = "http://localhost/api/chat"
TEST_MESSAGE = "分析一下SH600519这只股票，给出详细的股票分析报告。"

def test_chat_performance():
    """测试聊天性能"""
    print("=" * 80)
    print("智能体性能测试")
    print("=" * 80)
    print(f"测试消息: {TEST_MESSAGE}")
    print("-" * 80)
    
    # 记录开始时间
    start_time = time.time()
    first_chunk_time = None
    chunk_count = 0
    total_content = ""
    
    try:
        # 发送请求
        response = requests.post(
            API_URL,
            json={
                "message": TEST_MESSAGE,
                "agent_type": "stock_analysis"
            },
            stream=True,
            timeout=120
        )
        
        response.raise_for_status()
        
        # 处理流式响应
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # 去掉 'data: ' 前缀
                    try:
                        data = json.loads(data_str)
                        
                        # 记录第一个chunk的时间
                        if first_chunk_time is None and data.get('type') == 'chunk':
                            first_chunk_time = time.time()
                            time_to_first_chunk = first_chunk_time - start_time
                            print(f"\n⚡ 第一个字符响应时间: {time_to_first_chunk:.3f}秒")
                            print("-" * 80)
                            print("智能体回复:")
                        
                        # 处理不同类型的响应
                        if data.get('type') == 'chunk':
                            content = data.get('content', '')
                            total_content += content
                            print(content, end='', flush=True)
                            chunk_count += 1
                        
                        elif data.get('type') == 'done':
                            end_time = time.time()
                            total_time = end_time - start_time
                            print("\n" + "-" * 80)
                            print(f"✅ 对话完成")
                            print(f"总耗时: {total_time:.3f}秒")
                            print(f"接收到的chunk数量: {chunk_count}")
                            print(f"回复总字符数: {len(total_content)}")
                            if chunk_count > 0:
                                print(f"平均每个chunk耗时: {(total_time - (first_chunk_time - start_time)) / chunk_count:.4f}秒")
                        
                        elif data.get('type') == 'error':
                            print(f"\n❌ 错误: {data.get('error')}")
                            
                    except json.JSONDecodeError:
                        pass
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {e}")
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
    
    print("=" * 80)

if __name__ == "__main__":
    test_chat_performance()
