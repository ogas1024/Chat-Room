"""
测试数据夹具
提供各种测试数据的生成和管理
"""

import json
import time
import uuid
from typing import Dict, List, Any
from datetime import datetime, timedelta

from shared.constants import MessageType, ChatType, AI_USER_ID


class UserFixtures:
    """用户数据夹具"""
    
    @staticmethod
    def get_valid_users() -> List[Dict[str, Any]]:
        """获取有效用户数据"""
        return [
            {
                "username": "alice",
                "password": "password123",
                "expected_id": 1
            },
            {
                "username": "bob", 
                "password": "securepass456",
                "expected_id": 2
            },
            {
                "username": "charlie",
                "password": "mypassword789",
                "expected_id": 3
            },
            {
                "username": "测试用户",
                "password": "中文密码123",
                "expected_id": 4
            }
        ]
    
    @staticmethod
    def get_invalid_users() -> List[Dict[str, Any]]:
        """获取无效用户数据"""
        return [
            {
                "username": "",  # 空用户名
                "password": "password123",
                "error": "用户名不能为空"
            },
            {
                "username": "ab",  # 用户名太短
                "password": "password123", 
                "error": "用户名长度必须在3-20个字符之间"
            },
            {
                "username": "a" * 21,  # 用户名太长
                "password": "password123",
                "error": "用户名长度必须在3-20个字符之间"
            },
            {
                "username": "validuser",
                "password": "123",  # 密码太短
                "error": "密码长度必须至少6个字符"
            },
            {
                "username": "user@invalid",  # 包含特殊字符
                "password": "password123",
                "error": "用户名只能包含字母、数字、下划线和中文字符"
            }
        ]
    
    @staticmethod
    def get_duplicate_user() -> Dict[str, Any]:
        """获取重复用户数据"""
        return {
            "username": "alice",  # 与第一个用户重复
            "password": "differentpass",
            "error": "用户名已存在"
        }


class ChatGroupFixtures:
    """聊天组数据夹具"""
    
    @staticmethod
    def get_valid_chat_groups() -> List[Dict[str, Any]]:
        """获取有效聊天组数据"""
        return [
            {
                "name": "public",
                "is_private_chat": False,
                "description": "公共聊天室"
            },
            {
                "name": "技术讨论",
                "is_private_chat": False,
                "description": "技术相关讨论"
            },
            {
                "name": "项目组",
                "is_private_chat": False,
                "description": "项目开发讨论"
            },
            {
                "name": "private_alice_bob",
                "is_private_chat": True,
                "description": "Alice和Bob的私聊"
            }
        ]
    
    @staticmethod
    def get_invalid_chat_groups() -> List[Dict[str, Any]]:
        """获取无效聊天组数据"""
        return [
            {
                "name": "",  # 空名称
                "is_private_chat": False,
                "error": "聊天组名称不能为空"
            },
            {
                "name": "ab",  # 名称太短
                "is_private_chat": False,
                "error": "聊天组名称长度必须在3-50个字符之间"
            },
            {
                "name": "a" * 51,  # 名称太长
                "is_private_chat": False,
                "error": "聊天组名称长度必须在3-50个字符之间"
            },
            {
                "name": "group@invalid",  # 包含特殊字符
                "is_private_chat": False,
                "error": "聊天组名称只能包含字母、数字、下划线、中划线和中文字符"
            }
        ]


class MessageFixtures:
    """消息数据夹具"""
    
    @staticmethod
    def get_valid_messages() -> List[Dict[str, Any]]:
        """获取有效消息数据"""
        return [
            {
                "sender_id": 1,
                "sender_username": "alice",
                "chat_group_id": 1,
                "chat_group_name": "public",
                "content": "Hello everyone!",
                "message_type": "chat"
            },
            {
                "sender_id": 2,
                "sender_username": "bob",
                "chat_group_id": 1,
                "chat_group_name": "public",
                "content": "Hi Alice! How are you?",
                "message_type": "chat"
            },
            {
                "sender_id": 1,
                "sender_username": "alice",
                "chat_group_id": 2,
                "chat_group_name": "技术讨论",
                "content": "有人了解Python的异步编程吗？",
                "message_type": "chat"
            },
            {
                "sender_id": 3,
                "sender_username": "charlie",
                "chat_group_id": 2,
                "chat_group_name": "技术讨论",
                "content": "我可以分享一些经验",
                "message_type": "chat"
            },
            {
                "sender_id": AI_USER_ID,
                "sender_username": "AI助手",
                "chat_group_id": 1,
                "chat_group_name": "public",
                "content": "我是AI助手，有什么可以帮助您的吗？",
                "message_type": "ai_response"
            }
        ]
    
    @staticmethod
    def get_invalid_messages() -> List[Dict[str, Any]]:
        """获取无效消息数据"""
        return [
            {
                "sender_id": 1,
                "chat_group_id": 1,
                "content": "",  # 空内容
                "error": "消息内容不能为空"
            },
            {
                "sender_id": 1,
                "chat_group_id": 1,
                "content": "a" * 2049,  # 内容太长
                "error": "消息内容长度不能超过2048个字符"
            },
            {
                "sender_id": 999,  # 不存在的用户
                "chat_group_id": 1,
                "content": "Test message",
                "error": "用户不存在"
            },
            {
                "sender_id": 1,
                "chat_group_id": 999,  # 不存在的聊天组
                "content": "Test message",
                "error": "聊天组不存在"
            }
        ]
    
    @staticmethod
    def get_ai_trigger_messages() -> List[Dict[str, Any]]:
        """获取触发AI回复的消息"""
        return [
            {
                "content": "@AI 你好",
                "should_trigger": True,
                "reason": "直接@AI"
            },
            {
                "content": "AI能帮我解决这个问题吗？",
                "should_trigger": True,
                "reason": "包含AI关键词"
            },
            {
                "content": "这个怎么做？",
                "should_trigger": True,
                "reason": "问号结尾的问题"
            },
            {
                "content": "今天天气不错",
                "should_trigger": False,
                "reason": "普通聊天内容"
            },
            {
                "content": "大家好",
                "should_trigger": False,
                "reason": "普通问候"
            }
        ]


class FileFixtures:
    """文件数据夹具"""
    
    @staticmethod
    def get_valid_files() -> List[Dict[str, Any]]:
        """获取有效文件数据"""
        return [
            {
                "filename": "test.txt",
                "content": "这是一个测试文件\nTest file content",
                "size": 35,
                "extension": ".txt"
            },
            {
                "filename": "document.pdf",
                "content": b"PDF content here",  # 二进制内容
                "size": 16,
                "extension": ".pdf"
            },
            {
                "filename": "中文文件名.txt",
                "content": "中文内容测试",
                "size": 18,
                "extension": ".txt"
            },
            {
                "filename": "image.jpg",
                "content": b"JPEG image data",
                "size": 15,
                "extension": ".jpg"
            }
        ]
    
    @staticmethod
    def get_invalid_files() -> List[Dict[str, Any]]:
        """获取无效文件数据"""
        return [
            {
                "filename": "large_file.txt",
                "size": 105 * 1024 * 1024,  # 超过100MB限制
                "error": "文件大小超过限制"
            },
            {
                "filename": "malicious.exe",
                "extension": ".exe",
                "error": "不支持的文件类型"
            },
            {
                "filename": "",  # 空文件名
                "error": "文件名不能为空"
            },
            {
                "filename": "file_without_extension",
                "error": "文件必须有扩展名"
            }
        ]


class ProtocolFixtures:
    """协议消息夹具"""
    
    @staticmethod
    def get_login_messages() -> Dict[str, Any]:
        """获取登录相关消息"""
        return {
            "valid_login_request": {
                "type": MessageType.LOGIN_REQUEST.value,
                "data": {
                    "username": "alice",
                    "password": "password123"
                }
            },
            "valid_login_response": {
                "type": MessageType.LOGIN_RESPONSE.value,
                "data": {
                    "success": True,
                    "user_id": 1,
                    "username": "alice"
                }
            },
            "invalid_login_response": {
                "type": MessageType.LOGIN_RESPONSE.value,
                "data": {
                    "success": False,
                    "error_message": "用户名或密码错误"
                }
            }
        }
    
    @staticmethod
    def get_chat_messages() -> Dict[str, Any]:
        """获取聊天相关消息"""
        return {
            "chat_message": {
                "type": MessageType.CHAT_MESSAGE.value,
                "data": {
                    "sender_id": 1,
                    "sender_username": "alice",
                    "chat_group_id": 1,
                    "chat_group_name": "public",
                    "content": "Hello everyone!",
                    "timestamp": time.time()
                }
            },
            "system_message": {
                "type": MessageType.SYSTEM_MESSAGE.value,
                "data": {
                    "content": "用户alice加入了聊天室",
                    "chat_group_id": 1,
                    "timestamp": time.time()
                }
            },
            "error_message": {
                "type": MessageType.ERROR_MESSAGE.value,
                "data": {
                    "error_code": "INVALID_COMMAND",
                    "error_message": "无效的命令",
                    "timestamp": time.time()
                }
            }
        }
    
    @staticmethod
    def get_file_transfer_messages() -> Dict[str, Any]:
        """获取文件传输相关消息"""
        return {
            "file_upload_request": {
                "type": MessageType.FILE_UPLOAD_REQUEST.value,
                "data": {
                    "filename": "test.txt",
                    "file_size": 1024,
                    "chat_group_id": 1
                }
            },
            "file_upload_response": {
                "type": MessageType.FILE_UPLOAD_RESPONSE.value,
                "data": {
                    "success": True,
                    "file_id": "12345",
                    "upload_url": "/upload/12345"
                }
            },
            "file_download_request": {
                "type": MessageType.FILE_DOWNLOAD_REQUEST.value,
                "data": {
                    "file_id": "12345"
                }
            }
        }
