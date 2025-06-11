"""
基本功能测试
测试服务器和客户端的基本连接、注册、登录功能
"""

import pytest
import threading
import time
import socket
from unittest.mock import patch

from server.core.server import ChatRoomServer
from client.core.client import ChatClient
from server.database.connection import DatabaseConnection
from shared.constants import DEFAULT_HOST


class TestBasicFunctionality:
    """基本功能测试类"""
    
    @pytest.fixture(scope="class")
    def test_server(self):
        """启动测试服务器"""
        # 使用测试数据库
        test_db_path = "tests/test_chatroom.db"
        DatabaseConnection.set_database_path(test_db_path)
        
        # 创建服务器实例
        server = ChatRoomServer(DEFAULT_HOST, 8889)
        
        # 在后台线程启动服务器
        server_thread = threading.Thread(target=server.start, daemon=True)
        server_thread.start()
        
        # 等待服务器启动
        time.sleep(2)
        
        # 验证服务器是否启动成功
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.connect((DEFAULT_HOST, 8889))
            test_socket.close()
        except ConnectionRefusedError:
            pytest.fail("测试服务器启动失败")
        
        yield server
        
        # 清理
        server.stop()
        
        # 清理测试数据库
        import os
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
    
    def test_server_startup(self, test_server):
        """测试服务器启动"""
        assert test_server.running
        assert test_server.server_socket is not None
    
    def test_client_connection(self, test_server):
        """测试客户端连接"""
        client = ChatClient(DEFAULT_HOST, 8889)
        
        # 测试连接
        assert client.connect()
        assert client.is_connected()
        
        # 清理
        client.disconnect()
        assert not client.is_connected()
    
    def test_user_registration(self, test_server):
        """测试用户注册"""
        client = ChatClient(DEFAULT_HOST, 8889)
        
        try:
            # 连接服务器
            assert client.connect()
            
            # 注册用户
            success, message = client.register("testuser1", "password123")
            assert success
            assert "注册成功" in message
            
            # 尝试重复注册
            success, message = client.register("testuser1", "password456")
            assert not success
            assert "已存在" in message
            
        finally:
            client.disconnect()
    
    def test_user_login(self, test_server):
        """测试用户登录"""
        client = ChatClient(DEFAULT_HOST, 8889)
        
        try:
            # 连接服务器
            assert client.connect()
            
            # 先注册用户
            success, _ = client.register("testuser2", "password123")
            assert success
            
            # 正确登录
            success, message = client.login("testuser2", "password123")
            assert success
            assert "登录成功" in message
            assert client.is_logged_in()
            
            # 错误密码登录
            client.disconnect()
            assert client.connect()
            
            success, message = client.login("testuser2", "wrongpassword")
            assert not success
            assert "错误" in message
            
        finally:
            client.disconnect()
    
    def test_multiple_clients(self, test_server):
        """测试多客户端连接"""
        clients = []
        
        try:
            # 创建多个客户端
            for i in range(3):
                client = ChatClient(DEFAULT_HOST, 8889)
                assert client.connect()
                
                # 注册和登录
                username = f"user{i}"
                success, _ = client.register(username, "password123")
                assert success
                
                success, _ = client.login(username, "password123")
                assert success
                
                clients.append(client)
            
            # 验证所有客户端都已连接和登录
            for client in clients:
                assert client.is_connected()
                assert client.is_logged_in()
                
        finally:
            # 清理所有客户端
            for client in clients:
                client.disconnect()
    
    def test_invalid_credentials(self, test_server):
        """测试无效凭据"""
        client = ChatClient(DEFAULT_HOST, 8889)
        
        try:
            assert client.connect()
            
            # 测试无效用户名格式
            success, message = client.register("ab", "password123")
            assert not success
            assert "长度" in message
            
            # 测试无效密码格式
            success, message = client.register("validuser", "123")
            assert not success
            assert "长度" in message or "字母" in message
            
            # 测试不存在的用户登录
            success, message = client.login("nonexistent", "password123")
            assert not success
            
        finally:
            client.disconnect()


class TestDatabaseOperations:
    """数据库操作测试"""
    
    @pytest.fixture
    def test_db(self):
        """创建测试数据库"""
        test_db_path = "tests/test_db_ops.db"
        DatabaseConnection.set_database_path(test_db_path)
        
        from server.database.connection import get_db
        db = get_db()
        
        yield db
        
        # 清理
        import os
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
    
    def test_user_creation(self, test_db):
        """测试用户创建"""
        # 创建用户
        user_id = test_db.create_user("testuser", "password123")
        assert user_id > 0
        
        # 获取用户信息
        user_info = test_db.get_user_by_id(user_id)
        assert user_info['username'] == "testuser"
        assert user_info['is_online'] == 0
        
        # 测试重复用户名
        with pytest.raises(Exception):
            test_db.create_user("testuser", "password456")
    
    def test_user_authentication(self, test_db):
        """测试用户认证"""
        # 创建用户
        test_db.create_user("authuser", "password123")
        
        # 正确认证
        user_info = test_db.authenticate_user("authuser", "password123")
        assert user_info is not None
        assert user_info['username'] == "authuser"
        
        # 错误密码
        user_info = test_db.authenticate_user("authuser", "wrongpassword")
        assert user_info is None
        
        # 不存在的用户
        user_info = test_db.authenticate_user("nonexistent", "password123")
        assert user_info is None
    
    def test_chat_group_operations(self, test_db):
        """测试聊天组操作"""
        # 创建用户
        user_id = test_db.create_user("chatuser", "password123")
        
        # 创建聊天组
        group_id = test_db.create_chat_group("testgroup", False)
        assert group_id > 0
        
        # 添加用户到聊天组
        test_db.add_user_to_chat_group(group_id, user_id)
        
        # 验证用户在聊天组中
        assert test_db.is_user_in_chat_group(group_id, user_id)
        
        # 获取聊天组成员
        members = test_db.get_chat_group_members(group_id)
        assert len(members) == 1
        assert members[0]['username'] == "chatuser"
    
    def test_message_operations(self, test_db):
        """测试消息操作"""
        # 创建用户和聊天组
        user_id = test_db.create_user("msguser", "password123")
        group_id = test_db.create_chat_group("msggroup", False)
        test_db.add_user_to_chat_group(group_id, user_id)
        
        # 保存消息
        message_id = test_db.save_message(group_id, user_id, "Hello World!")
        assert message_id > 0
        
        # 获取聊天历史
        history = test_db.get_chat_history(group_id, 10)
        assert len(history) == 1
        assert history[0]['content'] == "Hello World!"
        assert history[0]['sender_username'] == "msguser"


def run_basic_tests():
    """运行基本功能测试"""
    print("开始运行基本功能测试...")
    
    # 运行测试
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short"
    ])
    
    if exit_code == 0:
        print("✅ 所有基本功能测试通过！")
    else:
        print("❌ 部分测试失败，请检查代码")
    
    return exit_code


if __name__ == "__main__":
    run_basic_tests()
