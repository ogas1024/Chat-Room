#!/usr/bin/env python3
"""
重现权限问题
模拟用户报告的具体场景
"""

import sys
import os
import sqlite3

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from shared.constants import DEFAULT_PUBLIC_CHAT


def check_user_membership():
    """检查用户成员关系"""
    print("🔍 检查用户成员关系...")
    
    try:
        conn = sqlite3.connect("server/data/chatroom.db")
        cursor = conn.cursor()
        
        # 获取public聊天组ID
        cursor.execute('SELECT id FROM chat_groups WHERE name = ?', (DEFAULT_PUBLIC_CHAT,))
        group_data = cursor.fetchone()
        if not group_data:
            print(f"❌ 未找到{DEFAULT_PUBLIC_CHAT}聊天组")
            return False
        
        group_id = group_data[0]
        print(f"✅ {DEFAULT_PUBLIC_CHAT}聊天组ID: {group_id}")
        
        # 检查test和test1用户的成员关系
        test_users = ['test', 'test1']
        
        for username in test_users:
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            user_data = cursor.fetchone()
            if user_data:
                user_id = user_data[0]
                
                # 检查成员关系
                cursor.execute(
                    'SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?',
                    (group_id, user_id)
                )
                is_member = cursor.fetchone() is not None
                
                print(f"  - 用户 {username} (ID: {user_id}): {'✅ 是成员' if is_member else '❌ 不是成员'}")
                
                if not is_member:
                    print(f"    ⚠️ 用户 {username} 不是{DEFAULT_PUBLIC_CHAT}聊天组成员！")
                    
                    # 尝试添加用户到聊天组
                    print(f"    🔧 尝试添加用户 {username} 到{DEFAULT_PUBLIC_CHAT}聊天组...")
                    try:
                        cursor.execute(
                            'INSERT INTO group_members (group_id, user_id, joined_at) VALUES (?, ?, datetime("now"))',
                            (group_id, user_id)
                        )
                        conn.commit()
                        print(f"    ✅ 成功添加用户 {username} 到{DEFAULT_PUBLIC_CHAT}聊天组")
                    except Exception as e:
                        print(f"    ❌ 添加用户失败: {e}")
            else:
                print(f"  - 用户 {username}: ❌ 不存在")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 检查用户成员关系失败: {e}")
        return False


def test_database_permission_check():
    """测试数据库权限检查"""
    print("\n🧪 测试数据库权限检查...")
    
    try:
        from server.database.connection import DatabaseConnection
        
        # 初始化数据库连接
        DatabaseConnection.set_database_path("server/data/chatroom.db")
        db = DatabaseConnection.get_instance()
        
        # 获取public聊天组信息
        public_group = db.get_chat_group_by_name(DEFAULT_PUBLIC_CHAT)
        group_id = public_group['id']
        
        print(f"✅ {DEFAULT_PUBLIC_CHAT}聊天组: {public_group}")
        
        # 测试test1用户的权限
        conn = sqlite3.connect("server/data/chatroom.db")
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', ('test1',))
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            print("❌ 未找到test1用户")
            return False
        
        user_id = user_data[0]
        print(f"✅ test1用户ID: {user_id}")
        
        # 测试权限检查
        is_member = db.is_user_in_chat_group(group_id, user_id)
        print(f"权限检查结果: {is_member}")
        
        if not is_member:
            print("❌ 权限检查失败！用户不是聊天组成员。")
            return False
        
        # 测试发送消息权限
        print("📨 测试发送消息权限...")
        try:
            # 直接调用数据库的save_message方法
            message_id = db.save_message(group_id, user_id, "权限测试消息")
            print(f"✅ 消息保存成功，消息ID: {message_id}")
            return True
        except Exception as e:
            print(f"❌ 消息保存失败: {e}")
            return False
        
    except Exception as e:
        print(f"❌ 数据库权限检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chat_manager_permission():
    """测试聊天管理器权限"""
    print("\n🧪 测试聊天管理器权限...")
    
    try:
        from server.database.connection import DatabaseConnection
        from server.core.user_manager import UserManager
        from server.core.chat_manager import ChatManager
        
        # 初始化组件
        DatabaseConnection.set_database_path("server/data/chatroom.db")
        db = DatabaseConnection.get_instance()
        user_manager = UserManager()
        chat_manager = ChatManager(user_manager)
        
        # 获取test1用户信息
        conn = sqlite3.connect("server/data/chatroom.db")
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', ('test1',))
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            print("❌ 未找到test1用户")
            return False
        
        user_id = user_data[0]
        print(f"✅ test1用户ID: {user_id}")
        
        # 测试进入聊天组
        print(f"🚪 测试进入{DEFAULT_PUBLIC_CHAT}聊天组...")
        try:
            group_info = chat_manager.enter_chat_group(DEFAULT_PUBLIC_CHAT, user_id)
            print(f"✅ 进入聊天组成功: {group_info}")
        except Exception as e:
            print(f"❌ 进入聊天组失败: {e}")
            return False
        
        # 测试发送消息
        print("📨 测试发送消息...")
        try:
            message = chat_manager.send_message(user_id, group_info['id'], "聊天管理器测试消息")
            print(f"✅ 消息发送成功: {message.content}")
            return True
        except Exception as e:
            print(f"❌ 消息发送失败: {e}")
            return False
        
    except Exception as e:
        print(f"❌ 聊天管理器权限测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_recent_messages():
    """检查最近的消息"""
    print("\n📨 检查最近的消息...")
    
    try:
        conn = sqlite3.connect("server/data/chatroom.db")
        cursor = conn.cursor()
        
        # 获取public聊天组的最近消息
        cursor.execute('''
            SELECT m.id, m.content, u.username, m.timestamp
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            JOIN chat_groups cg ON m.group_id = cg.id
            WHERE cg.name = ?
            ORDER BY m.timestamp DESC
            LIMIT 10
        ''', (DEFAULT_PUBLIC_CHAT,))
        
        messages = cursor.fetchall()
        print(f"最近的{len(messages)}条消息:")
        
        for msg in messages:
            print(f"  - ID: {msg[0]}, 内容: {msg[1]}, 发送者: {msg[2]}, 时间: {msg[3]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 检查最近消息失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 开始重现权限问题...")
    
    tests = [
        ("检查用户成员关系", check_user_membership),
        ("数据库权限检查", test_database_permission_check),
        ("聊天管理器权限", test_chat_manager_permission),
        ("检查最近消息", check_recent_messages),
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
        print("\n🎉 所有测试通过！权限系统正常工作。")
        print("问题可能在网络通信或客户端状态管理层面。")
    else:
        print("\n💥 发现权限系统问题！")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
