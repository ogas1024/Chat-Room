#!/usr/bin/env python3
"""
调试用户会话问题
模拟用户报告的具体场景：多个终端登录的情况
"""

import sys
import os
import time
import threading
import socket

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from client.core.client import ChatClient
from shared.constants import MessageType, DEFAULT_PUBLIC_CHAT


def start_test_server():
    """启动测试服务器"""
    try:
        from server.core.server import ChatRoomServer
        server = ChatRoomServer("localhost", 8889)  # 使用不同端口避免冲突
        print("🚀 测试服务器启动在端口8889...")
        server.start()
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")


def test_multiple_user_sessions():
    """测试多用户会话场景"""
    print("🧪 测试多用户会话场景...")
    
    # 启动服务器
    print("🚀 启动测试服务器...")
    server_thread = threading.Thread(target=start_test_server, daemon=True)
    server_thread.start()
    time.sleep(3)  # 等待服务器启动
    
    try:
        # 创建第一个客户端（模拟test用户）
        print("\n👤 创建第一个客户端（test用户）...")
        client1 = ChatClient("localhost", 8889)
        
        if not client1.connect():
            print("❌ 客户端1连接失败")
            return False
        
        # 注册和登录test用户
        success, msg = client1.register("test_user1", "password123")
        print(f"test用户注册: {msg}")
        
        success, msg = client1.login("test_user1", "password123")
        if not success:
            print(f"❌ test用户登录失败: {msg}")
            return False
        
        print(f"✅ test用户登录成功: {msg}")
        
        # test用户进入public聊天组
        success, msg = client1.enter_chat_group(DEFAULT_PUBLIC_CHAT)
        if not success:
            print(f"❌ test用户进入聊天组失败: {msg}")
            return False
        
        print(f"✅ test用户进入聊天组成功: {msg}")
        
        # test用户发送几条消息
        print("📨 test用户发送消息...")
        for i in range(3):
            message = f"test用户的第{i+1}条消息"
            success = client1.send_chat_message(message, client1.current_chat_group['id'])
            if success:
                print(f"  ✅ 发送成功: {message}")
            else:
                print(f"  ❌ 发送失败: {message}")
            time.sleep(0.5)
        
        # 创建第二个客户端（模拟test1用户）
        print("\n👤 创建第二个客户端（test1用户）...")
        client2 = ChatClient("localhost", 8889)
        
        if not client2.connect():
            print("❌ 客户端2连接失败")
            return False
        
        # 注册和登录test1用户
        success, msg = client2.register("test_user2", "password123")
        print(f"test1用户注册: {msg}")
        
        success, msg = client2.login("test_user2", "password123")
        if not success:
            print(f"❌ test1用户登录失败: {msg}")
            return False
        
        print(f"✅ test1用户登录成功: {msg}")
        
        # test1用户进入public聊天组
        success, msg = client2.enter_chat_group(DEFAULT_PUBLIC_CHAT)
        if not success:
            print(f"❌ test1用户进入聊天组失败: {msg}")
            return False
        
        print(f"✅ test1用户进入聊天组成功: {msg}")
        print(f"test1用户当前聊天组: {client2.current_chat_group}")
        
        # test1用户尝试发送消息
        print("\n📨 test1用户尝试发送消息...")
        test_messages = ["hi?", "fuck", "worse!", "a?"]
        
        for message in test_messages:
            print(f"  发送消息: {message}")
            success = client2.send_chat_message(message, client2.current_chat_group['id'])
            if success:
                print(f"  ✅ 发送成功: {message}")
            else:
                print(f"  ❌ 发送失败: {message}")
            time.sleep(1)  # 等待可能的错误响应
        
        # 等待一段时间看是否有错误消息
        print("\n⏳ 等待可能的错误响应...")
        time.sleep(3)
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理资源
        if 'client1' in locals() and client1.is_connected():
            client1.disconnect()
        if 'client2' in locals() and client2.is_connected():
            client2.disconnect()


def test_user_session_state():
    """测试用户会话状态"""
    print("\n🧪 测试用户会话状态...")
    
    try:
        from server.database.connection import DatabaseConnection
        from server.core.user_manager import UserManager
        
        # 初始化组件
        DatabaseConnection.set_database_path("server/data/chatroom.db")
        db = DatabaseConnection.get_instance()
        user_manager = UserManager()
        
        # 模拟用户登录
        print("👤 模拟用户登录...")
        
        # 创建模拟socket
        mock_socket1 = socket.socket()
        mock_socket2 = socket.socket()
        
        # 获取用户信息
        import sqlite3
        conn = sqlite3.connect("server/data/chatroom.db")
        cursor = conn.cursor()
        
        # 获取或创建测试用户
        cursor.execute('SELECT id FROM users WHERE username = ?', ('test_session_user1',))
        user1_data = cursor.fetchone()
        if not user1_data:
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                         ('test_session_user1', 'dummy_hash'))
            conn.commit()
            user1_id = cursor.lastrowid
        else:
            user1_id = user1_data[0]
        
        cursor.execute('SELECT id FROM users WHERE username = ?', ('test_session_user2',))
        user2_data = cursor.fetchone()
        if not user2_data:
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                         ('test_session_user2', 'dummy_hash'))
            conn.commit()
            user2_id = cursor.lastrowid
        else:
            user2_id = user2_data[0]
        
        conn.close()
        
        print(f"✅ 测试用户ID: user1={user1_id}, user2={user2_id}")
        
        # 模拟用户1登录
        print("🔐 模拟用户1登录...")
        user1_info = user_manager.login_user(user1_id, mock_socket1)
        print(f"用户1会话: {user1_info}")
        
        # 模拟用户2登录
        print("🔐 模拟用户2登录...")
        user2_info = user_manager.login_user(user2_id, mock_socket2)
        print(f"用户2会话: {user2_info}")
        
        # 检查用户会话状态
        print("\n📋 检查用户会话状态...")
        session1 = user_manager.get_user_by_socket(mock_socket1)
        session2 = user_manager.get_user_by_socket(mock_socket2)
        
        print(f"用户1会话状态: {session1}")
        print(f"用户2会话状态: {session2}")
        
        if not session1 or not session2:
            print("❌ 用户会话状态异常！")
            return False
        
        # 测试设置当前聊天组
        print("\n🏠 测试设置当前聊天组...")
        public_group = db.get_chat_group_by_name(DEFAULT_PUBLIC_CHAT)
        group_id = public_group['id']
        
        user_manager.set_user_current_chat(user1_id, group_id)
        user_manager.set_user_current_chat(user2_id, group_id)
        
        current_chat1 = user_manager.get_user_current_chat(user1_id)
        current_chat2 = user_manager.get_user_current_chat(user2_id)
        
        print(f"用户1当前聊天组: {current_chat1}")
        print(f"用户2当前聊天组: {current_chat2}")
        
        if current_chat1 != group_id or current_chat2 != group_id:
            print("❌ 当前聊天组设置异常！")
            return False
        
        print("✅ 用户会话状态正常")
        return True
        
    except Exception as e:
        print(f"❌ 用户会话状态测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("🚀 开始调试用户会话问题...")
    
    tests = [
        ("用户会话状态", test_user_session_state),
        ("多用户会话场景", test_multiple_user_sessions),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"测试: {test_name}")
        print(f"{'='*60}")
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！用户会话管理正常。")
    else:
        print("\n💥 发现用户会话管理问题！")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
