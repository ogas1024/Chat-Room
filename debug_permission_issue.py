#!/usr/bin/env python3
"""
调试权限问题
调查用户进入聊天组后的权限检查问题
"""

import sys
import os
import sqlite3

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from shared.constants import DEFAULT_PUBLIC_CHAT


def debug_user_permissions():
    """调试用户权限问题"""
    print("🔍 调试用户权限问题...")
    
    try:
        # 连接数据库
        conn = sqlite3.connect("server/data/chatroom.db")
        cursor = conn.cursor()
        
        # 1. 检查所有用户
        print("\n👤 所有用户:")
        cursor.execute('SELECT id, username FROM users ORDER BY id')
        users = cursor.fetchall()
        for user in users:
            print(f"  - ID: {user[0]}, 用户名: {user[1]}")
        
        # 2. 检查public聊天组信息
        print(f"\n📋 {DEFAULT_PUBLIC_CHAT}聊天组信息:")
        cursor.execute('SELECT id, name FROM chat_groups WHERE name = ?', (DEFAULT_PUBLIC_CHAT,))
        public_group = cursor.fetchone()
        if public_group:
            public_group_id = public_group[0]
            print(f"  - ID: {public_group_id}, 名称: {public_group[1]}")
        else:
            print(f"  ❌ 未找到{DEFAULT_PUBLIC_CHAT}聊天组")
            return False
        
        # 3. 检查group_members表中的成员关系
        print(f"\n👥 {DEFAULT_PUBLIC_CHAT}聊天组成员关系:")
        cursor.execute('''
            SELECT gm.user_id, u.username, gm.joined_at
            FROM group_members gm
            JOIN users u ON gm.user_id = u.id
            WHERE gm.group_id = ?
            ORDER BY gm.user_id
        ''', (public_group_id,))
        
        members = cursor.fetchall()
        print(f"  成员总数: {len(members)}")
        for member in members:
            print(f"  - 用户ID: {member[0]}, 用户名: {member[1]}, 加入时间: {member[2]}")
        
        # 4. 测试特定用户的权限检查
        print(f"\n🔐 测试用户权限检查:")
        test_users = ['test', 'test1']
        
        for username in test_users:
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            user_data = cursor.fetchone()
            if user_data:
                user_id = user_data[0]
                
                # 检查是否在group_members表中
                cursor.execute(
                    'SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?',
                    (public_group_id, user_id)
                )
                is_member = cursor.fetchone() is not None
                
                print(f"  - 用户 {username} (ID: {user_id}): {'✅ 是成员' if is_member else '❌ 不是成员'}")
                
                if not is_member:
                    print(f"    ⚠️ 用户 {username} 不在{DEFAULT_PUBLIC_CHAT}聊天组的成员列表中！")
            else:
                print(f"  - 用户 {username}: ❌ 不存在")
        
        # 5. 检查最近的消息发送记录
        print(f"\n📨 最近的消息记录:")
        cursor.execute('''
            SELECT m.id, m.content, u.username, m.timestamp, m.group_id
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.group_id = ?
            ORDER BY m.timestamp DESC
            LIMIT 10
        ''', (public_group_id,))
        
        recent_messages = cursor.fetchall()
        for msg in recent_messages:
            print(f"  - ID: {msg[0]}, 内容: {msg[1]}, 发送者: {msg[2]}, 时间: {msg[3]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 调试权限问题失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enter_chat_logic():
    """测试进入聊天组的逻辑"""
    print("\n🧪 测试进入聊天组的逻辑...")
    
    try:
        from server.database.connection import DatabaseConnection
        from server.core.chat_manager import ChatManager
        from server.core.user_manager import UserManager
        
        # 初始化组件
        DatabaseConnection.set_database_path("server/data/chatroom.db")
        db = DatabaseConnection.get_instance()
        user_manager = UserManager()
        chat_manager = ChatManager(user_manager)
        
        # 获取test1用户信息
        conn = sqlite3.connect("server/data/chatroom.db")
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM users WHERE username = ?', ('test1',))
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            print("❌ 未找到test1用户")
            return False
        
        user_id, username = user_data
        print(f"✅ 找到用户: {username} (ID: {user_id})")
        
        # 测试进入聊天组前的权限检查
        print(f"\n📋 进入{DEFAULT_PUBLIC_CHAT}聊天组前的权限检查:")
        public_group = db.get_chat_group_by_name(DEFAULT_PUBLIC_CHAT)
        group_id = public_group['id']
        
        is_member_before = db.is_user_in_chat_group(group_id, user_id)
        print(f"进入前是否是成员: {is_member_before}")
        
        # 执行进入聊天组
        print(f"\n🚪 执行进入{DEFAULT_PUBLIC_CHAT}聊天组...")
        try:
            group_info = chat_manager.enter_chat_group(DEFAULT_PUBLIC_CHAT, user_id)
            print(f"✅ 成功进入聊天组: {group_info}")
        except Exception as e:
            print(f"❌ 进入聊天组失败: {e}")
            return False
        
        # 测试进入聊天组后的权限检查
        print(f"\n📋 进入{DEFAULT_PUBLIC_CHAT}聊天组后的权限检查:")
        is_member_after = db.is_user_in_chat_group(group_id, user_id)
        print(f"进入后是否是成员: {is_member_after}")
        
        if not is_member_after:
            print("❌ 进入聊天组后用户仍然不是成员！这是问题所在。")
            return False
        
        # 测试发送消息的权限检查
        print(f"\n📨 测试发送消息的权限检查...")
        try:
            test_message = chat_manager.send_message(user_id, group_id, "测试消息")
            print(f"✅ 消息发送成功: {test_message.content}")
            return True
        except Exception as e:
            print(f"❌ 消息发送失败: {e}")
            return False
        
    except Exception as e:
        print(f"❌ 测试进入聊天组逻辑失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_enter_chat_group_implementation():
    """检查进入聊天组的实现"""
    print("\n🔍 检查进入聊天组的实现...")
    
    try:
        # 查看enter_chat_group方法的实现
        with open("server/core/chat_manager.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 查找enter_chat_group方法
        if "def enter_chat_group(self, group_name: str, user_id: int)" in content:
            print("✅ 找到enter_chat_group方法")
            
            # 检查是否有加入聊天组的逻辑
            if "join_chat_group" in content:
                print("✅ 方法中包含join_chat_group调用")
            else:
                print("❌ 方法中没有join_chat_group调用")
                return False
        else:
            print("❌ 未找到enter_chat_group方法")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 检查实现失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 开始调试权限问题...")
    
    tests = [
        ("用户权限调试", debug_user_permissions),
        ("进入聊天组实现检查", check_enter_chat_group_implementation),
        ("进入聊天组逻辑测试", test_enter_chat_logic),
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
        print("\n🎉 所有测试通过！权限逻辑正常。")
    else:
        print("\n💥 发现权限问题！")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
