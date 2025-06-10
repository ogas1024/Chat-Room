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
    message_type: str = MessageType.LOGIN_REQUEST
    username: str = ""
    password: str = ""


@dataclass
class LoginResponse(BaseMessage):
    """登录响应消息"""
    message_type: str = MessageType.LOGIN_RESPONSE
    success: bool = False
    user_id: Optional[int] = None
    username: Optional[str] = None
    error_message: Optional[str] = None
    current_chat_group: Optional[Dict[str, Any]] = None


@dataclass
class RegisterRequest(BaseMessage):
    """注册请求消息"""
    message_type: str = MessageType.REGISTER_REQUEST
    username: str = ""
    password: str = ""


@dataclass
class RegisterResponse(BaseMessage):
    """注册响应消息"""
    message_type: str = MessageType.REGISTER_RESPONSE
    success: bool = False
    user_id: Optional[int] = None
    username: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class ChatMessage(BaseMessage):
    """聊天消息"""
    message_type: str = MessageType.CHAT_MESSAGE
    sender_id: int = 0
    sender_username: str = ""
    chat_group_id: int = 0
    chat_group_name: str = ""
    content: str = ""
    message_id: Optional[int] = None


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
    message_type: str = MessageType.USER_INFO_RESPONSE
    user_info: Optional[UserInfo] = None
    joined_chats_count: int = 0
    private_chats_count: int = 0
    group_chats_count: int = 0
    total_users_count: int = 0
    online_users_count: int = 0
    total_chats_count: int = 0


@dataclass
class ListUsersResponse(BaseMessage):
    """用户列表响应"""
    message_type: str = MessageType.LIST_USERS_RESPONSE
    users: List[UserInfo] = None

    def __post_init__(self):
        super().__post_init__()
        if self.users is None:
            self.users = []


@dataclass
class ListChatsResponse(BaseMessage):
    """聊天组列表响应"""
    message_type: str = MessageType.LIST_CHATS_RESPONSE
    chats: List[ChatGroupInfo] = None

    def __post_init__(self):
        super().__post_init__()
        if self.chats is None:
            self.chats = []


@dataclass
class FileListResponse(BaseMessage):
    """文件列表响应"""
    message_type: str = MessageType.FILE_LIST_RESPONSE
    chat_group_id: int = 0
    files: List[FileInfo] = None

    def __post_init__(self):
        super().__post_init__()
        if self.files is None:
            self.files = []


@dataclass
class SystemMessage(BaseMessage):
    """系统消息"""
    message_type: str = MessageType.SYSTEM_MESSAGE
    content: str = ""
    level: str = "info"  # info, warning, error


@dataclass
class FileUploadResponse(BaseMessage):
    """文件上传响应"""
    message_type: str = MessageType.FILE_UPLOAD_RESPONSE
    success: bool = False
    message: str = ""
    file_id: Optional[int] = None


@dataclass
class FileDownloadResponse(BaseMessage):
    """文件下载响应"""
    message_type: str = MessageType.FILE_DOWNLOAD_RESPONSE
    success: bool = False
    message: str = ""
    filename: str = ""
    file_size: int = 0


@dataclass
class ErrorMessage(BaseMessage):
    """错误消息"""
    message_type: str = MessageType.ERROR_MESSAGE
    error_code: int = 0
    error_message: str = ""


@dataclass
class CreateChatRequest(BaseMessage):
    """创建聊天组请求"""
    message_type: str = MessageType.CREATE_CHAT_REQUEST
    chat_name: str = ""
    member_usernames: List[str] = None

    def __post_init__(self):
        super().__post_init__()
        if self.member_usernames is None:
            self.member_usernames = []


@dataclass
class CreateChatResponse(BaseMessage):
    """创建聊天组响应"""
    message_type: str = MessageType.CREATE_CHAT_RESPONSE
    success: bool = False
    chat_group_id: Optional[int] = None
    chat_name: str = ""
    error_message: Optional[str] = None


@dataclass
class JoinChatRequest(BaseMessage):
    """加入聊天组请求"""
    message_type: str = MessageType.JOIN_CHAT_REQUEST
    chat_name: str = ""


@dataclass
class JoinChatResponse(BaseMessage):
    """加入聊天组响应"""
    message_type: str = MessageType.JOIN_CHAT_RESPONSE
    success: bool = False
    chat_group_id: Optional[int] = None
    chat_name: str = ""
    error_message: Optional[str] = None


@dataclass
class EnterChatRequest(BaseMessage):
    """进入聊天组请求"""
    message_type: str = MessageType.ENTER_CHAT_REQUEST
    chat_name: str = ""


@dataclass
class EnterChatResponse(BaseMessage):
    """进入聊天组响应"""
    message_type: str = MessageType.ENTER_CHAT_RESPONSE
    success: bool = False
    chat_group_id: Optional[int] = None
    chat_name: str = ""
    error_message: Optional[str] = None


@dataclass
class FileListRequest(BaseMessage):
    """文件列表请求"""
    message_type: str = MessageType.FILE_LIST_REQUEST
    chat_group_id: Optional[int] = None


@dataclass
class FileUploadRequest(BaseMessage):
    """文件上传请求"""
    message_type: str = MessageType.FILE_UPLOAD_REQUEST
    filename: str = ""
    file_data: str = ""
    chat_group_id: Optional[int] = None


@dataclass
class FileDownloadRequest(BaseMessage):
    """文件下载请求"""
    message_type: str = MessageType.FILE_DOWNLOAD_REQUEST
    file_id: str = ""


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
        MessageType.CREATE_CHAT_REQUEST: CreateChatRequest,
        MessageType.CREATE_CHAT_RESPONSE: CreateChatResponse,
        MessageType.JOIN_CHAT_REQUEST: JoinChatRequest,
        MessageType.JOIN_CHAT_RESPONSE: JoinChatResponse,
        MessageType.ENTER_CHAT_REQUEST: EnterChatRequest,
        MessageType.ENTER_CHAT_RESPONSE: EnterChatResponse,
        MessageType.FILE_LIST_REQUEST: FileListRequest,
        MessageType.FILE_LIST_RESPONSE: FileListResponse,
        MessageType.FILE_UPLOAD_REQUEST: FileUploadRequest,
        MessageType.FILE_UPLOAD_RESPONSE: FileUploadResponse,
        MessageType.FILE_DOWNLOAD_REQUEST: FileDownloadRequest,
        MessageType.FILE_DOWNLOAD_RESPONSE: FileDownloadResponse,
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
