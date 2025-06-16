"""
测试服务器用户管理器
测试用户注册、登录、会话管理等功能
"""

import pytest
import time
from unittest.mock import Mock, patch

from server.core.user_manager import UserManager
from server.database.models import DatabaseManager
from shared.exceptions import UserNotFoundError, AuthenticationError
from test.fixtures.data_fixtures import UserFixtures


class TestUserManager:
    """测试用户管理器"""
    
    def test_user_manager_creation(self, db_manager):
        """测试用户管理器创建"""
        user_manager = UserManager(db_manager)
        assert user_manager is not None
        assert user_manager.db_manager == db_manager
        assert hasattr(user_manager, 'active_sessions')
        assert isinstance(user_manager.active_sessions, dict)
    
    def test_register_user_success(self, db_manager):
        """测试成功注册用户"""
        user_manager = UserManager(db_manager)
        
        success, message, user_id = user_manager.register_user("alice", "password123")
        
        assert success is True
        assert user_id > 0
        assert "成功" in message
        
        # 验证用户已创建
        user = db_manager.get_user_by_username("alice")
        assert user is not None
        assert user['username'] == "alice"
    
    def test_register_user_duplicate(self, db_manager):
        """测试注册重复用户"""
        user_manager = UserManager(db_manager)
        
        # 注册第一个用户
        user_manager.register_user("alice", "password123")
        
        # 尝试注册重复用户
        success, message, user_id = user_manager.register_user("alice", "password456")
        
        assert success is False
        assert user_id is None
        assert "已存在" in message
    
    def test_register_user_invalid_username(self, db_manager):
        """测试注册无效用户名"""
        user_manager = UserManager(db_manager)
        
        # 空用户名
        success, message, user_id = user_manager.register_user("", "password123")
        assert success is False
        assert "用户名" in message
        
        # 用户名太短
        success, message, user_id = user_manager.register_user("ab", "password123")
        assert success is False
        assert "长度" in message
        
        # 用户名太长
        success, message, user_id = user_manager.register_user("a" * 21, "password123")
        assert success is False
        assert "长度" in message
    
    def test_register_user_invalid_password(self, db_manager):
        """测试注册无效密码"""
        user_manager = UserManager(db_manager)
        
        # 密码太短
        success, message, user_id = user_manager.register_user("alice", "123")
        assert success is False
        assert "密码" in message
    
    def test_login_user_success(self, db_manager):
        """测试成功登录用户"""
        user_manager = UserManager(db_manager)
        
        # 先注册用户
        user_manager.register_user("alice", "password123")
        
        # 登录
        success, message, user_info = user_manager.login_user("alice", "password123")
        
        assert success is True
        assert user_info is not None
        assert user_info['username'] == "alice"
        assert "成功" in message
        
        # 验证用户在线状态
        user = db_manager.get_user_by_username("alice")
        assert user['is_online'] == 1
    
    def test_login_user_wrong_password(self, db_manager):
        """测试错误密码登录"""
        user_manager = UserManager(db_manager)
        
        # 先注册用户
        user_manager.register_user("alice", "password123")
        
        # 使用错误密码登录
        success, message, user_info = user_manager.login_user("alice", "wrongpassword")
        
        assert success is False
        assert user_info is None
        assert "密码" in message
    
    def test_login_nonexistent_user(self, db_manager):
        """测试登录不存在的用户"""
        user_manager = UserManager(db_manager)
        
        success, message, user_info = user_manager.login_user("nonexistent", "password")
        
        assert success is False
        assert user_info is None
        assert "不存在" in message
    
    def test_logout_user(self, db_manager):
        """测试用户登出"""
        user_manager = UserManager(db_manager)
        
        # 注册并登录用户
        user_manager.register_user("alice", "password123")
        success, message, user_info = user_manager.login_user("alice", "password123")
        user_id = user_info['id']
        
        # 登出
        success, message = user_manager.logout_user(user_id)
        
        assert success is True
        assert "成功" in message
        
        # 验证用户离线状态
        user = db_manager.get_user_by_id(user_id)
        assert user['is_online'] == 0
    
    def test_logout_nonexistent_user(self, db_manager):
        """测试登出不存在的用户"""
        user_manager = UserManager(db_manager)
        
        success, message = user_manager.logout_user(999)
        
        assert success is False
        assert "不存在" in message
    
    def test_get_user_info(self, db_manager):
        """测试获取用户信息"""
        user_manager = UserManager(db_manager)
        
        # 注册用户
        user_manager.register_user("alice", "password123")
        user = db_manager.get_user_by_username("alice")
        user_id = user['id']
        
        # 获取用户信息
        user_info = user_manager.get_user_info(user_id)
        
        assert user_info is not None
        assert user_info['username'] == "alice"
        assert user_info['id'] == user_id
        assert 'password_hash' not in user_info  # 密码不应该返回
    
    def test_get_online_users(self, db_manager):
        """测试获取在线用户列表"""
        user_manager = UserManager(db_manager)
        
        # 注册多个用户
        user_manager.register_user("alice", "password123")
        user_manager.register_user("bob", "password456")
        user_manager.register_user("charlie", "password789")
        
        # 部分用户登录
        user_manager.login_user("alice", "password123")
        user_manager.login_user("bob", "password456")
        
        # 获取在线用户
        online_users = user_manager.get_online_users()
        
        assert len(online_users) == 2
        usernames = [user['username'] for user in online_users]
        assert "alice" in usernames
        assert "bob" in usernames
        assert "charlie" not in usernames
    
    def test_is_user_online(self, db_manager):
        """测试检查用户是否在线"""
        user_manager = UserManager(db_manager)
        
        # 注册用户
        user_manager.register_user("alice", "password123")
        user = db_manager.get_user_by_username("alice")
        user_id = user['id']
        
        # 用户未登录时
        assert user_manager.is_user_online(user_id) is False
        
        # 用户登录后
        user_manager.login_user("alice", "password123")
        assert user_manager.is_user_online(user_id) is True
        
        # 用户登出后
        user_manager.logout_user(user_id)
        assert user_manager.is_user_online(user_id) is False
    
    def test_session_management(self, db_manager):
        """测试会话管理"""
        user_manager = UserManager(db_manager)
        
        # 注册并登录用户
        user_manager.register_user("alice", "password123")
        success, message, user_info = user_manager.login_user("alice", "password123")
        user_id = user_info['id']
        
        # 验证会话存在
        assert user_id in user_manager.active_sessions
        session = user_manager.active_sessions[user_id]
        assert session['username'] == "alice"
        assert 'login_time' in session
        
        # 登出后会话应该被清除
        user_manager.logout_user(user_id)
        assert user_id not in user_manager.active_sessions
    
    def test_validate_session(self, db_manager):
        """测试验证会话"""
        user_manager = UserManager(db_manager)
        
        # 注册并登录用户
        user_manager.register_user("alice", "password123")
        success, message, user_info = user_manager.login_user("alice", "password123")
        user_id = user_info['id']
        
        # 有效会话
        assert user_manager.validate_session(user_id) is True
        
        # 无效会话
        assert user_manager.validate_session(999) is False
        
        # 登出后会话无效
        user_manager.logout_user(user_id)
        assert user_manager.validate_session(user_id) is False
    
    def test_get_session_info(self, db_manager):
        """测试获取会话信息"""
        user_manager = UserManager(db_manager)
        
        # 注册并登录用户
        user_manager.register_user("alice", "password123")
        success, message, user_info = user_manager.login_user("alice", "password123")
        user_id = user_info['id']
        
        # 获取会话信息
        session_info = user_manager.get_session_info(user_id)
        
        assert session_info is not None
        assert session_info['username'] == "alice"
        assert session_info['user_id'] == user_id
        assert 'login_time' in session_info
        
        # 不存在的会话
        assert user_manager.get_session_info(999) is None
    
    def test_cleanup_expired_sessions(self, db_manager):
        """测试清理过期会话"""
        user_manager = UserManager(db_manager)
        
        # 设置较短的会话超时时间
        original_timeout = user_manager.session_timeout
        user_manager.session_timeout = 1  # 1秒
        
        try:
            # 注册并登录用户
            user_manager.register_user("alice", "password123")
            success, message, user_info = user_manager.login_user("alice", "password123")
            user_id = user_info['id']
            
            # 验证会话存在
            assert user_id in user_manager.active_sessions
            
            # 等待会话过期
            time.sleep(2)
            
            # 清理过期会话
            user_manager.cleanup_expired_sessions()
            
            # 验证会话已被清理
            assert user_id not in user_manager.active_sessions
            
            # 验证用户状态已更新为离线
            user = db_manager.get_user_by_id(user_id)
            assert user['is_online'] == 0
            
        finally:
            # 恢复原始超时时间
            user_manager.session_timeout = original_timeout
    
    def test_concurrent_login_logout(self, db_manager):
        """测试并发登录登出"""
        import threading
        
        user_manager = UserManager(db_manager)
        
        # 注册用户
        user_manager.register_user("alice", "password123")
        
        results = []
        
        def login_logout():
            try:
                success, message, user_info = user_manager.login_user("alice", "password123")
                if success:
                    user_id = user_info['id']
                    time.sleep(0.1)  # 短暂等待
                    user_manager.logout_user(user_id)
                    results.append("success")
                else:
                    results.append("failed")
            except Exception as e:
                results.append(str(e))
        
        # 创建多个线程同时登录登出
        threads = []
        for i in range(5):
            thread = threading.Thread(target=login_logout)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        assert len(results) == 5
        # 至少有一些成功的操作
        success_count = results.count("success")
        assert success_count > 0
    
    def test_user_manager_with_chinese_users(self, db_manager):
        """测试中文用户名处理"""
        user_manager = UserManager(db_manager)
        
        # 注册中文用户
        success, message, user_id = user_manager.register_user("测试用户", "密码123")
        assert success is True
        
        # 登录中文用户
        success, message, user_info = user_manager.login_user("测试用户", "密码123")
        assert success is True
        assert user_info['username'] == "测试用户"
        
        # 获取在线用户
        online_users = user_manager.get_online_users()
        assert len(online_users) == 1
        assert online_users[0]['username'] == "测试用户"
