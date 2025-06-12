#!/usr/bin/env python3
"""
简单的调试测试
直接测试关键的权限检查和历史消息加载逻辑
"""

import sys
import os
import sqlite3

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def simple_permission_test():
    """简单的权限测试"""
    print("🧪 简单的权限测试...")
    
    try:
        # 直接使用SQLite查询
        conn = sqlite3.connect("server/data/chatroom.db")
        cursor = conn.cursor()
        
        # 1. 获取public聊天组的一个成员
        cursor.execute('''
            SELECT gm.user_id, u.username 
            FROM group_members gm 
            JOIN users u ON gm.user_id = u.id 
            WHERE gm.group_id = 1 
            LIMIT 1
        ''')
        user_data = cursor.fetchone()
        
        if not user_data:
            print("❌ 没有找到public聊天组的成员")
            return False
        
        user_id, username = user_data
        print(f"✅ 找到测试用户: {username} (ID: {user_id})")
        
        # 2. 测试权限检查查询
        cursor.execute(
            "SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?",
            (1, user_id)
        )
        result = cursor.fetchone()
        has_permission = result is not None
        print(f"📋 权限检查结果: {has_permission}")
        
        # 3. 测试历史消息查询
        cursor.execute('''
            SELECT m.id, m.content, m.message_type, m.timestamp,
                   u.id as sender_id, u.username as sender_username
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.group_id = ?
            ORDER BY m.timestamp DESC
            LIMIT ?
        ''', (1, 5))
        
        messages = cursor.fetchall()
        print(f"📨 历史消息查询结果: {len(messages)}条消息")
        
        for msg in messages:
            print(f"  - ID: {msg[0]}, 内容: {msg[1]}, 发送者: {msg[5]}")
        
        conn.close()
        
        return has_permission and len(messages) > 0
        
    except Exception as e:
        print(f"❌ 简单权限测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_manager_directly():
    """直接测试数据库管理器"""
    print("\n🧪 直接测试数据库管理器...")
    
    try:
        from server.database.models import DatabaseManager
        
        db = DatabaseManager("server/data/chatroom.db")
        
        # 获取一个测试用户
        conn = sqlite3.connect("server/data/chatroom.db")
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM group_members WHERE group_id = 1 LIMIT 1')
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            print("❌ 没有找到测试用户")
            return False
        
        user_id = user_data[0]
        print(f"✅ 使用测试用户ID: {user_id}")
        
        # 测试权限检查
        has_permission = db.is_user_in_chat_group(1, user_id)
        print(f"📋 数据库管理器权限检查: {has_permission}")
        
        if has_permission:
            # 测试历史消息获取
            history = db.get_chat_history(1, limit=5)
            print(f"📨 数据库管理器历史消息: {len(history)}条")
            
            for msg in history[-3:]:
                print(f"  - ID: {msg['id']}, 内容: {msg['content']}, 发送者: {msg['sender_username']}")
            
            return len(history) > 0
        else:
            print("❌ 权限检查失败")
            return False
        
    except Exception as e:
        print(f"❌ 数据库管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("🚀 开始简单调试测试...")
    
    # 测试1: 简单权限测试
    result1 = simple_permission_test()
    
    # 测试2: 数据库管理器测试
    result2 = test_database_manager_directly()
    
    print(f"\n📊 测试结果:")
    print(f"简单权限测试: {'✅ 通过' if result1 else '❌ 失败'}")
    print(f"数据库管理器测试: {'✅ 通过' if result2 else '❌ 失败'}")
    
    if result1 and result2:
        print("\n🎉 基础功能正常！问题可能在更高层的逻辑中。")
    else:
        print("\n💥 发现基础功能问题！")
    
    return result1 and result2


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
