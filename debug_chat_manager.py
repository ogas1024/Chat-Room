#!/usr/bin/env python3
"""
调试聊天管理器的历史消息加载
模拟服务器端的完整流程
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from shared.constants import DEFAULT_PUBLIC_CHAT


def test_chat_manager_flow():
    """测试聊天管理器的完整流程"""
    print("🧪 测试聊天管理器的完整流程...")
    
    try:
        from server.core.chat_manager import ChatManager
        from server.core.user_manager import UserManager
        
        # 初始化组件
        from server.database.connection import DatabaseConnection
        DatabaseConnection.set_database_path("server/data/chatroom.db")

        db = DatabaseConnection.get_instance()
        user_manager = UserManager()
        chat_manager = ChatManager(user_manager)
        
        print("✅ 组件初始化成功")
        
        # 获取一个测试用户
        import sqlite3
        conn = sqlite3.connect("server/data/chatroom.db")
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.group_id = 1 LIMIT 1')
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            print("❌ 没有找到测试用户")
            return False
        
        user_id, username = user_data
        print(f"✅ 使用测试用户: {username} (ID: {user_id})")
        
        # 1. 测试进入聊天组
        print(f"\n📋 测试进入{DEFAULT_PUBLIC_CHAT}聊天组...")
        try:
            group_info = chat_manager.enter_chat_group(DEFAULT_PUBLIC_CHAT, user_id)
            print(f"✅ 成功进入聊天组: {group_info}")
            group_id = group_info['id']
        except Exception as e:
            print(f"❌ 进入聊天组失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 2. 测试权限检查
        print(f"\n🔐 测试权限检查...")
        has_permission = db.is_user_in_chat_group(group_id, user_id)
        print(f"权限检查结果: {has_permission}")
        
        if not has_permission:
            print("❌ 权限检查失败！这是问题所在。")
            return False
        
        # 3. 测试加载历史消息
        print(f"\n📨 测试加载历史消息...")
        try:
            history_messages = chat_manager.load_chat_history_for_user(group_id, user_id, limit=10)
            print(f"✅ 成功加载历史消息: {len(history_messages)}条")
            
            if len(history_messages) > 0:
                print("最近的3条历史消息:")
                for i, msg in enumerate(history_messages[-3:], 1):
                    print(f"  {i}. 内容: {msg.content}")
                    print(f"     发送者: {msg.sender_username}")
                    print(f"     消息类型: {msg.message_type}")
                    print(f"     聊天组ID: {msg.chat_group_id}")
                return True
            else:
                print("❌ 没有加载到历史消息")
                return False
            
        except Exception as e:
            print(f"❌ 加载历史消息失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ 聊天管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_server_enter_chat_simulation():
    """模拟服务器端进入聊天组的完整流程"""
    print("\n🧪 模拟服务器端进入聊天组的完整流程...")
    
    try:
        from server.core.chat_manager import ChatManager
        from server.core.user_manager import UserManager
        from shared.messages import ChatHistoryComplete
        
        # 初始化组件
        from server.database.connection import DatabaseConnection
        DatabaseConnection.set_database_path("server/data/chatroom.db")

        db = DatabaseConnection.get_instance()
        user_manager = UserManager()
        chat_manager = ChatManager(user_manager)
        
        # 获取测试用户
        import sqlite3
        conn = sqlite3.connect("server/data/chatroom.db")
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.group_id = 1 LIMIT 1')
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            print("❌ 没有找到测试用户")
            return False
        
        user_id, username = user_data
        print(f"✅ 模拟用户: {username} (ID: {user_id})")
        
        # 模拟服务器端的进入聊天组处理逻辑
        print(f"\n📋 模拟服务器端处理进入{DEFAULT_PUBLIC_CHAT}聊天组请求...")
        
        try:
            # 1. 获取聊天组信息
            group_info = db.get_chat_group_by_name(DEFAULT_PUBLIC_CHAT)
            print(f"✅ 获取聊天组信息: {group_info}")
            
            # 2. 检查用户是否在聊天组中
            is_member = db.is_user_in_chat_group(group_info['id'], user_id)
            print(f"✅ 用户成员检查: {is_member}")
            
            if not is_member:
                print("❌ 用户不是聊天组成员")
                return False
            
            # 3. 设置用户当前聊天组（模拟）
            print(f"✅ 设置用户当前聊天组: {group_info['id']}")
            
            # 4. 加载历史消息
            print(f"📨 加载历史消息...")
            history_messages = chat_manager.load_chat_history_for_user(
                group_info['id'], user_id, limit=50
            )
            print(f"✅ 加载历史消息成功: {len(history_messages)}条")
            
            # 5. 创建完成通知
            complete_notification = ChatHistoryComplete(
                chat_group_id=group_info['id'],
                message_count=len(history_messages)
            )
            print(f"✅ 创建完成通知: 聊天组ID={complete_notification.chat_group_id}, 消息数量={complete_notification.message_count}")
            
            # 显示一些历史消息
            if len(history_messages) > 0:
                print("最近的历史消息:")
                for i, msg in enumerate(history_messages[-3:], 1):
                    print(f"  {i}. {msg.sender_username}: {msg.content}")
            
            return len(history_messages) > 0
            
        except Exception as e:
            print(f"❌ 模拟服务器端处理失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ 服务器端模拟测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("🚀 开始调试聊天管理器...")
    
    # 测试1: 聊天管理器流程
    print("="*50)
    print("测试1: 聊天管理器流程")
    print("="*50)
    result1 = test_chat_manager_flow()
    
    # 测试2: 服务器端模拟
    print("\n" + "="*50)
    print("测试2: 服务器端模拟")
    print("="*50)
    result2 = test_server_enter_chat_simulation()
    
    # 总结
    print("\n" + "="*50)
    print("测试结果总结")
    print("="*50)
    print(f"聊天管理器流程: {'✅ 通过' if result1 else '❌ 失败'}")
    print(f"服务器端模拟: {'✅ 通过' if result2 else '❌ 失败'}")
    
    if result1 and result2:
        print("\n🎉 聊天管理器功能正常！")
        print("问题可能在网络通信或客户端处理层面。")
    else:
        print("\n💥 发现聊天管理器问题！")
    
    return result1 and result2


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
