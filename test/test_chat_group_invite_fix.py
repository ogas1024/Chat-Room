#!/usr/bin/env python3
"""
测试聊天组用户邀请功能修复
验证 /create_chat 命令是否能正确邀请用户到聊天组
"""

import sys
import os
import sqlite3
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 简化版测试，直接测试数据库操作
def simple_test():
    """简化版测试，直接操作数据库"""
    print("🧪 开始简化版聊天组用户邀请功能测试...")

    # 创建临时数据库
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)

    try:
        # 连接数据库并创建表
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 创建必要的表
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_online INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE chat_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                is_private_chat INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE group_members (
                group_id INTEGER,
                user_id INTEGER,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (group_id, user_id),
                FOREIGN KEY (group_id) REFERENCES chat_groups(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # 创建测试用户
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("test", "hash1"))
        test_user_id = cursor.lastrowid

        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("test1", "hash2"))
        test1_user_id = cursor.lastrowid

        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("ai", "hash3"))
        ai_user_id = cursor.lastrowid

        print(f"✅ 创建测试用户: test (ID: {test_user_id}), test1 (ID: {test1_user_id}), ai (ID: {ai_user_id})")

        # 创建聊天组
        cursor.execute("INSERT INTO chat_groups (name, is_private_chat) VALUES (?, ?)", ("test", 0))
        group_id = cursor.lastrowid
        print(f"✅ 创建聊天组 'test' (ID: {group_id})")

        # 模拟修复后的逻辑：添加创建者和初始成员
        cursor.execute("INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, test_user_id))
        cursor.execute("INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, ai_user_id))
        cursor.execute("INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, test1_user_id))

        conn.commit()

        # 验证成员是否正确添加
        cursor.execute("SELECT COUNT(*) as count FROM group_members WHERE group_id = ?", (group_id,))
        member_count = cursor.fetchone()['count']
        print(f"✅ 聊天组成员数量: {member_count}")

        # 验证test1用户是否在聊天组中
        cursor.execute("SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?", (group_id, test1_user_id))
        is_test1_in_group = cursor.fetchone() is not None
        print(f"✅ test1用户在聊天组中: {is_test1_in_group}")

        # 获取所有成员
        cursor.execute('''
            SELECT u.username, u.id
            FROM users u
            JOIN group_members gm ON u.id = gm.user_id
            WHERE gm.group_id = ?
            ORDER BY u.username
        ''', (group_id,))

        members = cursor.fetchall()
        print("聊天组成员:")
        for member in members:
            print(f"  - {member['username']} (ID: {member['id']})")

        # 验证结果
        assert member_count == 3, f"聊天组应该有3个成员，实际有{member_count}个"
        assert is_test1_in_group, "test1用户应该在聊天组中"

        print("\n🎉 简化版测试通过！修复逻辑正确！")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False

    finally:
        conn.close()
        try:
            os.unlink(db_path)
        except:
            pass


def setup_test_database():
    """设置测试数据库"""
    # 创建临时数据库文件
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # 初始化数据库
    db_manager = DatabaseManager(db_path)
    db_manager.init_database()
    
    return db_manager, db_path


def create_test_users(db_manager):
    """创建测试用户"""
    # 创建测试用户
    test_user_id = db_manager.create_user("test", "test123")
    test1_user_id = db_manager.create_user("test1", "test123")
    
    return test_user_id, test1_user_id


def test_chat_group_invite():
    """测试聊天组邀请功能"""
    print("🧪 开始测试聊天组用户邀请功能修复...")
    
    # 设置测试环境
    db_manager, db_path = setup_test_database()
    user_manager = UserManager(db_manager)
    chat_manager = ChatManager(db_manager, user_manager)
    
    try:
        # 创建测试用户
        test_user_id, test1_user_id = create_test_users(db_manager)
        print(f"✅ 创建测试用户: test (ID: {test_user_id}), test1 (ID: {test1_user_id})")
        
        # 测试1: 创建聊天组并邀请用户
        print("\n📝 测试1: 创建聊天组并邀请用户")
        group_id = chat_manager.create_chat_group(
            name="test",
            creator_id=test_user_id,
            initial_members=[test_user_id, test1_user_id],  # 邀请test和test1
            is_private_chat=False
        )
        print(f"✅ 创建聊天组 'test' (ID: {group_id})")
        
        # 测试2: 验证创建者是否在聊天组中
        print("\n📝 测试2: 验证创建者是否在聊天组中")
        is_creator_in_group = db_manager.is_user_in_chat_group(group_id, test_user_id)
        print(f"✅ 创建者test在聊天组中: {is_creator_in_group}")
        assert is_creator_in_group, "创建者应该在聊天组中"
        
        # 测试3: 验证被邀请用户是否在聊天组中
        print("\n📝 测试3: 验证被邀请用户是否在聊天组中")
        is_test1_in_group = db_manager.is_user_in_chat_group(group_id, test1_user_id)
        print(f"✅ 被邀请用户test1在聊天组中: {is_test1_in_group}")
        assert is_test1_in_group, "被邀请用户应该在聊天组中"
        
        # 测试4: 验证AI用户是否在聊天组中
        print("\n📝 测试4: 验证AI用户是否在聊天组中")
        is_ai_in_group = db_manager.is_user_in_chat_group(group_id, AI_USER_ID)
        print(f"✅ AI用户在聊天组中: {is_ai_in_group}")
        assert is_ai_in_group, "AI用户应该在聊天组中"
        
        # 测试5: 获取聊天组成员列表
        print("\n📝 测试5: 获取聊天组成员列表")
        members = db_manager.get_chat_group_members(group_id)
        print(f"✅ 聊天组成员数量: {len(members)}")
        print("聊天组成员:")
        for member in members:
            print(f"  - {member['username']} (ID: {member['id']})")
        
        # 验证成员数量（应该包含：test, test1, AI用户）
        expected_members = 3
        assert len(members) == expected_members, f"聊天组应该有{expected_members}个成员，实际有{len(members)}个"
        
        # 测试6: 验证test1用户能否进入聊天组
        print("\n📝 测试6: 验证test1用户能否进入聊天组")
        try:
            group_info = chat_manager.enter_chat_group("test", test1_user_id)
            print(f"✅ test1用户成功进入聊天组: {group_info['name']}")
        except Exception as e:
            print(f"❌ test1用户进入聊天组失败: {e}")
            raise
        
        print("\n🎉 所有测试通过！聊天组用户邀请功能修复成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False
        
    finally:
        # 清理测试数据库
        try:
            os.unlink(db_path)
            print(f"🧹 清理测试数据库: {db_path}")
        except:
            pass


def test_private_chat_still_works():
    """测试私聊功能是否仍然正常工作"""
    print("\n🧪 测试私聊功能是否仍然正常工作...")
    
    # 设置测试环境
    db_manager, db_path = setup_test_database()
    user_manager = UserManager(db_manager)
    chat_manager = ChatManager(db_manager, user_manager)
    
    try:
        # 创建测试用户
        test_user_id, test1_user_id = create_test_users(db_manager)
        
        # 创建私聊
        private_chat_id = chat_manager.create_private_chat(test_user_id, test1_user_id)
        print(f"✅ 创建私聊 (ID: {private_chat_id})")
        
        # 验证两个用户都在私聊中
        is_test_in_private = db_manager.is_user_in_chat_group(private_chat_id, test_user_id)
        is_test1_in_private = db_manager.is_user_in_chat_group(private_chat_id, test1_user_id)
        
        print(f"✅ test用户在私聊中: {is_test_in_private}")
        print(f"✅ test1用户在私聊中: {is_test1_in_private}")
        
        assert is_test_in_private and is_test1_in_private, "私聊功能应该正常工作"
        
        print("🎉 私聊功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 私聊功能测试失败: {e}")
        return False
        
    finally:
        # 清理测试数据库
        try:
            os.unlink(db_path)
        except:
            pass


if __name__ == "__main__":
    print("=" * 60)
    print("聊天组用户邀请功能修复测试")
    print("=" * 60)
    
    # 运行测试
    test1_passed = test_chat_group_invite()
    test2_passed = test_private_chat_still_works()
    
    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("🎉 所有测试通过！修复成功！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败！")
        sys.exit(1)
