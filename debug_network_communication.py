#!/usr/bin/env python3
"""
调试网络通信
测试客户端和服务器之间的消息传输
"""

import sys
import os
import time
import threading
import socket
import json

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from shared.constants import MessageType, DEFAULT_PUBLIC_CHAT
from shared.messages import create_message_from_dict


def start_test_server():
    """启动测试服务器"""
    print("🚀 启动测试服务器...")
    
    try:
        from server.core.server import ChatRoomServer
        server = ChatRoomServer("localhost", 8888)
        server.start()
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")


def test_client_server_communication():
    """测试客户端服务器通信"""
    print("🧪 测试客户端服务器通信...")
    
    # 启动服务器
    server_thread = threading.Thread(target=start_test_server, daemon=True)
    server_thread.start()
    time.sleep(3)  # 等待服务器启动
    
    try:
        # 创建原始socket连接
        print("🔗 创建socket连接...")
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", 8888))
        print("✅ Socket连接成功")
        
        # 发送登录请求
        print("👤 发送登录请求...")
        # 先尝试注册用户，如果已存在则忽略错误
        register_request = {
            "message_type": MessageType.REGISTER_REQUEST,
            "username": "test",
            "password": "test123"
        }

        message_json = json.dumps(register_request) + '\n'
        client_socket.send(message_json.encode('utf-8'))

        # 接收注册响应（可能成功或失败）
        try:
            response_data = client_socket.recv(4096).decode('utf-8').strip()
            register_response = json.loads(response_data)
            print(f"📨 注册响应: {register_response.get('message', '已存在')}")
        except:
            pass

        # 发送登录请求
        login_request = {
            "message_type": MessageType.LOGIN_REQUEST,
            "username": "test",
            "password": "test123"
        }
        
        message_json = json.dumps(login_request) + '\n'
        client_socket.send(message_json.encode('utf-8'))
        
        # 接收登录响应
        response_data = client_socket.recv(4096).decode('utf-8').strip()
        print(f"📨 收到登录响应: {response_data}")
        
        login_response = json.loads(response_data)
        if login_response.get('success'):
            print("✅ 登录成功")
        else:
            print(f"❌ 登录失败: {login_response.get('message')}")
            return False
        
        # 发送进入聊天组请求
        print(f"📋 发送进入{DEFAULT_PUBLIC_CHAT}聊天组请求...")
        enter_chat_request = {
            "message_type": MessageType.ENTER_CHAT_GROUP_REQUEST,
            "group_name": DEFAULT_PUBLIC_CHAT
        }
        
        message_json = json.dumps(enter_chat_request) + '\n'
        client_socket.send(message_json.encode('utf-8'))
        
        # 接收响应和历史消息
        print("📨 接收响应和历史消息...")
        messages_received = []
        
        # 设置socket超时
        client_socket.settimeout(10.0)
        
        try:
            while True:
                response_data = client_socket.recv(4096).decode('utf-8')
                if not response_data:
                    break
                
                # 处理可能的多条消息
                lines = response_data.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            message_dict = json.loads(line)
                            message = create_message_from_dict(message_dict)
                            messages_received.append(message)
                            
                            print(f"📨 收到消息: {message.message_type}")
                            if hasattr(message, 'content'):
                                print(f"   内容: {message.content}")
                            if hasattr(message, 'message_count'):
                                print(f"   消息数量: {message.message_count}")
                            
                            # 如果收到历史消息完成通知，停止接收
                            if message.message_type == MessageType.CHAT_HISTORY_COMPLETE:
                                print("✅ 收到历史消息完成通知，停止接收")
                                break
                                
                        except json.JSONDecodeError as e:
                            print(f"⚠️ JSON解析失败: {e}, 数据: {line}")
                        except Exception as e:
                            print(f"⚠️ 消息处理失败: {e}")
                
                # 如果收到完成通知，退出循环
                if any(msg.message_type == MessageType.CHAT_HISTORY_COMPLETE for msg in messages_received):
                    break
                    
        except socket.timeout:
            print("⏰ 接收消息超时")
        
        # 分析接收到的消息
        print(f"\n📊 消息接收分析:")
        print(f"总共接收到 {len(messages_received)} 条消息")
        
        # 按类型分组
        message_types = {}
        for msg in messages_received:
            msg_type = msg.message_type
            if msg_type not in message_types:
                message_types[msg_type] = []
            message_types[msg_type].append(msg)
        
        for msg_type, msgs in message_types.items():
            print(f"  - {msg_type}: {len(msgs)}条")
            
            # 显示一些详细信息
            if msg_type == MessageType.CHAT_HISTORY and len(msgs) > 0:
                print(f"    最近的历史消息:")
                for i, msg in enumerate(msgs[-3:], 1):
                    print(f"      {i}. {msg.sender_username}: {msg.content}")
            
            elif msg_type == MessageType.CHAT_HISTORY_COMPLETE and len(msgs) > 0:
                complete_msg = msgs[0]
                print(f"    完成通知: 聊天组ID={complete_msg.chat_group_id}, 消息数量={complete_msg.message_count}")
        
        # 验证结果
        history_messages = message_types.get(MessageType.CHAT_HISTORY, [])
        complete_notifications = message_types.get(MessageType.CHAT_HISTORY_COMPLETE, [])
        
        success = len(history_messages) > 0 and len(complete_notifications) > 0
        
        if success:
            print("✅ 网络通信测试成功！客户端正确接收到历史消息和完成通知。")
        else:
            print("❌ 网络通信测试失败！")
            if len(history_messages) == 0:
                print("  - 没有收到历史消息")
            if len(complete_notifications) == 0:
                print("  - 没有收到完成通知")
        
        client_socket.close()
        return success
        
    except Exception as e:
        print(f"❌ 网络通信测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("🚀 开始调试网络通信...")
    
    success = test_client_server_communication()
    
    if success:
        print("\n🎉 网络通信正常！问题可能在客户端的消息处理逻辑中。")
    else:
        print("\n💥 发现网络通信问题！")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
