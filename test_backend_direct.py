"""
直接测试后端性能
"""
import time
import requests
import json

# 直接访问后端容器
BACKEND_URL = "http://localhost:8000/api/chat"
TEST_MESSAGE = "分析一下SH600519"

def test_backend():
    """测试后端性能"""
    print("=" * 80)
    print("后端性能测试（直接访问后端容器）")
    print("=" * 80)
    print(f"后端URL: {BACKEND_URL}")
    print(f"测试消息: {TEST_MESSAGE}")
    print("-" * 80)
    
    start_time = time.time()
    first_chunk_time = None
    chunk_count = 0
    total_content = ""
    
    try:
        response = requests.post(
            BACKEND_URL,
            json={
                "message": TEST_MESSAGE,
                "agent_type": "stock_analysis"
            },
            stream=True,
            timeout=120
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print("-" * 80)
        
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    try:
                        data = json.loads(data_str)
                        
                        if first_chunk_time is None and data.get('type') == 'chunk':
                            first_chunk_time = time.time()
                            time_to_first_chunk = first_chunk_time - start_time
                            print(f"\n⚡ 第一个字符响应时间: {time_to_first_chunk:.3f}秒")
                            print("-" * 80)
                            print("智能体回复:")
                        
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
                            if first_chunk_time and chunk_count > 0:
                                print(f"第一个chunk后的平均耗时: {(total_time - (first_chunk_time - start_time)) / chunk_count:.4f}秒")
                        
                        elif data.get('type') == 'error':
                            print(f"\n❌ 错误: {data.get('error')}")
                            
                    except json.JSONDecodeError as e:
                        print(f"JSON解析错误: {e}, 内容: {data_str[:100]}")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {e}")
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
    
    print("=" * 80)

if __name__ == "__main__":
    test_backend()
