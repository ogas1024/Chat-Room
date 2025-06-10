"""
消息协议定义
定义客户端和服务器之间通信的消息格式和数据结构
"""

import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

from .constants import MessageType, TIMESTAMP_FORMAT


@dataclass
class BaseMessage:
    """基础消息类"""
    message_type: str
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建消息对象"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str):
        """从JSON字符串创建消息对象"""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class LoginRequest(BaseMessage):
    """登录请求消息"""
    username: str
    password: str
    message_type: str = MessageType.LOGIN_REQUEST


@dataclass
class LoginResponse(BaseMessage):
    """登录响应消息"""
    success: bool
    user_id: Optional[int] = None
    username: Optional[str] = None
    error_message: Optional[str] = None
    message_type: str = MessageType.LOGIN_RESPONSE


@dataclass
class RegisterRequest(BaseMessage):
    """注册请求消息"""
    username: str
    password: str
    message_type: str = MessageType.REGISTER_REQUEST


@dataclass
class RegisterResponse(BaseMessage):
    """注册响应消息"""
    success: bool
    user_id: Optional[int] = None
    username: Optional[str] = None
    error_message: Optional[str] = None
    message_type: str = MessageType.REGISTER_RESPONSE


@dataclass
class ChatMessage(BaseMessage):
    """聊天消息"""
    sender_id: int
    sender_username: str
    chat_group_id: int
    chat_group_name: str
    content: str
    message_id: Optional[int] = None
    message_type: str = MessageType.CHAT_MESSAGE


@dataclass
class UserInfo:
    """用户信息数据结构"""
    user_id: int
    username: str
    is_online: bool


@dataclass
class ChatGroupInfo:
    """聊天组信息数据结构"""
    group_id: int
    group_name: str
    is_private_chat: bool
    member_count: int
    created_at: str


@dataclass
class FileInfo:
    """文件信息数据结构"""
    file_id: int
    original_filename: str
    file_size: int
    uploader_username: str
    upload_time: str


@dataclass
class UserInfoResponse(BaseMessage):
    """用户信息响应"""
    user_info: UserInfo
    joined_chats_count: int
    private_chats_count: int
    group_chats_count: int
    total_users_count: int
    online_users_count: int
    total_chats_count: int
    message_type: str = MessageType.USER_INFO_RESPONSE


@dataclass
class ListUsersResponse(BaseMessage):
    """用户列表响应"""
    users: List[UserInfo]
    message_type: str = MessageType.LIST_USERS_RESPONSE


@dataclass
class ListChatsResponse(BaseMessage):
    """聊天组列表响应"""
    chats: List[ChatGroupInfo]
    message_type: str = MessageType.LIST_CHATS_RESPONSE


@dataclass
class FileListResponse(BaseMessage):
    """文件列表响应"""
    files: List[FileInfo]
    chat_group_id: int
    message_type: str = MessageType.FILE_LIST_RESPONSE


@dataclass
class SystemMessage(BaseMessage):
    """系统消息"""
    content: str
    level: str = "info"  # info, warning, error
    message_type: str = MessageType.SYSTEM_MESSAGE


@dataclass
class ErrorMessage(BaseMessage):
    """错误消息"""
    error_code: int
    error_message: str
    message_type: str = MessageType.ERROR_MESSAGE


def create_message_from_dict(data: Dict[str, Any]) -> BaseMessage:
    """根据消息类型创建对应的消息对象"""
    message_type = data.get('message_type')
    
    message_classes = {
        MessageType.LOGIN_REQUEST: LoginRequest,
        MessageType.LOGIN_RESPONSE: LoginResponse,
        MessageType.REGISTER_REQUEST: RegisterRequest,
        MessageType.REGISTER_RESPONSE: RegisterResponse,
        MessageType.CHAT_MESSAGE: ChatMessage,
        MessageType.USER_INFO_RESPONSE: UserInfoResponse,
        MessageType.LIST_USERS_RESPONSE: ListUsersResponse,
        MessageType.LIST_CHATS_RESPONSE: ListChatsResponse,
        MessageType.FILE_LIST_RESPONSE: FileListResponse,
        MessageType.SYSTEM_MESSAGE: SystemMessage,
        MessageType.ERROR_MESSAGE: ErrorMessage,
    }
    
    message_class = message_classes.get(message_type, BaseMessage)
    return message_class.from_dict(data)


def parse_message(json_str: str) -> BaseMessage:
    """解析JSON消息字符串"""
    try:
        data = json.loads(json_str)
        return create_message_from_dict(data)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        # 如果解析失败，返回错误消息
        return ErrorMessage(
            error_code=1008,
            error_message=f"消息解析失败: {str(e)}"
        )
