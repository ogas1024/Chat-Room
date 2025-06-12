#!/usr/bin/env python3
"""
调试数据库表结构
检查实际的数据库表和成员关系
"""

import sys
import os
import sqlite3

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from shared.constants import DEFAULT_PUBLIC_CHAT


def debug_database_schema():
    """调试数据库表结构"""
    print("🔍 调试数据库表结构...")
    
    db_path = "server/data/chatroom.db"
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 获取所有表名
        print("\n📋 数据库中的所有表:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        
        # 2. 检查group_members表
        print("\n🔍 检查group_members表:")
        try:
            cursor.execute("SELECT COUNT(*) FROM group_members")
            count = cursor.fetchone()[0]
            print(f"✅ group_members表存在，记录数: {count}")
            
            # 查看表结构
            cursor.execute("PRAGMA table_info(group_members)")
            schema = cursor.fetchall()
            print("group_members表结构:")
            for col in schema:
                print(f"  - {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'}")
            
            # 查看所有成员关系
            cursor.execute('''
                SELECT gm.group_id, gm.user_id, gm.joined_at,
                       cg.name as group_name, u.username
                FROM group_members gm
                JOIN chat_groups cg ON gm.group_id = cg.id
                JOIN users u ON gm.user_id = u.id
                ORDER BY gm.group_id, gm.user_id
            ''')
            members = cursor.fetchall()
            print(f"\n👥 所有成员关系 (总数: {len(members)}):")
            for member in members:
                print(f"  - 聊天组: {member[3]} (ID: {member[0]}), 用户: {member[4]} (ID: {member[1]}), 加入时间: {member[2]}")
            
        except sqlite3.OperationalError as e:
            print(f"❌ group_members表不存在或查询失败: {e}")
        
        # 3. 检查public聊天组的成员
        print(f"\n🔍 检查{DEFAULT_PUBLIC_CHAT}聊天组的成员:")
        cursor.execute('SELECT id FROM chat_groups WHERE name = ?', (DEFAULT_PUBLIC_CHAT,))
        result = cursor.fetchone()
        if result:
            public_group_id = result[0]
            print(f"✅ {DEFAULT_PUBLIC_CHAT}聊天组ID: {public_group_id}")
            
            try:
                cursor.execute('''
                    SELECT u.id, u.username, gm.joined_at
                    FROM users u
                    JOIN group_members gm ON u.id = gm.user_id
                    WHERE gm.group_id = ?
                    ORDER BY gm.joined_at ASC
                ''', (public_group_id,))
                
                members = cursor.fetchall()
                print(f"📊 {DEFAULT_PUBLIC_CHAT}聊天组成员数: {len(members)}")
                for member in members:
                    print(f"  - 用户ID: {member[0]}, 用户名: {member[1]}, 加入时间: {member[2]}")
                    
            except sqlite3.OperationalError as e:
                print(f"❌ 查询{DEFAULT_PUBLIC_CHAT}聊天组成员失败: {e}")
        else:
            print(f"❌ 未找到{DEFAULT_PUBLIC_CHAT}聊天组")
        
        # 4. 测试用户权限检查
        print(f"\n🧪 测试用户权限检查:")
        cursor.execute('SELECT id, username FROM users ORDER BY id')
        users = cursor.fetchall()
        
        for user in users[:5]:  # 只测试前5个用户
            user_id, username = user
            cursor.execute(
                "SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?",
                (public_group_id, user_id)
            )
            is_member = cursor.fetchone() is not None
            print(f"  - 用户 {username} (ID: {user_id}) 是否在{DEFAULT_PUBLIC_CHAT}聊天组中: {is_member}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 调试数据库表结构失败: {e}")
        import traceback
        traceback.print_exc()


def test_user_permission_check():
    """测试用户权限检查逻辑"""
    print("\n🧪 测试用户权限检查逻辑...")
    
    try:
        from server.database.models import DatabaseManager
        
        db = DatabaseManager()
        
        # 获取public聊天组信息
        public_group = db.get_chat_group_by_name(DEFAULT_PUBLIC_CHAT)
        print(f"✅ 获取{DEFAULT_PUBLIC_CHAT}聊天组: {public_group}")
        
        # 获取一些用户
        db_path = "server/data/chatroom.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM users LIMIT 5')
        users = cursor.fetchall()
        conn.close()
        
        # 测试每个用户的权限
        for user_id, username in users:
            is_member = db.is_user_in_chat_group(public_group['id'], user_id)
            print(f"  - 用户 {username} (ID: {user_id}) 权限检查结果: {is_member}")
            
            if is_member:
                # 如果用户有权限，测试获取历史消息
                try:
                    history = db.get_chat_history(public_group['id'], limit=5)
                    print(f"    ✅ 可以获取历史消息，数量: {len(history)}")
                except Exception as e:
                    print(f"    ❌ 获取历史消息失败: {e}")
        
    except Exception as e:
        print(f"❌ 测试用户权限检查失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_database_schema()
    test_user_permission_check()
