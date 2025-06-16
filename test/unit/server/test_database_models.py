"""
测试服务器数据库模型
测试用户、聊天组、消息等数据模型的CRUD操作
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

from server.database.models import DatabaseManager
from shared.constants import DEFAULT_PUBLIC_CHAT, AI_USER_ID
from shared.exceptions import DatabaseError, UserNotFoundError, ChatGroupNotFoundError
from test.fixtures.data_fixtures import UserFixtures, ChatGroupFixtures, MessageFixtures


class TestDatabaseManager:
    """测试数据库管理器"""
    
    def test_database_manager_creation(self, test_db_path):
        """测试数据库管理器创建"""
        db_manager = DatabaseManager(str(test_db_path))
        assert db_manager is not None
        assert db_manager.db_path == str(test_db_path)
    
    def test_init_database(self, test_db_path):
        """测试数据库初始化"""
        db_manager = DatabaseManager(str(test_db_path))
        db_manager.init_database()
        
        # 验证数据库文件存在
        assert test_db_path.exists()
        
        # 验证表结构
        with sqlite3.connect(str(test_db_path)) as conn:
            cursor = conn.cursor()
            
            # 检查用户表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            assert cursor.fetchone() is not None
            
            # 检查聊天组表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_groups'")
            assert cursor.fetchone() is not None
            
            # 检查消息表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
            assert cursor.fetchone() is not None
            
            # 检查文件元数据表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files_metadata'")
            assert cursor.fetchone() is not None
    
    def test_create_default_data(self, db_manager):
        """测试创建默认数据"""
        # 验证默认公频聊天组存在
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chat_groups WHERE name = ?", (DEFAULT_PUBLIC_CHAT,))
            public_chat = cursor.fetchone()
            assert public_chat is not None
            assert public_chat[2] == 0  # is_private_chat = False
            
            # 验证AI用户存在
            cursor.execute("SELECT * FROM users WHERE id = ?", (AI_USER_ID,))
            ai_user = cursor.fetchone()
            assert ai_user is not None
            assert "AI" in ai_user[1]  # username包含AI


class TestUserOperations:
    """测试用户相关操作"""
    
    def test_create_user_success(self, db_manager):
        """测试成功创建用户"""
        user_id = db_manager.create_user("alice", "password123")
        assert user_id > 0
        
        # 验证用户存在
        user = db_manager.get_user_by_username("alice")
        assert user is not None
        assert user['username'] == "alice"
        assert user['id'] == user_id
    
    def test_create_user_duplicate(self, db_manager):
        """测试创建重复用户"""
        # 创建第一个用户
        db_manager.create_user("alice", "password123")
        
        # 尝试创建重复用户
        with pytest.raises(DatabaseError):
            db_manager.create_user("alice", "password456")
    
    def test_create_user_with_chinese(self, db_manager):
        """测试创建中文用户名"""
        user_id = db_manager.create_user("测试用户", "密码123")
        assert user_id > 0
        
        user = db_manager.get_user_by_username("测试用户")
        assert user is not None
        assert user['username'] == "测试用户"
    
    def test_get_user_by_id(self, db_manager):
        """测试通过ID获取用户"""
        user_id = db_manager.create_user("bob", "password456")
        
        user = db_manager.get_user_by_id(user_id)
        assert user is not None
        assert user['id'] == user_id
        assert user['username'] == "bob"
    
    def test_get_user_by_username(self, db_manager):
        """测试通过用户名获取用户"""
        db_manager.create_user("charlie", "password789")
        
        user = db_manager.get_user_by_username("charlie")
        assert user is not None
        assert user['username'] == "charlie"
    
    def test_get_nonexistent_user(self, db_manager):
        """测试获取不存在的用户"""
        user = db_manager.get_user_by_username("nonexistent")
        assert user is None
        
        user = db_manager.get_user_by_id(999)
        assert user is None
    
    def test_verify_user_password(self, db_manager):
        """测试验证用户密码"""
        db_manager.create_user("alice", "password123")
        
        # 正确密码
        assert db_manager.verify_user_password("alice", "password123") is True
        
        # 错误密码
        assert db_manager.verify_user_password("alice", "wrongpassword") is False
        
        # 不存在的用户
        assert db_manager.verify_user_password("nonexistent", "password") is False
    
    def test_update_user_online_status(self, db_manager):
        """测试更新用户在线状态"""
        user_id = db_manager.create_user("alice", "password123")
        
        # 设置在线
        db_manager.update_user_online_status(user_id, True)
        user = db_manager.get_user_by_id(user_id)
        assert user['is_online'] == 1
        
        # 设置离线
        db_manager.update_user_online_status(user_id, False)
        user = db_manager.get_user_by_id(user_id)
        assert user['is_online'] == 0
    
    def test_get_online_users(self, db_manager):
        """测试获取在线用户列表"""
        # 创建用户
        user1_id = db_manager.create_user("alice", "password123")
        user2_id = db_manager.create_user("bob", "password456")
        user3_id = db_manager.create_user("charlie", "password789")
        
        # 设置在线状态
        db_manager.update_user_online_status(user1_id, True)
        db_manager.update_user_online_status(user2_id, True)
        db_manager.update_user_online_status(user3_id, False)
        
        online_users = db_manager.get_online_users()
        assert len(online_users) == 2
        
        usernames = [user['username'] for user in online_users]
        assert "alice" in usernames
        assert "bob" in usernames
        assert "charlie" not in usernames


class TestChatGroupOperations:
    """测试聊天组相关操作"""
    
    def test_create_chat_group(self, db_manager):
        """测试创建聊天组"""
        group_id = db_manager.create_chat_group("test_group", False)
        assert group_id > 0
        
        group = db_manager.get_chat_group_by_name("test_group")
        assert group is not None
        assert group['name'] == "test_group"
        assert group['is_private_chat'] == 0
    
    def test_create_private_chat_group(self, db_manager):
        """测试创建私聊组"""
        group_id = db_manager.create_chat_group("private_alice_bob", True)
        assert group_id > 0
        
        group = db_manager.get_chat_group_by_id(group_id)
        assert group is not None
        assert group['is_private_chat'] == 1
    
    def test_create_duplicate_chat_group(self, db_manager):
        """测试创建重复聊天组"""
        db_manager.create_chat_group("test_group", False)
        
        with pytest.raises(DatabaseError):
            db_manager.create_chat_group("test_group", False)
    
    def test_get_chat_group_by_id(self, db_manager):
        """测试通过ID获取聊天组"""
        group_id = db_manager.create_chat_group("test_group", False)
        
        group = db_manager.get_chat_group_by_id(group_id)
        assert group is not None
        assert group['id'] == group_id
        assert group['name'] == "test_group"
    
    def test_get_chat_group_by_name(self, db_manager):
        """测试通过名称获取聊天组"""
        db_manager.create_chat_group("test_group", False)
        
        group = db_manager.get_chat_group_by_name("test_group")
        assert group is not None
        assert group['name'] == "test_group"
    
    def test_get_all_chat_groups(self, db_manager):
        """测试获取所有聊天组"""
        # 创建几个聊天组
        db_manager.create_chat_group("group1", False)
        db_manager.create_chat_group("group2", False)
        db_manager.create_chat_group("private_group", True)
        
        all_groups = db_manager.get_all_chat_groups()
        # 包括默认的public聊天组
        assert len(all_groups) >= 4
        
        group_names = [group['name'] for group in all_groups]
        assert "group1" in group_names
        assert "group2" in group_names
        assert "private_group" in group_names
        assert DEFAULT_PUBLIC_CHAT in group_names
    
    def test_add_user_to_chat_group(self, db_manager):
        """测试将用户添加到聊天组"""
        user_id = db_manager.create_user("alice", "password123")
        group_id = db_manager.create_chat_group("test_group", False)
        
        db_manager.add_user_to_chat_group(user_id, group_id)
        
        # 验证用户在聊天组中
        members = db_manager.get_chat_group_members(group_id)
        assert len(members) == 1
        assert members[0]['username'] == "alice"
    
    def test_remove_user_from_chat_group(self, db_manager):
        """测试从聊天组移除用户"""
        user_id = db_manager.create_user("alice", "password123")
        group_id = db_manager.create_chat_group("test_group", False)
        
        # 添加用户
        db_manager.add_user_to_chat_group(user_id, group_id)
        assert len(db_manager.get_chat_group_members(group_id)) == 1
        
        # 移除用户
        db_manager.remove_user_from_chat_group(user_id, group_id)
        assert len(db_manager.get_chat_group_members(group_id)) == 0
    
    def test_get_user_chat_groups(self, db_manager):
        """测试获取用户加入的聊天组"""
        user_id = db_manager.create_user("alice", "password123")
        group1_id = db_manager.create_chat_group("group1", False)
        group2_id = db_manager.create_chat_group("group2", False)
        
        # 将用户添加到聊天组
        db_manager.add_user_to_chat_group(user_id, group1_id)
        db_manager.add_user_to_chat_group(user_id, group2_id)
        
        user_groups = db_manager.get_user_chat_groups(user_id)
        assert len(user_groups) == 2
        
        group_names = [group['name'] for group in user_groups]
        assert "group1" in group_names
        assert "group2" in group_names


class TestMessageOperations:
    """测试消息相关操作"""
    
    def test_save_message(self, db_manager):
        """测试保存消息"""
        user_id = db_manager.create_user("alice", "password123")
        group_id = db_manager.create_chat_group("test_group", False)
        
        message_id = db_manager.save_message(
            sender_id=user_id,
            chat_group_id=group_id,
            content="Hello world!",
            message_type="chat"
        )
        
        assert message_id > 0
    
    def test_get_chat_history(self, db_manager):
        """测试获取聊天历史"""
        user_id = db_manager.create_user("alice", "password123")
        group_id = db_manager.create_chat_group("test_group", False)
        
        # 保存几条消息
        db_manager.save_message(user_id, group_id, "Message 1", "chat")
        db_manager.save_message(user_id, group_id, "Message 2", "chat")
        db_manager.save_message(user_id, group_id, "Message 3", "chat")
        
        # 获取聊天历史
        history = db_manager.get_chat_history(group_id, limit=10)
        assert len(history) == 3
        
        # 验证消息顺序（最新的在前）
        assert history[0]['content'] == "Message 3"
        assert history[1]['content'] == "Message 2"
        assert history[2]['content'] == "Message 1"
    
    def test_get_chat_history_with_limit(self, db_manager):
        """测试限制数量的聊天历史"""
        user_id = db_manager.create_user("alice", "password123")
        group_id = db_manager.create_chat_group("test_group", False)
        
        # 保存5条消息
        for i in range(5):
            db_manager.save_message(user_id, group_id, f"Message {i+1}", "chat")
        
        # 限制获取2条
        history = db_manager.get_chat_history(group_id, limit=2)
        assert len(history) == 2
        assert history[0]['content'] == "Message 5"
        assert history[1]['content'] == "Message 4"
    
    def test_save_message_with_chinese(self, db_manager):
        """测试保存中文消息"""
        user_id = db_manager.create_user("测试用户", "密码123")
        group_id = db_manager.create_chat_group("中文聊天室", False)
        
        message_id = db_manager.save_message(
            sender_id=user_id,
            chat_group_id=group_id,
            content="你好，世界！这是一条中文消息。",
            message_type="chat"
        )
        
        assert message_id > 0
        
        history = db_manager.get_chat_history(group_id, limit=1)
        assert len(history) == 1
        assert history[0]['content'] == "你好，世界！这是一条中文消息。"
        assert history[0]['sender_username'] == "测试用户"


class TestFileOperations:
    """测试文件相关操作"""
    
    def test_save_file_metadata(self, db_manager):
        """测试保存文件元数据"""
        user_id = db_manager.create_user("alice", "password123")
        group_id = db_manager.create_chat_group("test_group", False)
        
        file_id = db_manager.save_file_metadata(
            original_filename="test.txt",
            server_filepath="/path/to/server/file.txt",
            file_size=1024,
            uploader_id=user_id,
            chat_group_id=group_id
        )
        
        assert file_id > 0
    
    def test_get_file_metadata(self, db_manager):
        """测试获取文件元数据"""
        user_id = db_manager.create_user("alice", "password123")
        group_id = db_manager.create_chat_group("test_group", False)
        
        file_id = db_manager.save_file_metadata(
            original_filename="test.txt",
            server_filepath="/path/to/server/file.txt",
            file_size=1024,
            uploader_id=user_id,
            chat_group_id=group_id
        )
        
        file_info = db_manager.get_file_metadata(file_id)
        assert file_info is not None
        assert file_info['original_filename'] == "test.txt"
        assert file_info['file_size'] == 1024
        assert file_info['uploader_username'] == "alice"
    
    def test_get_chat_group_files(self, db_manager):
        """测试获取聊天组文件列表"""
        user_id = db_manager.create_user("alice", "password123")
        group_id = db_manager.create_chat_group("test_group", False)
        
        # 保存几个文件
        db_manager.save_file_metadata("file1.txt", "/path/1.txt", 1024, user_id, group_id)
        db_manager.save_file_metadata("file2.txt", "/path/2.txt", 2048, user_id, group_id)
        
        files = db_manager.get_chat_group_files(group_id)
        assert len(files) == 2
        
        filenames = [f['original_filename'] for f in files]
        assert "file1.txt" in filenames
        assert "file2.txt" in filenames


class TestDatabaseTransactions:
    """测试数据库事务"""
    
    def test_transaction_rollback(self, db_manager):
        """测试事务回滚"""
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # 插入用户
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    ("test_user", "hash")
                )
                
                # 故意引发错误
                cursor.execute("INSERT INTO invalid_table VALUES (1)")
                
        except sqlite3.OperationalError:
            pass  # 预期的错误
        
        # 验证用户没有被插入（事务回滚）
        user = db_manager.get_user_by_username("test_user")
        assert user is None
    
    def test_concurrent_access(self, db_manager):
        """测试并发访问"""
        import threading
        import time
        
        results = []
        
        def create_user(username):
            try:
                user_id = db_manager.create_user(username, "password")
                results.append(user_id)
            except Exception as e:
                results.append(str(e))
        
        # 创建多个线程同时创建用户
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_user, args=(f"user_{i}",))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        assert len(results) == 5
        successful_creates = [r for r in results if isinstance(r, int)]
        assert len(successful_creates) == 5
