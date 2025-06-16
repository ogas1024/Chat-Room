"""
测试共享消息模块
测试消息类的序列化、反序列化和验证功能
"""

import pytest
import json
import time
from typing import Dict, Any

from shared.messages import (
    BaseMessage, LoginRequest, LoginResponse, RegisterRequest, RegisterResponse,
    ChatMessage, SystemMessage, ErrorMessage, UserInfoResponse,
    ListUsersRequest, ListUsersResponse, ListChatsRequest, ListChatsResponse,
    CreateChatRequest, CreateChatResponse, JoinChatRequest, EnterChatRequest,
    EnterChatResponse, FileUploadRequest, FileUploadResponse,
    FileDownloadRequest, FileDownloadResponse, FileListRequest, FileListResponse,
    AIChatRequest, AIChatResponse, parse_message
)
from shared.constants import MessageType


class TestBaseMessage:
    """测试基础消息类"""
    
    def test_base_message_creation(self):
        """测试基础消息创建"""
        message = BaseMessage()
        assert hasattr(message, 'timestamp')
        assert isinstance(message.timestamp, float)
        assert message.timestamp > 0
    
    def test_base_message_to_dict(self):
        """测试基础消息转字典"""
        message = BaseMessage()
        data = message.to_dict()
        assert isinstance(data, dict)
        assert 'timestamp' in data
    
    def test_base_message_to_json(self):
        """测试基础消息转JSON"""
        message = BaseMessage()
        json_str = message.to_json()
        assert isinstance(json_str, str)
        
        # 验证JSON格式正确
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
        assert 'timestamp' in parsed


class TestLoginMessages:
    """测试登录相关消息"""
    
    def test_login_request_creation(self):
        """测试登录请求创建"""
        request = LoginRequest(username="alice", password="password123")
        assert request.username == "alice"
        assert request.password == "password123"
        assert request.message_type == MessageType.LOGIN_REQUEST
    
    def test_login_request_to_dict(self):
        """测试登录请求转字典"""
        request = LoginRequest(username="alice", password="password123")
        data = request.to_dict()
        
        assert data['type'] == MessageType.LOGIN_REQUEST.value
        assert data['data']['username'] == "alice"
        assert data['data']['password'] == "password123"
        assert 'timestamp' in data['data']
    
    def test_login_request_to_json(self):
        """测试登录请求转JSON"""
        request = LoginRequest(username="alice", password="password123")
        json_str = request.to_json()
        
        parsed = json.loads(json_str)
        assert parsed['type'] == MessageType.LOGIN_REQUEST.value
        assert parsed['data']['username'] == "alice"
    
    def test_login_response_success(self):
        """测试成功登录响应"""
        response = LoginResponse(
            success=True,
            user_id=1,
            username="alice"
        )
        
        assert response.success is True
        assert response.user_id == 1
        assert response.username == "alice"
        assert response.error_message is None
        assert response.message_type == MessageType.LOGIN_RESPONSE
    
    def test_login_response_failure(self):
        """测试失败登录响应"""
        response = LoginResponse(
            success=False,
            error_message="用户名或密码错误"
        )
        
        assert response.success is False
        assert response.error_message == "用户名或密码错误"
        assert response.user_id is None
        assert response.username is None
    
    def test_login_response_to_dict(self):
        """测试登录响应转字典"""
        response = LoginResponse(
            success=True,
            user_id=1,
            username="alice"
        )
        data = response.to_dict()
        
        assert data['type'] == MessageType.LOGIN_RESPONSE.value
        assert data['data']['success'] is True
        assert data['data']['user_id'] == 1
        assert data['data']['username'] == "alice"


class TestRegisterMessages:
    """测试注册相关消息"""
    
    def test_register_request_creation(self):
        """测试注册请求创建"""
        request = RegisterRequest(username="bob", password="password456")
        assert request.username == "bob"
        assert request.password == "password456"
        assert request.message_type == MessageType.REGISTER_REQUEST
    
    def test_register_response_success(self):
        """测试成功注册响应"""
        response = RegisterResponse(
            success=True,
            user_id=2,
            username="bob"
        )
        
        assert response.success is True
        assert response.user_id == 2
        assert response.username == "bob"
        assert response.error_message is None
    
    def test_register_response_failure(self):
        """测试失败注册响应"""
        response = RegisterResponse(
            success=False,
            error_message="用户名已存在"
        )
        
        assert response.success is False
        assert response.error_message == "用户名已存在"


class TestChatMessages:
    """测试聊天相关消息"""
    
    def test_chat_message_creation(self):
        """测试聊天消息创建"""
        message = ChatMessage(
            sender_id=1,
            sender_username="alice",
            chat_group_id=1,
            chat_group_name="public",
            content="Hello everyone!"
        )
        
        assert message.sender_id == 1
        assert message.sender_username == "alice"
        assert message.chat_group_id == 1
        assert message.chat_group_name == "public"
        assert message.content == "Hello everyone!"
        assert message.message_type == MessageType.CHAT_MESSAGE
    
    def test_chat_message_with_chinese(self):
        """测试包含中文的聊天消息"""
        message = ChatMessage(
            sender_id=1,
            sender_username="测试用户",
            chat_group_id=1,
            chat_group_name="中文聊天室",
            content="你好，世界！"
        )
        
        json_str = message.to_json()
        parsed = json.loads(json_str)
        assert parsed['data']['sender_username'] == "测试用户"
        assert parsed['data']['chat_group_name'] == "中文聊天室"
        assert parsed['data']['content'] == "你好，世界！"
    
    def test_system_message_creation(self):
        """测试系统消息创建"""
        message = SystemMessage(
            content="用户alice加入了聊天室",
            chat_group_id=1
        )
        
        assert message.content == "用户alice加入了聊天室"
        assert message.chat_group_id == 1
        assert message.message_type == MessageType.SYSTEM_MESSAGE
    
    def test_error_message_creation(self):
        """测试错误消息创建"""
        message = ErrorMessage(
            error_code="INVALID_COMMAND",
            error_message="无效的命令"
        )
        
        assert message.error_code == "INVALID_COMMAND"
        assert message.error_message == "无效的命令"
        assert message.message_type == MessageType.ERROR_MESSAGE


class TestFileTransferMessages:
    """测试文件传输相关消息"""
    
    def test_file_upload_request(self):
        """测试文件上传请求"""
        request = FileUploadRequest(
            filename="test.txt",
            file_size=1024,
            chat_group_id=1
        )
        
        assert request.filename == "test.txt"
        assert request.file_size == 1024
        assert request.chat_group_id == 1
        assert request.message_type == MessageType.FILE_UPLOAD_REQUEST
    
    def test_file_upload_response_success(self):
        """测试成功文件上传响应"""
        response = FileUploadResponse(
            success=True,
            file_id="12345",
            upload_url="/upload/12345"
        )
        
        assert response.success is True
        assert response.file_id == "12345"
        assert response.upload_url == "/upload/12345"
    
    def test_file_download_request(self):
        """测试文件下载请求"""
        request = FileDownloadRequest(file_id="12345")
        
        assert request.file_id == "12345"
        assert request.message_type == MessageType.FILE_DOWNLOAD_REQUEST


class TestAIMessages:
    """测试AI相关消息"""
    
    def test_ai_chat_request(self):
        """测试AI聊天请求"""
        request = AIChatRequest(
            command="chat",
            message="你好，AI",
            chat_group_id=1
        )
        
        assert request.command == "chat"
        assert request.message == "你好，AI"
        assert request.chat_group_id == 1
        assert request.message_type == MessageType.AI_CHAT_REQUEST
    
    def test_ai_chat_response(self):
        """测试AI聊天响应"""
        response = AIChatResponse(
            success=True,
            response="你好！我是AI助手，有什么可以帮助您的吗？",
            chat_group_id=1
        )
        
        assert response.success is True
        assert response.response == "你好！我是AI助手，有什么可以帮助您的吗？"
        assert response.chat_group_id == 1


class TestMessageParsing:
    """测试消息解析功能"""
    
    def test_parse_valid_message(self):
        """测试解析有效消息"""
        message_data = {
            "type": MessageType.LOGIN_REQUEST.value,
            "data": {
                "username": "alice",
                "password": "password123",
                "timestamp": time.time()
            }
        }
        json_str = json.dumps(message_data, ensure_ascii=False)
        
        parsed = parse_message(json_str)
        assert parsed is not None
        assert isinstance(parsed, LoginRequest)
        assert parsed.username == "alice"
        assert parsed.password == "password123"
    
    def test_parse_invalid_json(self):
        """测试解析无效JSON"""
        invalid_json = "{ invalid json }"
        parsed = parse_message(invalid_json)
        assert parsed is None
    
    def test_parse_unknown_message_type(self):
        """测试解析未知消息类型"""
        message_data = {
            "type": "unknown_type",
            "data": {}
        }
        json_str = json.dumps(message_data)
        
        parsed = parse_message(json_str)
        assert parsed is None
    
    def test_parse_missing_data(self):
        """测试解析缺少数据的消息"""
        message_data = {
            "type": MessageType.LOGIN_REQUEST.value
            # 缺少data字段
        }
        json_str = json.dumps(message_data)
        
        parsed = parse_message(json_str)
        assert parsed is None


class TestMessageSerialization:
    """测试消息序列化"""
    
    def test_message_roundtrip(self):
        """测试消息序列化往返"""
        original = ChatMessage(
            sender_id=1,
            sender_username="alice",
            chat_group_id=1,
            chat_group_name="public",
            content="Hello world!"
        )
        
        # 序列化
        json_str = original.to_json()
        
        # 反序列化
        parsed = parse_message(json_str)
        
        assert parsed is not None
        assert isinstance(parsed, ChatMessage)
        assert parsed.sender_id == original.sender_id
        assert parsed.sender_username == original.sender_username
        assert parsed.chat_group_id == original.chat_group_id
        assert parsed.chat_group_name == original.chat_group_name
        assert parsed.content == original.content
    
    def test_unicode_handling(self):
        """测试Unicode字符处理"""
        message = ChatMessage(
            sender_id=1,
            sender_username="用户😀",
            chat_group_id=1,
            chat_group_name="测试🎉",
            content="你好世界！🌍"
        )
        
        json_str = message.to_json()
        parsed = parse_message(json_str)
        
        assert parsed.sender_username == "用户😀"
        assert parsed.chat_group_name == "测试🎉"
        assert parsed.content == "你好世界！🌍"
