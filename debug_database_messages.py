#!/usr/bin/env python3
"""
调试数据库中的消息数据
检查public聊天组的消息存储情况
"""

import sys
import os
import sqlite3

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from shared.constants import DEFAULT_PUBLIC_CHAT


def debug_database():
    """调试数据库中的消息"""
    print("🔍 调试数据库中的消息数据...")
    
    db_path = "server/data/chatroom.db"
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 检查所有聊天组
        print("\n📋 所有聊天组:")
        cursor.execute('SELECT id, name, created_at FROM chat_groups ORDER BY id')
        groups = cursor.fetchall()
        for group in groups:
            print(f"  - ID: {group[0]}, 名称: {group[1]}, 创建时间: {group[2]}")
        
        # 2. 检查public聊天组
        print(f"\n🔍 检查{DEFAULT_PUBLIC_CHAT}聊天组:")
        cursor.execute('SELECT id, name FROM chat_groups WHERE name = ?', (DEFAULT_PUBLIC_CHAT,))
        public_group = cursor.fetchone()
        
        if not public_group:
            print(f"❌ 未找到{DEFAULT_PUBLIC_CHAT}聊天组")
            return
        
        public_group_id = public_group[0]
        print(f"✅ 找到{DEFAULT_PUBLIC_CHAT}聊天组: ID={public_group_id}")
        
        # 3. 检查public聊天组的所有消息
        print(f"\n📨 {DEFAULT_PUBLIC_CHAT}聊天组的所有消息:")
        cursor.execute('''
            SELECT m.id, m.content, m.message_type, m.timestamp,
                   u.username as sender_username
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.group_id = ?
            ORDER BY m.timestamp ASC
        ''', (public_group_id,))
        
        messages = cursor.fetchall()
        print(f"📊 消息总数: {len(messages)}")
        
        for i, msg in enumerate(messages, 1):
            print(f"  {i}. ID: {msg[0]}")
            print(f"     内容: {msg[1]}")
            print(f"     类型: {msg[2]}")
            print(f"     时间戳: {msg[3]}")
            print(f"     发送者: {msg[4]}")
            print()
        
        # 4. 检查public聊天组的成员
        print(f"\n👥 {DEFAULT_PUBLIC_CHAT}聊天组的成员:")
        cursor.execute('''
            SELECT u.id, u.username, cgm.joined_at
            FROM chat_group_members cgm
            JOIN users u ON cgm.user_id = u.id
            WHERE cgm.group_id = ?
            ORDER BY cgm.joined_at ASC
        ''', (public_group_id,))
        
        members = cursor.fetchall()
        print(f"📊 成员总数: {len(members)}")
        
        for member in members:
            print(f"  - 用户ID: {member[0]}, 用户名: {member[1]}, 加入时间: {member[2]}")
        
        # 5. 检查所有用户
        print("\n👤 所有用户:")
        cursor.execute('SELECT id, username, created_at FROM users ORDER BY id')
        users = cursor.fetchall()
        for user in users:
            print(f"  - ID: {user[0]}, 用户名: {user[1]}, 创建时间: {user[2]}")
        
        # 6. 检查数据库表结构
        print("\n🏗️ 数据库表结构:")
        
        # 检查messages表结构
        cursor.execute("PRAGMA table_info(messages)")
        messages_schema = cursor.fetchall()
        print("messages表结构:")
        for col in messages_schema:
            print(f"  - {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'}")
        
        # 检查chat_groups表结构
        cursor.execute("PRAGMA table_info(chat_groups)")
        groups_schema = cursor.fetchall()
        print("chat_groups表结构:")
        for col in groups_schema:
            print(f"  - {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 调试数据库失败: {e}")
        import traceback
        traceback.print_exc()


def test_chat_history_query():
    """测试聊天历史查询"""
    print("\n🧪 测试聊天历史查询...")
    
    db_path = "server/data/chatroom.db"
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取public聊天组ID
        cursor.execute('SELECT id FROM chat_groups WHERE name = ?', (DEFAULT_PUBLIC_CHAT,))
        result = cursor.fetchone()
        if not result:
            print(f"❌ 未找到{DEFAULT_PUBLIC_CHAT}聊天组")
            return
        
        group_id = result[0]
        print(f"✅ {DEFAULT_PUBLIC_CHAT}聊天组ID: {group_id}")
        
        # 使用与服务器相同的查询语句
        print("\n📋 使用服务器相同的查询语句:")
        cursor.execute('''
            SELECT m.id, m.content, m.message_type, m.timestamp,
                   u.id as sender_id, u.username as sender_username
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.group_id = ?
            ORDER BY m.timestamp DESC
            LIMIT ?
        ''', (group_id, 50))
        
        messages = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        messages = list(reversed(messages))  # 按时间正序返回
        
        print(f"📊 查询结果: {len(messages)}条消息")
        for msg in messages:
            print(f"  - ID: {msg['id']}, 内容: {msg['content']}, 发送者: {msg['sender_username']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 测试查询失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_database()
    test_chat_history_query()
