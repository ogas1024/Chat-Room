#!/usr/bin/env python3
"""
编码问题修复测试脚本
测试中文消息的编码和传输
"""

import sys
import os
import socket
import threading
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.messages import ChatMessage, BaseMessage
from shared.constants import MessageType


def test_utf8_encoding():
    """测试UTF-8编码处理"""
    print("🧪 测试UTF-8编码处理...")
    
    # 测试包含中文的消息
    test_messages = [
        "Hello World",
        "你好世界",
        "@AI 帮我翻译下面这段话: hello world",
        "这是一个包含中文的长消息：人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支",
        "混合语言测试: Hello 你好 World 世界 AI人工智能",
        "特殊字符测试：！@#￥%……&*（）——+｜【】｛｝；：""''《》，。？",
    ]
    
    for i, content in enumerate(test_messages):
        try:
            # 创建聊天消息
            message = ChatMessage(
                sender_id=1,
                sender_username="test_user",
                chat_group_id=1,
                chat_group_name="test_group",
                content=content
            )
            
            # 转换为JSON
            json_str = message.to_json()
            print(f"✅ 消息 {i+1} JSON编码成功: {len(json_str)} 字符")
            
            # 转换为字节
            json_bytes = json_str.encode('utf-8')
            print(f"✅ 消息 {i+1} UTF-8编码成功: {len(json_bytes)} 字节")
            
            # 解码回字符串
            decoded_str = json_bytes.decode('utf-8')
            print(f"✅ 消息 {i+1} UTF-8解码成功")
            
            # 验证内容一致性
            if json_str == decoded_str:
                print(f"✅ 消息 {i+1} 编码解码一致性验证通过")
            else:
                print(f"❌ 消息 {i+1} 编码解码一致性验证失败")
                return False
                
        except Exception as e:
            print(f"❌ 消息 {i+1} 编码测试失败: {e}")
            return False
    
    return True


def test_message_fragmentation():
    """测试消息分片处理"""
    print("🧪 测试消息分片处理...")
    
    # 创建一个长消息
    long_content = "这是一个很长的中文消息，用来测试消息分片处理。" * 50
    message = ChatMessage(
        sender_id=1,
        sender_username="test_user",
        chat_group_id=1,
        chat_group_name="test_group",
        content=long_content
    )
    
    try:
        # 转换为字节
        json_str = message.to_json() + '\n'
        message_bytes = json_str.encode('utf-8')
        print(f"✅ 长消息编码成功: {len(message_bytes)} 字节")
        
        # 模拟分片传输
        chunk_size = 1024  # 1KB分片
        chunks = []
        for i in range(0, len(message_bytes), chunk_size):
            chunk = message_bytes[i:i+chunk_size]
            chunks.append(chunk)
        
        print(f"✅ 消息分为 {len(chunks)} 个分片")
        
        # 模拟接收端重组
        buffer = b""
        for chunk in chunks:
            buffer += chunk
        
        # 处理完整消息
        if b'\n' in buffer:
            line_bytes, remaining = buffer.split(b'\n', 1)
            try:
                decoded_message = line_bytes.decode('utf-8')
                print(f"✅ 分片重组和解码成功: {len(decoded_message)} 字符")
                
                # 验证消息内容
                import json
                parsed_data = json.loads(decoded_message)
                if parsed_data.get('content') == long_content:
                    print("✅ 分片消息内容验证通过")
                    return True
                else:
                    print("❌ 分片消息内容验证失败")
                    return False
                    
            except UnicodeDecodeError as e:
                print(f"❌ 分片重组解码失败: {e}")
                return False
        else:
            print("❌ 分片重组失败：未找到消息结束符")
            return False
            
    except Exception as e:
        print(f"❌ 消息分片测试失败: {e}")
        return False


def test_socket_transmission():
    """测试Socket传输编码"""
    print("🧪 测试Socket传输编码...")
    
    # 测试消息
    test_content = "@AI 帮我翻译下面这段话: hello world 你好世界"
    
    def server_handler(server_socket):
        """服务器处理函数"""
        try:
            client_socket, addr = server_socket.accept()
            print(f"✅ 客户端连接: {addr}")
            
            # 接收消息
            buffer = b""
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                buffer += data
                
                # 处理完整消息
                while b'\n' in buffer:
                    line_bytes, buffer = buffer.split(b'\n', 1)
                    if line_bytes:
                        try:
                            message_str = line_bytes.decode('utf-8')
                            print(f"✅ 服务器接收消息成功: {len(message_str)} 字符")
                            
                            # 解析消息
                            import json
                            message_data = json.loads(message_str)
                            received_content = message_data.get('content', '')
                            
                            if received_content == test_content:
                                print("✅ 消息内容验证通过")
                                
                                # 发送回复
                                reply = ChatMessage(
                                    sender_id=-1,
                                    sender_username="AI助手",
                                    chat_group_id=1,
                                    chat_group_name="test_group",
                                    content="你好！这是AI的回复：Hello World 翻译为 你好世界"
                                )
                                reply_json = reply.to_json() + '\n'
                                client_socket.send(reply_json.encode('utf-8'))
                                print("✅ 服务器发送回复成功")
                            else:
                                print(f"❌ 消息内容验证失败: 期望 '{test_content}', 收到 '{received_content}'")
                                
                        except UnicodeDecodeError as e:
                            print(f"❌ 服务器解码失败: {e}")
                        except Exception as e:
                            print(f"❌ 服务器处理消息失败: {e}")
            
            client_socket.close()
            
        except Exception as e:
            print(f"❌ 服务器处理失败: {e}")
    
    try:
        # 创建服务器
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', 0))  # 使用随机端口
        port = server_socket.getsockname()[1]
        server_socket.listen(1)
        
        print(f"✅ 测试服务器启动: localhost:{port}")
        
        # 启动服务器线程
        server_thread = threading.Thread(target=server_handler, args=(server_socket,))
        server_thread.daemon = True
        server_thread.start()
        
        # 等待服务器启动
        time.sleep(0.1)
        
        # 创建客户端
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', port))
        print("✅ 客户端连接成功")
        
        # 发送测试消息
        message = ChatMessage(
            sender_id=1,
            sender_username="test_user",
            chat_group_id=1,
            chat_group_name="test_group",
            content=test_content
        )
        
        message_json = message.to_json() + '\n'
        client_socket.send(message_json.encode('utf-8'))
        print("✅ 客户端发送消息成功")
        
        # 接收回复
        buffer = b""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
                
            buffer += data
            
            if b'\n' in buffer:
                line_bytes, buffer = buffer.split(b'\n', 1)
                if line_bytes:
                    try:
                        reply_str = line_bytes.decode('utf-8')
                        print(f"✅ 客户端接收回复成功: {len(reply_str)} 字符")
                        
                        # 解析回复
                        import json
                        reply_data = json.loads(reply_str)
                        reply_content = reply_data.get('content', '')
                        print(f"✅ AI回复内容: {reply_content}")
                        
                        client_socket.close()
                        server_socket.close()
                        return True
                        
                    except UnicodeDecodeError as e:
                        print(f"❌ 客户端解码回复失败: {e}")
                        break
        
        client_socket.close()
        server_socket.close()
        return False
        
    except Exception as e:
        print(f"❌ Socket传输测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("🔧 编码问题修复测试")
    print("=" * 60)
    
    tests = [
        ("UTF-8编码处理测试", test_utf8_encoding),
        ("消息分片处理测试", test_message_fragmentation),
        ("Socket传输编码测试", test_socket_transmission),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print("✅ 测试通过")
            else:
                print("❌ 测试失败")
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有编码测试通过！编码问题修复成功！")
    else:
        print("⚠️  部分测试失败，需要进一步检查")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
