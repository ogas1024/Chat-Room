#!/usr/bin/env python3
"""
调试聊天组状态同步问题
检查客户端和服务器端的聊天组状态是否同步
"""

import sys
import os
import time
import threading

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from client.core.client import ChatClient
from shared.constants import MessageType, DEFAULT_PUBLIC_CHAT


def start_test_server():
    """启动测试服务器"""
    try:
        from server.core.server import ChatRoomServer
        server = ChatRoomServer("localhost", 8888)
        server.start()
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")


def test_chat_group_state_sync():
    """测试聊天组状态同步"""
    print("🧪 测试聊天组状态同步...")
    
    # 启动服务器
    print("🚀 启动测试服务器...")
    server_thread = threading.Thread(target=start_test_server, daemon=True)
    server_thread.start()
    time.sleep(3)  # 等待服务器启动
    
    try:
        # 创建客户端
        client = ChatClient("localhost", 8888)
        
        # 连接和登录
        print("🔗 连接客户端...")
        if not client.connect():
            print("❌ 客户端连接失败")
            return False
        
        print("👤 注册和登录用户...")
        success, msg = client.register("test_sync_user", "password123")
        print(f"注册响应: {msg}")
        
        success, msg = client.login("test_sync_user", "password123")
        if not success:
            print(f"❌ 登录失败: {msg}")
            return False
        
        print(f"✅ 登录成功: {msg}")
        
        # 检查初始状态
        print(f"\n📋 检查初始状态...")
        print(f"客户端当前聊天组: {client.current_chat_group}")
        
        # 进入public聊天组
        print(f"\n🚪 进入{DEFAULT_PUBLIC_CHAT}聊天组...")
        success, msg = client.enter_chat_group(DEFAULT_PUBLIC_CHAT)
        if not success:
            print(f"❌ 进入聊天组失败: {msg}")
            return False
        
        print(f"✅ 进入聊天组成功: {msg}")
        
        # 检查进入后的状态
        print(f"\n📋 检查进入后的状态...")
        print(f"客户端当前聊天组: {client.current_chat_group}")
        
        if not client.current_chat_group:
            print("❌ 客户端当前聊天组为空！")
            return False
        
        group_id = client.current_chat_group['id']
        group_name = client.current_chat_group['name']
        print(f"聊天组ID: {group_id}, 聊天组名称: {group_name}")
        
        # 验证服务器端的用户状态
        print(f"\n🔍 验证服务器端的用户状态...")
        
        # 通过数据库直接查询服务器端的用户状态
        import sqlite3
        conn = sqlite3.connect("server/data/chatroom.db")
        cursor = conn.cursor()
        
        # 获取用户ID
        cursor.execute('SELECT id FROM users WHERE username = ?', ('test_sync_user',))
        user_data = cursor.fetchone()
        if not user_data:
            print("❌ 未找到用户")
            return False
        
        user_id = user_data[0]
        print(f"用户ID: {user_id}")
        
        # 检查用户是否在聊天组中
        cursor.execute(
            'SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?',
            (group_id, user_id)
        )
        is_member = cursor.fetchone() is not None
        print(f"用户是否是聊天组成员: {is_member}")
        
        conn.close()
        
        if not is_member:
            print("❌ 用户不是聊天组成员！这可能是问题所在。")
            return False
        
        # 测试发送消息
        print(f"\n📨 测试发送消息...")
        test_message = "这是一条测试消息"
        
        print(f"发送消息: {test_message}")
        print(f"使用聊天组ID: {group_id}")
        
        success = client.send_chat_message(test_message, group_id)
        
        if success:
            print("✅ 消息发送成功")
            time.sleep(2)  # 等待可能的错误响应
            return True
        else:
            print("❌ 消息发送失败")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理资源
        if 'client' in locals() and client.is_connected():
            client.disconnect()


def test_server_user_state():
    """测试服务器端用户状态管理"""
    print("\n🧪 测试服务器端用户状态管理...")
    
    try:
        from server.database.connection import DatabaseConnection
        from server.core.user_manager import UserManager
        from server.core.chat_manager import ChatManager
        
        # 初始化组件
        DatabaseConnection.set_database_path("server/data/chatroom.db")
        db = DatabaseConnection.get_instance()
        user_manager = UserManager()
        chat_manager = ChatManager(user_manager)
        
        # 获取test_sync_user的信息
        import sqlite3
        conn = sqlite3.connect("server/data/chatroom.db")
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM users WHERE username = ?', ('test_sync_user',))
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            print("❌ 未找到test_sync_user")
            return False
        
        user_id, username = user_data
        print(f"✅ 找到用户: {username} (ID: {user_id})")
        
        # 模拟用户登录（设置在线状态）
        print(f"📋 模拟用户登录...")
        # 注意：这里我们无法完全模拟socket连接，但可以检查逻辑
        
        # 测试进入聊天组
        print(f"🚪 测试进入{DEFAULT_PUBLIC_CHAT}聊天组...")
        try:
            group_info = chat_manager.enter_chat_group(DEFAULT_PUBLIC_CHAT, user_id)
            print(f"✅ 进入聊天组成功: {group_info}")
            
            # 检查用户当前聊天组状态
            current_chat = user_manager.get_user_current_chat(user_id)
            print(f"用户当前聊天组: {current_chat}")
            
            if current_chat == group_info['id']:
                print("✅ 服务器端用户状态设置正确")
            else:
                print(f"❌ 服务器端用户状态不正确，期望: {group_info['id']}, 实际: {current_chat}")
                return False
            
            # 测试发送消息权限
            print(f"📨 测试发送消息权限...")
            test_message = chat_manager.send_message(user_id, group_info['id'], "服务器端测试消息")
            print(f"✅ 消息发送成功: {test_message.content}")
            
            return True
            
        except Exception as e:
            print(f"❌ 服务器端测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ 服务器端用户状态测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("🚀 开始调试聊天组状态同步问题...")
    
    tests = [
        ("聊天组状态同步", test_chat_group_state_sync),
        ("服务器端用户状态", test_server_user_state),
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
        print("\n🎉 所有测试通过！聊天组状态同步正常。")
    else:
        print("\n💥 发现聊天组状态同步问题！")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
