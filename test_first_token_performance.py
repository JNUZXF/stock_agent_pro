"""
首Token响应时间性能测试脚本
详细记录每个环节的耗时，定位性能瓶颈
"""
import time
import requests
import json
import sys
from datetime import datetime

# 测试配置 - 通过nginx访问
BACKEND_URL = "http://localhost/api/chat"
TEST_MESSAGES = [
    "分析一下SH600519",
    "你好",
    "分析一下SZ000001"
]

def format_time(seconds):
    """格式化时间显示"""
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f}μs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f}ms"
    else:
        return f"{seconds:.3f}s"

def test_first_token_performance(message, test_num):
    """测试首Token响应时间"""
    print("\n" + "=" * 100)
    print(f"测试 #{test_num}: {message}")
    print("=" * 100)
    
    timestamps = {}
    timestamps['request_start'] = time.time()
    
    try:
        # 1. 准备请求
        timestamps['request_prepared'] = time.time()
        prep_time = timestamps['request_prepared'] - timestamps['request_start']
        print(f"[1] 请求准备耗时: {format_time(prep_time)}")
        
        # 2. 发送HTTP请求
        timestamps['http_sent'] = time.time()
        response = requests.post(
            BACKEND_URL,
            json={
                "message": message,
                "agent_type": "stock_analysis"
            },
            stream=True,
            timeout=120
        )
        timestamps['http_response_received'] = time.time()
        
        http_time = timestamps['http_response_received'] - timestamps['http_sent']
        print(f"[2] HTTP请求耗时: {format_time(http_time)}")
        print(f"    HTTP状态码: {response.status_code}")
        
        # 3. 开始接收流式响应
        timestamps['stream_start'] = time.time()
        first_chunk_time = None
        first_token_time = None
        chunk_count = 0
        total_content = ""
        last_chunk_time = None
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    try:
                        chunk_data = json.loads(data_str)
                        
                        # 记录第一个chunk的时间
                        if first_chunk_time is None:
                            first_chunk_time = time.time()
                            time_to_first_chunk = first_chunk_time - timestamps['stream_start']
                            print(f"[3] 第一个SSE chunk到达时间: {format_time(time_to_first_chunk)}")
                        
                        # 处理不同类型的响应
                        if chunk_data.get('type') == 'chunk':
                            if first_token_time is None:
                                first_token_time = time.time()
                                time_to_first_token = first_token_time - timestamps['request_start']
                                print(f"[4] ⚡ 首Token响应时间: {format_time(time_to_first_token)}")
                                print("-" * 100)
                                print("智能体回复:")
                            
                            content = chunk_data.get('content', '')
                            total_content += content
                            print(content, end='', flush=True)
                            chunk_count += 1
                            last_chunk_time = time.time()
                        
                        elif chunk_data.get('type') == 'done':
                            end_time = time.time()
                            total_time = end_time - timestamps['request_start']
                            
                            print("\n" + "-" * 100)
                            print(f"[5] ✅ 对话完成")
                            print(f"    总耗时: {format_time(total_time)}")
                            print(f"    接收到的chunk数量: {chunk_count}")
                            print(f"    回复总字符数: {len(total_content)}")
                            
                            if first_token_time and chunk_count > 0:
                                generation_time = end_time - first_token_time
                                avg_chunk_time = generation_time / chunk_count
                                print(f"    生成耗时: {format_time(generation_time)}")
                                print(f"    平均每个chunk耗时: {format_time(avg_chunk_time)}")
                            
                            # 时间分解
                            print("\n" + "-" * 100)
                            print("时间分解:")
                            print(f"    请求准备: {format_time(prep_time)}")
                            print(f"    HTTP传输: {format_time(http_time)}")
                            if first_chunk_time:
                                print(f"    首Chunk延迟: {format_time(first_chunk_time - timestamps['stream_start'])}")
                            if first_token_time:
                                print(f"    首Token延迟: {format_time(first_token_time - timestamps['request_start'])}")
                            if first_token_time and first_chunk_time:
                                print(f"    首Token处理: {format_time(first_token_time - first_chunk_time)}")
                            
                            break
                        
                        elif chunk_data.get('type') == 'error':
                            print(f"\n❌ 错误: {chunk_data.get('error')}")
                            break
                            
                    except json.JSONDecodeError as e:
                        print(f"\n⚠️  JSON解析错误: {e}")
                        print(f"    原始数据: {data_str[:200]}")
        
        return {
            'message': message,
            'first_token_time': time_to_first_token if first_token_time else None,
            'total_time': total_time if 'end_time' in locals() else None,
            'chunk_count': chunk_count,
            'content_length': len(total_content)
        }
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ HTTP请求失败: {e}")
        return None
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
        return None
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数"""
    print("\n" + "=" * 100)
    print("首Token响应时间性能测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"后端URL: {BACKEND_URL}")
    print("=" * 100)
    
    results = []
    
    for i, message in enumerate(TEST_MESSAGES, 1):
        result = test_first_token_performance(message, i)
        if result:
            results.append(result)
        
        # 测试之间稍作停顿
        if i < len(TEST_MESSAGES):
            time.sleep(2)
    
    # 汇总结果
    if results:
        print("\n" + "=" * 100)
        print("测试结果汇总")
        print("=" * 100)
        print(f"{'序号':<6} {'消息':<30} {'首Token时间':<15} {'总耗时':<15} {'Chunk数':<10} {'字符数':<10}")
        print("-" * 100)
        
        for i, r in enumerate(results, 1):
            first_token_str = format_time(r['first_token_time']) if r['first_token_time'] else "N/A"
            total_time_str = format_time(r['total_time']) if r['total_time'] else "N/A"
            print(f"{i:<6} {r['message']:<30} {first_token_str:<15} {total_time_str:<15} {r['chunk_count']:<10} {r['content_length']:<10}")
        
        # 计算平均值
        valid_results = [r for r in results if r['first_token_time'] is not None]
        if valid_results:
            avg_first_token = sum(r['first_token_time'] for r in valid_results) / len(valid_results)
            print("-" * 100)
            print(f"平均首Token响应时间: {format_time(avg_first_token)}")
    
    print("=" * 100)

if __name__ == "__main__":
    main()
