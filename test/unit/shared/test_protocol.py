"""
测试共享协议模块
测试消息协议的编码、解码和验证功能
"""

import pytest
import json
from typing import Dict, Any

from shared.protocol import (
    MessageType, create_message, parse_message,
    create_login_request, create_login_response,
    create_register_request, create_register_response,
    create_chat_message, create_system_message, create_error_message
)


class TestMessageType:
    """测试消息类型枚举"""
    
    def test_message_type_values(self):
        """测试消息类型值"""
        assert MessageType.LOGIN_REQUEST.value == "login_request"
        assert MessageType.LOGIN_RESPONSE.value == "login_response"
        assert MessageType.REGISTER_REQUEST.value == "register_request"
        assert MessageType.REGISTER_RESPONSE.value == "register_response"
        assert MessageType.CHAT_MESSAGE.value == "chat_message"
        assert MessageType.SYSTEM_MESSAGE.value == "system_message"
        assert MessageType.ERROR_MESSAGE.value == "error_message"
    
    def test_message_type_uniqueness(self):
        """测试消息类型值的唯一性"""
        values = [msg_type.value for msg_type in MessageType]
        assert len(values) == len(set(values)), "消息类型值应该是唯一的"


class TestCreateMessage:
    """测试消息创建功能"""
    
    def test_create_simple_message(self):
        """测试创建简单消息"""
        message_str = create_message(MessageType.LOGIN_REQUEST, {
            "username": "alice",
            "password": "password123"
        })
        
        assert isinstance(message_str, str)
        
        # 验证JSON格式
        parsed = json.loads(message_str)
        assert parsed["type"] == "login_request"
        assert parsed["data"]["username"] == "alice"
        assert parsed["data"]["password"] == "password123"
    
    def test_create_message_with_chinese(self):
        """测试创建包含中文的消息"""
        message_str = create_message(MessageType.CHAT_MESSAGE, {
            "sender_username": "测试用户",
            "content": "你好，世界！"
        })
        
        parsed = json.loads(message_str)
        assert parsed["data"]["sender_username"] == "测试用户"
        assert parsed["data"]["content"] == "你好，世界！"
    
    def test_create_message_with_empty_data(self):
        """测试创建空数据消息"""
        message_str = create_message(MessageType.SYSTEM_MESSAGE, {})
        
        parsed = json.loads(message_str)
        assert parsed["type"] == "system_message"
        assert parsed["data"] == {}
    
    def test_create_message_with_nested_data(self):
        """测试创建嵌套数据消息"""
        nested_data = {
            "user_info": {
                "id": 1,
                "username": "alice",
                "preferences": {
                    "theme": "dark",
                    "language": "zh-CN"
                }
            },
            "metadata": {
                "version": "1.0",
                "timestamp": 1234567890
            }
        }
        
        message_str = create_message(MessageType.USER_INFO_RESPONSE, nested_data)
        parsed = json.loads(message_str)
        
        assert parsed["data"]["user_info"]["username"] == "alice"
        assert parsed["data"]["user_info"]["preferences"]["theme"] == "dark"
        assert parsed["data"]["metadata"]["version"] == "1.0"


class TestParseMessage:
    """测试消息解析功能"""
    
    def test_parse_valid_message(self):
        """测试解析有效消息"""
        message_str = json.dumps({
            "type": "login_request",
            "data": {
                "username": "alice",
                "password": "password123"
            }
        }, ensure_ascii=False)
        
        parsed = parse_message(message_str)
        assert parsed["type"] == "login_request"
        assert parsed["data"]["username"] == "alice"
        assert parsed["data"]["password"] == "password123"
    
    def test_parse_invalid_json(self):
        """测试解析无效JSON"""
        invalid_json = "{ invalid json format }"
        parsed = parse_message(invalid_json)
        
        assert parsed["type"] == "error"
        assert "Invalid JSON format" in parsed["data"]["error"]
    
    def test_parse_missing_type(self):
        """测试解析缺少类型的消息"""
        message_str = json.dumps({
            "data": {"username": "alice"}
        })
        
        parsed = parse_message(message_str)
        assert parsed["type"] is None
        assert parsed["data"] == {"username": "alice"}
    
    def test_parse_missing_data(self):
        """测试解析缺少数据的消息"""
        message_str = json.dumps({
            "type": "login_request"
        })
        
        parsed = parse_message(message_str)
        assert parsed["type"] == "login_request"
        assert parsed["data"] == {}
    
    def test_parse_empty_string(self):
        """测试解析空字符串"""
        parsed = parse_message("")
        assert parsed["type"] == "error"
        assert "Invalid JSON format" in parsed["data"]["error"]
    
    def test_parse_chinese_content(self):
        """测试解析中文内容"""
        message_str = json.dumps({
            "type": "chat_message",
            "data": {
                "sender_username": "测试用户",
                "content": "你好，这是一条中文消息！"
            }
        }, ensure_ascii=False)
        
        parsed = parse_message(message_str)
        assert parsed["type"] == "chat_message"
        assert parsed["data"]["sender_username"] == "测试用户"
        assert parsed["data"]["content"] == "你好，这是一条中文消息！"


class TestSpecificMessageCreators:
    """测试特定消息创建器"""
    
    def test_create_login_request(self):
        """测试创建登录请求"""
        message_str = create_login_request("alice", "password123")
        parsed = json.loads(message_str)
        
        assert parsed["type"] == "login_request"
        assert parsed["data"]["username"] == "alice"
        assert parsed["data"]["password"] == "password123"
    
    def test_create_login_response_success(self):
        """测试创建成功登录响应"""
        message_str = create_login_response(
            success=True,
            user_id=1,
            username="alice"
        )
        parsed = json.loads(message_str)
        
        assert parsed["type"] == "login_response"
        assert parsed["data"]["success"] is True
        assert parsed["data"]["user_id"] == 1
        assert parsed["data"]["username"] == "alice"
    
    def test_create_login_response_failure(self):
        """测试创建失败登录响应"""
        message_str = create_login_response(
            success=False,
            error_message="用户名或密码错误"
        )
        parsed = json.loads(message_str)
        
        assert parsed["type"] == "login_response"
        assert parsed["data"]["success"] is False
        assert parsed["data"]["error_message"] == "用户名或密码错误"
    
    def test_create_register_request(self):
        """测试创建注册请求"""
        message_str = create_register_request("bob", "password456")
        parsed = json.loads(message_str)
        
        assert parsed["type"] == "register_request"
        assert parsed["data"]["username"] == "bob"
        assert parsed["data"]["password"] == "password456"
    
    def test_create_register_response_success(self):
        """测试创建成功注册响应"""
        message_str = create_register_response(
            success=True,
            user_id=2,
            username="bob"
        )
        parsed = json.loads(message_str)
        
        assert parsed["type"] == "register_response"
        assert parsed["data"]["success"] is True
        assert parsed["data"]["user_id"] == 2
        assert parsed["data"]["username"] == "bob"
    
    def test_create_register_response_failure(self):
        """测试创建失败注册响应"""
        message_str = create_register_response(
            success=False,
            error_message="用户名已存在"
        )
        parsed = json.loads(message_str)
        
        assert parsed["type"] == "register_response"
        assert parsed["data"]["success"] is False
        assert parsed["data"]["error_message"] == "用户名已存在"
    
    def test_create_chat_message(self):
        """测试创建聊天消息"""
        message_str = create_chat_message(
            sender_id=1,
            sender_username="alice",
            chat_group_id=1,
            chat_group_name="public",
            content="Hello everyone!"
        )
        parsed = json.loads(message_str)
        
        assert parsed["type"] == "chat_message"
        assert parsed["data"]["sender_id"] == 1
        assert parsed["data"]["sender_username"] == "alice"
        assert parsed["data"]["chat_group_id"] == 1
        assert parsed["data"]["chat_group_name"] == "public"
        assert parsed["data"]["content"] == "Hello everyone!"
        assert "timestamp" in parsed["data"]
    
    def test_create_system_message(self):
        """测试创建系统消息"""
        message_str = create_system_message(
            content="用户alice加入了聊天室",
            chat_group_id=1
        )
        parsed = json.loads(message_str)
        
        assert parsed["type"] == "system_message"
        assert parsed["data"]["content"] == "用户alice加入了聊天室"
        assert parsed["data"]["chat_group_id"] == 1
        assert "timestamp" in parsed["data"]
    
    def test_create_error_message(self):
        """测试创建错误消息"""
        message_str = create_error_message(
            error_code="INVALID_COMMAND",
            error_message="无效的命令"
        )
        parsed = json.loads(message_str)
        
        assert parsed["type"] == "error_message"
        assert parsed["data"]["error_code"] == "INVALID_COMMAND"
        assert parsed["data"]["error_message"] == "无效的命令"
        assert "timestamp" in parsed["data"]


class TestMessageRoundTrip:
    """测试消息往返处理"""
    
    def test_login_request_roundtrip(self):
        """测试登录请求往返"""
        # 创建消息
        original_message = create_login_request("alice", "password123")
        
        # 解析消息
        parsed = parse_message(original_message)
        
        # 重新创建消息
        recreated_message = create_message(
            MessageType.LOGIN_REQUEST,
            parsed["data"]
        )
        
        # 验证一致性
        original_parsed = json.loads(original_message)
        recreated_parsed = json.loads(recreated_message)
        
        assert original_parsed["type"] == recreated_parsed["type"]
        assert original_parsed["data"]["username"] == recreated_parsed["data"]["username"]
        assert original_parsed["data"]["password"] == recreated_parsed["data"]["password"]
    
    def test_chat_message_roundtrip(self):
        """测试聊天消息往返"""
        original_message = create_chat_message(
            sender_id=1,
            sender_username="alice",
            chat_group_id=1,
            chat_group_name="public",
            content="Hello world!"
        )
        
        parsed = parse_message(original_message)
        recreated_message = create_message(
            MessageType.CHAT_MESSAGE,
            parsed["data"]
        )
        
        original_parsed = json.loads(original_message)
        recreated_parsed = json.loads(recreated_message)
        
        assert original_parsed["type"] == recreated_parsed["type"]
        assert original_parsed["data"]["sender_id"] == recreated_parsed["data"]["sender_id"]
        assert original_parsed["data"]["content"] == recreated_parsed["data"]["content"]
    
    def test_unicode_roundtrip(self):
        """测试Unicode字符往返"""
        original_message = create_chat_message(
            sender_id=1,
            sender_username="测试用户😀",
            chat_group_id=1,
            chat_group_name="中文聊天室🎉",
            content="你好世界！🌍"
        )
        
        parsed = parse_message(original_message)
        recreated_message = create_message(
            MessageType.CHAT_MESSAGE,
            parsed["data"]
        )
        
        original_parsed = json.loads(original_message)
        recreated_parsed = json.loads(recreated_message)
        
        assert original_parsed["data"]["sender_username"] == recreated_parsed["data"]["sender_username"]
        assert original_parsed["data"]["chat_group_name"] == recreated_parsed["data"]["chat_group_name"]
        assert original_parsed["data"]["content"] == recreated_parsed["data"]["content"]
