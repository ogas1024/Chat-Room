"""
测试客户端核心模块
测试网络客户端的连接、消息发送接收等功能
"""

import pytest
import socket
import threading
import time
import json
from unittest.mock import Mock, patch, MagicMock

from client.core.client import NetworkClient, ChatClient
from shared.constants import DEFAULT_HOST, DEFAULT_PORT, MessageType
from shared.messages import LoginRequest, LoginResponse, ChatMessage
from test.utils.test_helpers import MockServer, MessageBuilder


class TestNetworkClient:
    """测试网络客户端"""
    
    def test_network_client_creation(self):
        """测试网络客户端创建"""
        client = NetworkClient(DEFAULT_HOST, DEFAULT_PORT)
        assert client.host == DEFAULT_HOST
        assert client.port == DEFAULT_PORT
        assert client.socket is None
        assert client.connected is False
    
    @patch('socket.socket')
    def test_connect_success(self, mock_socket):
        """测试成功连接"""
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        
        client = NetworkClient(DEFAULT_HOST, DEFAULT_PORT)
        result = client.connect()
        
        assert result is True
        assert client.connected is True
        assert client.socket == mock_sock_instance
        mock_sock_instance.connect.assert_called_once_with((DEFAULT_HOST, DEFAULT_PORT))
    
    @patch('socket.socket')
    def test_connect_failure(self, mock_socket):
        """测试连接失败"""
        mock_sock_instance = Mock()
        mock_sock_instance.connect.side_effect = ConnectionRefusedError("Connection refused")
        mock_socket.return_value = mock_sock_instance
        
        client = NetworkClient(DEFAULT_HOST, DEFAULT_PORT)
        result = client.connect()
        
        assert result is False
        assert client.connected is False
        assert client.socket is None
    
    def test_disconnect(self):
        """测试断开连接"""
        client = NetworkClient(DEFAULT_HOST, DEFAULT_PORT)
        
        # 模拟已连接状态
        mock_socket = Mock()
        client.socket = mock_socket
        client.connected = True
        
        client.disconnect()
        
        assert client.connected is False
        assert client.socket is None
        mock_socket.close.assert_called_once()
    
    def test_disconnect_when_not_connected(self):
        """测试未连接时断开连接"""
        client = NetworkClient(DEFAULT_HOST, DEFAULT_PORT)
        
        # 应该不会抛出异常
        client.disconnect()
        
        assert client.connected is False
        assert client.socket is None
    
    @patch('socket.socket')
    def test_send_message_success(self, mock_socket):
        """测试成功发送消息"""
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        
        client = NetworkClient(DEFAULT_HOST, DEFAULT_PORT)
        client.connect()
        
        message = LoginRequest(username="alice", password="password123")
        result = client.send_message(message)
        
        assert result is True
        mock_sock_instance.send.assert_called_once()
        
        # 验证发送的数据
        sent_data = mock_sock_instance.send.call_args[0][0]
        assert isinstance(sent_data, bytes)
        
        # 解析发送的JSON数据
        sent_json = json.loads(sent_data.decode('utf-8'))
        assert sent_json['type'] == MessageType.LOGIN_REQUEST.value
        assert sent_json['data']['username'] == "alice"
    
    def test_send_message_when_not_connected(self):
        """测试未连接时发送消息"""
        client = NetworkClient(DEFAULT_HOST, DEFAULT_PORT)
        
        message = LoginRequest(username="alice", password="password123")
        result = client.send_message(message)
        
        assert result is False
    
    @patch('socket.socket')
    def test_send_message_socket_error(self, mock_socket):
        """测试发送消息时socket错误"""
        mock_sock_instance = Mock()
        mock_sock_instance.send.side_effect = OSError("Socket error")
        mock_socket.return_value = mock_sock_instance
        
        client = NetworkClient(DEFAULT_HOST, DEFAULT_PORT)
        client.connect()
        
        message = LoginRequest(username="alice", password="password123")
        result = client.send_message(message)
        
        assert result is False
        assert client.connected is False  # 连接应该被标记为断开
    
    @patch('socket.socket')
    def test_receive_message_success(self, mock_socket):
        """测试成功接收消息"""
        mock_sock_instance = Mock()
        
        # 模拟接收到的数据
        response_data = {
            "type": MessageType.LOGIN_RESPONSE.value,
            "data": {
                "success": True,
                "user_id": 1,
                "username": "alice"
            }
        }
        response_json = json.dumps(response_data, ensure_ascii=False)
        mock_sock_instance.recv.return_value = response_json.encode('utf-8')
        mock_socket.return_value = mock_sock_instance
        
        client = NetworkClient(DEFAULT_HOST, DEFAULT_PORT)
        client.connect()
        
        message = client.receive_message()
        
        assert message is not None
        assert isinstance(message, LoginResponse)
        assert message.success is True
        assert message.user_id == 1
        assert message.username == "alice"
    
    @patch('socket.socket')
    def test_receive_message_timeout(self, mock_socket):
        """测试接收消息超时"""
        mock_sock_instance = Mock()
        mock_sock_instance.recv.side_effect = socket.timeout("Timeout")
        mock_socket.return_value = mock_sock_instance
        
        client = NetworkClient(DEFAULT_HOST, DEFAULT_PORT)
        client.connect()
        
        message = client.receive_message(timeout=1.0)
        
        assert message is None
    
    @patch('socket.socket')
    def test_receive_message_connection_error(self, mock_socket):
        """测试接收消息时连接错误"""
        mock_sock_instance = Mock()
        mock_sock_instance.recv.side_effect = ConnectionResetError("Connection reset")
        mock_socket.return_value = mock_sock_instance
        
        client = NetworkClient(DEFAULT_HOST, DEFAULT_PORT)
        client.connect()
        
        message = client.receive_message()
        
        assert message is None
        assert client.connected is False  # 连接应该被标记为断开
    
    def test_wait_for_response_success(self):
        """测试等待响应成功"""
        client = NetworkClient(DEFAULT_HOST, DEFAULT_PORT)
        
        # 模拟接收消息的方法
        response_message = LoginResponse(
            success=True,
            user_id=1,
            username="alice"
        )
        
        with patch.object(client, 'receive_message', return_value=response_message):
            result = client.wait_for_response(
                timeout=5.0,
                message_types=[MessageType.LOGIN_RESPONSE]
            )
            
            assert result is not None
            assert isinstance(result, LoginResponse)
            assert result.success is True
    
    def test_wait_for_response_timeout(self):
        """测试等待响应超时"""
        client = NetworkClient(DEFAULT_HOST, DEFAULT_PORT)
        
        with patch.object(client, 'receive_message', return_value=None):
            result = client.wait_for_response(
                timeout=0.1,
                message_types=[MessageType.LOGIN_RESPONSE]
            )
            
            assert result is None
    
    def test_wait_for_response_wrong_type(self):
        """测试等待响应类型不匹配"""
        client = NetworkClient(DEFAULT_HOST, DEFAULT_PORT)
        
        # 返回错误类型的消息
        wrong_message = ChatMessage(
            sender_id=1,
            sender_username="alice",
            chat_group_id=1,
            chat_group_name="public",
            content="Hello"
        )
        
        with patch.object(client, 'receive_message', return_value=wrong_message):
            result = client.wait_for_response(
                timeout=0.1,
                message_types=[MessageType.LOGIN_RESPONSE]
            )
            
            assert result is None


class TestChatClient:
    """测试聊天客户端"""
    
    def test_chat_client_creation(self):
        """测试聊天客户端创建"""
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
        assert client.network_client is not None
        assert client.current_user is None
        assert client.current_chat_group is None
    
    def test_connect(self):
        """测试连接"""
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
        
        with patch.object(client.network_client, 'connect', return_value=True):
            result = client.connect()
            assert result is True
    
    def test_disconnect(self):
        """测试断开连接"""
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
        
        with patch.object(client.network_client, 'disconnect'):
            client.disconnect()
            client.network_client.disconnect.assert_called_once()
    
    def test_is_connected(self):
        """测试检查连接状态"""
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
        
        with patch.object(client.network_client, 'is_connected', return_value=True):
            assert client.is_connected() is True
        
        with patch.object(client.network_client, 'is_connected', return_value=False):
            assert client.is_connected() is False
    
    def test_login_success(self):
        """测试成功登录"""
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
        
        # 模拟网络客户端方法
        with patch.object(client.network_client, 'is_connected', return_value=True), \
             patch.object(client.network_client, 'send_message', return_value=True), \
             patch.object(client.network_client, 'wait_for_response') as mock_wait:
            
            # 模拟成功的登录响应
            mock_response = LoginResponse(
                success=True,
                user_id=1,
                username="alice"
            )
            mock_wait.return_value = mock_response
            
            success, message = client.login("alice", "password123")
            
            assert success is True
            assert "成功" in message
            assert client.current_user is not None
            assert client.current_user['id'] == 1
            assert client.current_user['username'] == "alice"
    
    def test_login_failure(self):
        """测试登录失败"""
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
        
        with patch.object(client.network_client, 'is_connected', return_value=True), \
             patch.object(client.network_client, 'send_message', return_value=True), \
             patch.object(client.network_client, 'wait_for_response') as mock_wait:
            
            # 模拟失败的登录响应
            mock_response = LoginResponse(
                success=False,
                error_message="用户名或密码错误"
            )
            mock_wait.return_value = mock_response
            
            success, message = client.login("alice", "wrongpassword")
            
            assert success is False
            assert "错误" in message
            assert client.current_user is None
    
    def test_login_not_connected(self):
        """测试未连接时登录"""
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
        
        with patch.object(client.network_client, 'is_connected', return_value=False):
            success, message = client.login("alice", "password123")
            
            assert success is False
            assert "连接" in message
    
    def test_register_success(self):
        """测试成功注册"""
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
        
        with patch.object(client.network_client, 'is_connected', return_value=True), \
             patch.object(client.network_client, 'send_message', return_value=True), \
             patch.object(client.network_client, 'wait_for_response') as mock_wait:
            
            # 模拟成功的注册响应
            from shared.messages import RegisterResponse
            mock_response = RegisterResponse(
                success=True,
                user_id=1,
                username="alice"
            )
            mock_wait.return_value = mock_response
            
            success, message = client.register("alice", "password123")
            
            assert success is True
            assert "成功" in message
    
    def test_send_chat_message(self):
        """测试发送聊天消息"""
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
        
        # 设置当前用户
        client.current_user = {'id': 1, 'username': 'alice'}
        
        with patch.object(client.network_client, 'send_message', return_value=True) as mock_send:
            result = client.send_chat_message("Hello world!", 1)
            
            assert result is True
            mock_send.assert_called_once()
            
            # 验证发送的消息
            sent_message = mock_send.call_args[0][0]
            assert isinstance(sent_message, ChatMessage)
            assert sent_message.content == "Hello world!"
            assert sent_message.sender_id == 1
            assert sent_message.sender_username == "alice"
    
    def test_send_chat_message_not_logged_in(self):
        """测试未登录时发送消息"""
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
        
        result = client.send_chat_message("Hello world!", 1)
        
        assert result is False
    
    def test_is_logged_in(self):
        """测试检查登录状态"""
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
        
        # 未登录
        assert client.is_logged_in() is False
        
        # 已登录
        client.current_user = {'id': 1, 'username': 'alice'}
        assert client.is_logged_in() is True
    
    def test_get_current_user(self):
        """测试获取当前用户"""
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
        
        # 未登录
        assert client.get_current_user() is None
        
        # 已登录
        user_info = {'id': 1, 'username': 'alice'}
        client.current_user = user_info
        assert client.get_current_user() == user_info
    
    def test_message_handler_registration(self):
        """测试消息处理器注册"""
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
        
        # 验证默认处理器已注册
        assert MessageType.LOGIN_RESPONSE in client.network_client.message_handlers
        assert MessageType.CHAT_MESSAGE in client.network_client.message_handlers
        assert MessageType.SYSTEM_MESSAGE in client.network_client.message_handlers
    
    def test_handle_chat_message(self):
        """测试处理聊天消息"""
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
        
        # 创建聊天消息
        chat_message = ChatMessage(
            sender_id=2,
            sender_username="bob",
            chat_group_id=1,
            chat_group_name="public",
            content="Hello everyone!"
        )
        
        # 模拟消息处理
        with patch.object(client, '_on_chat_message') as mock_handler:
            client._handle_chat_message(chat_message)
            mock_handler.assert_called_once_with(chat_message)
    
    def test_concurrent_operations(self):
        """测试并发操作"""
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
        
        # 模拟并发登录和发送消息
        results = []
        
        def login_operation():
            with patch.object(client.network_client, 'is_connected', return_value=True), \
                 patch.object(client.network_client, 'send_message', return_value=True), \
                 patch.object(client.network_client, 'wait_for_response') as mock_wait:
                
                mock_response = LoginResponse(success=True, user_id=1, username="alice")
                mock_wait.return_value = mock_response
                
                success, message = client.login("alice", "password123")
                results.append(("login", success))
        
        def send_message_operation():
            time.sleep(0.1)  # 等待登录完成
            if client.current_user:
                with patch.object(client.network_client, 'send_message', return_value=True):
                    result = client.send_chat_message("Hello", 1)
                    results.append(("send", result))
        
        # 创建并启动线程
        login_thread = threading.Thread(target=login_operation)
        send_thread = threading.Thread(target=send_message_operation)
        
        login_thread.start()
        send_thread.start()
        
        login_thread.join()
        send_thread.join()
        
        # 验证结果
        assert len(results) >= 1  # 至少登录操作完成
        login_result = next((r for r in results if r[0] == "login"), None)
        assert login_result is not None
        assert login_result[1] is True  # 登录成功
