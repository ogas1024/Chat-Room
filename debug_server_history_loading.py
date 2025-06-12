#!/usr/bin/env python3
"""
调试服务器端历史消息加载逻辑
直接测试服务器端的历史消息加载功能
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from shared.constants import DEFAULT_PUBLIC_CHAT


def test_database_manager():
    """测试数据库管理器的历史消息加载功能"""
    print("🧪 测试数据库管理器的历史消息加载功能...")
    
    try:
        from server.database.models import DatabaseManager
        
        db = DatabaseManager()
        
        # 1. 获取public聊天组信息
        print(f"\n📋 获取{DEFAULT_PUBLIC_CHAT}聊天组信息...")
        public_group = db.get_chat_group_by_name(DEFAULT_PUBLIC_CHAT)
        print(f"✅ {DEFAULT_PUBLIC_CHAT}聊天组: {public_group}")
        
        group_id = public_group['id']
        
        # 2. 获取一些用户ID进行测试
        print(f"\n👤 获取用户信息...")
        import sqlite3
        conn = sqlite3.connect("server/data/chatroom.db")
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM users WHERE id IN (SELECT user_id FROM group_members WHERE group_id = ?) LIMIT 3', (group_id,))
        users = cursor.fetchall()
        conn.close()
        
        print(f"📊 找到{len(users)}个{DEFAULT_PUBLIC_CHAT}聊天组成员:")
        for user_id, username in users:
            print(f"  - 用户ID: {user_id}, 用户名: {username}")
        
        # 3. 测试每个用户的权限检查
        print(f"\n🔐 测试用户权限检查...")
        for user_id, username in users:
            is_member = db.is_user_in_chat_group(group_id, user_id)
            print(f"  - 用户 {username} (ID: {user_id}) 权限检查: {is_member}")
            
            if not is_member:
                print(f"    ❌ 权限检查失败！这可能是问题所在。")
        
        # 4. 直接测试历史消息查询
        print(f"\n📨 直接测试历史消息查询...")
        history = db.get_chat_history(group_id, limit=10)
        print(f"📊 直接查询历史消息数量: {len(history)}")
        
        for i, msg in enumerate(history[-5:], 1):  # 显示最后5条
            print(f"  {i}. ID: {msg['id']}, 内容: {msg['content']}, 发送者: {msg['sender_username']}")
        
        # 5. 测试聊天管理器的历史消息加载
        print(f"\n🔧 测试聊天管理器的历史消息加载...")
        
        if users:
            test_user_id = users[0][0]
            test_username = users[0][1]
            print(f"使用测试用户: {test_username} (ID: {test_user_id})")
            
            try:
                from server.core.chat_manager import ChatManager
                from server.core.user_manager import UserManager
                
                user_manager = UserManager(db)
                chat_manager = ChatManager(db, user_manager)
                
                # 测试加载历史消息
                history_messages = chat_manager.load_chat_history_for_user(group_id, test_user_id, limit=10)
                print(f"📊 聊天管理器加载的历史消息数量: {len(history_messages)}")
                
                for i, msg in enumerate(history_messages[-3:], 1):  # 显示最后3条
                    print(f"  {i}. 消息ID: {msg.message_id}, 内容: {msg.content}, 发送者: {msg.sender_username}")
                    print(f"     消息类型: {msg.message_type}, 聊天组ID: {msg.chat_group_id}")
                
            except Exception as e:
                print(f"❌ 聊天管理器测试失败: {e}")
                import traceback
                traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_server_enter_chat_logic():
    """测试服务器进入聊天组的逻辑"""
    print("\n🧪 测试服务器进入聊天组的逻辑...")
    
    try:
        from server.database.models import DatabaseManager
        from server.core.chat_manager import ChatManager
        from server.core.user_manager import UserManager
        
        db = DatabaseManager()
        user_manager = UserManager(db)
        chat_manager = ChatManager(db, user_manager)
        
        # 获取一个测试用户
        import sqlite3
        conn = sqlite3.connect("server/data/chatroom.db")
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM users WHERE id IN (SELECT user_id FROM group_members WHERE group_id = 1) LIMIT 1')
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            print("❌ 没有找到测试用户")
            return False
        
        user_id, username = user_data
        print(f"使用测试用户: {username} (ID: {user_id})")
        
        # 1. 测试进入聊天组
        print(f"\n📋 测试进入{DEFAULT_PUBLIC_CHAT}聊天组...")
        try:
            group_info = chat_manager.enter_chat_group(DEFAULT_PUBLIC_CHAT, user_id)
            print(f"✅ 成功进入聊天组: {group_info}")
        except Exception as e:
            print(f"❌ 进入聊天组失败: {e}")
            return False
        
        # 2. 测试加载历史消息
        print(f"\n📨 测试加载历史消息...")
        try:
            history_messages = chat_manager.load_chat_history_for_user(group_info['id'], user_id, limit=10)
            print(f"✅ 成功加载历史消息: {len(history_messages)}条")
            
            for i, msg in enumerate(history_messages[-3:], 1):
                print(f"  {i}. 内容: {msg.content}, 发送者: {msg.sender_username}")
            
            return len(history_messages) > 0
            
        except Exception as e:
            print(f"❌ 加载历史消息失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ 服务器进入聊天组逻辑测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 开始调试服务器端历史消息加载逻辑...")
    
    # 测试1: 数据库管理器
    print("\n" + "="*50)
    print("测试1: 数据库管理器")
    print("="*50)
    db_test_result = test_database_manager()
    
    # 测试2: 服务器进入聊天组逻辑
    print("\n" + "="*50)
    print("测试2: 服务器进入聊天组逻辑")
    print("="*50)
    server_test_result = test_server_enter_chat_logic()
    
    # 总结
    print("\n" + "="*50)
    print("测试结果总结")
    print("="*50)
    print(f"数据库管理器测试: {'✅ 通过' if db_test_result else '❌ 失败'}")
    print(f"服务器逻辑测试: {'✅ 通过' if server_test_result else '❌ 失败'}")
    
    if db_test_result and server_test_result:
        print("\n🎉 所有测试通过！服务器端历史消息加载逻辑正常。")
        print("问题可能在客户端或网络通信层面。")
    else:
        print("\n💥 发现问题！需要进一步调查。")
    
    return db_test_result and server_test_result


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
