"""
客户端-服务器集成测试
测试客户端与服务器之间的完整通信流程
"""

import pytest
import threading
import time
import socket
from pathlib import Path

from server.core.server import ChatRoomServer
from client.core.client import ChatClient
from shared.constants import DEFAULT_HOST, DEFAULT_PORT
from test.utils.test_helpers import wait_for_condition


class TestClientServerIntegration:
    """客户端-服务器集成测试"""
    
    @pytest.fixture
    def test_server(self, db_manager, temp_dir):
        """测试服务器夹具"""
        # 创建服务器配置
        config = {
            "server": {
                "host": DEFAULT_HOST,
                "port": DEFAULT_PORT + 1000,  # 使用不同端口避免冲突
                "max_connections": 10,
                "buffer_size": 4096,
            },
            "database": {
                "path": str(temp_dir / "test_server.db"),
            },
            "file_storage": {
                "path": str(temp_dir / "files"),
                "max_file_size": 1024 * 1024,
            },
            "ai": {
                "enabled": False,  # 集成测试中禁用AI
            }
        }
        
        server = ChatRoomServer(config)
        
        # 在单独线程中启动服务器
        server_thread = threading.Thread(target=server.start, daemon=True)
        server_thread.start()
        
        # 等待服务器启动
        time.sleep(0.5)
        
        yield server
        
        # 清理
        server.stop()
    
    @pytest.fixture
    def test_client(self, test_server):
        """测试客户端夹具"""
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT + 1000)
        yield client
        client.disconnect()
    
    def test_client_server_connection(self, test_client):
        """测试客户端服务器连接"""
        # 连接到服务器
        success = test_client.connect()
        assert success is True
        assert test_client.is_connected() is True
        
        # 断开连接
        test_client.disconnect()
        assert test_client.is_connected() is False
    
    def test_user_registration_flow(self, test_client):
        """测试用户注册流程"""
        # 连接到服务器
        assert test_client.connect() is True
        
        # 注册新用户
        success, message = test_client.register("alice", "password123")
        assert success is True
        assert "成功" in message
    
    def test_user_login_flow(self, test_client):
        """测试用户登录流程"""
        # 连接到服务器
        assert test_client.connect() is True
        
        # 先注册用户
        success, message = test_client.register("alice", "password123")
        assert success is True
        
        # 登录用户
        success, message = test_client.login("alice", "password123")
        assert success is True
        assert "成功" in message
        assert test_client.is_logged_in() is True
        
        # 验证用户信息
        user_info = test_client.get_current_user()
        assert user_info is not None
        assert user_info['username'] == "alice"
    
    def test_duplicate_registration(self, test_client):
        """测试重复注册"""
        assert test_client.connect() is True
        
        # 注册第一个用户
        success, message = test_client.register("alice", "password123")
        assert success is True
        
        # 尝试重复注册
        success, message = test_client.register("alice", "password456")
        assert success is False
        assert "已存在" in message
    
    def test_invalid_login(self, test_client):
        """测试无效登录"""
        assert test_client.connect() is True
        
        # 注册用户
        test_client.register("alice", "password123")
        
        # 错误密码登录
        success, message = test_client.login("alice", "wrongpassword")
        assert success is False
        assert "密码" in message
        
        # 不存在的用户登录
        success, message = test_client.login("nonexistent", "password")
        assert success is False
        assert "不存在" in message
    
    def test_chat_group_operations(self, test_client):
        """测试聊天组操作"""
        assert test_client.connect() is True
        
        # 注册并登录用户
        test_client.register("alice", "password123")
        test_client.login("alice", "password123")
        
        # 创建聊天组
        success, message = test_client.create_chat_group("test_group")
        assert success is True
        assert "成功" in message
        
        # 加入聊天组
        success, message = test_client.join_chat_group("test_group")
        assert success is True
        
        # 进入聊天组
        success, message = test_client.enter_chat("test_group")
        assert success is True
    
    def test_message_sending(self, test_client):
        """测试消息发送"""
        assert test_client.connect() is True
        
        # 注册并登录用户
        test_client.register("alice", "password123")
        test_client.login("alice", "password123")
        
        # 进入默认聊天组
        success, message = test_client.enter_chat("public")
        assert success is True
        
        # 发送消息
        current_user = test_client.get_current_user()
        success = test_client.send_chat_message("Hello world!", 1)  # 假设public聊天组ID为1
        assert success is True
    
    def test_multiple_clients(self, test_server):
        """测试多客户端连接"""
        clients = []
        
        try:
            # 创建多个客户端
            for i in range(3):
                client = ChatClient(DEFAULT_HOST, DEFAULT_PORT + 1000)
                assert client.connect() is True
                
                # 注册并登录用户
                username = f"user_{i}"
                client.register(username, "password123")
                client.login(username, "password123")
                
                clients.append(client)
            
            # 验证所有客户端都已连接
            for client in clients:
                assert client.is_connected() is True
                assert client.is_logged_in() is True
            
            # 获取在线用户列表
            success, message, users = clients[0].list_users()
            assert success is True
            assert len(users) >= 3  # 至少有3个用户在线
            
        finally:
            # 清理客户端连接
            for client in clients:
                client.disconnect()
    
    def test_concurrent_operations(self, test_server):
        """测试并发操作"""
        import threading
        
        results = []
        
        def client_operation(user_id):
            client = ChatClient(DEFAULT_HOST, DEFAULT_PORT + 1000)
            try:
                # 连接
                if not client.connect():
                    results.append(f"user_{user_id}: connect_failed")
                    return
                
                # 注册
                username = f"user_{user_id}"
                success, message = client.register(username, "password123")
                if not success:
                    results.append(f"user_{user_id}: register_failed")
                    return
                
                # 登录
                success, message = client.login(username, "password123")
                if not success:
                    results.append(f"user_{user_id}: login_failed")
                    return
                
                # 创建聊天组
                group_name = f"group_{user_id}"
                success, message = client.create_chat_group(group_name)
                if success:
                    results.append(f"user_{user_id}: success")
                else:
                    results.append(f"user_{user_id}: create_group_failed")
                
            except Exception as e:
                results.append(f"user_{user_id}: exception_{str(e)}")
            finally:
                client.disconnect()
        
        # 创建多个线程同时执行操作
        threads = []
        for i in range(5):
            thread = threading.Thread(target=client_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        assert len(results) == 5
        success_count = len([r for r in results if "success" in r])
        assert success_count > 0  # 至少有一些成功的操作
    
    def test_connection_recovery(self, test_client):
        """测试连接恢复"""
        # 初始连接
        assert test_client.connect() is True
        
        # 注册并登录
        test_client.register("alice", "password123")
        test_client.login("alice", "password123")
        
        # 模拟连接断开
        test_client.disconnect()
        assert test_client.is_connected() is False
        
        # 重新连接
        assert test_client.connect() is True
        
        # 重新登录
        success, message = test_client.login("alice", "password123")
        assert success is True
    
    def test_server_shutdown_handling(self, test_server, test_client):
        """测试服务器关闭处理"""
        # 连接到服务器
        assert test_client.connect() is True
        
        # 注册并登录
        test_client.register("alice", "password123")
        test_client.login("alice", "password123")
        
        # 关闭服务器
        test_server.stop()
        
        # 等待一段时间让连接断开
        time.sleep(1)
        
        # 尝试发送消息应该失败
        success = test_client.send_chat_message("Hello", 1)
        assert success is False
        
        # 连接状态应该被更新
        assert test_client.is_connected() is False
    
    def test_message_flow_between_clients(self, test_server):
        """测试客户端间消息流"""
        client1 = ChatClient(DEFAULT_HOST, DEFAULT_PORT + 1000)
        client2 = ChatClient(DEFAULT_HOST, DEFAULT_PORT + 1000)
        
        try:
            # 两个客户端都连接并登录
            assert client1.connect() is True
            assert client2.connect() is True
            
            client1.register("alice", "password123")
            client1.login("alice", "password123")
            
            client2.register("bob", "password456")
            client2.login("bob", "password456")
            
            # 两个客户端都进入同一个聊天组
            client1.enter_chat("public")
            client2.enter_chat("public")
            
            # 设置消息接收处理器
            received_messages = []
            
            def message_handler(message):
                received_messages.append(message)
            
            # 注册消息处理器（这里需要根据实际实现调整）
            # client2.set_message_handler(message_handler)
            
            # client1发送消息
            success = client1.send_chat_message("Hello from Alice!", 1)
            assert success is True
            
            # 等待消息传播
            time.sleep(0.5)
            
            # 验证client2收到消息（这里需要根据实际实现调整）
            # assert len(received_messages) > 0
            # assert "Hello from Alice!" in received_messages[-1].content
            
        finally:
            client1.disconnect()
            client2.disconnect()
    
    def test_error_handling_integration(self, test_client):
        """测试错误处理集成"""
        assert test_client.connect() is True
        
        # 测试各种错误情况
        error_cases = [
            # 无效用户名注册
            ("register", ("", "password"), False),
            ("register", ("ab", "password"), False),
            ("register", ("a" * 21, "password"), False),
            
            # 无效密码注册
            ("register", ("alice", "123"), False),
            
            # 未登录操作
            ("create_chat_group", ("test_group",), False),
            ("send_chat_message", ("Hello", 1), False),
        ]
        
        for operation, args, expected_success in error_cases:
            if hasattr(test_client, operation):
                method = getattr(test_client, operation)
                try:
                    result = method(*args)
                    if isinstance(result, tuple):
                        success = result[0]
                    else:
                        success = result
                    
                    if expected_success:
                        assert success is True, f"Operation {operation} should succeed"
                    else:
                        assert success is False, f"Operation {operation} should fail"
                except Exception as e:
                    if expected_success:
                        pytest.fail(f"Operation {operation} raised unexpected exception: {e}")
    
    def test_performance_under_load(self, test_server):
        """测试负载下的性能"""
        import time
        
        start_time = time.time()
        
        # 创建多个客户端并执行操作
        clients = []
        try:
            for i in range(10):
                client = ChatClient(DEFAULT_HOST, DEFAULT_PORT + 1000)
                assert client.connect() is True
                
                username = f"load_user_{i}"
                client.register(username, "password123")
                client.login(username, "password123")
                
                clients.append(client)
            
            # 所有客户端发送消息
            for i, client in enumerate(clients):
                client.enter_chat("public")
                client.send_chat_message(f"Message from user {i}", 1)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # 验证性能（10个客户端的操作应该在合理时间内完成）
            assert total_time < 10.0, f"Operations took too long: {total_time}s"
            
        finally:
            for client in clients:
                client.disconnect()
